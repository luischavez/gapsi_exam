variable "project_id" {
  description = "GCP project where everything is deployed"
  type        = string
}

variable "region" {
  description = "Region for Cloud Run, Artifact Registry and Firestore"
  type        = string
  default     = "us-central1"
}

variable "repository_id" {
  description = "Artifact Registry repository for the Docker images"
  type        = string
  default     = "gapsi-exam"
}

variable "backend_service_name" {
  type    = string
  default = "backend"
}

variable "backend_image_tag" {
  description = "Tag of the backend image already pushed to Artifact Registry"
  type        = string
  default     = null
}

variable "hosting_site_id" {
  description = "Firebase Hosting site, defaults to <project_id>-app. Must be globally unique"
  type        = string
  default     = null
}

variable "max_instances" {
  description = "Max Cloud Run instances for the backend"
  type        = number
  default     = 1
}

variable "jwt_secret_version" {
  description = "Bump it to generate and store a new JWT secret key"
  type        = number
  default     = 1
}
