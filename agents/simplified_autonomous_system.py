"""
Simplified Autonomous Trading System

This system implements the whitepaper architecture with 5 core agents:
1. Mission Agent - Maintains mission alignment and strategic direction
2. Research Agent - Discovers alpha opportunities and market insights
3. Analysis Agent - Performs technical and fundamental analysis
4. Execution Agent - Executes trades and manages positions
5. Monitor Agent - Monitors system health and performance

The system is mission-driven, agile, connected, collaborative, and radically transparent.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from utils.logger import logger
from core.governor_directive_system import governor_directive_system, SystemContext
from core.central_event_bus import central_event_bus, EventType, EventPriority
from agents.agent_monitoring_system import agent_monitor
from core.pnl_tracker import pnl_tracker
from core.performance_tracker import performance_tracker
from core.alpaca_client import alpaca_client

class AgentType(Enum):
    """Core agent types in the simplified system"""
    MISSION = "mission"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    MONITOR = "monitor"

@dataclass
class AgentThought:
    """Standardized agent thought structure"""
    agent_id: str
    agent_type: AgentType
    thought: str
    reasoning: str
    confidence: float
    action_taken: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class SimplifiedAutonomousSystem:
    """Simplified autonomous trading system with 5 core agents"""
    
    def __init__(self):
        self.running = False
        self.agents = {}
        self.thought_stream = []
        self.mission = "Discover the smartest and greatest upside that nobody is looking at"
        self.current_strategy = "organic_alpha_hunting"
        self.system_mode = "normal"
        
        # Initialize core agents
        self._initialize_agents()
        
        logger.info("🧠 Simplified Autonomous System initialized")
    
    def _initialize_agents(self):
        """Initialize the 5 core agents"""
        self.agents = {
            "mission_agent": MissionAgent("mission_agent"),
            "research_agent": ResearchAgent("research_agent"),
            "analysis_agent": AnalysisAgent("analysis_agent"),
            "execution_agent": ExecutionAgent("execution_agent"),
            "monitor_agent": MonitorAgent("monitor_agent")
        }
        
        # Register agents with monitoring system
        for agent_id, agent in self.agents.items():
            agent_monitor.register_agent(agent_id, {
                "type": agent.agent_type.value,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "status": "active"
            })
        
        logger.info(f"✅ Initialized {len(self.agents)} core agents")
    
    async def run(self):
        """Main autonomous system loop"""
        self.running = True
        logger.info("🚀 Starting simplified autonomous system")
        
        try:
            while self.running:
                # Get current system context
                context = governor_directive_system.get_system_context()
                
                # Check for emergency stops or system mode changes
                if context.system_mode == "emergency":
                    logger.warning("🛑 Emergency mode detected - pausing autonomous operations")
                    await asyncio.sleep(30)
                    continue
                
                # Run one cycle of autonomous operations
                await self._run_cycle(context)
                
                # Wait before next cycle
                await asyncio.sleep(60)  # 1 minute between cycles
                
        except asyncio.CancelledError:
            logger.info("🛑 Autonomous system cancelled")
        except Exception as e:
            logger.error(f"❌ Error in autonomous system: {e}")
        finally:
            self.running = False
            logger.info("🛑 Autonomous system stopped")
    
    async def _run_cycle(self, context: SystemContext):
        """Run one cycle of autonomous operations"""
        try:
            # Step 1: Mission Agent - Update mission and strategy
            mission_thought = await self.agents["mission_agent"].think(context)
            await self._broadcast_thought(mission_thought)
            
            # Step 2: Research Agent - Discover opportunities
            research_thought = await self.agents["research_agent"].think(context)
            await self._broadcast_thought(research_thought)
            
            # Step 3: Analysis Agent - Analyze opportunities
            if research_thought.metadata.get("opportunity_found"):
                analysis_thought = await self.agents["analysis_agent"].think(context, research_thought.metadata)
                await self._broadcast_thought(analysis_thought)
                
                # Step 4: Execution Agent - Execute if analysis is positive
                if analysis_thought.confidence > 0.7:  # High confidence threshold
                    execution_thought = await self.agents["execution_agent"].think(context, analysis_thought.metadata)
                    await self._broadcast_thought(execution_thought)
            
            # Step 5: Monitor Agent - Monitor system health
            monitor_thought = await self.agents["monitor_agent"].think(context)
            await self._broadcast_thought(monitor_thought)
            
            # Update agent heartbeats
            for agent_id in self.agents:
                agent_monitor.update_heartbeat(agent_id)
            
        except Exception as e:
            logger.error(f"❌ Error in autonomous cycle: {e}")
    
    async def _broadcast_thought(self, thought: AgentThought):
        """Broadcast agent thought to all connected clients"""
        try:
            # Add to thought stream
            self.thought_stream.append(thought)
            
            # Keep only last 100 thoughts
            if len(self.thought_stream) > 100:
                self.thought_stream = self.thought_stream[-100:]
            
            # Broadcast via central event bus
            central_event_bus.capture_ai_thought(
                thought.agent_type.value,
                thought.thought,
                {
                    "agent_id": thought.agent_id,
                    "reasoning": thought.reasoning,
                    "confidence": thought.confidence,
                    "action_taken": thought.action_taken,
                    "metadata": thought.metadata
                }
            )
            
            # Log the thought
            logger.info(f"🧠 {thought.agent_id}: {thought.thought}")
            
        except Exception as e:
            logger.error(f"Error broadcasting thought: {e}")
    
    def stop(self):
        """Stop the autonomous system"""
        self.running = False
        logger.info("🛑 Autonomous system stop requested")

class BaseAgent:
    """Base class for all agents in the simplified system"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, description: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.description = description
        self.capabilities = capabilities
    
    async def think(self, context: SystemContext, additional_data: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Generate a thought based on current context"""
        raise NotImplementedError("Subclasses must implement think method")
    
    def _create_thought(self, thought: str, reasoning: str, confidence: float, 
                       action_taken: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Create a standardized agent thought"""
        return AgentThought(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            thought=thought,
            reasoning=reasoning,
            confidence=confidence,
            action_taken=action_taken,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

class MissionAgent(BaseAgent):
    """Mission Agent - Maintains mission alignment and strategic direction"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.MISSION,
            description="Maintains mission alignment and strategic direction",
            capabilities=["mission_alignment", "strategy_planning", "goal_setting"]
        )
    
    async def think(self, context: SystemContext, additional_data: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Think about mission alignment and strategic direction"""
        
        # Check if mission is being followed
        current_mission = context.mission
        current_strategy = context.current_strategy
        
        # Analyze if current activities align with mission
        research_priorities = context.research_priorities
        active_directives = len(governor_directive_system.get_active_directives())
        
        # Generate thought based on current state
        if "alpha" in research_priorities and "discovery" in research_priorities:
            thought = f"Mission alignment confirmed: Focused on alpha discovery as per mission '{current_mission}'"
            reasoning = f"Current research priorities {research_priorities} align with mission. Strategy '{current_strategy}' supports alpha discovery."
            confidence = 0.9
            action_taken = "Mission alignment verified"
        else:
            thought = f"Mission alignment check: Current focus may need adjustment to better align with '{current_mission}'"
            reasoning = f"Research priorities {research_priorities} could be better aligned with alpha discovery mission."
            confidence = 0.7
            action_taken = "Mission alignment review completed"
        
        return self._create_thought(
            thought=thought,
            reasoning=reasoning,
            confidence=confidence,
            action_taken=action_taken,
            metadata={
                "mission": current_mission,
                "strategy": current_strategy,
                "research_priorities": research_priorities,
                "active_directives": active_directives
            }
        )

class ResearchAgent(BaseAgent):
    """Research Agent - Discovers alpha opportunities and market insights"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.RESEARCH,
            description="Discovers alpha opportunities and market insights",
            capabilities=["opportunity_discovery", "market_research", "trend_analysis"]
        )
    
    async def think(self, context: SystemContext, additional_data: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Think about alpha opportunities and market research"""
        
        # Simulate research activities
        research_topics = ["AI sector momentum", "EV market trends", "Biotech breakthroughs", "Clean energy adoption"]
        current_topic = research_topics[hash(str(datetime.utcnow().hour)) % len(research_topics)]
        
        # Simulate opportunity discovery
        opportunity_found = hash(str(datetime.utcnow().minute)) % 3 == 0  # 33% chance of finding opportunity
        
        if opportunity_found:
            thought = f"Alpha opportunity discovered: {current_topic} showing strong momentum and potential"
            reasoning = f"Research into {current_topic} revealed positive market sentiment, increasing volume, and favorable technical indicators."
            confidence = 0.8
            action_taken = "Opportunity identified for analysis"
            metadata = {
                "opportunity_found": True,
                "topic": current_topic,
                "sector": current_topic.split()[0],
                "sentiment": "positive",
                "volume_trend": "increasing"
            }
        else:
            thought = f"Research update: Continuing analysis of {current_topic} - no clear opportunity yet"
            reasoning = f"Ongoing research into {current_topic} shows mixed signals. Continuing monitoring for clearer patterns."
            confidence = 0.6
            action_taken = "Research continued"
            metadata = {
                "opportunity_found": False,
                "topic": current_topic,
                "status": "monitoring"
            }
        
        return self._create_thought(
            thought=thought,
            reasoning=reasoning,
            confidence=confidence,
            action_taken=action_taken,
            metadata=metadata
        )

class AnalysisAgent(BaseAgent):
    """Analysis Agent - Performs technical and fundamental analysis"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.ANALYSIS,
            description="Performs technical and fundamental analysis",
            capabilities=["technical_analysis", "fundamental_analysis", "risk_assessment"]
        )
    
    async def think(self, context: SystemContext, additional_data: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Think about analysis of opportunities"""
        
        if not additional_data or not additional_data.get("opportunity_found"):
            thought = "No opportunity to analyze - waiting for research findings"
            reasoning = "Research agent has not identified any opportunities for analysis."
            confidence = 0.5
            action_taken = "Waiting for research input"
            metadata = {"status": "waiting"}
        else:
            topic = additional_data.get("topic", "Unknown")
            sector = additional_data.get("sector", "Unknown")
            
            # Simulate analysis results
            technical_score = 0.7 + (hash(topic) % 30) / 100  # 0.7-1.0
            fundamental_score = 0.6 + (hash(sector) % 40) / 100  # 0.6-1.0
            risk_score = 0.3 + (hash(str(datetime.utcnow())) % 40) / 100  # 0.3-0.7
            
            overall_score = (technical_score + fundamental_score + risk_score) / 3
            
            if overall_score > 0.7:
                thought = f"Analysis complete: {topic} shows strong technical and fundamental indicators"
                reasoning = f"Technical analysis score: {technical_score:.2f}, Fundamental score: {fundamental_score:.2f}, Risk score: {risk_score:.2f}. Overall positive outlook."
                confidence = overall_score
                action_taken = "Analysis approved for execution"
                metadata = {
                    "topic": topic,
                    "technical_score": technical_score,
                    "fundamental_score": fundamental_score,
                    "risk_score": risk_score,
                    "overall_score": overall_score,
                    "recommendation": "execute"
                }
            else:
                thought = f"Analysis complete: {topic} shows mixed signals - not recommended for execution"
                reasoning = f"Technical analysis score: {technical_score:.2f}, Fundamental score: {fundamental_score:.2f}, Risk score: {risk_score:.2f}. Insufficient confidence for execution."
                confidence = overall_score
                action_taken = "Analysis rejected"
                metadata = {
                    "topic": topic,
                    "technical_score": technical_score,
                    "fundamental_score": fundamental_score,
                    "risk_score": risk_score,
                    "overall_score": overall_score,
                    "recommendation": "reject"
                }
        
        return self._create_thought(
            thought=thought,
            reasoning=reasoning,
            confidence=confidence,
            action_taken=action_taken,
            metadata=metadata
        )

class ExecutionAgent(BaseAgent):
    """Execution Agent - Executes trades and manages positions"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.EXECUTION,
            description="Executes trades and manages positions",
            capabilities=["trade_execution", "position_management", "risk_control"]
        )
    
    async def think(self, context: SystemContext, additional_data: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Think about trade execution and position management"""
        
        if not additional_data or additional_data.get("recommendation") != "execute":
            thought = "No trades to execute - waiting for analysis approval"
            reasoning = "Analysis agent has not approved any opportunities for execution."
            confidence = 0.5
            action_taken = "Waiting for analysis approval"
            metadata = {"status": "waiting"}
        else:
            topic = additional_data.get("topic", "Unknown")
            overall_score = additional_data.get("overall_score", 0.0)
            
            # Check risk parameters
            risk_params = context.risk_parameters
            max_position_size = risk_params.get("max_position_size", 0.02)
            max_daily_loss = risk_params.get("max_daily_loss", 0.05)
            
            # Simulate position sizing based on confidence
            position_size = max_position_size * overall_score
            
            # Check if we should execute (paper trading only)
            if context.system_mode == "paper_trading":
                thought = f"Paper trade executed: {topic} with {position_size:.1%} position size"
                reasoning = f"Analysis approved with {overall_score:.2f} confidence. Position sized at {position_size:.1%} of portfolio based on risk parameters."
                confidence = overall_score
                action_taken = "Paper trade executed"
                metadata = {
                    "topic": topic,
                    "position_size": position_size,
                    "confidence": overall_score,
                    "trade_type": "paper",
                    "execution_time": datetime.utcnow().isoformat()
                }
            else:
                thought = f"Trade execution blocked: System not in paper trading mode"
                reasoning = f"Analysis approved but system mode '{context.system_mode}' does not allow execution."
                confidence = 0.0
                action_taken = "Execution blocked"
                metadata = {
                    "topic": topic,
                    "reason": "system_mode",
                    "system_mode": context.system_mode
                }
        
        return self._create_thought(
            thought=thought,
            reasoning=reasoning,
            confidence=confidence,
            action_taken=action_taken,
            metadata=metadata
        )

class MonitorAgent(BaseAgent):
    """Monitor Agent - Monitors system health and performance"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.MONITOR,
            description="Monitors system health and performance",
            capabilities=["health_monitoring", "performance_tracking", "alert_generation"]
        )
    
    async def think(self, context: SystemContext, additional_data: Optional[Dict[str, Any]] = None) -> AgentThought:
        """Think about system health and performance monitoring"""
        
        # Get system metrics
        try:
            performance = performance_tracker.get_performance_summary()
            positions = pnl_tracker.get_positions()
            trades = pnl_tracker.get_recent_trades(10)
            
            # Calculate health indicators
            win_rate = performance.get("win_rate", 0.0)
            total_pnl = performance.get("total_pnl", 0.0)
            active_positions = len(positions)
            recent_trades = len(trades)
            
            # Assess system health
            if win_rate > 0.6 and total_pnl > 0:
                health_status = "excellent"
                thought = f"System health excellent: {win_rate:.1%} win rate, ${total_pnl:.2f} PnL, {active_positions} positions"
                confidence = 0.9
            elif win_rate > 0.5:
                health_status = "good"
                thought = f"System health good: {win_rate:.1%} win rate, ${total_pnl:.2f} PnL, {active_positions} positions"
                confidence = 0.7
            else:
                health_status = "warning"
                thought = f"System health warning: {win_rate:.1%} win rate, ${total_pnl:.2f} PnL - monitoring closely"
                confidence = 0.5
            
            reasoning = f"Performance metrics: Win rate {win_rate:.1%}, Total PnL ${total_pnl:.2f}, Active positions {active_positions}, Recent trades {recent_trades}"
            action_taken = "Health assessment completed"
            
            metadata = {
                "health_status": health_status,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "active_positions": active_positions,
                "recent_trades": recent_trades,
                "system_mode": context.system_mode
            }
            
        except Exception as e:
            thought = f"System health monitoring error: {str(e)}"
            reasoning = f"Error occurred while monitoring system health: {str(e)}"
            confidence = 0.0
            action_taken = "Monitoring error"
            metadata = {"error": str(e)}
        
        return self._create_thought(
            thought=thought,
            reasoning=reasoning,
            confidence=confidence,
            action_taken=action_taken,
            metadata=metadata
        )

# Global instance for easy access
simplified_autonomous_system = SimplifiedAutonomousSystem() 