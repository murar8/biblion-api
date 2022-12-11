# We need to create a service account for GitHub Actions to be able to push the
# images to the Artifact registry and update the Cloud Run configuration.
# See https://github.com/google-github-actions/auth#authenticating-via-workload-identity-federation
# See https://gist.github.com/palewire/12c4b2b974ef735d22da7493cf7f4d37

resource "google_service_account" "github_service_account" {
  depends_on = [google_project_service.project_services]
  account_id = "github-service-account"
}

resource "google_iam_workload_identity_pool" "github_identity_pool" {
  depends_on                = [google_project_service.project_services]
  workload_identity_pool_id = "github-identity-pool"
}

resource "google_iam_workload_identity_pool_provider" "github_oidc_provider" {
  workload_identity_pool_provider_id = "github-oidc-provider"
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_identity_pool.workload_identity_pool_id

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_binding" "github_iam_binding" {
  service_account_id = google_service_account.github_service_account.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_identity_pool.name}/attribute.repository/${var.github_repo}",
  ]
}

locals {
  github_roles = [
    "roles/artifactregistry.admin",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
  ]
}

resource "google_project_iam_binding" "github_bindings" {
  for_each = toset(local.github_roles)
  project  = var.gcloud_project
  role     = each.key
  members  = ["serviceAccount:${google_service_account.github_service_account.email}", ]
}
