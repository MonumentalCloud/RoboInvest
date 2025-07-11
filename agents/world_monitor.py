from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List

# Third-party imports – add type: ignore to silence linter if the packages are not installed yet
import feedparser  # type: ignore

from core.config import config
from utils.logger import logger  # type: ignore
from core.finnhub_client import finnhub_client
from tools.web_intelligence_agent import web_intelligence_agent
from core.openai_manager import openai_manager

class WorldMonitorAgent:
    """Collects broad market data, news, forums, and web sentiment using LLMs and browser automation."""

    def __init__(self) -> None:
        self.symbols: List[str] = config.symbols_to_watch
        # Configurable, broad list of sources (news, forums, blogs, etc.)
        self.web_sources: List[str] = getattr(config, 'web_sources', [
            # News
            "https://www.cnbc.com/world/?region=world",
            "https://www.bloomberg.com/markets",
            "https://finance.yahoo.com/",
            # Forums
            "https://www.reddit.com/r/stocks/",
            "https://www.reddit.com/r/wallstreetbets/",
            "https://stocktwits.com/",
            # Blogs/Niche
            "https://seekingalpha.com/",
            "https://www.tradingview.com/ideas/",
        ])
        self.news_feeds: List[str] = getattr(config, 'news_sources', [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
            "https://www.marketwatch.com/rss/topstories",
        ])

    async def __call__(self) -> Dict[str, Any]:  # LangGraph node entry-point
        return await self.observe()

    async def observe(self) -> Dict[str, Any]:
        """Fetch price data, news, and web intelligence from a broad set of sources."""
        # In parallel gather market, news, and web intelligence
        market_task = asyncio.create_task(self._get_market_data())
        news_task = asyncio.create_task(self._get_news_headlines())
        web_task = asyncio.create_task(self._get_web_opportunities())

        market = await market_task
        news = await news_task
        web_opps = await web_task

        # LLM-based extraction of tickers/opportunities from all sources
        all_text = "\n".join(news + web_opps)
        extracted = await self._extract_opportunities_with_llm(all_text)

        observation = {
            "timestamp": datetime.utcnow().isoformat(),
            "market": market,
            "news": news,
            "web_opportunities": web_opps,
            "extracted_opportunities": extracted,
            "sentiment": self._simple_sentiment(news + web_opps),
        }
        logger.info(f"WorldMonitor | Fetched observation – {len(market)} symbols, {len(news)} headlines, {len(web_opps)} web opps, {len(extracted)} extracted")
        # TODO: Pipe extracted opportunities into central queue/db for research pipeline
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

    async def _get_web_opportunities(self) -> List[str]:
        """Scrape and summarize opportunities from a broad set of web sources."""
        results: List[str] = []
        for url in self.web_sources:
            try:
                # Use web_intelligence_agent to crawl and summarize
                result = await web_intelligence_agent.gather_intelligence(query=url, tickers=[], max_pages=3)
                # Collect page titles and insights
                if hasattr(result, 'insights') and result.insights:
                    results.extend(result.insights)
                if hasattr(result, 'pages') and result.pages:
                    results.extend([p.title for p in result.pages if p.title])
            except Exception as exc:
                logger.warning(f"WorldMonitor | web source error {url}: {exc}")
        return results

    async def _extract_opportunities_with_llm(self, text: str) -> List[str]:
        """Use LLM to extract tickers and opportunity signals from text."""
        prompt = (
            """
            Extract a list of unique stock tickers and brief opportunity descriptions from the following text.\n
            Return as a JSON list of objects with 'ticker' and 'opportunity' fields.\n
            Text:\n""" + text[:8000] +  # Truncate for token limit
            """
            """
        )
        try:
            messages = [
                {"role": "system", "content": "You are a financial research assistant."},
                {"role": "user", "content": prompt}
            ]
            response = openai_manager.chat_completion(messages)
            import json
            content = response["content"] if isinstance(response, dict) else response
            data = json.loads(content)
            if isinstance(data, list):
                return [f"{item.get('ticker')}: {item.get('opportunity')}" for item in data if 'ticker' in item]
        except Exception as exc:
            logger.warning(f"WorldMonitor | LLM extraction error: {exc}")
        return []

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