#!/usr/bin/env python3
"""
Test script to generate sample alpha opportunities with buy/exit conditions.
"""

import asyncio
import json
from datetime import datetime
from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent

async def generate_test_alpha_opportunities():
    """Generate test alpha opportunities with buy/exit conditions."""
    
    # Create a test agent
    agent = EnhancedAutonomousAgent("test_agent", "alpha_hunting")
    
    # Sample insights that should generate alpha opportunities
    test_insights = [
        {
            "competitive_edge": "SPY momentum divergence with volume - potential reversal signal",
            "actionable_steps": ["Monitor volume patterns", "Set alert at $620 support"],
            "timeline": "1-3 days",
            "risk_factors": ["Market volatility", "False breakout"],
            "validated_confidence": 0.75,
            "priority": "high"
        },
        {
            "competitive_edge": "Tech sector rotation into defensive stocks - risk-off sentiment",
            "actionable_steps": ["Reduce tech exposure", "Increase defensive positions"],
            "timeline": "1-2 weeks",
            "risk_factors": ["Sector rotation reversal", "Market recovery"],
            "validated_confidence": 0.68,
            "priority": "medium"
        },
        {
            "competitive_edge": "Retail vs institutional sentiment divergence",
            "actionable_steps": ["Short retail favorites", "Long institutional picks"],
            "timeline": "3-5 days",
            "risk_factors": ["Sentiment convergence", "Market shock"],
            "validated_confidence": 0.82,
            "priority": "high"
        }
    ]
    
    # Generate alpha opportunities with buy/exit conditions
    opportunities = agent._extract_competitive_edges(test_insights)
    
    print("🎯 Generated Alpha Opportunities with Buy/Exit Conditions:")
    print("=" * 80)
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['opportunity']}")
        print(f"   Confidence: {opp['confidence']:.0%}")
        print(f"   Priority: {opp['priority'].upper()}")
        print(f"   Timeline: {opp['timeline']}")
        
        print(f"\n   📈 Buy Conditions:")
        for condition in opp['buy_conditions']:
            print(f"      • {condition}")
        
        print(f"\n   🚪 Exit Conditions:")
        for condition in opp['exit_conditions']:
            print(f"      • {condition}")
        
        print(f"\n   📊 Risk Management:")
        print(f"      • Stop Loss: {opp['stop_loss']}")
        print(f"      • Take Profit: {opp['take_profit']}")
        print(f"      • Position Sizing: {opp['position_sizing']}")
        
        print(f"\n   ⚠️  Risk Factors:")
        for risk in opp['risk_factors']:
            print(f"      • {risk}")
        
        print("-" * 80)
    
    # Save to file for API testing
    test_data = {
        "opportunities": opportunities,
        "generated_at": datetime.now().isoformat(),
        "total_opportunities": len(opportunities)
    }
    
    with open("test_alpha_opportunities.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n✅ Generated {len(opportunities)} alpha opportunities")
    print("📁 Saved to test_alpha_opportunities.json")
    
    return opportunities

if __name__ == "__main__":
    asyncio.run(generate_test_alpha_opportunities()) 