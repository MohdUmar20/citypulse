variable "cluster_name" {
  description = "Minikube cluster/profile name."
  type        = string
  default     = "citypulse"
}

variable "kubernetes_version" {
  description = "Kubernetes version for Minikube."
  type        = string
  default     = "v1.34.0"
}

variable "minikube_driver" {
  description = "Minikube driver to use. Docker keeps the demo lightweight and portable."
  type        = string
  default     = "docker"
}

variable "cpus" {
  description = "CPU count allocated to the Minikube cluster."
  type        = number
  default     = 4
}

variable "memory" {
  description = "Memory allocated to Minikube in MB."
  type        = string
  default     = "6144mb"
}

variable "namespace" {
  description = "Kubernetes namespace for CityPulse."
  type        = string
  default     = "citypulse"
}

variable "image_repository" {
  description = "Public Docker image repository for CityPulse."
  type        = string
  default     = "umar20/citypulse"
}

variable "image_tag" {
  description = "CityPulse Docker image tag."
  type        = string
  default     = "1.1.0"
}

