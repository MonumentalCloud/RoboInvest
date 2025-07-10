#!/bin/bash

# Quick RoboInvest Duplicate Killer
# Emergency script to kill all duplicate processes

echo "🚨 RoboInvest Emergency Duplicate Killer"
echo "======================================="

# Kill all RoboInvest-related processes
echo "🔪 Killing all RoboInvest processes..."

patterns=(
    "start_enhanced_meta_agent.py"
    "background_research_service.py"
    "uvicorn.*fastapi_app"
    "vite"
    "npm run dev"
    "enhanced_meta_agent"
    "meta_agent"
    "research_service"
)

total_killed=0

for pattern in "${patterns[@]}"; do
    pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ ! -z "$pids" ]; then
        count=$(echo "$pids" | wc -w)
        echo "🔪 Killing $count instance(s) of $pattern (PIDs: $pids)"
        echo "$pids" | xargs kill -9 2>/dev/null
        total_killed=$((total_killed + count))
    fi
done

# Also kill processes on our ports
echo "🔪 Killing processes on RoboInvest ports..."
lsof -ti:8081 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo ""
if [ $total_killed -gt 0 ]; then
    echo "✅ Killed $total_killed RoboInvest process(es)"
    echo "⏳ Waiting for processes to terminate..."
    sleep 3
    echo "✅ All RoboInvest processes terminated"
else
    echo "✅ No RoboInvest processes were running"
fi

echo ""
echo "💡 To restart cleanly, run: ./startup.sh" 