"""
Data fetcher tool for historical and real-time market data.
Upgraded to use Polygon.io for professional-grade market data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta, date
import requests
from utils.logger import logger  # type: ignore
from core.config import config

# Try to import Polygon, fallback to yfinance if not available
try:
    from polygon import RESTClient
    POLYGON_AVAILABLE = True
except ImportError:
    POLYGON_AVAILABLE = False
    logger.warning("Polygon not available, falling back to yfinance")

# Import yfinance as fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.error("Neither Polygon nor yfinance available!")


class DataFetcher:
    """Enhanced market data fetcher with Polygon.io integration."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        # Initialize Polygon client if available and configured
        self.polygon_client = None
        if POLYGON_AVAILABLE and config.polygon_api_key:
            try:
                self.polygon_client = RESTClient(api_key=config.polygon_api_key)
                logger.info("🚀 DataFetcher | Polygon.io client initialized - using premium data")
            except Exception as e:
                logger.error(f"Polygon client initialization failed: {e}")
        
        # Determine data source priority
        if self.polygon_client:
            self.data_source = "polygon"
            logger.info("📊 DataFetcher | Primary data source: Polygon.io (Premium)")
        elif YFINANCE_AVAILABLE:
            self.data_source = "yfinance"
            logger.info("📊 DataFetcher | Primary data source: yfinance (Free)")
        else:
            logger.error("❌ No market data source available!")
    
    def is_premium_data_available(self) -> bool:
        """Check if premium Polygon data is available."""
        return self.polygon_client is not None
    
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
            
            # Try Polygon first if available
            if self.polygon_client:
                data = self._get_polygon_historical_data(symbol, period, interval)
                if data and not data.get("error"):
                    self.cache[cache_key] = (data, datetime.now())
                    return data
                else:
                    logger.warning(f"Polygon data failed for {symbol}, falling back to yfinance")
            
            # Fallback to yfinance
            if YFINANCE_AVAILABLE:
                data = self._get_yfinance_historical_data(symbol, period, interval)
                if data:
                    self.cache[cache_key] = (data, datetime.now())
                    return data
            
            return {"error": f"No data source available for {symbol}", "data": None}
            
        except Exception as e:
            logger.error(f"DataFetcher error for {symbol}: {e}")
            return {"error": str(e), "data": None}
    
    def _get_polygon_historical_data(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Get historical data from Polygon.io."""
        try:
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
            
            # Get aggregates from Polygon
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
    
    def _get_yfinance_historical_data(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Get historical data from yfinance (fallback)."""
        try:
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": f"No yfinance data found for {symbol}", "data": None}
            
            # Convert to clean format
            data = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": {
                    "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                    "prices": {
                        "open": hist['Open'].round(2).tolist(),
                        "high": hist['High'].round(2).tolist(),
                        "low": hist['Low'].round(2).tolist(),
                        "close": hist['Close'].round(2).tolist(),
                        "volume": hist['Volume'].tolist()
                    }
                },
                "stats": {
                    "total_days": len(hist),
                    "start_date": hist.index[0].strftime('%Y-%m-%d'),
                    "end_date": hist.index[-1].strftime('%Y-%m-%d'),
                    "start_price": float(hist['Close'].iloc[0]),
                    "end_price": float(hist['Close'].iloc[-1]),
                    "total_return": float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100),
                    "avg_volume": float(hist['Volume'].mean())
                },
                "data_source": "yfinance"
            }
            
            return data
            
        except Exception as e:
            logger.error(f"yfinance historical data error for {symbol}: {e}")
            return {"error": str(e), "data": None}
    
    def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a symbol (Polygon premium feature).
        Falls back to latest available data if real-time not available.
        """
        if not self.polygon_client:
            logger.warning("Real-time quotes require Polygon.io - using latest historical data")
            # Fallback to latest historical data
            data = self.get_historical_data(symbol, period="5d", interval="1d")
            if data and data.get("data") and data["data"]["prices"]["close"]:
                latest_price = data["data"]["prices"]["close"][-1]
                return {
                    "symbol": symbol,
                    "current_price": latest_price,
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "historical_fallback"
                }
            return {"error": "No real-time data available", "data": None}
        
        try:
            # Get latest trade from Polygon
            prev_close_data = list(self.polygon_client.get_previous_close(symbol))
            prev_close_price = prev_close_data[0].close if prev_close_data else None
            
            # For real-time, we'll use the previous close as an approximation
            # (Full real-time requires WebSocket subscription)
            return {
                "symbol": symbol,
                "current_price": prev_close_price,
                "previous_close": prev_close_price,
                "timestamp": datetime.now().isoformat(),
                "data_source": "Polygon.io"
            }
            
        except Exception as e:
            logger.error(f"Real-time quote error for {symbol}: {e}")
            return {"error": str(e), "data": None}
    
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
        """Get a comprehensive market overview with premium data if available."""
        try:
            # Major indices
            indices = ["SPY", "QQQ", "IWM", "VIX"]
            index_data = {}
            
            for index in indices:
                if self.polygon_client:
                    # Use real-time/latest data from Polygon
                    quote = self.get_real_time_quote(index)
                    if not quote.get("error"):
                        index_data[index] = {
                            "current_price": quote.get("current_price"),
                            "data_source": "Polygon.io"
                        }
                else:
                    # Fallback to historical data
                    data = self.get_historical_data(index, period="5d")
                    if data.get("data"):
                        prices = data["data"]["prices"]["close"]
                        index_data[index] = {
                            "current_price": prices[-1],
                            "daily_change_pct": ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) > 1 else 0,
                            "week_change_pct": ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 0 else 0,
                            "data_source": self.data_source
                        }
            
            # Market sentiment based on VIX
            vix_level = index_data.get("VIX", {}).get("current_price", 20)
            if vix_level < 15:
                sentiment = "complacent"
            elif vix_level < 25:
                sentiment = "normal"
            elif vix_level < 35:
                sentiment = "fearful"
            else:
                sentiment = "panic"
            
            return {
                "indices": index_data,
                "market_sentiment": sentiment,
                "vix_level": vix_level,
                "timestamp": datetime.now().isoformat(),
                "data_source": self.data_source,
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
                # Fallback to yfinance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
            
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


# Global data fetcher instance
data_fetcher = DataFetcher()