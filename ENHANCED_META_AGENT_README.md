# Enhanced Meta Agent System

## Overview

The Enhanced Meta Agent is a sophisticated system monitoring and improvement coordinator that continuously monitors the entire multiagent trading system, analyzes performance patterns, and suggests automated improvements that can be relayed to code fixing agents and administrative agents.

## Key Features

### 🔍 Continuous System Monitoring
- **Real-time Metrics Collection**: Monitors all agents, system resources, and performance indicators
- **Health Assessment**: Continuously evaluates system health and identifies issues
- **Performance Tracking**: Tracks response times, success rates, error counts, and resource usage
- **Agent Status Monitoring**: Monitors individual agent health and performance

### 📊 Performance Analysis & Bottleneck Detection
- **Trend Analysis**: Identifies performance degradation patterns over time
- **Bottleneck Detection**: Automatically detects system bottlenecks and performance issues
- **Resource Usage Analysis**: Monitors CPU, memory, and other resource utilization
- **Predictive Analytics**: Uses historical data to predict potential issues

### 🛠️ Automated Improvement Suggestions
- **Intelligent Recommendations**: Generates improvement suggestions based on system analysis
- **Priority Classification**: Categorizes improvements by criticality (Critical, High, Medium, Low)
- **Impact Assessment**: Estimates the potential impact of each improvement
- **Implementation Planning**: Provides detailed implementation plans for each suggestion

### 🤖 Coordination with Specialized Agents
- **Code Editor Agent**: Handles code fixes, optimizations, and bug repairs
- **Prompt Engineer Agent**: Optimizes agent prompts and communication
- **System Architect Agent**: Designs new agents and system improvements
- **Performance Analyst Agent**: Analyzes and optimizes system performance

### 🔮 Predictive Maintenance
- **Pattern Recognition**: Identifies patterns that could lead to future issues
- **Proactive Optimization**: Suggests improvements before problems occur
- **Resource Leak Detection**: Monitors for memory leaks and resource waste
- **Scalability Planning**: Suggests improvements for system scaling

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Enhanced Meta Agent                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Monitoring    │  │   Analysis      │  │ Coordination │ │
│  │     Engine      │  │     Engine      │  │    Engine    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Code Editor    │  │   Prompt        │  │   System     │ │
│  │     Agent       │  │  Engineer       │  │  Architect   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Performance     │  │   Database      │  │ Notification │ │
│  │   Analyst       │  │   Storage       │  │    System    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### 1. Prerequisites
```bash
# Ensure you have the required dependencies
pip install psutil sqlite3 asyncio
```

### 2. Start the Enhanced Meta Agent
```bash
# Option 1: Use the enhanced startup script
./startup_with_meta_agent.sh

# Option 2: Start manually
python scripts/start_enhanced_meta_agent.py
```

### 3. Verify Installation
```bash
# Check if the meta agent is running
curl http://localhost:8081/api/meta-agent/status

# Check system health
curl http://localhost:8081/api/meta-agent/health
```

## API Endpoints

### System Status & Health
- `GET /api/meta-agent/status` - Get current system status
- `GET /api/meta-agent/health` - Get detailed health information
- `GET /api/meta-agent/metrics?hours=24` - Get system metrics

### Improvement Management
- `GET /api/meta-agent/improvements` - List all improvement suggestions
- `GET /api/meta-agent/improvements?status=pending` - List pending improvements
- `POST /api/meta-agent/improvements/{id}/approve` - Approve an improvement
- `POST /api/meta-agent/improvements/{id}/reject` - Reject an improvement

### Performance Monitoring
- `GET /api/meta-agent/agent-performance` - Get agent performance history
- `GET /api/meta-agent/agent-performance?agent_name=alpha_hunter` - Get specific agent performance

### Reports & Analysis
- `GET /api/meta-agent/reports` - List available system reports
- `GET /api/meta-agent/reports/{filename}` - Get specific report
- `POST /api/meta-agent/trigger-analysis` - Manually trigger system analysis

### Control
- `POST /api/meta-agent/control/start` - Start meta agent monitoring
- `POST /api/meta-agent/control/stop` - Stop meta agent monitoring

## Configuration

### Performance Thresholds
The system uses configurable thresholds for triggering improvements:

```python
performance_thresholds = {
    "response_time": 30.0,  # seconds
    "success_rate": 0.8,    # 80%
    "cpu_usage": 80.0,      # percentage
    "memory_usage": 85.0,   # percentage
    "error_rate": 0.1       # percentage
}
```

### Monitoring Intervals
- **Health Monitoring**: Every 30 seconds
- **Performance Analysis**: Every 5 minutes
- **Predictive Maintenance**: Every 10 minutes
- **System Reports**: Every 5 minutes

## Data Storage

### Database Schema
The system uses SQLite for data storage:

```sql
-- System metrics table
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    total_agents INTEGER NOT NULL,
    active_agents INTEGER NOT NULL,
    failed_agents INTEGER NOT NULL,
    avg_response_time REAL NOT NULL,
    avg_success_rate REAL NOT NULL,
    system_cpu_usage REAL NOT NULL,
    system_memory_usage REAL NOT NULL,
    total_errors INTEGER NOT NULL,
    total_insights INTEGER NOT NULL,
    research_cycles_completed INTEGER NOT NULL,
    performance_score REAL NOT NULL
);

-- System improvements table
CREATE TABLE system_improvements (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    priority TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    affected_components TEXT NOT NULL,
    estimated_impact TEXT NOT NULL,
    implementation_plan TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    assigned_agent TEXT,
    completion_time TEXT
);

-- Agent performance history
CREATE TABLE agent_performance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    response_time REAL,
    success_rate REAL,
    error_count INTEGER,
    insights_generated INTEGER,
    memory_usage REAL,
    cpu_usage REAL
);
```

### File Structure
```
meta_agent_data/
├── enhanced_meta_agent.db          # Main database
├── system_status.json              # Current system status
└── system_reports/                 # Generated reports
    ├── system_report_20241201_120000.json
    ├── system_report_20241201_130000.json
    └── ...
```

## Usage Examples

### 1. Monitor System Health
```bash
# Get current system status
curl http://localhost:8081/api/meta-agent/status

# Response:
{
  "status": "success",
  "data": {
    "meta_agent_active": true,
    "total_improvements": 5,
    "pending_improvements": 2,
    "completed_improvements": 3,
    "performance_score": 85.2
  }
}
```

### 2. Review Improvement Suggestions
```bash
# Get all pending improvements
curl http://localhost:8081/api/meta-agent/improvements?status=pending

# Response:
{
  "status": "success",
  "data": [
    {
      "id": "improvement_1701234567_1",
      "type": "performance",
      "priority": "high",
      "title": "Response Time Optimization",
      "description": "Average response time (35.2s) exceeds threshold (30s)",
      "confidence": 0.85,
      "status": "pending"
    }
  ]
}
```

### 3. Approve an Improvement
```bash
# Approve a specific improvement
curl -X POST http://localhost:8081/api/meta-agent/improvements/improvement_1701234567_1/approve

# Response:
{
  "status": "success",
  "message": "Improvement 'Response Time Optimization' approved for implementation",
  "improvement_id": "improvement_1701234567_1"
}
```

### 4. View Performance Metrics
```bash
# Get system metrics for last 24 hours
curl http://localhost:8081/api/meta-agent/metrics?hours=24

# Get specific agent performance
curl http://localhost:8081/api/meta-agent/agent-performance?agent_name=alpha_hunter
```

## Integration with Existing System

### Automatic Integration
The enhanced meta agent automatically integrates with:

1. **Agent Monitoring System**: Collects real-time agent metrics
2. **Notification System**: Sends alerts for critical issues
3. **Specialized Meta Agents**: Coordinates with code fixing and optimization agents
4. **Background Research Service**: Monitors research cycle performance

### Manual Integration
To integrate with custom systems:

```python
from agents.enhanced_meta_agent import enhanced_meta_agent

# Get system status
status = enhanced_meta_agent.get_system_status()

# Start monitoring
await enhanced_meta_agent.start_continuous_monitoring()

# Stop monitoring
enhanced_meta_agent.stop_monitoring()
```

## Monitoring Dashboard

Access the monitoring dashboard at:
- **Frontend**: http://localhost:5173/
- **API Documentation**: http://localhost:8081/docs

The dashboard provides:
- Real-time system health visualization
- Performance metrics charts
- Improvement suggestion management
- Agent performance tracking
- System reports and analytics

## Troubleshooting

### Common Issues

1. **Meta Agent Not Starting**
   ```bash
   # Check logs
   tail -f meta_agent.log
   
   # Check if database is accessible
   ls -la meta_agent_data/
   ```

2. **No Metrics Being Collected**
   ```bash
   # Check if agent monitoring system is running
   curl http://localhost:8081/api/agents/status
   
   # Check database
   sqlite3 meta_agent_data/enhanced_meta_agent.db "SELECT COUNT(*) FROM system_metrics;"
   ```

3. **Improvements Not Being Generated**
   ```bash
   # Check performance thresholds
   curl http://localhost:8081/api/meta-agent/health
   
   # Manually trigger analysis
   curl -X POST http://localhost:8081/api/meta-agent/trigger-analysis
   ```

### Log Files
- **Meta Agent Logs**: `meta_agent.log`
- **System Reports**: `meta_agent_data/system_reports/`
- **Database**: `meta_agent_data/enhanced_meta_agent.db`

## Performance Optimization

### System Requirements
- **CPU**: 2+ cores recommended
- **Memory**: 4GB+ RAM recommended
- **Storage**: 1GB+ free space for metrics storage
- **Network**: Stable internet connection for API calls

### Optimization Tips
1. **Adjust Monitoring Intervals**: Increase intervals for lower resource usage
2. **Clean Old Data**: Regularly clean old metrics data
3. **Database Optimization**: Periodically vacuum the SQLite database
4. **Resource Limits**: Set appropriate resource limits for the meta agent

## Security Considerations

1. **API Access**: Secure API endpoints with authentication
2. **Database Access**: Restrict access to the meta agent database
3. **Log Security**: Ensure logs don't contain sensitive information
4. **Network Security**: Use HTTPS for API communication

## Future Enhancements

### Planned Features
1. **Machine Learning Integration**: Advanced pattern recognition
2. **Distributed Monitoring**: Multi-node system monitoring
3. **Custom Metrics**: User-defined performance metrics
4. **Advanced Analytics**: Predictive modeling and forecasting
5. **Integration APIs**: Third-party system integration

### Extensibility
The system is designed to be easily extensible:
- Add new improvement types
- Customize performance thresholds
- Integrate with external monitoring systems
- Add custom analysis algorithms

## Support

For issues and questions:
1. Check the logs in `meta_agent.log`
2. Review the API documentation at `/docs`
3. Check system status via `/api/meta-agent/health`
4. Review this README for common solutions

## License

This enhanced meta agent system is part of the RoboInvest project and follows the same licensing terms.