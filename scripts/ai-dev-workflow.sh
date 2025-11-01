#!/bin/bash

# FixItFred AI Development Workflow Automation
# Powered by Grok + Claude AI Team for faster development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="FixItFred"
DEV_PORT="8001"
AI_DEV_API_PORT="8001"

echo -e "${PURPLE}🤖 FixItFred AI Development Workflow${NC}"
echo -e "${PURPLE}Powered by Claude + Grok AI Team${NC}"
echo "========================================"

# Function to display menu
show_menu() {
    echo ""
    echo -e "${BLUE}🔧 Development Actions:${NC}"
    echo "1. 🚀 Start AI Development Server"
    echo "2. 💻 Generate New App with AI"
    echo "3. 🐛 AI Bug Diagnosis & Fix"
    echo "4. ⚡ AI Code Optimization"
    echo "5. 🔍 AI Code Review"
    echo "6. 🚀 Deploy with AI Automation"
    echo "7. 📊 AI Team Status"
    echo "8. 🧪 Run Tests with AI Analysis"
    echo "9. 📱 Launch AI Development Dashboard"
    echo "0. 🚪 Exit"
    echo ""
}

# Function to start AI development server
start_ai_dev_server() {
    echo -e "${GREEN}🚀 Starting AI Development Server...${NC}"
    
    # Check if already running
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  AI Development Server already running on port $AI_DEV_API_PORT${NC}"
        echo -e "${BLUE}🌐 Access at: http://localhost:$AI_DEV_API_PORT${NC}"
        return
    fi
    
    # Start the development server
    echo -e "${BLUE}📡 Launching AI Development API...${NC}"
    cd "$(dirname "$0")/.."
    
    # Install dependencies if needed
    if [ ! -f "venv/bin/activate" ]; then
        echo -e "${YELLOW}📦 Setting up virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start in background
    nohup python3 api/ai_development_api.py > logs/ai_dev_server.log 2>&1 &
    AI_DEV_PID=$!
    
    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for AI Development Server to start...${NC}"
    sleep 5
    
    # Check if running
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✅ AI Development Server started successfully!${NC}"
        echo -e "${BLUE}🌐 Dashboard: http://localhost:$AI_DEV_API_PORT${NC}"
        echo -e "${BLUE}📚 API Docs: http://localhost:$AI_DEV_API_PORT/docs${NC}"
        echo -e "${YELLOW}📝 Logs: tail -f logs/ai_dev_server.log${NC}"
    else
        echo -e "${RED}❌ Failed to start AI Development Server${NC}"
        echo -e "${YELLOW}📝 Check logs: cat logs/ai_dev_server.log${NC}"
    fi
}

# Function to generate new app with AI
generate_ai_app() {
    echo -e "${GREEN}💻 AI-Powered App Generation${NC}"
    echo -e "${BLUE}🤖 The AI team will help you build the perfect app${NC}"
    
    cd "$(dirname "$0")/.."
    
    # Make sure we have the virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    python3 tools/generators/fixitfred_app_generator.py create --interactive
}

# Function for AI bug diagnosis
ai_bug_diagnosis() {
    echo -e "${GREEN}🐛 AI Bug Diagnosis & Fix${NC}"
    echo ""
    
    read -p "📝 Describe the bug: " bug_description
    
    if [ -z "$bug_description" ]; then
        echo -e "${RED}❌ Bug description required${NC}"
        return
    fi
    
    echo -e "${YELLOW}🔍 AI team analyzing the bug...${NC}"
    
    # Call AI development API
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        curl -s -X POST "http://localhost:$AI_DEV_API_PORT/api/dev/diagnose-bug" \
            -H "Content-Type: application/json" \
            -d "{\"title\": \"Bug Report\", \"description\": \"$bug_description\"}" | \
            python3 -m json.tool
    else
        echo -e "${RED}❌ AI Development Server not running. Start it first (option 1)${NC}"
    fi
}

# Function for AI code optimization
ai_code_optimization() {
    echo -e "${GREEN}⚡ AI Code Optimization${NC}"
    echo ""
    
    # List recent Python files
    echo -e "${BLUE}📂 Recent Python files:${NC}"
    find . -name "*.py" -type f -not -path "./venv/*" -not -path "./.git/*" | head -10
    
    echo ""
    read -p "📁 Enter file path to optimize: " file_path
    
    if [ ! -f "$file_path" ]; then
        echo -e "${RED}❌ File not found: $file_path${NC}"
        return
    fi
    
    echo -e "${YELLOW}⚡ AI team optimizing your code...${NC}"
    
    # Read file content and send to AI
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        file_content=$(cat "$file_path")
        curl -s -X POST "http://localhost:$AI_DEV_API_PORT/api/dev/optimize-code" \
            -H "Content-Type: application/json" \
            -d "{\"code\": $(echo "$file_content" | jq -Rs .), \"optimization_goals\": [\"performance\", \"readability\"]}" | \
            python3 -m json.tool
    else
        echo -e "${RED}❌ AI Development Server not running. Start it first (option 1)${NC}"
    fi
}

# Function for AI code review
ai_code_review() {
    echo -e "${GREEN}🔍 AI Code Review${NC}"
    echo ""
    
    # Check for uncommitted changes
    if [ -d ".git" ]; then
        if [ -n "$(git status --porcelain)" ]; then
            echo -e "${BLUE}📋 Reviewing uncommitted changes...${NC}"
            changed_files=$(git diff --name-only)
            
            for file in $changed_files; do
                if [[ $file == *.py ]] || [[ $file == *.js ]] || [[ $file == *.ts ]]; then
                    echo -e "${YELLOW}🔍 Reviewing: $file${NC}"
                    
                    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
                        file_content=$(cat "$file")
                        curl -s -X POST "http://localhost:$AI_DEV_API_PORT/api/dev/ask" \
                            -H "Content-Type: application/json" \
                            -d "{\"message\": \"Review this code for bugs, security issues, and improvements: $(echo "$file_content" | jq -Rs .)\"}" | \
                            python3 -c "import sys, json; data=json.load(sys.stdin); print('\\n'.join([f'{k.upper()}: {v[\"content\"][:200]}...' for k,v in data['responses'].items()]))"
                        echo ""
                    fi
                fi
            done
        else
            echo -e "${YELLOW}ℹ️  No uncommitted changes to review${NC}"
        fi
    else
        echo -e "${YELLOW}ℹ️  Not a git repository${NC}"
    fi
}

# Function for AI-powered deployment
ai_deployment() {
    echo -e "${GREEN}🚀 AI Deployment Automation${NC}"
    echo ""
    
    echo -e "${BLUE}🤖 AI team will create optimized deployment strategy${NC}"
    
    read -p "🏷️  Service name: " service_name
    
    if [ -z "$service_name" ]; then
        service_name="fixitfred-service"
    fi
    
    echo ""
    echo "🌍 Environment options:"
    echo "1. Development"
    echo "2. Staging" 
    echo "3. Production"
    read -p "Choose environment (1-3): " env_choice
    
    case $env_choice in
        1) environment="development" ;;
        2) environment="staging" ;;
        3) environment="production" ;;
        *) environment="development" ;;
    esac
    
    echo -e "${YELLOW}🚀 AI team generating deployment automation...${NC}"
    
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        curl -s -X POST "http://localhost:$AI_DEV_API_PORT/api/dev/automate-deployment" \
            -H "Content-Type: application/json" \
            -d "{\"service_name\": \"$service_name\", \"environment\": \"$environment\"}" | \
            python3 -m json.tool
    else
        echo -e "${RED}❌ AI Development Server not running. Start it first (option 1)${NC}"
    fi
}

# Function to show AI team status
ai_team_status() {
    echo -e "${GREEN}📊 AI Team Status${NC}"
    echo ""
    
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        echo -e "${BLUE}🤖 Fetching AI team status...${NC}"
        curl -s "http://localhost:$AI_DEV_API_PORT/api/dev/status" | python3 -m json.tool
    else
        echo -e "${RED}❌ AI Development Server not running. Start it first (option 1)${NC}"
    fi
}

# Function to run tests with AI analysis
ai_test_analysis() {
    echo -e "${GREEN}🧪 Running Tests with AI Analysis${NC}"
    echo ""
    
    # Check if pytest is available
    if command -v pytest &> /dev/null; then
        echo -e "${BLUE}🧪 Running pytest...${NC}"
        pytest_output=$(pytest tests/ -v 2>&1 || true)
        echo "$pytest_output"
        
        # If there are failures, ask AI for help
        if echo "$pytest_output" | grep -q "FAILED"; then
            echo ""
            echo -e "${YELLOW}🤖 AI analyzing test failures...${NC}"
            
            if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
                curl -s -X POST "http://localhost:$AI_DEV_API_PORT/api/dev/ask" \
                    -H "Content-Type: application/json" \
                    -d "{\"message\": \"Analyze these test failures and suggest fixes: $(echo "$pytest_output" | jq -Rs .)\"}" | \
                    python3 -c "import sys, json; data=json.load(sys.stdin); print('\\n'.join([f'{k.upper()}: {v[\"content\"]}' for k,v in data['responses'].items()]))"
            fi
        else
            echo -e "${GREEN}✅ All tests passed!${NC}"
        fi
    else
        echo -e "${YELLOW}ℹ️  pytest not found. Install with: pip install pytest${NC}"
    fi
}

# Function to launch AI development dashboard
launch_ai_dashboard() {
    echo -e "${GREEN}📱 Launching AI Development Dashboard${NC}"
    
    if lsof -i :$AI_DEV_API_PORT > /dev/null 2>&1; then
        echo -e "${BLUE}🌐 Opening dashboard in browser...${NC}"
        
        # Try to open browser (works on macOS and Linux)
        if command -v open &> /dev/null; then
            open "http://localhost:$AI_DEV_API_PORT"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:$AI_DEV_API_PORT"
        else
            echo -e "${BLUE}🌐 Dashboard URL: http://localhost:$AI_DEV_API_PORT${NC}"
        fi
    else
        echo -e "${RED}❌ AI Development Server not running. Start it first (option 1)${NC}"
    fi
}

# Main menu loop
while true; do
    show_menu
    read -p "Choose an option (0-9): " choice
    
    case $choice in
        1) start_ai_dev_server ;;
        2) generate_ai_app ;;
        3) ai_bug_diagnosis ;;
        4) ai_code_optimization ;;
        5) ai_code_review ;;
        6) ai_deployment ;;
        7) ai_team_status ;;
        8) ai_test_analysis ;;
        9) launch_ai_dashboard ;;
        0) 
            echo -e "${GREEN}👋 Thanks for using FixItFred AI Development!${NC}"
            break
            ;;
        *)
            echo -e "${RED}❌ Invalid option. Please choose 0-9.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done