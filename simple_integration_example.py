"""
Simple Integration Example: How to Use AI Risk Management in Your Trading System
This shows the minimal code needed to integrate risk assessment into your trading workflow.
"""

from core.ai_risk_monitor_improved import improved_ai_risk_monitor


def your_trading_strategy():
    """
    Example of how your existing trading strategy would integrate the risk system.
    """
    print("🤖 AI TRADING STRATEGY WITH RISK MANAGEMENT")
    print("=" * 55)
    
    # Step 1: Your strategy generates a trading decision
    print("\n1️⃣ STRATEGY GENERATES DECISION")
    strategy_decision = {
        "primary_ticker": "AAPL",
        "action": "BUY",
        "confidence": 0.82,          # Your AI's confidence score
        "position_size": 0.15,       # 15% of portfolio
        "strategy_name": "earnings_momentum",
        "market_volatility": "medium",
        "research_source_count": 4
    }
    
    print(f"   Original Decision: {strategy_decision['action']} {strategy_decision['primary_ticker']}")
    print(f"   Position Size: {strategy_decision['position_size']:.1%}")
    print(f"   Confidence: {strategy_decision['confidence']:.1%}")
    
    # Step 2: Run risk assessment (JUST ONE LINE!)
    print("\n2️⃣ RISK ASSESSMENT")
    risk_result = improved_ai_risk_monitor.check_trading_decision(strategy_decision)
    
    # Step 3: Use the result to decide whether to proceed
    print("\n3️⃣ RISK-ADJUSTED DECISION")
    if risk_result['should_proceed']:
        # Use risk-adjusted parameters
        final_decision = risk_result['mitigated_context']
        print(f"   ✅ EXECUTING TRADE")
        print(f"   Final Action: {final_decision['action']}")
        print(f"   Final Position: {final_decision.get('position_size', 0):.1%}")
        print(f"   Risk Level: {risk_result['risk_summary']['level']}")
        
        # Here you would call your broker API
        # execute_trade(final_decision)
        
    else:
        print(f"   ❌ TRADE BLOCKED")
        print(f"   Risk Level: {risk_result['risk_summary']['level']}")
        print(f"   Reason: Risk too high for automated execution")
        
        # Here you might log for human review
        # log_for_human_review(strategy_decision, risk_result)


def batch_risk_checking():
    """
    Example of checking multiple trades at once (useful for portfolio rebalancing).
    """
    print("\n\n🔄 BATCH RISK CHECKING EXAMPLE")
    print("=" * 55)
    
    # Multiple trading ideas from your strategy
    trade_ideas = [
        {"primary_ticker": "NVDA", "action": "BUY", "confidence": 0.75, "position_size": 0.10},
        {"primary_ticker": "TSLA", "action": "SELL", "confidence": 0.65, "position_size": 0.08},
        {"primary_ticker": "MSFT", "action": "BUY", "confidence": 0.88, "position_size": 0.12},
    ]
    
    approved_trades = []
    
    for trade in trade_ideas:
        result = improved_ai_risk_monitor.check_trading_decision(trade)
        
        print(f"\n📊 {trade['primary_ticker']}: {result['risk_summary']['level']} risk")
        
        if result['should_proceed']:
            approved_trades.append(result['mitigated_context'])
            print(f"   ✅ Approved")
        else:
            print(f"   ❌ Rejected")
    
    print(f"\n📈 Summary: {len(approved_trades)}/{len(trade_ideas)} trades approved")
    return approved_trades


def real_time_monitoring_example():
    """
    Example of how to monitor your system's risk in real-time.
    """
    print("\n\n📊 REAL-TIME MONITORING EXAMPLE")
    print("=" * 55)
    
    # Get current system status
    risk_summary = improved_ai_risk_monitor.get_risk_summary()
    
    print(f"System Status: {risk_summary.get('monitoring_status', 'unknown')}")
    print(f"Current Risk Level: {risk_summary.get('current_risk_level', 'N/A')}")
    print(f"Recent Assessments: {risk_summary.get('assessments_last_hour', 0)}")
    print(f"High-Risk Events: {risk_summary.get('high_risk_events', 0)}")
    
    # You could set up alerts based on these metrics
    if risk_summary.get('high_risk_events', 0) > 3:
        print("🚨 ALERT: Multiple high-risk events detected!")
        # send_alert_to_risk_team()


def customize_for_your_strategy():
    """
    Example of how to customize risk thresholds for different strategies.
    """
    print("\n\n⚙️  CUSTOMIZATION EXAMPLE")
    print("=" * 55)
    
    # You can create different risk monitors for different strategies
    # (This would require modifying the ImprovedAIRiskMonitor class to accept custom thresholds)
    
    print("For a Conservative Strategy:")
    print("   • Max position size: 5%")
    print("   • Min confidence: 80%")
    print("   • Strict compliance checks")
    
    print("\nFor an Aggressive Strategy:")
    print("   • Max position size: 20%")
    print("   • Min confidence: 50%")
    print("   • Relaxed thresholds")
    
    print("\nFor a High-Frequency Strategy:")
    print("   • Max position size: 2%")
    print("   • Min confidence: 60%")
    print("   • Enhanced security monitoring")


if __name__ == "__main__":
    print("🚀 SIMPLE INTEGRATION EXAMPLES")
    print("This shows exactly how to use the risk system in your code.\n")
    
    # Run all examples
    your_trading_strategy()
    batch_risk_checking()
    real_time_monitoring_example()
    customize_for_your_strategy()
    
    print("\n" + "=" * 55)
    print("✨ That's it! The risk system is ready to use.")
    print("Just import it and call check_trading_decision() before executing trades.")