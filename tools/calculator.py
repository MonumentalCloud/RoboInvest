"""
Calculator and data analysis tools for LLM agents.
Provides safe numerical computation and pandas operations.
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union, Optional
import yfinance as yf
from datetime import datetime, timedelta
import json
from utils.logger import logger  # type: ignore


class CalculatorTool:
    """Safe calculator for LLM agents to perform numerical analysis."""
    
    def __init__(self):
        self.data_cache = {}
        self.allowed_functions = {
            # Math operations
            'abs', 'round', 'sum', 'min', 'max', 'len',
            # NumPy functions
            'np.mean', 'np.std', 'np.median', 'np.percentile',
            'np.correlate', 'np.cov', 'np.var',
            # Pandas operations
            'pd.Series', 'pd.DataFrame', 'pd.to_datetime',
        }
    
    def calculate(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely execute mathematical operations.
        
        Args:
            operation: Description of what to calculate
            data: Input data for calculation
            
        Returns:
            Dictionary with calculation results
        """
        try:
            logger.info(f"Calculator | Performing: {operation}")
            
            # Route to appropriate calculation method
            if "pnl" in operation.lower() or "profit" in operation.lower():
                return self._calculate_pnl(data)
            elif "sharpe" in operation.lower():
                return self._calculate_sharpe(data)
            elif "drawdown" in operation.lower():
                return self._calculate_drawdown(data)
            elif "correlation" in operation.lower():
                return self._calculate_correlation(data)
            elif "volatility" in operation.lower():
                return self._calculate_volatility(data)
            elif "technical" in operation.lower():
                return self._calculate_technical_indicators(data)
            else:
                return self._general_calculation(operation, data)
                
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return {"error": str(e), "result": None}
    
    def _calculate_pnl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate profit and loss for trades."""
        try:
            trades = data.get("trades", [])
            if not trades:
                return {"error": "No trades provided", "result": None}
            
            df = pd.DataFrame(trades)
            
            # Calculate PnL for each trade
            if "entry_price" in df.columns and "exit_price" in df.columns:
                df["pnl"] = (df["exit_price"] - df["entry_price"]) * df.get("quantity", 1)
                df["pnl_pct"] = (df["exit_price"] - df["entry_price"]) / df["entry_price"] * 100
            
            # Calculate statistics
            total_pnl = df["pnl"].sum() if "pnl" in df.columns else 0
            win_rate = (df["pnl"] > 0).mean() if "pnl" in df.columns else 0
            avg_win = df[df["pnl"] > 0]["pnl"].mean() if "pnl" in df.columns else 0
            avg_loss = df[df["pnl"] < 0]["pnl"].mean() if "pnl" in df.columns else 0
            
            return {
                "result": {
                    "total_pnl": float(total_pnl),
                    "win_rate": float(win_rate),
                    "avg_win": float(avg_win) if not pd.isna(avg_win) else 0,
                    "avg_loss": float(avg_loss) if not pd.isna(avg_loss) else 0,
                    "num_trades": len(df),
                    "profit_factor": float(abs(avg_win / avg_loss)) if avg_loss != 0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"PnL calculation error: {e}", "result": None}
    
    def _calculate_sharpe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Sharpe ratio."""
        try:
            returns = data.get("returns", [])
            if not returns:
                return {"error": "No returns provided", "result": None}
            
            returns_series = pd.Series(returns)
            risk_free_rate = data.get("risk_free_rate", 0.02)  # 2% default
            
            excess_returns = returns_series - (risk_free_rate / 252)  # Daily risk-free rate
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            
            return {
                "result": {
                    "sharpe_ratio": float(sharpe_ratio),
                    "mean_return": float(returns_series.mean()),
                    "volatility": float(returns_series.std()),
                    "annualized_return": float(returns_series.mean() * 252),
                    "annualized_volatility": float(returns_series.std() * np.sqrt(252))
                }
            }
            
        except Exception as e:
            return {"error": f"Sharpe calculation error: {e}", "result": None}
    
    def _calculate_drawdown(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate maximum drawdown."""
        try:
            prices = data.get("prices", [])
            if not prices:
                return {"error": "No prices provided", "result": None}
            
            prices_series = pd.Series(prices)
            cumulative = (1 + prices_series.pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            
            max_drawdown = drawdown.min()
            max_drawdown_duration = self._calculate_drawdown_duration(drawdown)
            
            return {
                "result": {
                    "max_drawdown": float(max_drawdown),
                    "max_drawdown_pct": float(max_drawdown * 100),
                    "current_drawdown": float(drawdown.iloc[-1]),
                    "max_drawdown_duration": int(max_drawdown_duration)
                }
            }
            
        except Exception as e:
            return {"error": f"Drawdown calculation error: {e}", "result": None}
    
    def _calculate_correlation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate correlation between series."""
        try:
            series1 = pd.Series(data.get("series1", []))
            series2 = pd.Series(data.get("series2", []))
            
            if len(series1) == 0 or len(series2) == 0:
                return {"error": "Empty series provided", "result": None}
            
            correlation = series1.corr(series2)
            
            return {
                "result": {
                    "correlation": float(correlation),
                    "p_value": float(self._calculate_correlation_pvalue(series1, series2)),
                    "series1_stats": {
                        "mean": float(series1.mean()),
                        "std": float(series1.std())
                    },
                    "series2_stats": {
                        "mean": float(series2.mean()),
                        "std": float(series2.std())
                    }
                }
            }
            
        except Exception as e:
            return {"error": f"Correlation calculation error: {e}", "result": None}
    
    def _calculate_volatility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various volatility metrics."""
        try:
            prices = pd.Series(data.get("prices", []))
            if len(prices) == 0:
                return {"error": "No prices provided", "result": None}
            
            returns = prices.pct_change().dropna()
            
            # Various volatility calculations
            realized_vol = returns.std() * np.sqrt(252)  # Annualized
            rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
            
            # GARCH-like volatility (simple version)
            ewm_vol = returns.ewm(span=30).std() * np.sqrt(252)
            
            return {
                "result": {
                    "realized_volatility": float(realized_vol),
                    "current_rolling_vol": float(rolling_vol.iloc[-1]) if not pd.isna(rolling_vol.iloc[-1]) else 0,
                    "ewm_volatility": float(ewm_vol.iloc[-1]) if not pd.isna(ewm_vol.iloc[-1]) else 0,
                    "vol_of_vol": float(rolling_vol.std()) if not pd.isna(rolling_vol.std()) else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Volatility calculation error: {e}", "result": None}
    
    def _calculate_technical_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical indicators."""
        try:
            prices = pd.Series(data.get("prices", []))
            if len(prices) == 0:
                return {"error": "No prices provided", "result": None}
            
            # Simple moving averages
            sma_20 = prices.rolling(window=20).mean()
            sma_50 = prices.rolling(window=50).mean()
            
            # RSI calculation
            rsi = self._calculate_rsi(prices)
            
            # MACD
            macd_line, macd_signal = self._calculate_macd(prices)
            
            # Bollinger Bands
            bb_upper, bb_lower = self._calculate_bollinger_bands(prices)
            
            current_price = prices.iloc[-1]
            
            return {
                "result": {
                    "current_price": float(current_price),
                    "sma_20": float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else 0,
                    "sma_50": float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else 0,
                    "rsi": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50,
                    "macd": float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0,
                    "macd_signal": float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else 0,
                    "bb_upper": float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else 0,
                    "bb_lower": float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else 0,
                    "price_vs_sma20": float((current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100) if not pd.isna(sma_20.iloc[-1]) else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Technical indicators error: {e}", "result": None}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        return macd_line, macd_signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band
    
    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate maximum drawdown duration."""
        is_drawdown = drawdown < 0
        drawdown_periods = is_drawdown.astype(int).groupby((~is_drawdown).cumsum()).sum()
        return drawdown_periods.max() if len(drawdown_periods) > 0 else 0
    
    def _calculate_correlation_pvalue(self, series1: pd.Series, series2: pd.Series) -> float:
        """Calculate correlation p-value (simplified)."""
        from scipy.stats import pearsonr
        try:
            _, p_value = pearsonr(series1, series2)
            return p_value
        except:
            return 0.5  # Default neutral p-value
    
    def _general_calculation(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general calculations."""
        try:
            # Simple calculator operations
            if "sum" in operation.lower():
                values = data.get("values", [])
                result = sum(values)
            elif "mean" in operation.lower() or "average" in operation.lower():
                values = data.get("values", [])
                result = np.mean(values)
            elif "std" in operation.lower() or "standard deviation" in operation.lower():
                values = data.get("values", [])
                result = np.std(values)
            else:
                return {"error": f"Unknown operation: {operation}", "result": None}
            
            return {"result": float(result)}
            
        except Exception as e:
            return {"error": f"General calculation error: {e}", "result": None}


# Global calculator instance
calculator = CalculatorTool()