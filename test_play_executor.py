#!/usr/bin/env python3
"""
Test script for the Play Executor Agent.
Demonstrates natural language play parsing, execution, and intelligent intervention.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from agents.play_executor import play_executor, PlayStatus, InterventionType
from utils.logger import logger


def create_sample_market_data(symbol: str, price: float, change_pct: float, volume_ratio: float = 1.0) -> Dict[str, Any]:
    """Create sample market data for testing"""
    return {
        "price": price,
        "change_pct": change_pct,
        "volume": int(1000000 * volume_ratio),
        "avg_volume": 1000000,
        "pe": 25.5,
        "pb": 2.1,
        "valuation": "fair",
        "historical_data": [
            {"close": price * 0.98, "date": "2024-01-01"},
            {"close": price * 0.99, "date": "2024-01-02"},
            {"close": price, "date": "2024-01-03"}
        ]
    }


def create_sample_news_data(sentiment: str = "neutral") -> list:
    """Create sample news data with specified sentiment"""
    if sentiment == "positive":
        return [
            "Tech stocks rally on strong earnings reports",
            "Analysts upgrade outlook for technology sector",
            "Trading volume surges as investors reposition portfolios",
            "Market sentiment turns bullish on Fed policy"
        ]
    elif sentiment == "negative":
        return [
            "Tech stocks decline on inflation concerns",
            "Analysts downgrade outlook for technology sector",
            "Trading volume drops as investors remain cautious",
            "Market sentiment turns bearish on economic data"
        ]
    else:
        return [
            "Tech stocks trade mixed as investors weigh options",
            "Analysts maintain neutral outlook for technology sector",
            "Trading volume remains steady",
            "Market sentiment remains cautious"
        ]


def test_natural_language_play_parsing():
    """Test natural language play parsing"""
    print("\n" + "="*60)
    print("🧠 TESTING NATURAL LANGUAGE PLAY PARSING")
    print("="*60)
    
    # Test different types of plays
    test_plays = [
        {
            "description": "Buy NVDA on momentum breakout above $500 with strong volume confirmation. Target $550, stop loss at $480. This is a short-term momentum play based on AI chip demand surge.",
            "symbol": "NVDA",
            "expected_side": "buy"
        },
        {
            "description": "Short TSLA on technical breakdown below $200 support level. Expecting further decline to $180. Stop loss at $220. This is a bearish technical play.",
            "symbol": "TSLA",
            "expected_side": "sell"
        },
        {
            "description": "Long-term position in AAPL ahead of earnings. Strong fundamentals and technical setup suggest 15% upside over 2-3 months. Conservative entry with tight risk management.",
            "symbol": "AAPL",
            "expected_side": "buy"
        }
    ]
    
    for i, test_play in enumerate(test_plays, 1):
        print(f"\n📋 Test Play {i}: {test_play['symbol']}")
        print(f"   Description: {test_play['description'][:100]}...")
        
        # Parse the play
        parsed_play = play_executor._parse_natural_language_play(
            test_play["description"], 
            test_play["symbol"]
        )
        
        print(f"   Parsed Results:")
        print(f"     Title: {parsed_play['title']}")
        print(f"     Side: {parsed_play['side']} (expected: {test_play['expected_side']})")
        print(f"     Timeframe: {parsed_play['timeframe']}")
        print(f"     Priority: {parsed_play['priority']}")
        print(f"     Tags: {parsed_play['tags']}")
        print(f"     Entry Strategy: {parsed_play['entry_strategy'][:80]}...")
        print(f"     Exit Strategy: {parsed_play['exit_strategy'][:80]}...")
        
        # Validate parsing
        if parsed_play['side'] == test_play['expected_side']:
            print(f"     ✅ Side correctly parsed")
        else:
            print(f"     ❌ Side parsing error")


def test_play_creation():
    """Test creating plays from natural language"""
    print("\n" + "="*60)
    print("🎯 TESTING PLAY CREATION")
    print("="*60)
    
    # Create a momentum play
    play_description = "Buy NVDA on momentum breakout above $500 with strong volume confirmation. Target $550, stop loss at $480. This is a short-term momentum play based on AI chip demand surge."
    symbol = "NVDA"
    initial_quantity = 5
    market_data = create_sample_market_data("NVDA", 510.0, 2.5, 1.5)
    news_data = create_sample_news_data("positive")
    
    print(f"📋 Creating Play:")
    print(f"   Symbol: {symbol}")
    print(f"   Description: {play_description[:100]}...")
    print(f"   Quantity: {initial_quantity}")
    print(f"   Current Price: ${market_data['price']}")
    
    # Create the play
    play = play_executor.create_play_from_natural_language(
        play_description=play_description,
        symbol=symbol,
        initial_quantity=initial_quantity,
        market_data=market_data,
        news_data=news_data,
        confidence_score=0.75
    )
    
    print(f"\n✅ Play Created:")
    print(f"   Play ID: {play['play_id']}")
    print(f"   Order ID: {play['order_id']}")
    print(f"   Status: {play['status'].value}")
    print(f"   Title: {play['parsed_play']['title']}")
    print(f"   Side: {play['parsed_play']['side']}")
    print(f"   Timeframe: {play['parsed_play']['timeframe']}")
    print(f"   Priority: {play['parsed_play']['priority']}")
    print(f"   Tags: {play['parsed_play']['tags']}")
    
    print(f"\n📊 Execution Plan:")
    execution_plan = play['execution_plan']
    print(f"   Phases: {len(execution_plan['phases'])}")
    for phase in execution_plan['phases']:
        print(f"     - {phase['phase']}: {phase['description']}")
    
    print(f"   Exit Triggers: {len(execution_plan['exit_triggers'])}")
    for trigger in execution_plan['exit_triggers']:
        print(f"     - {trigger['type']}: {trigger['condition']}")
    
    print(f"\n🔍 Monitoring Conditions:")
    monitoring = play['monitoring_conditions']
    print(f"   Price Monitoring: {len(monitoring['price_monitoring']['alert_thresholds'])} thresholds")
    print(f"   Volume Monitoring: {len(monitoring['volume_monitoring']['alert_thresholds'])} thresholds")
    print(f"   News Monitoring: {len(monitoring['news_monitoring']['alert_thresholds'])} thresholds")
    print(f"   Technical Monitoring: {len(monitoring['technical_monitoring']['alert_thresholds'])} thresholds")
    
    return play


def test_play_monitoring():
    """Test play monitoring and intervention"""
    print("\n" + "="*60)
    print("📊 TESTING PLAY MONITORING")
    print("="*60)
    
    # Create a play first
    play_description = "Buy AAPL on earnings momentum. Strong fundamentals suggest 10% upside. Stop loss at 5% below entry."
    symbol = "AAPL"
    initial_quantity = 10
    market_data = create_sample_market_data("AAPL", 150.0, 1.0)
    news_data = create_sample_news_data("positive")
    
    play = play_executor.create_play_from_natural_language(
        play_description=play_description,
        symbol=symbol,
        initial_quantity=initial_quantity,
        market_data=market_data,
        news_data=news_data,
        confidence_score=0.8
    )
    
    play_id = play['play_id']
    print(f"📋 Monitoring Play: {play_id}")
    print(f"   Initial Price: ${market_data['price']}")
    
    # Test different market scenarios
    scenarios = [
        {
            "name": "Positive Momentum",
            "market_data": create_sample_market_data("AAPL", 157.5, 5.0, 1.2),
            "expected_action": "adaptation"
        },
        {
            "name": "Stop Loss Hit",
            "market_data": create_sample_market_data("AAPL", 142.5, -5.0, 0.8),
            "expected_action": "intervention"
        },
        {
            "name": "Take Profit Hit",
            "market_data": create_sample_market_data("AAPL", 165.0, 10.0, 1.5),
            "expected_action": "intervention"
        },
        {
            "name": "Volume Anomaly",
            "market_data": create_sample_market_data("AAPL", 150.0, 0.0, 0.3),
            "expected_action": "intervention"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔄 Scenario {i}: {scenario['name']}")
        print(f"   Price: ${scenario['market_data']['price']} (Change: {scenario['market_data']['change_pct']:.1f}%)")
        print(f"   Volume Ratio: {scenario['market_data']['volume'] / scenario['market_data']['avg_volume']:.2f}")
        
        # Monitor the play
        result = play_executor.monitor_and_execute_play(play_id, scenario['market_data'])
        
        if 'error' in result:
            print(f"   Error: {result['error']}")
        else:
            print(f"   Result: {result['status']}")
        if 'intervention' in result:
            intervention = result['intervention']
            print(f"   Intervention: {intervention['type'].value}")
            print(f"   Reason: {intervention['reason']}")
            print(f"   Action: {intervention['action']}")
        
        if 'adaptation' in result:
            adaptation = result['adaptation']
            print(f"   Adaptation: {adaptation['type']}")
            print(f"   Reason: {adaptation['reason']}")
            print(f"   Action: {adaptation['action']}")
        
        # Get updated play summary
        summary = play_executor.get_play_summary(play_id)
        if summary:
            print(f"   Play Status: {summary['status']}")
            if 'pnl_pct' in summary['performance']:
                print(f"   P&L: {summary['performance']['pnl_pct']:.2%}")
            print(f"   Max Profit: {summary['performance']['max_profit']:.2%}")
            print(f"   Max Drawdown: {summary['performance']['max_drawdown']:.2%}")
            print(f"   Time in Play: {summary['performance']['time_in_play']:.1f} hours")
            print(f"   Interventions: {summary['interventions']}")
            print(f"   Adaptations: {summary['adaptations']}")


def test_multiple_plays():
    """Test managing multiple plays simultaneously"""
    print("\n" + "="*60)
    print("🎭 TESTING MULTIPLE PLAYS")
    print("="*60)
    
    # Create multiple plays
    plays = [
        {
            "description": "Momentum play on NVDA. Buy on breakout above $500, target $550.",
            "symbol": "NVDA",
            "quantity": 3
        },
        {
            "description": "Conservative position in SPY. Long-term bullish outlook with tight stops.",
            "symbol": "SPY",
            "quantity": 5
        },
        {
            "description": "Short-term swing trade on TSLA. Bearish technical setup, target $180.",
            "symbol": "TSLA",
            "quantity": 2
        }
    ]
    
    created_plays = []
    
    for i, play_config in enumerate(plays, 1):
        print(f"\n📋 Creating Play {i}: {play_config['symbol']}")
        
        market_data = create_sample_market_data(
            play_config['symbol'], 
            100.0 + i*50, 
            1.0 + i*0.5
        )
        news_data = create_sample_news_data("neutral")
        
        play = play_executor.create_play_from_natural_language(
            play_description=play_config['description'],
            symbol=play_config['symbol'],
            initial_quantity=play_config['quantity'],
            market_data=market_data,
            news_data=news_data,
            confidence_score=0.7
        )
        
        created_plays.append(play)
        print(f"   ✅ Created: {play['play_id']}")
    
    # Monitor all plays
    print(f"\n📊 Monitoring All Plays:")
    
    for play in created_plays:
        play_id = play['play_id']
        symbol = play['symbol']
        
        # Simulate different market conditions for each
        if symbol == "NVDA":
            market_data = create_sample_market_data("NVDA", 520.0, 4.0, 1.3)  # Positive momentum
        elif symbol == "SPY":
            market_data = create_sample_market_data("SPY", 450.0, -1.0, 0.7)   # Slight decline
        else:  # TSLA
            market_data = create_sample_market_data("TSLA", 190.0, -5.0, 1.1)  # Bearish move
        
        result = play_executor.monitor_and_execute_play(play_id, market_data)
        
        print(f"   {symbol}: {result['status']} - {result['play_status']}")
        
        if 'intervention' in result:
            print(f"     ⚠️  Intervention: {result['intervention']['type'].value}")
        elif 'adaptation' in result:
            print(f"     🔄 Adaptation: {result['adaptation']['type']}")
    
    # Get summary of all plays
    print(f"\n📈 All Plays Summary:")
    summary = play_executor.get_all_plays_summary()
    
    print(f"   Active Plays: {summary['statistics']['total_active']}")
    print(f"   Historical Plays: {summary['statistics']['total_historical']}")
    print(f"   Average Performance: {summary['statistics']['average_performance']:.2%}")
    print(f"   Success Rate: {summary['statistics']['success_rate']:.1%}")
    
    print(f"\n📋 Active Play Details:")
    for play_summary in summary['active_plays']:
        if play_summary:
            pnl = play_summary['performance'].get('pnl_pct', 0) if play_summary['performance'] else 0
            print(f"   {play_summary['symbol']}: {play_summary['status']} - P&L: {pnl:.2%}")


def test_intervention_scenarios():
    """Test specific intervention scenarios"""
    print("\n" + "="*60)
    print("⚠️  TESTING INTERVENTION SCENARIOS")
    print("="*60)
    
    # Test different intervention types
    intervention_tests = [
        {
            "name": "Stop Loss Intervention",
            "description": "Buy MSFT on technical breakout. Stop loss at 5% below entry.",
            "symbol": "MSFT",
            "initial_price": 300.0,
            "scenario_price": 285.0,  # 5% below entry
            "expected_intervention": InterventionType.STOP_LOSS_HIT
        },
        {
            "name": "Take Profit Intervention",
            "description": "Buy GOOGL on momentum. Take profit at 10% above entry.",
            "symbol": "GOOGL",
            "initial_price": 140.0,
            "scenario_price": 154.0,  # 10% above entry
            "expected_intervention": InterventionType.TAKE_PROFIT_HIT
        },
        {
            "name": "Volume Anomaly Intervention",
            "description": "Buy META on earnings. Monitor volume for confirmation.",
            "symbol": "META",
            "initial_price": 200.0,
            "scenario_price": 200.0,
            "volume_ratio": 0.3,  # 30% of average volume
            "expected_intervention": InterventionType.VOLUME_ANOMALY
        }
    ]
    
    for test in intervention_tests:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   Description: {test['description']}")
        print(f"   Symbol: {test['symbol']}")
        print(f"   Initial Price: ${test['initial_price']}")
        print(f"   Scenario Price: ${test['scenario_price']}")
        
        # Create the play
        market_data = create_sample_market_data(
            test['symbol'], 
            test['initial_price'], 
            0.0
        )
        news_data = create_sample_news_data("neutral")
        
        play = play_executor.create_play_from_natural_language(
            play_description=test['description'],
            symbol=test['symbol'],
            initial_quantity=5,
            market_data=market_data,
            news_data=news_data,
            confidence_score=0.7
        )
        
        play_id = play['play_id']
        
        # Create scenario market data
        scenario_market_data = create_sample_market_data(
            test['symbol'],
            test['scenario_price'],
            ((test['scenario_price'] - test['initial_price']) / test['initial_price']) * 100,
            test.get('volume_ratio', 1.0)
        )
        
        # Monitor and check for intervention
        result = play_executor.monitor_and_execute_play(play_id, scenario_market_data)
        
        print(f"   Result: {result['status']}")
        
        if 'intervention' in result:
            intervention = result['intervention']
            print(f"   Intervention Type: {intervention['type'].value}")
            print(f"   Expected Type: {test['expected_intervention'].value}")
            
            if intervention['type'] == test['expected_intervention']:
                print(f"   ✅ Correct intervention detected")
            else:
                print(f"   ❌ Unexpected intervention type")
            
            print(f"   Reason: {intervention['reason']}")
            print(f"   Action: {intervention['action']}")
        else:
            print(f"   ⚠️  No intervention detected (expected: {test['expected_intervention'].value})")


def main():
    """Run all tests"""
    print("🎭 PLAY EXECUTOR SYSTEM TEST")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all tests
        test_natural_language_play_parsing()
        test_play_creation()
        test_play_monitoring()
        test_multiple_plays()
        test_intervention_scenarios()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("🎯 Key Features Demonstrated:")
        print("   • Natural language play parsing")
        print("   • Complex play execution planning")
        print("   • Intelligent monitoring and intervention")
        print("   • Multiple play management")
        print("   • Risk-based intervention scenarios")
        print("   • Performance tracking and adaptation")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 