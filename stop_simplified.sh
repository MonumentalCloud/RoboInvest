#!/bin/bash

# Simplified RoboInvest Stop Script
# Cleanly shuts down the streamlined system

set -e

echo "🛑 Stopping Simplified RoboInvest System"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Stop backend process
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_status "Stopping backend process (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        
        # Force kill if still running
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            print_warning "Backend process still running, force killing..."
            kill -9 $BACKEND_PID
        fi
        
        print_success "Backend process stopped"
    else
        print_warning "Backend process not running"
    fi
    rm -f .backend.pid
else
    print_warning "Backend PID file not found"
fi

# Stop frontend process
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        print_status "Stopping frontend process (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        
        # Force kill if still running
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            print_warning "Frontend process still running, force killing..."
            kill -9 $FRONTEND_PID
        fi
        
        print_success "Frontend process stopped"
    else
        print_warning "Frontend process not running"
    fi
    rm -f .frontend.pid
else
    print_warning "Frontend PID file not found"
fi

# Kill any remaining Python processes related to the system
print_status "Cleaning up any remaining processes..."
pkill -f "simplified_fastapi_app.py" || true
pkill -f "uvicorn" || true

# Check if processes are still running
BACKEND_RUNNING=$(pgrep -f "simplified_fastapi_app.py" || true)
FRONTEND_RUNNING=$(pgrep -f "npm run dev" || true)

if [ -z "$BACKEND_RUNNING" ] && [ -z "$FRONTEND_RUNNING" ]; then
    print_success "All processes stopped successfully"
else
    print_warning "Some processes may still be running:"
    if [ ! -z "$BACKEND_RUNNING" ]; then
        echo "  Backend PIDs: $BACKEND_RUNNING"
    fi
    if [ ! -z "$FRONTEND_RUNNING" ]; then
        echo "  Frontend PIDs: $FRONTEND_RUNNING"
    fi
fi

echo ""
print_success "Simplified RoboInvest System stopped!"
print_status "Use './startup_simplified.sh' to restart the system" 