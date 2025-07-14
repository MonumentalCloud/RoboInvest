#!/bin/bash

# Simplified RoboInvest Startup Script
# Uses the new streamlined architecture with governor-centric design

set -e

echo "🚀 Starting Simplified RoboInvest System"
echo "========================================"

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

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/api/simplified_fastapi_app.py" ]; then
    print_error "Please run this script from the RoboInvest root directory"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p research_data

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Installing basic dependencies..."
    pip install fastapi uvicorn sqlite3 asyncio websockets
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating default configuration..."
    cat > .env << EOF
# Simplified RoboInvest Configuration
AUTO_START_TRADING=false
SYSTEM_MODE=paper_trading
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=5173
EOF
fi

# Load environment variables
print_status "Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Kill any existing processes
print_status "Checking for existing processes..."
pkill -f "simplified_fastapi_app.py" || true
pkill -f "uvicorn" || true

# Start the simplified backend
print_status "Starting simplified FastAPI backend..."
python backend/api/simplified_fastapi_app.py &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

# Wait for backend to start
print_status "Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_success "Backend started successfully on port 8000"
else
    print_error "Backend failed to start"
    exit 1
fi

# Start frontend if it exists
if [ -d "frontend" ]; then
    print_status "Starting frontend..."
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../.frontend.pid
    cd ..
    
    print_success "Frontend started successfully on port 5173"
else
    print_warning "Frontend directory not found. Skipping frontend startup."
fi

# Display system status
echo ""
echo "🎯 Simplified RoboInvest System Status"
echo "======================================"
print_success "Backend: http://localhost:8000"
print_success "API Health: http://localhost:8000/api/health"
print_success "Governor Panel: http://localhost:8000/api/governor/context"

if [ -d "frontend" ]; then
    print_success "Frontend: http://localhost:5173"
fi

echo ""
echo "🔧 Available Endpoints:"
echo "  - GET  /api/health                    - System health check"
echo "  - GET  /api/governor/context          - System context"
echo "  - GET  /api/governor/pulse            - System pulse"
echo "  - GET  /api/governor/directives       - Active directives"
echo "  - POST /api/governor/directives       - Issue new directive"
echo "  - POST /api/governor/conversation     - Natural language control"
echo "  - GET  /api/dashboard/performance     - Performance metrics"
echo "  - GET  /api/dashboard/trades          - Recent trades"
echo "  - GET  /api/dashboard/positions       - Current positions"
echo "  - POST /api/autonomous/start          - Start autonomous system"
echo "  - POST /api/autonomous/stop           - Stop autonomous system"
echo "  - GET  /api/autonomous/status         - Autonomous system status"
echo ""
echo "🔌 WebSocket Endpoints:"
echo "  - /ws/governor                        - Governor control panel"
echo "  - /ws/dashboard                       - Dashboard updates"
echo "  - /ws/stream                          - Unified real-time stream"
echo ""

# Show how to start autonomous trading
echo "🚀 To start autonomous trading:"
echo "  curl -X POST http://localhost:8000/api/autonomous/start"
echo ""
echo "💬 To use natural language control:"
echo "  curl -X POST http://localhost:8000/api/governor/conversation \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"Show me the current system status\"}'"
echo ""

print_success "Simplified RoboInvest System is ready!"
print_status "Use 'tail -f logs/backend.log' to monitor backend logs"
print_status "Use './stop_simplified.sh' to stop the system"

# Keep script running to maintain background processes
wait 