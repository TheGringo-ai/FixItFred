#!/usr/bin/env python3
"""
Simple GCP Deployment Script for FixItFred
Deploys the application to Google Cloud Run
"""

import subprocess
import sys
import os

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
    """Deploy FixItFred to Google Cloud Run"""

    print("🚀 Deploying FixItFred to Google Cloud Run")
    print("="*50)

    # Configuration
    project_id = "fredfix"
    region = "us-central1"
    service_name = "fixitfred"
    image_name = f"gcr.io/{project_id}/{service_name}"

    # 1. Configure Docker
    print("📦 Configuring Docker for GCR...")
    run_command("gcloud auth configure-docker gcr.io --quiet")

    # 2. Build Docker image
    print("🔨 Building Docker image...")
    run_command(f"docker build --platform linux/amd64 -t {image_name}:latest .")

    # 3. Push to GCR
    print("📤 Pushing to Google Container Registry...")
    run_command(f"docker push {image_name}:latest")

    # 4. Deploy to Cloud Run
    print("☁️ Deploying to Cloud Run...")
    run_command(
        f"gcloud run deploy {service_name} "
        f"--image {image_name}:latest "
        f"--platform managed "
        f"--region {region} "
        f"--project {project_id} "
        f"--allow-unauthenticated "
        f"--port 8000 "
        f"--memory 1Gi "
        f"--cpu 1"
    )

    print("✅ Deployment successful!")
    print(f"🌐 Your app is live at: https://{service_name}-psycl7nhha-uc.a.run.app")

if __name__ == "__main__":
    main()
