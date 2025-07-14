# RoboInvest - Autonomous Trading System

A sophisticated autonomous trading system with AI-powered agents, hybrid memory architecture, and real-time market analysis.

## 🚀 Quick Start

### Single Command Startup
```bash
./start.sh
```

This single command will:
- ✅ Check dependencies (Python, Node.js, npm)
- ✅ Install Python and frontend dependencies
- ✅ Initialize databases (ChromaDB, SQLite)
- ✅ Start backend API server (port 8000)
- ✅ Start frontend development server (port 5173)
- ✅ Display system status and access information

### System Management
```bash
# Check system status
./status.sh

# Stop all services
./stop.sh

# Restart system
./stop.sh && ./start.sh
```

## 🌐 Access Points

Once started, access the system at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Health**: http://localhost:8000/api/health
- **Governor Panel**: http://localhost:8000/api/governor/context

## 🧠 System Architecture

### Core Components
- **Governor Agent**: Central coordinator and meta-agent
- **Trading Agent**: Portfolio management and trade execution
- **Research Agent**: Market analysis and alpha discovery
- **Self-Editing Agent**: Code modification and system improvement

### Memory System
- **Hybrid Memory**: ChromaDB (semantic) + SQLite (structured)
- **Intelligent Pruning**: LLM-based memory optimization
- **Session Context**: Cross-conversation memory and learning
- **Experience Storage**: All interactions and insights preserved

### Data Sources
- **Alpaca Trading API**: Real portfolio and market data
- **Research Agents**: Autonomous market analysis
- **Error Event Bus**: Centralized error handling and self-healing

## 🎯 Key Features

### 🤖 AI-Powered Agents
- **LLM-Based**: All agents use OpenAI for intelligent responses
- **Memory-Aware**: Agents remember past interactions and learn
- **Contextual**: Responses based on conversation history
- **Modular**: Easy to add new specialized agents

### 📊 Real-Time Data
- **Live Portfolio**: Real Alpaca trading account integration
- **Market Analysis**: Autonomous research and alpha discovery
- **Risk Management**: Intelligent risk assessment and monitoring
- **Performance Tracking**: Comprehensive P&L and performance metrics

### 🎨 Interactive Visualizations
- **Dynamic Dashboards**: Agent-generated interactive charts
- **Real-Time Updates**: Live data visualization
- **Custom Components**: HTML/CSS/JS visualizations
- **Responsive Design**: Works on desktop and mobile

### 🔧 System Management
- **Self-Healing**: Automatic error detection and recovery
- **Self-Editing**: Agents can modify the codebase
- **Hybrid Memory**: Intelligent data retention and pruning
- **Unified Control**: Single start/stop/status system

## 📋 Prerequisites

### Required Software
- **Python 3.8+**: Core backend and AI functionality
- **Node.js 16+**: Frontend development server
- **npm**: Package management for frontend

### API Keys
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM-based agents
- `ALPACA_API_KEY`: Trading account access
- `ALPACA_SECRET_KEY`: Trading account authentication
- `CHROMA_DB_PATH`: ChromaDB storage location (default: `./chroma`)

### Database Files
- `data/central_experience.db`: Hybrid memory storage
- `data/governor_directives.db`: System directives and commands
- `chroma/`: Vector database for semantic search

## 📊 System Status

Check comprehensive system status:
```bash
./status.sh
```

Shows:
- ✅ Backend and frontend process status
- ✅ Database initialization status
- ✅ Research data availability
- ✅ Network port usage
- ✅ System resource usage
- ✅ Environment configuration

## 🧪 Testing

### Quick Tests
```bash
# Test API health
curl http://localhost:8000/api/health

# Test governor conversation
curl -X POST http://localhost:8000/api/governor/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# Test memory system
python scripts/test_hybrid_memory_system.py
```

### Research System
```bash
# Start research agents
python scripts/run_continuous_research.py

# Check research status
curl -X POST http://localhost:8000/api/governor/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "How is research going?", "session_id": "test"}'
```

## 📁 Project Structure

```
RoboInvest/
├── start.sh              # Unified startup script
├── stop.sh               # Unified stop script
├── status.sh             # System status checker
├── backend/              # FastAPI backend
│   └── api/
│       └── fastapi_app.py
├── frontend/             # React/Vite frontend
│   └── src/
├── core/                 # Core system components
│   ├── central_experience_db.py
│   ├── intelligent_memory_manager.py
│   └── ...
├── agents/               # AI agent implementations
├── data/                 # Database and research data
├── scripts/              # Utility and test scripts
└── docs/                 # Documentation
```

## 🚨 Troubleshooting

### Common Issues

**System won't start:**
```bash
# Check dependencies
./status.sh

# Check logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

**API not responding:**
```bash
# Check if backend is running
./status.sh

# Restart backend
./stop.sh && ./start.sh
```

**Research data not found:**
```bash
# Start research agents
python scripts/run_continuous_research.py

# Check research status
curl -X POST http://localhost:8000/api/governor/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Research status", "session_id": "test"}'
```

### Log Files
- `logs/backend.log`: Backend API server logs
- `logs/frontend.log`: Frontend development server logs
- `logs/chromadb_setup.log`: Database initialization logs

## 🔄 Development

### Adding New Agents
1. Create agent implementation in `agents/`
2. Add to agent registry in `backend/api/governor_endpoints.py`
3. Update intent detection for routing
4. Test with governor conversation

### Modifying Memory System
1. Update `core/central_experience_db.py` for storage changes
2. Modify `core/intelligent_memory_manager.py` for optimization
3. Test with `scripts/test_hybrid_memory_system.py`

### Frontend Customization
1. Modify components in `frontend/src/`
2. Add new visualization types
3. Update agent response handling

## 📈 Performance

### Memory Optimization
- **Automatic Pruning**: LLM-based importance scoring
- **Semantic Clustering**: Similar experiences grouped
- **Adaptive Retention**: Different strategies per data type
- **Background Optimization**: Continuous memory management

### Scalability
- **Hybrid Storage**: Efficient semantic + structured search
- **Process Management**: Proper PID tracking and cleanup
- **Resource Monitoring**: Built-in status checking
- **Error Recovery**: Self-healing capabilities

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Test** with `./status.sh` and `python scripts/test_hybrid_memory_system.py`
4. **Submit** a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check `./status.sh` for system diagnostics
2. Review log files in `logs/`
3. Test individual components
4. Create an issue with detailed information

---

**RoboInvest** - Intelligent autonomous trading with persistent memory and self-improving agents. 🚀 