#!/bin/bash

# Unified RoboInvest Startup Script
# Starts both backend (advanced FastAPI) and frontend (Vite/React)

set -e

# Always run from the directory containing this script (project root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data

print_status "Killing any old backend/frontend processes..."
pkill -f "fastapi_app.py" || true
pkill -f "uvicorn" || true
pkill -f "npm run dev" || true

# Activate virtual environment if present
if [ -d ".venv" ]; then
    print_status "Activating virtual environment..."
    source .venv/bin/activate
else
    print_warning "No .venv found, using system python."
fi

# Install backend dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Skipping backend dependency install."
fi

# Start backend (advanced FastAPI app)
print_status "Starting backend (FastAPI, port 8000)..."
PYTHONPATH=$(pwd) uvicorn backend.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

# Wait for backend to start
sleep 5
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_success "Backend started successfully on port 8000"
else
    print_error "Backend failed to start. Check logs/backend.log for details."
    exit 1
fi

# Start frontend
if [ -d "frontend" ]; then
    print_status "Starting frontend (Vite, port 5173)..."
    FRONTEND_DIR="$SCRIPT_DIR/frontend"
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
    cd "$SCRIPT_DIR"
    print_success "Frontend started successfully on port 5173"
else
    print_warning "Frontend directory not found. Skipping frontend startup."
fi

# Print status and instructions
print_success "RoboInvest system is running!"
echo ""
echo "Backend:   http://localhost:8000"
echo "Frontend:  http://localhost:5173"
echo "API Health: http://localhost:8000/api/health"
echo "Governor Panel: http://localhost:8000/api/governor/context"
echo ""
print_status "To stop all services, run: ./stop.sh"
print_status "To monitor backend logs: tail -f logs/backend.log"
print_status "To monitor frontend logs: tail -f logs/frontend.log"
echo ""
wait 