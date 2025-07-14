"""
Simplified RoboInvest FastAPI Application

This is the streamlined backend that implements the whitepaper architecture:
- Mission-driven, agile, connected, collaborative, and radically transparent
- Governor-centric control system
- Simplified agent coordination
- Unified real-time streaming
- Clean, maintainable codebase
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import uvicorn
import logging
from pathlib import Path

from utils.logger import logger
from core.config import config
from core.pnl_tracker import pnl_tracker
from core.performance_tracker import performance_tracker
from core.governor_directive_system import (
    governor_directive_system, DirectiveType, DirectivePriority, 
    DirectiveStatus, SystemContext, update_mission, update_strategy,
    adjust_risk_parameters, emergency_stop, update_research_priorities
)
from agents.agent_monitoring_system import agent_monitor
from core.alpaca_client import alpaca_client

# Initialize FastAPI app
app = FastAPI(
    title="RoboInvest Simplified API", 
    version="2.0.0",
    description="Streamlined autonomous trading system with governor-centric architecture"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
autonomous_task = None
manager = None

class SimplifiedConnectionManager:
    """Unified WebSocket connection manager for all real-time data"""
    
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.connection_types: Dict[WebSocket, str] = {}  # Track what each connection is for
        
    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.connections.append(websocket)
        self.connection_types[websocket] = connection_type
        
        # Send initial data based on connection type
        if connection_type == "governor":
            await self.send_initial_governor_data(websocket)
        elif connection_type == "dashboard":
            await self.send_initial_dashboard_data(websocket)
        
        logger.info(f"New {connection_type} connection established")
        
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            if websocket in self.connection_types:
                del self.connection_types[websocket]
            logger.info("WebSocket connection disconnected")
    
    async def broadcast(self, message: Dict[str, Any], connection_type: Optional[str] = None):
        """Broadcast message to all connections (or specific type)"""
        if not self.connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.connections:
            try:
                # Send to all connections or specific type
                if connection_type is None or self.connection_types.get(connection) == connection_type:
                    await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_initial_governor_data(self, websocket: WebSocket):
        """Send initial governor data to new connection"""
        try:
            # System context
            context = governor_directive_system.get_system_context()
            await websocket.send_text(json.dumps({
                "type": "initial_context",
                "context": context.to_dict()
            }))
            
            # Active directives
            directives = governor_directive_system.get_active_directives()
            await websocket.send_text(json.dumps({
                "type": "initial_directives",
                "directives": [d.to_dict() for d in directives]
            }))
            
            # System pulse
            pulse = self.get_system_pulse()
            await websocket.send_text(json.dumps({
                "type": "system_pulse",
                "pulse": pulse
            }))
            
        except Exception as e:
            logger.error(f"Error sending initial governor data: {e}")
    
    async def send_initial_dashboard_data(self, websocket: WebSocket):
        """Send initial dashboard data to new connection"""
        try:
            # Performance data
            performance = performance_tracker.get_performance_summary()
            await websocket.send_text(json.dumps({
                "type": "performance_data",
                "performance": performance
            }))
            
            # Recent trades
            trades = pnl_tracker.get_recent_trades(50)
            await websocket.send_text(json.dumps({
                "type": "trades_data",
                "trades": trades
            }))
            
            # Current positions
            positions = pnl_tracker.get_positions()
            await websocket.send_text(json.dumps({
                "type": "positions_data",
                "positions": positions
            }))
            
        except Exception as e:
            logger.error(f"Error sending initial dashboard data: {e}")
    
    def get_system_pulse(self) -> Dict[str, Any]:
        """Generate real-time system pulse data"""
        try:
            # Get real agent count
            active_agents = len(agent_monitor.heartbeats) if hasattr(agent_monitor, 'heartbeats') else 0
            
            # Get real trade count
            trades_executed = len(pnl_tracker.closed_trades) if hasattr(pnl_tracker, 'closed_trades') else 0
            
            # Get real research activities
            research_data_dir = Path("research_data")
            research_files = list(research_data_dir.glob("*_latest.json")) if research_data_dir.exists() else []
            research_activities = len(research_files)
            
            # Get active directives
            active_directives = len(governor_directive_system.get_active_directives())
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "active_agents": active_agents,
                "directives_processed": active_directives,
                "trades_executed": trades_executed,
                "research_activities": research_activities,
                "system_health": "operational",
                "mission": governor_directive_system.get_system_context().mission
            }
        except Exception as e:
            logger.error(f"Error generating system pulse: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "active_agents": 0,
                "directives_processed": 0,
                "trades_executed": 0,
                "research_activities": 0,
                "system_health": "error",
                "mission": "System error detected"
            }

# Initialize connection manager
manager = SimplifiedConnectionManager()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the simplified system on startup"""
    global manager
    
    logger.info("🚀 Starting Simplified RoboInvest System")
    
    # Start the governor directive system
    await governor_directive_system.start()
    
    # Start the central event bus
    from core.central_event_bus import central_event_bus
    await central_event_bus.start()
    
    # Setup governor subscriptions for real-time updates
    setup_governor_subscriptions()
    
    # Start background tasks
    asyncio.create_task(background_system_pulse())
    asyncio.create_task(background_agent_monitoring())
    
    # Check if autonomous trading should start
    auto_start = os.getenv("AUTO_START_TRADING", "false").lower() == "true"
    if auto_start:
        logger.info("🚀 Auto-starting autonomous trading system")
        asyncio.create_task(start_autonomous_system())
    
    logger.info("✅ Simplified RoboInvest System initialized")

def setup_governor_subscriptions():
    """Setup real-time subscriptions for governor system"""
    def broadcast_directive_update(directive):
        """Broadcast directive updates to all governor connections"""
        asyncio.create_task(manager.broadcast({
            "type": "directive_update",
            "directive": directive.to_dict()
        }, "governor"))
    
    def broadcast_context_update(context):
        """Broadcast context updates to all governor connections"""
        asyncio.create_task(manager.broadcast({
            "type": "context_update",
            "context": context.to_dict()
        }, "governor"))
    
    # Subscribe to governor system updates
    governor_directive_system.subscribe_to_directives(broadcast_directive_update)
    governor_directive_system.subscribe_to_context(broadcast_context_update)
    
    logger.info("👑 Governor subscriptions setup complete")

async def background_system_pulse():
    """Background task to update system pulse every 5 seconds"""
    while True:
        try:
            pulse = manager.get_system_pulse()
            await manager.broadcast({
                "type": "system_pulse",
                "pulse": pulse
            }, "governor")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error in background system pulse: {e}")
            await asyncio.sleep(5)

async def background_agent_monitoring():
    """Background task to monitor agent health and broadcast updates"""
    while True:
        try:
            # Get agent statuses
            agent_statuses = agent_monitor.get_all_agent_statuses()
            
            # Broadcast agent updates
            await manager.broadcast({
                "type": "agent_status_update",
                "agents": agent_statuses
            }, "governor")
            
            await asyncio.sleep(10)  # Update every 10 seconds
        except Exception as e:
            logger.error(f"Error in background agent monitoring: {e}")
            await asyncio.sleep(10)

async def start_autonomous_system():
    """Start the simplified autonomous trading system"""
    global autonomous_task
    
    try:
        logger.info("🧠 Starting simplified autonomous system")
        
        # Import the simplified autonomous system
        from agents.simplified_autonomous_system import SimplifiedAutonomousSystem
        
        # Create and start the system
        autonomous_system = SimplifiedAutonomousSystem()
        autonomous_task = asyncio.create_task(autonomous_system.run())
        
        logger.info("✅ Simplified autonomous system started")
        
    except Exception as e:
        logger.error(f"❌ Error starting autonomous system: {e}")

# ============================================================================
# ESSENTIAL API ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "system": "simplified_roboinvest"
    }

# ============================================================================
# GOVERNOR ENDPOINTS (Core Control System)
# ============================================================================

@app.get("/api/governor/context")
async def get_system_context():
    """Get current system context"""
    try:
        context = governor_directive_system.get_system_context()
        return {"status": "success", "context": context.to_dict()}
    except Exception as e:
        logger.error(f"Error getting system context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/governor/pulse")
async def get_system_pulse():
    """Get current system pulse"""
    try:
        pulse = manager.get_system_pulse()
        return {"status": "success", "pulse": pulse}
    except Exception as e:
        logger.error(f"Error getting system pulse: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/governor/directives")
async def get_directives(status: Optional[str] = None, limit: int = 50):
    """Get directives with optional filtering"""
    try:
        if status == "active":
            directives = governor_directive_system.get_active_directives()
        else:
            directives = list(governor_directive_system.directives.values())
        
        # Sort by timestamp and limit
        directives.sort(key=lambda x: x.timestamp, reverse=True)
        directives = directives[:limit]
        
        return {
            "status": "success",
            "directives": [d.to_dict() for d in directives],
            "total": len(directives)
        }
    except Exception as e:
        logger.error(f"Error getting directives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/governor/directives")
async def issue_directive(request: Dict[str, Any]):
    """Issue a new directive"""
    try:
        # Validate required fields
        required_fields = ["directive_type", "title", "description", "payload"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate directive type
        try:
            directive_type = DirectiveType(request["directive_type"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid directive type: {request['directive_type']}")
        
        # Validate priority
        priority = DirectivePriority.MEDIUM
        if "priority" in request:
            try:
                priority = DirectivePriority(request["priority"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {request['priority']}")
        
        # Issue directive
        directive_id = await governor_directive_system.issue_directive(
            directive_type=directive_type,
            title=request["title"],
            description=request["description"],
            payload=request["payload"],
            target_agents=request.get("target_agents", []),
            priority=priority,
            source=request.get("source", "human_governor"),
            metadata=request.get("metadata", {}),
            tags=request.get("tags", [])
        )
        
        return {
            "status": "success",
            "directive_id": directive_id,
            "message": f"Directive '{request['title']}' issued successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error issuing directive: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/governor/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Handle natural language conversation with the Governor Agent"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get current system context
        context = governor_directive_system.get_system_context()
        
        # Create AI prompt for natural language processing
        prompt = f"""
You are the Governor Agent, an AI administrative assistant for an autonomous trading system.
You have complete control over the system and can execute any changes the Human Governor requests.

Current System Context:
- Mission: {context.mission}
- Strategy: {context.current_strategy}
- System Mode: {context.system_mode}
- Active Agents: {len(governor_directive_system.get_active_directives())}
- Research Priorities: {', '.join(context.research_priorities)}

Human Governor Message: "{message}"

Respond naturally as if in a conversation. You can:
1. Answer questions about system status, agents, trades, performance
2. Execute system changes based on requests
3. Provide insights and recommendations
4. Ask clarifying questions if needed

Always be helpful, professional, and take action when requested.
"""

        # Get AI response
        try:
            from core.openai_manager import openai_manager
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
            
            response = openai_manager.chat_completion(messages=messages, temperature=0.7)
            response_text = response.get("content", "")
            
            # Execute actions based on message content
            actions_taken = await execute_conversation_actions(message, context)
            
            if actions_taken:
                response_text += f"\n\n✅ Actions taken: {', '.join(actions_taken)}"
            
            return {
                "status": "success",
                "response": response_text,
                "metadata": {
                    "actions_taken": actions_taken,
                    "context_used": True
                }
            }
            
        except Exception as ai_error:
            # Fallback response
            fallback_response = get_conversation_fallback_response(message, context)
            return {
                "status": "success",
                "response": fallback_response,
                "metadata": {
                    "actions_taken": [],
                    "context_used": True,
                    "fallback": True
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in governor conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_conversation_actions(message: str, context: SystemContext) -> List[str]:
    """Execute actions based on conversation content"""
    actions_taken = []
    message_lower = message.lower()
    
    # Mission updates
    if any(word in message_lower for word in ['mission', 'goal', 'objective']) and 'change' in message_lower:
        new_mission = "Discover the smartest and greatest upside that nobody is looking at"
        await update_mission(new_mission, "governor_agent")
        actions_taken.append("Updated system mission")
    
    # Risk adjustments
    if 'risk' in message_lower:
        if 'conservative' in message_lower:
            new_risk_params = {
                "max_position_size": 0.01,
                "max_daily_loss": 0.02,
                "correlation_threshold": 0.5,
                "volatility_threshold": 0.2
            }
            await adjust_risk_parameters(new_risk_params, "governor_agent")
            actions_taken.append("Adjusted risk parameters to conservative")
        elif 'aggressive' in message_lower:
            new_risk_params = {
                "max_position_size": 0.05,
                "max_daily_loss": 0.10,
                "correlation_threshold": 0.8,
                "volatility_threshold": 0.4
            }
            await adjust_risk_parameters(new_risk_params, "governor_agent")
            actions_taken.append("Adjusted risk parameters to aggressive")
    
    # Emergency stops
    if any(word in message_lower for word in ['stop', 'emergency', 'halt']) and 'trading' in message_lower:
        await emergency_stop("Emergency stop requested via conversation", "governor_agent")
        actions_taken.append("Emergency stop initiated")
    
    # Strategy changes
    if 'strategy' in message_lower and 'change' in message_lower:
        new_strategy = "conversational_strategy_update"
        strategy_params = {"source": "conversation", "reason": message}
        await update_strategy(new_strategy, strategy_params, "governor_agent")
        actions_taken.append("Updated trading strategy")
    
    return actions_taken

def get_conversation_fallback_response(message: str, context: SystemContext) -> str:
    """Provide fallback responses when AI is unavailable"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['status', 'how', 'what', 'doing']):
        return f"The system is running in {context.system_mode} mode with strategy '{context.current_strategy}'. We have {len(context.active_directives)} active directives and are focused on: {', '.join(context.research_priorities)}."
    
    if any(word in message_lower for word in ['trade', 'trades', 'performance']):
        return "I can help you with trade information. The system is configured for paper trading. Would you like to see recent performance or adjust trading parameters?"
    
    if 'risk' in message_lower:
        return f"Current risk parameters: max position size {context.risk_parameters.get('max_position_size', 'unknown')}, max daily loss {context.risk_parameters.get('max_daily_loss', 'unknown')}. Would you like me to adjust these?"
    
    if 'mission' in message_lower:
        return f"Our mission is: {context.mission}. This drives all our research and trading decisions."
    
    return "I can help you with system status, trade performance, risk management, research insights, and system changes. What would you like to know or adjust?"

# ============================================================================
# DASHBOARD ENDPOINTS (Performance & Analytics)
# ============================================================================

@app.get("/api/dashboard/performance")
async def get_performance():
    """Get performance metrics"""
    try:
        return {
            "status": "success",
            "performance": performance_tracker.get_performance_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/trades")
async def get_trades(limit: int = 50):
    """Get recent trades"""
    try:
        return {
            "status": "success",
            "trades": pnl_tracker.get_recent_trades(limit)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/positions")
async def get_positions():
    """Get current positions"""
    try:
        return {
            "status": "success",
            "positions": pnl_tracker.get_positions()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBSOCKET ENDPOINTS (Real-time Streaming)
# ============================================================================

@app.websocket("/ws/governor")
async def websocket_governor(websocket: WebSocket):
    """WebSocket endpoint for governor control panel"""
    await manager.connect(websocket, "governor")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard updates"""
    await manager.connect(websocket, "dashboard")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """Unified WebSocket endpoint for all real-time data"""
    await manager.connect(websocket, "general")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============================================================================
# AUTONOMOUS SYSTEM CONTROL
# ============================================================================

@app.post("/api/autonomous/start")
async def start_autonomous():
    """Start the autonomous trading system"""
    try:
        await start_autonomous_system()
        return {"status": "success", "message": "Autonomous system started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/autonomous/stop")
async def stop_autonomous():
    """Stop the autonomous trading system"""
    global autonomous_task
    try:
        if autonomous_task and not autonomous_task.done():
            autonomous_task.cancel()
            autonomous_task = None
        return {"status": "success", "message": "Autonomous system stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/autonomous/status")
async def get_autonomous_status():
    """Get autonomous system status"""
    global autonomous_task
    try:
        if autonomous_task is None:
            status = "not_started"
        elif autonomous_task.done():
            status = "completed"
        elif autonomous_task.cancelled():
            status = "cancelled"
        else:
            status = "running"
        
        return {"status": "success", "autonomous_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 