#!/usr/bin/env python3
"""
Test script for the new structured order system.
Demonstrates SWOT analysis, risk assessment, and comprehensive order management.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from core.structured_order import OrderStatus, OrderType, RiskLevel
from agents.enhanced_trade_executor import enhanced_trade_executor
from agents.swot_analyzer import swot_analyzer
from agents.risk_assessor import risk_assessor
from utils.logger import logger


def create_sample_market_data(symbol: str, price: float, change_pct: float) -> Dict[str, Any]:
    """Create sample market data for testing"""
    return {
        "price": price,
        "change_pct": change_pct,
        "volume": 1000000,
        "avg_volume": 1200000,
        "pe": 25.5,
        "pb": 2.1,
        "valuation": "fair",
        "historical_data": [
            {"close": price * 0.98, "date": "2024-01-01"},
            {"close": price * 0.99, "date": "2024-01-02"},
            {"close": price, "date": "2024-01-03"}
        ]
    }


def create_sample_news_data() -> list:
    """Create sample news data for testing"""
    return [
        "Tech stocks rally on strong earnings reports",
        "Market volatility increases as Fed meeting approaches",
        "Analysts upgrade outlook for technology sector",
        "Trading volume surges as investors reposition portfolios"
    ]


def test_swot_analysis():
    """Test SWOT analysis functionality"""
    print("\n" + "="*60)
    print("🧠 TESTING SWOT ANALYSIS")
    print("="*60)
    
    # Test data
    symbol = "AAPL"
    market_data = create_sample_market_data("AAPL", 150.0, 2.5)
    news_data = create_sample_news_data()
    
    # Perform SWOT analysis
    swot_analysis = swot_analyzer.analyze_opportunity(
        symbol=symbol,
        market_data=market_data,
        news_data=news_data
    )
    
    print(f"📊 SWOT Analysis for {symbol}:")
    print(f"   Overall Score: {swot_analysis.overall_score:.3f}")
    print(f"   Confidence: {swot_analysis.confidence:.3f}")
    print(f"   Strengths: {len(swot_analysis.strengths)} items")
    print(f"   Weaknesses: {len(swot_analysis.weaknesses)} items")
    print(f"   Opportunities: {len(swot_analysis.opportunities)} items")
    print(f"   Threats: {len(swot_analysis.threats)} items")
    
    print("\n📋 SWOT Details:")
    print(f"   Strengths: {swot_analysis.strengths}")
    print(f"   Weaknesses: {swot_analysis.weaknesses}")
    print(f"   Opportunities: {swot_analysis.opportunities}")
    print(f"   Threats: {swot_analysis.threats}")


def test_risk_assessment():
    """Test risk assessment functionality"""
    print("\n" + "="*60)
    print("⚠️  TESTING RISK ASSESSMENT")
    print("="*60)
    
    # Test data
    symbol = "TSLA"
    quantity = 10
    current_price = 250.0
    market_data = create_sample_market_data("TSLA", current_price, -1.5)
    
    # Perform risk assessment
    risk_assessment = risk_assessor.assess_risk(
        symbol=symbol,
        quantity=quantity,
        current_price=current_price,
        market_data=market_data
    )
    
    print(f"📊 Risk Assessment for {symbol}:")
    print(f"   Risk Level: {risk_assessment.risk_level.value}")
    print(f"   Overall Risk Score: {risk_assessment.overall_risk_score:.3f}")
    print(f"   Max Loss Amount: ${risk_assessment.max_loss_amount:.2f}")
    print(f"   Max Loss Percentage: {risk_assessment.max_loss_percentage:.1f}%")
    print(f"   VaR (95%): ${risk_assessment.var_95:.2f}")
    print(f"   Volatility: {risk_assessment.volatility:.3f}")
    print(f"   Sharpe Ratio: {risk_assessment.sharpe_ratio}")
    print(f"   Beta: {risk_assessment.beta}")
    print(f"   Correlation with SPY: {risk_assessment.correlation_with_spy:.3f}")
    
    print("\n🔍 Risk Breakdown:")
    print(f"   Sector Risk: {risk_assessment.sector_risk:.3f}")
    print(f"   Market Timing Risk: {risk_assessment.market_timing_risk:.3f}")
    print(f"   Liquidity Risk: {risk_assessment.liquidity_risk:.3f}")
    
    # Get risk summary
    risk_summary = risk_assessor.get_risk_summary(risk_assessment)
    print(f"\n📋 Risk Summary: {json.dumps(risk_summary, indent=2)}")


def test_structured_order_creation():
    """Test structured order creation"""
    print("\n" + "="*60)
    print("📋 TESTING STRUCTURED ORDER CREATION")
    print("="*60)
    
    # Test data
    symbol = "NVDA"
    side = "buy"
    quantity = 5
    market_data = create_sample_market_data("NVDA", 500.0, 3.2)
    news_data = create_sample_news_data()
    
    # Create structured trade
    order = enhanced_trade_executor.create_structured_trade(
        symbol=symbol,
        side=side,
        quantity=quantity,
        market_data=market_data,
        news_data=news_data,
        play_title="NVDA AI Momentum Play",
        play_description="Capitalizing on AI chip demand surge",
        confidence_score=0.75,
        priority=7,
        tags=["AI", "momentum", "tech"],
        notes="Strong technical breakout with positive news flow"
    )
    
    print(f"📊 Created Structured Order:")
    print(f"   Order ID: {order.order_id}")
    print(f"   Symbol: {order.symbol}")
    print(f"   Side: {order.side}")
    print(f"   Quantity: {order.quantity}")
    print(f"   Status: {order.status.value}")
    print(f"   Play Title: {order.play.title}")
    print(f"   SWOT Score: {order.swot_analysis.overall_score:.3f}")
    print(f"   Risk Level: {order.risk_assessment.risk_level.value}")
    print(f"   Confidence: {order.confidence_score:.3f}")
    print(f"   Priority: {order.priority}")
    print(f"   Tags: {order.tags}")
    
    print(f"\n🛑 Stop Conditions:")
    print(f"   Stop Loss: ${order.stop_conditions.stop_loss_price:.2f} ({order.stop_conditions.stop_loss_percentage:.1f}%)")
    print(f"   Take Profit: ${order.stop_conditions.take_profit_price:.2f} ({order.stop_conditions.take_profit_percentage:.1f}%)")
    print(f"   Max Holding Period: {order.stop_conditions.max_holding_period}")
    
    print(f"\n📈 Risk Metrics:")
    print(f"   Max Loss: ${order.risk_assessment.max_loss_amount:.2f}")
    print(f"   VaR (95%): ${order.risk_assessment.var_95:.2f}")
    print(f"   Volatility: {order.risk_assessment.volatility:.3f}")
    
    return order


def test_order_management():
    """Test order management functionality"""
    print("\n" + "="*60)
    print("🗂️  TESTING ORDER MANAGEMENT")
    print("="*60)
    
    # Create multiple orders for testing
    symbols = ["AAPL", "MSFT", "GOOGL"]
    orders = []
    
    for i, symbol in enumerate(symbols):
        market_data = create_sample_market_data(symbol, 100.0 + i*50, 1.0 + i*0.5)
        news_data = create_sample_news_data()
        
        order = enhanced_trade_executor.create_structured_trade(
            symbol=symbol,
            side="buy" if i % 2 == 0 else "sell",
            quantity=10 + i*5,
            market_data=market_data,
            news_data=news_data,
            play_title=f"{symbol} Test Play {i+1}",
            confidence_score=0.6 + i*0.1,
            priority=5 + i,
            tags=[f"test-{i+1}", "demo"]
        )
        orders.append(order)
    
    # Test order management functions
    print(f"📊 Order Management Summary:")
    summary = enhanced_trade_executor.get_all_orders_summary()
    print(f"   Active Orders: {summary['statistics']['total_active']}")
    print(f"   Historical Orders: {summary['statistics']['total_historical']}")
    print(f"   Average SWOT Score: {summary['statistics']['average_swot_score']:.3f}")
    print(f"   Risk Distribution: {summary['statistics']['risk_distribution']}")
    
    # Test order approval workflow
    print(f"\n✅ Testing Order Approval Workflow:")
    for order in orders:
        order_summary = enhanced_trade_executor.get_order_summary(order.order_id)
        if order_summary:
            print(f"   Order {order.symbol}: {order_summary['status']} (Risk: {order_summary['risk_level']})")
            
            if order.should_require_approval():
                print(f"     ⚠️  Requires manual approval")
            else:
                print(f"     ✅ Auto-approved")
        else:
            print(f"   Order {order.symbol}: Could not retrieve summary")
    
    # Test high-risk orders
    high_risk_orders = enhanced_trade_executor.get_high_risk_orders()
    print(f"\n⚠️  High-Risk Orders: {len(high_risk_orders)}")
    for order_summary in high_risk_orders:
        print(f"   {order_summary['symbol']}: {order_summary['risk_level']} (Score: {order_summary['overall_risk_score']:.3f})")
    
    # Test orders requiring approval
    approval_orders = enhanced_trade_executor.get_orders_requiring_approval()
    print(f"\n🔍 Orders Requiring Approval: {len(approval_orders)}")
    for order_summary in approval_orders:
        print(f"   {order_summary['symbol']}: {order_summary['play_title']}")


def test_order_execution_simulation():
    """Test order execution simulation (without actually trading)"""
    print("\n" + "="*60)
    print("🚀 TESTING ORDER EXECUTION SIMULATION")
    print("="*60)
    
    # Create a test order
    symbol = "SPY"
    market_data = create_sample_market_data("SPY", 450.0, 0.5)
    news_data = create_sample_news_data()
    
    order = enhanced_trade_executor.create_structured_trade(
        symbol=symbol,
        side="buy",
        quantity=2,
        market_data=market_data,
        news_data=news_data,
        play_title="SPY Conservative Position",
        confidence_score=0.8,
        priority=3,
        tags=["conservative", "index"]
    )
    
    print(f"📊 Test Order Created:")
    print(f"   Order ID: {order.order_id}")
    print(f"   Symbol: {order.symbol}")
    print(f"   Side: {order.side}")
    print(f"   Quantity: {order.quantity}")
    print(f"   SWOT Score: {order.swot_analysis.overall_score:.3f}")
    print(f"   Risk Level: {order.risk_assessment.risk_level.value}")
    
    # Simulate execution (without actually trading)
    print(f"\n🚀 Simulating Order Execution:")
    
    # Check if order would be auto-approved
    if enhanced_trade_executor._should_auto_approve(order):
        print(f"   ✅ Order would be auto-approved")
        print(f"   📋 Execution would proceed with:")
        print(f"      - Stop Loss: ${order.stop_conditions.stop_loss_price:.2f}")
        print(f"      - Take Profit: ${order.stop_conditions.take_profit_price:.2f}")
        print(f"      - Max Loss: ${order.risk_assessment.max_loss_amount:.2f}")
    else:
        print(f"   ⚠️  Order would require manual approval")
        print(f"   📋 Approval required due to:")
        print(f"      - Risk Level: {order.risk_assessment.risk_level.value}")
        print(f"      - Position Size: ${order.quantity * market_data['price']:.2f}")
        print(f"      - Confidence: {order.confidence_score:.3f}")


def test_order_persistence():
    """Test order persistence (save/load)"""
    print("\n" + "="*60)
    print("💾 TESTING ORDER PERSISTENCE")
    print("="*60)
    
    # Create some test orders
    symbols = ["AAPL", "MSFT"]
    for i, symbol in enumerate(symbols):
        market_data = create_sample_market_data(symbol, 100.0 + i*50, 1.0)
        news_data = create_sample_news_data()
        
        enhanced_trade_executor.create_structured_trade(
            symbol=symbol,
            side="buy",
            quantity=5,
            market_data=market_data,
            news_data=news_data,
            play_title=f"{symbol} Persistence Test",
            tags=["persistence-test"]
        )
    
    # Save orders
    filename = "test_structured_orders.json"
    enhanced_trade_executor.save_orders(filename)
    print(f"💾 Saved orders to {filename}")
    
    # Create new executor and load orders
    print(f"📂 Loading orders from {filename}")
    # Note: In a real scenario, you'd create a new executor instance
    # For this test, we'll just verify the file was created
    import os
    if os.path.exists(filename):
        print(f"✅ Orders file created successfully")
        with open(filename, 'r') as f:
            data = json.load(f)
            print(f"   Active Orders: {len(data.get('active_orders', []))}")
            print(f"   Historical Orders: {len(data.get('order_history', []))}")
    else:
        print(f"❌ Orders file not found")


def main():
    """Run all tests"""
    print("🤖 STRUCTURED ORDER SYSTEM TEST")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all tests
        test_swot_analysis()
        test_risk_assessment()
        test_structured_order_creation()
        test_order_management()
        test_order_execution_simulation()
        test_order_persistence()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("🎯 Key Features Demonstrated:")
        print("   • Comprehensive SWOT analysis")
        print("   • Detailed risk assessment")
        print("   • Structured order creation")
        print("   • Order lifecycle management")
        print("   • Approval workflow")
        print("   • Stop condition management")
        print("   • Order persistence")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 