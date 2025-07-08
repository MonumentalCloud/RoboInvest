#!/bin/bash

# RoboInvest Status Script
# Shows current status of backend + frontend services

echo "📊 RoboInvest Status"
echo "==================="

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# Function to check service
check_service() {
    local url=$1
    local name=$2
    if curl -s "$url" >/dev/null 2>&1; then
        echo "✅ $name: Running"
        return 0
    else
        echo "❌ $name: Not running"
        return 1
    fi
}

# Function to show port usage
show_port() {
    local port=$1
    local name=$2
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "✅ $name (port $port): Running (PID: $pid)"
    else
        echo "❌ $name (port $port): Not running"
    fi
}

echo "🚀 Services:"
show_port 8081 "Backend API"
show_port 5173 "Frontend UI"

echo ""
echo "🌐 Endpoints:"
check_service "http://localhost:8081/api/budget" "Backend API"
check_service "http://localhost:5173/" "Frontend UI"
check_service "http://localhost:5173/api/budget" "API Proxy"

echo ""
echo "📁 Saved PIDs:"
if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/.backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "✅ Backend PID: $BACKEND_PID (running)"
    else
        echo "❌ Backend PID: $BACKEND_PID (not running)"
    fi
else
    echo "❌ No backend PID file"
fi

if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "✅ Frontend PID: $FRONTEND_PID (running)"
    else
        echo "❌ Frontend PID: $FRONTEND_PID (not running)"
    fi
else
    echo "❌ No frontend PID file"
fi

echo ""
echo "📝 Logs:"
if [ -f "$PROJECT_ROOT/backend.log" ]; then
    echo "📄 Backend log: $(wc -l < "$PROJECT_ROOT/backend.log") lines"
else
    echo "❌ No backend log"
fi

if [ -f "$PROJECT_ROOT/frontend.log" ]; then
    echo "📄 Frontend log: $(wc -l < "$PROJECT_ROOT/frontend.log") lines"
else
    echo "❌ No frontend log"
fi

echo ""
echo "🔧 Commands:"
echo "   Start:  ./startup.sh"
echo "   Stop:   ./stop.sh"
echo "   Status: ./status.sh" 