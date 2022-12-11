resource "google_artifact_registry_repository" "biblion_repository" {
  depends_on    = [google_project_service.project_services]
  location      = var.gcloud_region
  repository_id = "biblion-repository"
  format        = "DOCKER"
}

locals {
  environment = {
    "WEBSITE_BASE_URL"                = var.website_base_url
    "DATABASE_URL"                    = var.database_url
    "DATABASE_NAME"                   = var.database_name
    "JWT_ALGORITHM"                   = var.jwt_algorithm
    "JWT_SECRET"                      = var.jwt_secret
    "JWT_AUDIENCE"                    = var.jwt_audience
    "JWT_ISSUER"                      = var.jwt_issuer
    "JWT_EXPIRATION"                  = var.jwt_expiration
    "EMAIL_SENDER"                    = var.email_sender
    "EMAIL_SMTP_SERVER"               = var.email_smtp_server
    "EMAIL_SMTP_USERNAME"             = var.email_smtp_username
    "EMAIL_SMTP_PASSWORD"             = var.email_smtp_password
    "EMAIL_VERIFICATION_EXPIRATION"   = var.email_verification_expiration
    "EMAIL_PASSWORD_RESET_EXPIRATION" = var.email_password_reset_expiration
  }
}

resource "google_cloud_run_service" "biblion_service" {
  depends_on = [google_project_service.project_services]
  name       = "biblion-service"
  location   = var.gcloud_region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "3"
      }
    }

    spec {
      containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello"

        dynamic "env" {
          for_each = local.environment

          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  lifecycle {
    ignore_changes = [
      # The image will be updated by the CI pipeline at each push so we can
      # ignore the some of the properties since they will be modified when
      # a new image is pushed.
      template[0].spec[0].containers[0].image,
      template[0].metadata[0].annotations["client.knative.dev/user-image"],
      template[0].metadata[0].annotations["run.googleapis.com/client-name"],
      template[0].metadata[0].annotations["run.googleapis.com/client-version"],
      template[0].metadata[0].labels["commit-sha"],
      template[0].metadata[0].labels["managed-by"]
    ]
  }
}

data "google_iam_policy" "biblion_service_policy" {
  binding {
    role    = "roles/run.invoker"
    members = ["allUsers"]
  }
}

resource "google_cloud_run_service_iam_policy" "biblion_service_policy" {
  location    = google_cloud_run_service.biblion_service.location
  project     = google_cloud_run_service.biblion_service.project
  service     = google_cloud_run_service.biblion_service.name
  policy_data = data.google_iam_policy.biblion_service_policy.policy_data
}
