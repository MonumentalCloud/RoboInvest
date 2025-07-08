#!/bin/bash
# Quick demo deployment - no signup required!

echo "🚀 Starting your trading app demo..."

# Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# Start backend in background
echo "🐍 Starting FastAPI backend..."
python3 -m uvicorn backend.api.fastapi_app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background  
echo "⚛️ Starting React frontend..."
cd frontend && npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

echo ""
echo "🌟 Your app is running locally:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "🌍 Making it public with localhost.run (no signup needed)..."
echo "   Press Ctrl+C to stop"
echo ""

# Try localhost.run as primary option (more reliable)
ssh -R 80:localhost:8000 localhost.run

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT