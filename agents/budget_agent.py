from __future__ import annotations

from typing import Any, Dict

from core.openai_manager import openai_manager
from core.performance_tracker import performance_tracker
from utils.logger import logger  # type: ignore


class BudgetAgent:
    """Adjusts OpenAI daily budget based on performance stats."""

    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        current_budget = openai_manager.daily_budget
        suggestion = performance_tracker.should_adjust_budget(current_budget)
        if suggestion is not None and suggestion != current_budget:
            openai_manager.set_budget(suggestion)
            logger.info(f"BudgetAgent | adjusted budget to ${suggestion:.2f}")
        data["budget"] = openai_manager.daily_budget
        return data 