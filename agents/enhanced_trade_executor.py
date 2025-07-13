# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
import json

from core.alpaca_client import alpaca_client
from core.openai_manager import openai_manager
from core.performance_tracker import performance_tracker
from core.pnl_tracker import pnl_tracker
from agents.experience_learning_system import experience_learning_system
from agents.performance_analyzer_agent import performance_analyzer_agent
from utils.logger import logger  # type: ignore


class EnhancedTradeExecutorAgent:
    """
    Enhanced AI-powered trade executor that learns from experience
    and uses comprehensive analysis for execution decisions.
    """

    DEFAULT_QTY = 1  # For MVP, trade 1 share

    def __init__(self) -> None:
        """Initialize the enhanced trade executor."""
        self.execution_history: List[Dict[str, Any]] = []
        self.agent_id = "enhanced_trade_executor"

    async def __call__(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced trade execution with experience learning integration.
        
        Args:
            decision: Trade decision from strategy agent
            
        Returns:
            Enhanced decision with execution results and learning insights
        """
        action = decision.get("action", "HOLD").upper()
        symbol = decision.get("symbol") or "SPY"
        
        logger.info(f"EnhancedTradeExecutor | Processing {action} decision for {symbol}")

        if action not in ("BUY", "SELL"):
            logger.info("EnhancedTradeExecutor | No trade to execute (HOLD).")
            decision["executed"] = False
            return decision

        if not alpaca_client.is_ready():
            logger.warning("EnhancedTradeExecutor | Alpaca not configured; skipping execution.")
            decision["executed"] = False
            return decision

        try:
            # Retrieve relevant experience for this trade
            experience_data = await self._retrieve_relevant_experience(decision)
            
            # Enhanced AI-powered execution analysis with experience
            execution_analysis = await self._analyze_execution_with_experience(decision, experience_data)
            
            if execution_analysis.get("should_execute", True):
                # Execute the trade
                order = alpaca_client.submit_order(symbol=symbol, qty=self.DEFAULT_QTY, side=action.lower())
                decision["executed"] = True if order else False
                decision["alpaca_order"] = order
                decision["execution_reasoning"] = execution_analysis.get("reasoning", "AI approved execution with experience")
                decision["experience_insights"] = execution_analysis.get("experience_insights", [])
            else:
                decision["executed"] = False
                decision["execution_reasoning"] = execution_analysis.get("reasoning", "AI rejected execution based on experience")
                decision["experience_insights"] = execution_analysis.get("experience_insights", [])

            # Log to performance tracker
            self._log_trade_to_performance_tracker(decision)
            
            # Store execution in history
            self._store_execution_history(decision)
            
            # Trigger performance analysis if this completes a play
            await self._trigger_performance_analysis_if_needed(decision)
            
            logger.info(f"EnhancedTradeExecutor | Decision processed: {decision['executed']}")
            return decision
            
        except Exception as exc:
            logger.error(f"EnhancedTradeExecutor | Execution error: {exc}")
            decision["executed"] = False
            decision["error"] = str(exc)
            return decision

    async def _retrieve_relevant_experience(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant experience data for this trade decision."""
        
        try:
            # Create context for experience retrieval
            context = {
                "symbol": decision.get("symbol"),
                "action": decision.get("action"),
                "confidence": decision.get("confidence"),
                "reasoning": decision.get("reasoning"),
                "market_conditions": decision.get("market_context", {})
            }
            
            # Get experience data for this agent
            experience_data = experience_learning_system.get_agent_experience(self.agent_id, context)
            
            logger.info(f"EnhancedTradeExecutor | Retrieved {len(experience_data.get('relevant_insights', []))} relevant insights")
            return experience_data
            
        except Exception as exc:
            logger.error(f"EnhancedTradeExecutor | Failed to retrieve experience: {exc}")
            return {"shared_experiences": [], "agent_feedback": [], "relevant_insights": []}

    async def _analyze_execution_with_experience(self, decision: Dict[str, Any], experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced execution analysis incorporating experience data."""
        
        # Prepare analysis context
        analysis_context = {
            "decision": decision,
            "experience_data": experience_data,
            "current_market": decision.get("market_context", {}),
            "agent_history": self.execution_history[-5:] if self.execution_history else []
        }
        
        # AI-powered execution analysis with experience
        analysis_prompt = f"""
        You are an expert trade execution analyst with access to historical experience data.
        Analyze this trade execution decision comprehensively:

        DECISION DATA:
        {json.dumps(decision, indent=2)}

        EXPERIENCE DATA:
        {json.dumps(experience_data, indent=2)}

        ANALYSIS CONTEXT:
        {json.dumps(analysis_context, indent=2)}

        Provide execution analysis in JSON format:
        {{
            "should_execute": true/false,
            "reasoning": "detailed reasoning for execution decision",
            "confidence_adjustment": "increase/decrease/maintain",
            "risk_assessment": {{
                "risk_level": "low/medium/high",
                "risk_factors": ["list", "of", "risk", "factors"],
                "risk_mitigation": ["list", "of", "mitigation", "strategies"]
            }},
            "experience_insights": [
                {{
                    "insight": "specific insight from experience",
                    "application": "how to apply this insight",
                    "impact": "high/medium/low"
                }}
            ],
            "execution_recommendations": [
                {{
                    "recommendation": "specific recommendation",
                    "priority": "high/medium/low",
                    "rationale": "reason for recommendation"
                }}
            ],
            "learning_opportunities": [
                {{
                    "opportunity": "specific learning opportunity",
                    "focus_area": "area to focus on",
                    "expected_outcome": "expected learning outcome"
                }}
            ]
        }}
        """
        
        try:
            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are an expert trade execution analyst with deep knowledge of market dynamics, risk management, and AI trading systems."},
                {"role": "user", "content": analysis_prompt}
            ])
            
            analysis = json.loads(response["content"])
            return analysis
            
        except Exception as exc:
            logger.error(f"EnhancedTradeExecutor | Execution analysis failed: {exc}")
            return self._fallback_execution_analysis(decision)

    def _fallback_execution_analysis(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback execution analysis when AI analysis fails."""
        
        # Basic risk assessment
        confidence = decision.get("confidence", 0.5)
        symbol = decision.get("symbol", "SPY")
        
        should_execute = confidence > 0.6  # Basic threshold
        
        return {
            "should_execute": should_execute,
            "reasoning": f"Fallback analysis: confidence {confidence} {'above' if should_execute else 'below'} threshold",
            "confidence_adjustment": "maintain",
            "risk_assessment": {
                "risk_level": "medium",
                "risk_factors": ["AI analysis unavailable"],
                "risk_mitigation": ["Use basic risk controls"]
            },
            "experience_insights": [
                {
                    "insight": "AI analysis system needs attention",
                    "application": "Restore AI analysis capability",
                    "impact": "high"
                }
            ],
            "execution_recommendations": [
                {
                    "recommendation": "Enable AI analysis for better decisions",
                    "priority": "high",
                    "rationale": "Current analysis limited by system issues"
                }
            ],
            "learning_opportunities": [
                {
                    "opportunity": "Improve system reliability",
                    "focus_area": "AI analysis system",
                    "expected_outcome": "Better execution decisions"
                }
            ]
        }

    def _log_trade_to_performance_tracker(self, decision: Dict[str, Any]) -> None:
        """Log trade to performance tracker for analysis."""
        
        try:
            trade_data = {
                "symbol": decision.get("symbol"),
                "action": decision.get("action"),
                "quantity": self.DEFAULT_QTY,
                "confidence": decision.get("confidence"),
                "reasoning": decision.get("reasoning"),
                "executed": decision.get("executed", False),
                "execution_reasoning": decision.get("execution_reasoning"),
                "experience_insights": decision.get("experience_insights", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            performance_tracker.log_trade(trade_data)
            logger.info(f"EnhancedTradeExecutor | Logged trade to performance tracker")
            
        except Exception as exc:
            logger.error(f"EnhancedTradeExecutor | Failed to log trade: {exc}")

    def _store_execution_history(self, decision: Dict[str, Any]) -> None:
        """Store execution decision in history for learning."""
        
        execution_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "agent_id": self.agent_id,
            "market_context": decision.get("market_context", {})
        }
        
        self.execution_history.append(execution_record)
        
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]

    async def _trigger_performance_analysis_if_needed(self, decision: Dict[str, Any]) -> None:
        """Trigger performance analysis if this completes a significant play."""
        
        try:
            # Check if we should trigger analysis (e.g., after N trades or significant PnL)
            recent_trades = len(self.execution_history)
            
            # Trigger analysis every 10 trades or on significant events
            if recent_trades % 10 == 0 or self._is_significant_event(decision):
                
                # Prepare play data for analysis
                play_data = await self._prepare_play_data_for_analysis()
                
                # Trigger performance analysis
                analysis_result = await performance_analyzer_agent(play_data)
                
                logger.info(f"EnhancedTradeExecutor | Triggered performance analysis: {analysis_result.get('status')}")
                
        except Exception as exc:
            logger.error(f"EnhancedTradeExecutor | Failed to trigger performance analysis: {exc}")

    def _is_significant_event(self, decision: Dict[str, Any]) -> bool:
        """Check if this decision represents a significant event requiring analysis."""
        
        # Check for high confidence trades
        confidence = decision.get("confidence", 0)
        if confidence > 0.8:
            return True
        
        # Check for large position sizes (future enhancement)
        # Check for unusual market conditions
        # Check for significant PnL impact
        
        return False

    async def _prepare_play_data_for_analysis(self) -> Dict[str, Any]:
        """Prepare play data for performance analysis."""
        
        # Get recent trades from performance tracker
        recent_trades = performance_tracker.trades[-20:] if performance_tracker.trades else []
        
        # Get current performance metrics
        performance_metrics = performance_tracker.rolling_stats()
        
        # Get PnL data
        pnl_data = pnl_tracker.get_performance_summary()
        
        play_data = {
            "play_id": f"play_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "trades": recent_trades,
            "performance": {
                **performance_metrics,
                **pnl_data
            },
            "context": {
                "agent_id": self.agent_id,
                "execution_history_count": len(self.execution_history),
                "market_conditions": "current_market_context",  # Would be populated with real data
                "strategy_used": "enhanced_trade_executor",
                "risk_parameters": {
                    "default_quantity": self.DEFAULT_QTY,
                    "confidence_threshold": 0.6
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return play_data

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics for this agent."""
        
        if not self.execution_history:
            return {
                "total_decisions": 0,
                "execution_rate": 0,
                "avg_confidence": 0,
                "success_rate": 0
            }
        
        total_decisions = len(self.execution_history)
        executed_decisions = [d for d in self.execution_history if d["decision"].get("executed", False)]
        execution_rate = len(executed_decisions) / total_decisions * 100
        
        confidences = [d["decision"].get("confidence", 0) for d in self.execution_history]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Success rate would be calculated from actual trade outcomes
        success_rate = 0  # Would be calculated from PnL data
        
        return {
            "total_decisions": total_decisions,
            "execution_rate": round(execution_rate, 2),
            "avg_confidence": round(avg_confidence, 2),
            "success_rate": round(success_rate, 2),
            "recent_insights": len(self.execution_history[-5:]) if self.execution_history else 0
        }

    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights for this agent."""
        
        try:
            # Get experience data for this agent
            experience_data = experience_learning_system.get_agent_experience(self.agent_id)
            
            # Get performance trends
            performance_trends = performance_analyzer_agent.get_performance_trends()
            
            return {
                "experience_data": experience_data,
                "performance_trends": performance_trends,
                "execution_stats": self.get_execution_stats(),
                "learning_focus": self._identify_learning_focus(experience_data)
            }
            
        except Exception as exc:
            logger.error(f"EnhancedTradeExecutor | Failed to get learning insights: {exc}")
            return {
                "experience_data": {},
                "performance_trends": {"trend": "insufficient_data"},
                "execution_stats": self.get_execution_stats(),
                "learning_focus": "system_reliability"
            }

    def _identify_learning_focus(self, experience_data: Dict[str, Any]) -> str:
        """Identify the primary learning focus area for this agent."""
        
        # Analyze experience data to identify focus areas
        insights = experience_data.get("relevant_insights", [])
        
        if not insights:
            return "general_improvement"
        
        # Count focus areas
        focus_areas = {}
        for insight in insights:
            # Extract focus area from insight (simplified)
            if "risk" in str(insight).lower():
                focus_areas["risk_management"] = focus_areas.get("risk_management", 0) + 1
            elif "timing" in str(insight).lower():
                focus_areas["execution_timing"] = focus_areas.get("execution_timing", 0) + 1
            elif "confidence" in str(insight).lower():
                focus_areas["confidence_calibration"] = focus_areas.get("confidence_calibration", 0) + 1
            else:
                focus_areas["general_improvement"] = focus_areas.get("general_improvement", 0) + 1
        
        # Return the most common focus area
        if focus_areas:
            return max(focus_areas, key=lambda k: focus_areas[k])
        
        return "general_improvement"


# Global instance
enhanced_trade_executor = EnhancedTradeExecutorAgent() 