#!/bin/bash

# RoboInvest Status Script
# Checks the status of all RoboInvest services

echo "🔍 RoboInvest System Status"
echo "==========================="

# Function to check if process is running
check_process() {
    local pattern=$1
    local service_name=$2
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ ! -z "$pids" ]; then
        local count=$(echo "$pids" | wc -w)
        echo "✅ $service_name: Running ($count instance(s), PID: $pids)"
        return 0
    else
        echo "❌ $service_name: Not running"
        return 1
    fi
}

# Function to check if port is in use
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        echo "✅ $service_name: Port $port in use (PID: $pid)"
        return 0
    else
        echo "❌ $service_name: Port $port not in use"
        return 1
    fi
}

# Function to check if URL is accessible
check_url() {
    local url=$1
    local service_name=$2
    
    if curl -s "$url" >/dev/null 2>&1; then
        echo "✅ $service_name: Accessible at $url"
        return 0
    else
        echo "❌ $service_name: Not accessible at $url"
        return 1
    fi
}

# Function to check log file
check_log() {
    local log_file=$1
    local service_name=$2
    
    if [ -f "$log_file" ]; then
        local size=$(du -h "$log_file" | cut -f1)
        local last_modified=$(stat -f "%Sm" "$log_file" 2>/dev/null || stat -c "%y" "$log_file" 2>/dev/null)
        echo "📝 $service_name: Log file exists (Size: $size, Modified: $last_modified)"
        return 0
    else
        echo "❌ $service_name: Log file not found"
        return 1
    fi
}

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Check Python environment
echo "🐍 Python Environment:"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    echo "✅ Python3: $python_version"
else
    echo "❌ Python3: Not found"
fi

if command -v pip3 &> /dev/null; then
    echo "✅ pip3: Available"
else
    echo "❌ pip3: Not found"
fi

echo ""

# Check Node.js environment
echo "📦 Node.js Environment:"
if command -v node &> /dev/null; then
    node_version=$(node --version 2>&1)
    echo "✅ Node.js: $node_version"
else
    echo "❌ Node.js: Not found"
fi

if command -v npm &> /dev/null; then
    npm_version=$(npm --version 2>&1)
    echo "✅ npm: $npm_version"
else
    echo "❌ npm: Not found"
fi

echo ""

# Check processes
echo "🔄 Process Status:"
check_process "uvicorn.*fastapi_app" "Backend API"
check_process "vite" "Frontend Dev Server"
check_process "start_enhanced_meta_agent.py" "Enhanced Meta Agent"
check_process "background_research_service.py" "Research Service"
check_process "experience_learning" "Experience Learning System"
check_process "performance_analyzer" "Performance Analyzer"
check_process "governor_directive" "Governor Directive System"

echo ""

# Check ports
echo "🔌 Port Status:"
check_port 8081 "Backend API"
check_port 5173 "Frontend Dev Server"
check_port 8000 "Alternative Backend"

echo ""

# Check URLs
echo "🌐 Service Accessibility:"
check_url "http://localhost:8081/api/health" "Backend API"
check_url "http://localhost:5173/" "Frontend UI"
check_url "http://localhost:5173/api/health" "Frontend API Proxy"

echo ""

# Check log files
echo "📝 Log Files:"
check_log "$PROJECT_ROOT/backend.log" "Backend"
check_log "$PROJECT_ROOT/frontend.log" "Frontend"
check_log "$PROJECT_ROOT/research.log" "Research Service"
check_log "$PROJECT_ROOT/meta_agent.log" "Meta Agent"

echo ""

# Check PID files
echo "🆔 PID Files:"
for pid_file in ".backend.pid" ".frontend.pid" ".research.pid" ".meta_agent.pid"; do
    if [ -f "$PROJECT_ROOT/$pid_file" ]; then
        pid=$(cat "$PROJECT_ROOT/$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ $pid_file: Valid (PID: $pid)"
        else
            echo "⚠️  $pid_file: Invalid (PID: $pid not running)"
        fi
    else
        echo "❌ $pid_file: Not found"
    fi
done

echo ""

# Check ChromaDB
echo "🗄️  ChromaDB Status:"
if [ -d "$PROJECT_ROOT/chroma" ]; then
    echo "✅ ChromaDB directory exists"
    chroma_size=$(du -sh "$PROJECT_ROOT/chroma" 2>/dev/null | cut -f1)
    echo "   Size: $chroma_size"
else
    echo "❌ ChromaDB directory not found"
fi

echo ""

# Check environment variables
echo "🔧 Environment Variables:"
env_vars=("OPENAI_API_KEY" "ALPACA_API_KEY" "ALPACA_SECRET_KEY" "POLYGON_API_KEY")
for var in "${env_vars[@]}"; do
    if [ ! -z "${!var}" ]; then
        echo "✅ $var: Set"
    else
        echo "❌ $var: Not set"
    fi
done

echo ""

# Check for duplicate processes
echo "🔍 Duplicate Process Check:"
duplicates_found=false

services=(
    "start_enhanced_meta_agent.py:Meta Agent"
    "background_research_service.py:Research Service"
    "uvicorn.*fastapi_app:Backend API"
    "vite:Frontend"
)

for service in "${services[@]}"; do
    pattern=$(echo "$service" | cut -d: -f1)
    name=$(echo "$service" | cut -d: -f2)
    count=$(pgrep -f "$pattern" | wc -l)
    
    if [ $count -gt 1 ]; then
        echo "⚠️  $name: $count instances running (DUPLICATE!)"
        duplicates_found=true
    elif [ $count -eq 1 ]; then
        echo "✅ $name: Single instance running"
    else
        echo "❌ $name: Not running"
    fi
done

echo ""

# Overall system status
echo "📊 Overall System Status:"
backend_ok=$(check_url "http://localhost:8081/api/health" "Backend" 2>/dev/null; echo $?)
frontend_ok=$(check_url "http://localhost:5173/" "Frontend" 2>/dev/null; echo $?)

if [ $backend_ok -eq 0 ] && [ $frontend_ok -eq 0 ]; then
    echo "🎉 System Status: HEALTHY"
    echo "   All core services are running and accessible"
elif [ $backend_ok -eq 0 ]; then
    echo "⚠️  System Status: PARTIAL"
    echo "   Backend is running but frontend may have issues"
elif [ $frontend_ok -eq 0 ]; then
    echo "⚠️  System Status: PARTIAL"
    echo "   Frontend is running but backend may have issues"
else
    echo "❌ System Status: UNHEALTHY"
    echo "   Core services are not accessible"
fi

if [ "$duplicates_found" = true ]; then
    echo "⚠️  WARNING: Duplicate processes detected"
    echo "   Consider running: ./stop.sh && ./startup.sh"
fi

echo ""
echo "🔧 Quick Actions:"
echo "   • Restart system: ./stop.sh && ./startup.sh"
echo "   • View logs: tail -f backend.log frontend.log"
echo "   • Check processes: ps aux | grep -E '(uvicorn|vite|meta_agent)'"
echo "   • Emergency cleanup: pkill -f 'robinvest|fastapi_app|vite'" 