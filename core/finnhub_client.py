from __future__ import annotations

from typing import Any, Dict

import finnhub
from core.config import config
from utils.logger import logger  # type: ignore


class FinnhubClientWrapper:
    """Wrapper around finnhub-python SDK."""

    def __init__(self) -> None:
        if not config.finnhub_api_key:
            logger.error("Finnhub API key missing – market data disabled.")
            self.client = None
        else:
            self.client = finnhub.Client(api_key=config.finnhub_api_key)

    def quote(self, symbol: str) -> Dict[str, Any]:
        if not self.client:
            return {}
        try:
            return self.client.quote(symbol)
        except Exception as exc:
            logger.warning(f"Finnhub quote error {symbol}: {exc}")
            return {}

    def fundamentals(self, symbol: str) -> Dict[str, Any]:
        if not self.client:
            return {}
        try:
            return self.client.company_basic_financials(symbol, 'all').get('metric', {})
        except Exception as exc:
            logger.warning(f"Finnhub basic financials error {symbol}: {exc}")
            return {}


finnhub_client = FinnhubClientWrapper() 