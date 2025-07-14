from __future__ import annotations

from typing import Any, Dict
from datetime import datetime

from core.alpaca_client import alpaca_client
from core.openai_manager import openai_manager
from utils.logger import logger  # type: ignore
from core.performance_tracker import performance_tracker


class TradeExecutorAgent:
    """AI-powered trade executor that uses LLM reasoning for execution decisions."""

    DEFAULT_QTY = 1  # For MVP, trade 1 share

    def __call__(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        action = decision.get("action", "HOLD").upper()
        symbol = decision.get("symbol") or "SPY"

        if action not in ("BUY", "SELL"):
            logger.info("Executor | No trade to execute (HOLD).")
            decision["executed"] = False
            return decision

        if not alpaca_client.is_ready():
            logger.warning("Executor | Alpaca not configured; skipping execution.")
            decision["executed"] = False
            return decision

        # AI-powered execution analysis
        execution_analysis = self._analyze_execution_decision(decision)
        
        if execution_analysis.get("should_execute", True):
            order = alpaca_client.submit_order(symbol=symbol, qty=self.DEFAULT_QTY, side=action.lower())
            decision["executed"] = True if order else False
            decision["alpaca_order"] = order
            decision["execution_reasoning"] = execution_analysis.get("reasoning", "AI approved execution")
        else:
            decision["executed"] = False
            decision["execution_reasoning"] = execution_analysis.get("reasoning", "AI rejected execution")

        # Log to performance tracker
        performance_tracker.log_trade({
            "symbol": symbol,
            "action": action,
            "qty": self.DEFAULT_QTY,
            "executed": decision["executed"],
            "pnl": 0,
            "confidence": decision.get("confidence", 0),
            "timestamp": decision.get("timestamp") or datetime.utcnow().isoformat(),
            "ai_reasoning": execution_analysis.get("reasoning", "")
        })

        return decision

    def _analyze_execution_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze whether to execute the trade decision."""
        try:
            # Get current market context
            symbol = decision.get("symbol", "SPY")
            current_price = self._get_current_price(symbol)
            
            prompt = f"""You are an AI trade execution analyst. Analyze whether to execute this trade decision:

Decision: {decision}
Current Price: {current_price}

Consider:
1. Market conditions and timing
2. Risk/reward ratio
3. Position sizing appropriateness
4. Market volatility
5. Execution timing

Respond in JSON format:
{{
    "should_execute": true/false,
    "reasoning": "detailed explanation",
    "confidence": 0.0-1.0,
    "suggested_modifications": {{}}
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a trade execution analyst. Be conservative and thorough in your analysis."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)

            try:
                import json
                analysis = json.loads(response["content"] or "{}")
                return analysis
            except Exception as parse_exc:
                logger.warning(f"TradeExecutor | JSON parse error: {parse_exc}")
                return {"should_execute": True, "reasoning": "Fallback: proceeding with execution", "confidence": 0.5}

        except Exception as e:
            logger.warning(f"TradeExecutor | LLM analysis failed: {e}")
            return {"should_execute": True, "reasoning": "LLM unavailable, proceeding with execution", "confidence": 0.3}

    def _get_current_price(self, symbol: str) -> float:
        """Get current price for the symbol."""
        try:
            from tools.data_fetcher import data_fetcher
            quote = data_fetcher.get_real_time_quote(symbol)
            return quote.get('current_price', 0.0) if quote else 0.0
        except Exception as e:
            logger.warning(f"TradeExecutor | Failed to get price for {symbol}: {e}")
            return 0.0 