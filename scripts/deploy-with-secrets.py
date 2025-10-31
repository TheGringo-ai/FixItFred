#!/usr/bin/env python3
"""
Deploy FixItFred to Cloud Run with Secret Manager integration
"""

import subprocess
import sys

def run_command(command):
    """Runs a command and prints its output in real-time."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        for line in process.stdout:
            print(line, end="")
        process.wait()
        if process.returncode != 0:
            print(f"Error: Command '{command}' failed with exit code {process.returncode}")
            sys.exit(process.returncode)
    except Exception as e:
        print(f"An exception occurred: {e}")
        sys.exit(1)

def main():
    """Deploy FixItFred with Secret Manager integration"""
    
    print("🚀 Deploying FixItFred with Secret Manager secrets")
    print("="*50)
    
    project_id = "fredfix"
    region = "us-central1"
    service_name = "fixitfred"
    image_name = f"gcr.io/{project_id}/{service_name}:latest"
    
    # Deploy to Cloud Run with secret environment variables
    print("☁️ Deploying to Cloud Run with secrets...")
    deploy_cmd = f"""
    gcloud run deploy {service_name} \
        --image {image_name} \
        --platform managed \
        --region {region} \
        --project {project_id} \
        --allow-unauthenticated \
        --port 8000 \
        --memory 1Gi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars="USE_SECRET_MANAGER=true,GCP_PROJECT_ID={project_id}" \
        --set-secrets="OPENAI_API_KEY=openai-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,DATABASE_URL=database-url:latest"
    """
    
    run_command(deploy_cmd)
    
    print("✅ Deployment with secrets successful!")
    print(f"🌐 Your app is live at: https://{service_name}-650169261019.{region}.run.app")
    
    # Test the deployment
    print("🧪 Testing deployment...")
    run_command(f"curl -s -o /dev/null -w '%{{http_code}}' https://{service_name}-650169261019.{region}.run.app/")

if __name__ == "__main__":
    main()