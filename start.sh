#!/usr/bin/env bash
# Start both the FastAPI backend (port 8000) and React/MUI Vite frontend (port 5173)
# Usage:  ./start.sh
# Ensure you have run `pip install -r requirements.txt` (backend) and `npm i` inside ./frontend (frontend) once beforehand.

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
  echo "Loading environment from .env"
  set -a; source .env; set +a
fi

BACKEND_CMD="python3 -m uvicorn backend.api.fastapi_app:app --reload --port 8000"
FRONTEND_CMD="cd frontend && npm run dev -- --port 5173"

# Start backend in background and capture PID
echo "Starting FastAPI backend on http://localhost:8000 ..."
$BACKEND_CMD &
BACK_PID=$!

# Start frontend (foreground)
echo "Starting React frontend on http://localhost:5173 ..."
exec bash -c "$FRONTEND_CMD"

# When frontend process exits, kill backend
kill $BACK_PID 