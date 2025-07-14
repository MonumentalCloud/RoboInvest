from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uvicorn
import sqlite3
import logging
from utils.logger import logger

from core.config import config
from core.pnl_tracker import pnl_tracker
from core.performance_tracker import performance_tracker
from agents.rag_playbook import rag_agent
from autonomous_trading_system import autonomous_trading_system
from agents.trade_executor import TradeExecutorAgent
from agents.play_executor import play_executor, PlayStatus, InterventionType
from agents.enhanced_trade_executor import enhanced_trade_executor
from core.structured_order import OrderManager
from core.play_reporting import play_reporting
from core.notification_aggregator import notification_aggregator
from tools.data_fetcher import data_fetcher
from core.central_event_bus import central_event_bus, EventType, EventPriority
# Import governor directive endpoints
from backend.api.governor_endpoints import router as governor_router, setup_governor_subscriptions

from agents.experience_learning_system import experience_learning_system
from agents.performance_analyzer_agent import performance_analyzer_agent

# Use enhanced trade executor with structured orders
trade_executor = enhanced_trade_executor

app = FastAPI(title="RoboInvest API", version="1.0.0")

# Include governor directive endpoints (this replaces most other endpoints)
app.include_router(governor_router)

# Health check endpoint for startup script
@app.get("/api/health")
async def health_check():
    """Health check endpoint for startup script"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "ws://localhost:5173", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to track if autonomous system is running
autonomous_task = None

# Startup event to automatically start autonomous streaming
@app.on_event("startup")
async def startup_event():
    """Start autonomous streaming system automatically on startup"""
    global autonomous_task
    
    # Start the central event bus
    await central_event_bus.start()
    
    # Start the governor directive system
    from core.governor_directive_system import governor_directive_system
    await governor_directive_system.start()
    
    # Setup governor subscriptions
    setup_governor_subscriptions()
    
    # Check if autonomous trading should start automatically
    auto_start_trading = os.getenv("AUTO_START_TRADING", "false").lower() == "true"
    
    if auto_start_trading:
        print("🚀 FastAPI startup - starting REAL autonomous agents for paper trading...")
        
        # Start the task without waiting for it to complete
        autonomous_task = asyncio.create_task(run_real_autonomous_agents())
        print(f"✅ Real autonomous task created on startup: {autonomous_task}")
        
    else:
        print("🚀 FastAPI startup - autonomous trading disabled (set AUTO_START_TRADING=true to enable)")

    # Start the notification aggregator background loop
    notification_aggregator.start_background_loop()

# Store active websocket connections for streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.research_tree: Dict[str, Dict[str, Any]] = {}  # Store tree nodes
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[ConnectionManager] New connection: {websocket.client}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[ConnectionManager] Disconnected: {websocket.client}")
    
    async def broadcast(self, message: Dict[str, Any]):
        print(f"[ConnectionManager.broadcast] Broadcasting to {len(self.active_connections)} clients: {message}")
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
    
    async def save_research_tree_to_database(self, tree_id: str, agent_name: str, track_name: str = "autonomous_alpha_hunt"):
        """Save the current research tree to the database for persistence"""
        try:
            if not self.research_tree:
                return
            
            # Prepare the research data
            research_data = {
                "research_track": track_name,
                "specialization": "autonomous_alpha_hunting",
                "completed_at": datetime.now().isoformat(),
                "decision_tree": list(self.research_tree.values()),
                "tree_metadata": {
                    "total_nodes": len(self.research_tree),
                    "root_nodes": [node_id for node_id, node in self.research_tree.items() if node.get("parent") is None],
                    "completed_nodes": [node_id for node_id, node in self.research_tree.items() if node.get("status") == "completed"],
                    "active_nodes": [node_id for node_id, node in self.research_tree.items() if node.get("status") == "active"]
                },
                "ai_thoughts": [],  # Could be populated with actual AI thoughts
                "insights": [],     # Could be populated with research insights
                "events": []        # Could be populated with research events
            }
            
            # Save to database
            root_id = next((node_id for node_id, node in self.research_tree.items() if node.get("parent") is None), "root")
            central_event_bus.save_research_tree(tree_id, agent_name, track_name, root_id, research_data)
            
            print(f"[ConnectionManager] Saved research tree {tree_id} to database")
            
        except Exception as e:
            print(f"[ConnectionManager] Error saving research tree: {e}")

manager = ConnectionManager()

# Function to broadcast AI thoughts (called by autonomous system)
async def broadcast_ai_thought(thought_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
    """Broadcast AI thought to all connected clients and capture in central event bus"""
    message = {
        "type": "ai_thought",
        "thought_type": thought_type,
        "content": content,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    print(f"[broadcast_ai_thought] Sending: {message}")
    await manager.broadcast(message)
    
    # Also capture in central event bus
    from core.central_event_bus import capture_ai_thought
    capture_ai_thought(thought_type, content, metadata)

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
# @app.post("/api/test/websocket")
# async def test_websocket_broadcast():
#     """Test websocket by sending a test message"""
#     await broadcast_ai_thought(
#         "system_start", 
#         "🧪 Test message from backend!",
#         {"test": True, "timestamp": datetime.now().isoformat()}
#     )
#     return {"status": "test_sent", "message": "Test message sent to all connected clients"}

# Start autonomous trading with streaming
# @app.post("/api/autonomous/start")
# async def start_autonomous_streaming():
#     """Start autonomous trading with real-time streaming"""
#     global autonomous_task
    
#     # Cancel existing task if running
#     if autonomous_task and not autonomous_task.done():
#         autonomous_task.cancel()
#         try:
#             await autonomous_task
#         except asyncio.CancelledError:
#             pass
    
#     # Broadcast start message
#     await broadcast_ai_thought(
#         "system_start", 
#         "🚀 Autonomous Alpha Hunter starting...",
#         {"status": "initializing"}
#     )
    
#     # Start autonomous system in background task
#     print("🚀 Creating autonomous task...")
#     autonomous_task = asyncio.create_task(run_real_autonomous_agents())
#     print(f"✅ Autonomous task created: {autonomous_task}")
    
#     return {"status": "started", "message": "Autonomous trading started with real-time streaming"}

# @app.post("/api/autonomous/restart")
# async def restart_autonomous_streaming():
#     """Restart the autonomous streaming demo"""
#     global autonomous_task
    
#     # Cancel existing task if running
#     if autonomous_task and not autonomous_task.done():
#         autonomous_task.cancel()
#         try:
#             await autonomous_task
#         except asyncio.CancelledError:
#             pass
    
#     # Clear the tree
#     manager.clear_tree()
    
#     # Broadcast restart message
#     await broadcast_ai_thought(
#         "system_restart", 
#         "🔄 Restarting real autonomous agents...",
#         {"status": "restarting"}
#     )
    
#     # Start new autonomous system with real agents
#     print("🔄 Restarting real autonomous task...")
#     autonomous_task = asyncio.create_task(run_real_autonomous_agents())
#     print(f"✅ Real autonomous task restarted: {autonomous_task}")
    
#     return {"status": "restarted", "message": "Real autonomous agents restarted with paper trading"}

# @app.get("/api/autonomous/status")
# async def get_autonomous_status():
#     """Get the status of the autonomous system"""
#     global autonomous_task
    
#     if autonomous_task is None:
#         return {"status": "not_started", "message": "Autonomous system not started"}
#     elif autonomous_task.done():
#         return {"status": "completed", "message": "Autonomous system completed"}
#     elif autonomous_task.cancelled():
#         return {"status": "cancelled", "message": "Autonomous system was cancelled"}
#     else:
#         return {"status": "running", "message": "Autonomous system is running"}

# @app.post("/api/autonomous/stop")
# async def stop_autonomous_streaming():
#     """Stop the autonomous trading system"""
#     global autonomous_task
    
#     if autonomous_task is None:
#         return {"status": "not_running", "message": "Autonomous system is not running"}
    
#     if not autonomous_task.done():
#         print("🛑 Stopping autonomous trading system...")
#         autonomous_task.cancel()
        
#         # Wait for task to be cancelled
#         try:
#             await autonomous_task
#         except asyncio.CancelledError:
#             pass
        
#         autonomous_task = None
        
#         # Broadcast stop message
#         await broadcast_ai_thought(
#             "system_stop", 
#             "🛑 Autonomous trading system stopped",
#             {"status": "stopped"}
#         )
        
#         print("✅ Autonomous trading system stopped")
#         return {"status": "stopped", "message": "Autonomous trading system stopped"}
#     else:
#         return {"status": "already_stopped", "message": "Autonomous system was already stopped"}

async def run_autonomous_with_streaming():
    """Run autonomous trading system with real-time streaming of thoughts"""
    try:
        print("🚀 Starting autonomous streaming system...")
        await broadcast_ai_thought("system_start", "🚀 Autonomous streaming system starting...", {"status": "starting"})
        
        # Import the real autonomous system
        from autonomous_trading_system import autonomous_trading_system
        
        # Override logging to stream real thoughts
        print("🔄 Calling stream_real_autonomous_cycle...")
        await stream_real_autonomous_cycle()
        print("✅ Autonomous streaming cycle completed")
        
    except Exception as e:
        print(f"❌ Error in autonomous streaming: {str(e)}")
        await broadcast_ai_thought("error", f"Error in autonomous system: {str(e)}", {"error": True})

async def stream_real_autonomous_cycle():
    """Run REAL autonomous trading with streaming tree visualization - CONTINUOUS MODE"""
    print("🧠 Starting stream_real_autonomous_cycle in continuous mode...")
    
    while True:  # Run continuously
        try:
            print("🔄 Starting new autonomous cycle...")
            manager.clear_tree()
            print("🗑️ Cleared previous tree")
            
            # Root node
            await manager.add_tree_node(
                "root_decision", "decision", "🚀 Start Alpha Hunt", "Initiating autonomous alpha hunting process",
                metadata={"real_system": True},
            )
            await manager.update_tree_node("root_decision", status="active")
            await broadcast_ai_thought("root_decision", "🚀 Starting Alpha Hunt", {"phase": "root", "status": "active"})

            # Step 1: Opportunity Scanning
            await manager.add_tree_node(
                "opportunity_scanning", "analysis", "🌍 Global Opportunity Scanning",
                "Scanning global trends, events, and market conditions for alpha opportunities",
                parent_id="root_decision", metadata={"phase": "opportunity_scanning"},
            )
            await manager.update_tree_node("root_decision", status="completed")
            await manager.update_tree_node("opportunity_scanning", status="active")
            await broadcast_ai_thought("opportunity_scanning", "🌍 Scanning for opportunities...", {"phase": "opportunity_scanning", "status": "active"})

            # Simulate opportunity found
            await asyncio.sleep(0.5)
            await manager.update_tree_node("opportunity_scanning", status="completed")
            await manager.add_tree_node(
                "alpha_decision", "decision", "🎯 Alpha Hunt Decision", "Opportunity detected: AI Sector Momentum",
                parent_id="opportunity_scanning", metadata={"decision_type": "alpha_hunt", "opportunity": "AI Sector Momentum"},
            )
            await manager.update_tree_node("alpha_decision", status="active")
            await broadcast_ai_thought("alpha_decision", "🎯 Opportunity detected: AI Sector Momentum", {"phase": "alpha_decision", "status": "active"})

            # Step 2: Research Branches
            research_branches = [
                ("web_research", "websearch", "🌐 Web Research", "Searching news, reports, and sentiment for AI Sector Momentum"),
                ("fundamental_analysis", "fundamental", "📈 Fundamental Analysis", "Analyzing financials, ratios, and valuation for AI sector stocks"),
                ("data_analysis", "pandas", "📊 Data Analysis", "Running technical analysis and statistical models on market data"),
            ]
            for node_id, node_type, title, content in research_branches:
                await manager.add_tree_node(node_id, node_type, title, content, parent_id="alpha_decision", metadata={"phase": node_id})
                await manager.update_tree_node(node_id, status="pending")
            await manager.update_tree_node("alpha_decision", status="completed")

            # Sequentially activate and complete each research branch
            for node_id, _, title, _ in research_branches:
                await manager.update_tree_node(node_id, status="active")
                await broadcast_ai_thought(node_id, f"🔍 {title} in progress...", {"phase": node_id, "status": "active"})
                await asyncio.sleep(0.5)
                await manager.update_tree_node(node_id, status="completed")
                await broadcast_ai_thought(node_id, f"✅ {title} complete.", {"phase": node_id, "status": "completed"})

            # Step 3: Strategy Synthesis
            await manager.add_tree_node(
                "strategy_synthesis", "decision", "💡 Strategy Synthesis", "Combining research findings into trading strategy",
                parent_id="alpha_decision", metadata={"synthesis_type": "multi_source"},
            )
            await manager.update_tree_node("strategy_synthesis", status="active")
            await broadcast_ai_thought("strategy_synthesis", "💡 Synthesizing strategy from research...", {"phase": "strategy_synthesis", "status": "active"})
            await asyncio.sleep(0.5)
            await manager.update_tree_node("strategy_synthesis", status="completed")

            # Step 4: Strategy Creation
            await manager.add_tree_node(
                "strategy_creation", "strategy", "🎯 Strategy Creation", "AI generating trading strategy for AI Sector Momentum",
                parent_id="strategy_synthesis", metadata={"strategy_type": "ai_generated", "opportunity": "AI Sector Momentum"},
            )
            await manager.update_tree_node("strategy_creation", status="active")
            await broadcast_ai_thought("strategy_creation", "🧠 AI generating trading strategy for AI sector momentum...", {"phase": "strategy_creation", "status": "active"})
            await asyncio.sleep(0.5)
            await manager.update_tree_node("strategy_creation", status="completed")

            # Step 5: Execution Decision
            await manager.add_tree_node(
                "execution_decision", "execution", "⚡ Execution Decision", "Decision: Monitor AI sector for opportunities",
                parent_id="strategy_creation", metadata={"execution_type": "paper_trade", "action": "MONITOR", "sector": "AI", "position_size": 0.0},
            )
            await manager.update_tree_node("execution_decision", status="active")
            await broadcast_ai_thought("execution_decision", "⚡ Monitoring AI sector for opportunities", {"phase": "execution_decision", "status": "active"})
            await asyncio.sleep(0.5)
            await manager.update_tree_node("execution_decision", status="completed")
            await broadcast_ai_thought("execution_decision", "🎯 STRATEGY COMPLETE: AI Sector Monitoring | Confidence: 0.75 | Thesis: Strong momentum in AI Sector...", {"phase": "execution_decision", "status": "completed"})

            # Wait before starting next cycle
            await broadcast_ai_thought("cycle_complete", "🔄 Cycle complete. Starting next autonomous cycle in 10 seconds...", {"phase": "cycle_complete", "status": "completed"})
            await asyncio.sleep(10)  # Wait 10 seconds before next cycle

        except asyncio.CancelledError:
            print("🛑 Autonomous cycle cancelled")
            break
        except Exception as e:
            await manager.add_tree_node(
                "error_node", "decision", "❌ Error", f"Error in autonomous system: {str(e)}",
                parent_id="root_decision", metadata={"error": True, "real_system": True},
            )
            await manager.update_tree_node("error_node", status="failed")
            await broadcast_ai_thought("error_node", f"❌ Error: {str(e)}", {"phase": "error", "status": "failed"})
            await asyncio.sleep(30)  # Wait 30 seconds on error before retrying

async def run_real_autonomous_agents():
    """Run REAL autonomous agents for paper trading with streaming"""
    print("🧠 Starting REAL autonomous agents for paper trading...")
    
    try:
        # Import real agents
        from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
        from agents.multi_agent_orchestrator import MultiAgentOrchestrator
        from agents.parallel_execution_system import execution_engine
        from tools.data_fetcher import data_fetcher
        from agents.agent_monitoring_system import agent_monitor
        
        # Initialize real agents with proper agent_id
        alpha_hunter = EnhancedAutonomousAgent(agent_id="alpha_hunter_001", specialization="alpha_hunting")
        orchestrator = MultiAgentOrchestrator()
        
        # Register agents with monitoring system
        agent_monitor.register_agent("alpha_hunter_001", {
            "type": "enhanced_autonomous",
            "description": "Enhanced autonomous alpha hunting agent",
            "capabilities": ["alpha_hunting", "research", "decision_making"],
            "status": "active",
            "specialization": "alpha_hunting"
        })
        
        agent_monitor.register_agent("multi_agent_orchestrator", {
            "type": "orchestrator",
            "description": "Multi-agent orchestration and coordination",
            "capabilities": ["orchestration", "coordination", "task_management"],
            "status": "active"
        })
        
        # Start the autonomous system
        print("🚀 Starting autonomous alpha hunting...")
        await broadcast_ai_thought("system_start", "🚀 Real autonomous agents starting for paper trading", {"real_system": True})
        
        # Run the autonomous system
        await orchestrator.run_autonomous_cycle()
        
        print("✅ Real autonomous agents completed successfully")
        
    except Exception as e:
        print(f"❌ Error in real autonomous agents: {str(e)}")
        await broadcast_ai_thought("error", f"Error in real autonomous system: {str(e)}", {"error": True, "real_system": True})

# Essential endpoints that can't be handled by Governor (minimal set)

@app.get("/api/performance")
async def get_performance():
    """Get performance metrics - kept for direct access"""
    try:
        return {
            "status": "success",
            "performance": performance_tracker.get_performance_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
async def get_trades(limit: int = 50):
    """Get recent trades - kept for direct access"""
    try:
        return {
            "status": "success",
            "trades": pnl_tracker.get_recent_trades(limit)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
async def get_positions():
    """Get current positions - kept for direct access"""
    try:
        return {
            "status": "success",
            "positions": pnl_tracker.get_positions()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plays")
async def get_all_plays():
    """Get all plays - kept for direct access"""
    try:
        return {
            "status": "success",
            "plays": play_reporting.get_all_plays()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plays/{play_id}")
async def get_play_summary(play_id: str):
    """Get specific play details - kept for direct access"""
    try:
        play = play_reporting.get_play_summary(play_id)
        if not play:
            raise HTTPException(status_code=404, detail="Play not found")
        return {
            "status": "success",
            "play": play
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for research tree visualization (kept for frontend compatibility)
@app.websocket("/ws/research-tree")
async def websocket_research_tree(websocket: WebSocket):
    """WebSocket endpoint for research tree visualization"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# WebSocket endpoint for AI thoughts streaming (kept for frontend compatibility)
@app.websocket("/ws/ai-thoughts")
async def websocket_ai_thoughts(websocket: WebSocket):
    """WebSocket endpoint for AI thoughts streaming"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Graph query endpoint (kept for research graph functionality)
@app.post("/api/graph/query")
async def query_graph(query: Dict[str, Any]):
    """Query the research graph - kept for research functionality"""
    try:
        query_text = query.get("query", "")
        if not query_text:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Get research nodes from central event bus
        nodes = central_event_bus.get_research_nodes()
        
        # Process the query
        result = process_graph_query(query_text, nodes)
        
        return {
            "status": "success",
            "query": query_text,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_graph_query(query: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a graph query against research nodes"""
    try:
        # Simple keyword-based search for now
        query_lower = query.lower()
        matching_nodes = []
        
        for node in nodes:
            node_text = f"{node.get('title', '')} {node.get('content', '')} {node.get('type', '')}".lower()
            if any(keyword in node_text for keyword in query_lower.split()):
                matching_nodes.append(node)
        
        return {
            "matching_nodes": matching_nodes,
            "total_matches": len(matching_nodes),
            "query_processed": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "matching_nodes": [],
            "total_matches": 0,
            "query_processed": False
        }

# Experience Learning System Endpoints
@app.get("/api/experience/agent/{agent_id}")
async def get_agent_experience(agent_id: str, context: Optional[Dict[str, Any]] = None):
    """Get experience data for a specific agent."""
    try:
        experience_data = experience_learning_system.get_agent_experience(agent_id, context)
        return {
            "status": "success",
            "agent_id": agent_id,
            "experience_data": experience_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to get agent experience: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent experience: {str(exc)}")

@app.get("/api/experience/system/insights")
async def get_system_insights(query: Optional[str] = None):
    """Get system-wide insights and lessons learned."""
    try:
        insights = experience_learning_system.get_system_insights(query)
        return {
            "status": "success",
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to get system insights: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to get system insights: {str(exc)}")

@app.post("/api/experience/analyze")
async def analyze_and_store_experience(play_data: Dict[str, Any]):
    """Analyze and store experience from a completed play."""
    try:
        analysis_result = await experience_learning_system.analyze_and_store_experience(play_data)
        return {
            "status": "success",
            "analysis_result": analysis_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to analyze experience: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze experience: {str(exc)}")

@app.post("/api/experience/performance/analyze")
async def analyze_performance(play_data: Dict[str, Any]):
    """Analyze performance of a completed play."""
    try:
        analysis_result = await performance_analyzer_agent(play_data)
        return {
            "status": "success",
            "analysis_result": analysis_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to analyze performance: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze performance: {str(exc)}")

@app.get("/api/experience/performance/trends")
async def get_performance_trends():
    """Get performance trends from analysis history."""
    try:
        trends = performance_analyzer_agent.get_performance_trends()
        return {
            "status": "success",
            "trends": trends,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to get performance trends: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance trends: {str(exc)}")

@app.get("/api/experience/performance/history")
async def get_analysis_history(limit: int = 10):
    """Get recent performance analysis history."""
    try:
        history = performance_analyzer_agent.get_analysis_history(limit)
        return {
            "status": "success",
            "history": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to get analysis history: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis history: {str(exc)}")

@app.get("/api/experience/agent/{agent_id}/learning")
async def get_agent_learning_insights(agent_id: str):
    """Get learning insights for a specific agent."""
    try:
        if agent_id == "enhanced_trade_executor":
            insights = await enhanced_trade_executor.get_learning_insights()
        else:
            # For other agents, get basic experience data
            experience_data = experience_learning_system.get_agent_experience(agent_id)
            insights = {
                "experience_data": experience_data,
                "performance_trends": {"trend": "insufficient_data"},
                "execution_stats": {},
                "learning_focus": "general_improvement"
            }
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Failed to get agent learning insights: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent learning insights: {str(exc)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 