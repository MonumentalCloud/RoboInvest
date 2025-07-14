#!/bin/bash

# RoboInvest - Unified Startup Script
# Starts the complete autonomous trading system with all components

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
    echo -e "${PURPLE}🚀 RoboInvest System Startup${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_footer() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}✅ RoboInvest System Ready!${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check if system is already running
check_running() {
    if [ -f ".backend.pid" ] || [ -f ".frontend.pid" ]; then
        print_warning "RoboInvest appears to be already running!"
        echo "PIDs found:"
        [ -f ".backend.pid" ] && echo "  Backend: $(cat .backend.pid)"
        [ -f ".frontend.pid" ] && echo "  Frontend: $(cat .frontend.pid)"
        echo ""
        read -p "Do you want to stop the existing processes and restart? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Stopping existing processes..."
            ./stop.sh
            sleep 2
        else
            print_status "Exiting startup..."
            exit 0
        fi
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p chroma
    
    print_success "Directories ready"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    print_success "Dependencies check passed"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "No requirements.txt found"
    fi
}

# Install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        if [ -f "package.json" ]; then
            npm install
            print_success "Frontend dependencies installed"
        else
            print_warning "No package.json found in frontend directory"
        fi
        cd ..
    else
        print_warning "Frontend directory not found"
    fi
}

# Start backend
start_backend() {
    print_status "Starting backend (FastAPI, port 8000)..."
    
    # Set environment variables
    export PYTHONPATH=$(pwd)
    
    # Start backend with uvicorn
    uvicorn backend.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "Backend started successfully on port 8000"
    else
        print_error "Backend failed to start. Check logs/backend.log"
        exit 1
    fi
}

# Start frontend
start_frontend() {
    print_status "Starting frontend (Vite, port 5173)..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # Start frontend with npm
        npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../.frontend.pid
        
        cd ..
        
        # Wait for frontend to start
        sleep 5
        
        # Check if frontend is running
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            print_success "Frontend started successfully on port 5173"
        else
            print_warning "Frontend may still be starting. Check logs/frontend.log"
        fi
    else
        print_warning "Frontend directory not found, skipping frontend startup"
    fi
}

# Initialize databases
initialize_databases() {
    print_status "Initializing databases..."
    
    # Initialize ChromaDB if needed
    if [ ! -d "chroma" ] || [ -z "$(ls -A chroma 2>/dev/null)" ]; then
        print_status "Setting up ChromaDB..."
        python scripts/setup_chromadb_system.py > logs/chromadb_setup.log 2>&1
        print_success "ChromaDB initialized"
    else
        print_success "ChromaDB already initialized"
    fi
    
    # Initialize other databases will happen automatically when backend starts
}

# Display system information
display_info() {
    echo ""
    print_success "RoboInvest system is running!"
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo "  Backend:   http://localhost:8000"
    echo "  Frontend:  http://localhost:5173"
    echo "  API Health: http://localhost:8000/api/health"
    echo "  Governor Panel: http://localhost:8000/api/governor/context"
    echo ""
    echo -e "${CYAN}📋 Management:${NC}"
    echo "  To stop all services: ./stop.sh"
    echo "  To monitor backend logs: tail -f logs/backend.log"
    echo "  To monitor frontend logs: tail -f logs/frontend.log"
    echo ""
    echo -e "${CYAN}🔧 Quick Commands:${NC}"
    echo "  Test system: curl http://localhost:8000/api/health"
    echo "  Governor chat: curl -X POST http://localhost:8000/api/governor/conversation -H 'Content-Type: application/json' -d '{\"message\": \"Hello\"}'"
    echo ""
    echo -e "${CYAN}📊 System Status:${NC}"
    echo "  Backend PID: $(cat .backend.pid 2>/dev/null || echo 'Not running')"
    echo "  Frontend PID: $(cat .frontend.pid 2>/dev/null || echo 'Not running')"
    echo ""
}

# Main startup sequence
main() {
    print_header
    
    # Check if already running
    check_running
    
    # Setup and checks
    setup_directories
    check_dependencies
    install_python_deps
    install_frontend_deps
    
    # Initialize databases
    initialize_databases
    
    # Start services
    start_backend
    start_frontend
    
    # Display information
    display_info
    
    print_footer
}

# Handle script interruption
cleanup() {
    print_error "Startup interrupted. Cleaning up..."
    [ -f ".backend.pid" ] && kill $(cat .backend.pid) 2>/dev/null || true
    [ -f ".frontend.pid" ] && kill $(cat .frontend.pid) 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@" 