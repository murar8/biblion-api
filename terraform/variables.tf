variable "gcloud_project" {
  type = string
}

variable "gcloud_region" {
  type = string
}

variable "github_repo" {
  type = string
}

variable "website_base_url" {
  type = string
}

variable "database_url" {
  type      = string
  sensitive = true
}

variable "database_name" {
  type = string
}

variable "jwt_algorithm" {
  type    = string
  default = "HS256"
}

variable "jwt_secret" {
  type      = string
  sensitive = true
}

variable "jwt_audience" {
  type    = string
  default = "https://api.biblion.com"
}

variable "jwt_issuer" {
  type    = string
  default = "https://api.biblion.com"
}

variable "jwt_expiration" {
  type    = string
  default = "604800" # seconds (1 week)
}

variable "email_sender" {
  type = string
}

variable "email_smtp_server" {
  type = string
}

variable "email_smtp_username" {
  type = string
}

variable "email_smtp_password" {
  type      = string
  sensitive = true
}

variable "email_verification_expiration" {
  type    = string
  default = "300" # seconds (5 minutes)
}

variable "email_password_reset_expiration" {
  type    = string
  default = "300" # seconds (5 minutes)
}
