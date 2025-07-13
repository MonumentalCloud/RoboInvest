"""
Data fetcher tool for historical and real-time market data.
Upgraded to use Polygon.io for professional-grade market data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta, date
import requests
import time
import random
from utils.logger import logger  # type: ignore
from core.config import config
import os

# Import Polygon for professional market data
try:
    from polygon import RESTClient
    POLYGON_AVAILABLE = True
except ImportError:
    POLYGON_AVAILABLE = False
    logger.error("Polygon not available - please install: pip install polygon-api-client")


class DataFetcher:
    """Enhanced market data fetcher with Polygon.io integration - Upgraded Plan Optimized."""
    
    def __init__(self):
        """Initialize DataFetcher with Polygon.io upgraded plan."""
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
        self.last_request_time = 0
        self.upgraded_delay = 0.1  # 100ms between requests for upgraded plan
        
        # Initialize Polygon client
        self.polygon_client = None
        try:
            from polygon import RESTClient
            api_key = os.getenv('POLYGON_API_KEY')
            if api_key:
                self.polygon_client = RESTClient(api_key)
                logger.info("🚀 DataFetcher | Polygon.io UPGRADED PLAN initialized - full access enabled")
            else:
                logger.error("❌ POLYGON_API_KEY not found in environment variables")
        except Exception as e:
            logger.error(f"Polygon client initialization failed: {e}")
        
        # Set data source
        if self.polygon_client:
            self.data_source = "polygon_upgraded"
            logger.info("📊 DataFetcher | Primary data source: Polygon.io UPGRADED PLAN (high rate limits, real-time access)")
        else:
            logger.error("❌ Polygon.io not available - please check API key configuration")
            self.data_source = "unavailable"
    
    def _wait_for_rate_limit(self):
        """Implement minimal rate limiting for Polygon upgraded plan."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.upgraded_delay:
            wait_time = self.upgraded_delay - time_since_last_request
            logger.debug(f"⏳ Polygon upgraded plan rate limiting: waiting {wait_time:.3f}s")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def is_premium_data_available(self) -> bool:
        """Check if premium Polygon data is available."""
        return True  # We're using upgraded plan
    
    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """
        Fetch historical price data for a symbol.
        Uses Polygon.io if available, otherwise falls back to yfinance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'SPY')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            Dictionary with price data and metadata
        """
        try:
            cache_key = f"{symbol}_{period}_{interval}_{self.data_source}"
            
            # Check cache first
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    logger.info(f"DataFetcher | Using cached data for {symbol}")
                    return cached_data
            
            logger.info(f"DataFetcher | Fetching {symbol} data for {period} via {self.data_source}")
            
            # Use Polygon for all data
            if self.polygon_client:
                self._wait_for_rate_limit() # Apply rate limiting
                data = self._get_polygon_historical_data(symbol, period, interval)
                if data and not data.get("error"):
                    self.cache[cache_key] = (data, datetime.now())
                    return data
                else:
                    logger.error(f"Polygon data failed for {symbol}: {data.get('error', 'Unknown error')}")
                    return {"error": f"Polygon data failed for {symbol}", "data": None}
            else:
                logger.error("Polygon client not available")
                return {"error": "Polygon client not available", "data": None}
            
        except Exception as e:
            logger.error(f"DataFetcher error for {symbol}: {e}")
            return {"error": str(e), "data": None}
    
    def _get_polygon_historical_data(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Get historical data from Polygon.io."""
        try:
            if not self.polygon_client:
                return {"error": "Polygon client not available", "data": None}
                
            # Calculate date range
            end_date = date.today()
            
            # Map period to days
            period_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, 
                '6mo': 180, '1y': 365, '2y': 730, '5y': 1825, '10y': 3650
            }
            days = period_map.get(period, 365)
            start_date = end_date - timedelta(days=days)
            
            # Map interval to Polygon timespan
            interval_map = {
                '1m': ('minute', 1), '5m': ('minute', 5), '15m': ('minute', 15),
                '30m': ('minute', 30), '1h': ('hour', 1), '1d': ('day', 1)
            }
            timespan, multiplier = interval_map.get(interval, ('day', 1))
            
            # Get aggregates from Polygon (rate limiting applied at caller level)
            aggs = list(self.polygon_client.get_aggs(
                symbol, multiplier, timespan, start_date, end_date,
                adjusted=True, sort="asc", limit=5000
            ))
            
            if not aggs:
                return {"error": f"No Polygon data found for {symbol}", "data": None}
            
            # Convert to standard format
            dates = []
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            
            for agg in aggs:
                dates.append(datetime.fromtimestamp(agg.timestamp / 1000).strftime('%Y-%m-%d'))
                opens.append(round(agg.open, 2))
                highs.append(round(agg.high, 2))
                lows.append(round(agg.low, 2))
                closes.append(round(agg.close, 2))
                volumes.append(agg.volume)
            
            # Calculate statistics
            start_price = closes[0] if closes else 0
            end_price = closes[-1] if closes else 0
            total_return = ((end_price / start_price - 1) * 100) if start_price != 0 else 0
            
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": {
                    "dates": dates,
                    "prices": {
                        "open": opens,
                        "high": highs,
                        "low": lows,
                        "close": closes,
                        "volume": volumes
                    }
                },
                "stats": {
                    "total_days": len(aggs),
                    "start_date": dates[0] if dates else None,
                    "end_date": dates[-1] if dates else None,
                    "start_price": start_price,
                    "end_price": end_price,
                    "total_return": round(total_return, 2),
                    "avg_volume": int(np.mean(volumes)) if volumes else 0
                },
                "data_source": "Polygon.io"
            }
            
        except Exception as e:
            logger.error(f"Polygon historical data error for {symbol}: {e}")
            return {"error": str(e), "data": None}
    

    
    def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get quote for a symbol - FREE TIER uses latest historical data only.
        Real-time quotes require paid Polygon plan ($199/month).
        """
        logger.info(f"📊 Getting latest price for {symbol} (FREE TIER: using end-of-day data)")
        
        # For free tier, always use latest historical data
        data = self.get_historical_data(symbol, period="5d", interval="1d")
        if data and data.get("data") and data["data"]["prices"]["close"]:
            latest_price = data["data"]["prices"]["close"][-1]
            latest_date = data["data"]["dates"][-1]
            return {
                "symbol": symbol,
                "current_price": latest_price,
                "timestamp": datetime.now().isoformat(),
                "data_date": latest_date,
                "data_source": "polygon_free_tier_eod",
                "note": "End-of-day data only (free tier)"
            }
        
        return {"error": "No historical data available for quote", "data": None}
    
    def _get_historical_fallback_quote(self, symbol: str) -> Dict[str, Any]:
        """Fallback method to get quote using historical data."""
        data = self.get_historical_data(symbol, period="5d", interval="1d")
        if data and data.get("data") and data["data"]["prices"]["close"]:
            latest_price = data["data"]["prices"]["close"][-1]
            return {
                "symbol": symbol,
                "current_price": latest_price,
                "timestamp": datetime.now().isoformat(),
                "data_source": "historical_fallback"
            }
        return {"error": "No fallback data available", "data": None}
    
    def get_multiple_symbols(self, symbols: List[str], period: str = "1y") -> Dict[str, Any]:
        """
        Fetch data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            period: Time period
            
        Returns:
            Dictionary with data for all symbols
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_historical_data(symbol, period)
                results[symbol] = data
            except Exception as e:
                logger.error(f"DataFetcher error for {symbol}: {e}")
                results[symbol] = {"error": str(e), "data": None}
        
        return results
    
    def get_benchmark_data(self, period: str = "1y") -> Dict[str, Any]:
        """Get benchmark data (SPY) for comparison."""
        return self.get_historical_data("SPY", period)
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview - FREE TIER optimized to minimize API calls."""
        try:
            # For free tier, get only SPY to avoid rate limits
            # Users can upgrade to get full market overview
            logger.info("📊 Getting market overview (FREE TIER: SPY only to avoid rate limits)")
            
            index_data = {}
            
            # Get SPY data only to stay within rate limits
            data = self.get_historical_data("SPY", period="5d")
            if data.get("data"):
                prices = data["data"]["prices"]["close"]
                dates = data["data"]["dates"]
                index_data["SPY"] = {
                    "current_price": prices[-1],
                    "daily_change_pct": ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) > 1 else 0,
                    "week_change_pct": ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 0 else 0,
                    "data_source": f"{self.data_source}_free_tier",
                    "data_date": dates[-1]
                }
            
            # Estimate market sentiment based on SPY performance
            spy_daily_change = index_data.get("SPY", {}).get("daily_change_pct", 0)
            if spy_daily_change > 1:
                sentiment = "bullish"
            elif spy_daily_change > 0:
                sentiment = "positive"
            elif spy_daily_change > -1:
                sentiment = "neutral"
            else:
                sentiment = "bearish"
            
            return {
                "indices": index_data,
                "market_sentiment": sentiment,
                "spy_daily_change": spy_daily_change,
                "timestamp": datetime.now().isoformat(),
                "data_source": f"{self.data_source}_free_tier",
                "note": "Free tier: SPY only. Upgrade for full market overview (QQQ, IWM, VIX)",
                "premium_data": self.is_premium_data_available()
            }
            
        except Exception as e:
            logger.error(f"Market overview error: {e}")
            return {"error": str(e)}
    
    def get_sector_data(self, period: str = "1y") -> Dict[str, Any]:
        """Get sector ETF data for broader market analysis."""
        sector_etfs = {
            "Technology": "XLK",
            "Healthcare": "XLV", 
            "Financial": "XLF",
            "Consumer Discretionary": "XLY",
            "Communication Services": "XLC",
            "Industrials": "XLI",
            "Consumer Staples": "XLP",
            "Energy": "XLE",
            "Utilities": "XLU",
            "Real Estate": "XLRE",
            "Materials": "XLB"
        }
        
        results = {}
        for sector, etf in sector_etfs.items():
            try:
                data = self.get_historical_data(etf, period)
                results[sector] = data
            except Exception as e:
                logger.error(f"DataFetcher error for {sector} ({etf}): {e}")
                results[sector] = {"error": str(e), "data": None}
        
        return results
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Get economic indicators that might affect trading decisions.
        Using proxy ETFs since direct economic data requires specialized APIs.
        """
        indicators = {
            "10_year_treasury": "^TNX",
            "vix": "^VIX",
            "dollar_index": "DX-Y.NYB",
            "gold": "GLD",
            "oil": "USO",
            "emerging_markets": "EEM",
            "developed_markets": "EFA"
        }
        
        results = {}
        for indicator, symbol in indicators.items():
            try:
                data = self.get_historical_data(symbol, period="3mo")
                if data.get("data"):
                    # Extract just the latest value and trend
                    prices = data["data"]["prices"]["close"]
                    latest_price = prices[-1]
                    prev_price = prices[-2] if len(prices) > 1 else latest_price
                    change_pct = ((latest_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
                    
                    results[indicator] = {
                        "current_value": latest_price,
                        "daily_change_pct": round(change_pct, 2),
                        "symbol": symbol,
                        "data_source": self.data_source
                    }
                else:
                    results[indicator] = {"error": "No data", "symbol": symbol}
            except Exception as e:
                logger.error(f"DataFetcher error for {indicator}: {e}")
                results[indicator] = {"error": str(e), "symbol": symbol}
        
        return results
    
    def prepare_backtest_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Prepare data specifically for backtesting.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Clean data formatted for backtesting
        """
        try:
            # For backtesting, use daily data with extended history
            if self.polygon_client:
                # Use Polygon for more accurate backtesting data
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                aggs = list(self.polygon_client.get_aggs(
                    symbol, 1, 'day', start, end, adjusted=True, sort="asc"
                ))
                
                if not aggs:
                    return {"error": f"No Polygon backtest data for {symbol}", "data": None}
                
                # Convert to DataFrame for technical indicators
                df_data = []
                for agg in aggs:
                    df_data.append({
                        'Date': datetime.fromtimestamp(agg.timestamp / 1000),
                        'Open': agg.open,
                        'High': agg.high,
                        'Low': agg.low,
                        'Close': agg.close,
                        'Volume': agg.volume
                    })
                
                hist = pd.DataFrame(df_data).set_index('Date')
                
            else:
                # No data source available
                return {"error": f"No data source available for {symbol}", "data": None}
            
            if hist.empty:
                return {"error": f"No backtest data for {symbol}", "data": None}
            
            # Add technical indicators for backtesting
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['RSI'] = self._calculate_rsi(hist['Close'])
            hist['Returns'] = hist['Close'].pct_change()
            
            # Clean format for backtesting
            backtest_data = {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "data": hist.round(4).to_dict('records'),  # Convert to list of dictionaries
                "metadata": {
                    "total_days": len(hist),
                    "trading_days": len(hist.dropna()),
                    "start_price": float(hist['Close'].iloc[0]),
                    "end_price": float(hist['Close'].iloc[-1]),
                    "benchmark_return": float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100),
                    "volatility": float(hist['Returns'].std() * np.sqrt(252) * 100),  # Annualized volatility
                    "data_source": self.data_source
                }
            }
            
            return backtest_data
            
        except Exception as e:
            logger.error(f"Backtest data preparation error: {e}")
            return {"error": str(e), "data": None}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI for the data."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch key fundamentals for a symbol from Polygon.io.
        Returns a dict with pe, pb, eps, market_cap, revenue, and other fields if available.
        """
        if not self.polygon_client:
            logger.warning("Polygon client not available for fundamentals.")
            return {"pe": None, "pb": None, "eps": None, "market_cap": None, "revenue": None}
        try:
            # Polygon vX/reference/financials endpoint (quarterly or annual)
            # We'll use the most recent annual report if available
            fin = self.polygon_client.get_stock_financials(symbol, limit=1, time_frame="annual")
            if fin and hasattr(fin, 'results') and fin.results:
                f = fin.results[0]
                return {
                    "pe": f.get("ratios", {}).get("priceToEarnings", None),
                    "pb": f.get("ratios", {}).get("priceToBook", None),
                    "eps": f.get("earningsPerBasicShare", None),
                    "market_cap": f.get("marketCapitalization", None),
                    "revenue": f.get("incomeStatement", {}).get("revenues", None),
                    "raw": f
                }
            else:
                logger.warning(f"No fundamentals found for {symbol}")
                return {"pe": None, "pb": None, "eps": None, "market_cap": None, "revenue": None}
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return {"pe": None, "pb": None, "eps": None, "market_cap": None, "revenue": None}


# Global data fetcher instance
data_fetcher = DataFetcher()