# RoboInvest - Autonomous Trading System

## Project Structure

```
RoboInvest/
├── agents/           # AI agent implementations
├── backend/          # FastAPI backend server
├── core/            # Core trading and AI modules
├── frontend/        # React frontend application
├── tools/           # Trading and research tools
├── utils/           # Utility functions
├── logs/            # Application logs
├── docs/            # Documentation files
├── scripts/         # Utility scripts and demos
├── tests/           # Test files
├── config/          # Configuration files
├── data/            # Data files and backups
└── chroma/          # Vector database
```

## Quick Start

1. **Start the system:**
   ```bash
   ./scripts/start.sh
   ```

2. **Check status:**
   ```bash
   ./scripts/status.sh
   ```

3. **Stop the system:**
   ```bash
   ./scripts/stop.sh
   ```

## Key Components

- **LLM-Driven Research**: Autonomous AI agents conducting market research
- **Real-time Trading**: Live trading with risk management
- **Web Interface**: Real-time dashboard at http://localhost:5174
- **API Server**: Backend API at http://localhost:8000

## Documentation

See the `docs/` directory for detailed documentation on:
- System architecture
- Risk management
- Trading strategies
- API endpoints

## Logs

Application logs are stored in the `logs/` directory:
- `backend.log` - Backend server logs
- `frontend.log` - Frontend application logs
- `research.log` - Research agent logs
