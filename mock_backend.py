from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
import json
import asyncio

app = FastAPI(title="Mock RoboInvest API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "ws://localhost:5173", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket endpoints
@app.websocket("/api/governor/ws/context")
async def websocket_context(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send mock context updates every 5 seconds
            await asyncio.sleep(5)
            context_update = {
                "type": "context_update",
                "context": {
                    "mission": "Maximize risk-adjusted returns through autonomous trading",
                    "current_strategy": "Multi-factor momentum with sentiment overlay",
                    "risk_parameters": {"max_position_size": 0.05, "max_drawdown": 0.15},
                    "performance_targets": {"annual_return": 0.25, "sharpe_ratio": 1.5},
                    "active_directives": ["Monitor market volatility", "Adjust position sizing"],
                    "system_mode": "autonomous",
                    "governance_rules": {"require_approval": False, "auto_rebalance": True},
                    "research_priorities": ["AI sentiment analysis", "Technical patterns"],
                    "trading_rules": {"min_confidence": 0.7, "max_hold_time": 72},
                    "last_updated": datetime.now().isoformat()
                }
            }
            await manager.send_personal_message(json.dumps(context_update), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/api/governor/ws/thoughts")
async def websocket_thoughts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send mock agent thoughts every 3 seconds
            await asyncio.sleep(3)
            thought = {
                "type": "agent_thought",
                "thought": {
                    "agent_id": f"agent_{random.randint(1, 5)}",
                    "timestamp": datetime.now().isoformat(),
                    "thought": f"Analyzing market conditions for {random.choice(['AAPL', 'GOOGL', 'MSFT'])}",
                    "reasoning": "Technical indicators suggest momentum continuation",
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "action_taken": random.choice(["hold", "buy", "sell"])
                }
            }
            await manager.send_personal_message(json.dumps(thought), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/api/governor/ws/pulse")
async def websocket_pulse(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send mock system pulse every 2 seconds
            await asyncio.sleep(2)
            pulse = {
                "type": "system_pulse",
                "pulse": {
                    "timestamp": datetime.now().isoformat(),
                    "active_agents": random.randint(3, 8),
                    "directives_processed": random.randint(10, 50),
                    "trades_executed": random.randint(1, 10),
                    "research_activities": random.randint(5, 20),
                    "system_health": random.choice(["excellent", "good", "operational"])
                }
            }
            await manager.send_personal_message(json.dumps(pulse), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Governor API endpoints
@app.get("/api/governor/context")
async def get_governor_context():
    return {
        "context": {
            "mission": "Maximize risk-adjusted returns through autonomous trading",
            "current_strategy": "Multi-factor momentum with sentiment overlay",
            "risk_parameters": {"max_position_size": 0.05, "max_drawdown": 0.15},
            "performance_targets": {"annual_return": 0.25, "sharpe_ratio": 1.5},
            "active_directives": ["Monitor market volatility", "Adjust position sizing"],
            "system_mode": "autonomous",
            "governance_rules": {"require_approval": False, "auto_rebalance": True},
            "research_priorities": ["AI sentiment analysis", "Technical patterns"],
            "trading_rules": {"min_confidence": 0.7, "max_hold_time": 72},
            "last_updated": datetime.now().isoformat()
        }
    }

@app.get("/api/governor/pulse")
async def get_governor_pulse():
    return {
        "timestamp": datetime.now().isoformat(),
        "active_agents": random.randint(3, 8),
        "directives_processed": random.randint(10, 50),
        "trades_executed": random.randint(1, 10),
        "research_activities": random.randint(5, 20),
        "system_health": random.choice(["excellent", "good", "operational"])
    }

@app.post("/api/governor/conversation")
async def governor_conversation(request: dict):
    message = request.get("message", "")
    
    # Mock responses based on message content
    if "status" in message.lower():
        response = "System status: All agents operational. Current performance: +12.5% YTD. Risk metrics within acceptable ranges."
    elif "strategy" in message.lower():
        response = "Current strategy: Multi-factor momentum with sentiment overlay. Active positions: 8. Recent trades: 15 this week."
    elif "risk" in message.lower():
        response = "Risk management active. Max position size: 5%. Current drawdown: 2.3%. Stop-losses configured for all positions."
    else:
        response = "I understand your request. The autonomous trading system is operating within normal parameters. How can I assist you further?"
    
    return {
        "response": response,
        "metadata": {
            "confidence": 0.95,
            "processing_time": 0.12,
            "timestamp": datetime.now().isoformat()
        }
    }

# Mock budget data
@app.get("/api/budget")
async def get_budget():
    return {
        "budget": {
            "total_budget": 100000.00,
            "used_budget": 45678.90,
            "available_budget": 54321.10,
            "daily_limit": 5000.00,
            "daily_used": 2345.67,
            "monthly_limit": 50000.00,
            "monthly_used": 45678.90,
            "risk_level": "moderate",
            "last_updated": datetime.now().isoformat()
        }
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Mock performance data
@app.get("/api/performance")
async def get_performance():
    return {
        "performance": {
            "total_trades": 150,
            "winning_trades": 95,
            "losing_trades": 55,
            "win_rate": 0.633,
            "total_pnl": 12500.50,
            "avg_pnl": 83.34,
            "max_drawdown": -2500.00,
            "sharpe_ratio": 1.85,
            "current_positions": 8,
            "unrealized_pnl": 3200.75
        }
    }

# Mock trades data
@app.get("/api/trades")
async def get_trades(limit: int = 100):
    trades = []
    for i in range(min(limit, 50)):
        entry_time = datetime.now() - timedelta(days=random.randint(1, 30))
        exit_time = entry_time + timedelta(hours=random.randint(1, 48)) if random.random() > 0.3 else None
        
        trade = {
            "symbol": random.choice(["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]),
            "quantity": random.randint(10, 1000),
            "entry_price": round(random.uniform(50, 500), 2),
            "entry_time": entry_time.isoformat(),
            "side": random.choice(["buy", "sell"]),
            "confidence": round(random.uniform(0.6, 0.95), 2)
        }
        
        if exit_time:
            trade["exit_price"] = round(trade["entry_price"] * random.uniform(0.9, 1.1), 2)
            trade["exit_time"] = exit_time.isoformat()
            trade["pnl"] = round((trade["exit_price"] - trade["entry_price"]) * trade["quantity"], 2)
            trade["pnl_pct"] = round((trade["exit_price"] - trade["entry_price"]) / trade["entry_price"] * 100, 2)
        
        trades.append(trade)
    
    return {"trades": trades}

# Mock positions data
@app.get("/api/positions")
async def get_positions():
    positions = []
    for i in range(8):
        entry_time = datetime.now() - timedelta(days=random.randint(1, 7))
        entry_price = round(random.uniform(50, 500), 2)
        current_price = round(entry_price * random.uniform(0.95, 1.05), 2)
        
        position = {
            "symbol": random.choice(["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]),
            "quantity": random.randint(10, 1000),
            "entry_price": entry_price,
            "entry_time": entry_time.isoformat(),
            "side": random.choice(["buy", "sell"]),
            "current_price": current_price,
            "unrealized_pnl": round((current_price - entry_price) * random.randint(10, 1000), 2),
            "unrealized_pnl_pct": round((current_price - entry_price) / entry_price * 100, 2)
        }
        positions.append(position)
    
    return {"positions": positions}

# Mock research endpoints
@app.get("/api/research/status")
async def get_research_status():
    return {
        "status": "active",
        "active_tracks": 3,
        "total_insights": 45,
        "last_update": datetime.now().isoformat()
    }

@app.get("/api/research/insights")
async def get_research_insights(limit: int = 50):
    insights = []
    for i in range(min(limit, 20)):
        insight = {
            "id": f"insight_{i}",
            "title": f"Market Insight {i+1}",
            "content": f"This is a mock market insight about trading opportunities.",
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
            "category": random.choice(["technical", "fundamental", "sentiment", "macro"])
        }
        insights.append(insight)
    
    return {"insights": insights}

@app.get("/api/research/alpha-opportunities")
async def get_alpha_opportunities(min_confidence: float = 0.0):
    opportunities = []
    for i in range(10):
        confidence = round(random.uniform(0.6, 0.95), 2)
        if confidence >= min_confidence:
            opportunity = {
                "symbol": random.choice(["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]),
                "confidence": confidence,
                "expected_return": round(random.uniform(0.05, 0.25), 3),
                "timeframe": random.choice(["1d", "1w", "1m"]),
                "strategy": random.choice(["momentum", "mean_reversion", "breakout", "sentiment"]),
                "timestamp": datetime.now().isoformat()
            }
            opportunities.append(opportunity)
    
    return {"opportunities": opportunities}

@app.get("/api/research/decision-trees")
async def get_decision_trees():
    return {
        "status": "success",
        "data": {
            "autonomous_alpha_hunt": {
                "tree": {
                    "nodes": {
                        "root": {
                            "id": "root",
                            "content": "Market Analysis",
                            "parent_id": None,
                            "created_at": datetime.now().isoformat()
                        },
                        "node1": {
                            "id": "node1",
                            "content": "Technical Analysis",
                            "parent_id": "root",
                            "created_at": datetime.now().isoformat()
                        },
                        "node2": {
                            "id": "node2",
                            "content": "Fundamental Analysis",
                            "parent_id": "root",
                            "created_at": datetime.now().isoformat()
                        }
                    }
                }
            }
        }
    }

@app.get("/api/research/tracks")
async def get_research_tracks():
    return {
        "tracks": [
            {
                "id": "autonomous_alpha_hunt",
                "name": "Autonomous Alpha Hunt",
                "status": "active",
                "insights_count": 25,
                "last_update": datetime.now().isoformat()
            },
            {
                "id": "market_sentiment",
                "name": "Market Sentiment Analysis",
                "status": "active",
                "insights_count": 15,
                "last_update": datetime.now().isoformat()
            },
            {
                "id": "technical_patterns",
                "name": "Technical Pattern Recognition",
                "status": "paused",
                "insights_count": 5,
                "last_update": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
    }

# Mock lessons endpoint
@app.get("/api/lessons")
async def get_lessons():
    return {
        "lessons": [
            {
                "id": "lesson_1",
                "title": "Market Volatility Patterns",
                "content": "Analysis of recent market volatility and its impact on trading strategies.",
                "timestamp": datetime.now().isoformat(),
                "category": "market_analysis"
            },
            {
                "id": "lesson_2",
                "title": "Risk Management Insights",
                "content": "Key learnings about position sizing and stop-loss strategies.",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "category": "risk_management"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)