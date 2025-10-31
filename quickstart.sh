#!/bin/bash
# Quick start script for Fix It Fred - runs directly with Python

echo "🔧 FixItFred Quick Start"
echo "========================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p data logs deployments ui/web/static ui/web/templates storage

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting FixItFred API server..."
echo "Access at: http://localhost:8000"
echo "Docs at: http://localhost:8000/docs"
echo ""

# Run the API server
cd api && python main.py
