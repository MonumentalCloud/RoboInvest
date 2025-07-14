"""
Reasoning Endpoints - Support streaming reasoning chains from intelligent agents
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.base_reasoning_agent import ReasoningStep, StepType
from agents.intelligent_governor_agent import IntelligentGovernorAgent
from agents.intelligent_research_agent import IntelligentResearchAgent
from agents.intelligent_conversation_agent import IntelligentConversationAgent
from openai import AsyncOpenAI

router = APIRouter(prefix="/api/reasoning", tags=["reasoning"])

# Global agent instances
governor_agent: Optional[IntelligentGovernorAgent] = None
research_agent: Optional[IntelligentResearchAgent] = None
conversation_agent: Optional[IntelligentConversationAgent] = None

class QueryRequest(BaseModel):
    message: str
    session_id: str = "default"
    stream_reasoning: bool = True
    evaluate_performance: bool = False

class AgentRegistryRequest(BaseModel):
    agent_name: str
    agent_type: str

async def initialize_agents():
    """Initialize the reasoning agents."""
    global governor_agent, research_agent
    
    if governor_agent is None:
        openai_client = AsyncOpenAI()
        governor_agent = IntelligentGovernorAgent(openai_client)
        research_agent = IntelligentResearchAgent(openai_client)
        conversation_agent = IntelligentConversationAgent(openai_client)
        
        # Register agents with governor
        governor_agent.register_agent(research_agent)
        governor_agent.register_agent(conversation_agent)
        
        print("✅ Reasoning agents initialized")

async def stream_reasoning_chain(query: str, session_id: str, **kwargs) -> AsyncGenerator[str, None]:
    """Stream reasoning steps from the governor agent."""
    await initialize_agents()
    
    try:
        async for step in governor_agent.process_query(query, **kwargs):
            # Convert step to JSON and yield as SSE
            step_data = {
                "step_id": step.step_id,
                "step_type": step.step_type.value,
                "content": step.content,
                "timestamp": step.timestamp,
                "agent_name": step.metadata.get("routing_agent", "governor") if step.metadata else "governor",
                "tool_used": step.tool_used,
                "agent_called": step.agent_called,
                "metadata": step.metadata
            }
            
            yield f"data: {json.dumps(step_data)}\n\n"
            
    except Exception as e:
        error_data = {
            "step_type": "error",
            "content": f"Error in reasoning chain: {str(e)}",
            "timestamp": asyncio.get_event_loop().time()
        }
        yield f"data: {json.dumps(error_data)}\n\n"

@router.post("/conversation")
async def reasoning_conversation(request: QueryRequest):
    """Process a query with streaming reasoning chain."""
    if request.stream_reasoning:
        return StreamingResponse(
            stream_reasoning_chain(
                request.message, 
                request.session_id,
                evaluate_performance=request.evaluate_performance
            ),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    else:
        # Non-streaming response (for compatibility)
        await initialize_agents()
        
        reasoning_steps = []
        async for step in governor_agent.process_query(
            request.message, 
            evaluate_performance=request.evaluate_performance
        ):
            reasoning_steps.append(step.to_dict())
        
        # Return the final result
        final_step = reasoning_steps[-1] if reasoning_steps else None
        return {
            "response": final_step["content"] if final_step else "No response generated",
            "reasoning_chain": reasoning_steps,
            "session_id": request.session_id
        }

@router.get("/agents")
async def list_agents():
    """List all available reasoning agents."""
    await initialize_agents()
    
    agents = []
    for name, agent in governor_agent.agent_registry.items():
        agents.append({
            "name": name,
            "description": agent.description,
            "reasoning_chain_length": len(agent.reasoning_chain)
        })
    
    return {
        "agents": agents,
        "total_agents": len(agents)
    }

@router.get("/agent/{agent_name}/reasoning-chain")
async def get_agent_reasoning_chain(agent_name: str):
    """Get the reasoning chain for a specific agent."""
    await initialize_agents()
    
    if agent_name not in governor_agent.agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    agent = governor_agent.agent_registry[agent_name]
    reasoning_chain = await agent.get_reasoning_chain()
    
    return {
        "agent_name": agent_name,
        "reasoning_chain": [step.to_dict() for step in reasoning_chain],
        "chain_length": len(reasoning_chain)
    }

@router.post("/agent/{agent_name}/clear-chain")
async def clear_agent_reasoning_chain(agent_name: str):
    """Clear the reasoning chain for a specific agent."""
    await initialize_agents()
    
    if agent_name not in governor_agent.agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    agent = governor_agent.agent_registry[agent_name]
    await agent.clear_reasoning_chain()
    
    return {
        "message": f"Reasoning chain cleared for agent '{agent_name}'",
        "agent_name": agent_name
    }

@router.get("/system-status")
async def get_system_status():
    """Get comprehensive system status including all agents."""
    await initialize_agents()
    
    status = await governor_agent.use_tool("get_system_status")
    
    # Add reasoning chain information
    for agent_name, agent_info in status["agent_statuses"].items():
        agent = governor_agent.agent_registry[agent_name]
        agent_info["recent_reasoning_steps"] = [
            step.to_dict() for step in agent.reasoning_chain[-5:]  # Last 5 steps
        ]
    
    return status

@router.post("/test-reasoning")
async def test_reasoning():
    """Test the reasoning system with a simple query."""
    test_query = "What is the current research progress?"
    
    reasoning_steps = []
    async for step in governor_agent.process_query(test_query):
        reasoning_steps.append(step.to_dict())
    
    return {
        "test_query": test_query,
        "reasoning_steps": reasoning_steps,
        "total_steps": len(reasoning_steps),
        "final_response": reasoning_steps[-1]["content"] if reasoning_steps else "No response"
    } 