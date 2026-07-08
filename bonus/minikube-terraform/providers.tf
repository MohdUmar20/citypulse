provider "minikube" {
  kubernetes_version = var.kubernetes_version
}

provider "helm" {
  kubernetes {
    host = minikube_cluster.citypulse.host

    client_certificate     = minikube_cluster.citypulse.client_certificate
    client_key             = minikube_cluster.citypulse.client_key
    cluster_ca_certificate = minikube_cluster.citypulse.cluster_ca_certificate
  }
}
