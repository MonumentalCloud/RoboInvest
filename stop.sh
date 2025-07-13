#!/bin/bash

# RoboInvest Stop Script
# Stops all RoboInvest processes and cleans up

echo "🛑 RoboInvest Stop Script"
echo "=========================="

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ ! -z "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "🔪 Killing $service_name (PID: $pid)"
            kill -9 "$pid" 2>/dev/null
            rm -f "$pid_file"
        else
            echo "✅ $service_name already stopped"
            rm -f "$pid_file"
        fi
    else
        echo "✅ $service_name PID file not found"
    fi
}

# Function to kill processes by pattern
kill_by_pattern() {
    local pattern=$1
    local service_name=$2
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🔪 Killing $service_name processes: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null
    else
        echo "✅ No $service_name processes found"
    fi
}

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo "📁 Project root: $PROJECT_ROOT"

# Kill processes by PID files
echo ""
echo "🛑 Stopping services by PID files..."
kill_by_pid_file "$PROJECT_ROOT/.backend.pid" "Backend API"
kill_by_pid_file "$PROJECT_ROOT/.frontend.pid" "Frontend"
kill_by_pid_file "$PROJECT_ROOT/.research.pid" "Research Service"
kill_by_pid_file "$PROJECT_ROOT/.meta_agent.pid" "Meta Agent"

# Kill processes by pattern (backup method)
echo ""
echo "🔍 Scanning for remaining RoboInvest processes..."

# Array of process patterns to kill
local patterns=(
    "start_enhanced_meta_agent.py:Enhanced Meta Agent"
    "background_research_service.py:Research Service"
    "uvicorn.*fastapi_app:Backend API"
    "vite:Frontend"
    "npm run dev:Frontend Dev"
    "enhanced_meta_agent:Meta Agent"
    "meta_agent:Meta Agent"
    "research_service:Research Service"
    "experience_learning:Experience Learning"
    "performance_analyzer:Performance Analyzer"
    "governor_directive:Governor Directive"
    "autonomous_trading:Autonomous Trading"
    "chromadb:ChromaDB"
    "langgraph:LangGraph"
)

for pattern_info in "${patterns[@]}"; do
    pattern=$(echo "$pattern_info" | cut -d: -f1)
    service_name=$(echo "$pattern_info" | cut -d: -f2)
    kill_by_pattern "$pattern" "$service_name"
done

# Kill processes on specific ports
echo ""
echo "🔌 Freeing up ports..."
kill_by_pattern "8081" "Backend Port 8081"
kill_by_pattern "5173" "Frontend Port 5173"
kill_by_pattern "8000" "Alternative Backend Port 8000"

# Additional cleanup
echo ""
echo "🧹 Additional cleanup..."
pkill -f "uvicorn.*fastapi_app" 2>/dev/null && echo "🔪 Killed remaining uvicorn processes"
pkill -f "vite" 2>/dev/null && echo "🔪 Killed remaining vite processes"
pkill -f "start_enhanced_meta_agent.py" 2>/dev/null && echo "🔪 Killed remaining meta-agent processes"
pkill -f "background_research_service.py" 2>/dev/null && echo "🔪 Killed remaining research processes"
pkill -f "experience_learning" 2>/dev/null && echo "🔪 Killed remaining experience learning processes"
pkill -f "performance_analyzer" 2>/dev/null && echo "🔪 Killed remaining performance analyzer processes"

# Wait for processes to terminate
echo ""
echo "⏳ Waiting for processes to terminate..."
sleep 3

# Final verification
echo ""
echo "🔍 Final verification..."

# Check if any RoboInvest processes are still running
remaining_processes=$(pgrep -f "robinvest\|fastapi_app\|vite\|meta_agent\|research_service" 2>/dev/null)

if [ ! -z "$remaining_processes" ]; then
    echo "⚠️  Some processes may still be running:"
    echo "$remaining_processes" | while read pid; do
        if [ ! -z "$pid" ]; then
            ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null
        fi
    done
    echo ""
    echo "💡 You may need to manually kill these processes:"
    echo "   kill -9 $remaining_processes"
else
    echo "✅ All RoboInvest processes have been stopped"
fi

# Clean up PID files
echo ""
echo "🧹 Cleaning up PID files..."
rm -f "$PROJECT_ROOT/.backend.pid"
rm -f "$PROJECT_ROOT/.frontend.pid"
rm -f "$PROJECT_ROOT/.research.pid"
rm -f "$PROJECT_ROOT/.meta_agent.pid"
echo "✅ PID files cleaned up"

# Check if ports are free
echo ""
echo "🔌 Checking port availability..."
if lsof -ti:8081 >/dev/null 2>&1; then
    echo "⚠️  Port 8081 is still in use"
else
    echo "✅ Port 8081 is free"
fi

if lsof -ti:5173 >/dev/null 2>&1; then
    echo "⚠️  Port 5173 is still in use"
else
    echo "✅ Port 5173 is free"
fi

echo ""
echo "🎉 RoboInvest has been stopped!"
echo "================================"
echo ""
echo "📝 To restart the system:"
echo "   ./startup.sh"
echo ""
echo "🔧 To check system status:"
echo "   ./status.sh" 