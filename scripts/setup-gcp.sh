#!/bin/bash

# FixItFred GCP Setup Script
# Sets up all required GCP services and configurations

set -e

echo "🚀 Setting up GCP integration for FixItFred"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-"fredfix"}
REGION=${2:-"us-central1"}

echo -e "${YELLOW}Project ID: $PROJECT_ID${NC}"
echo -e "${YELLOW}Region: $REGION${NC}"

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Configure Docker
echo "🐳 Configuring Docker for GCR..."
gcloud auth configure-docker gcr.io --quiet

# Create storage bucket
echo "🪣 Creating storage bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-fixitfred-storage || echo "Bucket may already exist"

# Create secrets (empty - to be filled manually)
echo "🔐 Creating Secret Manager secrets..."
secrets=("openai-api-key" "anthropic-api-key" "gemini-api-key" "jwt-secret-key" "database-url")

for secret in "${secrets[@]}"; do
    if ! gcloud secrets describe $secret --project=$PROJECT_ID >/dev/null 2>&1; then
        echo "placeholder" | gcloud secrets create $secret --data-file=- --project=$PROJECT_ID
        echo -e "${GREEN}Created secret: $secret${NC}"
    else
        echo -e "${YELLOW}Secret $secret already exists${NC}"
    fi
done

# Set up Cloud Build trigger (optional)
echo "🏗️ Cloud Build integration ready"
echo "To set up automatic builds, connect your GitHub repository:"
echo "gcloud builds triggers create github --repo-name=FixItFred --repo-owner=TheGringo-ai --branch-pattern=^main\$ --build-config=cloudbuild.yaml"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your actual values${NC}"
fi

echo -e "${GREEN}✅ GCP setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update secrets in Secret Manager with actual values"
echo "2. Edit .env file with your configuration"
echo "3. Run: python3 gcp_deploy.py"
echo ""
echo "Useful commands:"
echo "- Deploy: python3 gcp_deploy.py"
echo "- View logs: gcloud logs tail --service=fixitfred"
echo "- Check secrets: gcloud secrets list"