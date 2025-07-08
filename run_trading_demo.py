#!/usr/bin/env python3
"""
RoboInvest Autonomous Trading Demo
Run this script to see the trading system in action with:
- Real-time market analysis
- Alpha opportunity hunting
- Strategy development
- Paper trading execution
- Performance tracking
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_trading_system import AutonomousTradingSystem
from demo_enhanced_system import demo_data_fetcher, demo_calculator, demo_pnl_tracker
from tools.data_fetcher import data_fetcher
from tools.calculator import calculator
from core.config import config
from core.pnl_tracker import pnl_tracker


class TradingDemo:
    """Interactive demo of the RoboInvest autonomous trading system"""
    
    def __init__(self):
        self.system = AutonomousTradingSystem()
        self.session_data = {
            "start_time": datetime.now(),
            "trades": [],
            "strategies": [],
            "performance": {}
        }
    
    def print_banner(self):
        """Print the demo banner"""
        print("\n" + "="*80)
        print("🤖 ROBOINVEST AUTONOMOUS TRADING SYSTEM DEMO")
        print("="*80)
        print("📊 Paper Trading with Alpaca | AI-Powered Alpha Hunting")
        print("🔍 Real-time Market Analysis | Dynamic Strategy Creation")
        print("="*80)
        print(f"🕐 Session Started: {self.session_data['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
    
    def check_environment(self) -> bool:
        """Check if required environment variables are set"""
        print("🔧 Checking Environment Configuration...")
        
        missing_vars = []
        
        if not config.alpaca_api_key:
            missing_vars.append("ALPACA_API_KEY")
        if not config.alpaca_secret_key:
            missing_vars.append("ALPACA_SECRET_KEY")
        if not config.openai_api_key:
            missing_vars.append("OPENAI_API_KEY (optional but recommended)")
        
        if missing_vars:
            print("❌ Missing required environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n📝 Please create a .env file with the required variables.")
            print("   Copy env_template.txt to .env and fill in your API keys.")
            print("   Get Alpaca keys from: https://app.alpaca.markets/paper/dashboard/overview")
            print("   Get OpenAI key from: https://platform.openai.com/api-keys")
            return False
        
        print("✅ Environment configuration looks good!")
        print(f"   📈 Alpaca Paper Trading: {'✅' if config.alpaca_api_key else '❌'}")
        print(f"   🧠 OpenAI LLM: {'✅' if config.openai_api_key else '❌ (limited functionality)'}")
        print(f"   📊 Finnhub Data: {'✅' if config.finnhub_api_key else '❌ (optional)'}")
        return True
    
    def demo_market_data(self):
        """Demonstrate real-time market data capabilities"""
        print("\n📊 DEMO: Real-time Market Data")
        print("-" * 50)
        
        try:
            # Get current market overview
            print("🔍 Fetching current market data...")
            market_data = data_fetcher.get_market_overview()
            
            if market_data.get("error"):
                print(f"❌ Error fetching market data: {market_data['error']}")
                return
            
            # Display market sentiment
            sentiment = market_data.get("market_sentiment", "unknown")
            vix_level = market_data.get("vix_level", "unknown")
            print(f"📈 Market Sentiment: {sentiment}")
            print(f"😰 VIX Level: {vix_level}")
            
            # Show key indices
            indices = market_data.get("indices", {})
            print("\n📊 Key Market Indices:")
            for symbol in ["SPY", "QQQ", "IWM", "GLD", "TLT"]:
                if symbol in indices:
                    data = indices[symbol]
                    price = data.get("current_price", 0)
                    change = data.get("daily_change_pct", 0)
                    change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    print(f"   {change_symbol} {symbol}: ${price:.2f} ({change:+.2f}%)")
            
            # Show symbols being watched
            print(f"\n👀 Watching Symbols: {', '.join(config.symbols_to_watch)}")
            
        except Exception as e:
            print(f"❌ Error in market data demo: {e}")
    
    def demo_autonomous_trading(self, max_iterations: int = 3):
        """Run the autonomous trading system with visible progress"""
        print(f"\n🤖 DEMO: Autonomous Alpha Hunting ({max_iterations} iterations)")
        print("-" * 50)
        
        try:
            print("🚀 Starting autonomous trading system...")
            print("   This will hunt for alpha opportunities and create dynamic strategies")
            print("   Each iteration includes: market analysis → opportunity hunting → strategy creation → validation")
            print()
            
            # Run the autonomous trading system
            results = self.system.start_autonomous_trading(max_iterations=max_iterations)
            
            if results.get("error"):
                print(f"❌ Error in autonomous trading: {results['error']}")
                return
            
            # Display results
            print("📊 AUTONOMOUS TRADING RESULTS")
            print("=" * 50)
            
            iterations = results.get("iterations", [])
            for i, iteration in enumerate(iterations, 1):
                print(f"\n🔄 Iteration {i}:")
                result = iteration.get("result", {})
                
                # Strategy details
                action = result.get("action", "HOLD")
                symbol = result.get("primary_ticker", "UNKNOWN")
                confidence = result.get("confidence", 0)
                position_size = result.get("position_size", 0)
                thesis = result.get("alpha_thesis", "No thesis provided")
                
                print(f"   📈 Action: {action}")
                print(f"   🎯 Symbol: {symbol}")
                print(f"   🔥 Confidence: {confidence:.2%}")
                print(f"   📊 Position Size: {position_size:.2%}")
                print(f"   💭 Thesis: {thesis[:100]}...")
                
                # Risk assessment
                risk = result.get("risk_level", "UNKNOWN")
                print(f"   ⚠️  Risk Level: {risk}")
                
                # Research factors
                research_factors = result.get("research_factors", [])
                if research_factors:
                    print(f"   🔍 Research Factors: {', '.join(research_factors[:3])}")
                
                # Cycle time
                cycle_time = result.get("cycle_time_seconds", 0)
                print(f"   ⏱️  Cycle Time: {cycle_time:.2f}s")
            
            # Final strategy
            final_strategy = results.get("final_strategy")
            if final_strategy:
                print(f"\n🏆 FINAL STRATEGY SELECTED:")
                print(f"   📈 Action: {final_strategy.get('action', 'HOLD')}")
                print(f"   🎯 Symbol: {final_strategy.get('primary_ticker', 'UNKNOWN')}")
                print(f"   🔥 Confidence: {final_strategy.get('confidence', 0):.2%}")
                print(f"   💭 Thesis: {final_strategy.get('alpha_thesis', 'No thesis')}")
                
                # Store for potential execution
                self.session_data["strategies"].append(final_strategy)
            
            # Key insights
            insights = results.get("key_insights", [])
            if insights:
                print(f"\n💡 KEY INSIGHTS:")
                for insight in insights[:3]:
                    print(f"   • {insight}")
            
        except Exception as e:
            print(f"❌ Error in autonomous trading demo: {e}")
            import traceback
            traceback.print_exc()
    
    def demo_paper_trading(self):
        """Demonstrate paper trading capabilities"""
        print("\n💰 DEMO: Paper Trading Simulation")
        print("-" * 50)
        
        try:
            # Check if we have any strategies to execute
            if not self.session_data["strategies"]:
                print("📝 No strategies available for execution.")
                print("   Run the autonomous trading demo first to generate strategies.")
                return
            
            # Get the latest strategy
            strategy = self.session_data["strategies"][-1]
            
            print(f"📈 Executing Strategy:")
            print(f"   Action: {strategy.get('action', 'HOLD')}")
            print(f"   Symbol: {strategy.get('primary_ticker', 'UNKNOWN')}")
            print(f"   Position Size: {strategy.get('position_size', 0):.2%}")
            print(f"   Confidence: {strategy.get('confidence', 0):.2%}")
            
            # Simulate trade execution
            if strategy.get("action") in ["BUY", "SELL"]:
                print("\n🔄 Simulating trade execution...")
                
                # Get current price
                symbol = strategy.get("primary_ticker", "SPY")
                try:
                    market_data = data_fetcher.get_market_overview()
                    indices = market_data.get("indices", {})
                    if symbol in indices:
                        current_price = indices[symbol].get("current_price", 100.0)
                    else:
                        current_price = 100.0  # Fallback price
                except:
                    current_price = 100.0
                
                # Create trade record
                trade = {
                    "symbol": symbol,
                    "action": strategy.get("action"),
                    "quantity": 10,  # Fixed quantity for demo
                    "price": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "strategy_confidence": strategy.get("confidence", 0),
                    "alpha_thesis": strategy.get("alpha_thesis", ""),
                    "position_size": strategy.get("position_size", 0)
                }
                
                # Process trade through PnL tracker
                result = pnl_tracker.process_trade(trade)
                
                print(f"✅ Trade Executed:")
                print(f"   {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
                print(f"   Status: {result.get('position_status', 'unknown')}")
                
                # Store trade
                self.session_data["trades"].append(trade)
                
                # Show updated performance
                summary = pnl_tracker.get_performance_summary()
                print(f"\n📊 Updated Performance:")
                print(f"   Total Trades: {summary.get('total_trades', 0)}")
                print(f"   Total PnL: ${summary.get('total_pnl', 0):.2f}")
                print(f"   Win Rate: {summary.get('win_rate', 0):.2f}%")
            else:
                print("⏸️  Strategy recommends HOLD - no trade executed")
            
        except Exception as e:
            print(f"❌ Error in paper trading demo: {e}")
    
    def show_performance_summary(self):
        """Show comprehensive performance summary"""
        print("\n📊 PERFORMANCE SUMMARY")
        print("-" * 50)
        
        try:
            # Get PnL summary
            summary = pnl_tracker.get_performance_summary()
            
            print("💰 Trading Performance:")
            print(f"   Total Trades: {summary.get('total_trades', 0)}")
            print(f"   Total PnL: ${summary.get('total_pnl', 0):.2f}")
            print(f"   Win Rate: {summary.get('win_rate', 0):.2f}%")
            print(f"   Profit Factor: {summary.get('profit_factor', 0):.2f}")
            print(f"   Average Trade: ${summary.get('average_trade', 0):.2f}")
            
            # Session summary
            session_duration = datetime.now() - self.session_data["start_time"]
            print(f"\n⏱️  Session Duration: {session_duration}")
            print(f"   Strategies Generated: {len(self.session_data['strategies'])}")
            print(f"   Trades Executed: {len(self.session_data['trades'])}")
            
            # Recent trades
            if self.session_data["trades"]:
                print(f"\n📈 Recent Trades:")
                for trade in self.session_data["trades"][-3:]:  # Last 3 trades
                    print(f"   {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
            
        except Exception as e:
            print(f"❌ Error showing performance summary: {e}")
    
    def interactive_menu(self):
        """Interactive menu for running different demos"""
        while True:
            print("\n" + "="*50)
            print("🤖 ROBOINVEST DEMO MENU")
            print("="*50)
            print("1. 📊 Show Market Data")
            print("2. 🧮 Test Calculator Tools")
            print("3. 💰 Test PnL Tracker")
            print("4. 🤖 Run Autonomous Trading (3 iterations)")
            print("5. 💰 Execute Paper Trading")
            print("6. 📊 Show Performance Summary")
            print("7. 🚀 Run Full Demo Sequence")
            print("8. ❌ Exit")
            print("="*50)
            
            choice = input("\nSelect an option (1-8): ").strip()
            
            if choice == "1":
                self.demo_market_data()
            elif choice == "2":
                demo_calculator()
            elif choice == "3":
                demo_pnl_tracker()
            elif choice == "4":
                self.demo_autonomous_trading(3)
            elif choice == "5":
                self.demo_paper_trading()
            elif choice == "6":
                self.show_performance_summary()
            elif choice == "7":
                self.run_full_demo()
            elif choice == "8":
                print("\n👋 Thanks for trying RoboInvest! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-8.")
    
    def run_full_demo(self):
        """Run the complete demo sequence"""
        print("\n🚀 RUNNING FULL DEMO SEQUENCE")
        print("="*50)
        
        # 1. Market data
        self.demo_market_data()
        time.sleep(2)
        
        # 2. Calculator tools
        demo_calculator()
        time.sleep(2)
        
        # 3. PnL tracker
        demo_pnl_tracker()
        time.sleep(2)
        
        # 4. Autonomous trading
        self.demo_autonomous_trading(2)
        time.sleep(2)
        
        # 5. Paper trading
        self.demo_paper_trading()
        time.sleep(2)
        
        # 6. Performance summary
        self.show_performance_summary()
        
        print("\n✅ Full demo sequence complete!")
    
    def run(self):
        """Main entry point"""
        self.print_banner()
        
        # Check environment
        if not self.check_environment():
            print("\n❌ Please configure your environment variables and try again.")
            return
        
        # Show quick market overview
        self.demo_market_data()
        
        # Start interactive menu
        self.interactive_menu()


def main():
    """Main function"""
    try:
        demo = TradingDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 