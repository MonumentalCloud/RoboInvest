import os
import json
from typing import Any, Dict
from pathlib import Path

CONTEXT_DIR = Path("context")
CONTEXT_DIR.mkdir(exist_ok=True)

SHARED_CONTEXT_FILE = CONTEXT_DIR / "shared.json"

def get_context(agent_name: str) -> Dict[str, Any]:
    """Retrieve the context for a specific agent."""
    file_path = CONTEXT_DIR / f"{agent_name}.json"
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def set_context(agent_name: str, data: Dict[str, Any]) -> None:
    """Set the context for a specific agent."""
    file_path = CONTEXT_DIR / f"{agent_name}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def append_context(agent_name: str, key: str, value: Any) -> None:
    """Append a value to a list in the agent's context."""
    ctx = get_context(agent_name)
    if key not in ctx or not isinstance(ctx[key], list):
        ctx[key] = []
    ctx[key].append(value)
    set_context(agent_name, ctx)

def get_shared_context() -> Dict[str, Any]:
    """Retrieve the shared context."""
    if not SHARED_CONTEXT_FILE.exists():
        return {}
    with open(SHARED_CONTEXT_FILE, "r") as f:
        return json.load(f)

def set_shared_context(data: Dict[str, Any]) -> None:
    """Set the shared context."""
    with open(SHARED_CONTEXT_FILE, "w") as f:
        json.dump(data, f, indent=2) 