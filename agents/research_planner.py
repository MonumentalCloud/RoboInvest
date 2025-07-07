from __future__ import annotations

"""ResearchPlannerAgent: given an event and memory, decide next tasks.

A *task* is a dict with at least keys:
    - type: str  (e.g., "fetch_10k", "backtest", "news_dive", "trade_signal")
    - payload: arbitrary dict specific to the type

For a minimal prototype we only support two task types:
    1. news_dive – deeper sentiment analysis on a symbol
    2. trade_signal – direct long/short suggestion from strategy LLM

The planner uses OpenAIManager for reasoning; for cost control we fall back to a
simple heuristic if the manager is unavailable.
"""

from typing import Any, Dict, List

from core.openai_manager import openai_manager
from agents.rag_playbook import rag_agent
from utils.logger import logger  # type: ignore


class ResearchPlannerAgent:
    """LLM-based planner that turns events into research tasks."""

    def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Planner received event {event.get('type')}")

        # Retrieve some memories for context
        memories = rag_agent.retrieve({"symbol": event.get("symbol"), "sentiment": "any"})

        prompt = (
            "You are a hedge-fund research director. Based on the incoming event, "
            "propose the single most valuable next action. Reply as JSON with keys "
            "type and payload."
        )
        user_msg = f"Event: {event}\nPast insights: {memories}"

        try:
            resp = openai_manager.chat_completion([
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_msg},
            ])
            # Expecting e.g. {"type":"trade_signal","payload":{"symbol":"MSFT","action":"BUY","confidence":0.82}}
            task = resp  # already parsed by OpenAIManager
            if not isinstance(task, dict) or "type" not in task:
                raise ValueError("invalid planner output")
        except Exception as exc:  # fallback heuristic
            logger.warning(f"Planner fallback, error: {exc}")
            task: Dict[str, Any] = {
                "type": "news_dive",
                "payload": {"headline": event.get("headline", ""), "symbol": event.get("symbol")},
            }
        return task 