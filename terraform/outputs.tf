output "github_service_account" {
  value = google_service_account.github_service_account.email
}

output "github_identity_provider" {
  value = google_iam_workload_identity_pool_provider.github_oidc_provider.name
}

output "gcloud_registry" {
  value = "${var.gcloud_region}-docker.pkg.dev"
}

output "gcloud_repository" {
  value = "${var.gcloud_region}-docker.pkg.dev/${var.gcloud_project}/${google_artifact_registry_repository.biblion_repository.name}"
}

output "gcloud_service" {
  value = google_cloud_run_service.biblion_service.name
}

output "gcloud_region" {
  value = var.gcloud_region
}
