resource "google_artifact_registry_repository" "biblion_repo" {
  depends_on    = [google_project_service.project_services]
  location      = var.gcloud_region
  repository_id = "biblion-repo"
  format        = "DOCKER"
}

resource "google_service_account" "cloud_run_service_account" {
  depends_on = [google_project_service.project_services]
  account_id = "cloud-run-service-account"
}

resource "google_project_iam_binding" "cloud_run_secret_manager_admin_binding" {
  project = var.gcloud_project
  role    = "roles/secretmanager.admin"
  members = [
    "serviceAccount:${google_service_account.cloud_run_service_account.email}",
  ]
}

locals {
  biblion_environment = {
    "WEBSITE_BASE_URL"                = var.website_base_url
    "DATABASE_NAME"                   = var.database_name
    "JWT_ALGORITHM"                   = var.jwt_algorithm
    "JWT_AUDIENCE"                    = var.jwt_audience
    "JWT_ISSUER"                      = var.jwt_issuer
    "JWT_EXPIRATION"                  = var.jwt_expiration
    "EMAIL_SENDER"                    = var.email_sender
    "EMAIL_SMTP_SERVER"               = var.email_smtp_server
    "EMAIL_SMTP_USERNAME"             = var.email_smtp_username
    "EMAIL_VERIFICATION_EXPIRATION"   = var.email_verification_expiration
    "EMAIL_PASSWORD_RESET_EXPIRATION" = var.email_password_reset_expiration
  }

  biblion_secrets = [
    { name = "DATABASE_URL", value = var.database_url },
    { name = "JWT_SECRET", value = var.jwt_secret },
    { name = "EMAIL_SMTP_PASSWORD", value = var.email_smtp_password }
  ]
}

resource "google_secret_manager_secret" "biblion_secrets" {
  depends_on = [google_project_service.project_services]
  for_each   = { for index, secret in local.biblion_secrets : index => secret.name }
  secret_id  = "biblion-secret-${lower(each.value)}"
  replication { automatic = true }
}

resource "google_secret_manager_secret_version" "biblion_secrets" {
  for_each    = google_secret_manager_secret.biblion_secrets
  secret      = each.value.id
  secret_data = local.biblion_secrets[each.key].value
}

resource "google_cloud_run_service" "biblion_service" {
  depends_on = [google_project_iam_binding.cloud_run_secret_manager_admin_binding]
  name       = "biblion-service"
  location   = var.gcloud_region

  # See https://github.com/hashicorp/terraform-provider-google/issues/9438#issuecomment-871946786
  autogenerate_revision_name = true

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "3"
      }
    }

    spec {
      service_account_name = google_service_account.cloud_run_service_account.email

      containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello"

        resources {
          limits = { cpu = "1", memory = "256Mi" }
        }

        dynamic "env" {
          for_each = local.biblion_environment

          content {
            name  = env.key
            value = env.value
          }
        }

        dynamic "env" {
          for_each = google_secret_manager_secret_version.biblion_secrets

          content {
            name = local.biblion_secrets[env.key].name

            value_from {
              secret_key_ref {
                name = google_secret_manager_secret.biblion_secrets[env.key].secret_id
                key  = env.value.version
              }
            }
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
