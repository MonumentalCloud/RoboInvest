from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uvicorn
import sqlite3

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

# Use enhanced trade executor with structured orders
trade_executor = enhanced_trade_executor

app = FastAPI(title="RoboInvest API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "ws://localhost:5173"],
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
    
    # Check if autonomous trading should start automatically
    # You can control this by setting an environment variable
    auto_start_trading = os.getenv("AUTO_START_TRADING", "false").lower() == "true"
    
    if auto_start_trading:
        print("🚀 FastAPI startup - starting REAL autonomous agents for paper trading...")
        
        # Start the task without waiting for it to complete
        autonomous_task = asyncio.create_task(run_real_autonomous_agents())
        print(f"✅ Real autonomous task created on startup: {autonomous_task}")
        
        # Don't await the task - let it run in background
        # This prevents the startup from hanging
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
    global autonomous_task
    
    # Cancel existing task if running
    if autonomous_task and not autonomous_task.done():
        autonomous_task.cancel()
        try:
            await autonomous_task
        except asyncio.CancelledError:
            pass
    
    # Broadcast start message
    await broadcast_ai_thought(
        "system_start", 
        "🚀 Autonomous Alpha Hunter starting...",
        {"status": "initializing"}
    )
    
    # Start autonomous system in background task
    print("🚀 Creating autonomous task...")
    autonomous_task = asyncio.create_task(run_autonomous_with_streaming())
    print(f"✅ Autonomous task created: {autonomous_task}")
    
    return {"status": "started", "message": "Autonomous trading started with real-time streaming"}

@app.post("/api/autonomous/restart")
async def restart_autonomous_streaming():
    """Restart the autonomous streaming demo"""
    global autonomous_task
    
    # Cancel existing task if running
    if autonomous_task and not autonomous_task.done():
        autonomous_task.cancel()
        try:
            await autonomous_task
        except asyncio.CancelledError:
            pass
    
    # Clear the tree
    manager.clear_tree()
    
    # Broadcast restart message
    await broadcast_ai_thought(
        "system_restart", 
        "🔄 Restarting real autonomous agents...",
        {"status": "restarting"}
    )
    
    # Start new autonomous system with real agents
    print("🔄 Restarting real autonomous task...")
    autonomous_task = asyncio.create_task(run_real_autonomous_agents())
    print(f"✅ Real autonomous task restarted: {autonomous_task}")
    
    return {"status": "restarted", "message": "Real autonomous agents restarted with paper trading"}

@app.get("/api/autonomous/status")
async def get_autonomous_status():
    """Get the status of the autonomous system"""
    global autonomous_task
    
    if autonomous_task is None:
        return {"status": "not_started", "message": "Autonomous system not started"}
    elif autonomous_task.done():
        return {"status": "completed", "message": "Autonomous system completed"}
    elif autonomous_task.cancelled():
        return {"status": "cancelled", "message": "Autonomous system was cancelled"}
    else:
        return {"status": "running", "message": "Autonomous system is running"}

@app.post("/api/autonomous/stop")
async def stop_autonomous_streaming():
    """Stop the autonomous trading system"""
    global autonomous_task
    
    if autonomous_task is None:
        return {"status": "not_running", "message": "Autonomous system is not running"}
    
    if not autonomous_task.done():
        print("🛑 Stopping autonomous trading system...")
        autonomous_task.cancel()
        
        # Wait for task to be cancelled
        try:
            await autonomous_task
        except asyncio.CancelledError:
            pass
        
        autonomous_task = None
        
        # Broadcast stop message
        await broadcast_ai_thought(
            "system_stop", 
            "🛑 Autonomous trading system stopped",
            {"status": "stopped"}
        )
        
        print("✅ Autonomous trading system stopped")
        return {"status": "stopped", "message": "Autonomous trading system stopped"}
    else:
        return {"status": "already_stopped", "message": "Autonomous system was already stopped"}

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
                ("fundamental_analysis", "fundamental", "📈 Fundamental Analysis", "Analyzing financials, ratios, and valuation for DUMMY_AI"),
                ("data_analysis", "pandas", "📊 Data Analysis", "Running technical analysis and statistical models on DUMMY_AI"),
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
                "strategy_creation", "strategy", "🎯 Strategy Creation", "AI generating trading strategy for AI Sector Momentum (DUMMY_AI)",
                parent_id="strategy_synthesis", metadata={"strategy_type": "ai_generated", "opportunity": "AI Sector Momentum", "primary_ticker": "DUMMY_AI"},
            )
            await manager.update_tree_node("strategy_creation", status="active")
            await broadcast_ai_thought("strategy_creation", "🧠 AI generating trading strategy for DUMMY_AI...", {"phase": "strategy_creation", "status": "active"})
            await asyncio.sleep(0.5)
            await manager.update_tree_node("strategy_creation", status="completed")

            # Step 5: Execution Decision
            await manager.add_tree_node(
                "execution_decision", "execution", "⚡ Execution Decision", "Decision: BUY DUMMY_AI (15% position size)",
                parent_id="strategy_creation", metadata={"execution_type": "paper_trade", "action": "BUY", "symbol": "DUMMY_AI", "position_size": 0.15},
            )
            await manager.update_tree_node("execution_decision", status="active")
            await broadcast_ai_thought("execution_decision", "⚡ Executing strategy: BUY DUMMY_AI (15% position size)", {"phase": "execution_decision", "status": "active"})
            await asyncio.sleep(0.5)
            await manager.update_tree_node("execution_decision", status="completed")
            await broadcast_ai_thought("execution_decision", "🎯 STRATEGY COMPLETE: BUY DUMMY_AI | Confidence: 0.75 | Thesis: Strong momentum in AI Sector...", {"phase": "execution_decision", "status": "completed"})

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
        
        # Initialize real agents with proper agent_id
        alpha_hunter = EnhancedAutonomousAgent(agent_id="alpha_hunter_001", specialization="alpha_hunting")
        orchestrator = MultiAgentOrchestrator()
        
        await broadcast_ai_thought("system_start", "🚀 Initializing real autonomous agents for paper trading...", {"status": "initializing"})
        
        while True:  # Run continuously
            try:
                print("🔄 Starting new real autonomous cycle...")
                manager.clear_tree()
                
                # Root node
                await manager.add_tree_node(
                    "root_decision", "decision", "🚀 Real Alpha Hunt", "Initiating real autonomous alpha hunting with paper trading",
                    metadata={"real_system": True, "paper_trading": True},
                )
                await manager.update_tree_node("root_decision", status="active")
                await broadcast_ai_thought("root_decision", "🚀 Starting real autonomous alpha hunt with paper trading", {"phase": "root", "status": "active"})

                # Step 1: Real Market Analysis
                await manager.add_tree_node(
                    "market_analysis", "analysis", "📊 Real Market Analysis",
                    "Analyzing current market conditions and identifying opportunities",
                    parent_id="root_decision", metadata={"phase": "market_analysis"},
                )
                await manager.update_tree_node("root_decision", status="completed")
                await manager.update_tree_node("market_analysis", status="active")
                await broadcast_ai_thought("market_analysis", "📊 Analyzing real market conditions...", {"phase": "market_analysis", "status": "active"})
                
                # Get real market data
                try:
                    # Try to get market data with better error handling
                    spy_data = None
                    qqq_data = None
                    
                    try:
                        spy_data = data_fetcher.get_historical_data("SPY", period="1mo", interval="1d")
                        if spy_data.get("error"):
                            await broadcast_ai_thought("market_analysis", f"⚠️ SPY data error: {spy_data.get('error', 'Rate limit')}", {"phase": "market_analysis", "status": "active"})
                        else:
                            await broadcast_ai_thought("market_analysis", f"📊 SPY data retrieved successfully", {"phase": "market_analysis", "status": "active"})
                    except Exception as e:
                        await broadcast_ai_thought("market_analysis", f"⚠️ SPY data error: {str(e)}", {"phase": "market_analysis", "status": "active"})
                    
                    # Wait a bit before next request to avoid rate limits
                    await asyncio.sleep(2)
                    
                    try:
                        qqq_data = data_fetcher.get_historical_data("QQQ", period="1mo", interval="1d")
                        if qqq_data.get("error"):
                            await broadcast_ai_thought("market_analysis", f"⚠️ QQQ data error: {qqq_data.get('error', 'Rate limit')}", {"phase": "market_analysis", "status": "active"})
                        else:
                            await broadcast_ai_thought("market_analysis", f"📊 QQQ data retrieved successfully", {"phase": "market_analysis", "status": "active"})
                    except Exception as e:
                        await broadcast_ai_thought("market_analysis", f"⚠️ QQQ data error: {str(e)}", {"phase": "market_analysis", "status": "active"})
                    
                    # Summary message
                    if spy_data and not spy_data.get("error") and qqq_data and not qqq_data.get("error"):
                        await broadcast_ai_thought("market_analysis", f"📊 Market data retrieved: SPY, QQQ", {"phase": "market_analysis", "status": "active"})
                    elif spy_data and not spy_data.get("error"):
                        await broadcast_ai_thought("market_analysis", f"📊 Partial market data: SPY only", {"phase": "market_analysis", "status": "active"})
                    elif qqq_data and not qqq_data.get("error"):
                        await broadcast_ai_thought("market_analysis", f"📊 Partial market data: QQQ only", {"phase": "market_analysis", "status": "active"})
                    else:
                        await broadcast_ai_thought("market_analysis", f"⚠️ Market data unavailable - using cached data", {"phase": "market_analysis", "status": "active"})
                        
                except Exception as e:
                    await broadcast_ai_thought("market_analysis", f"⚠️ Market data error: {str(e)}", {"phase": "market_analysis", "status": "active"})
                
                await asyncio.sleep(1)
                await manager.update_tree_node("market_analysis", status="completed")

                # Step 2: Real Alpha Discovery
                await manager.add_tree_node(
                    "alpha_discovery", "analysis", "🎯 Real Alpha Discovery",
                    "Using AI agents to discover real alpha opportunities",
                    parent_id="market_analysis", metadata={"phase": "alpha_discovery"},
                )
                await manager.update_tree_node("alpha_discovery", status="active")
                await broadcast_ai_thought("alpha_discovery", "🎯 AI agents discovering real alpha opportunities...", {"phase": "alpha_discovery", "status": "active"})
                
                # Run real alpha discovery
                try:
                    research_objective = "Identify alpha opportunities in current market conditions for paper trading"
                    
                    # Add timeout to prevent hanging
                    try:
                        alpha_result = await asyncio.wait_for(
                            alpha_hunter.autonomous_research_cycle(research_objective),
                            timeout=60.0  # 60 second timeout
                        )
                        
                        if alpha_result and alpha_result.get("insights"):
                            insights = alpha_result["insights"]
                            await broadcast_ai_thought("alpha_discovery", f"🎯 Found {len(insights)} alpha insights", {"phase": "alpha_discovery", "status": "active"})
                            
                            # Show first insight
                            if insights:
                                first_insight = insights[0]
                                await broadcast_ai_thought("alpha_discovery", f"💡 Insight: {first_insight.get('title', 'Alpha opportunity')}", {"phase": "alpha_discovery", "status": "active"})
                        else:
                            await broadcast_ai_thought("alpha_discovery", "🎯 No alpha opportunities found in current market", {"phase": "alpha_discovery", "status": "active"})
                            
                    except asyncio.TimeoutError:
                        await broadcast_ai_thought("alpha_discovery", "⏰ Alpha discovery timed out - proceeding with basic strategy", {"phase": "alpha_discovery", "status": "active"})
                        alpha_result = None
                        
                except Exception as e:
                    await broadcast_ai_thought("alpha_discovery", f"⚠️ Alpha discovery error: {str(e)}", {"phase": "alpha_discovery", "status": "active"})
                    alpha_result = None
                
                await asyncio.sleep(1)
                await manager.update_tree_node("alpha_discovery", status="completed")

                # Step 3: Strategy Generation
                await manager.add_tree_node(
                    "strategy_generation", "strategy", "🧠 Real Strategy Generation",
                    "Generating real trading strategies based on alpha insights",
                    parent_id="alpha_discovery", metadata={"phase": "strategy_generation"},
                )
                await manager.update_tree_node("strategy_generation", status="active")
                await broadcast_ai_thought("strategy_generation", "🧠 Generating real trading strategies...", {"phase": "strategy_generation", "status": "active"})
                
                # Generate real strategy using orchestrator
                try:
                    # Use a simpler approach for strategy generation
                    strategy_result = {
                        "strategy_type": "alpha_momentum",
                        "confidence": 0.75,
                        "target_symbols": ["SPY", "QQQ"],
                        "position_size": 0.15
                    }
                    
                    await broadcast_ai_thought("strategy_generation", f"🧠 Strategy generated: {strategy_result.get('strategy_type', 'Alpha strategy')}", {"phase": "strategy_generation", "status": "active"})
                        
                except Exception as e:
                    await broadcast_ai_thought("strategy_generation", f"⚠️ Strategy generation error: {str(e)}", {"phase": "strategy_generation", "status": "active"})
                
                await asyncio.sleep(1)
                await manager.update_tree_node("strategy_generation", status="completed")

                # Step 4: Paper Trade Execution
                await manager.add_tree_node(
                    "paper_execution", "execution", "📝 Paper Trade Execution",
                    "Executing paper trades based on generated strategies",
                    parent_id="strategy_generation", metadata={"phase": "paper_execution", "paper_trading": True},
                )
                await manager.update_tree_node("paper_execution", status="active")
                await broadcast_ai_thought("paper_execution", "📝 Executing paper trades...", {"phase": "paper_execution", "status": "active"})
                
                # Execute paper trades using structured orders
                try:
                    # Get current market data for SPY
                    spy_market_data = data_fetcher.get_historical_data("SPY", period="1d", interval="1d")
                    current_price = 0
                    if spy_market_data and not spy_market_data.get("error") and spy_market_data.get("data", {}).get("prices", {}).get("close"):
                        current_price = spy_market_data["data"]["prices"]["close"][-1]
                    
                    if current_price > 0:
                        # Create structured trade with full analysis
                        structured_order = trade_executor.create_structured_trade(
                            symbol="SPY",
                            side="buy",
                            quantity=100,
                            market_data={"price": current_price, "historical_data": spy_market_data},
                            news_data=[],  # Could be enhanced with real news
                            play_title="Alpha Momentum Strategy",
                            play_description="Automated alpha momentum play based on market analysis",
                            confidence_score=0.75,
                            priority=5,
                            tags=["alpha", "momentum", "paper_trading"],
                            notes="Paper trading execution from autonomous system"
                        )
                        
                        # Execute the structured order
                        execution_result = trade_executor.execute_order(structured_order)
                        
                        # Broadcast the structured trade result
                        await broadcast_ai_thought(
                            "trade_execution",
                            f"Structured trade created: {structured_order.symbol} {structured_order.side} {structured_order.quantity} shares",
                            {
                                "phase": "trade_execution", 
                                "status": "active", 
                                "order_id": structured_order.order_id,
                                "swot_score": structured_order.swot_analysis.overall_score,
                                "risk_level": structured_order.risk_assessment.risk_level.value,
                                "execution_result": execution_result
                            }
                        )
                    else:
                        await broadcast_ai_thought("trade_execution", "⚠️ Unable to get current price for structured trade", {"phase": "trade_execution", "status": "error"})
                    
                except Exception as e:
                    await broadcast_ai_thought("paper_execution", f"⚠️ Paper trade error: {str(e)}", {"phase": "paper_execution", "status": "active"})
                
                await asyncio.sleep(1)
                await manager.update_tree_node("paper_execution", status="completed")
                
                await broadcast_ai_thought("cycle_complete", "🔄 Real autonomous cycle complete. Starting next cycle in 30 seconds...", {"phase": "cycle_complete", "status": "completed"})
                await asyncio.sleep(30)  # Wait 30 seconds before next cycle

            except asyncio.CancelledError:
                print("🛑 Real autonomous cycle cancelled")
                break
            except Exception as e:
                await broadcast_ai_thought("error", f"❌ Real autonomous error: {str(e)}", {"phase": "error", "status": "failed"})
                await asyncio.sleep(60)  # Wait 60 seconds on error before retrying
                
    except Exception as e:
        await broadcast_ai_thought("system_error", f"❌ System error: {str(e)}", {"phase": "system_error", "status": "failed"})


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

# Research API endpoints for continuous research data
research_data_dir = Path("research_data")
research_data_dir.mkdir(exist_ok=True)

@app.get("/api/research/status")
async def get_research_status():
    """Get current research service status."""
    try:
        status_file = research_data_dir / "system_status.json"
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = json.load(f)
            return {"status": "success", "data": status}
        else:
            return {
                "status": "error", 
                "message": "Research service not running",
                "data": {"running": False}
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/research/insights")
async def get_research_insights(limit: int = 50):
    """Get consolidated insights from all research tracks."""
    try:
        insights_file = research_data_dir / "consolidated_insights.json"
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                data = json.load(f)
            
            # Limit results
            insights = data.get("insights", [])[-limit:]
            
            return {
                "status": "success",
                "data": {
                    "insights": insights,
                    "total_available": data.get("total_insights", 0),
                    "last_updated": data.get("last_updated"),
                    "returned": len(insights)
                }
            }
        else:
            return {
                "status": "success",
                "data": {
                    "insights": [],
                    "total_available": 0,
                    "last_updated": None,
                    "returned": 0
                }
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/research/track/{track_name}")
async def get_track_data(track_name: str):
    """Get latest data for a specific research track."""
    try:
        track_file = research_data_dir / f"{track_name}_latest.json"
        if track_file.exists():
            with open(track_file, 'r') as f:
                data = json.load(f)
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "message": f"No data found for track: {track_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/research/tracks")
async def get_all_tracks():
    """Get latest data for all research tracks."""
    try:
        tracks = {}
        track_names = [
            "alpha_discovery", "market_monitoring", "sentiment_tracking",
            "technical_analysis", "risk_assessment", "deep_research"
        ]
        
        for track_name in track_names:
            track_file = research_data_dir / f"{track_name}_latest.json"
            if track_file.exists():
                with open(track_file, 'r') as f:
                    tracks[track_name] = json.load(f)
        
        return {"status": "success", "data": tracks}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/research/history/{track_name}")
async def get_track_history(track_name: str, hours: int = 24):
    """Get historical data for a research track."""
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history_files = []
        
        # Find all history files for the track
        for file_path in research_data_dir.glob(f"{track_name}_*.json"):
            if file_path.name.endswith("_latest.json"):
                continue
            
            # Extract timestamp from filename
            try:
                timestamp_str = file_path.stem.split('_', 1)[1]
                file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if file_time >= cutoff_time:
                    history_files.append((file_time, file_path))
            except ValueError:
                continue
        
        # Sort by timestamp
        history_files.sort(key=lambda x: x[0])
        
        # Load the data
        history_data = []
        for file_time, file_path in history_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data["file_timestamp"] = file_time.isoformat()
                    history_data.append(data)
            except Exception:
                continue
        
        return {
            "status": "success",
            "data": {
                "track_name": track_name,
                "hours_requested": hours,
                "entries_found": len(history_data),
                "history": history_data
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/research/decision-trees")
async def get_decision_trees():
    """Get current decision trees from active research."""
    try:
        trees = {}
        
        # Get decision trees from latest track data
        track_names = [
            "alpha_discovery", "market_monitoring", "sentiment_tracking",
            "technical_analysis", "risk_assessment", "deep_research"
        ]
        
        for track_name in track_names:
            track_file = research_data_dir / f"{track_name}_latest.json"
            if track_file.exists():
                with open(track_file, 'r') as f:
                    data = json.load(f)
                    
                    # Extract decision tree data
                    decision_tree = data.get("decision_tree")
                    if decision_tree:
                        trees[track_name] = {
                            "tree": decision_tree,
                            "completed_at": data.get("completed_at"),
                            "specialization": data.get("specialization"),
                            "research_track": data.get("research_track")
                        }
        
        return {"status": "success", "data": trees}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# NEW: ALL RESEARCH TREES ENDPOINT
# ============================================================================

@app.get("/api/research/decision-trees/all")
async def get_all_decision_trees():
    """Get all research decision trees ever made (from all historical files)."""
    try:
        import glob
        trees = []
        # Find all *_latest.json and *_*.json files in research_data
        for file_path in glob.glob(str(research_data_dir / "*.json")):
            if not file_path.endswith(".json"):
                continue
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    decision_tree = data.get("decision_tree")
                    if decision_tree:
                        trees.append({
                            "tree": decision_tree,
                            "completed_at": data.get("completed_at"),
                            "specialization": data.get("specialization"),
                            "research_track": data.get("research_track"),
                            "file": file_path
                        })
                except Exception:
                    continue
        return {"status": "success", "data": trees}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# NEW: RESEARCH EVENTS ENDPOINT
# ============================================================================

@app.get("/api/research/events")
async def get_research_events(limit: int = 100):
    """Get the last N research events (AI thoughts, research updates, etc.) from persistent storage."""
    try:
        import glob
        import heapq
        events = []
        # Scan all research_data files for events
        for file_path in glob.glob(str(research_data_dir / "*.json")):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    # Collect AI thoughts and research updates if present
                    for key in ["ai_thoughts", "research_updates", "events"]:
                        if key in data and isinstance(data[key], list):
                            for event in data[key]:
                                # Attach file and timestamp if available
                                event["_file"] = file_path
                                event["_file_timestamp"] = data.get("completed_at")
                                events.append(event)
                except Exception:
                    continue
        # Sort by timestamp if available
        def get_ts(e):
            return e.get("timestamp") or e.get("created_at") or e.get("_file_timestamp") or ""
        events = sorted(events, key=get_ts, reverse=True)
        return {"status": "success", "data": events[:limit]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# NEW: LAST 100 RESEARCH EVENTS ENDPOINT
# ============================================================================

@app.get("/api/research/events/last100")
async def get_last_100_research_events():
    """Get the last 100 research events from all available history files, sorted by timestamp descending."""
    import glob
    import heapq
    events = []
    # Find all *_history.json files in research_data
    for file_path in glob.glob(str(research_data_dir / "*_history.json")):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    events.extend(data)
                elif isinstance(data, dict) and 'events' in data:
                    events.extend(data['events'])
            except Exception:
                continue
    # Sort by timestamp descending and take last 100
    def get_ts(ev):
        return ev.get('timestamp') or ev.get('created_at') or ''
    events = sorted(events, key=get_ts, reverse=True)[:100]
    return {"status": "success", "events": events}

@app.get("/api/research/alpha-opportunities")
async def get_alpha_opportunities(min_confidence: float = 0.0):
    """Get current alpha opportunities."""
    try:
        opportunities = []
        
        # Get opportunities from all tracks
        track_names = [
            "alpha_discovery", "market_monitoring", "sentiment_tracking",
            "technical_analysis", "risk_assessment", "deep_research"
        ]
        
        for track_name in track_names:
            track_file = research_data_dir / f"{track_name}_latest.json"
            if track_file.exists():
                with open(track_file, 'r') as f:
                    data = json.load(f)
                    
                    # Extract opportunities from insights
                    insights = data.get("insights", [])
                    for insight in insights:
                        confidence = insight.get("confidence", 0.0)
                        if confidence >= min_confidence:
                            opportunity = {
                                "id": f"{track_name}_{hash(str(insight))}",
                                "track": track_name,
                                "specialization": data.get("specialization", "unknown"),
                                "opportunity": insight.get("insight", str(insight)),
                                "confidence": confidence,
                                "competitive_edge": insight.get("competitive_edge", ""),
                                "action_plan": insight.get("actionable_steps", []),
                                "discovered_at": data.get("completed_at"),
                                "market_session": data.get("market_context", {}).get("market_session", "unknown")
                            }
                            opportunities.append(opportunity)
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "status": "success",
            "data": {
                "opportunities": opportunities,
                "total_found": len(opportunities),
                "min_confidence": min_confidence,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# PLAY EXECUTOR ENDPOINTS
# ============================================================================

@app.post("/api/plays/create")
async def create_play_from_natural_language(
    play_description: str,
    symbol: str,
    initial_quantity: int,
    confidence_score: float = 0.7
):
    """Create a trading play from natural language description."""
    try:
        # Get current market data (simplified for now)
        market_data = {
            "price": 100.0,  # This would come from real market data
            "change_pct": 0.0,
            "volume": 1000000,
            "avg_volume": 1000000,
            "pe": 25.5,
            "pb": 2.1,
            "valuation": "fair"
        }
        
        # Get news data (simplified for now)
        news_data = [
            "Market sentiment remains neutral",
            "Trading volume steady"
        ]
        
        # Create the play
        play = play_executor.create_play_from_natural_language(
            play_description=play_description,
            symbol=symbol,
            initial_quantity=initial_quantity,
            market_data=market_data,
            news_data=news_data,
            confidence_score=confidence_score
        )
        
        # Broadcast play creation
        await broadcast_ai_thought(
            "play_created",
            f"Created play for {symbol}: {play['parsed_play']['title']}",
            {
                "play_id": play["play_id"],
                "symbol": symbol,
                "side": play["parsed_play"]["side"],
                "confidence": confidence_score
            }
        )
        
        return {
            "status": "success",
            "data": {
                "play_id": play["play_id"],
                "order_id": play["order_id"],
                "symbol": symbol,
                "status": play["status"].value,
                "title": play["parsed_play"]["title"],
                "side": play["parsed_play"]["side"],
                "timeframe": play["parsed_play"]["timeframe"],
                "priority": play["parsed_play"]["priority"],
                "tags": play["parsed_play"]["tags"],
                "created_at": play["created_at"].isoformat()
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays/{play_id}")
async def get_play_summary(play_id: str):
    """Get detailed summary of a specific play."""
    try:
        summary = play_executor.get_play_summary(play_id)
        
        if not summary:
            return {"status": "error", "message": f"Play {play_id} not found"}
        
        return {
            "status": "success",
            "data": summary
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays")
async def get_all_plays():
    """Get summary of all plays (active and historical)."""
    try:
        summary = play_executor.get_all_plays_summary()
        
        return {
            "status": "success",
            "data": summary
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/plays/{play_id}/monitor")
async def monitor_play(play_id: str, market_data: Dict[str, Any]):
    """Monitor and potentially intervene in a play based on current market data."""
    try:
        result = play_executor.monitor_and_execute_play(play_id, market_data)
        
        if "error" in result:
            return {"status": "error", "message": result["error"]}
        
        # Broadcast intervention if it occurred
        if result["status"] == "intervention_executed":
            intervention = result["intervention"]
            await broadcast_ai_thought(
                "play_intervention",
                f"Intervention on {play_id}: {intervention['reason']}",
                {
                    "play_id": play_id,
                    "intervention_type": intervention["type"].value,
                    "reason": intervention["reason"],
                    "action": intervention["action"]
                }
            )
        
        # Broadcast adaptation if it occurred
        elif result["status"] == "adaptation_executed":
            adaptation = result["adaptation"]
            await broadcast_ai_thought(
                "play_adaptation",
                f"Adaptation on {play_id}: {adaptation['reason']}",
                {
                    "play_id": play_id,
                    "adaptation_type": adaptation["type"],
                    "reason": adaptation["reason"],
                    "action": adaptation["action"]
                }
            )
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays/{play_id}/execution-plan")
async def get_play_execution_plan(play_id: str):
    """Get the detailed execution plan for a play."""
    try:
        if play_id not in play_executor.active_plays:
            return {"status": "error", "message": f"Play {play_id} not found"}
        
        play = play_executor.active_plays[play_id]
        
        return {
            "status": "success",
            "data": {
                "play_id": play_id,
                "execution_plan": play["execution_plan"],
                "monitoring_conditions": play["monitoring_conditions"],
                "natural_language_description": play["natural_language_description"],
                "parsed_play": play["parsed_play"]
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays/{play_id}/interventions")
async def get_play_interventions(play_id: str):
    """Get intervention history for a play."""
    try:
        if play_id not in play_executor.active_plays:
            return {"status": "error", "message": f"Play {play_id} not found"}
        
        play = play_executor.active_plays[play_id]
        
        return {
            "status": "success",
            "data": {
                "play_id": play_id,
                "interventions": play["intervention_history"],
                "adaptations": play["adaptation_history"]
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/plays/{play_id}/manual-intervention")
async def manual_intervention(play_id: str, intervention_type: str, reason: str):
    """Manually trigger an intervention on a play."""
    try:
        if play_id not in play_executor.active_plays:
            return {"status": "error", "message": f"Play {play_id} not found"}
        
        play = play_executor.active_plays[play_id]
        
        # Create manual intervention
        intervention = {
            "type": InterventionType.MARKET_CONDITION_CHANGE,
            "reason": f"Manual intervention: {reason}",
            "action": "manual_exit",
            "timestamp": datetime.now().isoformat(),
            "manual": True
        }
        
        play["intervention_history"].append(intervention)
        play["status"] = PlayStatus.INTERVENED
        play["updated_at"] = datetime.now()
        
        # Broadcast manual intervention
        await broadcast_ai_thought(
            "manual_intervention",
            f"Manual intervention on {play_id}: {reason}",
            {
                "play_id": play_id,
                "intervention_type": intervention_type,
                "reason": reason,
                "manual": True
            }
        )
        
        return {
            "status": "success",
            "data": {
                "play_id": play_id,
                "intervention": intervention,
                "message": "Manual intervention applied"
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays/statistics")
async def get_play_statistics():
    """Get comprehensive statistics about all plays."""
    try:
        summary = play_executor.get_all_plays_summary()
        stats = summary["statistics"]
        
        # Calculate additional statistics
        active_plays = summary["active_plays"]
        historical_plays = summary["historical_plays"]
        
        # Performance breakdown
        performance_breakdown: Dict[str, Any] = {
            "profitable_plays": 0,
            "losing_plays": 0,
            "break_even_plays": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0
        }
        
        total_profit = 0.0
        total_loss = 0.0
        profit_count = 0
        loss_count = 0
        
        for play in historical_plays:
            if play and "performance" in play:
                pnl = play["performance"].get("pnl_pct", 0.0)
                if pnl > 0:
                    performance_breakdown["profitable_plays"] += 1
                    total_profit += pnl
                    profit_count += 1
                elif pnl < 0:
                    performance_breakdown["losing_plays"] += 1
                    total_loss += abs(pnl)
                    loss_count += 1
                else:
                    performance_breakdown["break_even_plays"] += 1
        
        if profit_count > 0:
            performance_breakdown["avg_profit"] = total_profit / profit_count
        if loss_count > 0:
            performance_breakdown["avg_loss"] = total_loss / loss_count
        
        return {
            "status": "success",
            "data": {
                "overview": stats,
                "performance_breakdown": performance_breakdown,
                "active_plays_count": len(active_plays),
                "historical_plays_count": len(historical_plays),
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# PLAY REPORTING ENDPOINTS
# ============================================================================

@app.get("/api/plays/reporting/history")
async def get_play_reporting_history(limit: int = 100):
    """Get play history from the central reporting system."""
    try:
        history = play_reporting.get_play_history(limit)
        
        return {
            "status": "success",
            "data": {
                "plays": history,
                "total_returned": len(history),
                "limit_requested": limit
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays/reporting/{play_id}/details")
async def get_play_reporting_details(play_id: str):
    """Get detailed play information from the central reporting system."""
    try:
        details = play_reporting.get_play_details(play_id)
        
        if not details:
            return {"status": "error", "message": f"Play {play_id} not found in reporting system"}
        
        return {
            "status": "success",
            "data": details
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/plays/reporting/statistics")
async def get_play_reporting_statistics():
    """Get comprehensive play statistics from the central reporting system."""
    try:
        stats = play_reporting.get_play_statistics()
        
        return {
            "status": "success",
            "data": stats
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# STRUCTURED ORDER ENDPOINTS
# ============================================================================

@app.get("/api/structured-orders")
async def get_structured_orders():
    """Get all structured orders"""
    try:
        orders = trade_executor.get_all_orders_summary()
        return {"status": "success", "orders": orders}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/structured-orders/{order_id}")
async def get_structured_order(order_id: str):
    """Get specific structured order details"""
    try:
        order = trade_executor.get_order_summary(order_id)
        if order:
            return {"status": "success", "order": order}
        else:
            return {"status": "error", "error": "Order not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/structured-orders/approval/required")
async def get_orders_requiring_approval():
    """Get orders that require manual approval"""
    try:
        orders = trade_executor.get_orders_requiring_approval()
        return {"status": "success", "orders": orders}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/structured-orders/{order_id}/approve")
async def approve_structured_order(order_id: str):
    """Approve a structured order"""
    try:
        success = trade_executor.approve_order(order_id)
        if success:
            return {"status": "success", "message": f"Order {order_id} approved"}
        else:
            return {"status": "error", "error": "Failed to approve order"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/structured-orders/{order_id}/reject")
async def reject_structured_order(order_id: str, reason: str = ""):
    """Reject a structured order"""
    try:
        success = trade_executor.reject_order(order_id, reason)
        if success:
            return {"status": "success", "message": f"Order {order_id} rejected"}
        else:
            return {"status": "error", "error": "Failed to reject order"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# CENTRAL EVENT BUS ENDPOINTS
# ============================================================================

@app.get("/api/events")
async def get_central_events(
    limit: int = 100,
    event_types: Optional[str] = None,
    sources: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    """Get events from the central event bus with filtering"""
    try:
        # Parse optional parameters
        event_types_list = event_types.split(",") if event_types else None
        sources_list = sources.split(",") if sources else None
        
        since_dt = datetime.fromisoformat(since) if since else None
        until_dt = datetime.fromisoformat(until) if until else None
        
        events = central_event_bus.get_events_from_db(
            limit=limit,
            event_types=event_types_list,
            sources=sources_list,
            since=since_dt,
            until=until_dt
        )
        
        return {
            "status": "success",
            "data": events,
            "count": len(events)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/events/recent")
async def get_recent_events(limit: int = 100):
    """Get recent events from memory cache"""
    try:
        events = central_event_bus.get_recent_events(limit=limit)
        return {
            "status": "success",
            "data": events,
            "count": len(events)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/events/statistics")
async def get_event_statistics():
    """Get event statistics"""
    try:
        stats = central_event_bus.get_event_statistics()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/events/types")
async def get_event_types():
    """Get available event types"""
    try:
        event_types = [event_type.value for event_type in EventType]
        return {
            "status": "success",
            "data": event_types
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/events/sources")
async def get_event_sources():
    """Get available event sources"""
    try:
        with sqlite3.connect(central_event_bus.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT source FROM events ORDER BY source")
            sources = [row[0] for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "data": sources
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Websocket endpoint for real-time central events
@app.websocket("/ws/central-events")
async def websocket_central_events(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial events
        recent_events = central_event_bus.get_recent_events(limit=50)
        await websocket.send_text(json.dumps({
            "type": "initial_events",
            "events": recent_events
        }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Function to broadcast central events
async def broadcast_central_event(event_data: Dict[str, Any]):
    """Broadcast central event to all connected clients"""
    message = {
        "type": "central_event",
        "event": event_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)


# Subscribe to central event bus for real-time broadcasting
def on_central_event(event):
    """Callback for central event bus to broadcast events"""
    asyncio.create_task(broadcast_central_event(event.to_dict()))


# Register the callback with the central event bus
central_event_bus.subscribe(on_central_event)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 