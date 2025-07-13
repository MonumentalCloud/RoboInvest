#!/usr/bin/env python3
"""
Generate sample dashboard data for testing the comprehensive trading dashboard.
This script creates realistic trade and position data to populate the charts and tables.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

def generate_sample_trades() -> List[Dict[str, Any]]:
    """Generate realistic sample trade data."""
    symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "SPY", "QQQ", "IWM"]
    trades = []
    
    # Generate trades over the last 30 days
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(50):
        trade_date = base_date + timedelta(days=random.randint(0, 30))
        symbol = random.choice(symbols)
        side = random.choice(["BUY", "SELL"])
        quantity = random.randint(1, 10)
        entry_price = round(random.uniform(50, 500), 2)
        
        # 70% chance of being a closed trade
        if random.random() < 0.7:
            exit_price = entry_price + random.uniform(-50, 50)
            exit_date = trade_date + timedelta(days=random.randint(1, 7))
            pnl = (exit_price - entry_price) * quantity if side == "BUY" else (entry_price - exit_price) * quantity
            pnl_pct = (pnl / (entry_price * quantity)) * 100
            confidence = random.uniform(0.3, 0.9)
            
            trades.append({
                "symbol": symbol,
                "quantity": quantity,
                "entry_price": entry_price,
                "exit_price": round(exit_price, 2),
                "entry_time": trade_date.isoformat(),
                "exit_time": exit_date.isoformat(),
                "side": side,
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
                "confidence": round(confidence, 2)
            })
        else:
            # Open trade
            trades.append({
                "symbol": symbol,
                "quantity": quantity,
                "entry_price": entry_price,
                "entry_time": trade_date.isoformat(),
                "side": side,
                "confidence": round(random.uniform(0.3, 0.9), 2)
            })
    
    return trades

def generate_sample_positions() -> List[Dict[str, Any]]:
    """Generate realistic sample position data."""
    symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]
    positions = []
    
    for symbol in symbols:
        if random.random() < 0.6:  # 60% chance of having a position
            quantity = random.randint(1, 20)
            entry_price = round(random.uniform(100, 400), 2)
            current_price = entry_price + random.uniform(-30, 30)
            side = random.choice(["BUY", "SELL"])
            entry_time = datetime.now() - timedelta(days=random.randint(1, 14))
            
            # Calculate unrealized PnL
            if side == "BUY":
                unrealized_pnl = (current_price - entry_price) * quantity
            else:
                unrealized_pnl = (entry_price - current_price) * quantity
            
            unrealized_pnl_pct = (unrealized_pnl / (entry_price * quantity)) * 100
            
            positions.append({
                "symbol": symbol,
                "quantity": quantity,
                "entry_price": entry_price,
                "current_price": round(current_price, 2),
                "entry_time": entry_time.isoformat(),
                "side": side,
                "unrealized_pnl": round(unrealized_pnl, 2),
                "unrealized_pnl_pct": round(unrealized_pnl_pct, 2)
            })
    
    return positions

def generate_sample_performance() -> Dict[str, Any]:
    """Generate realistic sample performance data."""
    total_trades = 50
    winning_trades = int(total_trades * 0.65)  # 65% win rate
    losing_trades = total_trades - winning_trades
    
    total_pnl = random.uniform(-500, 2000)
    avg_pnl = total_pnl / total_trades
    max_drawdown = random.uniform(5, 25)
    sharpe_ratio = random.uniform(0.5, 2.5)
    current_positions = random.randint(2, 8)
    unrealized_pnl = random.uniform(-200, 500)
    
    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round((winning_trades / total_trades) * 100, 1),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl": round(avg_pnl, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "current_positions": current_positions,
        "unrealized_pnl": round(unrealized_pnl, 2)
    }

def generate_graph_data() -> Dict[str, Any]:
    """Generate sample graph data for force-directed visualization."""
    nodes = [
        {"id": "SPY", "name": "SPY", "type": "ETF", "value": 100, "group": 0},
        {"id": "QQQ", "name": "QQQ", "type": "ETF", "value": 85, "group": 0},
        {"id": "IWM", "name": "IWM", "type": "ETF", "value": 70, "group": 0},
        {"id": "AAPL", "name": "AAPL", "type": "Stock", "value": 90, "group": 1},
        {"id": "TSLA", "name": "TSLA", "type": "Stock", "value": 75, "group": 1},
        {"id": "NVDA", "name": "NVDA", "type": "Stock", "value": 95, "group": 1},
        {"id": "MSFT", "name": "MSFT", "type": "Stock", "value": 88, "group": 1},
        {"id": "GOOGL", "name": "GOOGL", "type": "Stock", "value": 82, "group": 1},
        {"id": "Tech", "name": "Tech Sector", "type": "Sector", "value": 85, "group": 2},
        {"id": "AI", "name": "AI Sector", "type": "Sector", "value": 92, "group": 2},
        {"id": "EV", "name": "EV Sector", "type": "Sector", "value": 68, "group": 2},
    ]
    
    links = [
        {"source": "SPY", "target": "AAPL", "value": 1, "type": "correlation"},
        {"source": "SPY", "target": "TSLA", "value": 1, "type": "correlation"},
        {"source": "SPY", "target": "NVDA", "value": 1, "type": "correlation"},
        {"source": "SPY", "target": "MSFT", "value": 1, "type": "correlation"},
        {"source": "SPY", "target": "GOOGL", "value": 1, "type": "correlation"},
        {"source": "QQQ", "target": "AAPL", "value": 1, "type": "correlation"},
        {"source": "QQQ", "target": "NVDA", "value": 1, "type": "correlation"},
        {"source": "QQQ", "target": "MSFT", "value": 1, "type": "correlation"},
        {"source": "QQQ", "target": "GOOGL", "value": 1, "type": "correlation"},
        {"source": "AAPL", "target": "Tech", "value": 1, "type": "sector"},
        {"source": "MSFT", "target": "Tech", "value": 1, "type": "sector"},
        {"source": "GOOGL", "target": "Tech", "value": 1, "type": "sector"},
        {"source": "NVDA", "target": "AI", "value": 1, "type": "sector"},
        {"source": "TSLA", "target": "EV", "value": 1, "type": "sector"},
        {"source": "AI", "target": "Tech", "value": 1, "type": "correlation"},
        {"source": "EV", "target": "Tech", "value": 1, "type": "correlation"},
    ]
    
    return {"nodes": nodes, "links": links}

def save_sample_data():
    """Save sample data to files for testing."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate and save sample data
    trades = generate_sample_trades()
    positions = generate_sample_positions()
    performance = generate_sample_performance()
    graph_data = generate_graph_data()
    
    # Save trades to performance.jsonl (simulating the performance tracker format)
    with open("performance.jsonl", "w") as f:
        for trade in trades:
            if "pnl" in trade:  # Only save closed trades
                f.write(json.dumps(trade) + "\n")
    
    # Save positions to positions.json
    positions_dict = {}
    for pos in positions:
        positions_dict[pos["symbol"]] = {
            "symbol": pos["symbol"],
            "quantity": pos["quantity"],
            "entry_price": pos["entry_price"],
            "entry_time": pos["entry_time"],
            "side": pos["side"]
        }
    
    with open("positions.json", "w") as f:
        json.dump(positions_dict, f, indent=2)
    
    # Save closed trades to closed_trades.jsonl
    closed_trades = [t for t in trades if "exit_price" in t]
    with open("closed_trades.jsonl", "w") as f:
        for trade in closed_trades:
            f.write(json.dumps(trade) + "\n")
    
    # Save sample data for frontend testing
    sample_data = {
        "trades": trades,
        "positions": positions,
        "performance": performance,
        "graph_data": graph_data
    }
    
    with open("data/sample_dashboard_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("✅ Sample dashboard data generated successfully!")
    print(f"📊 Generated {len(trades)} trades, {len(positions)} positions")
    print(f"📈 Performance: {performance['win_rate']}% win rate, ${performance['total_pnl']} total PnL")
    print(f"🕸️ Graph: {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} links")
    print("\n📁 Files created:")
    print("  - performance.jsonl (for performance tracker)")
    print("  - positions.json (for PnL tracker)")
    print("  - closed_trades.jsonl (for PnL tracker)")
    print("  - data/sample_dashboard_data.json (for frontend testing)")

if __name__ == "__main__":
    save_sample_data() 