from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, Any, List, Optional
import json

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LLM-Based Agent System ---
class LLMAgent:
    def __init__(self, name: str, description: str, capabilities: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities

# Agent registry with LLM-based handlers
def get_agent_registry() -> List[LLMAgent]:
    return [
        LLMAgent(
            "trading", 
            "Handles trading operations, portfolio management, and market analysis",
            ["execute trades", "analyze positions", "risk management", "performance tracking"]
        ),
        LLMAgent(
            "research", 
            "Conducts market research, alpha discovery, and sentiment analysis",
            ["market research", "alpha discovery", "sentiment analysis", "data insights"]
        ),
        LLMAgent(
            "self_editing", 
            "Modifies the codebase, adds features, and improves the system",
            ["code changes", "feature addition", "system improvement", "bug fixes"]
        ),
        LLMAgent(
            "governor", 
            "Meta-agent that coordinates other agents and provides system oversight",
            ["agent coordination", "system status", "mission control", "strategy oversight"]
        )
    ]

def get_llm_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Get response from OpenAI LLM"""
    try:
        from core.openai_manager import openai_manager
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = openai_manager.chat_completion(messages=messages, temperature=0.7)
        return response.get("content", "I'm sorry, I couldn't process that request.")
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        return f"I encountered an error: {str(e)}"

def llm_intent_detection(message: str) -> Dict[str, Any]:
    """Use LLM to detect intent and route to appropriate agent"""
    system_prompt = """You are an intelligent intent detection system for a trading platform. 
    Analyze the user's message and determine:
    1. Which agent should handle this request (trading, research, self_editing, governor)
    2. The specific action needed
    3. Any additional context or parameters
    
    Available agents:
    - trading: trade execution, portfolio management, risk analysis
    - research: market research, alpha discovery, data analysis
    - self_editing: code changes, feature additions, system improvements
    - governor: system status, coordination, meta-level decisions
    
    Respond with JSON: {"agent": "agent_name", "action": "description", "context": "additional_info"}
    """
    
    prompt = f"User message: {message}\n\nAnalyze and respond with JSON:"
    
    try:
        response = get_llm_response(prompt, system_prompt)
        # Try to parse JSON response
        if response.strip().startswith('{'):
            return json.loads(response)
        else:
            # Fallback if LLM doesn't return JSON
            return {"agent": "governor", "action": "general inquiry", "context": message}
    except Exception as e:
        logger.error(f"Error in LLM intent detection: {e}")
        return {"agent": "governor", "action": "error handling", "context": str(e)}

def trading_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based trading agent"""
    system_prompt = """You are a sophisticated trading agent for an autonomous trading system.
    You can:
    - Analyze trading opportunities
    - Execute trades (paper trading only)
    - Monitor portfolio performance
    - Provide risk analysis
    - Generate trading insights
    
    Always be professional and provide actionable insights. Format responses as markdown when appropriate.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "trading",
        "actions_taken": []
    }

def research_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based research agent"""
    system_prompt = """You are a market research and alpha discovery agent.
    You can:
    - Analyze market trends and patterns
    - Identify alpha opportunities
    - Conduct sentiment analysis
    - Generate research insights
    - Provide data-driven recommendations
    
    Use markdown formatting for tables, lists, and structured information.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "research",
        "actions_taken": []
    }

def self_editing_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based self-editing agent"""
    system_prompt = """You are a self-editing agent that can modify the codebase.
    You can:
    - Add new features and endpoints
    - Modify existing code
    - Improve system functionality
    - Fix bugs and issues
    - Refactor code for better performance
    
    Always explain what changes you're making and why. Provide code examples when relevant.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "self_editing",
        "actions_taken": []
    }

def governor_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based governor/meta-agent"""
    system_prompt = """You are the Governor Agent, the central coordinator of an autonomous trading system.
    You oversee:
    - System status and health
    - Agent coordination
    - Mission and strategy alignment
    - Performance monitoring
    - Risk management
    
    You can coordinate with other agents and provide high-level insights and decisions.
    Be conversational, professional, and helpful.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "governor",
        "actions_taken": []
    }

# Agent handler mapping
AGENT_HANDLERS = {
    "trading": trading_agent_llm,
    "research": research_agent_llm,
    "self_editing": self_editing_agent_llm,
    "governor": governor_agent_llm
}

# --- Main Conversational Endpoint ---
@router.post("/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Unified conversational endpoint for all LLM-based agent requests"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Use LLM for intent detection
        intent_result = llm_intent_detection(message)
        agent_name = intent_result.get("agent", "governor")
        action = intent_result.get("action", "general inquiry")
        
        # Get the appropriate agent handler
        agent_handler = AGENT_HANDLERS.get(agent_name, governor_agent_llm)
        
        # Create context with intent information
        context = {
            "intent": intent_result,
            "user_message": message,
            "timestamp": "2025-07-14T13:36:11.888896"
        }
        
        # Get LLM response from the selected agent
        response = agent_handler(message, context)
        
        # Add metadata about the routing decision
        response["metadata"] = {
            "agent": agent_name,
            "intent": intent_result,
            "llm_based": True
        }
        
        return {
            "status": "success",
            "response": response,
            "metadata": {
                "agent": agent_name,
                "intent": intent_result,
                "llm_based": True
            }
        }
    except Exception as e:
        logger.error(f"Error in governor conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))