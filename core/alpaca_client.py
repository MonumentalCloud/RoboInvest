from __future__ import annotations

from typing import Any, Dict, List, Optional

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
            self._client = alpaca.REST(self.api_key, self.secret_key, self.base_url, api_version="v2")  # type: ignore

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

    def get_orders(self, status: str = "all", limit: int = 100) -> List[Dict[str, Any]]:
        """Get order history from Alpaca"""
        if not self.is_ready():
            logger.warning("Alpaca client not ready – cannot get orders.")
            return []
        try:
            orders = self._client.list_orders(status=status, limit=limit)  # type: ignore
            return [order._raw for order in orders]  # type: ignore
        except Exception as exc:
            logger.error(f"Alpaca get orders error: {exc}")
            return []

    def get_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trade history from Alpaca"""
        if not self.is_ready():
            logger.warning("Alpaca client not ready – cannot get trades.")
            return []
        try:
            # Get all orders first
            orders = self._client.list_orders(status="all", limit=limit)  # type: ignore
            
            # Filter for filled orders and convert to trade format
            trades = []
            for order in orders:
                if order.status == "filled":
                    # Safe type conversions with null checks
                    try:
                        qty = float(order.qty) if order.qty is not None else 0.0  # type: ignore
                        filled_qty = float(order.filled_qty) if order.filled_qty is not None else 0.0  # type: ignore
                        filled_avg_price = float(order.filled_avg_price) if order.filled_avg_price is not None else None  # type: ignore
                        
                        created_at = order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') and order.created_at is not None else None  # type: ignore
                        filled_at = order.filled_at.isoformat() if hasattr(order.filled_at, 'isoformat') and order.filled_at is not None else None  # type: ignore
                        
                        trade = {
                            "id": str(order.id) if order.id else None,  # type: ignore
                            "symbol": str(order.symbol) if order.symbol else None,  # type: ignore
                            "side": str(order.side) if order.side else None,  # type: ignore
                            "quantity": qty,
                            "filled_quantity": filled_qty,
                            "filled_avg_price": filled_avg_price,
                            "status": str(order.status) if order.status else None,  # type: ignore
                            "created_at": created_at,
                            "filled_at": filled_at,
                            "type": str(order.type) if order.type else None,  # type: ignore
                            "time_in_force": str(order.time_in_force) if order.time_in_force else None  # type: ignore
                        }
                        trades.append(trade)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error converting order {order.id} to trade format: {e}")
                        continue
            
            return trades
        except Exception as exc:
            logger.error(f"Alpaca get trades error: {exc}")
            return []

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions from Alpaca"""
        if not self.is_ready():
            logger.warning("Alpaca client not ready – cannot get positions.")
            return []
        try:
            positions = self._client.list_positions()  # type: ignore
            return [position._raw for position in positions]  # type: ignore
        except Exception as exc:
            logger.error(f"Alpaca get positions error: {exc}")
            return []

    def get_account_activities(self, activity_types: Optional[List[str]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get account activities (trades, dividends, etc.) from Alpaca"""
        if not self.is_ready():
            logger.warning("Alpaca client not ready – cannot get activities.")
            return []
        try:
            if activity_types is None:
                activity_types = ["FILL", "DIV", "ACATC", "ACATS", "CSD", "CSR", "CSW", "DIVCGL", "DIVCGS", "DIVFEE", "DIVNRA", "DIVROC", "DIVTW", "DTC", "FEE", "INT", "JNLC", "JNLS", "MA", "NC", "OPASN", "PAYMENT", "POS", "REORG", "SSO", "SSP", "SWEEP", "TC", "VEO", "WHT"]  # type: ignore
            
            activities = self._client.get_activities(activity_types=activity_types, limit=limit)  # type: ignore
            return [activity._raw for activity in activities]  # type: ignore
        except Exception as exc:
            logger.error(f"Alpaca get activities error: {exc}")
            return []


# Single shared instance
alpaca_client = AlpacaClientWrapper() 