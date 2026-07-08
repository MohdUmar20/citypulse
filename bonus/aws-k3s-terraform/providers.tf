provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

provider "helm" {
  kubernetes {
    host                   = "https://${local.fqdn}:6443"
    cluster_ca_certificate = base64decode(data.external.kubeconfig.result.cluster_ca_certificate)
    client_certificate     = base64decode(data.external.kubeconfig.result.client_certificate)
    client_key             = base64decode(data.external.kubeconfig.result.client_key)
  }
}
