resource "helm_release" "citypulse" {
  name             = "citypulse"
  namespace        = var.namespace
  create_namespace = true
  chart            = "${path.module}/../../helm/citypulse"
  force_update     = true

  set {
    name  = "image.repository"
    value = var.image_repository
  }

  set {
    name  = "image.tag"
    value = var.image_tag
  }

  set {
    name  = "image.pullPolicy"
    value = "Always"
  }

  set {
    name  = "elasticsearch.enabled"
    value = "true"
  }

  depends_on = [minikube_cluster.citypulse]
}
