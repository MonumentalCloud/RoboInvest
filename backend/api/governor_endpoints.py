"""
Governor Directive System API Endpoints

Provides REST API and WebSocket endpoints for:
1. Issuing directives from the frontend
2. Viewing system context and active directives
3. Real-time directive streaming
4. Directive acknowledgment and completion reporting
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid
from pathlib import Path

from core.governor_directive_system import (
    governor_directive_system, DirectiveType, DirectivePriority, 
    DirectiveStatus, SystemContext, update_mission, update_strategy,
    adjust_risk_parameters, emergency_stop, update_research_priorities
)
from utils.logger import logger
from agents.agent_monitoring_system import agent_monitor
from core.alpaca_client import alpaca_client

router = APIRouter(prefix="/api/governor", tags=["Governor"])

# WebSocket connections for real-time updates
directive_connections: List[WebSocket] = []
context_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        self.context_connections: List[WebSocket] = []
        self.directive_connections: List[WebSocket] = []
        self.thoughts_connections: List[WebSocket] = []
        self.pulse_connections: List[WebSocket] = []

    async def connect_context(self, websocket: WebSocket):
        await websocket.accept()
        self.context_connections.append(websocket)
        # Send initial context
        context = governor_directive_system.get_system_context()
        await websocket.send_text(json.dumps({
            "type": "initial_context",
            "context": context.to_dict()
        }))

    async def connect_directives(self, websocket: WebSocket):
        await websocket.accept()
        self.directive_connections.append(websocket)
        # Send initial directives
        directives = governor_directive_system.get_active_directives()
        await websocket.send_text(json.dumps({
            "type": "initial_directives",
            "directives": [d.to_dict() for d in directives]
        }))

    async def connect_thoughts(self, websocket: WebSocket):
        await websocket.accept()
        self.thoughts_connections.append(websocket)

    async def connect_pulse(self, websocket: WebSocket):
        await websocket.accept()
        self.pulse_connections.append(websocket)
        # Send initial pulse
        pulse = get_system_pulse()
        await websocket.send_text(json.dumps({
            "type": "system_pulse",
            "pulse": pulse
        }))

    def disconnect_context(self, websocket: WebSocket):
        if websocket in self.context_connections:
            self.context_connections.remove(websocket)

    def disconnect_directives(self, websocket: WebSocket):
        if websocket in self.directive_connections:
            self.directive_connections.remove(websocket)

    def disconnect_thoughts(self, websocket: WebSocket):
        if websocket in self.thoughts_connections:
            self.thoughts_connections.remove(websocket)

    def disconnect_pulse(self, websocket: WebSocket):
        if websocket in self.pulse_connections:
            self.pulse_connections.remove(websocket)

    async def broadcast_context_update(self, context: Dict[str, Any]):
        for connection in self.context_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "context_update",
                    "context": context
                }))
            except:
                pass

    async def broadcast_directive_update(self, directive: Dict[str, Any]):
        for connection in self.directive_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "directive_update",
                    "directive": directive
                }))
            except:
                pass

    async def broadcast_agent_thought(self, thought: Dict[str, Any]):
        for connection in self.thoughts_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "agent_thought",
                    "thought": thought
                }))
            except:
                pass

    async def broadcast_system_pulse(self, pulse: Dict[str, Any]):
        for connection in self.pulse_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "system_pulse",
                    "pulse": pulse
                }))
            except:
                pass

manager = ConnectionManager()

def get_system_pulse() -> Dict[str, Any]:
    """Generate system pulse data"""
    # Get real agent count from monitoring system
    try:
        from agents.agent_monitoring_system import agent_monitor
        active_agents = len(agent_monitor.heartbeats) if hasattr(agent_monitor, 'heartbeats') else 0
    except:
        active_agents = 0
    
    # Get real trade count from PnL tracker
    try:
        from core.pnl_tracker import pnl_tracker
        trades_executed = len(pnl_tracker.closed_trades)
    except:
        trades_executed = 0
    
    # Get real research activities from research data
    try:
        research_data_dir = Path("research_data")
        research_files = list(research_data_dir.glob("*_latest.json"))
        research_activities = len(research_files)
    except:
        research_activities = 0
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "active_agents": active_agents,
        "directives_processed": len(governor_directive_system.get_active_directives()),
        "trades_executed": trades_executed,
        "research_activities": research_activities,
        "system_health": "operational"
    }


@router.get("/context")
async def get_system_context():
    """Get current system context"""
    try:
        context = governor_directive_system.get_system_context()
        return {
            "status": "success",
            "context": context.to_dict()
        }
    except Exception as e:
        logger.error(f"Error getting system context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pulse")
async def get_system_pulse_endpoint():
    """Get current system pulse"""
    try:
        pulse = get_system_pulse()
        return {
            "status": "success",
            "pulse": pulse
        }
    except Exception as e:
        logger.error(f"Error getting system pulse: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/directives")
async def get_directives(
    status: Optional[str] = None,
    directive_type: Optional[str] = None,
    limit: int = 50
):
    """Get directives with optional filtering"""
    try:
        if status == "active":
            directives = governor_directive_system.get_active_directives()
        else:
            # Get all directives from database
            directives = list(governor_directive_system.directives.values())
        
        # Filter by type if specified
        if directive_type:
            directives = [d for d in directives if d.directive_type.value == directive_type]
        
        # Sort by timestamp (newest first) and limit
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


@router.get("/directives/{directive_id}")
async def get_directive(directive_id: str):
    """Get a specific directive"""
    try:
        directive = governor_directive_system.get_directive(directive_id)
        if not directive:
            raise HTTPException(status_code=404, detail="Directive not found")
        
        return {
            "status": "success",
            "directive": directive.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting directive {directive_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directives")
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


@router.post("/directives/{directive_id}/acknowledge")
async def acknowledge_directive(directive_id: str, request: Dict[str, Any]):
    """Acknowledge receipt of a directive"""
    try:
        agent_id = request.get("agent_id")
        if not agent_id:
            raise HTTPException(status_code=400, detail="Missing agent_id")
        
        success = governor_directive_system.acknowledge_directive(directive_id, agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Directive not found")
        
        return {
            "status": "success",
            "message": f"Directive {directive_id} acknowledged by {agent_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging directive: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directives/{directive_id}/complete")
async def complete_directive(directive_id: str, request: Dict[str, Any]):
    """Report completion of a directive"""
    try:
        agent_id = request.get("agent_id")
        report = request.get("report", {})
        
        if not agent_id:
            raise HTTPException(status_code=400, detail="Missing agent_id")
        
        success = governor_directive_system.report_directive_completion(directive_id, agent_id, report)
        if not success:
            raise HTTPException(status_code=404, detail="Directive not found")
        
        return {
            "status": "success",
            "message": f"Directive {directive_id} completed by {agent_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing directive: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience endpoints for common directive types
@router.post("/mission/update")
async def update_system_mission(request: Dict[str, Any]):
    """Update the system mission"""
    try:
        new_mission = request.get("mission")
        if not new_mission:
            raise HTTPException(status_code=400, detail="Missing mission")
        
        directive_id = await update_mission(new_mission, request.get("source", "human_governor"))
        
        return {
            "status": "success",
            "directive_id": directive_id,
            "message": f"Mission updated to: {new_mission}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy/update")
async def update_trading_strategy(request: Dict[str, Any]):
    """Update the trading strategy"""
    try:
        strategy = request.get("strategy")
        parameters = request.get("parameters", {})
        
        if not strategy:
            raise HTTPException(status_code=400, detail="Missing strategy")
        
        directive_id = await update_strategy(strategy, parameters, request.get("source", "human_governor"))
        
        return {
            "status": "success",
            "directive_id": directive_id,
            "message": f"Strategy updated to: {strategy}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/adjust")
async def adjust_risk(request: Dict[str, Any]):
    """Adjust risk parameters"""
    try:
        risk_params = request.get("risk_parameters", {})
        if not risk_params:
            raise HTTPException(status_code=400, detail="Missing risk_parameters")
        
        directive_id = await adjust_risk_parameters(risk_params, request.get("source", "human_governor"))
        
        return {
            "status": "success",
            "directive_id": directive_id,
            "message": "Risk parameters adjusted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency/stop")
async def emergency_stop_trading(request: Dict[str, Any]):
    """Emergency stop all trading"""
    try:
        reason = request.get("reason", "Emergency stop initiated")
        
        directive_id = await emergency_stop(reason, request.get("source", "human_governor"))
        
        return {
            "status": "success",
            "directive_id": directive_id,
            "message": f"Emergency stop initiated: {reason}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/priorities")
async def update_research_priorities_endpoint(request: Dict[str, Any]):
    """Update research priorities"""
    try:
        priorities = request.get("priorities", [])
        if not priorities:
            raise HTTPException(status_code=400, detail="Missing priorities")
        
        directive_id = await update_research_priorities(priorities, request.get("source", "human_governor"))
        
        return {
            "status": "success",
            "directive_id": directive_id,
            "message": "Research priorities updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating research priorities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoints for real-time updates
@router.websocket("/ws/directives")
async def websocket_directives(websocket: WebSocket):
    """WebSocket endpoint for real-time directive updates"""
    await websocket.accept()
    directive_connections.append(websocket)
    
    try:
        # Send initial active directives
        active_directives = governor_directive_system.get_active_directives()
        await websocket.send_text(json.dumps({
            "type": "initial_directives",
            "directives": [d.to_dict() for d in active_directives]
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle acknowledgment or completion reports
                if message.get("type") == "acknowledge":
                    governor_directive_system.acknowledge_directive(
                        message["directive_id"], 
                        message["agent_id"]
                    )
                elif message.get("type") == "complete":
                    governor_directive_system.report_directive_completion(
                        message["directive_id"], 
                        message["agent_id"], 
                        message.get("report", {})
                    )
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in directive_connections:
            directive_connections.remove(websocket)


@router.websocket("/ws/context")
async def websocket_context(websocket: WebSocket):
    """WebSocket endpoint for real-time context updates"""
    await manager.connect_context(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_context(websocket)


@router.websocket("/ws/thoughts")
async def websocket_thoughts(websocket: WebSocket):
    """WebSocket endpoint for real-time agent thought updates"""
    await manager.connect_thoughts(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_thoughts(websocket)


@router.websocket("/ws/pulse")
async def websocket_pulse(websocket: WebSocket):
    """WebSocket endpoint for real-time system pulse updates"""
    await manager.connect_pulse(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_pulse(websocket)


# Helper functions for broadcasting updates
async def broadcast_directive_update(directive):
    """Broadcast directive update to all WebSocket connections"""
    message = {
        "type": "directive_update",
        "directive": directive.to_dict()
    }
    
    for connection in directive_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error broadcasting directive update: {e}")
            if connection in directive_connections:
                directive_connections.remove(connection)


async def broadcast_context_update(context):
    """Broadcast context update to all WebSocket connections"""
    message = {
        "type": "context_update",
        "context": context.to_dict()
    }
    
    for connection in context_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error broadcasting context update: {e}")
            if connection in context_connections:
                context_connections.remove(connection)


# Subscribe to directive and context updates
def setup_governor_subscriptions():
    """Setup subscriptions for real-time updates"""
    def sync_broadcast_directive(directive):
        """Synchronous wrapper for directive broadcasting"""
        asyncio.create_task(broadcast_directive_update(directive))
    
    def sync_broadcast_context(context):
        """Synchronous wrapper for context broadcasting"""
        asyncio.create_task(broadcast_context_update(context))
    
    governor_directive_system.subscribe_to_directives(sync_broadcast_directive)
    governor_directive_system.subscribe_to_context(sync_broadcast_context)
    logger.info("👑 Governor directive system subscriptions setup complete") 

# Background task to update system pulse
async def background_simulation():
    """Update system pulse with real data"""
    while True:
        try:
            # Update system pulse with real data
            pulse = get_system_pulse()
            await manager.broadcast_system_pulse(pulse)
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Background simulation error: {e}")
            await asyncio.sleep(5)

# Start background simulation
@router.on_event("startup")
async def startup_event():
    asyncio.create_task(background_simulation()) 

@router.post("/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Handle natural language conversation with the Governor Agent"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get current system context for the AI
        context = governor_directive_system.get_system_context()
        
        # Create a comprehensive prompt for the AI
        prompt = f"""
You are the Governor Agent, an AI administrative assistant for an autonomous trading system. 
You have complete control over the system and can execute any changes the Human Governor requests.

Current System Context:
- Mission: {context.mission}
- Strategy: {context.current_strategy}
- System Mode: {context.system_mode}
- Active Agents: {len(governor_directive_system.get_active_directives())}
- Research Priorities: {', '.join(context.research_priorities)}
- Risk Parameters: {context.risk_parameters}
- Trading Rules: {context.trading_rules}

Human Governor Message: "{message}"

Respond naturally as if in a conversation. You can:
1. Answer questions about system status, agents, trades, performance
2. Execute system changes based on requests
3. Provide insights and recommendations
4. Ask clarifying questions if needed

Always be helpful, professional, and take action when requested. If you need to make system changes, 
explain what you're doing and why.

Response:"""

        # Get AI response using the existing meta agent system
        try:
            from core.openai_manager import openai_manager
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
            
            response = openai_manager.chat_completion(
                messages=messages,
                temperature=0.7
            )
            
            # Parse the response and extract any actions needed
            response_text = response.get("content", "")
            
            # Check if the message contains action requests and execute them
            actions_taken = []
            
            # Mission updates
            if any(word in message.lower() for word in ['mission', 'goal', 'objective']):
                if 'change' in message.lower() or 'update' in message.lower():
                    # Extract new mission from response or use a default
                    new_mission = "Discover the smartest and greatest upside that nobody is looking at"
                    await update_mission(new_mission, "governor_agent")
                    actions_taken.append("Updated system mission")
            
            # Risk adjustments
            if any(word in message.lower() for word in ['risk', 'conservative', 'aggressive', 'safe']):
                if 'conservative' in message.lower():
                    new_risk_params = {
                        "max_position_size": 0.01,  # 1% of portfolio
                        "max_daily_loss": 0.02,     # 2% daily loss limit
                        "correlation_threshold": 0.5,
                        "volatility_threshold": 0.2
                    }
                    await adjust_risk_parameters(new_risk_params, "governor_agent")
                    actions_taken.append("Adjusted risk parameters to conservative")
                elif 'aggressive' in message.lower():
                    new_risk_params = {
                        "max_position_size": 0.05,  # 5% of portfolio
                        "max_daily_loss": 0.10,     # 10% daily loss limit
                        "correlation_threshold": 0.8,
                        "volatility_threshold": 0.4
                    }
                    await adjust_risk_parameters(new_risk_params, "governor_agent")
                    actions_taken.append("Adjusted risk parameters to aggressive")
            
            # Emergency stops
            if any(word in message.lower() for word in ['stop', 'emergency', 'halt', 'pause']):
                if 'trading' in message.lower() or 'all' in message.lower():
                    await emergency_stop("Emergency stop requested via conversation", "governor_agent")
                    actions_taken.append("Emergency stop initiated")
            
            # Strategy changes
            if any(word in message.lower() for word in ['strategy', 'approach', 'method']):
                if 'change' in message.lower() or 'switch' in message.lower():
                    new_strategy = "conversational_strategy_update"
                    strategy_params = {"source": "conversation", "reason": message}
                    await update_strategy(new_strategy, strategy_params, "governor_agent")
                    actions_taken.append("Updated trading strategy")
            
            # Research priorities
            if any(word in message.lower() for word in ['research', 'focus', 'priority']):
                if 'change' in message.lower() or 'update' in message.lower():
                    new_priorities = ["alpha_discovery", "market_monitoring", "sentiment_tracking"]
                    await update_research_priorities(new_priorities, "governor_agent")
                    actions_taken.append("Updated research priorities")
            
            # Add action summary to response if actions were taken
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
            # Fallback to rule-based responses if AI fails
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


def get_conversation_fallback_response(message: str, context: SystemContext) -> str:
    """Provide fallback responses when AI is unavailable"""
    message_lower = message.lower()
    
    # System status queries
    if any(word in message_lower for word in ['status', 'how', 'what', 'doing']):
        return f"I can see the system is currently running in {context.system_mode} mode. The current strategy is '{context.current_strategy}' and we have {len(context.active_directives)} active directives. The system is focused on: {', '.join(context.research_priorities)}."
    
    # Trade queries
    if any(word in message_lower for word in ['trade', 'trades', 'performance', 'profit']):
        return "I can help you with trade information. The system is currently configured for paper trading only. Would you like me to show you recent trade performance or adjust trading parameters?"
    
    # Risk queries
    if any(word in message_lower for word in ['risk', 'safe', 'dangerous']):
        return f"Current risk parameters are: max position size {context.risk_parameters.get('max_position_size', 'unknown')}, max daily loss {context.risk_parameters.get('max_daily_loss', 'unknown')}. Would you like me to adjust these?"
    
    # Mission queries
    if any(word in message_lower for word in ['mission', 'goal', 'objective']):
        return f"Our current mission is: {context.mission}. This drives all our research and trading decisions."
    
    # Default response
    return "I understand your request. I can help you with system status, trade performance, risk management, research insights, and any system changes you need. What would you like to know or adjust?" 

@router.get("/agents")
async def get_all_agents():
    """Get status of all registered agents"""
    try:
        statuses = agent_monitor.get_all_agent_statuses()
        return {"status": "success", "agents": statuses}
    except Exception as e:
        logger.error(f"Error getting agent statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
async def get_system_health():
    """Get overall system health summary"""
    try:
        summary = agent_monitor.get_system_health_summary()
        return {"status": "success", "system_health": summary}
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_positions():
    """Get current Alpaca positions"""
    try:
        account = alpaca_client.get_account()
        positions = account.get('positions', [])
        return {"status": "success", "positions": positions}
    except Exception as e:
        logger.error(f"Error getting Alpaca positions: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 