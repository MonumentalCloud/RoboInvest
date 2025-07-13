#!/usr/bin/env python3
"""
Autonomous Trading System
Real-time autonomous trading with Monte Carlo decision search and risk management.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from agents.autonomous_alpha_hunter import autonomous_alpha_hunter
from agents.decision_tree import DecisionTree
from tools.web_researcher import web_researcher
from tools.data_fetcher import data_fetcher
from core.ai_risk_monitor import ai_risk_monitor
from core.pnl_tracker import pnl_tracker
from agents.agent_monitoring_system import agent_monitor
from core.governor_directive_system import GovernorDirectiveSystem

logger = logging.getLogger(__name__)

class AutonomousTradingSystem:
    """
    Autonomous trading system with Monte Carlo decision search.
    
    Features:
    - Real-time alpha hunting
    - Monte Carlo decision tree optimization
    - Risk assessment and management
    - Paper trading execution
    - Performance tracking
    - Governor directive integration
    """
    
    def __init__(self):
        self.system_memory = []
        self.active_strategies = []
        self.performance_history = []
        self.is_running = False
        self.decision_tree: Optional[DecisionTree] = None
        
        # Initialize Governor Directive System
        self.governor_system = GovernorDirectiveSystem()
        
        # Register agents with monitoring system
        self._register_agents()
        
        # Subscribe to governor directives
        self._subscribe_to_directives()
    
    def _register_agents(self):
        """Register all autonomous trading agents with the monitoring system."""
        try:
            # Register the main autonomous trading system
            agent_monitor.register_agent("AutonomousTradingSystem", {
                "type": "autonomous_trading",
                "description": "Main autonomous trading orchestrator",
                "capabilities": ["alpha_hunting", "strategy_generation", "risk_management", "paper_trading"],
                "status": "active"
            })
            
            # Register the alpha hunter agent
            agent_monitor.register_agent("AutonomousAlphaHunter", {
                "type": "alpha_hunter",
                "description": "Autonomous alpha opportunity discovery agent",
                "capabilities": ["market_analysis", "opportunity_detection", "alpha_thesis_generation"],
                "status": "active"
            })
            
            # Register the web researcher agent
            agent_monitor.register_agent("WebResearcher", {
                "type": "research",
                "description": "Comprehensive web research and analysis agent",
                "capabilities": ["web_research", "sentiment_analysis", "fundamental_analysis"],
                "status": "active"
            })
            
            # Register the decision tree agent
            agent_monitor.register_agent("DecisionTree", {
                "type": "decision_optimization",
                "description": "Monte Carlo decision tree optimization agent",
                "capabilities": ["decision_search", "confidence_optimization", "path_analysis"],
                "status": "active"
            })
            
            # Register the risk monitor agent
            agent_monitor.register_agent("AIRiskMonitor", {
                "type": "risk_management",
                "description": "AI-powered risk assessment and management agent",
                "capabilities": ["risk_assessment", "position_sizing", "risk_mitigation"],
                "status": "active"
            })
            
            logger.info("✅ All autonomous trading agents registered with monitoring system")
            
        except Exception as e:
            logger.error(f"Error registering agents: {e}")
    
    def _subscribe_to_directives(self):
        """Subscribe to governor directives for real-time updates."""
        try:
            # Create a wrapper function to handle async callback
            def directive_wrapper(directive):
                asyncio.create_task(self._handle_governor_directive(directive))
            
            # Subscribe to all directives
            self.governor_system.subscribe_to_directives(directive_wrapper)
            
            logger.info("✅ Autonomous trading system subscribed to governor directives")
            
        except Exception as e:
            logger.error(f"Error subscribing to directives: {e}")
    
    async def _handle_governor_directive(self, directive):
        """Handle incoming governor directives."""
        try:
            directive_type = directive.directive_type.value
            title = directive.title
            payload = directive.payload
            
            logger.info(f"🔄 Processing governor directive: {title} ({directive_type})")
            
            # Acknowledge the directive
            self.governor_system.acknowledge_directive(
                directive_id=directive.directive_id,
                agent_id="AutonomousTradingSystem"
            )
            
            # Handle different directive types
            if directive_type == "mission_update":
                await self._handle_mission_update(payload)
            elif directive_type == "strategy_change":
                await self._handle_strategy_change(payload)
            elif directive_type == "risk_adjustment":
                await self._handle_risk_adjustment(payload)
            elif directive_type == "research_priority":
                await self._handle_research_priority(payload)
            elif directive_type == "emergency_stop":
                await self._handle_emergency_stop(payload)
            elif directive_type == "system_parameter":
                await self._handle_system_parameter(payload)
            
            # Report completion
            self.governor_system.report_directive_completion(
                directive_id=directive.directive_id,
                agent_id="AutonomousTradingSystem",
                report={
                    "status": "completed",
                    "actions_taken": f"Applied {directive_type} directive",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling governor directive: {e}")
            # Report failure
            self.governor_system.report_directive_completion(
                directive_id=directive.directive_id,
                agent_id="AutonomousTradingSystem",
                report={
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def _handle_mission_update(self, payload: Dict[str, Any]):
        """Handle mission update directives."""
        new_mission = payload.get("mission", "")
        if new_mission:
            logger.info(f"🎯 Mission updated: {new_mission}")
            # Update system context with new mission
            async with self.governor_system.context_update() as context:
                context.mission = new_mission
    
    async def _handle_strategy_change(self, payload: Dict[str, Any]):
        """Handle strategy change directives."""
        new_strategy = payload.get("strategy", "")
        if new_strategy:
            logger.info(f"📈 Strategy changed: {new_strategy}")
            # Update system context with new strategy
            async with self.governor_system.context_update() as context:
                context.current_strategy = new_strategy
    
    async def _handle_risk_adjustment(self, payload: Dict[str, Any]):
        """Handle risk adjustment directives."""
        risk_params = payload.get("risk_parameters", {})
        if risk_params:
            logger.info(f"🛡️ Risk parameters adjusted: {risk_params}")
            # Update system context with new risk parameters
            async with self.governor_system.context_update() as context:
                context.risk_parameters.update(risk_params)
    
    async def _handle_research_priority(self, payload: Dict[str, Any]):
        """Handle research priority directives."""
        priorities = payload.get("research_priorities", [])
        if priorities:
            logger.info(f"🔍 Research priorities updated: {priorities}")
            # Update system context with new research priorities
            async with self.governor_system.context_update() as context:
                context.research_priorities = priorities
    
    async def _handle_emergency_stop(self, payload: Dict[str, Any]):
        """Handle emergency stop directives."""
        reason = payload.get("reason", "Emergency stop initiated")
        logger.warning(f"🚨 EMERGENCY STOP: {reason}")
        
        # Stop all trading activities
        self.is_running = False
        
        # Update system context
        async with self.governor_system.context_update() as context:
            context.system_mode = "emergency_stop"
    
    async def _handle_system_parameter(self, payload: Dict[str, Any]):
        """Handle system parameter directives."""
        trading_rules = payload.get("trading_rules", {})
        if trading_rules:
            logger.info(f"⚙️ Trading rules updated: {trading_rules}")
            # Update system context with new trading rules
            async with self.governor_system.context_update() as context:
                context.trading_rules.update(trading_rules)
    
    async def run_monte_carlo_decision_search(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run Monte Carlo search on decision tree for strategy optimization."""
        try:
            # Create decision tree for this opportunity
            self.decision_tree = DecisionTree(agent_name="AutonomousTrader")
            
            # Create root node
            root_id = self.decision_tree.create_root(
                content=f"Strategy Decision: {opportunity_data.get('theme', 'Alpha Opportunity')}",
                data=opportunity_data
            )
            
            # Add hypothesis nodes
            hypotheses = [
                "High conviction momentum strategy",
                "Mean reversion opportunity", 
                "Catalyst-driven position",
                "Risk-adjusted position sizing",
                "Multi-timeframe approach"
            ]
            
            hypothesis_ids = self.decision_tree.expand_hypotheses(root_id, hypotheses)
            
            # Add research paths for each hypothesis
            for hypothesis_id in hypothesis_ids:
                research_tasks = [
                    {"description": "Technical analysis", "confidence": 0.7},
                    {"description": "Fundamental analysis", "confidence": 0.8},
                    {"description": "Sentiment analysis", "confidence": 0.6},
                    {"description": "Risk assessment", "confidence": 0.9}
                ]
                self.decision_tree.expand_research_paths(hypothesis_id, research_tasks)
            
            # Run Monte Carlo search
            logger.info("AutonomousTrader | Starting Monte Carlo decision search")
            await self.decision_tree.run_monte_carlo_search(iterations=50, research_agent=self)
            
            # Get best path
            best_path = self.decision_tree.find_best_path()
            best_confidence = self.decision_tree.best_confidence
            
            logger.info(f"AutonomousTrader | Monte Carlo search complete. Best confidence: {best_confidence:.3f}")
            
            return {
                "best_path": best_path,
                "best_confidence": best_confidence,
                "tree_summary": self.decision_tree.get_summary()
            }
            
        except Exception as e:
            logger.error(f"Monte Carlo search error: {e}")
            return {"error": str(e)}
    
    async def _autonomous_cycle_async(self) -> Dict[str, Any]:
        """Async version of autonomous cycle with Monte Carlo search."""
        try:
            cycle_start = time.time()
            
            # Step 1: Hunt for alpha opportunities
            logger.info("AutonomousTrader | Hunting for alpha opportunities")
            alpha_strategy = autonomous_alpha_hunter.hunt_for_alpha()
            
            if not alpha_strategy or alpha_strategy.get("confidence", 0) < 0.3:
                logger.warning("AutonomousTrader | No viable alpha opportunities found")
                return self._create_fallback_strategy()
            
            # Step 2: Run Monte Carlo search on decision tree
            opportunity_data = {
                "theme": alpha_strategy.get("opportunity_theme", "Unknown"),
                "thesis": alpha_strategy.get("alpha_thesis", ""),
                "catalysts": alpha_strategy.get("catalysts", []),
                "risk_factors": [alpha_strategy.get("risk_level", "MEDIUM")]
            }
            
            mcts_result = await self.run_monte_carlo_decision_search(opportunity_data)
            
            # Step 3: Deep research on the opportunity
            logger.info(f"AutonomousTrader | Researching opportunity: {alpha_strategy.get('opportunity_theme', 'Unknown')}")
            research_report = await web_researcher.research_opportunity(opportunity_data, [alpha_strategy.get("primary_ticker", "SPY")])
            
            # Step 4: Enhance strategy with research insights
            enhanced_strategy = self._enhance_strategy_with_research(alpha_strategy, research_report)
            
            # Step 5: Final validation and risk assessment
            final_strategy = self._validate_final_strategy(enhanced_strategy)
            
            # Add Monte Carlo results
            final_strategy["monte_carlo_search"] = mcts_result
            
            cycle_time = time.time() - cycle_start
            final_strategy["cycle_time_seconds"] = cycle_time
            
            logger.info(f"AutonomousTrader | Async cycle complete in {cycle_time:.2f}s - Strategy: {final_strategy.get('action', 'HOLD')}")
            
            return final_strategy
            
        except Exception as e:
            logger.error(f"Async autonomous cycle error: {e}")
            return self._create_fallback_strategy()
    
    def start_autonomous_trading(self, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Start the autonomous trading system.
        """
        try:
            logger.info("AutonomousTrader | Starting autonomous trading system")
            self.is_running = True
            
            results = {
                "session_start": datetime.now().isoformat(),
                "iterations": [],
                "final_strategy": None,
                "performance_summary": {},
                "key_insights": []
            }
            
            for iteration in range(max_iterations):
                logger.info(f"AutonomousTrader | Iteration {iteration + 1}/{max_iterations}")
                
                # Run async cycle
                iteration_result = asyncio.run(self._autonomous_cycle_async())
                
                results["iterations"].append({
                    "iteration": iteration + 1,
                    "timestamp": datetime.now().isoformat(),
                    "result": iteration_result
                })
                
                # Check if we found a high-confidence strategy
                if iteration_result.get("confidence", 0) > 0.7:
                    results["final_strategy"] = iteration_result
                    logger.info(f"AutonomousTrader | High confidence strategy found: {iteration_result.get('alpha_thesis', 'Unknown')}")
                    break
                
                # Brief pause between iterations
                time.sleep(2)
            
            # Generate final performance summary
            results["performance_summary"] = self._generate_performance_summary()
            results["key_insights"] = self._extract_key_insights(results["iterations"])
            
            logger.info("AutonomousTrader | Autonomous trading session complete")
            return results
            
        except Exception as e:
            logger.error(f"AutonomousTrader error: {e}")
            self.is_running = False
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _autonomous_cycle(self) -> Dict[str, Any]:
        """
        Single cycle of autonomous trading:
        1. Hunt for alpha opportunities
        2. Research the best opportunity
        3. Create investment strategy
        4. Validate strategy
        """
        try:
            cycle_start = time.time()
            
            # Step 1: Hunt for alpha opportunities
            logger.info("AutonomousTrader | Hunting for alpha opportunities")
            alpha_strategy = autonomous_alpha_hunter.hunt_for_alpha()
            
            if not alpha_strategy or alpha_strategy.get("confidence", 0) < 0.3:
                logger.warning("AutonomousTrader | No viable alpha opportunities found")
                return self._create_fallback_strategy()
            
            # Step 2: Deep research on the opportunity
            logger.info(f"AutonomousTrader | Researching opportunity: {alpha_strategy.get('opportunity_theme', 'Unknown')}")
            
            opportunity_data = {
                "theme": alpha_strategy.get("opportunity_theme", "Unknown"),
                "thesis": alpha_strategy.get("alpha_thesis", ""),
                "catalysts": alpha_strategy.get("catalysts", []),
                "risk_factors": [alpha_strategy.get("risk_level", "MEDIUM")]
            }
            
            tickers = [alpha_strategy.get("primary_ticker", "SPY")]
            
            # Comprehensive web research (sync wrapper)
            research_report = asyncio.run(web_researcher.research_opportunity(opportunity_data, tickers))
            
            # Step 3: Enhance strategy with research insights
            enhanced_strategy = self._enhance_strategy_with_research(alpha_strategy, research_report)
            
            # Step 4: Final validation and risk assessment
            final_strategy = self._validate_final_strategy(enhanced_strategy)
            
            cycle_time = time.time() - cycle_start
            final_strategy["cycle_time_seconds"] = cycle_time
            
            logger.info(f"AutonomousTrader | Cycle complete in {cycle_time:.2f}s - Strategy: {final_strategy.get('action', 'HOLD')}")
            
            return final_strategy
            
        except Exception as e:
            logger.error(f"Autonomous cycle error: {e}")
            return self._create_fallback_strategy()
    
    def _enhance_strategy_with_research(self, base_strategy: Dict[str, Any], research: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance the base strategy with research insights.
        """
        try:
            # Extract key research insights
            sentiment = research.get("sentiment_analysis", {})
            fundamentals = research.get("fundamental_analysis", {})
            news = research.get("news_analysis", {})
            report = research.get("report", {})
            
            # Rule-based strategy enhancement
            enhanced_strategy = base_strategy.copy()
            
            # Extract research metrics
            sentiment_strength = sentiment.get('strength', 0.5)
            sentiment_value = sentiment.get('sentiment', 'neutral')
            fundamental_health = fundamentals.get('financial_health', 'unknown')
            fundamental_score = fundamentals.get('overall_score', 0.5)
            news_impact = news.get('impact', 'neutral')
            research_confidence = report.get('confidence', 0.5)
            
            # Calculate enhanced confidence
            base_confidence = enhanced_strategy.get("confidence", 0.5)
            confidence_factors = [
                base_confidence,
                research_confidence,
                sentiment_strength,
                fundamental_score
            ]
            
            # Weight the factors
            enhanced_confidence = sum(confidence_factors) / len(confidence_factors)
            enhanced_strategy["confidence"] = min(1.0, max(0.0, enhanced_confidence))
            
            # Adjust position size based on research confidence
            base_position = enhanced_strategy.get("position_size", 0.05)
            if research_confidence > 0.7 and sentiment_strength > 0.6:
                enhanced_strategy["position_size"] = min(base_position * 1.3, 0.15)
            elif research_confidence < 0.3 or sentiment_strength < 0.4:
                enhanced_strategy["position_size"] = base_position * 0.7
            
            # Enhance alpha thesis
            current_thesis = enhanced_strategy.get("alpha_thesis", "")
            research_insights = [
                f"Sentiment: {sentiment_value} (strength: {sentiment_strength:.2f})",
                f"Fundamentals: {fundamental_health} (score: {fundamental_score:.2f})",
                f"News: {news_impact} impact"
            ]
            
            enhanced_thesis = f"{current_thesis} | Research: {' | '.join(research_insights)}"
            enhanced_strategy["alpha_thesis"] = enhanced_thesis
            
            # Add research factors
            enhanced_strategy["research_factors"] = research_insights
            
            # Set sentiment and fundamental factors
            enhanced_strategy["sentiment_factor"] = sentiment_strength
            enhanced_strategy["fundamental_factor"] = fundamental_score
            
            # Add research metadata
            enhanced_strategy["research_summary"] = {
                "sentiment": sentiment.get("sentiment", "neutral"),
                "fundamental_score": fundamentals.get("overall_score", 0.5),
                "news_impact": news.get("impact", "neutral"),
                "research_confidence": report.get("confidence", 0.5)
            }
            
            return enhanced_strategy
            
        except Exception as e:
            logger.error(f"Strategy enhancement error: {e}")
            return base_strategy
    
    def _validate_final_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final validation of the strategy before potential execution with comprehensive risk assessment.
        """
        try:
            # Basic validation checks
            ticker = strategy.get("primary_ticker", "SPY")
            action = strategy.get("action", "HOLD")
            confidence = strategy.get("confidence", 0.5)
            position_size = strategy.get("position_size", 0.05)
            
            # Get current market data for validation
            market_data = data_fetcher.get_historical_data(ticker, period="1d")
            
            # Prepare context for risk assessment
            risk_context = {
                "primary_ticker": ticker,
                "action": action,
                "confidence": confidence,
                "position_size": position_size,
                "market_data_available": bool(market_data.get("data")),
                "research_summary": strategy.get("research_summary", {}),
                "alpha_thesis": strategy.get("alpha_thesis", ""),
                "audit_trail_enabled": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Perform comprehensive risk assessment
            risk_check = ai_risk_monitor.check_trading_decision(risk_context)
            risk_assessment = risk_check["assessment"]
            should_proceed = risk_check["should_proceed"]
            mitigated_context = risk_check["mitigated_context"]
            
            # Apply risk mitigations to strategy
            if not should_proceed:
                logger.warning(f"AutonomousTrader | Strategy blocked by risk assessment: {risk_assessment['risk_level']}")
                strategy["action"] = "HOLD"
                strategy["position_size"] = 0.0
                strategy["risk_mitigation"] = "Trading blocked due to high risk"
                strategy["risk_assessment"] = risk_assessment
            else:
                # Apply any risk-based adjustments
                if mitigated_context.get("position_size") != position_size:
                    strategy["position_size"] = mitigated_context["position_size"]
                    strategy["risk_mitigation"] = "Position size reduced by risk management"
                
                if mitigated_context.get("action") != action:
                    strategy["action"] = mitigated_context["action"]
                    strategy["risk_mitigation"] = "Action modified by risk management"
                
                strategy["risk_assessment"] = risk_assessment
            
            # Legacy risk-adjusted validation (additional safeguards)
            if confidence < 0.4:
                strategy["action"] = "HOLD"
                strategy["position_size"] = 0.0
                strategy["validation_note"] = "Low confidence - holding position"
            
            elif strategy["position_size"] > 0.15:  # Cap position size at 15%
                strategy["position_size"] = 0.15
                strategy["validation_note"] = "Position size capped at 15%"
            
            # Add validation metadata
            strategy["validation_timestamp"] = datetime.now().isoformat()
            strategy["market_data_available"] = bool(market_data.get("data"))
            strategy["validated"] = True
            strategy["risk_managed"] = True
            
            logger.info(f"AutonomousTrader | Strategy validated with risk assessment: {action} {ticker} "
                       f"(confidence: {confidence:.2f}, risk: {risk_assessment['risk_level']})")
            
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy validation error: {e}")
            strategy["validated"] = False
            strategy["validation_error"] = str(e)
            strategy["risk_managed"] = False
            return strategy
    
    def _create_fallback_strategy(self) -> Dict[str, Any]:
        """
        Create a conservative fallback strategy when autonomous hunting fails.
        """
        return {
            "primary_ticker": "SPY",
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 0.3,
            "alpha_thesis": "Conservative fallback - market neutral position",
            "time_horizon": "1 day",
            "risk_level": "LOW",
            "fallback": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """
        Generate performance summary of the autonomous trading session.
        """
        try:
            # Get current PnL data
            pnl_data = pnl_tracker.get_performance_summary()
            
            return {
                "total_pnl": pnl_data.get("total_pnl", 0.0),
                "win_rate": pnl_data.get("win_rate", 0.0),
                "total_trades": pnl_data.get("total_trades", 0),
                "active_strategies": len(self.active_strategies),
                "system_uptime": "Session complete",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance summary error: {e}")
            return {"error": str(e)}
    
    def _extract_key_insights(self, iterations: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key insights from the trading session.
        """
        insights = []
        
        try:
            # Analyze iteration results
            high_confidence_strategies = [
                iteration for iteration in iterations
                if iteration.get("result", {}).get("confidence", 0) > 0.6
            ]
            
            if high_confidence_strategies:
                insights.append(f"Found {len(high_confidence_strategies)} high-confidence opportunities")
            
            # Extract common themes
            themes = [
                iteration.get("result", {}).get("opportunity_theme", "Unknown")
                for iteration in iterations
                if iteration.get("result", {}).get("opportunity_theme")
            ]
            
            if themes:
                insights.append(f"Explored opportunities: {', '.join(set(themes))}")
            
            # Performance insights
            final_strategies = [
                iteration.get("result", {}) for iteration in iterations
                if iteration.get("result", {}).get("action") != "HOLD"
            ]
            
            if final_strategies:
                insights.append(f"Generated {len(final_strategies)} actionable strategies")
            else:
                insights.append("Market conditions favored conservative approach")
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight extraction error: {e}")
            return ["Session completed with mixed results"]


# Global instance
autonomous_trading_system = AutonomousTradingSystem()


def demo_autonomous_trading():
    """
    Demonstrate the autonomous trading system.
    """
    print("🚀 Starting Autonomous Alpha-Hunting Trading System")
    print("=" * 60)
    
    # Run the autonomous system
    results = autonomous_trading_system.start_autonomous_trading(max_iterations=3)
    
    # Display results
    print("\n📊 AUTONOMOUS TRADING RESULTS")
    print("=" * 60)
    
    print(f"Session Duration: {len(results.get('iterations', []))} iterations")
    
    if results.get('final_strategy'):
        strategy = results['final_strategy']
        print(f"\n🎯 FINAL STRATEGY:")
        print(f"   Ticker: {strategy.get('primary_ticker', 'N/A')}")
        print(f"   Action: {strategy.get('action', 'N/A')}")
        print(f"   Position Size: {strategy.get('position_size', 0):.1%}")
        print(f"   Confidence: {strategy.get('confidence', 0):.2f}")
        print(f"   Alpha Thesis: {strategy.get('alpha_thesis', 'N/A')}")
        print(f"   Time Horizon: {strategy.get('time_horizon', 'N/A')}")
    
    if results.get('key_insights'):
        print(f"\n🔍 KEY INSIGHTS:")
        for insight in results['key_insights']:
            print(f"   • {insight}")
    
    print(f"\n💡 PERFORMANCE SUMMARY:")
    perf = results.get('performance_summary', {})
    print(f"   Total PnL: ${perf.get('total_pnl', 0.0):.2f}")
    print(f"   Win Rate: {perf.get('win_rate', 0.0):.1%}")
    print(f"   Total Trades: {perf.get('total_trades', 0)}")
    
    print("\n✅ Autonomous trading session complete!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    demo_autonomous_trading()