#!/usr/bin/env python3
"""
Background Research Service
Continuous autonomous agent research system that runs 24/7 in the background.
"""

import asyncio
import json
import time
import signal
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

from enhanced_trading_system import enhanced_trading_system
from agents.parallel_execution_system import execution_engine
from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
from tools.data_fetcher import data_fetcher
from utils.logger import logger  # type: ignore

class ContinuousResearchService:
    """
    Background service that continuously runs autonomous agents for research.
    
    Features:
    - Continuous research cycles (every 15-30 minutes)
    - Multiple research tracks running in parallel
    - Results stored in JSON files for frontend consumption
    - Self-healing: restarts agents if they fail
    - Market hours awareness
    - Dynamic research objectives based on market conditions
    """
    
    def __init__(self):
        self.running = False
        self.research_threads = {}
        self.research_results_dir = Path("research_data")
        self.research_results_dir.mkdir(exist_ok=True)
        
        # Research configuration
        self.research_cycles = {
            "alpha_discovery": {
                "interval": 900,  # 15 minutes
                "last_run": 0,
                "agent_specialization": "alpha_hunting",
                "enabled": True
            },
            "market_monitoring": {
                "interval": 600,  # 10 minutes  
                "last_run": 0,
                "agent_specialization": "market_analysis",
                "enabled": True
            },
            "sentiment_tracking": {
                "interval": 1200,  # 20 minutes
                "last_run": 0,
                "agent_specialization": "sentiment_analysis", 
                "enabled": True
            },
            "technical_analysis": {
                "interval": 1800,  # 30 minutes
                "last_run": 0,
                "agent_specialization": "technical_analysis",
                "enabled": True
            },
            "risk_assessment": {
                "interval": 3600,  # 1 hour
                "last_run": 0,
                "agent_specialization": "risk_assessment",
                "enabled": True
            },
            "deep_research": {
                "interval": 7200,  # 2 hours
                "last_run": 0,
                "agent_specialization": "fundamental_research",
                "enabled": True
            }
        }
        
        # System state
        self.system_stats = {
            "service_started": datetime.now().isoformat(),
            "total_research_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "last_cycle_time": None,
            "active_research_tracks": 0,
            "insights_generated": 0
        }
        
        # Initialize the enhanced trading system
        enhanced_trading_system.initialize_system()
        
        logger.info("Continuous Research Service initialized")
    
    def start_service(self):
        """Start the continuous research service."""
        try:
            self.running = True
            logger.info("🚀 Starting Continuous Research Service...")
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start the main research loop
            asyncio.run(self._main_research_loop())
            
        except Exception as e:
            logger.error(f"Service startup error: {e}")
            self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def _main_research_loop(self):
        """Main research loop that coordinates all research tracks."""
        
        logger.info("🔄 Main research loop started")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check each research track and run if due
                research_tasks = []
                
                for track_name, config in self.research_cycles.items():
                    if not config["enabled"]:
                        continue
                    
                    time_since_last = current_time - config["last_run"]
                    
                    if time_since_last >= config["interval"]:
                        logger.info(f"🎯 Starting research track: {track_name}")
                        
                        # Create research task
                        task = asyncio.create_task(
                            self._run_research_track(track_name, config)
                        )
                        research_tasks.append((track_name, task))
                        
                        # Update last run time
                        config["last_run"] = current_time
                
                # Execute research tasks in parallel
                if research_tasks:
                    self.system_stats["active_research_tracks"] = len(research_tasks)
                    
                    for track_name, task in research_tasks:
                        try:
                            result = await task
                            if result:
                                self._save_research_result(track_name, result)
                                self.system_stats["successful_cycles"] += 1
                                self.system_stats["insights_generated"] += len(result.get("insights", []))
                            else:
                                self.system_stats["failed_cycles"] += 1
                                
                        except Exception as e:
                            logger.error(f"Research track {track_name} failed: {e}")
                            self.system_stats["failed_cycles"] += 1
                    
                    self.system_stats["total_research_cycles"] += len(research_tasks)
                    self.system_stats["last_cycle_time"] = datetime.now().isoformat()
                
                # Update system status file
                self._save_system_status()
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                # Don't crash the service on errors, just wait and continue
                await asyncio.sleep(120)  # Wait 2 minutes on errors before retrying
        
        logger.info("🛑 Research service stopped")
    
    async def _run_research_track(self, track_name: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run a specific research track."""
        
        try:
            specialization = config["agent_specialization"]
            
            # Create research objective based on track type and current market conditions
            research_objective = await self._generate_research_objective(track_name, specialization)
            
            # Get current market context
            market_context = await self._get_market_context()
            
            # Run the research using the enhanced system
            if track_name == "deep_research":
                # Use full multi-agent orchestration for deep research
                result = await enhanced_trading_system.hunt_for_alpha(
                    market_context=market_context,
                    focus_areas=[research_objective],
                    priority="normal"
                )
            else:
                # Use individual enhanced agent for specific tracks
                agent = EnhancedAutonomousAgent(f"{track_name}_agent", specialization)
                result = await agent.autonomous_research_cycle(
                    research_objective=research_objective,
                    context=market_context
                )
            
            # Add metadata
            result["research_track"] = track_name
            result["specialization"] = specialization
            result["market_context"] = market_context
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ Research track {track_name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Research track {track_name} error: {e}")
            return None
    
    async def _generate_research_objective(self, track_name: str, specialization: str) -> str:
        """Generate dynamic research objectives based on track type and market conditions."""
        
        current_hour = datetime.now().hour
        
        objective_templates = {
            "alpha_discovery": [
                "Hunt for unique alpha opportunities in current market conditions",
                "Identify undervalued securities with catalyst potential",
                "Discover sector rotation opportunities and momentum plays",
                "Find cross-asset arbitrage and relative value opportunities"
            ],
            "market_monitoring": [
                "Monitor real-time market patterns and unusual activity",
                "Analyze current price action and volume anomalies", 
                "Track sector performance and rotation signals",
                "Identify breakout patterns and momentum shifts"
            ],
            "sentiment_tracking": [
                "Analyze current market sentiment and narrative shifts",
                "Track news impact on market sectors and individual stocks",
                "Monitor social sentiment and retail trader behavior",
                "Assess institutional vs retail sentiment divergence"
            ],
            "technical_analysis": [
                "Identify technical patterns and signal confluences",
                "Analyze support/resistance levels and breakout potential",
                "Track momentum indicators and trend strength",
                "Find technical setups with favorable risk/reward"
            ],
            "risk_assessment": [
                "Assess current market risks and tail risk scenarios",
                "Analyze correlation structures and portfolio risks",
                "Monitor macro risks and policy impact potential",
                "Evaluate liquidity conditions and market stress indicators"
            ],
            "deep_research": [
                "Conduct comprehensive fundamental analysis on key opportunities",
                "Deep dive into sector dynamics and competitive positioning",
                "Analyze long-term thematic investment opportunities",
                "Research emerging trends and disruption potential"
            ]
        }
        
        # Get template objectives
        templates = objective_templates.get(track_name, ["General market research"])
        
        # Add time-based context
        if current_hour < 9:  # Pre-market
            time_context = "focusing on pre-market developments and overnight news"
        elif current_hour < 16:  # Market hours
            time_context = "focusing on live market action and intraday opportunities"
        else:  # After hours
            time_context = "focusing on after-hours developments and next-day preparation"
        
        # Select and customize objective
        base_objective = templates[hash(datetime.now().date()) % len(templates)]
        
        return f"{base_objective}, {time_context}"
    
    async def _get_market_context(self) -> Dict[str, Any]:
        """Get current market context for research."""
        
        try:
            # Get market overview
            market_overview = data_fetcher.get_market_overview()
            
            # Add timestamp and session info
            now = datetime.now()
            market_context = {
                "market_data": market_overview,
                "timestamp": now.isoformat(),
                "market_session": self._get_market_session(now),
                "symbols": ["SPY", "QQQ", "IWM", "TLT", "GLD", "VIX"],
                "focus_timeframe": "short_to_medium_term"
            }
            
            return market_context
            
        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "market_session": "unknown",
                "symbols": ["SPY"],
                "error": str(e)
            }
    
    def _get_market_session(self, dt: datetime) -> str:
        """Determine current market session."""
        hour = dt.hour
        
        if hour < 9:
            return "pre_market"
        elif hour < 16:
            return "regular_hours"  
        elif hour < 20:
            return "after_hours"
        else:
            return "overnight"
    
    def _save_research_result(self, track_name: str, result: Dict[str, Any]):
        """Save research result to file for frontend consumption."""
        
        try:
            # Save individual track result
            track_file = self.research_results_dir / f"{track_name}_latest.json"
            with open(track_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            # Save to history with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.research_results_dir / f"{track_name}_{timestamp}.json"
            with open(history_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            # Update consolidated insights file
            self._update_consolidated_insights(track_name, result)
            
            logger.info(f"💾 Saved research results for {track_name}")
            
        except Exception as e:
            logger.error(f"Error saving research result: {e}")
    
    def _update_consolidated_insights(self, track_name: str, result: Dict[str, Any]):
        """Update consolidated insights file for frontend."""
        
        try:
            insights_file = self.research_results_dir / "consolidated_insights.json"
            
            # Load existing insights
            if insights_file.exists():
                with open(insights_file, 'r') as f:
                    consolidated = json.load(f)
            else:
                consolidated = {
                    "insights": [],
                    "last_updated": None,
                    "total_insights": 0
                }
            
            # Extract insights from result
            new_insights = []
            
            if "insights" in result:
                for insight in result["insights"]:
                    insight_entry = {
                        "track": track_name,
                        "specialization": result.get("specialization", "unknown"),
                        "insight": insight.get("insight", str(insight)),
                        "confidence": insight.get("confidence", 0.5),
                        "timestamp": result.get("completed_at", datetime.now().isoformat()),
                        "competitive_edge": insight.get("competitive_edge", ""),
                        "action_plan": insight.get("actionable_steps", [])
                    }
                    new_insights.append(insight_entry)
            
            # Add to consolidated insights
            consolidated["insights"].extend(new_insights)
            consolidated["last_updated"] = datetime.now().isoformat()
            consolidated["total_insights"] = len(consolidated["insights"])
            
            # Keep only last 100 insights
            consolidated["insights"] = consolidated["insights"][-100:]
            
            # Save updated insights
            with open(insights_file, 'w') as f:
                json.dump(consolidated, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error updating consolidated insights: {e}")
    
    def _save_system_status(self):
        """Save current system status for monitoring."""
        
        try:
            status_file = self.research_results_dir / "system_status.json"
            
            status = {
                **self.system_stats,
                "research_tracks": {
                    name: {
                        "enabled": config["enabled"],
                        "interval_minutes": config["interval"] / 60,
                        "last_run": datetime.fromtimestamp(config["last_run"]).isoformat() if config["last_run"] > 0 else None,
                        "next_run_estimate": datetime.fromtimestamp(config["last_run"] + config["interval"]).isoformat() if config["last_run"] > 0 else "soon"
                    }
                    for name, config in self.research_cycles.items()
                },
                "uptime_minutes": (datetime.now() - datetime.fromisoformat(self.system_stats["service_started"])).total_seconds() / 60,
                "status_updated": datetime.now().isoformat()
            }
            
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving system status: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            "running": self.running,
            "stats": self.system_stats,
            "research_tracks": self.research_cycles,
            "results_directory": str(self.research_results_dir)
        }

def run_background_service():
    """Main entry point for the background service."""
    
    print("🤖 Autonomous AI Research Service")
    print("=" * 50)
    print("Starting continuous background research...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        service = ContinuousResearchService()
        service.start_service()
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Service error: {e}")
        logger.error(f"Service error: {e}")
    finally:
        print("👋 Goodbye!")

if __name__ == "__main__":
    run_background_service() 