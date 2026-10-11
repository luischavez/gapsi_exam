resource "google_service_account" "backend" {
  account_id   = "${var.backend_service_name}-run"
  display_name = "Backend Cloud Run service"
}

resource "google_project_iam_member" "backend_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = google_service_account.backend.member
}

resource "google_secret_manager_secret_iam_member" "backend_jwt" {
  secret_id = google_secret_manager_secret.jwt.id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_service_account.backend.member
}
