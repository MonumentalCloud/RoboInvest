#!/bin/bash

# Unified RoboInvest Stop Script
# Stops both backend (FastAPI) and frontend (Vite/React)

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

print_status "Stopping backend (FastAPI)..."
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
    print_success "Backend process stopped."
else
    print_warning ".backend.pid not found. Attempting to kill uvicorn..."
    pkill -f "uvicorn" || true
    pkill -f "fastapi_app.py" || true
fi

print_status "Stopping frontend (Vite/React)..."
if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
    print_success "Frontend process stopped."
else
    print_warning ".frontend.pid not found. Attempting to kill npm run dev..."
    pkill -f "npm run dev" || true
fi

print_status "Cleaning up ports 8000 and 5173..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

print_success "All RoboInvest services stopped."
print_status "If you see any lingering processes, use 'ps aux | grep python' or 'ps aux | grep npm' to find and kill them manually." 