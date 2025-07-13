#!/usr/bin/env python3
"""
Direct script to add test research nodes to the database.
This bypasses the event bus to avoid asyncio conflicts.
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import logger

def add_test_research_nodes():
    """Add test research nodes directly to the database"""
    db_path = Path("data/central_events.db")
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    # Test research nodes
    test_nodes = [
        {
            'node_id': 'market_analysis_tech_sector',
            'node_type': 'market_analysis',
            'content': 'Tech sector showing strong momentum with AI stocks leading gains. NVDA up 3.2%, AMD up 2.1%. Sector rotation from defensive to growth stocks observed.',
            'status': 'completed',
            'confidence': 0.85,
            'symbols': ['NVDA', 'AMD', 'TSLA', 'AAPL'],
            'sentiment': 'bullish',
            'analysis_type': 'sector_analysis'
        },
        {
            'node_id': 'technical_analysis_spy',
            'node_type': 'technical_analysis',
            'content': 'SPY showing bullish flag pattern on 4H timeframe. RSI at 65, MACD histogram expanding. Support at $520, resistance at $535. Volume increasing on up days.',
            'status': 'completed',
            'confidence': 0.78,
            'symbols': ['SPY'],
            'sentiment': 'bullish',
            'analysis_type': 'pattern_recognition'
        },
        {
            'node_id': 'news_sentiment_fed',
            'node_type': 'news_analysis',
            'content': 'Fed minutes indicate dovish stance on rate cuts. Market pricing in 2-3 cuts by year end. Financial sector stocks rallying on the news.',
            'status': 'completed',
            'confidence': 0.92,
            'symbols': ['XLF', 'JPM', 'BAC'],
            'sentiment': 'bullish',
            'analysis_type': 'macro_analysis'
        },
        {
            'node_id': 'alpha_discovery_momentum',
            'node_type': 'alpha_discovery',
            'content': 'Momentum strategy showing 15% alpha over past 30 days. Top performers: NVDA, AMD, TSLA. Risk-adjusted returns favorable with Sharpe ratio 1.8.',
            'status': 'completed',
            'confidence': 0.88,
            'symbols': ['NVDA', 'AMD', 'TSLA'],
            'sentiment': 'bullish',
            'analysis_type': 'strategy_backtest'
        },
        {
            'node_id': 'risk_assessment_market',
            'node_type': 'risk_analysis',
            'content': 'Market volatility (VIX) at 18.5, below historical average. Sector correlations decreasing, good for diversification. Geopolitical risks elevated but contained.',
            'status': 'completed',
            'confidence': 0.75,
            'symbols': ['VIX'],
            'sentiment': 'neutral',
            'analysis_type': 'volatility_analysis'
        },
        {
            'node_id': 'fundamental_analysis_aapl',
            'node_type': 'fundamental_analysis',
            'content': 'AAPL P/E ratio at 28.5, slightly above sector average. Strong cash flow generation, $200B+ cash reserves. iPhone sales stable, services revenue growing 15% YoY.',
            'status': 'completed',
            'confidence': 0.82,
            'symbols': ['AAPL'],
            'sentiment': 'neutral',
            'analysis_type': 'valuation_analysis'
        },
        {
            'node_id': 'synthesis_market_outlook',
            'node_type': 'synthesis',
            'content': 'Combined analysis suggests bullish short-term outlook. Tech momentum + dovish Fed + low volatility = favorable risk/reward. Focus on growth stocks with momentum.',
            'status': 'completed',
            'confidence': 0.90,
            'symbols': ['SPY', 'QQQ', 'NVDA', 'AMD'],
            'sentiment': 'bullish',
            'analysis_type': 'synthesis'
        }
    ]
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Add research events to the events table
            for i, node in enumerate(test_nodes):
                timestamp = datetime.now() - timedelta(hours=i)
                
                # Create event record
                event_id = f"research_{node['node_id']}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
                
                # Insert into events table
                conn.execute("""
                    INSERT INTO events (
                        event_id, event_type, priority, timestamp, source, title, message, metadata, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    'research',
                    'medium',
                    timestamp.isoformat(),
                    'test_populator',
                    f"Research Node: {node['node_id']}",
                    node['content'][:100] + "...",
                    json.dumps({
                        'node_id': node['node_id'],
                        'node_type': node['node_type'],
                        'content': node['content'],
                        'status': node['status'],
                        'confidence': node['confidence'],
                        'symbols': node['symbols'],
                        'sentiment': node['sentiment'],
                        'analysis_type': node['analysis_type'],
                        'timestamp': timestamp.isoformat()
                    }),
                    json.dumps(["research", "test_data", node['node_type'], node['sentiment']])
                ))
                
                logger.info(f"✅ Added research node: {node['node_id']}")
            
            conn.commit()
            logger.info(f"🎉 Successfully added {len(test_nodes)} test research nodes to database!")
            logger.info("💡 The LLM agent should now be able to interact with the research graph.")
            
    except Exception as e:
        logger.error(f"❌ Error adding test research nodes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_test_research_nodes() 