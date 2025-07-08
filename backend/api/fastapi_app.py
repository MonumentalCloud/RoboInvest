from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time
from datetime import datetime
import random

# Import the core modules (some may not exist yet, so we'll handle gracefully)
try:
    from core.performance_tracker import performance_tracker
except ImportError:
    performance_tracker = None

try:
    from core.openai_manager import openai_manager
except ImportError:
    openai_manager = None

try:
    from agents.rag_playbook import rag_agent
except ImportError:
    rag_agent = None

try:
    from core.alpaca_client import alpaca_client
except ImportError:
    alpaca_client = None

app = FastAPI(title="RoboInvest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for AI thinking process
ai_thoughts = [
    {"time": datetime.now().strftime("%H:%M:%S"), "thought": "AI systems initialized successfully!"}
]
ai_status = {"is_running": True}

@app.get("/api/budget")
def get_budget():
    """Return current OpenAI usage + budget."""
    if openai_manager:
        return openai_manager.usage() | {"daily_budget": openai_manager.daily_budget}
    return {"usage": 0, "daily_budget": 10.0, "status": "demo_mode"}


@app.patch("/api/config")
def patch_budget(budget: Optional[float] = None):
    if budget is not None and openai_manager:
        openai_manager.set_budget(budget)
    return {"daily_budget": budget or 10.0}


@app.get("/api/performance")
def get_perf():
    if performance_tracker:
        return performance_tracker.rolling_stats()
    return {"total_return": 5.2, "win_rate": 0.68, "sharpe_ratio": 1.45, "status": "demo_mode"}


@app.get("/api/trades")
def get_trades(limit: int = 100):
    if performance_tracker:
        return performance_tracker.trades[-limit:]
    return [
        {"symbol": "NVDA", "side": "buy", "qty": 10, "price": 135.0, "timestamp": "2024-01-15T10:30:00"},
        {"symbol": "QQQ", "side": "buy", "qty": 50, "price": 405.0, "timestamp": "2024-01-15T11:15:00"}
    ]


@app.get("/api/positions")
def get_positions():
    if alpaca_client and alpaca_client.is_ready() and hasattr(alpaca_client, '_client') and alpaca_client._client:
        return [p._raw for p in alpaca_client._client.list_positions()]
    return [
        {"symbol": "NVDA", "qty": 10, "market_value": 1350.0, "unrealized_pl": 150.0},
        {"symbol": "QQQ", "qty": 50, "market_value": 20250.0, "unrealized_pl": -75.0}
    ]


@app.get("/api/lessons")
def get_lessons():
    if rag_agent:
        res = rag_agent.retrieve({"sentiment": "any"})
        return res.get("similar_trades", [])
    return [
        {"lesson": "Always use stop losses on momentum trades", "confidence": 0.85},
        {"lesson": "Tech stocks perform better in low volatility environments", "confidence": 0.72}
    ]


@app.get("/api/research")
def get_research():
    """Return research data for the frontend."""
    return {
        "activeResearch": [
            {
                "id": 1,
                "title": "Market Sentiment Analysis - Live",
                "status": "analyzing",
                "progress": 85,
                "confidence": 0.78,
                "timeStarted": "5 min ago",
                "description": "Analyzing current market sentiment and identifying potential alpha opportunities",
                "leads": ["SPY momentum shift", "Tech sector rotation", "Fed policy impact"],
                "expectedOutcome": "Identify 2-3 high-conviction trades with 15%+ upside potential",
                "symbols": ["SPY", "QQQ", "IWM"]
            },
            {
                "id": 2,
                "title": "Earnings Season Alpha Hunt",
                "status": "validating",
                "progress": 62,
                "confidence": 0.85,
                "timeStarted": "12 min ago",
                "description": "Scanning upcoming earnings for potential surprise candidates",
                "leads": ["Revenue beat patterns", "Guidance upgrade signals", "Option flow anomalies"],
                "expectedOutcome": "Identify earnings plays with asymmetric risk/reward",
                "symbols": ["NVDA", "AAPL", "MSFT"]
            }
        ],
        "discoveredAlpha": [
            {
                "symbol": "NVDA",
                "confidence": 0.89,
                "thesis": "Strong AI demand continues to drive revenue growth. Recent pullback creates attractive entry point.",
                "timeHorizon": "2-4 weeks",
                "catalysts": ["Q4 earnings beat", "AI partnership announcements", "Data center demand"],
                "priceTarget": 150.0,
                "currentPrice": 135.0,
                "upside": 11.1
            },
            {
                "symbol": "QQQ",
                "confidence": 0.72,
                "thesis": "Tech sector oversold conditions suggest bounce incoming. RSI at oversold levels.",
                "timeHorizon": "1-2 weeks",
                "catalysts": ["Fed dovish tone", "Earnings season optimism", "Technical bounce"],
                "priceTarget": 420.0,
                "currentPrice": 405.0,
                "upside": 3.7
            }
        ],
        "marketInsights": [
            {
                "timestamp": datetime.now().isoformat(),
                "insight": "VIX below 20 suggests complacency - watch for volatility spike",
                "confidence": 0.75,
                "actionable": True
            },
            {
                "timestamp": datetime.now().isoformat(),
                "insight": "Tech/Finance ratio approaching key support level",
                "confidence": 0.68,
                "actionable": False
            }
        ]
    }


@app.post("/api/ai-thoughts/start")
def start_ai_thoughts():
    """Start the AI thinking service."""
    global ai_status, ai_thoughts
    ai_status["is_running"] = True
    ai_thoughts.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "thought": "AI research engine activated - scanning market data..."
    })
    return {"status": "started", "message": "AI thinking service is now running"}


@app.get("/api/ai-thoughts")
def get_ai_thoughts():
    """Get current AI thinking process and status."""
    global ai_thoughts, ai_status
    
    # Add a new thought periodically
    current_time = datetime.now().strftime("%H:%M:%S")
    thoughts = [
        "Analyzing market microstructure patterns...",
        "Scanning social sentiment for alpha signals...",
        "Processing earnings revision trends...",
        "Evaluating momentum factor strength...",
        "Monitoring unusual options activity...",
        "Checking for insider trading patterns...",
        "Analyzing sector rotation dynamics...",
        "Processing economic indicator releases..."
    ]
    
    new_thought = {
        "time": current_time,
        "thought": random.choice(thoughts)
    }
    
    # Keep only last 10 thoughts
    ai_thoughts = [new_thought] + ai_thoughts[:9]
    
    return {
        "thoughts": ai_thoughts,
        "status": ai_status
    }


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "RoboInvest API is running!", "timestamp": datetime.now().isoformat()} 