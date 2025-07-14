# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio
import json

from core.openai_manager import openai_manager
from agents.experience_learning_system import experience_learning_system
from utils.logger import logger  # type: ignore


class PerformanceAnalyzerAgent:
    """
    AI-powered performance analyzer that automatically analyzes every play/performance
    and triggers the experience learning system for continuous improvement.
    
    This agent runs after every play completion to:
    1. Analyze performance metrics
    2. Identify patterns and insights
    3. Generate learning recommendations
    4. Trigger experience storage and agent feedback
    """
    
    def __init__(self) -> None:
        """Initialize the performance analyzer agent."""
        self.analysis_history: List[Dict[str, Any]] = []
        
    async def __call__(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for performance analysis.
        
        Args:
            play_data: Complete play data including trades, performance, context
            
        Returns:
            Analysis results with insights and recommendations
        """
        play_id = play_data.get("play_id", "unknown")
        logger.info(f"PerformanceAnalyzer | Starting analysis for play: {play_id}")
        
        try:
            # Perform comprehensive performance analysis
            performance_analysis = await self._analyze_performance(play_data)
            
            # Trigger experience learning system
            experience_results = await experience_learning_system.analyze_and_store_experience(play_data)
            
            # Generate system recommendations
            recommendations = await self._generate_system_recommendations(play_data, performance_analysis)
            
            # Store analysis history
            analysis_record = {
                "play_id": play_id,
                "timestamp": datetime.utcnow().isoformat(),
                "performance_analysis": performance_analysis,
                "experience_results": experience_results,
                "recommendations": recommendations
            }
            self.analysis_history.append(analysis_record)
            
            # Broadcast insights to other agents
            await self._broadcast_insights(play_id, performance_analysis, recommendations)
            
            logger.info(f"PerformanceAnalyzer | Completed analysis for play: {play_id}")
            
            return {
                "status": "completed",
                "play_id": play_id,
                "performance_analysis": performance_analysis,
                "experience_results": experience_results,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as exc:
            logger.error(f"PerformanceAnalyzer | Analysis failed for play {play_id}: {exc}")
            return {
                "status": "failed",
                "play_id": play_id,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _analyze_performance(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed performance analysis of the play."""
        
        # Extract key performance metrics
        trades = play_data.get("trades", [])
        performance = play_data.get("performance", {})
        context = play_data.get("context", {})
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(trades, performance)
        
        # AI-powered performance analysis
        analysis_prompt = f"""
        You are an expert trading performance analyst. Analyze this trading play performance comprehensively:

        PERFORMANCE METRICS:
        {json.dumps(metrics, indent=2)}

        TRADES DATA:
        {json.dumps(trades, indent=2)}

        CONTEXT:
        {json.dumps(context, indent=2)}

        Provide a detailed performance analysis in JSON format:
        {{
            "performance_summary": {{
                "overall_rating": "excellent/good/fair/poor",
                "key_metrics": {{
                    "win_rate": "percentage",
                    "profit_factor": "ratio",
                    "avg_win_loss_ratio": "ratio",
                    "max_drawdown": "percentage",
                    "sharpe_ratio": "ratio"
                }},
                "strengths": ["list", "of", "strengths"],
                "weaknesses": ["list", "of", "weaknesses"],
                "opportunities": ["list", "of", "opportunities"],
                "threats": ["list", "of", "threats"]
            }},
            "pattern_analysis": {{
                "winning_patterns": ["list", "of", "winning", "patterns"],
                "losing_patterns": ["list", "of", "losing", "patterns"],
                "market_conditions": ["list", "of", "market", "conditions"],
                "timing_analysis": "good/fair/poor"
            }},
            "risk_assessment": {{
                "risk_level": "low/medium/high",
                "risk_indicators": ["list", "of", "risk", "indicators"],
                "risk_management_effectiveness": "high/medium/low",
                "risk_mitigation_success": "high/medium/low"
            }},
            "strategy_evaluation": {{
                "strategy_effectiveness": "high/medium/low",
                "strategy_adaptation": "high/medium/low",
                "strategy_consistency": "high/medium/low",
                "strategy_improvements": ["list", "of", "improvements"]
            }},
            "comparative_analysis": {{
                "vs_benchmark": "better/worse/similar",
                "vs_historical": "improving/declining/stable",
                "vs_peers": "top_quartile/middle/bottom_quartile"
            }},
            "actionable_insights": [
                {{
                    "insight": "specific insight",
                    "impact": "high/medium/low",
                    "actionability": "immediate/short_term/long_term",
                    "recommendation": "specific recommendation"
                }}
            ]
        }}
        """
        
        try:
            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are an expert trading performance analyst with deep knowledge of quantitative trading metrics, risk management, and market dynamics."},
                {"role": "user", "content": analysis_prompt}
            ])
            
            analysis = json.loads(response["content"])
            return analysis
            
        except Exception as exc:
            logger.error(f"PerformanceAnalyzer | Performance analysis failed: {exc}")
            return self._fallback_performance_analysis(metrics)

    def _calculate_performance_metrics(self, trades: List[Dict[str, Any]], performance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0,
                "profit_factor": 0,
                "avg_win_loss_ratio": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0
            }
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        # PnL metrics
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = sum(t.get("pnl", 0) for t in winning_trades)
        gross_loss = abs(sum(t.get("pnl", 0) for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0
        
        # Average win/loss ratio
        avg_win = gross_profit / len(winning_trades) if winning_trades else 0
        avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
        avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf') if avg_win > 0 else 0
        
        # Drawdown calculation
        cumulative_pnl = 0
        max_pnl = 0
        max_drawdown = 0
        for trade in trades:
            cumulative_pnl += trade.get("pnl", 0)
            max_pnl = max(max_pnl, cumulative_pnl)
            drawdown = max_pnl - cumulative_pnl
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio (simplified, assuming 0% risk-free rate)
        returns = [t.get("pnl", 0) for t in trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns) if returns else 0
        std_dev = variance ** 0.5
        sharpe_ratio = avg_return / std_dev if std_dev > 0 else 0
        
        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(avg_pnl, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "avg_win_loss_ratio": round(avg_win_loss_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "volatility": round(std_dev, 2)
        }

    def _fallback_performance_analysis(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback performance analysis when AI analysis fails."""
        
        win_rate = metrics.get("win_rate", 0)
        total_pnl = metrics.get("total_pnl", 0)
        profit_factor = metrics.get("profit_factor", 0)
        
        # Determine overall rating
        if win_rate >= 60 and total_pnl > 0 and profit_factor >= 1.5:
            overall_rating = "excellent"
        elif win_rate >= 50 and total_pnl > 0 and profit_factor >= 1.0:
            overall_rating = "good"
        elif win_rate >= 40 and total_pnl >= 0:
            overall_rating = "fair"
        else:
            overall_rating = "poor"
        
        return {
            "performance_summary": {
                "overall_rating": overall_rating,
                "key_metrics": {
                    "win_rate": f"{win_rate}%",
                    "profit_factor": f"{profit_factor:.2f}",
                    "avg_win_loss_ratio": f"{metrics.get('avg_win_loss_ratio', 0):.2f}",
                    "max_drawdown": f"{metrics.get('max_drawdown', 0):.2f}%",
                    "sharpe_ratio": f"{metrics.get('sharpe_ratio', 0):.2f}"
                },
                "strengths": ["Basic metrics calculated successfully"],
                "weaknesses": ["AI analysis unavailable"],
                "opportunities": ["Enable AI analysis for deeper insights"],
                "threats": ["Limited analysis capability"]
            },
            "pattern_analysis": {
                "winning_patterns": ["Basic pattern analysis available"],
                "losing_patterns": ["Basic pattern analysis available"],
                "market_conditions": ["Market context analysis needed"],
                "timing_analysis": "fair"
            },
            "risk_assessment": {
                "risk_level": "medium",
                "risk_indicators": ["Basic risk metrics available"],
                "risk_management_effectiveness": "medium",
                "risk_mitigation_success": "medium"
            },
            "strategy_evaluation": {
                "strategy_effectiveness": "medium",
                "strategy_adaptation": "medium",
                "strategy_consistency": "medium",
                "strategy_improvements": ["Enable AI analysis for detailed evaluation"]
            },
            "comparative_analysis": {
                "vs_benchmark": "similar",
                "vs_historical": "stable",
                "vs_peers": "middle"
            },
            "actionable_insights": [
                {
                    "insight": "AI analysis system needs attention",
                    "impact": "high",
                    "actionability": "immediate",
                    "recommendation": "Check AI system status and restore functionality"
                }
            ]
        }

    async def _generate_system_recommendations(self, play_data: Dict[str, Any], performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system-wide recommendations based on performance analysis."""
        
        recommendations_prompt = f"""
        Based on this performance analysis, generate system-wide recommendations:

        PERFORMANCE ANALYSIS:
        {json.dumps(performance_analysis, indent=2)}

        PLAY CONTEXT:
        {json.dumps(play_data.get('context', {}), indent=2)}

        Provide recommendations in JSON format:
        {{
            "immediate_actions": [
                {{
                    "action": "specific action",
                    "priority": "high/medium/low",
                    "impact": "high/medium/low",
                    "effort": "high/medium/low",
                    "timeline": "immediate/short_term/long_term"
                }}
            ],
            "strategy_adjustments": [
                {{
                    "adjustment": "specific adjustment",
                    "rationale": "reason for adjustment",
                    "expected_impact": "expected outcome"
                }}
            ],
            "risk_management": [
                {{
                    "risk_measure": "specific risk measure",
                    "implementation": "how to implement",
                    "monitoring": "how to monitor"
                }}
            ],
            "agent_improvements": [
                {{
                    "agent": "agent name",
                    "improvement": "specific improvement",
                    "priority": "high/medium/low"
                }}
            ],
            "system_optimizations": [
                {{
                    "optimization": "specific optimization",
                    "benefit": "expected benefit",
                    "implementation": "implementation approach"
                }}
            ]
        }}
        """
        
        try:
            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are an expert trading system consultant providing strategic recommendations for system improvement."},
                {"role": "user", "content": recommendations_prompt}
            ])
            
            recommendations = json.loads(response["content"])
            return recommendations
            
        except Exception as exc:
            logger.error(f"PerformanceAnalyzer | Failed to generate recommendations: {exc}")
            return self._fallback_recommendations()

    def _fallback_recommendations(self) -> Dict[str, Any]:
        """Fallback recommendations when AI generation fails."""
        return {
            "immediate_actions": [
                {
                    "action": "Restore AI analysis system",
                    "priority": "high",
                    "impact": "high",
                    "effort": "medium",
                    "timeline": "immediate"
                }
            ],
            "strategy_adjustments": [
                {
                    "adjustment": "Monitor basic performance metrics",
                    "rationale": "AI analysis unavailable",
                    "expected_impact": "Maintain basic functionality"
                }
            ],
            "risk_management": [
                {
                    "risk_measure": "Implement basic risk limits",
                    "implementation": "Set position size and loss limits",
                    "monitoring": "Track basic risk metrics"
                }
            ],
            "agent_improvements": [
                {
                    "agent": "All agents",
                    "improvement": "Restore AI feedback system",
                    "priority": "high"
                }
            ],
            "system_optimizations": [
                {
                    "optimization": "Improve system reliability",
                    "benefit": "Consistent analysis and feedback",
                    "implementation": "Fix AI system issues"
                }
            ]
        }

    async def _broadcast_insights(self, play_id: str, performance_analysis: Dict[str, Any], recommendations: Dict[str, Any]) -> None:
        """Broadcast insights and recommendations to other agents."""
        
        # Create broadcast message
        broadcast_message = {
            "type": "performance_insights",
            "play_id": play_id,
            "timestamp": datetime.utcnow().isoformat(),
            "performance_summary": performance_analysis.get("performance_summary", {}),
            "key_insights": performance_analysis.get("actionable_insights", []),
            "recommendations": recommendations.get("immediate_actions", []),
            "priority": "high" if performance_analysis.get("performance_summary", {}).get("overall_rating") in ["poor", "excellent"] else "medium"
        }
        
        # TODO: Implement actual broadcasting mechanism
        # This could be through a message queue, WebSocket, or event system
        logger.info(f"PerformanceAnalyzer | Broadcasting insights for play {play_id}")
        
        # For now, just log the broadcast
        logger.info(f"PerformanceAnalyzer | Broadcast message: {json.dumps(broadcast_message, indent=2)}")

    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history."""
        return self.analysis_history[-limit:]

    def get_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends from analysis history."""
        
        if len(self.analysis_history) < 2:
            return {"trend": "insufficient_data", "message": "Need more analysis data"}
        
        # Extract key metrics from recent analyses
        recent_analyses = self.analysis_history[-5:]  # Last 5 analyses
        
        ratings = []
        win_rates = []
        pnl_values = []
        
        for analysis in recent_analyses:
            perf_summary = analysis.get("performance_analysis", {}).get("performance_summary", {})
            ratings.append(perf_summary.get("overall_rating", "fair"))
            
            # Extract metrics if available
            metrics = perf_summary.get("key_metrics", {})
            if "win_rate" in metrics:
                win_rates.append(float(metrics["win_rate"].replace("%", "")))
            if "total_pnl" in metrics:
                pnl_values.append(float(metrics["total_pnl"]))
        
        # Determine trends
        rating_trend = self._analyze_rating_trend(ratings)
        win_rate_trend = self._analyze_numeric_trend(win_rates)
        pnl_trend = self._analyze_numeric_trend(pnl_values)
        
        return {
            "rating_trend": rating_trend,
            "win_rate_trend": win_rate_trend,
            "pnl_trend": pnl_trend,
            "overall_trend": self._determine_overall_trend(rating_trend, win_rate_trend, pnl_trend),
            "sample_size": len(recent_analyses)
        }

    def _analyze_rating_trend(self, ratings: List[str]) -> str:
        """Analyze trend in performance ratings."""
        if len(ratings) < 2:
            return "insufficient_data"
        
        # Convert ratings to numeric values
        rating_values = {"excellent": 4, "good": 3, "fair": 2, "poor": 1}
        numeric_ratings = [rating_values.get(r, 2) for r in ratings]
        
        # Calculate trend
        if numeric_ratings[-1] > numeric_ratings[0]:
            return "improving"
        elif numeric_ratings[-1] < numeric_ratings[0]:
            return "declining"
        else:
            return "stable"

    def _analyze_numeric_trend(self, values: List[float]) -> str:
        """Analyze trend in numeric values."""
        if len(values) < 2:
            return "insufficient_data"
        
        if values[-1] > values[0]:
            return "improving"
        elif values[-1] < values[0]:
            return "declining"
        else:
            return "stable"

    def _determine_overall_trend(self, rating_trend: str, win_rate_trend: str, pnl_trend: str) -> str:
        """Determine overall trend from multiple indicators."""
        trends = [rating_trend, win_rate_trend, pnl_trend]
        improving = trends.count("improving")
        declining = trends.count("declining")
        stable = trends.count("stable")
        
        if improving > declining:
            return "improving"
        elif declining > improving:
            return "declining"
        else:
            return "stable"


# Global instance
performance_analyzer_agent = PerformanceAnalyzerAgent() 