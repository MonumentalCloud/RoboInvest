#!/bin/bash

echo "🚀 RoboInvest Trading App with OpenRouter AI"
echo "============================================"

# Check if backend is already running
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend already running on port 8000"
else
    echo "📡 Starting FastAPI backend on port 8000..."
    cd /workspace/backend
    uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd /workspace
    sleep 3
fi

# Start frontend
echo "⚛️ Starting React frontend on port 5173..."
cd /workspace/frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd /workspace

# Wait for frontend to start
sleep 3

echo ""
echo "🎉 Your AI Trading App is running!"
echo "=================================="
echo "🔗 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo ""
echo "🤖 Features Available:"
echo "   • Live AI thinking with OpenRouter"
echo "   • Real Alpaca paper trading data"
echo "   • Autonomous alpha hunting (every 2 min)"
echo "   • Live P&L dashboard"
echo ""
echo "Press Ctrl+C to stop services"

# Trap to clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# Wait for user to stop
wait