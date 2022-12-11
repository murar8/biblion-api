terraform {
  cloud {
    organization = "Biblion"
    workspaces { name = "Biblion" }
  }
}

provider "google" {
  project = var.gcloud_project
  region  = var.gcloud_region
}

locals {
  project_services = [
    "cloudresourcemanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com"
  ]
}

# IMPROVEMENT: add some dead time after enabling the required APIs to allow for
# the changes to propagate.

resource "google_project_service" "project_services" {
  for_each                   = toset(local.project_services)
  service                    = each.key
  disable_dependent_services = true
}
