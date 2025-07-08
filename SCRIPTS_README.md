# 🤖 RoboInvest Management Scripts

Simple scripts to manage your RoboInvest trading system.

## 🚀 Quick Start

```bash
# Start both backend and frontend
./startup.sh

# Check status
./status.sh

# Stop all services
./stop.sh
```

## 📋 Scripts

### `./startup.sh`
- **Kills** any existing processes on ports 8081 & 5173
- **Starts** backend API server (FastAPI + uvicorn)
- **Starts** frontend development server (React + Vite)
- **Tests** connectivity and API proxy
- **Shows** all URLs and service information

### `./stop.sh`
- **Stops** both backend and frontend services gracefully
- **Cleans up** ports and processes
- **Archives** log files with timestamps
- **Removes** PID files

### `./status.sh`
- **Shows** current service status
- **Checks** port usage and PIDs
- **Tests** endpoint connectivity
- **Displays** log information

## 🌐 Services

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **Backend API** | 8081 | http://localhost:8081/api/ | FastAPI server |
| **Frontend UI** | 5173 | http://localhost:5173/ | React dashboard |

## 📊 Frontend Pages

- **Dashboard**: http://localhost:5173/ - P&L, costs, equity curve
- **Trades**: http://localhost:5173/trades - Trade history with AI reasoning
- **Positions**: http://localhost:5173/positions - Current Alpaca positions  
- **Insights**: http://localhost:5173/insights - AI decision-making process

## 📝 Logs

- `backend.log` - Backend API server logs
- `frontend.log` - Frontend development server logs
- Logs are archived with timestamps when stopping services

## 🔧 Process Management

- PIDs are saved to `.backend.pid` and `.frontend.pid`
- Services run in background with `nohup`
- Automatic port cleanup on startup
- Graceful shutdown with process tracking

## ⚡ Features

- **Port Conflict Resolution**: Automatically kills conflicting processes
- **Health Checks**: Waits for services to be ready before proceeding
- **API Proxy Testing**: Verifies frontend-backend communication
- **Clean Shutdown**: Proper process cleanup and log archiving
- **Status Monitoring**: Real-time service health checking

## 🤖 Ready for Trading!

Once started, your autonomous trading system will be running with:
- ✅ **Alpaca Paper Trading** integration
- ✅ **OpenAI LLM** for AI reasoning
- ✅ **Real-time Market Data** analysis
- ✅ **Interactive Dashboard** for monitoring 