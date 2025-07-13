#!/usr/bin/env python3
"""
Start autonomous research agents to populate the research graph.
This script runs the research agents in the background to create research nodes.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.world_monitor import WorldMonitorAgent
from agents.research_planner import ResearchPlannerAgent
from agents.action_executor import ActionExecutorAgent
from agents.rag_playbook import rag_agent
from core.central_event_bus import central_event_bus
from utils.logger import logger

class ResearchAgentRunner:
    """Runs research agents to populate the research graph"""
    
    def __init__(self):
        self.world_monitor = WorldMonitorAgent()
        self.planner = ResearchPlannerAgent()
        self.executor = ActionExecutorAgent()
        self.running = False
        
    async def start_research_loop(self):
        """Main research loop that continuously creates research nodes"""
        logger.info("🚀 Starting autonomous research agents...")
        self.running = True
        
        while self.running:
            try:
                # Step 1: Observe the world
                logger.info("🔍 Observing market and news...")
                observation = await self.world_monitor.observe()
                
                # Step 2: Create research events from observations
                research_events = self._create_research_events(observation)
                
                # Step 3: Process each research event
                for event in research_events:
                    await self._process_research_event(event)
                
                # Step 4: Wait before next cycle
                logger.info("⏳ Waiting 5 minutes before next research cycle...")
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in research loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def _create_research_events(self, observation):
        """Convert world observations into research events"""
        events = []
        
        # Create market analysis events
        if observation.get('market'):
            for symbol, data in observation['market'].items():
                events.append({
                    'type': 'market_analysis',
                    'symbol': symbol,
                    'data': data,
                    'timestamp': observation['timestamp']
                })
        
        # Create news analysis events
        if observation.get('news'):
            for i, headline in enumerate(observation['news'][:5]):  # Limit to 5 headlines
                events.append({
                    'type': 'news_analysis',
                    'headline': headline,
                    'timestamp': observation['timestamp']
                })
        
        # Create sentiment analysis events
        if observation.get('sentiment'):
            events.append({
                'type': 'sentiment_analysis',
                'sentiment': observation['sentiment'],
                'timestamp': observation['timestamp']
            })
        
        return events
    
    async def _process_research_event(self, event):
        """Process a research event and create research nodes"""
        try:
            logger.info(f"📊 Processing research event: {event['type']}")
            
            # Step 1: Planner decides what research to do
            task = self.planner(event)
            
            # Step 2: Executor performs the research
            result = self.executor(task)
            
            # Step 3: Store research findings
            if result.get('status') == 'stored':
                # Create a research node in the central event bus
                research_node = {
                    'node_id': f"research_{event['type']}_{event['timestamp']}",
                    'node_type': event['type'],
                    'content': f"Research on {event.get('symbol', 'market')}: {result.get('task', {}).get('payload', {})}",
                    'status': 'completed',
                    'confidence': 0.8,
                    'timestamp': event['timestamp'],
                    'metadata': {
                        'event_type': event['type'],
                        'symbol': event.get('symbol'),
                        'sentiment': event.get('sentiment'),
                        'task_type': task.get('type')
                    }
                }
                
                # Emit research node creation event
                from core.central_event_bus import EventType, EventPriority, create_event
                
                research_event = create_event(
                    event_type=EventType.RESEARCH,
                    source="research_agent",
                    title=f"Research Node Created: {research_node['node_id']}",
                    message=f"Created research node for {event['type']} analysis",
                    priority=EventPriority.MEDIUM,
                    metadata=research_node,
                    tags=["research", "node_created", event['type']]
                )
                
                await central_event_bus.event_queue.put(research_event)
                
                logger.info(f"✅ Created research node: {research_node['node_id']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing research event: {e}")
    
    def stop(self):
        """Stop the research loop"""
        self.running = False
        logger.info("🛑 Stopping research agents...")

async def main():
    """Main entry point"""
    runner = ResearchAgentRunner()
    
    try:
        await runner.start_research_loop()
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
        runner.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        runner.stop()

if __name__ == "__main__":
    asyncio.run(main()) 