"""
Backtesting system for testing trading strategies against historical data.
Uses the enhanced strategy agent with proper numerical analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

from tools.data_fetcher import data_fetcher
from tools.calculator import calculator
from agents.enhanced_strategy_agent import enhanced_strategy_agent
from core.pnl_tracker import PnLTracker
from utils.logger import logger  # type: ignore


class Backtester:
    """
    Backtesting system that simulates trading strategies on historical data.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trade_history: List[Dict[str, Any]] = []
        self.portfolio_history: List[Dict[str, Any]] = []
        self.pnl_tracker = PnLTracker()
        
    def run_backtest(self, 
                    symbol: str, 
                    start_date: str, 
                    end_date: str, 
                    strategy_agent=None) -> Dict[str, Any]:
        """
        Run a complete backtest on historical data.
        
        Args:
            symbol: Symbol to backtest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy_agent: Strategy agent to use (defaults to enhanced_strategy_agent)
            
        Returns:
            Comprehensive backtest results
        """
        try:
            logger.info(f"Backtester | Starting backtest for {symbol} from {start_date} to {end_date}")
            
            # Use enhanced strategy agent by default
            if strategy_agent is None:
                strategy_agent = enhanced_strategy_agent
            
            # Get historical data
            backtest_data = data_fetcher.prepare_backtest_data(symbol, start_date, end_date)
            
            if backtest_data.get("error"):
                return {"error": backtest_data["error"]}
            
            # Reset backtester state
            self._reset_backtest_state()
            
            # Run simulation
            simulation_results = self._simulate_trading(backtest_data, strategy_agent)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(backtest_data)
            
            # Generate comprehensive report
            backtest_report = self._generate_backtest_report(
                backtest_data, simulation_results, performance_metrics
            )
            
            logger.info(f"Backtester | Completed backtest. Total return: {performance_metrics.get('total_return', 0):.2f}%")
            
            return backtest_report
            
        except Exception as e:
            logger.error(f"Backtester error: {e}")
            return {"error": str(e)}
    
    def _reset_backtest_state(self):
        """Reset backtester state for a new run."""
        self.current_capital = self.initial_capital
        self.trade_history = []
        self.portfolio_history = []
        self.pnl_tracker = PnLTracker()  # Fresh tracker for backtest
    
    def _simulate_trading(self, backtest_data: Dict[str, Any], strategy_agent) -> Dict[str, Any]:
        """
        Simulate trading using the strategy agent.
        
        Args:
            backtest_data: Historical data prepared for backtesting
            strategy_agent: Strategy agent to use for decisions
            
        Returns:
            Simulation results
        """
        try:
            data_points = backtest_data["data"]
            symbol = backtest_data["symbol"]
            
            total_signals = 0
            executed_trades = 0
            
            # Process each day
            for i, day_data in enumerate(data_points):
                if i < 50:  # Skip first 50 days for indicators to warm up
                    continue
                
                # Prepare observation data for the strategy agent
                observation = self._prepare_observation(day_data, data_points, i, symbol)
                
                # Get strategy decision
                try:
                    decision = strategy_agent(observation)
                    total_signals += 1
                    
                    # Execute trade if decision is not HOLD
                    if decision.get("action") != "HOLD":
                        trade_result = self._execute_backtest_trade(decision, day_data, symbol)
                        
                        if trade_result.get("executed"):
                            executed_trades += 1
                            self.trade_history.append(trade_result)
                    
                except Exception as e:
                    logger.warning(f"Strategy agent error on day {i}: {e}")
                    continue
                
                # Record portfolio state
                self._record_portfolio_state(day_data, symbol)
            
            return {
                "total_signals": total_signals,
                "executed_trades": executed_trades,
                "execution_rate": executed_trades / total_signals if total_signals > 0 else 0,
                "final_capital": self.current_capital
            }
            
        except Exception as e:
            logger.error(f"Trading simulation error: {e}")
            return {"error": str(e)}
    
    def _prepare_observation(self, 
                           day_data: Dict[str, Any], 
                           all_data: List[Dict[str, Any]], 
                           current_index: int,
                           symbol: str) -> Dict[str, Any]:
        """Prepare observation data for the strategy agent."""
        
        # Get recent price history for context
        lookback_days = min(50, current_index)
        recent_data = all_data[current_index - lookback_days:current_index + 1]
        
        # Extract price series
        recent_closes = [d["Close"] for d in recent_data if d.get("Close")]
        recent_volumes = [d["Volume"] for d in recent_data if d.get("Volume")]
        
        # Calculate basic sentiment from price action
        if len(recent_closes) >= 5:
            short_ma = np.mean(recent_closes[-5:])
            long_ma = np.mean(recent_closes[-20:]) if len(recent_closes) >= 20 else np.mean(recent_closes)
            
            if short_ma > long_ma * 1.02:
                sentiment = "bullish"
            elif short_ma < long_ma * 0.98:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
        else:
            sentiment = "neutral"
        
        # Create observation
        observation = {
            "symbol": symbol,
            "symbols": [symbol],  # For compatibility
            "current_price": day_data.get("Close", 0),
            "volume": day_data.get("Volume", 0),
            "sentiment": sentiment,
            "headlines": [],  # No news data in backtest
            "market": {
                symbol: {
                    "price": day_data.get("Close", 0),
                    "change_pct": 0,  # Would need previous day for this
                    "volume": day_data.get("Volume", 0)
                }
            },
            "timestamp": day_data.get("Date", datetime.now().isoformat()),
            "backtest_mode": True,
            "historical_prices": recent_closes,
            "rsi": day_data.get("RSI", 50),
            "sma_20": day_data.get("SMA_20", day_data.get("Close", 0)),
            "sma_50": day_data.get("SMA_50", day_data.get("Close", 0))
        }
        
        return observation
    
    def _execute_backtest_trade(self, 
                              decision: Dict[str, Any], 
                              day_data: Dict[str, Any],
                              symbol: str) -> Dict[str, Any]:
        """Execute a trade in the backtest simulation."""
        try:
            action = decision.get("action", "HOLD")
            price = day_data.get("Close", 0)
            confidence = decision.get("confidence", 0.5)
            
            if not price:
                return {"executed": False, "error": "No price data"}
            
            # Calculate position size based on confidence and available capital
            position_size = decision.get("position_size", 0.05)  # Default 5%
            position_value = self.current_capital * position_size * confidence
            
            # Calculate quantity (assuming fractional shares allowed)
            quantity = position_value / price
            
            if quantity < 0.01:  # Minimum trade size
                return {"executed": False, "error": "Position too small"}
            
            # Create trade data
            trade_data = {
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": price,
                "confidence": confidence,
                "reasoning": decision.get("reasoning", ""),
                "timestamp": day_data.get("Date", datetime.now().isoformat())
            }
            
            # Process trade through PnL tracker
            trade_result = self.pnl_tracker.process_trade(trade_data, price)
            
            # Update capital based on trade
            if action == "BUY":
                self.current_capital -= position_value
            elif action == "SELL":
                self.current_capital += position_value
                
            # Add realized PnL if position was closed
            if trade_result.get("position_status") == "closed":
                self.current_capital += trade_result.get("pnl", 0)
            
            trade_result["executed"] = True
            trade_result["position_value"] = position_value
            
            return trade_result
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {"executed": False, "error": str(e)}
    
    def _record_portfolio_state(self, day_data: Dict[str, Any], symbol: str):
        """Record the portfolio state for this day."""
        
        # Get current prices for unrealized PnL calculation
        current_prices = {symbol: day_data.get("Close", 0)}
        unrealized_pnl = self.pnl_tracker.get_unrealized_pnl(current_prices)
        
        portfolio_value = self.current_capital + unrealized_pnl.get("total_unrealized_pnl", 0)
        
        portfolio_state = {
            "date": day_data.get("Date", datetime.now().isoformat()),
            "portfolio_value": portfolio_value,
            "cash": self.current_capital,
            "unrealized_pnl": unrealized_pnl.get("total_unrealized_pnl", 0),
            "total_return_pct": ((portfolio_value - self.initial_capital) / self.initial_capital) * 100,
            "open_positions": len(self.pnl_tracker.open_positions)
        }
        
        self.portfolio_history.append(portfolio_state)
    
    def _calculate_performance_metrics(self, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        try:
            if not self.portfolio_history:
                return {"error": "No portfolio history"}
            
            # Portfolio performance
            initial_value = self.initial_capital
            final_value = self.portfolio_history[-1]["portfolio_value"]
            total_return = ((final_value - initial_value) / initial_value) * 100
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(self.portfolio_history)):
                prev_value = self.portfolio_history[i-1]["portfolio_value"]
                curr_value = self.portfolio_history[i]["portfolio_value"]
                daily_return = ((curr_value - prev_value) / prev_value) if prev_value > 0 else 0
                daily_returns.append(daily_return)
            
            # Use calculator for performance metrics
            returns_analysis = calculator.calculate(
                "sharpe ratio calculation",
                {"returns": daily_returns}
            )
            
            drawdown_analysis = calculator.calculate(
                "drawdown analysis",
                {"prices": [p["portfolio_value"] for p in self.portfolio_history]}
            )
            
            # Benchmark comparison
            benchmark_return = backtest_data.get("metadata", {}).get("benchmark_return", 0)
            
            # Trade statistics
            trade_stats = self.pnl_tracker.get_performance_summary()
            
            return {
                "total_return": round(total_return, 2),
                "benchmark_return": round(benchmark_return, 2),
                "excess_return": round(total_return - benchmark_return, 2),
                "sharpe_ratio": returns_analysis.get("result", {}).get("sharpe_ratio", 0),
                "max_drawdown": drawdown_analysis.get("result", {}).get("max_drawdown_pct", 0),
                "volatility": returns_analysis.get("result", {}).get("annualized_volatility", 0),
                "final_portfolio_value": final_value,
                "trade_statistics": trade_stats,
                "total_trades": len(self.trade_history),
                "days_traded": len(self.portfolio_history)
            }
            
        except Exception as e:
            logger.error(f"Performance calculation error: {e}")
            return {"error": str(e)}
    
    def _generate_backtest_report(self, 
                                backtest_data: Dict[str, Any], 
                                simulation_results: Dict[str, Any],
                                performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive backtest report."""
        
        return {
            "backtest_info": {
                "symbol": backtest_data["symbol"],
                "start_date": backtest_data["start_date"],
                "end_date": backtest_data["end_date"],
                "trading_days": backtest_data["metadata"]["trading_days"],
                "initial_capital": self.initial_capital
            },
            "simulation_results": simulation_results,
            "performance_metrics": performance_metrics,
            "trade_history": self.trade_history,
            "portfolio_history": self.portfolio_history[-10:],  # Last 10 days
            "summary": {
                "profitable": performance_metrics.get("total_return", 0) > 0,
                "beat_benchmark": performance_metrics.get("excess_return", 0) > 0,
                "risk_adjusted_return": performance_metrics.get("sharpe_ratio", 0),
                "recommendation": self._generate_recommendation(performance_metrics)
            }
        }
    
    def _generate_recommendation(self, performance_metrics: Dict[str, Any]) -> str:
        """Generate trading recommendation based on backtest results."""
        
        total_return = performance_metrics.get("total_return", 0)
        sharpe_ratio = performance_metrics.get("sharpe_ratio", 0)
        max_drawdown = performance_metrics.get("max_drawdown", 0)
        excess_return = performance_metrics.get("excess_return", 0)
        
        if total_return > 20 and sharpe_ratio > 1.5 and max_drawdown < 15:
            return "EXCELLENT - Strong performance with good risk management"
        elif total_return > 10 and sharpe_ratio > 1.0 and excess_return > 0:
            return "GOOD - Profitable with reasonable risk"
        elif total_return > 0 and excess_return > 0:
            return "MODERATE - Profitable but consider risk optimization"
        elif total_return > 0:
            return "FAIR - Profitable but underperforming benchmark"
        else:
            return "POOR - Losing strategy, requires significant improvement"


def run_quick_backtest(symbol: str = "SPY", period_months: int = 6) -> Dict[str, Any]:
    """
    Run a quick backtest for testing purposes.
    
    Args:
        symbol: Symbol to test
        period_months: How many months back to test
        
    Returns:
        Backtest results
    """
    try:
        # Calculate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        # Format dates
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Run backtest
        backtester = Backtester(initial_capital=10000)
        results = backtester.run_backtest(symbol, start_date_str, end_date_str)
        
        return results
        
    except Exception as e:
        logger.error(f"Quick backtest error: {e}")
        return {"error": str(e)}


# Global backtester instance
backtester = Backtester()