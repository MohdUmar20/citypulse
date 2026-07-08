output "public_ip" {
  description = "Public IPv4 address of the K3s EC2 instance."
  value       = aws_instance.citypulse.public_ip
}

output "url" {
  description = "Public CityPulse URL."
  value       = "http://${local.fqdn}"
}

output "ssh_command" {
  description = "SSH command for the K3s node."
  value       = "ssh -i ${path.module}/citypulse-k3s-key.pem ubuntu@${aws_instance.citypulse.public_ip}"
}

output "test_commands" {
  description = "Basic smoke test commands."
  value = [
    "curl http://${local.fqdn}/healthz",
    "curl http://${local.fqdn}/readyz",
    "curl -X PUT http://${local.fqdn}/cities/Dubai -H 'Content-Type: application/json' -d '{\"population\":3331420}'",
    "curl http://${local.fqdn}/cities/Dubai",
  ]
}
