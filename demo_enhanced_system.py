#!/usr/bin/env python3
"""
Demo script showing the enhanced trading system with:
- LLM analytical thinking
- Proper numerical calculations via tools
- Real PnL tracking
- Backtesting capabilities
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Import the enhanced system components
from tools.data_fetcher import data_fetcher
from tools.calculator import calculator
from tools.backtester import run_quick_backtest
from agents.enhanced_strategy_agent import enhanced_strategy_agent
from core.pnl_tracker import pnl_tracker
from utils.logger import logger  # type: ignore


def demo_data_fetcher():
    """Demonstrate the data fetcher capabilities."""
    print("🔍 DEMO: Data Fetcher")
    print("=" * 50)
    
    # Get market overview
    print("📊 Getting market overview...")
    market_data = data_fetcher.get_market_overview()
    
    if market_data.get("error"):
        print(f"❌ Error: {market_data['error']}")
        return
    
    print(f"📈 Market Sentiment: {market_data.get('market_sentiment', 'unknown')}")
    print(f"📊 VIX Level: {market_data.get('vix_level', 'unknown')}")
    
    # Show some indices
    indices = market_data.get("indices", {})
    for symbol, data in indices.items():
        if symbol in ["SPY", "QQQ"]:
            print(f"📈 {symbol}: ${data.get('current_price', 0):.2f} ({data.get('daily_change_pct', 0):.2f}%)")
    
    print("\n")


def demo_calculator():
    """Demonstrate the calculator tool capabilities."""
    print("🧮 DEMO: Calculator Tool")
    print("=" * 50)
    
    # Create sample data
    sample_prices = [100, 102, 98, 105, 103, 108, 104, 110, 107, 112]
    sample_trades = [
        {"entry_price": 100, "exit_price": 105, "quantity": 10},
        {"entry_price": 102, "exit_price": 98, "quantity": 5},
        {"entry_price": 104, "exit_price": 110, "quantity": 15}
    ]
    
    # Test technical analysis
    print("📊 Technical Analysis:")
    tech_result = calculator.calculate(
        "technical analysis",
        {"prices": sample_prices}
    )
    
    if tech_result.get("result"):
        result = tech_result["result"]
        print(f"   RSI: {result.get('rsi', 0):.2f}")
        print(f"   SMA 20: ${result.get('sma_20', 0):.2f}")
        print(f"   Current Price: ${result.get('current_price', 0):.2f}")
    
    # Test PnL calculation
    print("\n💰 PnL Calculation:")
    pnl_result = calculator.calculate(
        "pnl analysis",
        {"trades": sample_trades}
    )
    
    if pnl_result.get("result"):
        result = pnl_result["result"]
        print(f"   Total PnL: ${result.get('total_pnl', 0):.2f}")
        print(f"   Win Rate: {result.get('win_rate', 0):.2%}")
        print(f"   Profit Factor: {result.get('profit_factor', 0):.2f}")
    
    # Test volatility
    print("\n📈 Volatility Analysis:")
    vol_result = calculator.calculate(
        "volatility analysis",
        {"prices": sample_prices}
    )
    
    if vol_result.get("result"):
        result = vol_result["result"]
        print(f"   Realized Volatility: {result.get('realized_volatility', 0):.2%}")
        print(f"   Current Rolling Vol: {result.get('current_rolling_vol', 0):.2%}")
    
    print("\n")


def demo_enhanced_strategy():
    """Demonstrate the enhanced strategy agent."""
    print("🤖 DEMO: Enhanced Strategy Agent")
    print("=" * 50)
    
    # Create sample observation
    observation = {
        "symbol": "SPY",
        "symbols": ["SPY", "QQQ"],
        "sentiment": "bullish",
        "headlines": [
            "Markets rally on strong earnings",
            "Fed signals dovish stance",
            "Tech stocks lead gains"
        ],
        "market": {
            "SPY": {"price": 450.0, "change_pct": 1.2},
            "QQQ": {"price": 380.0, "change_pct": 1.8}
        }
    }
    
    print("📊 Sample Market Observation:")
    print(f"   Sentiment: {observation['sentiment']}")
    print(f"   SPY: ${observation['market']['SPY']['price']} ({observation['market']['SPY']['change_pct']}%)")
    print(f"   Headlines: {len(observation['headlines'])} positive")
    
    print("\n🧠 Getting strategy decision...")
    try:
        # Get strategy decision (this will use LLM if available)
        decision = enhanced_strategy_agent(observation)
        
        print(f"📈 Decision: {decision.get('action', 'UNKNOWN')}")
        print(f"🎯 Symbol: {decision.get('symbol', 'UNKNOWN')}")
        print(f"🔥 Confidence: {decision.get('confidence', 0):.2f}")
        print(f"📊 Position Size: {decision.get('position_size', 0):.2%}")
        print(f"💭 Reasoning: {decision.get('reasoning', 'No reasoning provided')[:100]}...")
        
        risk_assessment = decision.get('risk_assessment', {})
        if risk_assessment:
            print(f"⚠️  Risk Score: {risk_assessment.get('risk_score', 0):.2f}")
            print(f"📉 Max Drawdown: {risk_assessment.get('max_drawdown', 0):.2%}")
    
    except Exception as e:
        print(f"❌ Error getting strategy decision: {e}")
        print("💡 This is likely because OpenAI API key is not configured")
    
    print("\n")


def demo_pnl_tracker():
    """Demonstrate the PnL tracker."""
    print("💰 DEMO: PnL Tracker")
    print("=" * 50)
    
    # Simulate some trades
    print("📈 Simulating trades...")
    
    # Trade 1: Buy SPY
    trade1 = {
        "symbol": "SPY",
        "action": "BUY",
        "quantity": 10,
        "price": 450.0,
        "timestamp": datetime.now().isoformat()
    }
    
    result1 = pnl_tracker.process_trade(trade1)
    print(f"   Trade 1: {result1.get('position_status', 'unknown')} - {trade1['action']} {trade1['quantity']} {trade1['symbol']} @ ${trade1['price']}")
    
    # Trade 2: Sell SPY (close position)
    trade2 = {
        "symbol": "SPY",
        "action": "SELL",
        "quantity": 10,
        "price": 465.0,
        "timestamp": datetime.now().isoformat()
    }
    
    result2 = pnl_tracker.process_trade(trade2)
    print(f"   Trade 2: {result2.get('position_status', 'unknown')} - {trade2['action']} {trade2['quantity']} {trade2['symbol']} @ ${trade2['price']}")
    print(f"   PnL: ${result2.get('pnl', 0):.2f} ({result2.get('pnl_pct', 0):.2f}%)")
    
    # Show performance summary
    print("\n📊 Performance Summary:")
    summary = pnl_tracker.get_performance_summary()
    print(f"   Total Trades: {summary.get('total_trades', 0)}")
    print(f"   Total PnL: ${summary.get('total_pnl', 0):.2f}")
    print(f"   Win Rate: {summary.get('win_rate', 0):.2f}%")
    print(f"   Profit Factor: {summary.get('profit_factor', 0):.2f}")
    
    print("\n")


def demo_backtesting():
    """Demonstrate backtesting capabilities."""
    print("📊 DEMO: Backtesting System")
    print("=" * 50)
    
    print("🕐 Running 3-month backtest on SPY...")
    print("   This may take a moment to fetch data and run analysis...")
    
    try:
        # Run a quick backtest
        results = run_quick_backtest(symbol="SPY", period_months=3)
        
        if results.get("error"):
            print(f"❌ Backtest error: {results['error']}")
            return
        
        # Show key results
        backtest_info = results.get("backtest_info", {})
        performance = results.get("performance_metrics", {})
        summary = results.get("summary", {})
        
        print(f"\n📈 Backtest Results:")
        print(f"   Period: {backtest_info.get('start_date', 'unknown')} to {backtest_info.get('end_date', 'unknown')}")
        print(f"   Trading Days: {backtest_info.get('trading_days', 0)}")
        print(f"   Initial Capital: ${backtest_info.get('initial_capital', 0):,.2f}")
        
        print(f"\n💰 Performance:")
        print(f"   Total Return: {performance.get('total_return', 0):.2f}%")
        print(f"   Benchmark Return: {performance.get('benchmark_return', 0):.2f}%")
        print(f"   Excess Return: {performance.get('excess_return', 0):.2f}%")
        print(f"   Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        print(f"   Max Drawdown: {performance.get('max_drawdown', 0):.2f}%")
        
        print(f"\n🎯 Summary:")
        print(f"   Profitable: {'✅' if summary.get('profitable', False) else '❌'}")
        print(f"   Beat Benchmark: {'✅' if summary.get('beat_benchmark', False) else '❌'}")
        print(f"   Recommendation: {summary.get('recommendation', 'Unknown')}")
        
        # Show some trades
        trade_history = results.get("trade_history", [])
        if trade_history:
            print(f"\n📋 Recent Trades ({len(trade_history)} total):")
            for i, trade in enumerate(trade_history[-3:]):  # Show last 3 trades
                action = trade.get("action", "UNKNOWN")
                symbol = trade.get("symbol", "UNKNOWN")
                pnl = trade.get("pnl", 0)
                print(f"   {i+1}. {action} {symbol} - PnL: ${pnl:.2f}")
    
    except Exception as e:
        print(f"❌ Backtesting error: {e}")
        print("💡 This might be due to network issues or API rate limits")
    
    print("\n")


def main():
    """Run all demonstrations."""
    print("🚀 ENHANCED TRADING SYSTEM DEMO")
    print("=" * 60)
    print("This demo shows the enhanced trading system that combines:")
    print("✅ LLM analytical thinking")
    print("✅ Proper numerical calculations")
    print("✅ Real PnL tracking")
    print("✅ Backtesting capabilities")
    print("✅ Risk management")
    print("=" * 60)
    print()
    
    # Run demonstrations
    demo_data_fetcher()
    demo_calculator()
    demo_enhanced_strategy()
    demo_pnl_tracker()
    demo_backtesting()
    
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("Key Improvements Over Previous System:")
    print("📊 Real PnL calculation (not hardcoded to 0)")
    print("🧮 LLM uses calculator tools for numerical analysis")
    print("📈 Comprehensive backtesting framework")
    print("⚖️  Proper risk assessment and position sizing")
    print("📋 Detailed performance tracking and reporting")
    print()
    print("💡 Next Steps:")
    print("1. Configure OpenAI API key for full LLM capabilities")
    print("2. Run longer backtests (6-12 months)")
    print("3. Test on different symbols and market conditions")
    print("4. Implement live paper trading")
    print("5. Add more sophisticated risk management")
    print("=" * 60)


if __name__ == "__main__":
    main()