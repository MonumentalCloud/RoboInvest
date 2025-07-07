from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timedelta
import json
import pathlib

from core.config import config
from utils.logger import logger  # type: ignore

FILE = pathlib.Path("performance.jsonl")


class PerformanceTracker:
    """Tracks trades and determines if OpenAI budget should change."""

    LOOKBACK = 10  # trades

    def __init__(self) -> None:
        self.trades: List[Dict[str, Any]] = []
        if FILE.exists():
            with FILE.open() as f:
                self.trades = [json.loads(line) for line in f if line.strip()]

    # -----------------------------------------------------
    def log_trade(self, trade: Dict[str, Any]) -> None:
        self.trades.append(trade)
        with FILE.open("a") as f:
            f.write(json.dumps(trade) + "\n")

    # -----------------------------------------------------
    def rolling_stats(self) -> Dict[str, Any]:
        recent = self.trades[-self.LOOKBACK :]
        wins = [t for t in recent if t.get("pnl", 0) > 0]
        losses = [t for t in recent if t.get("pnl", 0) < 0]
        avg_conf = sum(t.get("confidence", 0) for t in recent) / max(len(recent), 1)
        total_pnl = sum(t.get("pnl", 0) for t in recent)
        return {
            "trades": len(recent),
            "wins": len(wins),
            "losses": len(losses),
            "avg_confidence": avg_conf,
            "total_pnl": total_pnl,
        }

    # -----------------------------------------------------
    def should_adjust_budget(self, current_budget: float) -> float | None:
        stats = self.rolling_stats()
        if stats["trades"] < self.LOOKBACK:
            return None  # not enough data

        # Calculate drawdown simple
        total_pnl = stats["total_pnl"]
        if total_pnl < -config.openai_drawdown_cutoff * 100:
            # big loss: cut budget in half
            return current_budget * 0.5

        if stats["wins"] / max(stats["trades"], 1) >= 0.6 and stats["avg_confidence"] >= 0.6 and total_pnl > 0:
            gain = total_pnl * config.openai_gain_factor / 100  # convert to dollars roughly
            step = min(gain, config.openai_budget_step_max)
            return current_budget + step
        return None


performance_tracker = PerformanceTracker() 