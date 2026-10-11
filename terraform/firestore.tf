resource "google_firestore_database" "default" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.this]
}

# composite indexes used by GET /issues, one per filter combination.
# __name__ is listed because the API also orders by document id
locals {
  issue_indexes = {
    status          = ["status"]
    priority        = ["priority"]
    status_priority = ["status", "priority"]
  }
}

resource "google_firestore_index" "issues" {
  for_each = local.issue_indexes

  database   = google_firestore_database.default.name
  collection = "issues"

  dynamic "fields" {
    for_each = each.value

    content {
      field_path = fields.value
      order      = "ASCENDING"
    }
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "DESCENDING"
  }
}
