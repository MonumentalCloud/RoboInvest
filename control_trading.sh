#!/bin/bash

# RoboInvest Trading Control Script
# Control the autonomous trading system

echo "🎮 RoboInvest Trading Control"
echo "============================="

API_BASE="http://localhost:8081/api/autonomous"

case "${1:-status}" in
    "start")
        echo "🚀 Starting autonomous trading system..."
        curl -X POST "$API_BASE/start"
        echo ""
        ;;
    "stop")
        echo "🛑 Stopping autonomous trading system..."
        curl -X POST "$API_BASE/stop"
        echo ""
        ;;
    "restart")
        echo "🔄 Restarting autonomous trading system..."
        curl -X POST "$API_BASE/restart"
        echo ""
        ;;
    "status")
        echo "📊 Autonomous trading system status:"
        curl -s "$API_BASE/status" | python3 -m json.tool
        echo ""
        ;;
    "enable-auto")
        echo "✅ Enabling automatic trading on startup..."
        echo "   Set AUTO_START_TRADING=true environment variable"
        echo "   Then restart the backend: ./stop.sh && ./startup.sh"
        echo ""
        ;;
    "disable-auto")
        echo "❌ Disabling automatic trading on startup..."
        echo "   Set AUTO_START_TRADING=false environment variable (or unset it)"
        echo "   Then restart the backend: ./stop.sh && ./startup.sh"
        echo ""
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [start|stop|restart|status|enable-auto|disable-auto|help]"
        echo ""
        echo "Commands:"
        echo "  start       - Start autonomous trading system"
        echo "  stop        - Stop autonomous trading system"
        echo "  restart     - Restart autonomous trading system"
        echo "  status      - Check system status (default)"
        echo "  enable-auto - Enable automatic trading on startup"
        echo "  disable-auto- Disable automatic trading on startup"
        echo "  help        - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start trading"
        echo "  $0 stop     # Stop trading"
        echo "  $0 status   # Check if trading is running"
        echo ""
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 