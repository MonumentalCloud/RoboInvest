from __future__ import annotations

from typing import Any, Dict
import polygon
from core.config import config
from utils.logger import logger  # type: ignore


class PolygonClientWrapper:
    """Wrapper around Polygon.io Python SDK."""

    def __init__(self) -> None:
        if not config.polygon_api_key:
            logger.error("Polygon.io API key missing – market data disabled.")
            self.client = None
        else:
            # Use the main StocksClient for stock data
            self.client = polygon.StocksClient(config.polygon_api_key)
            # Use ReferenceClient for ticker details
            self.reference_client = polygon.ReferenceClient(config.polygon_api_key)

    def quote(self, symbol: str) -> Dict[str, Any]:
        """Get current quote data for a symbol."""
        if not self.client:
            return {}
        try:
            # Get last quote
            quote = self.client.get_last_quote(symbol)
            
            # Get previous close
            prev_close_data = self.client.get_previous_close(symbol)
            prev_close = prev_close_data.get('results', [{}])[0] if prev_close_data else {}
            
            # Get current price from quote
            current_price = 0
            if quote and 'results' in quote:
                current_price = quote['results'].get('last', {}).get('price', 0)
            
            # Fallback to previous close if no current price
            if not current_price and prev_close:
                current_price = prev_close.get('c', 0)
            
            # Format to match Finnhub's quote format
            return {
                "c": current_price,  # current price
                "pc": prev_close.get('c', 0),  # previous close
                "h": prev_close.get('h', 0),  # high
                "l": prev_close.get('l', 0),  # low
                "o": prev_close.get('o', 0),  # open
                "t": prev_close.get('t', 0),  # timestamp
            }
        except Exception as exc:
            logger.warning(f"Polygon.io quote error {symbol}: {exc}")
            return {}

    def fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data for a symbol."""
        if not self.reference_client:
            return {}
        try:
            # Get ticker details for fundamental data
            details = self.reference_client.get_ticker_details(symbol)
            
            # Polygon.io doesn't provide financial ratios in the same way as Finnhub
            # We'll return what we can get from ticker details
            results = details.get('results', {})
            
            # Extract market cap, shares outstanding, etc.
            market_cap = results.get('market_cap', 0)
            shares_outstanding = results.get('weighted_shares_outstanding', 0)
            
            # Return in a format similar to Finnhub
            return {
                "marketCapitalization": market_cap,
                "sharesOutstanding": shares_outstanding,
                "name": results.get('name', ''),
                "ticker": results.get('ticker', symbol),
                "exchange": results.get('primary_exchange', ''),
                "industry": results.get('sic_description', ''),
                "country": results.get('locale', ''),
                "currency": results.get('currency_name', 'USD'),
                # Note: P/E and P/B ratios are not directly available in Polygon.io ticker details
                # These would need to be calculated from financial data or obtained from another endpoint
                "peBasicExclExtraTTM": None,
                "peInclExtraTTM": None,
                "pbAnnual": None,
            }
        except Exception as exc:
            logger.warning(f"Polygon.io fundamentals error {symbol}: {exc}")
            return {}


polygon_client = PolygonClientWrapper() 