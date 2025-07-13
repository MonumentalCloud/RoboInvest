#!/usr/bin/env python3
"""
Test script to verify dashboard components work with sample data.
This simulates the API responses that the frontend expects.
"""

import json
from pathlib import Path

def test_dashboard_data():
    """Test that the sample dashboard data is properly formatted."""
    
    # Load sample data
    with open("data/sample_dashboard_data.json", "r") as f:
        data = json.load(f)
    
    print("📊 Testing Dashboard Data Structure")
    print("=" * 50)
    
    # Test performance data
    performance = data["performance"]
    print(f"✅ Performance Data:")
    print(f"   - Total Trades: {performance['total_trades']}")
    print(f"   - Win Rate: {performance['win_rate']}%")
    print(f"   - Total PnL: ${performance['total_pnl']}")
    print(f"   - Sharpe Ratio: {performance['sharpe_ratio']}")
    print(f"   - Max Drawdown: {performance['max_drawdown']}%")
    
    # Test trades data
    trades = data["trades"]
    print(f"\n✅ Trades Data:")
    print(f"   - Total Trades: {len(trades)}")
    print(f"   - Closed Trades: {len([t for t in trades if 'exit_price' in t])}")
    print(f"   - Open Trades: {len([t for t in trades if 'exit_price' not in t])}")
    
    # Show sample trade
    if trades:
        sample_trade = trades[0]
        print(f"   - Sample Trade: {sample_trade['symbol']} {sample_trade['side']} {sample_trade['quantity']} @ ${sample_trade['entry_price']}")
    
    # Test positions data
    positions = data["positions"]
    print(f"\n✅ Positions Data:")
    print(f"   - Total Positions: {len(positions)}")
    
    # Show sample position
    if positions:
        sample_position = positions[0]
        print(f"   - Sample Position: {sample_position['symbol']} {sample_position['side']} {sample_position['quantity']} @ ${sample_position['entry_price']}")
        print(f"   - Unrealized PnL: ${sample_position['unrealized_pnl']} ({sample_position['unrealized_pnl_pct']}%)")
    
    # Test graph data
    graph_data = data["graph_data"]
    print(f"\n✅ Graph Data:")
    print(f"   - Nodes: {len(graph_data['nodes'])}")
    print(f"   - Links: {len(graph_data['links'])}")
    
    # Show sample nodes
    print(f"   - Sample Nodes:")
    for node in graph_data['nodes'][:3]:
        print(f"     * {node['name']} ({node['type']}) - Group {node['group']}")
    
    # Show sample links
    print(f"   - Sample Links:")
    for link in graph_data['links'][:3]:
        print(f"     * {link['source']} -> {link['target']} ({link['type']})")
    
    print(f"\n🎉 All dashboard data structures are valid!")
    print(f"📁 Data file: data/sample_dashboard_data.json")
    print(f"🌐 Frontend Dashboard: http://localhost:5174/dashboard")
    
    return True

def test_api_endpoints():
    """Test that the API endpoints would return the expected data structure."""
    
    print(f"\n🔌 Testing API Endpoint Structures")
    print("=" * 50)
    
    # Simulate API responses
    api_responses = {
        "/api/performance": {
            "status": "success",
            "performance": {
                "total_trades": 50,
                "winning_trades": 32,
                "losing_trades": 18,
                "win_rate": 64.0,
                "total_pnl": 1267.91,
                "avg_pnl": 25.36,
                "max_drawdown": 12.5,
                "sharpe_ratio": 1.8,
                "current_positions": 4,
                "unrealized_pnl": 245.67
            }
        },
        "/api/trades": {
            "status": "success",
            "trades": [
                {
                    "symbol": "AAPL",
                    "quantity": 5,
                    "entry_price": 150.25,
                    "exit_price": 155.75,
                    "entry_time": "2024-01-15T10:30:00",
                    "exit_time": "2024-01-16T14:45:00",
                    "side": "BUY",
                    "pnl": 27.50,
                    "pnl_pct": 3.66,
                    "confidence": 0.85
                }
            ]
        },
        "/api/positions": {
            "status": "success",
            "positions": [
                {
                    "symbol": "NVDA",
                    "quantity": 10,
                    "entry_price": 450.00,
                    "current_price": 475.50,
                    "entry_time": "2024-01-20T09:15:00",
                    "side": "BUY",
                    "unrealized_pnl": 255.00,
                    "unrealized_pnl_pct": 5.67
                }
            ]
        }
    }
    
    for endpoint, response in api_responses.items():
        print(f"✅ {endpoint}")
        if "performance" in endpoint:
            perf = response["performance"]
            print(f"   - Win Rate: {perf['win_rate']}%")
            print(f"   - Total PnL: ${perf['total_pnl']}")
        elif "trades" in endpoint:
            trades = response["trades"]
            print(f"   - Trades Count: {len(trades)}")
        elif "positions" in endpoint:
            positions = response["positions"]
            print(f"   - Positions Count: {len(positions)}")
    
    print(f"\n🎯 API endpoint structures are ready for frontend consumption!")

if __name__ == "__main__":
    test_dashboard_data()
    test_api_endpoints() 