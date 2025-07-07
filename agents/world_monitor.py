from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List

# Third-party imports – add type: ignore to silence linter if the packages are not installed yet
import feedparser  # type: ignore

from core.config import config
from utils.logger import logger  # type: ignore
from core.finnhub_client import finnhub_client


class WorldMonitorAgent:
    """Collects basic market data & headline sentiment."""

    def __init__(self) -> None:
        self.symbols: List[str] = config.symbols_to_watch
        self.news_feeds: List[str] = config.news_sources

    async def __call__(self) -> Dict[str, Any]:  # LangGraph node entry-point
        return await self.observe()

    async def observe(self) -> Dict[str, Any]:
        """Fetch price data for watched symbols and a handful of news headlines."""
        # In parallel gather market & news
        market_task = asyncio.create_task(self._get_market_data())
        news_task = asyncio.create_task(self._get_news_headlines())

        market = await market_task
        news = await news_task

        observation = {
            "timestamp": datetime.utcnow().isoformat(),
            "market": market,
            "news": news,
            "sentiment": self._simple_sentiment(news),
        }
        logger.info(f"WorldMonitor | Fetched observation – {len(market)} symbols, {len(news)} headlines")
        return observation

    async def _get_market_data(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for sym in self.symbols:
            quote = finnhub_client.quote(sym)
            if not quote:
                continue
            price = quote.get("c")  # current price
            prev_close = quote.get("pc", price)
            change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0

            fundamentals = finnhub_client.fundamentals(sym)
            pe = fundamentals.get("peBasicExclExtraTTM") or fundamentals.get("peInclExtraTTM")
            pb = fundamentals.get("pbAnnual")
            undervalued = None
            if pe and pb:
                undervalued = "under" if pe < 15 and pb < 1.5 else "over" if pe > 25 or pb > 3 else "fair"

            data[sym] = {
                "price": price,
                "change_pct": change_pct,
                "pe": pe,
                "pb": pb,
                "valuation": undervalued,
            }
        return data

    async def _get_news_headlines(self) -> List[str]:
        headlines: List[str] = []
        for feed in self.news_feeds:
            try:
                parsed = feedparser.parse(feed)
                for entry in parsed.entries[:5]:
                    headlines.append(entry.title)
            except Exception as exc:
                logger.warning(f"WorldMonitor | news feed error {feed}: {exc}")
        return headlines

    def _simple_sentiment(self, headlines: List[str]) -> str:
        pos_kw = ("rally", "gain", "surge", "up")
        neg_kw = ("drop", "fall", "plunge", "down")
        score = 0
        for h in headlines:
            lower = h.lower()
            if any(k in lower for k in pos_kw):
                score += 1
            if any(k in lower for k in neg_kw):
                score -= 1
        if score > 1:
            return "bullish"
        if score < -1:
            return "bearish"
        return "neutral" 