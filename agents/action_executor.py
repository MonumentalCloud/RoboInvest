from __future__ import annotations

"""ActionExecutorAgent: execute planner tasks.

Currently supports:
    - news_dive  → stores research memory only.
    - trade_signal → forwards to TradeExecutorAgent.

Returns the result dict that downstream nodes can use.
"""
from typing import Any, Dict

from agents.rag_playbook import rag_agent
from agents.trade_executor import TradeExecutorAgent
from utils.logger import logger  # type: ignore

trade_executor = TradeExecutorAgent()


class ActionExecutorAgent:
    """Dispatch planner tasks to concrete actions."""

    def __call__(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        payload = task.get("payload", {})
        logger.info(f"Executing task {task_type}")

        if task_type == "news_dive":
            # For now just store payload as research memory
            rag_agent.store_research(payload)
            return {"status": "stored", "task": task}

        if task_type == "trade_signal":
            res = trade_executor({**payload, "source": "planner"})  # type: ignore[arg-type]
            return {"status": "executed", "trade_result": res}

        logger.warning(f"Unknown task type {task_type}")
        return {"status": "ignored", "task": task} 