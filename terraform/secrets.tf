ephemeral "random_password" "jwt" {
  length  = 64
  special = false
}

resource "google_secret_manager_secret" "jwt" {
  secret_id = "jwt-secret-key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.this]
}

# write-only, the key never ends up in the terraform state
resource "google_secret_manager_secret_version" "jwt" {
  secret                 = google_secret_manager_secret.jwt.id
  secret_data_wo         = ephemeral.random_password.jwt.result
  secret_data_wo_version = var.jwt_secret_version
}
