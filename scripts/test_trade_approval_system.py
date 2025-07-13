#!/usr/bin/env python3
"""
Test script for the Trade Approval Agent system.
Demonstrates how the system filters trades based on risk/reward analysis.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.trade_approval_agent import trade_approval_agent, ApprovalDecision, RiskRewardProfile
from agents.enhanced_trade_executor import enhanced_trade_executor
from core.structured_order import StructuredOrder, TradingPlay, SWOTAnalysis, RiskAssessment, StopConditions, OrderType, RiskLevel
from utils.logger import logger

async def test_trade_approval_scenarios():
    """Test different trade scenarios to see how the approval agent filters them"""
    
    logger.info("🧪 Testing Trade Approval Agent with different scenarios...")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Low Risk, Low Reward",
            "risk_score": 0.3,
            "confidence": 0.6,
            "swot_score": 0.2,
            "quantity": 10,
            "expected_decision": ApprovalDecision.AUTO_REJECT
        },
        {
            "name": "Low Risk, High Reward",
            "risk_score": 0.3,
            "confidence": 0.8,
            "swot_score": 0.8,
            "quantity": 50,
            "expected_decision": ApprovalDecision.AUTO_APPROVE
        },
        {
            "name": "High Risk, Low Reward",
            "risk_score": 0.7,
            "confidence": 0.5,
            "swot_score": 0.3,
            "quantity": 100,
            "expected_decision": ApprovalDecision.AUTO_REJECT
        },
        {
            "name": "High Risk, High Reward",
            "risk_score": 0.7,
            "confidence": 0.7,
            "swot_score": 0.8,
            "quantity": 75,
            "expected_decision": ApprovalDecision.REQUEST_PERMISSION
        },
        {
            "name": "Extreme Risk, High Reward",
            "risk_score": 0.9,
            "confidence": 0.8,
            "swot_score": 0.9,
            "quantity": 200,
            "expected_decision": ApprovalDecision.REQUEST_PERMISSION
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios):
        logger.info(f"\n📊 Testing Scenario {i+1}: {scenario['name']}")
        
        # Create a test structured order
        structured_order = create_test_structured_order(
            symbol="SPY",
            side="buy",
            quantity=scenario["quantity"],
            risk_score=scenario["risk_score"],
            confidence=scenario["confidence"],
            swot_score=scenario["swot_score"]
        )
        
        # Test market data
        market_data = {
            "price": 450.0,
            "volatility": 0.2,
            "trend": "neutral",
            "volume": 1000000
        }
        
        # Test alpha insights
        alpha_insights = {
            "confidence": scenario["confidence"],
            "strength": scenario["swot_score"],
            "type": "momentum_breakout",
            "catalyst": "earnings_beat",
            "timeframe": "1-3 days"
        }
        
        # Get approval analysis
        analysis = await trade_approval_agent.analyze_trade_for_approval(
            structured_order, market_data, alpha_insights
        )
        
        # Check if decision matches expectation
        decision_correct = analysis.decision == scenario["expected_decision"]
        
        result = {
            "scenario": scenario["name"],
            "expected_decision": scenario["expected_decision"].value,
            "actual_decision": analysis.decision.value,
            "correct": decision_correct,
            "risk_reward_profile": analysis.risk_reward_profile.value,
            "reasoning": analysis.reasoning,
            "risk_score": analysis.risk_score,
            "reward_potential": analysis.reward_potential
        }
        
        results.append(result)
        
        # Log the result
        status_emoji = "✅" if decision_correct else "❌"
        logger.info(f"{status_emoji} Decision: {analysis.decision.value}")
        logger.info(f"   Risk-Reward Profile: {analysis.risk_reward_profile.value}")
        logger.info(f"   Reasoning: {analysis.reasoning}")
        logger.info(f"   Risk Score: {analysis.risk_score:.2f}")
        logger.info(f"   Reward Potential: {analysis.reward_potential:.1%}")
        
        if analysis.decision == ApprovalDecision.REQUEST_PERMISSION:
            logger.info(f"   📧 Would send approval email")
    
    # Summary
    logger.info(f"\n📈 Test Results Summary:")
    correct_decisions = sum(1 for r in results if r["correct"])
    total_scenarios = len(results)
    
    logger.info(f"   Correct Decisions: {correct_decisions}/{total_scenarios} ({correct_decisions/total_scenarios*100:.1f}%)")
    
    for result in results:
        status = "✅" if result["correct"] else "❌"
        logger.info(f"   {status} {result['scenario']}: {result['actual_decision']} (expected: {result['expected_decision']})")
    
    # Test approval statistics
    stats = trade_approval_agent.get_approval_statistics()
    logger.info(f"\n📊 Approval Statistics:")
    logger.info(f"   Total Decisions: {stats['total_decisions']}")
    logger.info(f"   Auto-approve Rate: {stats.get('auto_approve_rate', 0):.1%}")
    logger.info(f"   Auto-reject Rate: {stats.get('auto_reject_rate', 0):.1%}")
    logger.info(f"   Permission Request Rate: {stats.get('permission_request_rate', 0):.1%}")
    
    return results

def create_test_structured_order(symbol: str, side: str, quantity: int, 
                               risk_score: float, confidence: float, swot_score: float) -> StructuredOrder:
    """Create a test structured order with specified parameters"""
    
    from core.structured_order import OrderManager, OrderType, OrderStatus
    
    # Create trading play
    play = TradingPlay(
        play_id=f"test_play_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        title=f"Test {symbol} {side.upper()} Play",
        description=f"Test trading play for {symbol}",
        thesis="This is a test play for demonstration purposes",
        catalyst="Test catalyst",
        timeframe="1-3 days",
        entry_strategy="Market order",
        exit_strategy="Take profit or stop loss",
        key_risks=["Market volatility", "Liquidity risk"],
        key_metrics={"pe": 15.5, "pb": 1.2},
        research_sources=["Test analysis"],
        analyst_notes="Test notes",
        market_context="Test market context",
        sector_analysis="Test sector analysis",
        technical_analysis="Test technical analysis",
        fundamental_analysis="Test fundamental analysis",
        sentiment_analysis="Test sentiment analysis",
        created_by="test_script",
        created_at=datetime.utcnow()
    )
    
    # Create SWOT analysis
    swot_analysis = SWOTAnalysis(
        strengths=["Strong momentum", "Good fundamentals"],
        weaknesses=["High volatility"],
        opportunities=["Earnings catalyst"],
        threats=["Market correction"],
        overall_score=swot_score,
        confidence=confidence
    )
    
    # Create risk assessment
    risk_assessment = RiskAssessment(
        risk_level=RiskLevel.HIGH if risk_score > 0.6 else RiskLevel.MEDIUM if risk_score > 0.3 else RiskLevel.LOW,
        max_loss_amount=quantity * 450 * 0.1,  # 10% max loss
        max_loss_percentage=10.0,
        var_95=quantity * 450 * 0.05,  # 5% VaR
        sharpe_ratio=1.2,
        beta=1.0,
        volatility=0.2,
        correlation_with_spy=0.8,
        sector_risk=0.3,
        market_timing_risk=0.4,
        liquidity_risk=0.2,
        overall_risk_score=risk_score
    )
    
    # Create stop conditions
    stop_conditions = StopConditions(
        stop_loss_price=450 * 0.95,  # 5% stop loss
        stop_loss_percentage=5.0,
        take_profit_price=450 * 1.1,  # 10% take profit
        take_profit_percentage=10.0,
        trailing_stop_percentage=3.0,
        time_based_stop=None,
        max_holding_period=None
    )
    
    # Create structured order
    order = StructuredOrder(
        order_id=f"test_order_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        symbol=symbol,
        side=side,
        order_type=OrderType.MARKET,
        quantity=quantity,
        price=450.0,
        status=OrderStatus.PENDING_ANALYSIS,
        play=play,
        swot_analysis=swot_analysis,
        risk_assessment=risk_assessment,
        stop_conditions=stop_conditions,
        confidence_score=confidence,
        priority=5,
        tags=["test", "approval_agent"],
        notes="Test order for approval agent",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        submitted_at=None,
        filled_at=None,
        cancelled_at=None,
        alpaca_order_id=None,
        fill_price=None,
        commission=None,
        realized_pnl=None
    )
    
    return order

async def test_pending_approvals():
    """Test the pending approvals functionality"""
    
    logger.info("\n📋 Testing Pending Approvals System...")
    
    # Get current pending approvals
    pending = enhanced_trade_executor.get_pending_approvals()
    logger.info(f"   Current pending approvals: {len(pending)}")
    
    for approval in pending:
        logger.info(f"   - {approval['symbol']} {approval['side'].upper()} {approval['quantity']} shares")
        logger.info(f"     Play: {approval['play_title']}")
        logger.info(f"     Requested: {approval['requested_at']}")

async def main():
    """Main test function"""
    
    logger.info("🚀 Starting Trade Approval Agent Test Suite")
    logger.info("=" * 60)
    
    # Test approval scenarios
    results = await test_trade_approval_scenarios()
    
    # Test pending approvals
    await test_pending_approvals()
    
    logger.info("\n🎉 Trade Approval Agent Test Suite Complete!")
    logger.info("=" * 60)
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 