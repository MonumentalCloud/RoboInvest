# 🚀 Quick Start Guide - Governor Control Panel

## Start the System (5 minutes)

### 1. Start Backend Server
```bash
# In the project root directory
python backend/api/fastapi_app.py
```

### 2. Start Frontend (in new terminal)
```bash
# In the project root directory
cd frontend && npm run dev
```

### 3. Access Governor Control Panel
Open your browser and navigate to:
```
http://localhost:5173/governor
```

## 🎮 First Steps

### 1. Check System Status
- Go to the **Overview** tab
- Verify system is running in "normal" mode
- Check current mission and strategy

### 2. Issue Your First Directive
- Go to the **Quick Actions** tab
- Click "Focus on Alpha Discovery" button
- Watch the real-time updates in the Overview tab

### 3. Monitor Agent Responses
- Check the **Directives** tab
- See which agents have acknowledged your directive
- Monitor completion status

## 🎯 Common Use Cases

### Emergency Stop
1. Go to **Quick Actions** tab
2. Click "Emergency Stop" button
3. System immediately stops all trading
4. Check system mode changes to "emergency_stop"

### Risk Adjustment
1. Go to **Quick Actions** tab
2. Click "Reduce Risk Exposure" button
3. Position sizes automatically reduced
4. Check risk parameters in **System Context** tab

### Mission Update
1. Go to **Directives** tab
2. Select "Mission Update" from dropdown
3. Enter title and description
4. Add JSON payload with new mission
5. Click "Issue Directive"

## 📊 Real-Time Monitoring

### System Context Tab
- **Mission**: Current system mission
- **Strategy**: Active trading strategy  
- **Risk Parameters**: Position sizes, loss limits
- **Research Priorities**: Current research focus
- **Trading Rules**: Approval settings, confidence thresholds

### Directives Tab
- **Active Directives**: All current directives
- **Status**: Pending, Acknowledged, Completed
- **Agent Responses**: Which agents have processed directives

## 🛡️ Governance Controls

### Email Approval System
- **High-risk, high-upside trades**: Require email approval
- **High-risk, low-upside trades**: Auto-rejected
- **Low-risk trades**: Execute immediately

### Risk Management
- **Position Sizing**: Configurable max position sizes
- **Daily Loss Limits**: Automatic stop-loss
- **Correlation Limits**: Portfolio diversification

## 🚨 Emergency Controls

### Emergency Stop
- **Immediate**: Stops all trading instantly
- **Preserve Positions**: Option to keep or close positions
- **Resume**: Controlled restart when ready

### System Modes
- **Normal**: Standard operations
- **Conservative**: Reduced risk parameters
- **Aggressive**: Higher risk tolerance
- **Emergency**: All trading stopped

## 📱 Quick Actions Reference

### Mission Control
- **Focus on Alpha Discovery**: Prioritize alpha hunting
- **Conservative Mode**: Reduce risk exposure

### Risk Management
- **Reduce Risk Exposure**: Lower position sizes
- **Increase Risk Tolerance**: Higher position sizes

### Research Focus
- **Market Anomalies**: Focus on inefficiencies
- **Fundamental Analysis**: Value-based research

### Emergency Controls
- **Emergency Stop**: Immediate halt
- **Paper Trading Only**: Safe mode

## 🔧 Advanced Features

### Custom Directives
1. Go to **Directives** tab
2. Fill in all required fields
3. Add JSON payload for complex configurations
4. Set priority level
5. Issue directive

### JSON Payload Examples
```json
// Risk Parameters
{
  "risk_parameters": {
    "max_position_size": 0.02,
    "max_daily_loss": 0.03,
    "correlation_threshold": 0.7
  }
}

// Trading Rules
{
  "trading_rules": {
    "require_email_approval": true,
    "min_confidence_threshold": 0.8,
    "paper_trading_only": true
  }
}

// Research Priorities
{
  "research_priorities": [
    "market_anomalies",
    "sentiment_analysis",
    "technical_patterns"
  ]
}
```

## 🎯 Success Indicators

### System Health
- ✅ All agents registered and active
- ✅ WebSocket connections established
- ✅ Real-time updates working
- ✅ Directive acknowledgments received

### Governance Working
- ✅ Directives propagate to agents
- ✅ System context updates in real-time
- ✅ Email approval system active
- ✅ Emergency controls responsive

## 🆘 Troubleshooting

### Frontend Not Loading
- Check if backend is running on port 8081
- Verify frontend is running on port 5173
- Check browser console for errors

### No Agent Responses
- Verify agents are initialized
- Check backend logs for errors
- Ensure WebSocket connections are active

### Directives Not Processing
- Check directive format and JSON payload
- Verify agent subscriptions are active
- Monitor backend logs for processing errors

## 🎉 You're Ready!

The Governor Control Panel is now fully operational. You have complete control over the autonomous trading system with:

- ✅ **Real-time monitoring** of all system components
- ✅ **Instant directive issuance** to all agents
- ✅ **Emergency controls** for immediate response
- ✅ **Email approval system** for high-risk trades
- ✅ **Comprehensive governance** with full transparency

Start by issuing a simple directive and watch the system respond in real-time! 