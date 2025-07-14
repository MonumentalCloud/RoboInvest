from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, Any, Callable, List, Optional

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Agent Registry ---
class Agent:
    def __init__(self, name: str, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]], description: str = ""):
        self.name = name
        self.handler = handler
        self.description = description

# Example agent handlers (to be replaced with real logic)
def trading_agent_handler(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder: handle trading-related requests
    return {"type": "markdown", "content": "Trading agent received: " + message}

def research_agent_handler(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder: handle research-related requests
    return {"type": "markdown", "content": "Research agent received: " + message}

def self_editing_agent_handler(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder: handle self-editing/code change requests
    return {"type": "markdown", "content": "Self-editing agent received: " + message}

# Agent registry
def get_agent_registry() -> List[Agent]:
    return [
        Agent("trading", trading_agent_handler, "Handles trading and portfolio management"),
        Agent("research", research_agent_handler, "Handles research and data analysis"),
        Agent("self_editing", self_editing_agent_handler, "Handles codebase changes and self-improvement"),
    ]

# --- Intent Detection ---
def detect_intent(message: str) -> str:
    """Very basic intent detection (replace with LLM or more advanced logic)"""
    msg = message.lower()
    if any(word in msg for word in ["trade", "order", "position", "portfolio"]):
        return "trading"
    if any(word in msg for word in ["research", "alpha", "insight", "analysis"]):
        return "research"
    if any(word in msg for word in ["edit", "change code", "self-edit", "refactor", "add endpoint"]):
        return "self_editing"
    return "governor"  # fallback to governor/meta-agent

# --- Main Conversational Endpoint ---
@router.post("/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Unified conversational endpoint for all agent-based requests"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Context can be expanded as needed
        context = {}

        # Detect intent and select agent
        intent = detect_intent(message)
        agent_registry = get_agent_registry()
        agent = next((a for a in agent_registry if a.name == intent), None)

        if agent:
            response = agent.handler(message, context)
        else:
            # Governor fallback: answer as meta-agent
            response = {
                "type": "markdown",
                "content": f"Governor received: {message}\n\n(You can ask about trading, research, or request code changes!)"
            }

        # Rich response formatting
        return {
            "status": "success",
            "response": response,
            "metadata": {
                "agent": agent.name if agent else "governor",
                "intent": intent
            }
        }
    except Exception as e:
        logger.error(f"Error in governor conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))