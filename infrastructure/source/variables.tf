variable "namespace" {
  type        = string
  description = "namespace for this environment"
}

variable "name" {
  type        = string
  description = "The software name..."
}

variable "owner" {
  type        = string
  description = "name of the owner for this service"
}

variable "region" {
  type        = string
  description = "The deployment region to be used (i.e. am (america), eu (europe), ap (apac), gl (global))"
}

variable "stage" {
  type        = string
  description = "The deployment stage to be used (t (testing), s (staging), q (qs), p (production))"
}

variable "additional_tags" {
  type        = map(any)
  description = "List of additional tags to append to all resources"
  default     = {}
}