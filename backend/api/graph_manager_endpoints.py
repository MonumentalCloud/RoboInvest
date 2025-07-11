from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import os

router = APIRouter()

# Load research data from the central event bus
def load_research_data():
    """Load research data from the central event bus database"""
    try:
        # This would typically load from your actual database
        # For now, we'll simulate loading from the research trees endpoint
        import requests
        response = requests.get("http://localhost:8081/api/research/decision-trees")
        if response.status_code == 200:
            return response.json().get('data', {})
        return {}
    except Exception as e:
        print(f"Error loading research data: {e}")
        return {}

@router.post("/graph/query")
async def query_graph(query: Dict[str, Any]):
    """
    Query the research graph intelligently
    """
    try:
        user_query = query.get("query", "").lower()
        research_data = load_research_data()
        
        # Extract all nodes from all research tracks
        all_nodes = []
        for track_name, track_data in research_data.items():
            if isinstance(track_data, dict) and 'tree' in track_data:
                for node in track_data['tree']:
                    node['research_track'] = track_name
                    all_nodes.append(node)
        
        # Process the query
        results = process_graph_query(user_query, all_nodes)
        
        return {
            "status": "success",
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

def process_graph_query(query: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process a natural language query about the research graph
    """
    query_lower = query.lower()
    
    # Initialize results
    results = {
        "answer": "",
        "highlighted_nodes": [],
        "suggestions": [],
        "node_count": 0,
        "confidence": 0.0
    }
    
    # Query patterns
    if any(word in query_lower for word in ['active', 'current', 'ongoing']):
        active_nodes = [node for node in nodes if node.get('status') == 'active']
        results.update({
            "answer": f"I found {len(active_nodes)} active research nodes. These represent ongoing research activities and current investigations.",
            "highlighted_nodes": [node['id'] for node in active_nodes],
            "node_count": len(active_nodes),
            "confidence": 0.9,
            "suggestions": [
                "Show me completed research",
                "Find synthesis nodes",
                "What are the high-confidence findings?",
                "Show me market analysis nodes"
            ]
        })
    
    elif any(word in query_lower for word in ['synthesis', 'finding', 'insight']):
        synthesis_nodes = [node for node in nodes if node.get('type') == 'synthesis']
        results.update({
            "answer": f"I found {len(synthesis_nodes)} synthesis nodes. These represent key findings and insights that combine multiple research threads.",
            "highlighted_nodes": [node['id'] for node in synthesis_nodes],
            "node_count": len(synthesis_nodes),
            "confidence": 0.9,
            "suggestions": [
                "Show me market analysis",
                "Find technical analysis nodes",
                "What are the risk assessments?",
                "Show me active research"
            ]
        })
    
    elif any(word in query_lower for word in ['market', 'trend']):
        market_nodes = [
            node for node in nodes 
            if (node.get('research_track') == 'market_analysis' or 
                'market' in node.get('content', '').lower() or
                'trend' in node.get('content', '').lower())
        ]
        results.update({
            "answer": f"I found {len(market_nodes)} market analysis nodes. These contain insights about market trends, sentiment, and analysis.",
            "highlighted_nodes": [node['id'] for node in market_nodes],
            "node_count": len(market_nodes),
            "confidence": 0.8,
            "suggestions": [
                "Show me technical indicators",
                "Find sentiment analysis",
                "What are the risk factors?",
                "Show me synthesis findings"
            ]
        })
    
    elif any(word in query_lower for word in ['technical', 'indicator', 'pattern']):
        technical_nodes = [
            node for node in nodes 
            if (node.get('research_track') == 'technical_analysis' or 
                any(word in node.get('content', '').lower() for word in ['technical', 'indicator', 'pattern', 'rsi', 'macd', 'sma']))
        ]
        results.update({
            "answer": f"I found {len(technical_nodes)} technical analysis nodes. These contain technical indicators, patterns, and analysis.",
            "highlighted_nodes": [node['id'] for node in technical_nodes],
            "node_count": len(technical_nodes),
            "confidence": 0.8,
            "suggestions": [
                "Show me market analysis",
                "Find fundamental research",
                "What are the synthesis findings?",
                "Show me risk assessments"
            ]
        })
    
    elif any(word in query_lower for word in ['confidence', 'important', 'reliable']):
        high_confidence_nodes = [
            node for node in nodes 
            if (node.get('confidence') and 
                (isinstance(node['confidence'], (int, float)) and node['confidence'] > 0.7 or
                 isinstance(node['confidence'], str) and float(node['confidence']) > 0.7))
        ]
        results.update({
            "answer": f"I found {len(high_confidence_nodes)} nodes with high confidence (>70%). These represent the most reliable research findings.",
            "highlighted_nodes": [node['id'] for node in high_confidence_nodes],
            "node_count": len(high_confidence_nodes),
            "confidence": 0.9,
            "suggestions": [
                "Show me active research",
                "Find synthesis nodes",
                "What are the market trends?",
                "Show me technical analysis"
            ]
        })
    
    elif any(word in query_lower for word in ['risk', 'assessment', 'danger']):
        risk_nodes = [
            node for node in nodes 
            if (node.get('research_track') == 'risk_assessment' or 
                any(word in node.get('content', '').lower() for word in ['risk', 'danger', 'volatility', 'drawdown']))
        ]
        results.update({
            "answer": f"I found {len(risk_nodes)} risk assessment nodes. These contain analysis of potential risks and volatility factors.",
            "highlighted_nodes": [node['id'] for node in risk_nodes],
            "node_count": len(risk_nodes),
            "confidence": 0.8,
            "suggestions": [
                "Show me market analysis",
                "Find technical indicators",
                "What are the synthesis findings?",
                "Show me active research"
            ]
        })
    
    elif any(word in query_lower for word in ['fundamental', 'value', 'earnings']):
        fundamental_nodes = [
            node for node in nodes 
            if (node.get('research_track') == 'fundamental_research' or 
                any(word in node.get('content', '').lower() for word in ['fundamental', 'earnings', 'revenue', 'profit']))
        ]
        results.update({
            "answer": f"I found {len(fundamental_nodes)} fundamental research nodes. These contain analysis of company fundamentals and valuations.",
            "highlighted_nodes": [node['id'] for node in fundamental_nodes],
            "node_count": len(fundamental_nodes),
            "confidence": 0.8,
            "suggestions": [
                "Show me technical analysis",
                "Find market trends",
                "What are the synthesis findings?",
                "Show me risk assessments"
            ]
        })
    
    else:
        # Default response for unrecognized queries
        results.update({
            "answer": f"I understand you're asking about '{query}'. I can help you explore the research graph. Try asking about active research, synthesis findings, market analysis, technical indicators, risk assessments, or high-confidence nodes.",
            "node_count": len(nodes),
            "confidence": 0.5,
            "suggestions": [
                "Show me active research nodes",
                "Find synthesis nodes",
                "What are the most important findings?",
                "Show me market analysis nodes",
                "Find nodes with high confidence",
                "Show me technical analysis",
                "What are the risk factors?"
            ]
        })
    
    return results

@router.get("/graph/stats")
async def get_graph_stats():
    """
    Get overall statistics about the research graph
    """
    try:
        research_data = load_research_data()
        
        # Calculate statistics
        total_nodes = 0
        track_stats = {}
        type_stats = {}
        status_stats = {}
        
        for track_name, track_data in research_data.items():
            if isinstance(track_data, dict) and 'tree' in track_data:
                nodes = track_data['tree']
                total_nodes += len(nodes)
                track_stats[track_name] = len(nodes)
                
                for node in nodes:
                    # Count by type
                    node_type = node.get('type', 'unknown')
                    type_stats[node_type] = type_stats.get(node_type, 0) + 1
                    
                    # Count by status
                    node_status = node.get('status', 'unknown')
                    status_stats[node_status] = status_stats.get(node_status, 0) + 1
        
        return {
            "status": "success",
            "data": {
                "total_nodes": total_nodes,
                "track_stats": track_stats,
                "type_stats": type_stats,
                "status_stats": status_stats,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting graph stats: {str(e)}") 