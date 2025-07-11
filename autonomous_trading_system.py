"""
Autonomous Trading System
A true alpha-hunting system that discovers opportunities, researches them, and creates dynamic strategies.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.autonomous_alpha_hunter import autonomous_alpha_hunter
from agents.decision_tree import DecisionTree, NodeType
from tools.web_researcher import web_researcher
from tools.calculator import calculator
from tools.data_fetcher import data_fetcher
from core.config import config
from core.openai_manager import openai_manager
from core.pnl_tracker import pnl_tracker
from core.ai_risk_monitor import ai_risk_monitor
from utils.logger import logger  # type: ignore


class AutonomousTradingSystem:
    """
    Complete autonomous trading system that:
    1. Hunts for alpha opportunities globally
    2. Researches opportunities using web tools
    3. Creates dynamic short-term strategies
    4. Tracks performance and learns from outcomes
    """
    
    def __init__(self):
        self.system_memory = []
        self.active_strategies = []
        self.performance_history = []
        self.is_running = False
        self.decision_tree: Optional[DecisionTree] = None
    
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
            if not config.openai_api_key:
                return base_strategy
            
            # Extract key research insights
            sentiment = research.get("sentiment_analysis", {})
            fundamentals = research.get("fundamental_analysis", {})
            news = research.get("news_analysis", {})
            report = research.get("report", {})
            
            # LLM integrates research with strategy
            enhancement_prompt = f"""You are enhancing a trading strategy with comprehensive research insights.
            
            Base Strategy:
            {json.dumps(base_strategy, indent=2)}
            
            Research Insights:
            - Sentiment: {sentiment.get('sentiment', 'neutral')} (strength: {sentiment.get('strength', 0.5)})
            - Fundamentals: {fundamentals.get('financial_health', 'unknown')} health, {fundamentals.get('valuation', 'unknown')} valuation
            - News Impact: {news.get('impact', 'neutral')} with {news.get('time_sensitivity', 'unknown')} timing
            - Research Recommendation: {report.get('recommendation', 'HOLD')} (confidence: {report.get('confidence', 0.5)})
            
            Detailed Research:
            {json.dumps(research, indent=2)}
            
            Enhance the strategy by:
            1. Adjusting position size based on research confidence
            2. Refining entry/exit criteria with research insights
            3. Updating risk assessment with research findings
            4. Modifying time horizon based on catalysts
            5. Integrating sentiment and fundamental factors
            
            Respond with enhanced strategy in JSON:
            {{
                "primary_ticker": "TICKER",
                "action": "BUY/SELL/HOLD",
                "position_size": 0.0-0.2,
                "entry_criteria": "enhanced entry conditions",
                "exit_criteria": "enhanced exit conditions",
                "stop_loss": percentage,
                "take_profit": percentage,
                "time_horizon": "enhanced timeline",
                "confidence": 0.0-1.0,
                "risk_level": "LOW/MEDIUM/HIGH",
                "alpha_thesis": "research-enhanced thesis",
                "research_factors": ["key research insight 1", "key research insight 2"],
                "catalyst_timeline": "when catalysts expected",
                "sentiment_factor": 0.0-1.0,
                "fundamental_factor": 0.0-1.0
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": enhancement_prompt}
            ], temperature=0.2)
            
            enhanced_strategy = json.loads(response.get("content", "{}"))
            
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