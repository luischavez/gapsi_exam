output "registry" {
  description = "Prefix for the docker images, e.g. <registry>/backend:<tag>"
  value       = local.registry
}

output "backend_url" {
  description = "Goes in frontend/src/environments/environment.ts as apiUrl"
  value       = local.backend_url
}

output "frontend_url" {
  value = google_firebase_hosting_site.frontend.default_url
}

output "hosting_site_id" {
  description = "Used by firebase target:apply in the frontend"
  value       = google_firebase_hosting_site.frontend.site_id
}
