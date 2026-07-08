resource "helm_release" "citypulse" {
  name             = "citypulse"
  namespace        = "citypulse"
  create_namespace = true
  chart            = "${path.module}/../../helm/citypulse"
  force_update     = true
  wait             = true
  timeout          = 600

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
    name  = "service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "resources.requests.cpu"
    value = "50m"
  }

  set {
    name  = "resources.requests.memory"
    value = "96Mi"
  }

  set {
    name  = "resources.limits.cpu"
    value = "300m"
  }

  set {
    name  = "resources.limits.memory"
    value = "256Mi"
  }

  set {
    name  = "elasticsearch.enabled"
    value = "true"
  }

  set {
    name  = "elasticsearch.javaOpts"
    value = "-Xms256m -Xmx256m"
  }

  set {
    name  = "elasticsearch.resources.requests.cpu"
    value = "75m"
  }

  set {
    name  = "elasticsearch.resources.requests.memory"
    value = "384Mi"
  }

  set {
    name  = "elasticsearch.resources.limits.cpu"
    value = "400m"
  }

  set {
    name  = "elasticsearch.resources.limits.memory"
    value = "768Mi"
  }

  depends_on = [null_resource.k3s_ready]
}
