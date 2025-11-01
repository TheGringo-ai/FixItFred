#!/bin/bash

# FixItFred Development Environment Startup
# Complete development environment with AI team integration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${PURPLE}🚀 FixItFred Development Environment${NC}"
echo -e "${PURPLE}Complete AI-Powered Development Setup${NC}"
echo "========================================"

# Create necessary directories
echo -e "${BLUE}📁 Setting up directories...${NC}"
mkdir -p logs apps tests/integration tests/unit

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
if [[ $(echo "$python_version" | cut -d'.' -f1) -lt 3 ]] || [[ $(echo "$python_version" | cut -d'.' -f2) -lt 8 ]]; then
    echo -e "${RED}❌ Python 3.8+ required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $python_version${NC}"

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
cat > requirements-dev.txt << EOF
# Development Dependencies
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.0.0
mypy>=1.5.0
pre-commit>=3.3.0
jupyter>=1.0.0
ipython>=8.0.0
httpx>=0.24.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
EOF

pip install -r requirements-dev.txt

# Setup pre-commit hooks
echo -e "${BLUE}🪝 Setting up pre-commit hooks...${NC}"
if [ ! -f ".pre-commit-config.yaml" ]; then
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
EOF
fi

pre-commit install

# Check environment variables
echo -e "${BLUE}🔐 Checking environment variables...${NC}"

required_vars=("OPENAI_API_KEY" "XAI_API_KEY" "ANTHROPIC_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Missing environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
        echo -e "${YELLOW}   - $var${NC}"
    done
    echo -e "${BLUE}💡 Set these in your .env file or export them${NC}"
fi

# Load secrets from GCP if available
if command -v gcloud &> /dev/null; then
    echo -e "${BLUE}🔐 Loading secrets from GCP Secret Manager...${NC}"
    
    # Try to get secrets (non-blocking)
    export OPENAI_API_KEY=$(gcloud secrets versions access latest --secret="openai-api-key" 2>/dev/null || echo "")
    export XAI_API_KEY=$(gcloud secrets versions access latest --secret="grok-api-key" 2>/dev/null || echo "")
    export ANTHROPIC_API_KEY=$(gcloud secrets versions access latest --secret="anthropic-api-key" 2>/dev/null || echo "")
    export GEMINI_API_KEY=$(gcloud secrets versions access latest --secret="gemini-api-key" 2>/dev/null || echo "")
    
    if [ -n "$OPENAI_API_KEY" ]; then
        echo -e "${GREEN}✅ Loaded API keys from Secret Manager${NC}"
    fi
fi

# Start services
echo -e "${BLUE}🚀 Starting development services...${NC}"

# Kill existing processes on ports
ports=(8000 8001 8002)
for port in "${ports[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${YELLOW}🔄 Stopping existing service on port $port...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
done

# Start main FixItFred API
echo -e "${BLUE}🔧 Starting main FixItFred API (port 8000)...${NC}"
nohup python3 main.py > logs/main_api.log 2>&1 &
MAIN_PID=$!

# Start AI Development API
echo -e "${BLUE}🤖 Starting AI Development API (port 8001)...${NC}"
nohup python3 api/ai_development_api.py > logs/ai_dev_api.log 2>&1 &
AI_DEV_PID=$!

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 8

# Check service health
services_ok=true

echo -e "${BLUE}🏥 Checking service health...${NC}"

# Check main API
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Main API (port 8000) - Healthy${NC}"
else
    echo -e "${RED}❌ Main API (port 8000) - Failed${NC}"
    services_ok=false
fi

# Check AI Development API
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ AI Development API (port 8001) - Healthy${NC}"
else
    echo -e "${RED}❌ AI Development API (port 8001) - Failed${NC}"
    services_ok=false
fi

# Summary
echo ""
echo -e "${PURPLE}🎉 FixItFred Development Environment Ready!${NC}"
echo "========================================"

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}✅ All services running successfully${NC}"
    echo ""
    echo -e "${BLUE}🌐 Available Services:${NC}"
    echo -e "   Main API:           http://localhost:8000"
    echo -e "   AI Development:     http://localhost:8001"
    echo -e "   API Documentation:  http://localhost:8000/docs"
    echo -e "   AI Dev Dashboard:   http://localhost:8001"
    echo ""
    echo -e "${BLUE}📚 Quick Commands:${NC}"
    echo -e "   AI Workflow:        ./scripts/ai-dev-workflow.sh"
    echo -e "   Generate App:       python3 tools/generators/fixitfred_app_generator.py create --interactive"
    echo -e "   Run Tests:          pytest tests/ -v"
    echo -e "   View Logs:          tail -f logs/*.log"
    echo ""
    echo -e "${BLUE}🤖 AI Team Status:${NC}"
    
    # Check AI team status
    ai_status=$(curl -s http://localhost:8001/api/dev/status 2>/dev/null || echo '{"available_providers": [], "error": "Not available"}')
    echo "$ai_status" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    providers = data.get('available_providers', [])
    if providers:
        print(f'   Available AIs: {', '.join(providers)}')
        print(f'   Active Tasks: {data.get(\"active_tasks\", 0)}')
        print(f'   Completed: {data.get(\"completed_tasks\", 0)}')
    else:
        print('   AI Team: Initializing...')
except:
    print('   AI Team: Initializing...')
"
    
    echo ""
    echo -e "${GREEN}💡 Ready to build amazing things with AI assistance!${NC}"
    
    # Auto-open dashboard if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${BLUE}🌐 Opening AI Development Dashboard...${NC}"
        sleep 2
        open http://localhost:8001
    fi
    
else
    echo -e "${RED}❌ Some services failed to start${NC}"
    echo -e "${YELLOW}📝 Check logs:${NC}"
    echo -e "   Main API: cat logs/main_api.log"
    echo -e "   AI Dev:   cat logs/ai_dev_api.log"
fi

# Store PIDs for cleanup
echo "$MAIN_PID" > logs/main_api.pid
echo "$AI_DEV_PID" > logs/ai_dev_api.pid

echo ""
echo -e "${BLUE}🛑 To stop all services: ./scripts/stop-dev-environment.sh${NC}"
echo -e "${BLUE}📋 For development workflow: ./scripts/ai-dev-workflow.sh${NC}"