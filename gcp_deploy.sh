#!/bin/bash

# Enhanced FixItFred Platform - GCP Deployment Script
# Deploys the complete multi-industry AI platform to Google Cloud Platform

echo "🚀 Enhanced FixItFred Platform - GCP Deployment"
echo "=" * 60

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project variables
PROJECT_ID=${1:-"fixitfred-platform"}
REGION=${2:-"us-central1"}
SERVICE_NAME="enhanced-fixitfred"

echo "📋 Deployment Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo ""

# Authenticate and set project
echo "🔐 Setting up GCP authentication..."
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "⚙️ Enabling required GCP APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable logging.googleapis.com

# Create secrets for API keys (if they don't exist)
echo "🔑 Setting up API key secrets..."

# Check and create OpenAI secret
if ! gcloud secrets describe openai-api-key >/dev/null 2>&1; then
    echo "Creating OpenAI API key secret..."
    echo -n "your-openai-key-here" | gcloud secrets create openai-api-key --data-file=-
else
    echo "✅ OpenAI secret already exists"
fi

# Check and create Anthropic secret
if ! gcloud secrets describe anthropic-api-key >/dev/null 2>&1; then
    echo "Creating Anthropic API key secret..."
    echo -n "your-anthropic-key-here" | gcloud secrets create anthropic-api-key --data-file=-
else
    echo "✅ Anthropic secret already exists"
fi

# Check and create Grok secret
if ! gcloud secrets describe grok-api-key >/dev/null 2>&1; then
    echo "Creating Grok API key secret..."
    echo -n "your-grok-key-here" | gcloud secrets create grok-api-key --data-file=-
else
    echo "✅ Grok secret already exists"
fi

# Check and create Gemini secret
if ! gcloud secrets describe gemini-api-key >/dev/null 2>&1; then
    echo "Creating Gemini API key secret..."
    echo -n "your-gemini-key-here" | gcloud secrets create gemini-api-key --data-file=-
else
    echo "✅ Gemini secret already exists"
fi

# Create Cloud Run service with secrets
echo "🌐 Deploying Enhanced FixItFred to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=info" \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest,XAI_API_KEY=grok-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Enhanced FixItFred Platform deployed successfully!"
    echo ""

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

    echo "📊 Deployment Details:"
    echo "   🌐 Platform URL: $SERVICE_URL"
    echo "   📖 API Docs: $SERVICE_URL/docs"
    echo "   🏥 Health Check: $SERVICE_URL/health"
    echo "   📊 Platform Test: $SERVICE_URL/api/platform/test"
    echo ""

    echo "✨ Enhanced Features Available:"
    echo "   🤖 Multi-AI Team Integration (OpenAI, Claude, Grok, Gemini)"
    echo "   🏭 5 Industry-Specific AI Modules"
    echo "   🎤 Voice Command System ('Hey Fred')"
    echo "   📊 Unified Cross-Industry Dashboard"
    echo "   ⚡ 47-Second Business Deployment"
    echo ""

    echo "🔧 Next Steps:"
    echo "   1. Update API keys in Google Secret Manager:"
    echo "      gcloud secrets versions add openai-api-key --data-file=<your-openai-key>"
    echo "      gcloud secrets versions add anthropic-api-key --data-file=<your-anthropic-key>"
    echo "      gcloud secrets versions add grok-api-key --data-file=<your-grok-key>"
    echo "      gcloud secrets versions add gemini-api-key --data-file=<your-gemini-key>"
    echo ""
    echo "   2. Test the platform: curl $SERVICE_URL/health"
    echo "   3. Access the dashboard: $SERVICE_URL"
    echo ""

    # Test the deployment
    echo "🧪 Testing deployment..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health)

    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "✅ Platform is responding correctly!"

        # Get platform status
        echo "📊 Platform Status:"
        curl -s $SERVICE_URL/api/status | python3 -m json.tool

    else
        echo "⚠️ Platform may still be starting up (Status: $HTTP_STATUS)"
        echo "   Check logs: gcloud run logs read --service=$SERVICE_NAME --region=$REGION"
    fi

else
    echo "❌ Deployment failed. Check the logs for details."
    echo "   gcloud run logs read --service=$SERVICE_NAME --region=$REGION"
    exit 1
fi

echo ""
echo "🎉 Enhanced FixItFred Platform deployment complete!"
echo "🌐 Your AI-powered multi-industry platform is now live at: $SERVICE_URL"
