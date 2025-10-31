#!/bin/bash
# FixItFred Universal AI Business Platform - Unified Deployment Script
# This script handles all deployment scenarios: local, staging, and production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="fixitfred"
GCP_PROJECT="fredfix"
GCP_REGION="us-central1"
IMAGE_NAME="gcr.io/${GCP_PROJECT}/${PROJECT_NAME}"

echo -e "${BLUE}🔧 FixItFred Deployment Script${NC}"
echo "=================================="

# Function to print colored messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Function to stop and remove old containers
cleanup_old_containers() {
    print_info "Cleaning up old containers..."

    # Stop and remove any running fixitfred containers
    docker ps -a | grep -E "fixitfred|linesmart|chatterfix" | awk '{print $1}' | xargs -r docker stop 2>/dev/null || true
    docker ps -a | grep -E "fixitfred|linesmart|chatterfix" | awk '{print $1}' | xargs -r docker rm 2>/dev/null || true

    print_status "Old containers cleaned up"
}

# Function to check dependencies
check_dependencies() {
    print_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose not found, checking for 'docker compose' plugin..."
        if ! docker compose version &> /dev/null; then
            print_error "Neither docker-compose nor docker compose plugin found"
            exit 1
        fi
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi

    print_status "Dependencies check passed"
}

# Function to build local Docker image
build_local() {
    print_info "Building Docker image locally..."
    docker build -t ${PROJECT_NAME}:latest .
    print_status "Docker image built successfully"
}

# Function to deploy locally
deploy_local() {
    print_info "Deploying FixItFred locally..."

    cleanup_old_containers
    build_local

    print_info "Starting services with docker-compose..."
    $COMPOSE_CMD up -d

    print_status "Local deployment complete!"
    print_info "Access FixItFred at: http://localhost:8000"
    print_info "API documentation: http://localhost:8000/docs"
    print_info "View logs: docker-compose logs -f fixitfred"
}

# Function to build and push to GCP
build_and_push_gcp() {
    print_info "Building and pushing to Google Container Registry..."

    # Configure Docker for GCP
    gcloud auth configure-docker gcr.io --quiet

    # Build with platform specification for consistency
    docker build --platform linux/amd64 -t ${IMAGE_NAME}:latest .

    # Tag with timestamp
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${TIMESTAMP}

    # Push both tags
    docker push ${IMAGE_NAME}:latest
    docker push ${IMAGE_NAME}:${TIMESTAMP}

    print_status "Image pushed to GCR"
    print_info "Latest: ${IMAGE_NAME}:latest"
    print_info "Timestamped: ${IMAGE_NAME}:${TIMESTAMP}"
}

# Function to deploy to Cloud Run
deploy_cloud_run() {
    print_info "Deploying to Cloud Run..."

    gcloud run deploy ${PROJECT_NAME} \
        --image ${IMAGE_NAME}:latest \
        --platform managed \
        --region ${GCP_REGION} \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --max-instances 10 \
        --port 8000 \
        --project ${GCP_PROJECT}

    print_status "Cloud Run deployment complete!"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe ${PROJECT_NAME} \
        --platform managed \
        --region ${GCP_REGION} \
        --project ${GCP_PROJECT} \
        --format 'value(status.url)')

    print_status "Service URL: ${SERVICE_URL}"
}

# Function to check deployment health
check_health() {
    local URL=$1
    print_info "Checking deployment health at ${URL}..."

    if curl -sf "${URL}/health" > /dev/null; then
        print_status "Health check passed!"
        return 0
    else
        print_error "Health check failed!"
        return 1
    fi
}

# Function to show logs
show_logs() {
    print_info "Showing logs..."
    $COMPOSE_CMD logs -f --tail=100
}

# Function to stop services
stop_services() {
    print_info "Stopping services..."
    $COMPOSE_CMD down
    print_status "Services stopped"
}

# Main script logic
case "${1:-local}" in
    local)
        check_dependencies
        deploy_local
        sleep 5
        check_health "http://localhost:8000" || true
        ;;

    build)
        check_dependencies
        build_local
        ;;

    gcp)
        check_dependencies
        cleanup_old_containers
        build_and_push_gcp
        deploy_cloud_run
        ;;

    push)
        check_dependencies
        build_and_push_gcp
        ;;

    logs)
        show_logs
        ;;

    stop)
        stop_services
        ;;

    clean)
        cleanup_old_containers
        print_status "Cleanup complete"
        ;;

    *)
        echo "Usage: $0 {local|build|gcp|push|logs|stop|clean}"
        echo ""
        echo "Commands:"
        echo "  local  - Build and deploy locally with Docker Compose (default)"
        echo "  build  - Build Docker image locally only"
        echo "  gcp    - Build, push to GCR, and deploy to Cloud Run"
        echo "  push   - Build and push to GCR only"
        echo "  logs   - Show logs from local deployment"
        echo "  stop   - Stop local services"
        echo "  clean  - Clean up old containers"
        exit 1
        ;;
esac

echo ""
print_status "Deployment script completed!"
