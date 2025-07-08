from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time
from datetime import datetime
import random
import asyncio

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
    from core.openrouter_manager import openrouter_manager
except ImportError:
    openrouter_manager = None

# Embedded simple AI thinking service
class EmbeddedAIThinkingService:
    def __init__(self):
        self.is_running = False
        self.current_thoughts = []
        self.max_thoughts = 10
        
    async def start_thinking(self):
        if self.is_running:
            return
        self.is_running = True
        self._add_thought("OpenRouter AI systems online - live thinking activated")
        # Start background thinking task
        asyncio.create_task(self._thinking_loop())
        
    def stop_thinking(self):
        self.is_running = False
        
    async def _thinking_loop(self):
        while self.is_running:
            try:
                thought = await self._generate_thought()
                if thought:
                    self._add_thought(thought)
                await asyncio.sleep(6)  # New thought every 6 seconds
            except Exception as e:
                print(f"AI thinking error: {e}")
                await asyncio.sleep(6)
                
    async def _generate_thought(self):
        try:
            if openrouter_manager and openrouter_manager.enabled and hasattr(openrouter_manager, 'generate_thinking_thought'):
                # Use OpenRouter for real AI thoughts
                import json
                context = {"time": datetime.now().isoformat(), "market": "active"}
                loop = asyncio.get_event_loop()
                thought = await loop.run_in_executor(
                    None,
                    lambda: openrouter_manager.generate_thinking_thought(context)
                )
                return f"AI: {thought}" if thought else self._fallback_thought()
            else:
                return self._fallback_thought()
        except Exception as e:
            return self._fallback_thought()
            
    def _fallback_thought(self):
        thoughts = [
            "Analyzing market microstructure patterns for alpha signals...",
            "Monitoring institutional flow patterns across sectors...", 
            "Detecting unusual options activity in mega-cap tech...",
            "Scanning earnings revision trends for beat candidates...",
            "Evaluating cross-asset correlation breakdown signals...",
            "Processing sentiment data for contrarian opportunities...",
            "Analyzing technical breakout setups in growth names...",
            "Monitoring volatility term structure for timing signals..."
        ]
        return random.choice(thoughts)
        
    def _add_thought(self, thought):
        new_thought = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        }
        self.current_thoughts.insert(0, new_thought)
        if len(self.current_thoughts) > self.max_thoughts:
            self.current_thoughts = self.current_thoughts[:self.max_thoughts]
            
    def get_current_thoughts(self):
        return self.current_thoughts.copy()
        
    def get_current_alpha_opportunities(self):
        return []
        
    def get_status(self):
        return {
            "is_running": self.is_running,
            "thought_count": len(self.current_thoughts),
            "openrouter_enabled": openrouter_manager.enabled if openrouter_manager else False,
            "service_type": "embedded",
            "last_thought_time": self.current_thoughts[0]["timestamp"] if self.current_thoughts else None
        }

ai_thinking_service = EmbeddedAIThinkingService()

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

# AI thinking service will be started on demand via /api/ai-thoughts/start endpoint

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
async def start_ai_thoughts():
    """Start the AI thinking service."""
    if ai_thinking_service:
        await ai_thinking_service.start_thinking()
        return {"status": "started", "message": "AI thinking service is now running"}
    else:
        return {"status": "error", "message": "AI thinking service not available"}


@app.post("/api/ai-thoughts/stop")
def stop_ai_thoughts():
    """Stop the AI thinking service."""
    if ai_thinking_service:
        ai_thinking_service.stop_thinking()
        return {"status": "stopped", "message": "AI thinking service stopped"}
    else:
        return {"status": "error", "message": "AI thinking service not available"}


@app.get("/api/ai-thoughts/status")
def get_ai_thoughts_status():
    """Get AI thinking service status."""
    if ai_thinking_service:
        return ai_thinking_service.get_status()
    else:
        return {"is_running": False, "error": "AI thinking service not available"}


@app.get("/api/ai-thoughts")
def get_ai_thoughts():
    """Get current AI thinking process and status."""
    if ai_thinking_service:
        thoughts = ai_thinking_service.get_current_thoughts()
        status = ai_thinking_service.get_status()
        return {
            "thoughts": thoughts,
            "status": status
        }
    else:
        # Fallback for when service is not available
        return {
            "thoughts": [{"time": datetime.now().strftime("%H:%M:%S"), "thought": "AI service offline - using fallback analysis..."}],
            "status": {"is_running": False, "error": "AI thinking service not available"}
        }


@app.get("/api/ai-alpha-opportunities")
def get_ai_alpha_opportunities():
    """Get current alpha opportunities discovered by AI."""
    if ai_thinking_service:
        return ai_thinking_service.get_current_alpha_opportunities()
    else:
        return []


@app.get("/api/openrouter/usage")
def get_openrouter_usage():
    """Get OpenRouter usage statistics."""
    if openrouter_manager and openrouter_manager.enabled:
        return openrouter_manager.usage()
    else:
        return {"error": "OpenRouter not available", "enabled": False}


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "RoboInvest API is running!", "timestamp": datetime.now().isoformat()} 