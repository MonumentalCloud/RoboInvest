#!/bin/bash

# RoboInvest Startup Script with Enhanced Meta Agent
# Kills existing processes and starts backend + frontend + enhanced meta agent

echo "🤖 RoboInvest Startup Script with Enhanced Meta Agent"
echo "======================================================"

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

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo "📁 Project root: $PROJECT_ROOT"

# Clean up existing processes
echo ""
echo "🧹 Cleaning up existing processes..."
kill_port 8081  # Backend
kill_port 5173  # Frontend

# Kill any existing uvicorn, vite, or meta agent processes
pkill -f "uvicorn.*fastapi_app" 2>/dev/null && echo "🔪 Killed existing uvicorn processes"
pkill -f "vite" 2>/dev/null && echo "🔪 Killed existing vite processes"
pkill -f "enhanced_meta_agent" 2>/dev/null && echo "🔪 Killed existing enhanced meta agent processes"

echo ""
echo "🚀 Starting services..."

# Start backend
echo "📡 Starting backend API server..."
cd "$PROJECT_ROOT"
nohup /usr/bin/python3 -m uvicorn backend.api.fastapi_app:app --reload --port 8081 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Start continuous research service
echo "🔍 Starting continuous research service..."
cd "$PROJECT_ROOT"
nohup /usr/bin/python3 scripts/background_research_service.py > research.log 2>&1 &
RESEARCH_PID=$!
echo "   Research Service PID: $RESEARCH_PID"

# Start enhanced meta agent service
echo "🤖 Starting enhanced meta agent service..."
cd "$PROJECT_ROOT"
nohup /usr/bin/python3 scripts/start_enhanced_meta_agent.py > meta_agent.log 2>&1 &
META_AGENT_PID=$!
echo "   Enhanced Meta Agent PID: $META_AGENT_PID"

# Start frontend
echo "🌐 Starting frontend development server..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."

# Wait for backend
if wait_for_service "http://localhost:8081/api/budget" "Backend API"; then
    echo "   Backend API: http://localhost:8081/api/"
else
    echo "❌ Backend failed to start. Check backend.log for errors."
    exit 1
fi

# Wait for frontend
if wait_for_service "http://localhost:5173/" "Frontend"; then
    echo "   Frontend UI: http://localhost:5173/"
else
    echo "❌ Frontend failed to start. Check frontend.log for errors."
    exit 1
fi

# Test API proxy
echo ""
echo "🔗 Testing API proxy..."
if curl -s "http://localhost:5173/api/budget" >/dev/null 2>&1; then
    echo "✅ API proxy working correctly"
else
    echo "⚠️  API proxy may have issues"
fi

echo ""
echo "🎉 RoboInvest with Enhanced Meta Agent is ready!"
echo "=================================================="
echo "📊 Frontend Dashboard: http://localhost:5173/"
echo "🔧 Backend API:        http://localhost:8081/api/"
echo "🤖 Enhanced Meta Agent: Active and monitoring system"
echo ""
echo "📋 Available Pages:"
echo "   • Dashboard: http://localhost:5173/"
echo "   • Trades:    http://localhost:5173/trades"
echo "   • Positions: http://localhost:5173/positions"
echo "   • Insights:  http://localhost:5173/insights"
echo ""
echo "🔍 Enhanced Meta Agent Features:"
echo "   • Continuous system monitoring"
echo "   • Performance analysis and bottleneck detection"
echo "   • Automated improvement suggestions"
echo "   • Predictive maintenance"
echo "   • Coordination with code fixing agents"
echo ""
echo "📝 Logs:"
echo "   • Backend:      $PROJECT_ROOT/backend.log"
echo "   • Frontend:     $PROJECT_ROOT/frontend.log"
echo "   • Research:     $PROJECT_ROOT/research.log"
echo "   • Meta Agent:   $PROJECT_ROOT/meta_agent.log"
echo ""
echo "📊 Meta Agent Data:"
echo "   • System Reports: $PROJECT_ROOT/meta_agent_data/system_reports/"
echo "   • System Status:  $PROJECT_ROOT/meta_agent_data/system_status.json"
echo "   • Database:       $PROJECT_ROOT/meta_agent_data/enhanced_meta_agent.db"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID $RESEARCH_PID $META_AGENT_PID"
echo "   or use: ./stop.sh"
echo ""
echo "🤖 Ready for autonomous trading with intelligent system monitoring!"

# Save PIDs for stop script
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"
echo "$RESEARCH_PID" > "$PROJECT_ROOT/.research.pid"
echo "$META_AGENT_PID" > "$PROJECT_ROOT/.meta_agent.pid"