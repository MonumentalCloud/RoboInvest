from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn

from core.config import config
from core.pnl_tracker import pnl_tracker
from core.performance_tracker import performance_tracker
from agents.rag_playbook import rag_agent
from autonomous_trading_system import autonomous_trading_system

app = FastAPI(title="RoboInvest API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "ws://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active websocket connections for streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            message_str = json.dumps(message)
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

# Websocket endpoint for real-time AI thoughts streaming
@app.websocket("/ws/ai-thoughts")
async def websocket_ai_thoughts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Websocket endpoint for alpha research tree updates
@app.websocket("/ws/research-tree")
async def websocket_research_tree(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Function to broadcast AI thoughts (called by autonomous system)
async def broadcast_ai_thought(thought_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
    """Broadcast AI thought to all connected clients"""
    message = {
        "type": "ai_thought",
        "thought_type": thought_type,
        "content": content,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

# Function to broadcast research tree updates
async def broadcast_research_update(node_type: str, node_data: Dict[str, Any]):
    """Broadcast research tree update to all connected clients"""
    message = {
        "type": "research_update",
        "node_type": node_type,
        "node_data": node_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

# Test websocket connection
@app.post("/api/test/websocket")
async def test_websocket_broadcast():
    """Test websocket by sending a test message"""
    await broadcast_ai_thought(
        "system_start", 
        "🧪 Test message from backend!",
        {"test": True, "timestamp": datetime.now().isoformat()}
    )
    return {"status": "test_sent", "message": "Test message sent to all connected clients"}

# Start autonomous trading with streaming
@app.post("/api/autonomous/start")
async def start_autonomous_streaming():
    """Start autonomous trading with real-time streaming"""
    
    # Broadcast start message
    await broadcast_ai_thought(
        "system_start", 
        "🚀 Autonomous Alpha Hunter starting...",
        {"status": "initializing"}
    )
    
    # Start autonomous system in background task
    asyncio.create_task(run_autonomous_with_streaming())
    
    return {"status": "started", "message": "Autonomous trading started with real-time streaming"}

async def run_autonomous_with_streaming():
    """Run autonomous trading system with real-time streaming of thoughts"""
    try:
        # Import the real autonomous system
        from autonomous_trading_system import autonomous_trading_system
        
        # Override logging to stream real thoughts
        await stream_real_autonomous_cycle()
    except Exception as e:
        await broadcast_ai_thought("error", f"Error in autonomous system: {str(e)}", {"error": True})

async def stream_real_autonomous_cycle():
    """Run REAL autonomous trading with streaming - not simulation"""
    
    await broadcast_ai_thought("system_start", "🚀 Starting REAL autonomous alpha hunting...", {"real_system": True})
    
    try:
        # Import the real autonomous trading system
        from autonomous_trading_system import autonomous_trading_system
        from agents.autonomous_alpha_hunter import autonomous_alpha_hunter
        from tools.web_researcher import web_researcher
        from tools.data_fetcher import data_fetcher
        
        # Step 1: Real market analysis
        await broadcast_ai_thought("phase_start", "🧠 Scanning real market data...", {"phase": "market_analysis"})
        
        await broadcast_research_update("market_scan", {
            "title": "Real Market Data Analysis",
            "status": "analyzing",
            "data": {
                "scanning": ["Live market indices", "VIX volatility", "Economic indicators"],
                "progress": 10
            }
        })
        
        # Get real market data
        market_data = data_fetcher.get_market_overview()
        vix_level = market_data.get("vix_level", 20)
        sentiment = market_data.get("market_sentiment", "neutral")
        
        await broadcast_ai_thought(
            "analysis", 
            f"📊 Real VIX: {vix_level:.1f} | Market sentiment: {sentiment}",
            {"vix": vix_level, "sentiment": sentiment, "real_data": True}
        )
        
        await broadcast_research_update("market_scan", {
            "title": "Market Data Retrieved",
            "status": "complete",
            "data": {
                "vix_level": vix_level,
                "sentiment": sentiment,
                "progress": 30
            }
        })
        
        # Step 2: Real alpha hunting
        await broadcast_ai_thought("phase_start", "🎯 Hunting for real alpha opportunities...", {"phase": "alpha_hunting"})
        
        await broadcast_research_update("opportunity_identification", {
            "title": "AI Alpha Opportunity Detection",
            "status": "scanning",
            "data": {
                "using_llm": True,
                "scanning_themes": ["Market trends", "Sector rotations", "News catalysts"],
                "progress": 50
            }
        })
        
        # Run real alpha hunting
        alpha_strategy = autonomous_alpha_hunter.hunt_for_alpha()
        
        if alpha_strategy and alpha_strategy.get("confidence", 0) > 0.3:
            opportunity_theme = alpha_strategy.get("opportunity_theme", "Market analysis")
            thesis = alpha_strategy.get("alpha_thesis", "No thesis")
            confidence = alpha_strategy.get("confidence", 0)
            
            await broadcast_ai_thought(
                "discovery", 
                f"🎯 REAL opportunity found: {opportunity_theme} (confidence: {confidence:.1%})",
                {"opportunity": opportunity_theme, "confidence": confidence, "real_ai": True}
            )
            
            # Step 3: Real web research
            await broadcast_ai_thought("phase_start", "🔍 Starting real web research...", {"phase": "web_research"})
            
            await broadcast_research_update("deep_research", {
                "title": "AI Web Research & Analysis",
                "status": "researching",
                "data": {
                    "opportunity": opportunity_theme,
                    "using_llm": True,
                    "research_areas": ["Sentiment analysis", "Fundamental research", "News impact"],
                    "progress": 70
                }
            })
            
            # Real web research
            opportunity_data = {
                "theme": opportunity_theme,
                "thesis": thesis,
                "catalysts": alpha_strategy.get("catalysts", []),
                "risk_factors": [alpha_strategy.get("risk_level", "MEDIUM")]
            }
            
            tickers = [alpha_strategy.get("primary_ticker", "SPY")]
            research_report = web_researcher.research_opportunity(opportunity_data, tickers)
            
            # Step 4: Real strategy creation
            await broadcast_ai_thought("phase_start", "💡 Creating real AI strategy...", {"phase": "strategy_creation"})
            
            # Run full autonomous cycle
            final_strategy = autonomous_trading_system._autonomous_cycle()
            
            action = final_strategy.get("action", "HOLD")
            symbol = final_strategy.get("primary_ticker", "SPY")
            position_size = final_strategy.get("position_size", 0)
            final_confidence = final_strategy.get("confidence", 0)
            final_thesis = final_strategy.get("alpha_thesis", "AI-generated strategy")
            
            await broadcast_ai_thought(
                "strategy", 
                f"💡 REAL AI strategy: {action} {symbol} ({position_size:.1%} position, {final_confidence:.1%} confidence)",
                {
                    "action": action, 
                    "symbol": symbol, 
                    "confidence": final_confidence, 
                    "position_size": position_size,
                    "real_ai_strategy": True
                }
            )
            
            await broadcast_research_update("strategy_creation", {
                "title": "AI Strategy Complete",
                "status": "complete", 
                "data": {
                    "final_strategy": {
                        "action": action,
                        "symbol": symbol,
                        "confidence": final_confidence,
                        "position_size": position_size,
                        "thesis": final_thesis
                    },
                    "progress": 100,
                    "real_ai": True
                }
            })
            
            await broadcast_ai_thought(
                "completion", 
                f"✅ REAL autonomous cycle complete - {action} {symbol} strategy ready",
                {"status": "complete", "real_system": True, "action": action, "symbol": symbol}
            )
            
        else:
            await broadcast_ai_thought(
                "discovery", 
                "📊 REAL AI analysis: No high-confidence opportunities found, staying conservative",
                {"confidence": alpha_strategy.get("confidence", 0) if alpha_strategy else 0, "real_ai": True}
            )
            
            await broadcast_research_update("strategy_creation", {
                "title": "Conservative Strategy",
                "status": "complete",
                "data": {
                    "final_strategy": {
                        "action": "HOLD",
                        "symbol": "SPY", 
                        "confidence": 0.3,
                        "position_size": 0,
                        "thesis": "Market conditions favor conservative approach"
                    },
                    "progress": 100,
                    "real_ai": True
                }
            })
            
            await broadcast_ai_thought(
                "completion", 
                "✅ REAL AI cycle complete - Conservative HOLD strategy",
                {"status": "complete", "real_system": True, "action": "HOLD"}
            )
            
    except Exception as e:
        await broadcast_ai_thought("error", f"Error in real autonomous system: {str(e)}", {"error": True, "real_system": True})


@app.get("/api/performance")
async def get_performance():
    """Get current performance metrics"""
    try:
        performance = performance_tracker.rolling_stats()
        return performance
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/trades")
async def get_trades(limit: int = 50):
    """Get recent trades"""
    try:
        # Get recent closed trades
        recent_trades = pnl_tracker.closed_trades[-limit:] if limit > 0 else pnl_tracker.closed_trades
        trades_data = [trade.to_dict() for trade in recent_trades]
        return {"trades": trades_data}
    except Exception as e:
        return {"error": str(e), "trades": []}

@app.get("/api/budget")
async def get_budget():
    """Get current budget information"""
    return {
        "tokens": 150,  # Mock data
        "cost_today": 0.0998,
        "budget_remaining": 9.90
    }

@app.get("/api/lessons")
async def get_lessons():
    """Get recent AI insights and lessons"""
    try:
        # Get some recent insights from RAG agent
        lessons = []
        if hasattr(rag_agent, 'retrieve'):
            result = rag_agent.retrieve({"type": "insight"})
            if isinstance(result, list) and len(result) > 0:
                lessons = list(result)[:10]
            elif isinstance(result, dict) and "similar_trades" in result:
                trades = result.get("similar_trades", [])
                if isinstance(trades, list):
                    lessons = list(trades)[:10]
        return {"lessons": lessons}
    except Exception as e:
        return {"lessons": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 