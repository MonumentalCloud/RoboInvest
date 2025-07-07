from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from core.performance_tracker import performance_tracker
from core.openai_manager import openai_manager
from agents.rag_playbook import rag_agent
from core.alpaca_client import alpaca_client

app = FastAPI(title="RoboInvest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/budget")
def get_budget():
    """Return current OpenAI usage + budget."""
    return openai_manager.usage() | {"daily_budget": openai_manager.daily_budget}


@app.patch("/api/config")
def patch_budget(budget: Optional[float] = None):
    if budget is not None:
        openai_manager.set_budget(budget)
    return {"daily_budget": openai_manager.daily_budget}


@app.get("/api/performance")
def get_perf():
    return performance_tracker.rolling_stats()


@app.get("/api/trades")
def get_trades(limit: int = 100):
    return performance_tracker.trades[-limit:]


@app.get("/api/positions")
def get_positions():
    if not alpaca_client.is_ready():
        return []
    return [p._raw for p in alpaca_client._client.list_positions()]  # type: ignore


@app.get("/api/lessons")
def get_lessons():
    res = rag_agent.retrieve({"sentiment": "any"})
    return res.get("similar_trades", []) 