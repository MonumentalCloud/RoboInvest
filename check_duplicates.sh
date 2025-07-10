#!/bin/bash

# RoboInvest Duplicate Process Checker
# Standalone script to detect and optionally kill duplicate processes

echo "🔍 RoboInvest Duplicate Process Checker"
echo "======================================"

# Function to check for duplicate processes
check_duplicates() {
    local duplicates_found=false
    local total_processes=0
    
    # Array of process patterns to check
    local patterns=(
        "start_enhanced_meta_agent.py:Meta-Agent"
        "background_research_service.py:Research-Service"
        "uvicorn.*fastapi_app:Backend-API"
        "vite:Frontend"
        "npm run dev:Frontend-Dev"
    )
    
    echo "📊 Current RoboInvest Processes:"
    echo "--------------------------------"
    
    for pattern in "${patterns[@]}"; do
        local process_pattern=$(echo "$pattern" | cut -d: -f1)
        local service_name=$(echo "$pattern" | cut -d: -f2)
        local pids=$(pgrep -f "$process_pattern" 2>/dev/null)
        
        if [ ! -z "$pids" ]; then
            local count=$(echo "$pids" | wc -w)
            total_processes=$((total_processes + count))
            
            if [ $count -gt 1 ]; then
                echo "⚠️  $service_name: $count instances (PIDs: $pids)"
                duplicates_found=true
            else
                echo "✅ $service_name: 1 instance (PID: $pids)"
            fi
        else
            echo "❌ $service_name: Not running"
        fi
    done
    
    echo "--------------------------------"
    echo "📈 Total RoboInvest processes: $total_processes"
    
    if [ "$duplicates_found" = true ]; then
        echo ""
        echo "🚨 DUPLICATE PROCESSES DETECTED!"
        echo "   This may cause:"
        echo "   • Notification spam"
        echo "   • System instability"
        echo "   • Resource conflicts"
        echo "   • Inconsistent behavior"
        echo ""
        echo "💡 To fix this, run:"
        echo "   ./stop.sh && ./startup.sh"
        echo ""
        echo "🔪 Or kill duplicates manually:"
        echo "   ./kill_duplicates.sh"
        return 1
    else
        echo ""
        echo "✅ No duplicate processes found"
        echo "   System is running cleanly"
        return 0
    fi
}

# Function to kill duplicate processes
kill_duplicates() {
    echo "🔪 Killing duplicate RoboInvest processes..."
    
    local patterns=(
        "start_enhanced_meta_agent.py"
        "background_research_service.py"
        "uvicorn.*fastapi_app"
        "vite"
        "npm run dev"
    )
    
    local total_killed=0
    
    for pattern in "${patterns[@]}"; do
        local pids=$(pgrep -f "$pattern" 2>/dev/null)
        if [ ! -z "$pids" ]; then
            local count=$(echo "$pids" | wc -w)
            if [ $count -gt 1 ]; then
                echo "🔪 Killing $count instances of $pattern (PIDs: $pids)"
                echo "$pids" | xargs kill -9 2>/dev/null
                total_killed=$((total_killed + count))
            fi
        fi
    done
    
    if [ $total_killed -gt 0 ]; then
        echo "✅ Killed $total_killed duplicate process(es)"
        echo "⏳ Waiting for processes to terminate..."
        sleep 2
        echo "🔍 Re-checking for duplicates..."
        check_duplicates
    else
        echo "✅ No duplicate processes found to kill"
    fi
}

# Main execution
case "${1:-check}" in
    "check"|"")
        check_duplicates
        ;;
    "kill")
        kill_duplicates
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [check|kill|help]"
        echo ""
        echo "Commands:"
        echo "  check  - Check for duplicate processes (default)"
        echo "  kill   - Kill duplicate processes"
        echo "  help   - Show this help message"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 