from __future__ import annotations

from typing import Any, Dict
from datetime import datetime

from core.alpaca_client import alpaca_client
from utils.logger import logger  # type: ignore
from core.performance_tracker import performance_tracker


class TradeExecutorAgent:
    """Executes BUY/SELL actions via Alpaca paper account."""

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

        order = alpaca_client.submit_order(symbol=symbol, qty=self.DEFAULT_QTY, side=action.lower())
        decision["executed"] = True if order else False
        decision["alpaca_order"] = order

        # Log to performance tracker (pnl placeholder 0)
        performance_tracker.log_trade({
            "symbol": symbol,
            "action": action,
            "qty": self.DEFAULT_QTY,
            "executed": bool(order),
            "pnl": 0,
            "confidence": decision.get("confidence", 0),
            "timestamp": decision.get("timestamp") or datetime.utcnow().isoformat(),
        })

        return decision 