"""
Data fetcher tool for historical market data.
Provides clean, structured data for LLM analysis.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import requests
from utils.logger import logger  # type: ignore
from core.config import config


class DataFetcher:
    """Fetches and structures market data for analysis."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """
        Fetch historical price data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'SPY')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            Dictionary with price data and metadata
        """
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            
            # Check cache first
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    logger.info(f"DataFetcher | Using cached data for {symbol}")
                    return cached_data
            
            logger.info(f"DataFetcher | Fetching {symbol} data for {period}")
            
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": f"No data found for {symbol}", "data": None}
            
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
                }
            }
            
            # Cache the result
            self.cache[cache_key] = (data, datetime.now())
            
            return data
            
        except Exception as e:
            logger.error(f"DataFetcher error for {symbol}: {e}")
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
                        "symbol": symbol
                    }
                else:
                    results[indicator] = {"error": "No data", "symbol": symbol}
            except Exception as e:
                logger.error(f"DataFetcher error for {indicator}: {e}")
                results[indicator] = {"error": str(e), "symbol": symbol}
        
        return results
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get a comprehensive market overview."""
        try:
            # Major indices
            indices = ["SPY", "QQQ", "IWM", "^VIX"]
            index_data = {}
            
            for index in indices:
                data = self.get_historical_data(index, period="5d")
                if data.get("data"):
                    prices = data["data"]["prices"]["close"]
                    index_data[index] = {
                        "current_price": prices[-1],
                        "daily_change_pct": ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) > 1 else 0,
                        "week_change_pct": ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 0 else 0
                    }
            
            # Economic indicators
            economic = self.get_economic_indicators()
            
            # Market sentiment based on VIX
            vix_level = index_data.get("^VIX", {}).get("current_price", 20)
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
                "economic_indicators": economic,
                "market_sentiment": sentiment,
                "vix_level": vix_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market overview error: {e}")
            return {"error": str(e)}
    
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
            # Calculate period from dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Use yfinance with specific date range
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {"error": f"No data found for {symbol} between {start_date} and {end_date}", "data": None}
            
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
                    "volatility": float(hist['Returns'].std() * np.sqrt(252) * 100)  # Annualized volatility
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