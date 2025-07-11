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
import os
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from agents.parallel_execution_system import execution_engine, ExecutionPriority
from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
from autonomous_trading_system import AutonomousTradingSystem
from tools.data_fetcher import data_fetcher
from core.central_event_bus import central_event_bus

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
        
        # Initialize database for logging
        self.db_path = Path("research_data/research.db")
        self._init_database()
        
        # Initialize autonomous trading system for Monte Carlo search
        self.autonomous_trader = AutonomousTradingSystem()
        
        # Research configuration
        self.research_cycles = {
            "alpha_discovery": {
                "interval": 900,  # 15 minutes
                "last_run": time.time() - 1000,  # Force immediate run for testing
                "agent_specialization": "alpha_hunting",
                "enabled": True,
                "monte_carlo_enabled": True
            },
            "market_monitoring": {
                "interval": 600,  # 10 minutes  
                "last_run": time.time() - 700,  # Force immediate run for testing
                "agent_specialization": "market_analysis",
                "enabled": True,
                "monte_carlo_enabled": True
            },
            "sentiment_tracking": {
                "interval": 1200,  # 20 minutes
                "last_run": time.time() - 1300,  # Force immediate run for testing
                "agent_specialization": "sentiment_analysis", 
                "enabled": True,
                "monte_carlo_enabled": False
            },
            "technical_analysis": {
                "interval": 1800,  # 30 minutes
                "last_run": time.time() - 1900,  # Force immediate run for testing
                "agent_specialization": "technical_analysis",
                "enabled": True,
                "monte_carlo_enabled": True
            },
            "risk_assessment": {
                "interval": 3600,  # 1 hour
                "last_run": time.time() - 3700,  # Force immediate run for testing
                "agent_specialization": "risk_assessment",
                "enabled": True,
                "monte_carlo_enabled": True
            },
            "deep_research": {
                "interval": 7200,  # 2 hours
                "last_run": time.time() - 7300,  # Force immediate run for testing
                "agent_specialization": "fundamental_research",
                "enabled": True,
                "monte_carlo_enabled": True
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
        
        print("🤖 Autonomous AI Research Service")
        print("=" * 50)
        print("Starting continuous background research...")
        print("Press Ctrl+C to stop")
        print("=" * 50)
    
    def _init_database(self):
        """Initialize the research database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create research cycles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS research_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_name TEXT NOT NULL,
                    specialization TEXT NOT NULL,
                    research_objective TEXT,
                    market_context TEXT,
                    result TEXT,
                    insights_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'completed',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create system logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    track_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✅ Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def _log_to_db(self, level: str, message: str, track_name: Optional[str] = None):
        """Log message to database instead of file."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_logs (level, message, track_name, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (level, message, track_name, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database logging error: {e}")
    
    def _save_research_result(self, track_name: str, result: Dict[str, Any]):
        """Save research result to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract data for database
            specialization = result.get("specialization", "unknown")
            research_objective = result.get("research_objective", "")
            market_context = json.dumps(result.get("market_context", {}))
            result_json = json.dumps(result)
            insights_count = len(result.get("insights", []))
            
            cursor.execute('''
                INSERT INTO research_cycles 
                (track_name, specialization, research_objective, market_context, result, insights_count, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (track_name, specialization, research_objective, market_context, result_json, insights_count, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Also save research tree to central event bus database
            if "decision_tree" in result:
                tree_id = result["decision_tree"].get("id", f"{track_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                agent_name = result["decision_tree"].get("agent_name", f"enhanced_{track_name}_agent")
                root_id = result["decision_tree"].get("root_id", "root")
                
                # Prepare tree data for central database
                tree_data = {
                    "research_track": track_name,
                    "specialization": specialization,
                    "completed_at": datetime.now().isoformat(),
                    "decision_tree": result["decision_tree"],
                    "tree_metadata": {
                        "total_nodes": len(result["decision_tree"].get("nodes", {})),
                        "insights_count": insights_count,
                        "agent_name": agent_name
                    },
                    "ai_thoughts": result.get("ai_thoughts", []),
                    "insights": result.get("insights", []),
                    "events": result.get("events", [])
                }
                
                central_event_bus.save_research_tree(tree_id, agent_name, track_name, root_id, tree_data)
                self._log_to_db("INFO", f"🌳 Saved research tree {tree_id} to central database", track_name)
            
            self._log_to_db("INFO", f"💾 Saved research results for {track_name}", track_name)
            
        except Exception as e:
            self._log_to_db("ERROR", f"Error saving research result: {e}", track_name)
    
    def start_service(self):
        """Start the continuous research service."""
        try:
            self.running = True
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start the main research loop
            asyncio.run(self._main_research_loop())
            
        except Exception as e:
            self._log_to_db("ERROR", f"Service startup error: {e}")
            self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self._log_to_db("INFO", f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def _main_research_loop(self):
        """Main research loop that coordinates all research tracks."""
        
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
                            self._log_to_db("ERROR", f"Research track {track_name} failed: {e}", track_name)
                            self.system_stats["failed_cycles"] += 1
                    
                    self.system_stats["total_research_cycles"] += len(research_tasks)
                    self.system_stats["last_cycle_time"] = datetime.now().isoformat()
                
                # Update system status file
                self._save_system_status()
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self._log_to_db("ERROR", f"Main loop error: {e}")
                # Don't crash the service on errors, just wait and continue
                await asyncio.sleep(120)  # Wait 2 minutes on errors before retrying
        
        self._log_to_db("INFO", "🛑 Research service stopped")
    
    async def _run_research_track(self, track_name: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run a single research track."""
        try:
            print(f"🔍 Running research track: {track_name}")
            
            # Check for ongoing research to continue
            ongoing_research = await self._check_ongoing_research(track_name, config["agent_specialization"])
            
            if ongoing_research:
                print(f"🔄 Continuing ongoing research for {track_name}")
                result = await self._continue_ongoing_research(ongoing_research, track_name, config)
            else:
                print(f"🆕 Starting new research for {track_name}")
                # Generate research objective
                research_objective = await self._generate_research_objective(track_name, config["agent_specialization"])
                
                # Get market context
                market_context = await self._get_market_context()
                
                # Run the main research cycle
                if track_name == "deep_research":
                    result = await self._run_deep_research(research_objective, market_context)
                elif track_name == "monte_carlo_search":
                    result = await self._run_monte_carlo_search(track_name, research_objective, market_context)
                else:
                    result = await self._run_single_agent_research(config["agent_specialization"], research_objective, market_context)
                
                # Run Monte Carlo search if enabled for this track
                if result and config.get("monte_carlo_enabled", False):
                    print(f"🎯 Running Monte Carlo search for {track_name}")
                    mcts_result = await self._run_monte_carlo_search(track_name, research_objective, market_context)
                    if mcts_result:
                        result["monte_carlo_search"] = mcts_result
                        print(f"✅ Monte Carlo search integrated for {track_name}")
            
            if result:
                # Save result to database
                self._save_research_result(track_name, result)
                
                # Update system stats
                self.system_stats["successful_cycles"] += 1
                self.system_stats["insights_generated"] += len(result.get("insights", []))
                
                print(f"✅ Research track {track_name} completed successfully")
                return result
            else:
                self.system_stats["failed_cycles"] += 1
                print(f"❌ Research track {track_name} failed")
                return None
                
        except Exception as e:
            self.system_stats["failed_cycles"] += 1
            self._log_to_db("ERROR", f"Research track failed: {e}", track_name)
            print(f"❌ Research track {track_name} error: {e}")
            return None
    
    async def _check_ongoing_research(self, track_name: str, specialization: str) -> Optional[Dict[str, Any]]:
        """Check if there's ongoing research for this track."""
        try:
            from core.central_event_bus import central_event_bus
            
            # Check for existing research trees
            existing_trees = central_event_bus.get_research_trees(agent_name=f"research_agent_{specialization}", track_name=track_name)
            
            if existing_trees:
                latest_tree = existing_trees[0]
                tree_data = latest_tree["tree_data"]
                
                # Check if tree has active nodes or ongoing Monte Carlo search
                active_nodes = 0
                mcts_nodes = 0
                
                for node_dict in tree_data.get("nodes", {}).values():
                    if node_dict.get("status") in ["pending", "in_progress"]:
                        active_nodes += 1
                    if node_dict.get("monte_carlo_visits", 0) > 0:
                        mcts_nodes += 1
                
                if active_nodes > 0 or mcts_nodes > 0:
                    return {
                        "tree_id": latest_tree["tree_id"],
                        "tree_data": tree_data,
                        "active_nodes": active_nodes,
                        "mcts_nodes": mcts_nodes,
                        "last_updated": latest_tree["updated_at"]
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to check ongoing research: {e}")
            return None
    
    async def _continue_ongoing_research(self, ongoing_research: Dict[str, Any], track_name: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Continue ongoing research from where it left off."""
        try:
            from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
            from agents.decision_tree import DecisionTree
            
            # Create research agent with existing tree
            research_agent = EnhancedAutonomousAgent(
                agent_id=f"research_agent_{config['agent_specialization']}", 
                specialization=config["agent_specialization"]
            )
            
            # Load existing decision tree
            research_agent.decision_tree = DecisionTree(
                tree_id=ongoing_research["tree_id"],
                agent_name=f"research_agent_{config['agent_specialization']}",
                track_name=track_name
            )
            
            print(f"🔄 Continuing research with {ongoing_research['active_nodes']} active nodes and {ongoing_research['mcts_nodes']} MCTS nodes")
            
            # Continue the research cycle
            market_context = await self._get_market_context()
            
            # Continue with existing research objective or generate new one
            if research_agent.decision_tree.root_id and research_agent.decision_tree.root_id in research_agent.decision_tree.nodes:
                root_node = research_agent.decision_tree.nodes[research_agent.decision_tree.root_id]
                research_objective = root_node.content.replace("Research Objective: ", "")
            else:
                research_objective = await self._generate_research_objective(track_name, config["agent_specialization"])
            
            # Continue research cycle
            result = await research_agent.autonomous_research_cycle(
                research_objective=research_objective,
                context=market_context
            )
            
            # Continue Monte Carlo search if it was in progress
            if config.get("monte_carlo_enabled", False) and ongoing_research["mcts_nodes"] > 0:
                print(f"🎯 Continuing Monte Carlo search for {track_name}")
                await research_agent.decision_tree.run_monte_carlo_search(
                    iterations=20,  # Continue with fewer iterations
                    research_agent=research_agent
                )
                result["monte_carlo_continued"] = True
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to continue ongoing research: {e}")
            return None
    
    async def _run_deep_research(self, research_objective: str, market_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run deep research using multi-agent orchestration."""
        try:
            # Use the execution engine for deep research
            result = await execution_engine.execute_parallel_research_mission(
                mission_objective=research_objective,
                context=market_context,
                priority=ExecutionPriority.NORMAL
            )
            return result
        except Exception as e:
            self._log_to_db("ERROR", f"Deep research failed: {e}", "deep_research")
            return None
    
    async def _run_single_agent_research(self, specialization: str, research_objective: str, market_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run research with a single enhanced autonomous agent."""
        try:
            agent = EnhancedAutonomousAgent(agent_id=f"research_agent_{specialization}", specialization=specialization)
            result = await agent.autonomous_research_cycle(
                research_objective=research_objective,
                context=market_context
            )
            return result
        except Exception as e:
            self._log_to_db("ERROR", f"Single agent research failed: {e}", specialization)
            return None
    
    async def _run_monte_carlo_search(self, track_name: str, research_objective: str, market_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run Monte Carlo search for decision optimization."""
        try:
            print(f"🎯 Running Monte Carlo search for {track_name}")
            
            # Create opportunity data for Monte Carlo search
            opportunity_data = {
                "theme": f"{track_name} research",
                "thesis": research_objective,
                "catalysts": market_context.get("catalysts", []),
                "risk_factors": market_context.get("risk_factors", []),
                "market_context": market_context
            }
            
            # Run Monte Carlo search
            mcts_result = await self.autonomous_trader.run_monte_carlo_decision_search(opportunity_data)
            
            # Also run Monte Carlo search on the research agent's decision tree if available
            if hasattr(self.autonomous_trader, 'decision_tree') and self.autonomous_trader.decision_tree:
                # Create a research agent for Monte Carlo simulation
                from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
                research_agent = EnhancedAutonomousAgent(
                    agent_id=f"mcts_agent_{track_name}", 
                    specialization=track_name
                )
                
                # Run Monte Carlo search with research agent
                await self.autonomous_trader.decision_tree.run_monte_carlo_search(
                    iterations=30, 
                    research_agent=research_agent
                )
                
            if mcts_result and "error" not in mcts_result:
                print(f"✅ Monte Carlo search completed for {track_name}")
                print(f"   Best confidence: {mcts_result.get('best_confidence', 0):.3f}")
                print(f"   Tree nodes: {mcts_result.get('tree_summary', {}).get('total_nodes', 0)}")
                
                # Broadcast tree update to frontend
                if self.autonomous_trader.decision_tree:
                    await self.autonomous_trader.decision_tree._broadcast_tree_update()
                
                return {
                    "monte_carlo_search": mcts_result,
                    "track_name": track_name,
                    "research_objective": research_objective,
                    "market_context": market_context,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"❌ Monte Carlo search failed for {track_name}")
                return None
                
        except Exception as e:
            self._log_to_db("ERROR", f"Monte Carlo search failed: {e}", track_name)
            print(f"❌ Monte Carlo search error: {e}")
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
            self._log_to_db("ERROR", f"Error getting market context: {e}", "market_monitoring")
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
    
    def _save_system_status(self):
        """Save current system status for monitoring."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create system status table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_started TEXT,
                    total_research_cycles INTEGER,
                    successful_cycles INTEGER,
                    failed_cycles INTEGER,
                    last_cycle_time TEXT,
                    active_research_tracks INTEGER,
                    insights_generated INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert current status
            cursor.execute('''
                INSERT INTO system_status 
                (service_started, total_research_cycles, successful_cycles, failed_cycles, 
                 last_cycle_time, active_research_tracks, insights_generated, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.system_stats["service_started"],
                self.system_stats["total_research_cycles"],
                self.system_stats["successful_cycles"],
                self.system_stats["failed_cycles"],
                self.system_stats["last_cycle_time"],
                self.system_stats["active_research_tracks"],
                self.system_stats["insights_generated"],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self._log_to_db("ERROR", f"Error saving system status: {e}", "system_status")
    
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
    
    try:
        service = ContinuousResearchService()
        service.start_service()
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Service error: {e}")
        # logger.error(f"Service error: {e}") # This line is removed as per the new_code
    finally:
        print("👋 Goodbye!")

if __name__ == "__main__":
    run_background_service() 