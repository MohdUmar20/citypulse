variable "aws_profile" {
  description = "AWS CLI profile used for deployment."
  type        = string
  default     = "aws-personal"
}

variable "aws_region" {
  description = "AWS region for the low-cost K3s instance."
  type        = string
  default     = "us-east-1"
}

variable "availability_zone" {
  description = "Availability zone that supports the selected ARM instance type."
  type        = string
  default     = "us-east-1a"
}

variable "name_prefix" {
  description = "Name prefix for AWS resources."
  type        = string
  default     = "citypulse"
}

variable "instance_type" {
  description = "ARM instance type. t4g.small is safer for K3s plus Elasticsearch than t4g.micro."
  type        = string
  default     = "t4g.small"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GiB."
  type        = number
  default     = 20
}

variable "hosted_zone_name" {
  description = "Route 53 public hosted zone name."
  type        = string
  default     = "clawstack.cloud."
}

variable "subdomain" {
  description = "Subdomain to create under hosted_zone_name."
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
