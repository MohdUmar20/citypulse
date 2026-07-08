output "cluster_name" {
  description = "Minikube cluster/profile name."
  value       = minikube_cluster.citypulse.cluster_name
}

output "namespace" {
  description = "Namespace where CityPulse is installed."
  value       = var.namespace
}

output "port_forward_command" {
  description = "Command to access CityPulse locally after apply."
  value       = "kubectl port-forward -n ${var.namespace} svc/citypulse 8080:80"
}

output "dashboard_url" {
  description = "Local URL after running the port-forward command."
  value       = "http://localhost:8080"
}
