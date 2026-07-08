data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "availability-zone"
    values = [var.availability_zone]
  }
}

data "aws_ssm_parameter" "ubuntu_arm64" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id"
}

data "aws_route53_zone" "domain" {
  name         = var.hosted_zone_name
  private_zone = false
}

data "http" "my_ip" {
  url = "https://checkip.amazonaws.com"
}

locals {
  fqdn       = "${var.subdomain}.${trim(var.hosted_zone_name, ".")}"
  admin_cidr = "${chomp(data.http.my_ip.response_body)}/32"
}

resource "tls_private_key" "ssh" {
  algorithm = "ED25519"
}

resource "local_sensitive_file" "ssh_private_key" {
  filename        = "${path.module}/citypulse-k3s-key.pem"
  content         = tls_private_key.ssh.private_key_openssh
  file_permission = "0600"
}

resource "aws_key_pair" "citypulse" {
  key_name   = "${var.name_prefix}-key"
  public_key = tls_private_key.ssh.public_key_openssh
}

resource "aws_security_group" "citypulse" {
  name        = "${var.name_prefix}-sg"
  description = "CityPulse K3s demo access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP public demo"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "K3s API from current public IP"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = [local.admin_cidr]
  }

  ingress {
    description = "SSH from current public IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.admin_cidr]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.name_prefix}-sg"
    Project = "CityPulse"
  }
}

resource "aws_instance" "citypulse" {
  ami                         = data.aws_ssm_parameter.ubuntu_arm64.value
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.citypulse.id]
  key_name                    = aws_key_pair.citypulse.key_name
  associate_public_ip_address = true

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y curl ca-certificates unzip
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644 --disable traefik --tls-san ${local.fqdn}" sh -
  EOF

  user_data_replace_on_change = true

  tags = {
    Name    = "${var.name_prefix}-k3s"
    Project = "CityPulse"
  }
}

resource "aws_route53_record" "citypulse" {
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = local.fqdn
  type    = "A"
  ttl     = 60
  records = [aws_instance.citypulse.public_ip]
}

resource "null_resource" "k3s_ready" {
  depends_on = [
    aws_instance.citypulse,
    aws_route53_record.citypulse,
    local_sensitive_file.ssh_private_key,
  ]

  triggers = {
    instance_id = aws_instance.citypulse.id
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = aws_instance.citypulse.public_ip
    private_key = tls_private_key.ssh.private_key_openssh
    timeout     = "10m"
  }

  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait",
      "sudo kubectl get nodes",
      "sudo kubectl wait --for=condition=Ready node --all --timeout=5m",
    ]
  }
}

data "external" "kubeconfig" {
  depends_on = [null_resource.k3s_ready]

  program = ["${path.module}/scripts/fetch-k3s-kubeconfig.py"]

  query = {
    host     = aws_instance.citypulse.public_ip
    key_path = local_sensitive_file.ssh_private_key.filename
  }
}
