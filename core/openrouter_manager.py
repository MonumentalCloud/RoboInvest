from __future__ import annotations

from typing import Any, Dict, List, Union
from datetime import datetime
import json
import requests

import openai  # type: ignore

from core.config import config
from utils.logger import logger  # type: ignore


# OpenRouter model costs (approximate, per 1K tokens)
OPENROUTER_MODEL_COST: Dict[str, float] = {
    "meta-llama/llama-3.2-3b-instruct:free": 0.0,  # Free model
    "meta-llama/llama-3.2-1b-instruct:free": 0.0,  # Free model
    "anthropic/claude-3-haiku": 0.0015,
    "anthropic/claude-3-sonnet": 0.015,
    "openai/gpt-4o-mini": 0.005,
    "openai/gpt-4o": 0.01,
}


class _OpenRouterUsageTracker:
    """Tracks daily token usage and cost for OpenRouter."""

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
        cost_per_1k = OPENROUTER_MODEL_COST.get(model, 0.001)  # default fallback
        self.tokens += tokens
        self.cost += (tokens / 1000) * cost_per_1k

    def summary(self) -> Dict[str, Any]:
        return {"date": str(self.date), "tokens": self.tokens, "cost_usd": round(self.cost, 4)}


_openrouter_usage_tracker = _OpenRouterUsageTracker()


class OpenRouterManager:
    """OpenRouter API wrapper for AI thinking processes."""

    def __init__(self) -> None:
        if not config.openrouter_api_key:
            logger.warning("OpenRouterManager | API key not set – OpenRouter disabled")
            self.enabled = False
        else:
            self.enabled = True

        self.model = config.openrouter_model
        self.base_url = config.openrouter_base_url
        self.daily_budget = config.openrouter_daily_budget_usd
        self.api_key = config.openrouter_api_key

        # Create OpenAI client configured for OpenRouter
        if self.enabled:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

    def chat_completion(self, messages: List[Dict[str, Any]], temperature: float = 0.7) -> Dict[str, Any]:
        """Generate chat completion using OpenRouter API."""
        if not self.enabled:
            raise RuntimeError("OpenRouter API key missing")

        # Check budget
        if self._over_budget():
            logger.warning("OpenRouter | daily budget exceeded")
            raise RuntimeError("OpenRouter daily budget exceeded")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=150,  # Limit tokens for thinking process
            )

            usage = response.usage
            total_tokens = usage.total_tokens if usage else 0
            _openrouter_usage_tracker.add(self.model, total_tokens)
            
            logger.info(f"OpenRouter | model={self.model} tokens={total_tokens} cost_today=${_openrouter_usage_tracker.cost:.4f}")

            return {
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": _openrouter_usage_tracker.summary(),
            }

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    def _over_budget(self) -> bool:
        """Check if daily budget is exceeded."""
        summary = _openrouter_usage_tracker.summary()
        return summary["cost_usd"] >= self.daily_budget

    def usage(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return _openrouter_usage_tracker.summary()

    def generate_thinking_thought(self, market_context: Dict[str, Any]) -> str:
        """Generate a single AI thinking thought based on market context."""
        if not self.enabled:
            return "OpenRouter not configured - using fallback thinking"

        try:
            # Create a focused prompt for generating realistic AI thinking
            prompt = f"""You are an autonomous AI trading system analyzing markets in real-time. 
            
            Current market context: {json.dumps(market_context, indent=2)}
            
            Generate a single, realistic thought that an AI trading system would have right now. 
            This should be specific, actionable, and focused on alpha discovery or risk management.
            
            Examples of good thoughts:
            - "Detecting unusual options flow in QQQ - investigating potential earnings plays"
            - "Cross-asset correlation breakdown suggests defensive positioning"
            - "Semiconductor sector showing relative strength vs SPY (+1.2% divergence)"
            
            Generate ONE specific thought (max 100 characters):"""

            messages = [
                {"role": "system", "content": "You are an expert AI trading analyst generating real-time thoughts."},
                {"role": "user", "content": prompt}
            ]

            response = self.chat_completion(messages, temperature=0.8)
            thought = response.get("content", "").strip()
            
            # Clean up and truncate if needed
            if thought.startswith('"') and thought.endswith('"'):
                thought = thought[1:-1]
            
            return thought[:120] if len(thought) > 120 else thought

        except Exception as e:
            logger.error(f"OpenRouter thinking generation error: {e}")
            return "Analyzing market microstructure for anomalies..."


# Singleton
openrouter_manager = OpenRouterManager() 