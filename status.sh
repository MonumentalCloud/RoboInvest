#!/bin/bash

# RoboInvest - Status Check Script
# Shows the current status of all system components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}📊 RoboInvest System Status${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check backend status
check_backend() {
    echo -e "${CYAN}🔧 Backend Status:${NC}"
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_success "Backend running (PID: $BACKEND_PID)"
            
            # Check if API is responding
            if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
                print_success "API responding on port 8000"
            else
                print_warning "API not responding on port 8000"
            fi
        else
            print_error "Backend PID file exists but process not running"
        fi
    else
        print_warning "No backend PID file found"
    fi
    
    # Check for any uvicorn processes
    UVICORN_PIDS=$(pgrep -f "uvicorn.*fastapi_app" 2>/dev/null || true)
    if [ -n "$UVICORN_PIDS" ]; then
        echo "  Uvicorn processes: $UVICORN_PIDS"
    fi
    
    echo ""
}

# Check frontend status
check_frontend() {
    echo -e "${CYAN}🎨 Frontend Status:${NC}"
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_success "Frontend running (PID: $FRONTEND_PID)"
            
            # Check if frontend is responding
            if curl -s http://localhost:5173 > /dev/null 2>&1; then
                print_success "Frontend responding on port 5173"
            else
                print_warning "Frontend not responding on port 5173"
            fi
        else
            print_error "Frontend PID file exists but process not running"
        fi
    else
        print_warning "No frontend PID file found"
    fi
    
    # Check for any npm processes
    NPM_PIDS=$(pgrep -f "npm.*dev" 2>/dev/null || true)
    if [ -n "$NPM_PIDS" ]; then
        echo "  NPM processes: $NPM_PIDS"
    fi
    
    echo ""
}

# Check database status
check_databases() {
    echo -e "${CYAN}🗄️ Database Status:${NC}"
    
    # Check ChromaDB
    if [ -d "chroma" ] && [ "$(ls -A chroma 2>/dev/null)" ]; then
        print_success "ChromaDB initialized"
    else
        print_warning "ChromaDB not initialized"
    fi
    
    # Check SQLite databases
    if [ -f "data/central_experience.db" ]; then
        print_success "Central Experience DB exists"
    else
        print_warning "Central Experience DB not found"
    fi
    
    if [ -f "data/governor_directives.db" ]; then
        print_success "Governor Directives DB exists"
    else
        print_warning "Governor Directives DB not found"
    fi
    
    echo ""
}

# Check research data
check_research_data() {
    echo -e "${CYAN}🔍 Research Data Status:${NC}"
    
    # Check research directories
    RESEARCH_DIRS=$(find data/ -name "*research*" -type d 2>/dev/null || true)
    
    if [ -n "$RESEARCH_DIRS" ]; then
        print_success "Research directories found:"
        for dir in $RESEARCH_DIRS; do
            FILE_COUNT=$(find "$dir" -name "*.json" -type f 2>/dev/null | wc -l)
            echo "  $dir ($FILE_COUNT files)"
        done
    else
        print_warning "No research directories found"
    fi
    
    # Check for latest research files
    LATEST_FILES=$(find data/ -name "*latest.json" -type f 2>/dev/null | head -5 || true)
    if [ -n "$LATEST_FILES" ]; then
        echo "  Latest research files:"
        for file in $LATEST_FILES; do
            echo "    $file"
        done
    fi
    
    echo ""
}

# Check logs
check_logs() {
    echo -e "${CYAN}📋 Log Files:${NC}"
    
    if [ -d "logs" ]; then
        LOG_FILES=$(ls -la logs/ 2>/dev/null || true)
        if [ -n "$LOG_FILES" ]; then
            echo "$LOG_FILES"
        else
            print_warning "No log files found"
        fi
    else
        print_warning "Logs directory not found"
    fi
    
    echo ""
}

# Check system resources
check_resources() {
    echo -e "${CYAN}💻 System Resources:${NC}"
    
    # Check disk usage
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}')
    echo "  Disk usage: $DISK_USAGE"
    
    # Check memory usage (macOS compatible)
    if command -v free &> /dev/null; then
        MEMORY_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
        echo "  Memory usage: $MEMORY_USAGE"
    else
        # macOS alternative
        MEMORY_USAGE=$(vm_stat | grep "Pages free:" | awk '{print $3}' | sed 's/\.//')
        MEMORY_TOTAL=$(sysctl -n hw.memsize | awk '{print $0/1024/1024/1024 "GB"}')
        echo "  Memory usage: $MEMORY_USAGE pages free / $MEMORY_TOTAL total"
    fi
    
    # Check CPU load
    CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}')
    echo "  CPU load: $CPU_LOAD"
    
    echo ""
}

# Check network ports
check_ports() {
    echo -e "${CYAN}🌐 Network Ports:${NC}"
    
    # Check port 8000 (backend)
    if lsof -i :8000 >/dev/null 2>&1; then
        print_success "Port 8000 (backend) is in use"
    else
        print_warning "Port 8000 (backend) is not in use"
    fi
    
    # Check port 5173 (frontend)
    if lsof -i :5173 >/dev/null 2>&1; then
        print_success "Port 5173 (frontend) is in use"
    else
        print_warning "Port 5173 (frontend) is not in use"
    fi
    
    echo ""
}

# Check environment
check_environment() {
    echo -e "${CYAN}🔧 Environment:${NC}"
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Python not found")
    echo "  Python: $PYTHON_VERSION"
    
    # Check Node.js version
    NODE_VERSION=$(node --version 2>/dev/null || echo "Node.js not found")
    echo "  Node.js: $NODE_VERSION"
    
    # Check npm version
    NPM_VERSION=$(npm --version 2>/dev/null || echo "npm not found")
    echo "  npm: $NPM_VERSION"
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        print_success ".env file exists"
    else
        print_warning ".env file not found"
    fi
    
    echo ""
}

# Display quick actions
display_actions() {
    echo -e "${CYAN}⚡ Quick Actions:${NC}"
    echo "  Start system: ./start.sh"
    echo "  Stop system: ./stop.sh"
    echo "  Check status: ./status.sh"
    echo "  View backend logs: tail -f logs/backend.log"
    echo "  View frontend logs: tail -f logs/frontend.log"
    echo "  Test API: curl http://localhost:8000/api/health"
    echo ""
}

# Main status check
main() {
    print_header
    echo ""
    
    check_backend
    check_frontend
    check_databases
    check_research_data
    check_logs
    check_resources
    check_ports
    check_environment
    display_actions
    
    echo -e "${PURPLE}================================${NC}"
}

# Run main function
main "$@" 