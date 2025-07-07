from __future__ import annotations

from typing import Any, Dict

import alpaca_trade_api as alpaca  # type: ignore

from core.config import config
from utils.logger import logger  # type: ignore


class AlpacaClientWrapper:
    """Thin wrapper around alpaca-py SDK for paper trading."""

    def __init__(self) -> None:
        self.api_key = config.alpaca_api_key
        self.secret_key = config.alpaca_secret_key
        self.base_url = config.alpaca_base_url

        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca keys not set – trade execution will be disabled.")
            self._client = None
        else:
            self._client = alpaca.REST(self.api_key, self.secret_key, self.base_url, api_version="v2")

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def is_ready(self) -> bool:
        return self._client is not None

    def get_account(self) -> Dict[str, Any]:
        if not self.is_ready():
            return {}
        return self._client.get_account()._raw  # type: ignore

    def submit_order(self, symbol: str, qty: int, side: str) -> Dict[str, Any] | None:  # side "buy"/"sell"
        if not self.is_ready():
            logger.warning("Alpaca client not ready – skipping order.")
            return None
        try:
            order = self._client.submit_order(symbol=symbol, qty=qty, side=side.lower(), type="market", time_in_force="day")  # type: ignore
            logger.info(f"Alpaca | order submitted {side} {qty} {symbol}")
            return order._raw  # type: ignore
        except Exception as exc:
            logger.error(f"Alpaca order error: {exc}")
            return None


# Single shared instance
alpaca_client = AlpacaClientWrapper() 