resource "minikube_cluster" "citypulse" {
  driver       = var.minikube_driver
  cluster_name = var.cluster_name
  cni          = "bridge"
  nodes        = 1
  cpus         = var.cpus
  memory       = var.memory

  addons = [
    "default-storageclass",
    "storage-provisioner",
  ]
}
