"""
Enhanced Trading System
Main integration point for the autonomous multi-agent system with parallel execution and decision trees.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.parallel_execution_system import execution_engine, ExecutionPriority
from agents.multi_agent_orchestrator import orchestrator
from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
from core.openai_manager import openai_manager
from tools.data_fetcher import data_fetcher
from utils.logger import logger  # type: ignore

class EnhancedTradingSystem:
    """
    Enhanced Trading System with Autonomous Multi-Agent Intelligence
    
    This system features:
    - 8 specialized autonomous agents working in parallel
    - Dynamic decision tree expansion for comprehensive analysis
    - Full tool integration (web research, data analysis, backtesting, etc.)
    - Intelligent coordination and insight synthesis
    - Continuous learning and adaptation
    - Real-time alpha opportunity hunting
    """
    
    def __init__(self):
        self.execution_engine = execution_engine
        self.orchestrator = orchestrator
        self.session_history: List[Dict[str, Any]] = []
        self.alpha_opportunities: List[Dict[str, Any]] = []
        self.system_initialized = False
        
    def initialize_system(self) -> Dict[str, Any]:
        """Initialize the enhanced trading system."""
        try:
            logger.info("Enhanced Trading System | Initializing autonomous agents...")
            
            # Initialize execution engine (already done on import, but we can check status)
            engine_status = self.execution_engine.get_system_status()
            
            # Initialize orchestrator agents (already done on import)
            orchestrator_status = self.orchestrator.get_orchestrator_status()
            
            self.system_initialized = True
            
            initialization_report = {
                "status": "success",
                "execution_engine": {
                    "active_agents": engine_status["execution_engine"]["active_agents"],
                    "agent_specializations": list(self.execution_engine.agents.keys())
                },
                "orchestrator": {
                    "total_agents": orchestrator_status["total_agents"],
                    "available_roles": list(self.orchestrator.agents.keys())
                },
                "capabilities": [
                    "Parallel autonomous research",
                    "Decision tree expansion",
                    "Multi-tool integration",
                    "Real-time alpha hunting",
                    "Continuous learning",
                    "Risk-aware analysis"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Enhanced Trading System | Initialized with {engine_status['execution_engine']['active_agents']} enhanced agents")
            return initialization_report
            
        except Exception as e:
            logger.error(f"System initialization error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def hunt_for_alpha(self, 
                           market_context: Dict[str, Any] = None,
                           focus_areas: List[str] = None,
                           priority: str = "high") -> Dict[str, Any]:
        """
        Main alpha hunting function using the enhanced multi-agent system.
        
        Args:
            market_context: Current market conditions and data
            focus_areas: Specific areas to focus research on
            priority: Research priority (critical/high/normal/low)
        """
        try:
            if not self.system_initialized:
                self.initialize_system()
                
            logger.info("Enhanced Trading System | Starting autonomous alpha hunt")
            
            # Get current market context if not provided
            if market_context is None:
                market_context = await self._gather_market_context()
            
            # Set research focus
            research_objectives = self._determine_research_objectives(market_context, focus_areas)
            
            # Convert priority
            execution_priority = {
                "critical": ExecutionPriority.CRITICAL,
                "high": ExecutionPriority.HIGH,
                "normal": ExecutionPriority.NORMAL,
                "low": ExecutionPriority.LOW
            }.get(priority.lower(), ExecutionPriority.HIGH)
            
            # Execute parallel alpha hunt
            alpha_hunt_results = []
            
            for objective in research_objectives:
                logger.info(f"Executing research mission: {objective}")
                
                # Use parallel execution engine for coordinated research
                mission_result = await self.execution_engine.execute_parallel_research_mission(
                    mission_objective=objective,
                    context=market_context,
                    priority=execution_priority
                )
                
                alpha_hunt_results.append(mission_result)
            
            # Synthesize all mission results
            comprehensive_synthesis = await self._synthesize_alpha_hunt_results(
                alpha_hunt_results, market_context
            )
            
            # Extract actionable alpha opportunities
            alpha_opportunities = self._extract_alpha_opportunities(comprehensive_synthesis)
            
            # Store opportunities for tracking
            self.alpha_opportunities.extend(alpha_opportunities)
            
            # Create final report
            alpha_hunt_session = {
                "session_id": f"alpha_hunt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "market_context": market_context,
                "research_objectives": research_objectives,
                "mission_results": alpha_hunt_results,
                "synthesis": comprehensive_synthesis,
                "alpha_opportunities": alpha_opportunities,
                "system_performance": self._analyze_system_performance(alpha_hunt_results),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store session
            self.session_history.append(alpha_hunt_session)
            
            logger.info(f"Alpha hunt completed: {len(alpha_opportunities)} opportunities identified")
            return alpha_hunt_session
            
        except Exception as e:
            logger.error(f"Alpha hunt error: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _gather_market_context(self) -> Dict[str, Any]:
        """Gather current market context."""
        try:
            # Get market overview
            market_overview = data_fetcher.get_market_overview()
            
            # Get sector data
            sector_data = data_fetcher.get_sector_data()
            
            # Prepare context for agents
            market_context = {
                "market_overview": market_overview,
                "sector_data": sector_data,
                "symbols": ["SPY", "QQQ", "IWM", "TLT", "GLD"],  # Default universe
                "timestamp": datetime.now().isoformat(),
                "market_session": "regular_hours"  # Could be enhanced with session detection
            }
            
            return market_context
            
        except Exception as e:
            logger.error(f"Market context gathering error: {e}")
            return {"error": str(e)}
    
    def _determine_research_objectives(self, 
                                     market_context: Dict[str, Any], 
                                     focus_areas: List[str] = None) -> List[str]:
        """Determine research objectives based on market context and focus areas."""
        
        default_objectives = [
            "Identify short-term alpha opportunities in current market conditions",
            "Analyze cross-asset correlations for potential arbitrage opportunities",
            "Assess sentiment vs fundamental disconnects in major sectors",
            "Evaluate technical pattern breakouts and momentum signals",
            "Research event-driven catalysts and earnings impact opportunities"
        ]
        
        if focus_areas:
            # Customize objectives based on focus areas
            custom_objectives = []
            for area in focus_areas:
                custom_objectives.append(f"Deep research into {area} for alpha opportunities")
            return custom_objectives
        
        # Analyze market context to prioritize objectives
        prioritized_objectives = default_objectives.copy()
        
        # Simple market condition analysis to adjust objectives
        market_data = market_context.get("market_overview", {})
        if market_data:
            # Add volatility-based objective if market is volatile
            # Add sector rotation objective if sector performance is divergent
            # etc. (This could be much more sophisticated)
            pass
        
        return prioritized_objectives[:3]  # Limit to 3 main objectives
    
    async def _synthesize_alpha_hunt_results(self, 
                                           mission_results: List[Dict[str, Any]], 
                                           market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple research missions."""
        try:
            # Extract insights from all missions
            all_insights = []
            all_opportunities = []
            mission_summaries = []
            
            for mission in mission_results:
                if mission.get("error"):
                    continue
                    
                synthesis = mission.get("synthesis", {})
                insights = synthesis.get("synthesis", {}).get("top_opportunities", [])
                
                all_insights.extend(insights)
                
                # Extract opportunities
                for insight in insights:
                    opportunity = {
                        "opportunity": insight.get("opportunity", ""),
                        "supporting_agents": insight.get("supporting_agents", []),
                        "confidence": insight.get("confidence", 0.5),
                        "mission_id": mission.get("mission_id", ""),
                        "source_objective": mission.get("objective", "")
                    }
                    all_opportunities.append(opportunity)
                
                mission_summaries.append({
                    "objective": mission.get("objective", ""),
                    "agents_participated": mission.get("performance", {}).get("successful_tasks", 0),
                    "insights_generated": len(insights),
                    "duration": mission.get("duration", 0)
                })
            
            # Use LLM to synthesize across all missions
            if all_insights:
                synthesis_prompt = f"""You are synthesizing alpha hunting results from multiple autonomous AI research missions.
                
                Market Context: {json.dumps(market_context, indent=2)}
                
                Mission Summaries: {json.dumps(mission_summaries, indent=2)}
                
                All Insights: {json.dumps(all_insights, indent=2)}
                
                Synthesize into:
                1. Top 5 alpha opportunities with highest potential
                2. Cross-mission patterns and confirmations
                3. Risk factors and considerations
                4. Recommended action plan with priorities
                5. Market timing considerations
                
                Focus on opportunities that:
                - Are confirmed by multiple agents/missions
                - Have high confidence scores
                - Are actionable in current market conditions
                - Provide genuine competitive edge
                
                Respond in JSON:
                {{
                    "top_alpha_opportunities": [
                        {{
                            "opportunity": "description",
                            "alpha_potential": "quantified potential",
                            "confidence": 0.0-1.0,
                            "supporting_evidence": ["evidence1", "evidence2"],
                            "action_plan": ["step1", "step2"],
                            "timing": "immediate/short-term/medium-term",
                            "risk_level": "low/medium/high"
                        }}
                    ],
                    "cross_mission_patterns": ["pattern1", "pattern2"],
                    "market_themes": ["theme1", "theme2"],
                    "risk_considerations": ["risk1", "risk2"],
                    "recommended_priorities": [
                        {{"action": "description", "priority": 1, "timeline": "timeframe"}}
                    ],
                    "overall_market_outlook": "outlook summary",
                    "system_confidence": 0.0-1.0
                }}"""
                
                response = await openai_manager.chat_completion([
                    {"role": "user", "content": synthesis_prompt}
                ], temperature=0.3)
                
                synthesis_result = json.loads(response.get("content", "{}"))
                
            else:
                synthesis_result = {
                    "top_alpha_opportunities": [],
                    "synthesis_note": "No insights available for synthesis"
                }
            
            return {
                "comprehensive_synthesis": synthesis_result,
                "mission_count": len(mission_results),
                "total_insights": len(all_insights),
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Alpha hunt synthesis error: {e}")
            return {"synthesis_error": str(e)}
    
    def _extract_alpha_opportunities(self, synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable alpha opportunities from synthesis."""
        
        opportunities = []
        top_opportunities = synthesis.get("comprehensive_synthesis", {}).get("top_alpha_opportunities", [])
        
        for opp in top_opportunities:
            alpha_opportunity = {
                "id": f"alpha_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(opportunities)}",
                "description": opp.get("opportunity", ""),
                "alpha_potential": opp.get("alpha_potential", ""),
                "confidence": opp.get("confidence", 0.5),
                "action_plan": opp.get("action_plan", []),
                "timing": opp.get("timing", "unknown"),
                "risk_level": opp.get("risk_level", "medium"),
                "supporting_evidence": opp.get("supporting_evidence", []),
                "identified_at": datetime.now().isoformat(),
                "status": "identified"
            }
            opportunities.append(alpha_opportunity)
        
        return opportunities
    
    def _analyze_system_performance(self, mission_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall system performance."""
        
        successful_missions = [m for m in mission_results if not m.get("error")]
        total_duration = sum(m.get("duration", 0) for m in successful_missions)
        total_agents_used = sum(
            m.get("performance", {}).get("successful_tasks", 0) 
            for m in successful_missions
        )
        total_insights = sum(
            len(m.get("synthesis", {}).get("synthesis", {}).get("top_opportunities", []))
            for m in successful_missions
        )
        
        return {
            "successful_missions": len(successful_missions),
            "total_missions": len(mission_results),
            "success_rate": len(successful_missions) / len(mission_results) if mission_results else 0,
            "total_duration": total_duration,
            "total_agents_used": total_agents_used,
            "total_insights_generated": total_insights,
            "avg_insights_per_mission": total_insights / len(successful_missions) if successful_missions else 0,
            "system_efficiency": total_insights / total_duration if total_duration > 0 else 0
        }
    
    def get_alpha_opportunities(self, status: str = None, min_confidence: float = None) -> List[Dict[str, Any]]:
        """Get current alpha opportunities with optional filtering."""
        
        opportunities = self.alpha_opportunities.copy()
        
        if status:
            opportunities = [opp for opp in opportunities if opp.get("status") == status]
        
        if min_confidence is not None:
            opportunities = [opp for opp in opportunities if opp.get("confidence", 0) >= min_confidence]
        
        # Sort by confidence and recency
        opportunities.sort(
            key=lambda x: (x.get("confidence", 0), x.get("identified_at", "")), 
            reverse=True
        )
        
        return opportunities
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        
        return {
            "system_initialized": self.system_initialized,
            "session_count": len(self.session_history),
            "alpha_opportunities_tracked": len(self.alpha_opportunities),
            "execution_engine_status": self.execution_engine.get_system_status(),
            "orchestrator_status": self.orchestrator.get_orchestrator_status(),
            "recent_performance": self._get_recent_performance_summary()
        }
    
    def _get_recent_performance_summary(self) -> Dict[str, Any]:
        """Get summary of recent performance."""
        
        if not self.session_history:
            return {"note": "No sessions completed yet"}
        
        recent_sessions = self.session_history[-5:]  # Last 5 sessions
        
        total_opportunities = sum(
            len(session.get("alpha_opportunities", [])) 
            for session in recent_sessions
        )
        
        avg_confidence = 0
        confidence_count = 0
        
        for session in recent_sessions:
            for opp in session.get("alpha_opportunities", []):
                avg_confidence += opp.get("confidence", 0)
                confidence_count += 1
        
        avg_confidence = avg_confidence / confidence_count if confidence_count > 0 else 0
        
        return {
            "recent_sessions": len(recent_sessions),
            "total_opportunities_identified": total_opportunities,
            "avg_opportunity_confidence": avg_confidence,
            "last_session_timestamp": recent_sessions[-1].get("timestamp", "") if recent_sessions else ""
        }

# Global enhanced trading system instance
enhanced_trading_system = EnhancedTradingSystem()

# Demo functions for testing
async def demo_alpha_hunt():
    """Demo function to show the enhanced system in action."""
    
    logger.info("Enhanced Trading System | Starting demo alpha hunt")
    
    # Initialize system
    init_result = enhanced_trading_system.initialize_system()
    logger.info(f"System initialization: {init_result['status']}")
    
    # Run alpha hunt
    alpha_hunt_result = await enhanced_trading_system.hunt_for_alpha(
        focus_areas=["technology sector momentum", "interest rate arbitrage"],
        priority="high"
    )
    
    if alpha_hunt_result.get("error"):
        logger.error(f"Alpha hunt failed: {alpha_hunt_result['error']}")
        return alpha_hunt_result
    
    # Display results
    opportunities = alpha_hunt_result.get("alpha_opportunities", [])
    logger.info(f"Demo completed: {len(opportunities)} alpha opportunities identified")
    
    for i, opp in enumerate(opportunities[:3], 1):  # Show top 3
        logger.info(f"Opportunity {i}: {opp['description']} (confidence: {opp['confidence']:.2f})")
    
    return alpha_hunt_result

if __name__ == "__main__":
    # Run demo
    result = asyncio.run(demo_alpha_hunt())
    print(json.dumps(result, indent=2)) 