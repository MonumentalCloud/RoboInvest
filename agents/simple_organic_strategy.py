from __future__ import annotations

from typing import Any, Dict, Optional
import random

# direct openai removed; use manager

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger  # type: ignore


class SimpleOrganicStrategyAgent:
    """Very naive agent that decides to BUY/SELL/HOLD based on sentiment or delegates to OpenAI."""

    def __init__(self) -> None:
        self.use_llm = bool(config.openai_api_key)
        self.temperature = 0.3

    def __call__(self, observation: Dict[str, Any]) -> Dict[str, Any]:  # LangGraph node function
        decision = self._decide(observation)
        logger.info(f"Strategy | decision={decision['action']} confidence={decision['confidence']:.2f}")
        return decision

    def _decide(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        sentiment = obs.get("sentiment", "neutral")
        top_symbol = self._pick_top_mover(obs)

        if self.use_llm:
            return self._llm_decision(obs, top_symbol)
        else:
            # Simple heuristic: bullish sentiment -> buy, bearish -> sell, else hold
            action = "HOLD"
            if sentiment == "bullish":
                action = "BUY"
            elif sentiment == "bearish":
                action = "SELL"
            confidence = random.uniform(0.4, 0.6)
            return {
                "action": action,
                "symbol": top_symbol,
                "confidence": confidence,
                "reasoning": f"Heuristic based on {sentiment} sentiment",
            }

    def _llm_decision(self, obs: Dict[str, Any], symbol: Optional[str]) -> Dict[str, Any]:
        prompt = (
            "You are an organic trading bot. Given the market observation below, "
            "suggest a single action (BUY/SELL/HOLD) with a confidence (0-1) and short reasoning.\n\n"
            f"Observation:\n{obs}\n"
            "Respond in JSON with keys action, confidence, reasoning."
        )
        try:
            result = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ], temperature=self.temperature)
            import json
            try:
                data = json.loads(result["content"] or "{}")
            except Exception as parse_exc:
                logger.warning(f"Strategy | JSON parse error: {parse_exc} content: {result['content']}")
                raise
            data.setdefault("symbol", symbol or "SPY")
            return data
        except Exception as exc:
            logger.warning(f"Strategy | LLM fallback due to error: {exc}")
            return {
                "action": "HOLD",
                "symbol": symbol,
                "confidence": 0.2,
                "reasoning": "LLM error fallback",
            }

    def _pick_top_mover(self, obs: Dict[str, Any]) -> Optional[str]:
        market = obs.get("market", {})
        if not market:
            return None
        return max(market.items(), key=lambda kv: abs(kv[1]["change_pct"]))[0] 