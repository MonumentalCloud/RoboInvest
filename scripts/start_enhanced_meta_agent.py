#!/usr/bin/env python3
"""
Enhanced Meta Agent Startup Script
Starts the enhanced meta agent as a background service for continuous system monitoring.
"""

import asyncio
import signal
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from agents.enhanced_meta_agent import enhanced_meta_agent
from utils.logger import logger

class EnhancedMetaAgentService:
    """Service wrapper for the enhanced meta agent."""
    
    def __init__(self):
        self.running = False
        self.enhanced_meta_agent = enhanced_meta_agent
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"🛑 Received signal {signum}, shutting down enhanced meta agent...")
        self.running = False
        self.enhanced_meta_agent.stop_monitoring()
    
    async def start_service(self):
        """Start the enhanced meta agent service."""
        try:
            # Setup signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.running = True
            
            logger.info("🚀 Starting Enhanced Meta Agent Service...")
            logger.info("🔍 Continuous system monitoring and improvement coordination active")
            logger.info("📊 Performance analysis and bottleneck detection enabled")
            logger.info("🛠️  Automated improvement suggestions and implementation active")
            logger.info("🔮 Predictive maintenance and proactive optimization enabled")
            
            # Start the enhanced meta agent
            await self.enhanced_meta_agent.start_continuous_monitoring()
            
        except Exception as e:
            logger.error(f"❌ Enhanced Meta Agent Service failed: {e}")
            raise
        finally:
            logger.info("🛑 Enhanced Meta Agent Service stopped")

async def main():
    """Main entry point."""
    service = EnhancedMetaAgentService()
    await service.start_service()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Enhanced Meta Agent Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Enhanced Meta Agent Service error: {e}")
        sys.exit(1)