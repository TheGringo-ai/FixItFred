# Terraform configuration for FixItFred GCP infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "fredfix"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])

  service = each.value
  disable_on_destroy = false
}

# Cloud Storage bucket for application data
resource "google_storage_bucket" "fixitfred_storage" {
  name     = "${var.project_id}-fixitfred-storage"
  location = var.region

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Secret Manager secrets
resource "google_secret_manager_secret" "app_secrets" {
  for_each = toset([
    "openai-api-key",
    "anthropic-api-key", 
    "gemini-api-key",
    "jwt-secret-key",
    "database-url"
  ])

  secret_id = each.value
  
  replication {
    automatic = true
  }
}

# Cloud SQL instance (PostgreSQL)
resource "google_sql_database_instance" "fixitfred_db" {
  name             = "fixitfred-db"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled = true
      start_time = "02:00"
    }
    
    ip_configuration {
      ipv4_enabled = true
      require_ssl  = true
    }
  }

  deletion_protection = false
}

# Database
resource "google_sql_database" "fixitfred_database" {
  name     = "fixitfred"
  instance = google_sql_database_instance.fixitfred_db.name
}

# Database user
resource "google_sql_user" "fixitfred_user" {
  name     = "fixitfred"
  instance = google_sql_database_instance.fixitfred_db.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.app_secrets["database-url"].name
  secret_data = "postgresql://${google_sql_user.fixitfred_user.name}:${random_password.db_password.result}@${google_sql_database_instance.fixitfred_db.ip_address.0.ip_address}:5432/${google_sql_database.fixitfred_database.name}"
}

# Outputs
output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "storage_bucket" {
  value = google_storage_bucket.fixitfred_storage.name
}

output "database_instance" {
  value = google_sql_database_instance.fixitfred_db.name
}

output "database_ip" {
  value = google_sql_database_instance.fixitfred_db.ip_address.0.ip_address
}