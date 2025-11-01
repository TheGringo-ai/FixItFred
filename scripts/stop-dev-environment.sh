#!/bin/bash

# FixItFred Development Environment Shutdown
# Clean shutdown of all development services

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

echo -e "${PURPLE}🛑 Stopping FixItFred Development Environment${NC}"
echo "========================================"

# Function to stop service by PID file
stop_service_by_pid() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}🛑 Stopping $service_name (PID: $pid)...${NC}"
            kill "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${RED}🔥 Force killing $service_name...${NC}"
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}ℹ️  $service_name was not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}ℹ️  No PID file found for $service_name${NC}"
    fi
}

# Function to stop service by port
stop_service_by_port() {
    local service_name=$1
    local port=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${YELLOW}🛑 Stopping $service_name on port $port...${NC}"
        local pids=$(lsof -ti :$port)
        for pid in $pids; do
            kill "$pid" 2>/dev/null || true
        done
        
        # Wait and check
        sleep 2
        if lsof -i :$port > /dev/null 2>&1; then
            echo -e "${RED}🔥 Force killing processes on port $port...${NC}"
            lsof -ti :$port | xargs kill -9 2>/dev/null || true
        fi
        
        echo -e "${GREEN}✅ $service_name stopped${NC}"
    else
        echo -e "${YELLOW}ℹ️  No service running on port $port${NC}"
    fi
}

# Stop services by PID files first
if [ -d "logs" ]; then
    stop_service_by_pid "Main API" "logs/main_api.pid"
    stop_service_by_pid "AI Development API" "logs/ai_dev_api.pid"
fi

# Stop services by ports (fallback)
echo -e "${BLUE}🔍 Checking for services on common ports...${NC}"
stop_service_by_port "Main API" 8000
stop_service_by_port "AI Development API" 8001
stop_service_by_port "Additional Service" 8002

# Stop any Python processes related to FixItFred
echo -e "${BLUE}🐍 Checking for FixItFred Python processes...${NC}"
fixitfred_pids=$(pgrep -f "fixitfred" 2>/dev/null || true)
if [ -n "$fixitfred_pids" ]; then
    echo -e "${YELLOW}🛑 Stopping FixItFred processes...${NC}"
    echo "$fixitfred_pids" | xargs kill 2>/dev/null || true
    sleep 2
    
    # Force kill if still running
    fixitfred_pids=$(pgrep -f "fixitfred" 2>/dev/null || true)
    if [ -n "$fixitfred_pids" ]; then
        echo -e "${RED}🔥 Force killing FixItFred processes...${NC}"
        echo "$fixitfred_pids" | xargs kill -9 2>/dev/null || true
    fi
fi

# Stop any uvicorn processes
echo -e "${BLUE}🦄 Checking for uvicorn processes...${NC}"
uvicorn_pids=$(pgrep -f "uvicorn" 2>/dev/null || true)
if [ -n "$uvicorn_pids" ]; then
    echo -e "${YELLOW}🛑 Stopping uvicorn processes...${NC}"
    echo "$uvicorn_pids" | xargs kill 2>/dev/null || true
    sleep 2
    
    # Force kill if still running
    uvicorn_pids=$(pgrep -f "uvicorn" 2>/dev/null || true)
    if [ -n "$uvicorn_pids" ]; then
        echo -e "${RED}🔥 Force killing uvicorn processes...${NC}"
        echo "$uvicorn_pids" | xargs kill -9 2>/dev/null || true
    fi
fi

# Clean up log files (optional)
echo -e "${BLUE}🧹 Cleaning up...${NC}"

# Rotate large log files
if [ -d "logs" ]; then
    for log_file in logs/*.log; do
        if [ -f "$log_file" ] && [ $(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo 0) -gt 10485760 ]; then
            echo -e "${YELLOW}📜 Rotating large log file: $log_file${NC}"
            mv "$log_file" "${log_file}.old"
            touch "$log_file"
        fi
    done
fi

# Remove temporary files
rm -f logs/*.pid 2>/dev/null || true
rm -f *.pyc 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Deactivate virtual environment if active
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${BLUE}🐍 Deactivating virtual environment...${NC}"
    deactivate 2>/dev/null || true
fi

# Final verification
echo -e "${BLUE}🔍 Final verification...${NC}"
ports_still_active=()

for port in 8000 8001 8002; do
    if lsof -i :$port > /dev/null 2>&1; then
        ports_still_active+=($port)
    fi
done

if [ ${#ports_still_active[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All FixItFred services stopped successfully${NC}"
    echo ""
    echo -e "${BLUE}📊 Environment Status:${NC}"
    echo -e "   Main API (8000):      ${GREEN}Stopped${NC}"
    echo -e "   AI Development (8001): ${GREEN}Stopped${NC}"
    echo -e "   Additional (8002):     ${GREEN}Stopped${NC}"
    echo ""
    echo -e "${GREEN}🎉 Development environment shutdown complete!${NC}"
    echo ""
    echo -e "${BLUE}💡 To restart: ./scripts/start-dev-environment.sh${NC}"
else
    echo -e "${YELLOW}⚠️  Some ports still active: ${ports_still_active[*]}${NC}"
    echo -e "${BLUE}🔧 You may need to manually check these processes${NC}"
fi

echo ""
echo -e "${PURPLE}👋 Thanks for using FixItFred AI Development Platform!${NC}"