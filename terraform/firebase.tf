locals {
  hosting_site_id = coalesce(var.hosting_site_id, "${var.project_id}-app")
}

resource "google_firebase_project" "this" {
  provider = google-beta
  project  = var.project_id

  depends_on = [google_project_service.this]
}

resource "google_firebase_hosting_site" "frontend" {
  provider = google-beta
  project  = google_firebase_project.this.project
  site_id  = local.hosting_site_id
}

locals {
  # firebase serves every site on both domains
  frontend_origins = [
    google_firebase_hosting_site.frontend.default_url,
    "https://${google_firebase_hosting_site.frontend.site_id}.firebaseapp.com",
  ]
}
