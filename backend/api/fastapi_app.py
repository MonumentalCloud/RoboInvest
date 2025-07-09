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
        self.research_tree: Dict[str, Dict[str, Any]] = {}  # Store tree nodes
        
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
    
    async def add_tree_node(self, node_id: str, node_type: str, title: str, content: str, 
                          parent_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a new node to the research tree"""
        node = {
            "id": node_id,
            "type": node_type,
            "title": title,
            "content": content,
            "status": "active",
            "parent": parent_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.research_tree[node_id] = node
        
        # Broadcast tree update
        await self.broadcast({
            "type": "tree_update",
            "action": "add_node",
            "node": node,
            "tree": list(self.research_tree.values())
        })
    
    async def update_tree_node(self, node_id: str, status: Optional[str] = None, 
                             progress: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """Update an existing tree node"""
        if node_id not in self.research_tree:
            return
            
        node = self.research_tree[node_id]
        
        if status:
            node["status"] = status
        if progress is not None:
            node["progress"] = progress
        if metadata:
            node["metadata"].update(metadata)
        
        # Broadcast tree update
        await self.broadcast({
            "type": "tree_update",
            "action": "update_node",
            "node": node,
            "tree": list(self.research_tree.values())
        })
    
    def clear_tree(self):
        """Clear the research tree"""
        self.research_tree.clear()

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
    """Run REAL autonomous trading with streaming tree visualization"""
    
    # Clear previous tree
    manager.clear_tree()
    
    try:
        # Import the real autonomous trading system
        from autonomous_trading_system import autonomous_trading_system
        from agents.autonomous_alpha_hunter import autonomous_alpha_hunter
        from tools.web_researcher import web_researcher
        from tools.data_fetcher import data_fetcher
        
        # Root decision: Start analysis
        await manager.add_tree_node(
            "root_decision", 
            "decision", 
            "🚀 Start Alpha Hunt",
            "Initiating autonomous alpha hunting process",
            metadata={"real_system": True}
        )
        
        # Step 1: Global Opportunity Scanning
        await manager.add_tree_node(
            "opportunity_scanning", 
            "analysis", 
            "🌍 Global Opportunity Scanning",
            "Scanning global trends, events, and market conditions for alpha opportunities",
            parent_id="root_decision",
            metadata={"phase": "opportunity_scanning"}
        )
        
        await manager.update_tree_node("opportunity_scanning", progress=30)
        
        # Run real alpha hunting - this uses LLM to scan opportunities
        alpha_strategy = autonomous_alpha_hunter.hunt_for_alpha()
        
        if alpha_strategy and alpha_strategy.get("confidence", 0) > 0.3:
            opportunity_theme = alpha_strategy.get("opportunity_theme", "Market analysis")
            thesis = alpha_strategy.get("alpha_thesis", "No thesis")
            confidence = alpha_strategy.get("confidence", 0)
            primary_ticker = alpha_strategy.get("primary_ticker", "SPY")
            
            await manager.update_tree_node(
                "opportunity_scanning", 
                status="completed", 
                progress=100,
                metadata={
                    "opportunity": opportunity_theme,
                    "confidence": confidence,
                    "primary_ticker": primary_ticker,
                    "real_ai": True
                }
            )
        
            # Decision: Should we hunt for alpha?
            await manager.add_tree_node(
                "alpha_decision", 
                "decision", 
                "🎯 Alpha Hunt Decision",
                f"Opportunity detected: {opportunity_theme}",
                parent_id="opportunity_scanning",
                metadata={"decision_type": "alpha_hunt", "opportunity": opportunity_theme, "confidence": confidence}
            )
            
            # Branch out to different research paths
            research_branches = []
            
            # Web Research Branch
            await manager.add_tree_node(
                "web_research", 
                "websearch", 
                "🌐 Web Research",
                f"Researching {opportunity_theme} via web sources",
                parent_id="alpha_decision",
                metadata={"research_type": "web", "opportunity": opportunity_theme}
            )
            research_branches.append("web_research")
            
            # Fundamental Analysis Branch
            await manager.add_tree_node(
                "fundamental_analysis", 
                "fundamental", 
                "📈 Fundamental Analysis",
                f"Analyzing fundamentals for {opportunity_theme}",
                parent_id="alpha_decision",
                metadata={"research_type": "fundamental", "opportunity": opportunity_theme}
            )
            research_branches.append("fundamental_analysis")
            
            # Pandas/Data Analysis Branch
            await manager.add_tree_node(
                "data_analysis", 
                "pandas", 
                "📊 Data Analysis",
                f"Performing quantitative analysis on {opportunity_theme}",
                parent_id="alpha_decision",
                metadata={"research_type": "quantitative", "opportunity": opportunity_theme}
            )
            research_branches.append("data_analysis")
            
            # Simulate parallel research execution
            for i, branch in enumerate(research_branches):
                await asyncio.sleep(0.5)  # Simulate research time
                await manager.update_tree_node(branch, progress=30 + i * 20)
            
            # Real web research
            opportunity_data = {
                "theme": opportunity_theme,
                "thesis": thesis,
                "catalysts": alpha_strategy.get("catalysts", []),
                "risk_factors": [alpha_strategy.get("risk_level", "MEDIUM")]
            }
            
            tickers = [alpha_strategy.get("primary_ticker", "SPY")]
            research_report = web_researcher.research_opportunity(opportunity_data, tickers)
            
            # Complete research branches
            for branch in research_branches:
                await manager.update_tree_node(
                    branch, 
                    status="completed", 
                    progress=100,
                    metadata={"research_complete": True}
                )
                await asyncio.sleep(0.3)
            
            # Strategy Synthesis Decision
            await manager.add_tree_node(
                "strategy_synthesis", 
                "decision", 
                "💡 Strategy Synthesis",
                "Combining research findings into trading strategy",
                parent_id="alpha_hunting",
                metadata={"synthesis_type": "multi_source"}
            )
            
            # Strategy Creation Branch
            await manager.add_tree_node(
                "strategy_creation", 
                "strategy", 
                "🎯 Strategy Creation",
                f"Creating trading strategy for {opportunity_theme}",
                parent_id="strategy_synthesis",
                metadata={"strategy_type": "ai_generated"}
            )
            
            await manager.update_tree_node("strategy_creation", progress=70)
            
            # Run full autonomous cycle
            final_strategy = autonomous_trading_system._autonomous_cycle()
            
            action = final_strategy.get("action", "HOLD")
            symbol = final_strategy.get("primary_ticker", "SPY")
            position_size = final_strategy.get("position_size", 0)
            final_confidence = final_strategy.get("confidence", 0)
            final_thesis = final_strategy.get("alpha_thesis", "AI-generated strategy")
            
            await manager.update_tree_node(
                "strategy_creation", 
                status="completed", 
                progress=100,
                metadata={
                    "final_strategy": {
                        "action": action,
                        "symbol": symbol,
                        "confidence": final_confidence,
                        "position_size": position_size,
                        "thesis": final_thesis
                    },
                    "real_ai": True
                }
            )
            
            # Final execution decision
            await manager.add_tree_node(
                "execution_decision", 
                "execution", 
                "⚡ Execution Decision",
                f"Decision: {action} {symbol} ({position_size:.1%} position size)",
                parent_id="strategy_creation",
                metadata={
                    "execution_type": "paper_trade",
                    "action": action,
                    "symbol": symbol,
                    "position_size": position_size,
                    "confidence": final_confidence
                }
            )
            
            await broadcast_ai_thought(
                "execution_decision", 
                f"🎯 STRATEGY COMPLETE: {action} {symbol} | Confidence: {final_confidence:.2f} | Thesis: {final_thesis}",
                {
                    "action": action,
                    "symbol": symbol,
                    "position_size": position_size,
                    "confidence": final_confidence,
                    "thesis": final_thesis,
                    "real_ai": True
                }
            )
            
        else:
            # No good opportunities found
            await manager.update_tree_node(
                "opportunity_scanning", 
                status="completed", 
                progress=100,
                metadata={
                    "opportunity": "No viable opportunities found",
                    "confidence": 0,
                    "fallback": True
                }
            )
            
            await manager.add_tree_node(
                "fallback_decision", 
                "decision", 
                "🛡️ Fallback Decision",
                "No viable opportunities found - maintaining market neutral position",
                parent_id="opportunity_scanning",
                metadata={"decision_type": "fallback", "action": "HOLD"}
            )
            
            await broadcast_ai_thought(
                "fallback_decision", 
                "🛡️ No viable alpha opportunities found - maintaining conservative position",
                {"action": "HOLD", "confidence": 0.3, "fallback": True}
            )

            
    except Exception as e:
        await manager.add_tree_node(
            "error_node", 
            "decision", 
            "❌ Error",
            f"Error in autonomous system: {str(e)}",
            parent_id="root_decision",
            metadata={"error": True, "real_system": True}
        )
        await manager.update_tree_node("error_node", status="failed")


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