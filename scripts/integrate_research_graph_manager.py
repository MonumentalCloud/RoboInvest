"""
Integrate Research Graph Manager with Research System

This script:
1. Fetches all research nodes from the database
2. Runs the research graph manager analysis
3. Creates synthesis nodes and adds them to the research graph
4. Updates the central event bus with new insights
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Any
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_graph_manager import research_graph_manager
from core.central_event_bus import central_event_bus, EventType, EventPriority

logger = logging.getLogger(__name__)

async def integrate_research_graph_manager():
    """Main integration function"""
    try:
        logger.info("🔄 Starting Research Graph Manager integration")
        
        # 1. Fetch all research nodes from database
        research_nodes = await fetch_all_research_nodes()
        logger.info(f"📊 Fetched {len(research_nodes)} research nodes")
        
        if len(research_nodes) < 2:
            logger.info("Not enough nodes for analysis, skipping")
            return
        
        # 2. Run graph analysis
        analysis_results = research_graph_manager.analyze_research_graph(research_nodes)
        
        if "error" in analysis_results:
            logger.error(f"Analysis failed: {analysis_results['error']}")
            return
        
        # 3. Log analysis results
        log_analysis_results(analysis_results)
        
        # 4. Create synthesis nodes and add to database
        synthesis_nodes = analysis_results.get("synthesis_nodes", [])
        if synthesis_nodes:
            await add_synthesis_nodes_to_database(synthesis_nodes)
            logger.info(f"✅ Added {len(synthesis_nodes)} synthesis nodes to database")
        
        # 5. Emit integration completion event
        from core.central_event_bus import create_event
        event = create_event(
            event_type=EventType.RESEARCH,
            source="research_graph_manager_integration",
            title="Research Graph Analysis Complete",
            message=f"Analyzed {len(research_nodes)} nodes, created {len(synthesis_nodes)} synthesis nodes",
            priority=EventPriority.HIGH,
            metadata={
                "nodes_analyzed": len(research_nodes),
                "synthesis_nodes_created": len(synthesis_nodes),
                "patterns_detected": len(analysis_results.get("patterns", [])),
                "opportunities_found": len(analysis_results.get("synthesis_opportunities", []))
            },
            tags=["research", "synthesis", "integration"]
        )
        central_event_bus.emit_event(event)
        
        logger.info("✅ Research Graph Manager integration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        raise

async def fetch_all_research_nodes() -> List[Dict[str, Any]]:
    """Fetch all research nodes from the database"""
    try:
        # Get all research trees
        trees = central_event_bus.get_research_trees()
        
        all_nodes = []
        
        for tree in trees:
            tree_id = tree["tree_id"]
            nodes = central_event_bus.get_research_tree_nodes(tree_id)
            
            for node in nodes:
                # Add research track info
                node["research_track"] = tree["track_name"]
                all_nodes.append(node)
        
        logger.info(f"📊 Fetched {len(all_nodes)} nodes from {len(trees)} research trees")
        return all_nodes
        
    except Exception as e:
        logger.error(f"Failed to fetch research nodes: {e}")
        return []

def log_analysis_results(results: Dict[str, Any]):
    """Log the analysis results"""
    logger.info("📈 Analysis Results:")
    
    patterns = results.get("patterns", [])
    logger.info(f"  - Patterns detected: {len(patterns)}")
    for pattern in patterns:
        logger.info(f"    * {pattern.pattern_type}: {pattern.description}")
    
    opportunities = results.get("synthesis_opportunities", [])
    logger.info(f"  - Synthesis opportunities: {len(opportunities)}")
    for opp in opportunities:
        logger.info(f"    * {opp.type.value}: {opp.title}")
    
    synthesis_nodes = results.get("synthesis_nodes", [])
    logger.info(f"  - Synthesis nodes created: {len(synthesis_nodes)}")
    for node in synthesis_nodes:
        logger.info(f"    * {node['title']} (confidence: {node.get('confidence', 'N/A')})")

async def add_synthesis_nodes_to_database(synthesis_nodes: List[Dict[str, Any]]):
    """Add synthesis nodes to the research database"""
    try:
        for node in synthesis_nodes:
            # Create a new research tree for synthesis nodes
            tree_id = f"synthesis_tree_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save the synthesis node
            central_event_bus.save_research_tree(
                tree_id=tree_id,
                agent_name="research_graph_manager",
                track_name="synthesis",
                root_id=node["id"],
                tree_data={
                    "nodes": {
                        node["id"]: {
                            "id": node["id"],
                            "type": node["type"],
                            "title": node["title"],
                            "content": node["content"],
                            "status": node["status"],
                            "confidence": node.get("confidence"),
                            "parent_id": node.get("parent"),
                            "metadata": node.get("metadata", {}),
                            "timestamp": node["timestamp"]
                        }
                    }
                }
            )
            
            logger.info(f"💾 Saved synthesis node: {node['title']}")
            
    except Exception as e:
        logger.error(f"Failed to add synthesis nodes to database: {e}")

async def run_periodic_analysis(interval_minutes: int = 30):
    """Run periodic analysis of the research graph"""
    logger.info(f"🔄 Starting periodic research graph analysis (every {interval_minutes} minutes)")
    
    while True:
        try:
            await integrate_research_graph_manager()
            logger.info(f"⏰ Next analysis in {interval_minutes} minutes")
            await asyncio.sleep(interval_minutes * 60)
            
        except Exception as e:
            logger.error(f"Periodic analysis failed: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Run the integration
    asyncio.run(integrate_research_graph_manager()) 