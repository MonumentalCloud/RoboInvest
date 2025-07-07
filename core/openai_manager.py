from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime
import os
import json
import re
import requests

import openai  # type: ignore

from core.config import config
from utils.logger import logger  # type: ignore


# Initially hard-coded; _refresh_pricing() will attempt to update
MODEL_COST: Dict[str, float] = {
    "gpt-4o-mini": 0.005,
    "gpt-4o": 0.01,
    "gpt-3.5-turbo": 0.0005,
}


class _UsageTracker:
    """Tracks daily token usage and cost in-memory."""

    def __init__(self) -> None:
        self.date = datetime.utcnow().date()
        self.tokens = 0
        self.cost = 0.0

    def add(self, model: str, tokens: int) -> None:
        if self.date != datetime.utcnow().date():
            # reset daily
            self.date = datetime.utcnow().date()
            self.tokens = 0
            self.cost = 0.0
        cost_per_1k = MODEL_COST.get(model, 0.002)  # default fallback
        self.tokens += tokens
        self.cost += (tokens / 1000) * cost_per_1k

    def summary(self) -> Dict[str, Any]:
        return {"date": str(self.date), "tokens": self.tokens, "cost_usd": round(self.cost, 4)}


_usage_tracker = _UsageTracker()


class OpenAIManager:
    """Wrapper that auto-selects model based on cost budget."""

    def __init__(self) -> None:
        if not config.openai_api_key:
            logger.warning("OpenAIManager | API key not set – LLM disabled")
            self.enabled = False
        else:
            openai.api_key = config.openai_api_key
            self.enabled = True

        self.primary_model = config.openai_model
        self.cheaper_model = config.openai_cheaper_model
        self.daily_budget = config.openai_daily_budget_usd
        self.budget_ceiling = config.openai_budget_ceiling

        # Try to refresh pricing from OpenAI website (best-effort)
        try:
            self._refresh_pricing()
        except Exception as exc:
            logger.warning(f"OpenAIManager | pricing refresh failed: {exc}")

    # ------------------------------------------------------------------
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> Dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("OpenAI API key missing")

        # Decide which model to use based on budget
        model_to_use = self._select_model()

        response = openai.chat.completions.create(  # type: ignore[attr-defined]
            model=model_to_use,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        usage = response.usage  # type: ignore[attr-defined]
        total_tokens = usage.total_tokens if usage else 0
        _usage_tracker.add(model_to_use, total_tokens)
        logger.info(f"OpenAI | model={model_to_use} tokens={total_tokens} cost_today=${_usage_tracker.cost:.4f}")

        return {
            "content": response.choices[0].message.content,
            "model": model_to_use,
            "usage": _usage_tracker.summary(),
        }

    # ------------------------------------------------------------------
    def _select_model(self) -> str:
        summary = _usage_tracker.summary()
        if summary["cost_usd"] >= self.daily_budget:
            logger.warning("OpenAI | budget reached – switching to cheaper model")
            return self.cheaper_model
        return self.primary_model

    # ------------------------------------------------------------------
    def _refresh_pricing(self) -> None:
        """Fetch latest per-1K token prices from OpenAI pricing page (best effort)."""
        url = "https://openai.com/pricing"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            raise RuntimeError("pricing page fetch failed")

        text = resp.text.lower()
        # crude regex: model name followed by $X /1k tokens
        pattern = re.compile(r"(gpt-[\w\-.]+).*?\$(\d+\.\d+).*?/\s*1k", re.I | re.S)
        found = pattern.findall(text)
        for name, price in found:
            MODEL_COST[name.strip()] = float(price)
        logger.info(f"OpenAIManager | updated pricing for {len(found)} models")

    # Expose usage summary
    def usage(self) -> Dict[str, Any]:
        return _usage_tracker.summary()

    # ------------------ external update ------------------
    def set_budget(self, new_budget: float) -> None:
        self.daily_budget = min(max(new_budget, 0.0), self.budget_ceiling)
        logger.info(f"OpenAI | daily budget set to ${self.daily_budget:.2f}")


# Singleton
openai_manager = OpenAIManager() 