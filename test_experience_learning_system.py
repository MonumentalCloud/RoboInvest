#!/usr/bin/env python3
"""
Test script for the Experience Learning System
Tests the comprehensive experience learning and performance analysis functionality
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from agents.experience_learning_system import experience_learning_system
from agents.performance_analyzer_agent import performance_analyzer_agent
from agents.enhanced_trade_executor import enhanced_trade_executor
from utils.logger import logger


def create_sample_play_data() -> Dict[str, Any]:
    """Create sample play data for testing."""
    
    # Create sample trades
    trades = [
        {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 1,
            "price": 150.00,
            "pnl": 5.50,
            "confidence": 0.75,
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
        },
        {
            "symbol": "MSFT",
            "action": "SELL",
            "quantity": 1,
            "price": 320.00,
            "pnl": -2.30,
            "confidence": 0.65,
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat()
        },
        {
            "symbol": "GOOGL",
            "action": "BUY",
            "quantity": 1,
            "price": 2800.00,
            "pnl": 15.20,
            "confidence": 0.85,
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    # Create sample performance metrics
    performance = {
        "total_pnl": 18.40,
        "win_rate": 66.67,
        "sharpe_ratio": 1.25,
        "max_drawdown": 2.30,
        "total_trades": 3,
        "winning_trades": 2,
        "losing_trades": 1
    }
    
    # Create sample context
    context = {
        "market_conditions": "bullish",
        "volatility": "medium",
        "sector_performance": "technology_leading",
        "news_sentiment": "positive",
        "strategy_used": "momentum_based",
        "risk_parameters": {
            "max_position_size": 1000,
            "stop_loss_percentage": 5.0,
            "take_profit_percentage": 10.0
        }
    }
    
    return {
        "play_id": f"test_play_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "trades": trades,
        "performance": performance,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }


async def test_experience_learning_system():
    """Test the experience learning system."""
    
    print("🧪 Testing Experience Learning System")
    print("=" * 50)
    
    # Test 1: Create and analyze sample play data
    print("\n1. Creating sample play data...")
    play_data = create_sample_play_data()
    print(f"   ✅ Created play data with {len(play_data['trades'])} trades")
    
    # Test 2: Analyze and store experience
    print("\n2. Analyzing and storing experience...")
    try:
        experience_result = await experience_learning_system.analyze_and_store_experience(play_data)
        print(f"   ✅ Experience analysis completed")
        print(f"   📊 Analysis insights: {len(experience_result.get('analysis', {}).get('insights', []))}")
        print(f"   🤖 Agent feedback: {len(experience_result.get('agent_feedback', {}))}")
    except Exception as e:
        print(f"   ❌ Experience analysis failed: {e}")
        return
    
    # Test 3: Performance analysis
    print("\n3. Running performance analysis...")
    try:
        performance_result = await performance_analyzer_agent(play_data)
        print(f"   ✅ Performance analysis completed")
        print(f"   📈 Overall rating: {performance_result.get('performance_analysis', {}).get('performance_summary', {}).get('overall_rating', 'unknown')}")
        print(f"   🎯 Actionable insights: {len(performance_result.get('performance_analysis', {}).get('actionable_insights', []))}")
    except Exception as e:
        print(f"   ❌ Performance analysis failed: {e}")
    
    # Test 4: Get agent experience
    print("\n4. Testing agent experience retrieval...")
    try:
        agent_experience = experience_learning_system.get_agent_experience("enhanced_trade_executor")
        print(f"   ✅ Agent experience retrieved")
        print(f"   📚 Shared experiences: {len(agent_experience.get('shared_experiences', []))}")
        print(f"   💡 Relevant insights: {len(agent_experience.get('relevant_insights', []))}")
    except Exception as e:
        print(f"   ❌ Agent experience retrieval failed: {e}")
    
    # Test 5: Get system insights
    print("\n5. Testing system insights...")
    try:
        system_insights = experience_learning_system.get_system_insights()
        print(f"   ✅ System insights retrieved")
        print(f"   🧠 Insights: {len(system_insights.get('insights', []))}")
        print(f"   📖 Lessons learned: {len(system_insights.get('lessons_learned', []))}")
    except Exception as e:
        print(f"   ❌ System insights retrieval failed: {e}")
    
    # Test 6: Enhanced trade executor learning
    print("\n6. Testing enhanced trade executor learning...")
    try:
        learning_insights = await enhanced_trade_executor.get_learning_insights()
        print(f"   ✅ Learning insights retrieved")
        print(f"   📊 Execution stats: {learning_insights.get('execution_stats', {})}")
        print(f"   🎯 Learning focus: {learning_insights.get('learning_focus', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Learning insights retrieval failed: {e}")
    
    # Test 7: Performance trends
    print("\n7. Testing performance trends...")
    try:
        trends = performance_analyzer_agent.get_performance_trends()
        print(f"   ✅ Performance trends retrieved")
        print(f"   📈 Overall trend: {trends.get('overall_trend', 'unknown')}")
        print(f"   📊 Sample size: {trends.get('sample_size', 0)}")
    except Exception as e:
        print(f"   ❌ Performance trends retrieval failed: {e}")
    
    # Test 8: Analysis history
    print("\n8. Testing analysis history...")
    try:
        history = performance_analyzer_agent.get_analysis_history(limit=5)
        print(f"   ✅ Analysis history retrieved")
        print(f"   📜 History entries: {len(history)}")
    except Exception as e:
        print(f"   ❌ Analysis history retrieval failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Experience Learning System Test Completed!")
    print("\nKey Features Tested:")
    print("  • Experience analysis and storage")
    print("  • Performance analysis with AI insights")
    print("  • Agent-specific experience retrieval")
    print("  • System-wide insights and lessons")
    print("  • Performance trend analysis")
    print("  • Learning insights for agents")
    print("  • Analysis history tracking")


async def test_multiple_plays():
    """Test with multiple plays to build up experience."""
    
    print("\n🧪 Testing Multiple Plays for Experience Building")
    print("=" * 50)
    
    # Create multiple sample plays
    plays = []
    for i in range(3):
        play_data = create_sample_play_data()
        play_data["play_id"] = f"multi_test_play_{i+1}"
        plays.append(play_data)
    
    print(f"Created {len(plays)} sample plays")
    
    # Analyze each play
    for i, play_data in enumerate(plays, 1):
        print(f"\nAnalyzing play {i}...")
        try:
            # Analyze experience
            await experience_learning_system.analyze_and_store_experience(play_data)
            
            # Analyze performance
            await performance_analyzer_agent(play_data)
            
            print(f"   ✅ Play {i} analyzed successfully")
        except Exception as e:
            print(f"   ❌ Play {i} analysis failed: {e}")
    
    # Test experience retrieval after multiple plays
    print("\nTesting experience retrieval after multiple plays...")
    try:
        agent_experience = experience_learning_system.get_agent_experience("enhanced_trade_executor")
        system_insights = experience_learning_system.get_system_insights()
        trends = performance_analyzer_agent.get_performance_trends()
        
        print(f"   ✅ Agent experiences: {len(agent_experience.get('shared_experiences', []))}")
        print(f"   ✅ System insights: {len(system_insights.get('insights', []))}")
        print(f"   ✅ Performance trend: {trends.get('overall_trend', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Experience retrieval failed: {e}")


async def main():
    """Main test function."""
    
    print("🚀 Starting Experience Learning System Tests")
    print("=" * 60)
    
    # Test basic functionality
    await test_experience_learning_system()
    
    # Test multiple plays
    await test_multiple_plays()
    
    print("\n" + "=" * 60)
    print("🎉 All Experience Learning System Tests Completed!")
    print("\nThe system is now ready to:")
    print("  • Analyze every play/performance automatically")
    print("  • Store comprehensive learning insights")
    print("  • Provide agent-specific feedback")
    print("  • Track performance trends over time")
    print("  • Enable continuous system improvement")


if __name__ == "__main__":
    asyncio.run(main()) 