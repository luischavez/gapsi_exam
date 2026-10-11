locals {
  # Cloud Run also gives each service a predictable url, which lets the frontend
  # be built with the backend url before the backend exists
  backend_url = "https://${var.backend_service_name}-${data.google_project.this.number}.${var.region}.run.app"
}

resource "google_cloud_run_v2_service" "backend" {
  count = var.backend_image_tag == null ? 0 : 1

  name                 = var.backend_service_name
  location             = var.region
  deletion_protection  = false
  invoker_iam_disabled = true

  template {
    service_account = google_service_account.backend.email

    scaling {
      max_instance_count = var.max_instances
    }

    containers {
      image = "${local.registry}/backend:${var.backend_image_tag}"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "CORS_ORIGINS"
        value = jsonencode(local.frontend_origins)
      }

      env {
        name = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_firestore_database.default,
    google_secret_manager_secret_iam_member.backend_jwt,
    google_secret_manager_secret_version.jwt,
  ]
}
