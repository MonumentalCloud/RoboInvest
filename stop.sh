#!/bin/bash

# RoboInvest - Unified Stop Script
# Stops the complete autonomous trading system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
    echo -e "${PURPLE}🛑 RoboInvest System Shutdown${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_footer() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}✅ RoboInvest System Stopped${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Stop backend
stop_backend() {
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        print_status "Stopping backend (PID: $BACKEND_PID)..."
        
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            sleep 2
            
            # Check if process is still running
            if kill -0 $BACKEND_PID 2>/dev/null; then
                print_warning "Backend process still running, force killing..."
                kill -9 $BACKEND_PID
                sleep 1
            fi
            
            print_success "Backend stopped"
        else
            print_warning "Backend process not running (PID: $BACKEND_PID)"
        fi
        
        rm -f .backend.pid
    else
        print_warning "No backend PID file found"
    fi
}

# Stop frontend
stop_frontend() {
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        print_status "Stopping frontend (PID: $FRONTEND_PID)..."
        
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            sleep 2
            
            # Check if process is still running
            if kill -0 $FRONTEND_PID 2>/dev/null; then
                print_warning "Frontend process still running, force killing..."
                kill -9 $FRONTEND_PID
                sleep 1
            fi
            
            print_success "Frontend stopped"
        else
            print_warning "Frontend process not running (PID: $FRONTEND_PID)"
        fi
        
        rm -f .frontend.pid
    else
        print_warning "No frontend PID file found"
    fi
}

# Stop any other RoboInvest processes
stop_other_processes() {
    print_status "Checking for other RoboInvest processes..."
    
    # Find and stop any remaining RoboInvest processes
    PIDS=$(pgrep -f "roboinvest\|uvicorn.*fastapi_app\|npm.*dev" 2>/dev/null || true)
    
    if [ -n "$PIDS" ]; then
        print_warning "Found additional RoboInvest processes: $PIDS"
        for pid in $PIDS; do
            print_status "Stopping process $pid..."
            kill $pid 2>/dev/null || true
        done
        sleep 2
        
        # Force kill any remaining processes
        PIDS=$(pgrep -f "roboinvest\|uvicorn.*fastapi_app\|npm.*dev" 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            print_warning "Force killing remaining processes: $PIDS"
            for pid in $PIDS; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
    else
        print_success "No additional RoboInvest processes found"
    fi
}

# Clean up temporary files
cleanup_files() {
    print_status "Cleaning up temporary files..."
    
    # Remove PID files
    rm -f .backend.pid .frontend.pid
    
    # Remove any temporary files
    rm -f *.tmp *.log.tmp 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Check if system is running
check_running() {
    local running=false
    
    if [ -f ".backend.pid" ] && kill -0 $(cat .backend.pid) 2>/dev/null; then
        running=true
    fi
    
    if [ -f ".frontend.pid" ] && kill -0 $(cat .frontend.pid) 2>/dev/null; then
        running=true
    fi
    
    if ! $running; then
        # Check for any RoboInvest processes
        if pgrep -f "roboinvest\|uvicorn.*fastapi_app\|npm.*dev" >/dev/null 2>&1; then
            running=true
        fi
    fi
    
    if ! $running; then
        print_warning "RoboInvest does not appear to be running"
        return 1
    fi
    
    return 0
}

# Display shutdown information
display_info() {
    echo ""
    print_success "RoboInvest system shutdown completed!"
    echo ""
    echo -e "${BLUE}📋 What was stopped:${NC}"
    echo "  ✅ Backend API server (port 8000)"
    echo "  ✅ Frontend development server (port 5173)"
    echo "  ✅ All related RoboInvest processes"
    echo ""
    echo -e "${BLUE}🧹 Cleanup performed:${NC}"
    echo "  ✅ PID files removed"
    echo "  ✅ Temporary files cleaned"
    echo ""
    echo -e "${BLUE}🚀 To restart:${NC}"
    echo "  ./start.sh"
    echo ""
}

# Main shutdown sequence
main() {
    print_header
    
    # Check if system is running
    if ! check_running; then
        print_warning "No running RoboInvest processes found"
        cleanup_files
        print_footer
        exit 0
    fi
    
    # Stop services in order
    stop_frontend
    stop_backend
    stop_other_processes
    
    # Cleanup
    cleanup_files
    
    # Display information
    display_info
    
    print_footer
}

# Handle script interruption
cleanup() {
    print_error "Stop script interrupted. Forcing cleanup..."
    stop_other_processes
    cleanup_files
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@" 