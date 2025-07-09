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
        self.demo_mode = False  # Disable demo mode - use real data with Polygon API
        
        # Initialize Polygon client if available and configured
        self.polygon_client = None
        if POLYGON_AVAILABLE and config.polygon_api_key and not self.demo_mode:
            try:
                self.polygon_client = RESTClient(api_key=config.polygon_api_key)
                logger.info("🚀 DataFetcher | Polygon.io client initialized - using premium data")
            except Exception as e:
                logger.error(f"Polygon client initialization failed: {e}")
        
        # Determine data source priority
        if self.demo_mode:
            self.data_source = "demo_data"
            logger.info("🎭 DataFetcher | Demo mode enabled - using realistic mock data")
        elif self.polygon_client:
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
            
            # Use demo data if in demo mode
            if self.demo_mode:
                data = self._get_demo_historical_data(symbol, period, interval)
                if data:
                    self.cache[cache_key] = (data, datetime.now())
                    return data
            
            # Try Polygon first if available
            elif self.polygon_client:
                data = self._get_polygon_historical_data(symbol, period, interval)
                if data and not data.get("error"):
                    self.cache[cache_key] = (data, datetime.now())
                    return data
                else:
                    logger.warning(f"Polygon data failed for {symbol}, falling back to yfinance")
            
            # Fallback to yfinance
            elif YFINANCE_AVAILABLE:
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
        """Get historical data using direct Yahoo Finance API (bypasses yfinance rate limits)."""
        try:
            # Use direct Yahoo Finance API instead of yfinance library
            logger.info(f"🚀 Fetching {symbol} via direct Yahoo Finance API")
            
            # Convert period to range parameter
            period_map = {
                '1d': '1d', '5d': '5d', '1mo': '1mo', '3mo': '3mo', 
                '6mo': '6mo', '1y': '1y', '2y': '2y', '5y': '5y', '10y': '10y'
            }
            range_param = period_map.get(period, '1y')
            
            # Convert interval
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '1d': '1d', '5d': '5d', '1wk': '1wk', '1mo': '1mo'
            }
            interval_param = interval_map.get(interval, '1d')
            
            # Direct Yahoo Finance API call
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'interval': interval_param,
                'range': range_param,
                'includePrePost': 'false'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache'
            }
            
            # Add small delay to be respectful
            time.sleep(random.uniform(0.5, 1.5))
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Yahoo Finance response
            if 'chart' not in data or not data['chart']['result']:
                return {"error": f"No data found for {symbol}", "data": None}
            
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Convert timestamps to dates
            dates = []
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            
            for i, ts in enumerate(timestamps):
                if quotes['open'][i] is not None:  # Skip null values
                    dates.append(datetime.fromtimestamp(ts).strftime('%Y-%m-%d'))
                    opens.append(round(quotes['open'][i], 2))
                    highs.append(round(quotes['high'][i], 2))
                    lows.append(round(quotes['low'][i], 2))
                    closes.append(round(quotes['close'][i], 2))
                    volumes.append(int(quotes['volume'][i]) if quotes['volume'][i] else 0)
            
            if not closes:
                return {"error": f"No valid price data for {symbol}", "data": None}
            
            # Calculate statistics
            start_price = closes[0]
            end_price = closes[-1]
            total_return = ((end_price / start_price - 1) * 100) if start_price != 0 else 0
            
            result_data = {
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
                    "total_days": len(closes),
                    "start_date": dates[0] if dates else None,
                    "end_date": dates[-1] if dates else None,
                    "start_price": start_price,
                    "end_price": end_price,
                    "total_return": round(total_return, 2),
                    "avg_volume": int(np.mean(volumes)) if volumes else 0
                },
                "data_source": "Yahoo Finance Direct API"
            }
            
            logger.info(f"✅ Successfully fetched {symbol} data ({len(closes)} points) via direct API")
            return result_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Yahoo Finance API request error for {symbol}: {e}")
            return {"error": f"API request failed: {str(e)}", "data": None}
        except KeyError as e:
            logger.error(f"Yahoo Finance API data parsing error for {symbol}: {e}")
            return {"error": f"Data parsing failed: {str(e)}", "data": None}
        except Exception as e:
            logger.error(f"Yahoo Finance API error for {symbol}: {e}")
            return {"error": str(e), "data": None}
    
    def _get_demo_historical_data(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Generate realistic demo data for testing purposes."""
        try:
            logger.info(f"🎭 Generating demo data for {symbol}")
            
            # Base prices for different symbols
            base_prices = {
                'SPY': 450.0,
                'AAPL': 175.0,
                'MSFT': 335.0,
                'GOOGL': 140.0,
                'TSLA': 250.0,
                'NVDA': 800.0,
                'VIX': 18.0,
                'QQQ': 380.0,
                'IWM': 195.0
            }
            
            base_price = base_prices.get(symbol, 100.0)
            
            # Calculate number of data points
            period_days = {
                '1d': 1, '5d': 5, '1mo': 22, '3mo': 66, 
                '6mo': 132, '1y': 252, '2y': 504, '5y': 1260, '10y': 2520
            }
            days = period_days.get(period, 5)
            
            # Generate dates
            end_date = datetime.now()
            dates = []
            for i in range(days):
                date = end_date - timedelta(days=days-1-i)
                dates.append(date.strftime('%Y-%m-%d'))
            
            # Generate realistic price movements
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            
            current_price = base_price
            
            for i in range(days):
                # Add some realistic volatility
                daily_change = random.uniform(-0.03, 0.03)  # ±3% daily movement
                trend = 0.0002  # Slight upward trend
                
                if symbol == 'VIX':
                    # VIX has different behavior
                    daily_change = random.uniform(-0.15, 0.15)
                    trend = -0.001
                
                # Calculate prices
                open_price = current_price * (1 + random.uniform(-0.005, 0.005))
                close_price = current_price * (1 + daily_change + trend)
                
                high_price = max(open_price, close_price) * (1 + random.uniform(0.001, 0.02))
                low_price = min(open_price, close_price) * (1 - random.uniform(0.001, 0.02))
                
                opens.append(round(open_price, 2))
                highs.append(round(high_price, 2))
                lows.append(round(low_price, 2))
                closes.append(round(close_price, 2))
                
                # Generate volume
                base_volume = {
                    'SPY': 50000000, 'AAPL': 45000000, 'MSFT': 25000000,
                    'GOOGL': 20000000, 'TSLA': 35000000, 'NVDA': 30000000,
                    'VIX': 0, 'QQQ': 25000000, 'IWM': 15000000
                }.get(symbol, 10000000)
                
                volume = int(base_volume * random.uniform(0.5, 1.5))
                volumes.append(volume)
                
                current_price = close_price
            
            # Calculate statistics
            start_price = closes[0]
            end_price = closes[-1]
            total_return = ((end_price / start_price - 1) * 100) if start_price != 0 else 0
            
            result_data = {
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
                    "total_days": len(closes),
                    "start_date": dates[0] if dates else None,
                    "end_date": dates[-1] if dates else None,
                    "start_price": start_price,
                    "end_price": end_price,
                    "total_return": round(total_return, 2),
                    "avg_volume": int(np.mean(volumes)) if volumes else 0
                },
                "data_source": "Demo Data (Mock)"
            }
            
            logger.info(f"✅ Generated demo data for {symbol} ({len(closes)} points)")
            return result_data
            
        except Exception as e:
            logger.error(f"Demo data generation error for {symbol}: {e}")
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
            # Get latest data using the correct Polygon API
            # Try to get previous close bar
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Get previous close data
            aggs = list(self.polygon_client.get_aggs(
                symbol, 1, "day", yesterday, yesterday, adjusted=True
            ))
            
            if aggs:
                latest_agg = aggs[-1]
                current_price = latest_agg.close
                
                return {
                    "symbol": symbol,
                    "current_price": current_price,
                    "previous_close": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "Polygon.io"
                }
            else:
                # If no recent data, fall back to historical method
                logger.warning(f"No recent Polygon data for {symbol}, using historical fallback")
                return self._get_historical_fallback_quote(symbol)
            
        except Exception as e:
            logger.error(f"Real-time quote error for {symbol}: {e}")
            # Fall back to historical data on any error
            return self._get_historical_fallback_quote(symbol)
    
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