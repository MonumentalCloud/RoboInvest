#!/bin/bash

# RoboInvest Stop Script
# Cleanly stops backend + frontend services

echo "🛑 RoboInvest Stop Script"
echo "========================="

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔪 Killing process on port $port (PID: $pid)"
        kill -9 $pid
        sleep 1
        echo "✅ Port $port is now free"
    else
        echo "✅ Port $port is already free"
    fi
}

# Kill by saved PIDs first
if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/.backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "🔪 Stopping backend (PID: $BACKEND_PID)"
        kill "$BACKEND_PID"
        sleep 2
    fi
    rm -f "$PROJECT_ROOT/.backend.pid"
fi

if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "🔪 Stopping frontend (PID: $FRONTEND_PID)"
        kill "$FRONTEND_PID"
        sleep 2
    fi
    rm -f "$PROJECT_ROOT/.frontend.pid"
fi

# Kill by port as backup
echo "🧹 Cleaning up ports..."
kill_port 8081  # Backend
kill_port 5173  # Frontend

# Kill any remaining processes
pkill -f "uvicorn.*fastapi_app" 2>/dev/null && echo "🔪 Killed remaining uvicorn processes"
pkill -f "vite" 2>/dev/null && echo "🔪 Killed remaining vite processes"

# Clean up log files
if [ -f "$PROJECT_ROOT/backend.log" ]; then
    echo "🗑️  Archiving backend.log"
    mv "$PROJECT_ROOT/backend.log" "$PROJECT_ROOT/backend.log.$(date +%Y%m%d_%H%M%S)"
fi

if [ -f "$PROJECT_ROOT/frontend.log" ]; then
    echo "🗑️  Archiving frontend.log" 
    mv "$PROJECT_ROOT/frontend.log" "$PROJECT_ROOT/frontend.log.$(date +%Y%m%d_%H%M%S)"
fi

echo ""
echo "✅ RoboInvest services stopped"
echo "💡 Run ./startup.sh to restart" 