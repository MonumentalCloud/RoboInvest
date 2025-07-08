#!/usr/bin/env python3
"""
Simple RoboInvest Demo
Shows the trading system capabilities with basic market data and strategy simulation
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please run: pip install yfinance pandas numpy python-dotenv")
    sys.exit(1)


class SimpleTradingDemo:
    """Simple demo of trading system capabilities"""
    
    def __init__(self):
        self.session_data = {
            "start_time": datetime.now(),
            "trades": [],
            "strategies": [],
            "performance": {"total_pnl": 0, "trades": 0, "wins": 0}
        }
        self.symbols = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
    
    def print_banner(self):
        """Print the demo banner"""
        print("\n" + "="*80)
        print("🤖 ROBOINVEST AUTONOMOUS TRADING SYSTEM DEMO")
        print("="*80)
        print("📊 Paper Trading Simulation | AI-Powered Strategy Generation")
        print("🔍 Real-time Market Analysis | Dynamic Alpha Hunting")
        print("="*80)
        print(f"🕐 Session Started: {self.session_data['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
    
    def get_market_data(self):
        """Get real-time market data"""
        print("📊 Fetching Real-time Market Data...")
        print("-" * 50)
        
        market_data = {}
        
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    market_data[symbol] = {
                        "current_price": current_price,
                        "change_pct": change_pct,
                        "volume": hist['Volume'].iloc[-1],
                        "high": hist['High'].iloc[-1],
                        "low": hist['Low'].iloc[-1]
                    }
                    
                    change_symbol = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
                    print(f"   {change_symbol} {symbol}: ${current_price:.2f} ({change_pct:+.2f}%)")
                else:
                    print(f"   ❌ {symbol}: No data available")
                    
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")
        
        return market_data
    
    def analyze_market_sentiment(self, market_data):
        """Analyze market sentiment based on price movements"""
        print("\n🧠 Analyzing Market Sentiment...")
        print("-" * 50)
        
        if not market_data:
            return "neutral"
        
        # Calculate overall sentiment
        changes = [data["change_pct"] for data in market_data.values()]
        avg_change = np.mean(changes)
        
        # Determine sentiment
        if avg_change > 1.0:
            sentiment = "bullish"
            sentiment_emoji = "📈"
        elif avg_change < -1.0:
            sentiment = "bearish"
            sentiment_emoji = "📉"
        else:
            sentiment = "neutral"
            sentiment_emoji = "➡️"
        
        print(f"   {sentiment_emoji} Overall Sentiment: {sentiment.upper()}")
        print(f"   📊 Average Change: {avg_change:+.2f}%")
        
        # Find best and worst performers
        best_symbol = max(market_data.items(), key=lambda x: x[1]["change_pct"])
        worst_symbol = min(market_data.items(), key=lambda x: x[1]["change_pct"])
        
        print(f"   🏆 Best Performer: {best_symbol[0]} ({best_symbol[1]['change_pct']:+.2f}%)")
        print(f"   📉 Worst Performer: {worst_symbol[0]} ({worst_symbol[1]['change_pct']:+.2f}%)")
        
        return sentiment
    
    def generate_trading_strategy(self, market_data, sentiment):
        """Generate a trading strategy based on market analysis"""
        print("\n🤖 Generating Trading Strategy...")
        print("-" * 50)
        
        if not market_data:
            return {"action": "HOLD", "reason": "No market data available"}
        
        # Simple strategy logic
        if sentiment == "bullish":
            # Find the best performing stock
            best_symbol = max(market_data.items(), key=lambda x: x[1]["change_pct"])
            strategy = {
                "action": "BUY",
                "symbol": best_symbol[0],
                "reason": f"Strong momentum in {best_symbol[0]} with {best_symbol[1]['change_pct']:+.2f}% gain",
                "confidence": 0.7,
                "position_size": 0.1,  # 10% of portfolio
                "stop_loss": -0.05,    # 5% stop loss
                "take_profit": 0.15    # 15% take profit
            }
        elif sentiment == "bearish":
            # Find the worst performing stock to short
            worst_symbol = min(market_data.items(), key=lambda x: x[1]["change_pct"])
            strategy = {
                "action": "SELL",
                "symbol": worst_symbol[0],
                "reason": f"Downward momentum in {worst_symbol[0]} with {worst_symbol[1]['change_pct']:+.2f}% loss",
                "confidence": 0.6,
                "position_size": 0.08,  # 8% of portfolio
                "stop_loss": 0.05,      # 5% stop loss
                "take_profit": -0.12    # 12% take profit
            }
        else:
            # Neutral sentiment - look for opportunities
            # Find stock with highest volume (potential breakout)
            high_volume_symbol = max(market_data.items(), key=lambda x: x[1]["volume"])
            strategy = {
                "action": "BUY",
                "symbol": high_volume_symbol[0],
                "reason": f"High volume activity in {high_volume_symbol[0]} suggests potential breakout",
                "confidence": 0.5,
                "position_size": 0.05,  # 5% of portfolio
                "stop_loss": -0.03,     # 3% stop loss
                "take_profit": 0.08     # 8% take profit
            }
        
        # Display strategy
        print(f"   📈 Action: {strategy['action']}")
        print(f"   🎯 Symbol: {strategy['symbol']}")
        print(f"   🔥 Confidence: {strategy['confidence']:.1%}")
        print(f"   📊 Position Size: {strategy['position_size']:.1%}")
        print(f"   💭 Reason: {strategy['reason']}")
        print(f"   🛑 Stop Loss: {strategy['stop_loss']:.1%}")
        print(f"   🎯 Take Profit: {strategy['take_profit']:.1%}")
        
        return strategy
    
    def simulate_trade_execution(self, strategy):
        """Simulate trade execution"""
        print("\n💰 Simulating Trade Execution...")
        print("-" * 50)
        
        if strategy["action"] == "HOLD":
            print("   ⏸️  Strategy recommends HOLD - no trade executed")
            return None
        
        # Get current price for the symbol
        try:
            ticker = yf.Ticker(strategy["symbol"])
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
        except:
            current_price = 100.0  # Fallback price
        
        # Create trade record
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": strategy["symbol"],
            "action": strategy["action"],
            "price": current_price,
            "quantity": 10,  # Fixed quantity for demo
            "strategy_confidence": strategy["confidence"],
            "reason": strategy["reason"],
            "stop_loss": current_price * (1 + strategy["stop_loss"]),
            "take_profit": current_price * (1 + strategy["take_profit"])
        }
        
        print(f"   ✅ Trade Executed:")
        print(f"      {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
        print(f"      Stop Loss: ${trade['stop_loss']:.2f}")
        print(f"      Take Profit: ${trade['take_profit']:.2f}")
        
        # Store trade
        self.session_data["trades"].append(trade)
        self.session_data["strategies"].append(strategy)
        
        return trade
    
    def simulate_market_movement(self, trade):
        """Simulate market movement and P&L"""
        if not trade:
            return
        
        print("\n📈 Simulating Market Movement...")
        print("-" * 50)
        
        # Simulate price movement based on strategy confidence
        confidence = trade["strategy_confidence"]
        base_movement = 0.02  # 2% base movement
        
        # Add some randomness
        import random
        random.seed(int(time.time()))
        random_factor = random.uniform(-0.5, 1.5)
        
        # Calculate price movement
        if trade["action"] == "BUY":
            movement = base_movement * confidence * random_factor
        else:  # SELL (short)
            movement = -base_movement * confidence * random_factor
        
        new_price = trade["price"] * (1 + movement)
        pnl = (new_price - trade["price"]) * trade["quantity"]
        if trade["action"] == "SELL":
            pnl = -pnl  # Reverse for short positions
        
        # Update performance
        self.session_data["performance"]["total_pnl"] += pnl
        self.session_data["performance"]["trades"] += 1
        if pnl > 0:
            self.session_data["performance"]["wins"] += 1
        
        print(f"   📊 Price moved from ${trade['price']:.2f} to ${new_price:.2f}")
        print(f"   💰 P&L: ${pnl:.2f} ({pnl/trade['price']/trade['quantity']*100:+.2f}%)")
        
        # Check if stop loss or take profit hit
        if trade["action"] == "BUY":
            if new_price <= trade["stop_loss"]:
                print("   🛑 Stop Loss triggered!")
            elif new_price >= trade["take_profit"]:
                print("   🎯 Take Profit hit!")
        else:  # SELL
            if new_price >= trade["stop_loss"]:
                print("   🛑 Stop Loss triggered!")
            elif new_price <= trade["take_profit"]:
                print("   🎯 Take Profit hit!")
    
    def show_performance_summary(self):
        """Show performance summary"""
        print("\n📊 PERFORMANCE SUMMARY")
        print("-" * 50)
        
        perf = self.session_data["performance"]
        session_duration = datetime.now() - self.session_data["start_time"]
        
        print(f"💰 Total P&L: ${perf['total_pnl']:.2f}")
        print(f"📈 Total Trades: {perf['trades']}")
        if perf['trades'] > 0:
            win_rate = (perf['wins'] / perf['trades']) * 100
            print(f"🏆 Win Rate: {win_rate:.1f}%")
            avg_pnl = perf['total_pnl'] / perf['trades']
            print(f"📊 Average P&L per Trade: ${avg_pnl:.2f}")
        
        print(f"⏱️  Session Duration: {session_duration}")
        print(f"🤖 Strategies Generated: {len(self.session_data['strategies'])}")
        
        # Recent trades
        if self.session_data["trades"]:
            print(f"\n📈 Recent Trades:")
            for trade in self.session_data["trades"][-3:]:
                print(f"   {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
    
    def run_full_demo(self):
        """Run the complete demo sequence"""
        print("🚀 Running Full Trading Demo...")
        print("=" * 50)
        
        # Step 1: Get market data
        market_data = self.get_market_data()
        time.sleep(1)
        
        # Step 2: Analyze sentiment
        sentiment = self.analyze_market_sentiment(market_data)
        time.sleep(1)
        
        # Step 3: Generate strategy
        strategy = self.generate_trading_strategy(market_data, sentiment)
        time.sleep(1)
        
        # Step 4: Execute trade
        trade = self.simulate_trade_execution(strategy)
        time.sleep(1)
        
        # Step 5: Simulate market movement
        self.simulate_market_movement(trade)
        time.sleep(1)
        
        # Step 6: Show performance
        self.show_performance_summary()
        
        print("\n✅ Demo complete! This shows the basic flow of the autonomous trading system.")
        print("   In the full system, this would be enhanced with:")
        print("   - Real Alpaca paper trading integration")
        print("   - OpenAI LLM for advanced strategy generation")
        print("   - Web research for alpha opportunities")
        print("   - Continuous monitoring and rebalancing")
        print("   - Advanced risk management")
    
    def interactive_menu(self):
        """Interactive menu"""
        while True:
            print("\n" + "="*50)
            print("🤖 ROBOINVEST DEMO MENU")
            print("="*50)
            print("1. 📊 Get Market Data")
            print("2. 🧠 Analyze Sentiment")
            print("3. 🤖 Generate Strategy")
            print("4. 💰 Execute Trade")
            print("5. 📈 Simulate Movement")
            print("6. 📊 Show Performance")
            print("7. 🚀 Run Full Demo")
            print("8. ❌ Exit")
            print("="*50)
            
            choice = input("\nSelect an option (1-8): ").strip()
            
            if choice == "1":
                self.get_market_data()
            elif choice == "2":
                market_data = self.get_market_data()
                self.analyze_market_sentiment(market_data)
            elif choice == "3":
                market_data = self.get_market_data()
                sentiment = self.analyze_market_sentiment(market_data)
                self.generate_trading_strategy(market_data, sentiment)
            elif choice == "4":
                market_data = self.get_market_data()
                sentiment = self.analyze_market_sentiment(market_data)
                strategy = self.generate_trading_strategy(market_data, sentiment)
                self.simulate_trade_execution(strategy)
            elif choice == "5":
                if self.session_data["trades"]:
                    self.simulate_market_movement(self.session_data["trades"][-1])
                else:
                    print("❌ No trades to simulate. Execute a trade first.")
            elif choice == "6":
                self.show_performance_summary()
            elif choice == "7":
                self.run_full_demo()
            elif choice == "8":
                print("\n👋 Thanks for trying RoboInvest! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-8.")
    
    def run(self):
        """Main entry point"""
        self.print_banner()
        
        # Check if we have basic dependencies
        try:
            import yfinance
            print("✅ Dependencies loaded successfully!")
        except ImportError:
            print("❌ Missing dependencies. Please install: pip install yfinance pandas numpy")
            return
        
        # Show quick market overview
        self.get_market_data()
        
        # Start interactive menu
        self.interactive_menu()


def main():
    """Main function"""
    try:
        demo = SimpleTradingDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 