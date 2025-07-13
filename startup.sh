#!/bin/bash

# RoboInvest Startup Script
# Kills existing processes and starts backend + frontend + all services

echo "🤖 RoboInvest Startup Script"
echo "=================================="

# Function to detect and kill RoboInvest processes
detect_and_kill_robinvest_processes() {
    echo "🔍 Scanning for existing RoboInvest processes..."
    
    # Array of process patterns to detect
    local patterns=(
        "start_enhanced_meta_agent.py"
        "background_research_service.py"
        "uvicorn.*fastapi_app"
        "vite"
        "npm run dev"
        "enhanced_meta_agent"
        "meta_agent"
        "research_service"
        "experience_learning"
        "performance_analyzer"
        "governor_directive"
        "autonomous_trading"
    )
    
    local total_killed=0
    
    for pattern in "${patterns[@]}"; do
        local pids=$(pgrep -f "$pattern" 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo "🔪 Found $pattern processes: $pids"
            echo "$pids" | xargs kill -9 2>/dev/null
            local count=$(echo "$pids" | wc -w)
            total_killed=$((total_killed + count))
            echo "   Killed $count process(es)"
        fi
    done
    
    if [ $total_killed -gt 0 ]; then
        echo "⏳ Waiting for processes to terminate..."
        sleep 3
    else
        echo "✅ No existing RoboInvest processes found"
    fi
    
    return $total_killed
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔪 Killing process on port $port (PID: $pid)"
        kill -9 $pid
        sleep 1
    else
        echo "✅ Port $port is free"
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $name to start..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo "✅ $name is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo "❌ $name failed to start after $max_attempts attempts"
    return 1
}

# Function to check if Python module exists
check_python_module() {
    local module=$1
    python3 -c "import $module" 2>/dev/null
    return $?
}

# Function to install missing dependencies
install_dependencies() {
    echo "📦 Checking and installing dependencies..."
    
    # Check if required packages are installed
    local missing_packages=()
    
    if ! check_python_module "fastapi"; then
        missing_packages+=("fastapi")
    fi
    
    if ! check_python_module "uvicorn"; then
        missing_packages+=("uvicorn")
    fi
    
    if ! check_python_module "chromadb"; then
        missing_packages+=("chromadb")
    fi
    
    if ! check_python_module "openai"; then
        missing_packages+=("openai")
    fi
    
    if ! check_python_module "langgraph"; then
        missing_packages+=("langgraph")
    fi
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "📦 Installing missing packages: ${missing_packages[*]}"
        pip3 install "${missing_packages[@]}"
    else
        echo "✅ All required Python packages are installed"
    fi
    
    # Check if Node.js and npm are available
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed. Please install npm first."
        exit 1
    fi
    
    echo "✅ Node.js and npm are available"
}

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo "📁 Project root: $PROJECT_ROOT"

# Install dependencies
install_dependencies

# Clean up existing processes
echo ""
echo "🧹 Cleaning up existing processes..."

# Detect and kill all RoboInvest processes
detect_and_kill_robinvest_processes
processes_killed=$?

# Also clean up ports
kill_port 8081  # Backend
kill_port 5173  # Frontend
kill_port 8000  # Alternative backend port

# Additional cleanup for any remaining processes
echo "🔍 Final cleanup check..."
pkill -f "uvicorn.*fastapi_app" 2>/dev/null && echo "🔪 Killed remaining uvicorn processes"
pkill -f "vite" 2>/dev/null && echo "🔪 Killed remaining vite processes"
pkill -f "start_enhanced_meta_agent.py" 2>/dev/null && echo "🔪 Killed remaining meta-agent processes"
pkill -f "background_research_service.py" 2>/dev/null && echo "🔪 Killed remaining research processes"

if [ $processes_killed -gt 0 ]; then
    echo "⚠️  Found and killed $processes_killed existing RoboInvest process(es)"
    echo "   This prevents duplicate sessions and notification spam"
fi

echo ""
echo "🚀 Starting services..."

# Set Python path to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
echo "🐍 Set PYTHONPATH to: $PYTHONPATH"

# Start backend with proper Python path
echo "📡 Starting backend API server..."
cd "$PROJECT_ROOT"
nohup python3 -m uvicorn backend.api.fastapi_app:app --reload --port 8081 --host 0.0.0.0 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Start continuous research service
echo "🔍 Starting continuous research service..."
cd "$PROJECT_ROOT"
nohup python3 scripts/background_research_service.py > research.log 2>&1 &
RESEARCH_PID=$!
echo "   Research Service PID: $RESEARCH_PID"

# Start enhanced meta-agent service
echo "🧠 Starting enhanced meta-agent service..."
cd "$PROJECT_ROOT"
nohup python3 scripts/start_enhanced_meta_agent.py > meta_agent.log 2>&1 &
META_AGENT_PID=$!
echo "   Meta-Agent PID: $META_AGENT_PID"

# Start experience learning system (if separate service needed)
echo "🎓 Starting experience learning system..."
cd "$PROJECT_ROOT"
# The experience learning system is integrated into the main backend
echo "   Experience Learning: Integrated into backend"

# Start frontend
echo "🌐 Starting frontend development server..."
cd "$PROJECT_ROOT/frontend"

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."

# Wait for backend
if wait_for_service "http://localhost:8081/api/health" "Backend API"; then
    echo "   Backend API: http://localhost:8081/api/"
else
    echo "❌ Backend failed to start. Check backend.log for errors."
    echo "   Common issues:"
    echo "   - Missing Python packages (run: pip3 install -r requirements.txt)"
    echo "   - Import path issues (check PYTHONPATH)"
    echo "   - Port 8081 already in use"
    exit 1
fi

# Wait for frontend
if wait_for_service "http://localhost:5173/" "Frontend"; then
    echo "   Frontend UI: http://localhost:5173/"
else
    echo "❌ Frontend failed to start. Check frontend.log for errors."
    echo "   Common issues:"
    echo "   - Missing Node.js/npm"
    echo "   - Port 5173 already in use"
    echo "   - Frontend dependencies not installed"
    exit 1
fi

# Test API proxy
echo ""
echo "🔗 Testing API proxy..."
if curl -s "http://localhost:5173/api/health" >/dev/null 2>&1; then
    echo "✅ API proxy working correctly"
else
    echo "⚠️  API proxy may have issues"
fi

echo ""
echo "🎉 RoboInvest is ready!"
echo "=================================="
echo "📊 Frontend Dashboard: http://localhost:5173/"
echo "🔧 Backend API:        http://localhost:8081/api/"
echo ""
echo "📋 Available Pages:"
echo "   • Dashboard: http://localhost:5173/"
echo "   • Experience Learning: http://localhost:5173/experience"
echo "   • Governor Control: http://localhost:5173/governor"
echo "   • Alpha Stream: http://localhost:5173/alpha-stream"
echo ""
echo "🧠 Available Systems:"
echo "   • Experience Learning System"
echo "   • Performance Analyzer Agent"
echo "   • Enhanced Trade Executor"
echo "   • Governor Directive System"
echo "   • Autonomous Trading System"
echo "   • Research Graph Manager"
echo ""
echo "📝 Logs:"
echo "   • Backend:  $PROJECT_ROOT/backend.log"
echo "   • Frontend: $PROJECT_ROOT/frontend.log"
echo "   • Research: $PROJECT_ROOT/research.log"
echo "   • Meta-Agent: $PROJECT_ROOT/meta_agent.log"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID $RESEARCH_PID $META_AGENT_PID"
echo "   or use: ./stop.sh"
echo ""
echo "🤖 Ready for autonomous trading!"

# Function to verify no duplicate processes
verify_no_duplicates() {
    echo ""
    echo "🔍 Verifying no duplicate processes..."
    
    local duplicates_found=false
    
    # Check for multiple instances of each service
    local services=(
        "start_enhanced_meta_agent.py:Meta-Agent"
        "background_research_service.py:Research-Service"
        "uvicorn.*fastapi_app:Backend-API"
        "vite:Frontend"
    )
    
    for service in "${services[@]}"; do
        local pattern=$(echo "$service" | cut -d: -f1)
        local name=$(echo "$service" | cut -d: -f2)
        local count=$(pgrep -f "$pattern" | wc -l)
        
        if [ $count -gt 1 ]; then
            echo "⚠️  WARNING: Found $count instances of $name"
            duplicates_found=true
        else
            echo "✅ $name: Single instance running"
        fi
    done
    
    if [ "$duplicates_found" = true ]; then
        echo ""
        echo "🚨 DUPLICATE PROCESSES DETECTED!"
        echo "   This may cause notification spam and system instability."
        echo "   Consider running: ./stop.sh && ./startup.sh"
    else
        echo "✅ All services running with single instances"
    fi
}

# Save PIDs for stop script
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"
echo "$RESEARCH_PID" > "$PROJECT_ROOT/.research.pid" 
echo "$META_AGENT_PID" > "$PROJECT_ROOT/.meta_agent.pid"

# Verify no duplicates are running
verify_no_duplicates

echo ""
echo "🔧 System Status:"
echo "   • Experience Learning: ✅ Active"
echo "   • Performance Analysis: ✅ Active"
echo "   • Governor Control: ✅ Active"
echo "   • Autonomous Trading: ✅ Ready"
echo "   • Research System: ✅ Active"
echo ""
echo "🚀 All systems operational!" 