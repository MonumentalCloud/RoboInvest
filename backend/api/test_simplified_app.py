"""
Minimal Test Simplified FastAPI App
For testing the basic functionality without complex dependencies
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(
    title="RoboInvest Test API", 
    version="2.0.0",
    description="Minimal test version of simplified RoboInvest API"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestConnectionManager:
    """Simple test connection manager"""
    
    def __init__(self):
        self.connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.connections.append(websocket)
        print(f"New connection established: {websocket.client}")
        
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            print(f"Connection disconnected: {websocket.client}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections"""
        if not self.connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

# Initialize connection manager
manager = TestConnectionManager()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "system": "test_simplified_roboinvest"
    }

@app.get("/api/governor/context")
async def get_system_context():
    """Get current system context"""
    return {
        "status": "success", 
        "context": {
            "mission": "Discover the smartest and greatest upside that nobody is looking at",
            "current_strategy": "organic_alpha_hunting",
            "system_mode": "paper_trading",
            "research_priorities": ["alpha_discovery", "market_monitoring", "sentiment_tracking"],
            "risk_parameters": {
                "max_position_size": 0.02,
                "max_daily_loss": 0.05,
                "correlation_threshold": 0.7,
                "volatility_threshold": 0.3
            },
            "trading_rules": {
                "paper_trading_only": True,
                "require_approval": False,
                "auto_reject_high_risk": True
            },
            "active_directives": 0,
            "last_updated": datetime.now().isoformat()
        }
    }

@app.get("/api/governor/pulse")
async def get_system_pulse():
    """Get current system pulse"""
    return {
        "status": "success",
        "pulse": {
            "timestamp": datetime.now().isoformat(),
            "active_agents": 5,
            "directives_processed": 0,
            "trades_executed": 0,
            "research_activities": 3,
            "system_health": "operational",
            "mission": "Discover the smartest and greatest upside that nobody is looking at"
        }
    }

@app.get("/api/governor/directives")
async def get_directives():
    """Get directives"""
    return {
        "status": "success",
        "directives": [],
        "total": 0
    }

@app.post("/api/governor/directives")
async def issue_directive(request: Dict[str, Any]):
    """Issue a new directive"""
    return {
        "status": "success",
        "directive_id": "test_directive_001",
        "message": f"Directive '{request.get('title', 'Test')}' issued successfully"
    }

@app.post("/api/governor/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Handle natural language conversation with the Governor Agent"""
    message = request.get("message", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Simple response logic
    message_lower = message.lower()
    
    if "status" in message_lower or "how" in message_lower:
        response = "The system is running in paper trading mode with 5 active agents. We're focused on alpha discovery, market monitoring, and sentiment tracking. Overall system health is excellent."
        actions_taken = []
    elif "risk" in message_lower and "conservative" in message_lower:
        response = "I'll adjust the risk parameters to be more conservative. This will reduce max position size to 1% of portfolio and lower the daily loss limit to 2%."
        actions_taken = ["Adjusted risk parameters to conservative"]
    elif "stop" in message_lower and "trading" in message_lower:
        response = "I'm initiating an emergency stop of all trading activities. This will immediately halt all active trades and prevent new ones from being executed."
        actions_taken = ["Emergency stop initiated"]
    else:
        response = "I understand your request. I can help you with system status, trade performance, risk management, research insights, and any system changes you need. What would you like to know or adjust?"
        actions_taken = []
    
    return {
        "status": "success",
        "response": response,
        "metadata": {
            "actions_taken": actions_taken,
            "context_used": True
        }
    }

@app.get("/api/dashboard/performance")
async def get_performance():
    """Get performance metrics"""
    return {
        "status": "success",
        "performance": {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "avg_pnl": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "current_positions": 0,
            "unrealized_pnl": 0.0
        }
    }

@app.get("/api/dashboard/trades")
async def get_trades(limit: int = 50):
    """Get recent trades"""
    return {
        "status": "success",
        "trades": []
    }

@app.get("/api/dashboard/positions")
async def get_positions():
    """Get current positions"""
    return {
        "status": "success",
        "positions": []
    }

@app.post("/api/autonomous/start")
async def start_autonomous():
    """Start the autonomous trading system"""
    return {"status": "success", "message": "Autonomous system started"}

@app.post("/api/autonomous/stop")
async def stop_autonomous():
    """Stop the autonomous trading system"""
    return {"status": "success", "message": "Autonomous system stopped"}

@app.get("/api/autonomous/status")
async def get_autonomous_status():
    """Get autonomous system status"""
    return {"status": "success", "autonomous_status": "not_started"}

# WebSocket endpoints
@app.websocket("/ws/governor")
async def websocket_governor(websocket: WebSocket):
    """WebSocket endpoint for governor control panel"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard updates"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """Unified WebSocket endpoint for all real-time data"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("🚀 Starting Test Simplified RoboInvest API...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 