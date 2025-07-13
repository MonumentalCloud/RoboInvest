# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, cast
import json
import asyncio

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # type: ignore

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger  # type: ignore


class ExperienceLearningSystem:
    """
    Comprehensive experience learning system that analyzes every play/performance
    and provides feedback to agents for continuous improvement.
    
    Hybrid RAG Architecture:
    - Centralized: Shared experience memory for cross-agent learning
    - Decentralized: Agent-specific collections for specialized knowledge
    """
    
    # Collection names for different types of experiences
    COLLECTIONS = {
        "shared_experiences": "shared_experiences",  # Cross-agent learning
        "trade_experiences": "trade_experiences",    # Trade-specific insights
        "strategy_experiences": "strategy_experiences",  # Strategy performance
        "risk_experiences": "risk_experiences",      # Risk management lessons
        "market_experiences": "market_experiences",  # Market condition patterns
        "agent_feedback": "agent_feedback",          # Direct agent feedback
        "performance_analysis": "performance_analysis",  # Detailed performance breakdowns
    }
    
    def __init__(self) -> None:
        """Initialize the experience learning system with ChromaDB collections."""
        if not config.openai_api_key:
            logger.warning("ExperienceLearning | OpenAI key missing – using in-memory fallback")
            self._client = None
            self._collections = {}
            self._memories = {name: [] for name in self.COLLECTIONS.values()}
            return

        embed_fn = OpenAIEmbeddingFunction(api_key=config.openai_api_key, model_name="text-embedding-3-small")
        self._client = chromadb.PersistentClient(path=config.chroma_db_path)
        
        # Initialize all collections
        self._collections = {}
        try:
            for collection_name in self.COLLECTIONS.values():
                self._collections[collection_name] = self._client.get_or_create_collection(
                    collection_name, embedding_function=embed_fn
                )
            logger.info(f"ExperienceLearning | Initialized {len(self._collections)} collections")
        except Exception as exc:
            logger.error(f"ExperienceLearning | Chroma error {exc}; falling back to memory")
            self._client = None
            self._collections = {}
            self._memories = {name: [] for name in self.COLLECTIONS.values()}

    async def analyze_and_store_experience(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a completed play/performance and store comprehensive learning insights.
        
        Args:
            play_data: Complete play data including trades, performance, context
            
        Returns:
            Analysis results with insights and feedback for agents
        """
        logger.info(f"ExperienceLearning | Analyzing play: {play_data.get('play_id', 'unknown')}")
        
        # Perform comprehensive analysis
        analysis = await self._perform_comprehensive_analysis(play_data)
        
        # Store in multiple collections based on insights
        await self._store_experience_insights(play_data, analysis)
        
        # Generate agent-specific feedback
        agent_feedback = await self._generate_agent_feedback(play_data, analysis)
        
        # Store feedback for agents to retrieve
        await self._store_agent_feedback(agent_feedback)
        
        logger.info(f"ExperienceLearning | Stored {len(analysis.get('insights', []))} insights and {len(agent_feedback)} feedback items")
        
        return {
            "analysis": analysis,
            "agent_feedback": agent_feedback,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _perform_comprehensive_analysis(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive AI-powered analysis of the play experience."""
        
        # Prepare analysis context
        context = self._prepare_analysis_context(play_data)
        
        # AI-powered comprehensive analysis
        analysis_prompt = f"""
        You are an expert trading system analyst. Analyze this trading play experience comprehensively:

        PLAY DATA:
        {json.dumps(play_data, indent=2)}

        CONTEXT:
        {json.dumps(context, indent=2)}

        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "overall_performance": {{
                "success_level": "high/medium/low",
                "key_achievements": ["list", "of", "achievements"],
                "major_issues": ["list", "of", "issues"],
                "unexpected_outcomes": ["list", "of", "surprises"]
            }},
            "strategy_analysis": {{
                "strategy_effectiveness": "high/medium/low",
                "strategy_strengths": ["list", "of", "strengths"],
                "strategy_weaknesses": ["list", "of", "weaknesses"],
                "strategy_improvements": ["list", "of", "improvements"]
            }},
            "risk_analysis": {{
                "risk_management_quality": "high/medium/low",
                "risk_indicators": ["list", "of", "risk", "indicators"],
                "risk_mitigation_success": "high/medium/low",
                "risk_lessons": ["list", "of", "risk", "lessons"]
            }},
            "market_analysis": {{
                "market_condition_accuracy": "high/medium/low",
                "market_timing": "good/fair/poor",
                "market_insights": ["list", "of", "market", "insights"],
                "market_patterns": ["list", "of", "patterns"]
            }},
            "agent_performance": {{
                "agent_effectiveness": {{
                    "world_monitor": "high/medium/low",
                    "strategy_agent": "high/medium/low",
                    "trade_executor": "high/medium/low",
                    "risk_assessor": "high/medium/low"
                }},
                "agent_collaboration": "high/medium/low",
                "agent_improvements": ["list", "of", "improvements"]
            }},
            "insights": [
                {{
                    "type": "strategy/risk/market/agent/technical",
                    "title": "insight title",
                    "description": "detailed description",
                    "impact": "high/medium/low",
                    "actionable": true/false,
                    "recommendation": "specific recommendation"
                }}
            ],
            "lessons_learned": [
                {{
                    "category": "strategy/risk/market/technical",
                    "lesson": "specific lesson",
                    "application": "how to apply this lesson",
                    "priority": "high/medium/low"
                }}
            ]
        }}
        """
        
        try:
            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are an expert trading system analyst with deep knowledge of market dynamics, risk management, and AI trading systems."},
                {"role": "user", "content": analysis_prompt}
            ])
            
            analysis = json.loads(response["content"])
            return analysis
            
        except Exception as exc:
            logger.error(f"ExperienceLearning | Analysis failed: {exc}")
            return self._fallback_analysis(play_data)

    def _prepare_analysis_context(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for analysis including historical data and market conditions."""
        
        # Extract key metrics
        trades = play_data.get("trades", [])
        performance = play_data.get("performance", {})
        
        # Calculate additional metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get("pnl", 0) > 0])
        losing_trades = len([t for t in trades if t.get("pnl", 0) < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        # Market context
        market_conditions = play_data.get("market_context", {})
        
        return {
            "metrics": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "avg_pnl": avg_pnl,
                "max_drawdown": performance.get("max_drawdown", 0),
                "sharpe_ratio": performance.get("sharpe_ratio", 0)
            },
            "market_conditions": market_conditions,
            "strategy_used": play_data.get("strategy", "unknown"),
            "risk_parameters": play_data.get("risk_parameters", {}),
            "execution_quality": play_data.get("execution_quality", {})
        }

    def _fallback_analysis(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI analysis fails."""
        trades = play_data.get("trades", [])
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        
        return {
            "overall_performance": {
                "success_level": "high" if total_pnl > 0 else "low",
                "key_achievements": ["Basic analysis completed"],
                "major_issues": ["AI analysis unavailable"],
                "unexpected_outcomes": []
            },
            "strategy_analysis": {
                "strategy_effectiveness": "medium",
                "strategy_strengths": ["Fallback analysis available"],
                "strategy_weaknesses": ["Limited AI insights"],
                "strategy_improvements": ["Enable AI analysis"]
            },
            "risk_analysis": {
                "risk_management_quality": "medium",
                "risk_indicators": ["Basic risk metrics available"],
                "risk_mitigation_success": "medium",
                "risk_lessons": ["Need AI analysis for detailed insights"]
            },
            "market_analysis": {
                "market_condition_accuracy": "medium",
                "market_timing": "fair",
                "market_insights": ["Basic market data available"],
                "market_patterns": ["Pattern analysis requires AI"]
            },
            "agent_performance": {
                "agent_effectiveness": {
                    "world_monitor": "medium",
                    "strategy_agent": "medium",
                    "trade_executor": "medium",
                    "risk_assessor": "medium"
                },
                "agent_collaboration": "medium",
                "agent_improvements": ["Enable AI analysis for detailed feedback"]
            },
            "insights": [
                {
                    "type": "technical",
                    "title": "Fallback Analysis",
                    "description": "AI analysis unavailable, using basic metrics",
                    "impact": "medium",
                    "actionable": False,
                    "recommendation": "Check AI system status"
                }
            ],
            "lessons_learned": [
                {
                    "category": "technical",
                    "lesson": "AI analysis system needs monitoring",
                    "application": "Implement fallback mechanisms",
                    "priority": "high"
                }
            ]
        }

    async def _store_experience_insights(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Store experience insights in appropriate collections."""
        
        if not self._client:
            # Store in memory
            for collection_name in self.COLLECTIONS.values():
                self._memories[collection_name].append({
                    "play_data": play_data,
                    "analysis": analysis,
                    "timestamp": datetime.utcnow().isoformat()
                })
            return
        
        # Store in ChromaDB collections
        try:
            # Shared experiences
            shared_doc = self._create_shared_experience_doc(play_data, analysis)
            self._collections["shared_experiences"].add(
                documents=[shared_doc],
                metadatas=[{"type": "shared_experience", "play_id": play_data.get("play_id", "unknown")}],
                ids=[f"shared_{play_data.get('play_id', datetime.utcnow().isoformat())}"]
            )
            
            # Trade experiences
            trade_doc = self._create_trade_experience_doc(play_data, analysis)
            self._collections["trade_experiences"].add(
                documents=[trade_doc],
                metadatas=[{"type": "trade_experience", "play_id": play_data.get("play_id", "unknown")}],
                ids=[f"trade_{play_data.get('play_id', datetime.utcnow().isoformat())}"]
            )
            
            # Strategy experiences
            strategy_doc = self._create_strategy_experience_doc(play_data, analysis)
            self._collections["strategy_experiences"].add(
                documents=[strategy_doc],
                metadatas=[{"type": "strategy_experience", "play_id": play_data.get("play_id", "unknown")}],
                ids=[f"strategy_{play_data.get('play_id', datetime.utcnow().isoformat())}"]
            )
            
            # Risk experiences
            risk_doc = self._create_risk_experience_doc(play_data, analysis)
            self._collections["risk_experiences"].add(
                documents=[risk_doc],
                metadatas=[{"type": "risk_experience", "play_id": play_data.get("play_id", "unknown")}],
                ids=[f"risk_{play_data.get('play_id', datetime.utcnow().isoformat())}"]
            )
            
            # Market experiences
            market_doc = self._create_market_experience_doc(play_data, analysis)
            self._collections["market_experiences"].add(
                documents=[market_doc],
                metadatas=[{"type": "market_experience", "play_id": play_data.get("play_id", "unknown")}],
                ids=[f"market_{play_data.get('play_id', datetime.utcnow().isoformat())}"]
            )
            
            # Performance analysis
            perf_doc = self._create_performance_analysis_doc(play_data, analysis)
            self._collections["performance_analysis"].add(
                documents=[perf_doc],
                metadatas=[{"type": "performance_analysis", "play_id": play_data.get("play_id", "unknown")}],
                ids=[f"perf_{play_data.get('play_id', datetime.utcnow().isoformat())}"]
            )
            
        except Exception as exc:
            logger.error(f"ExperienceLearning | Failed to store insights: {exc}")

    def _create_shared_experience_doc(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create document for shared experiences collection."""
        return f"""
        SHARED EXPERIENCE ANALYSIS
        
        Play ID: {play_data.get('play_id', 'unknown')}
        Overall Performance: {analysis.get('overall_performance', {}).get('success_level', 'unknown')}
        
        Key Achievements: {', '.join(analysis.get('overall_performance', {}).get('key_achievements', []))}
        Major Issues: {', '.join(analysis.get('overall_performance', {}).get('major_issues', []))}
        
        Strategy Effectiveness: {analysis.get('strategy_analysis', {}).get('strategy_effectiveness', 'unknown')}
        Risk Management Quality: {analysis.get('risk_analysis', {}).get('risk_management_quality', 'unknown')}
        
        Key Insights:
        {chr(10).join([f"- {insight.get('title', '')}: {insight.get('description', '')}" for insight in analysis.get('insights', [])])}
        
        Lessons Learned:
        {chr(10).join([f"- {lesson.get('lesson', '')}" for lesson in analysis.get('lessons_learned', [])])}
        """

    def _create_trade_experience_doc(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create document for trade experiences collection."""
        trades = play_data.get("trades", [])
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        
        return f"""
        TRADE EXPERIENCE ANALYSIS
        
        Play ID: {play_data.get('play_id', 'unknown')}
        Total Trades: {len(trades)}
        Total PnL: ${total_pnl:.2f}
        
        Trade Execution Quality: {analysis.get('agent_performance', {}).get('agent_effectiveness', {}).get('trade_executor', 'unknown')}
        
        Trade Insights:
        {chr(10).join([f"- {insight.get('title', '')}: {insight.get('description', '')}" for insight in analysis.get('insights', []) if insight.get('type') == 'strategy'])}
        
        Trade Lessons:
        {chr(10).join([f"- {lesson.get('lesson', '')}" for lesson in analysis.get('lessons_learned', []) if lesson.get('category') == 'strategy'])}
        """

    def _create_strategy_experience_doc(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create document for strategy experiences collection."""
        strategy_analysis = analysis.get('strategy_analysis', {})
        
        return f"""
        STRATEGY EXPERIENCE ANALYSIS
        
        Play ID: {play_data.get('play_id', 'unknown')}
        Strategy Used: {play_data.get('strategy', 'unknown')}
        Strategy Effectiveness: {strategy_analysis.get('strategy_effectiveness', 'unknown')}
        
        Strategy Strengths:
        {chr(10).join([f"- {strength}" for strength in strategy_analysis.get('strategy_strengths', [])])}
        
        Strategy Weaknesses:
        {chr(10).join([f"- {weakness}" for weakness in strategy_analysis.get('strategy_weaknesses', [])])}
        
        Strategy Improvements:
        {chr(10).join([f"- {improvement}" for improvement in strategy_analysis.get('strategy_improvements', [])])}
        """

    def _create_risk_experience_doc(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create document for risk experiences collection."""
        risk_analysis = analysis.get('risk_analysis', {})
        
        return f"""
        RISK EXPERIENCE ANALYSIS
        
        Play ID: {play_data.get('play_id', 'unknown')}
        Risk Management Quality: {risk_analysis.get('risk_management_quality', 'unknown')}
        Risk Mitigation Success: {risk_analysis.get('risk_mitigation_success', 'unknown')}
        
        Risk Indicators:
        {chr(10).join([f"- {indicator}" for indicator in risk_analysis.get('risk_indicators', [])])}
        
        Risk Lessons:
        {chr(10).join([f"- {lesson}" for lesson in risk_analysis.get('risk_lessons', [])])}
        """

    def _create_market_experience_doc(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create document for market experiences collection."""
        market_analysis = analysis.get('market_analysis', {})
        
        return f"""
        MARKET EXPERIENCE ANALYSIS
        
        Play ID: {play_data.get('play_id', 'unknown')}
        Market Condition Accuracy: {market_analysis.get('market_condition_accuracy', 'unknown')}
        Market Timing: {market_analysis.get('market_timing', 'unknown')}
        
        Market Insights:
        {chr(10).join([f"- {insight}" for insight in market_analysis.get('market_insights', [])])}
        
        Market Patterns:
        {chr(10).join([f"- {pattern}" for pattern in market_analysis.get('market_patterns', [])])}
        """

    def _create_performance_analysis_doc(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create document for performance analysis collection."""
        performance = play_data.get("performance", {})
        
        return f"""
        PERFORMANCE ANALYSIS
        
        Play ID: {play_data.get('play_id', 'unknown')}
        Win Rate: {performance.get('win_rate', 0)}%
        Total PnL: ${performance.get('total_pnl', 0):.2f}
        Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}
        Max Drawdown: {performance.get('max_drawdown', 0):.2f}%
        
        Agent Performance:
        {chr(10).join([f"- {agent}: {effectiveness}" for agent, effectiveness in analysis.get('agent_performance', {}).get('agent_effectiveness', {}).items()])}
        
        Agent Collaboration: {analysis.get('agent_performance', {}).get('agent_collaboration', 'unknown')}
        
        Performance Insights:
        {chr(10).join([f"- {insight.get('title', '')}: {insight.get('description', '')}" for insight in analysis.get('insights', [])])}
        """

    async def _generate_agent_feedback(self, play_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific feedback for each agent based on analysis."""
        
        agent_performance = analysis.get("agent_performance", {})
        agent_effectiveness = agent_performance.get("agent_effectiveness", {})
        
        feedback = {}
        
        # Generate feedback for each agent
        agents = {
            "world_monitor": "World Monitor Agent",
            "strategy_agent": "Strategy Agent", 
            "trade_executor": "Trade Executor Agent",
            "risk_assessor": "Risk Assessor Agent"
        }
        
        for agent_id, agent_name in agents.items():
            effectiveness = agent_effectiveness.get(agent_id, "medium")
            
            feedback_prompt = f"""
            Generate specific, actionable feedback for the {agent_name} based on this play analysis:
            
            PLAY DATA: {json.dumps(play_data, indent=2)}
            ANALYSIS: {json.dumps(analysis, indent=2)}
            AGENT EFFECTIVENESS: {effectiveness}
            
            Provide feedback in JSON format:
            {{
                "agent_id": "{agent_id}",
                "effectiveness_rating": "{effectiveness}",
                "strengths": ["list", "of", "strengths"],
                "weaknesses": ["list", "of", "weaknesses"],
                "improvements": ["list", "of", "specific", "improvements"],
                "recommendations": ["list", "of", "recommendations"],
                "priority_actions": ["list", "of", "priority", "actions"],
                "learning_focus": "specific area to focus learning on"
            }}
            """
            
            try:
                response = openai_manager.chat_completion([
                    {"role": "system", "content": f"You are an expert trading system analyst providing feedback to the {agent_name}."},
                    {"role": "user", "content": feedback_prompt}
                ])
                
                agent_feedback = json.loads(response["content"])
                feedback[agent_id] = agent_feedback
                
            except Exception as exc:
                logger.error(f"ExperienceLearning | Failed to generate feedback for {agent_id}: {exc}")
                feedback[agent_id] = self._fallback_agent_feedback(agent_id, effectiveness)
        
        return feedback

    def _fallback_agent_feedback(self, agent_id: str, effectiveness: str) -> Dict[str, Any]:
        """Fallback agent feedback when AI generation fails."""
        return {
            "agent_id": agent_id,
            "effectiveness_rating": effectiveness,
            "strengths": ["Basic functionality maintained"],
            "weaknesses": ["AI feedback generation unavailable"],
            "improvements": ["Enable AI feedback system"],
            "recommendations": ["Check AI system status"],
            "priority_actions": ["Restore AI feedback capability"],
            "learning_focus": "System reliability"
        }

    async def _store_agent_feedback(self, agent_feedback: Dict[str, Any]) -> None:
        """Store agent feedback for retrieval by agents."""
        
        if not self._client:
            # Store in memory
            self._memories["agent_feedback"].append({
                "feedback": agent_feedback,
                "timestamp": datetime.utcnow().isoformat()
            })
            return
        
        try:
            # Store feedback for each agent
            for agent_id, feedback in agent_feedback.items():
                feedback_doc = f"""
                AGENT FEEDBACK
                
                Agent: {agent_id}
                Effectiveness Rating: {feedback.get('effectiveness_rating', 'unknown')}
                
                Strengths:
                {chr(10).join([f"- {strength}" for strength in feedback.get('strengths', [])])}
                
                Weaknesses:
                {chr(10).join([f"- {weakness}" for weakness in feedback.get('weaknesses', [])])}
                
                Improvements:
                {chr(10).join([f"- {improvement}" for improvement in feedback.get('improvements', [])])}
                
                Recommendations:
                {chr(10).join([f"- {rec}" for rec in feedback.get('recommendations', [])])}
                
                Priority Actions:
                {chr(10).join([f"- {action}" for action in feedback.get('priority_actions', [])])}
                
                Learning Focus: {feedback.get('learning_focus', 'general improvement')}
                """
                
                self._collections["agent_feedback"].add(
                    documents=[feedback_doc],
                    metadatas=[{"type": "agent_feedback", "agent_id": agent_id}],
                    ids=[f"feedback_{agent_id}_{datetime.utcnow().isoformat()}"]
                )
                
        except Exception as exc:
            logger.error(f"ExperienceLearning | Failed to store agent feedback: {exc}")

    def get_agent_experience(self, agent_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Retrieve relevant experience for a specific agent.
        
        Args:
            agent_id: The agent requesting experience
            context: Current context for relevance matching
            
        Returns:
            Relevant experience data for the agent
        """
        if not self._client:
            # Return from memory
            return {
                "shared_experiences": self._memories["shared_experiences"][-5:],
                "agent_feedback": [f for f in self._memories["agent_feedback"] if f.get("feedback", {}).get(agent_id)],
                "relevant_insights": self._memories["shared_experiences"][-3:]
            }
        
        try:
            # Query relevant collections
            query_text = self._create_experience_query(agent_id, context)
            
            # Get shared experiences
            shared_results = self._collections["shared_experiences"].query(
                query_texts=[query_text], n_results=5, include=["metadatas"]
            )
            
            # Get agent-specific feedback
            feedback_results = self._collections["agent_feedback"].query(
                query_texts=[f"feedback for {agent_id}"], n_results=3, include=["metadatas"]
            )
            
            # Get relevant insights based on agent type
            insights_collection = self._get_insights_collection_for_agent(agent_id)
            insights_results = self._collections[insights_collection].query(
                query_texts=[query_text], n_results=3, include=["metadatas"]
            )
            
            return {
                "shared_experiences": shared_results.get("metadatas", [[]])[0],
                "agent_feedback": feedback_results.get("metadatas", [[]])[0],
                "relevant_insights": insights_results.get("metadatas", [[]])[0]
            }
            
        except Exception as exc:
            logger.error(f"ExperienceLearning | Failed to retrieve experience for {agent_id}: {exc}")
            return {"shared_experiences": [], "agent_feedback": [], "relevant_insights": []}

    def _create_experience_query(self, agent_id: str, context: Dict[str, Any] = None) -> str:
        """Create a query for retrieving relevant experience."""
        context_str = json.dumps(context) if context else "general trading context"
        return f"experience insights for {agent_id} in context: {context_str}"

    def _get_insights_collection_for_agent(self, agent_id: str) -> str:
        """Get the most relevant insights collection for an agent."""
        collection_mapping = {
            "world_monitor": "market_experiences",
            "strategy_agent": "strategy_experiences", 
            "trade_executor": "trade_experiences",
            "risk_assessor": "risk_experiences"
        }
        return collection_mapping.get(agent_id, "shared_experiences")

    def get_system_insights(self, query: str = None) -> Dict[str, Any]:
        """
        Get system-wide insights and lessons learned.
        
        Args:
            query: Optional specific query for insights
            
        Returns:
            System insights and recommendations
        """
        if not self._client:
            # Return from memory
            return {
                "insights": self._memories["shared_experiences"][-10:],
                "lessons_learned": self._memories["performance_analysis"][-5:]
            }
        
        try:
            query_text = query or "system insights and lessons learned"
            
            # Get insights from shared experiences
            shared_results = self._collections["shared_experiences"].query(
                query_texts=[query_text], n_results=10, include=["metadatas"]
            )
            
            # Get performance analysis
            perf_results = self._collections["performance_analysis"].query(
                query_texts=[query_text], n_results=5, include=["metadatas"]
            )
            
            return {
                "insights": shared_results.get("metadatas", [[]])[0],
                "lessons_learned": perf_results.get("metadatas", [[]])[0]
            }
            
        except Exception as exc:
            logger.error(f"ExperienceLearning | Failed to retrieve system insights: {exc}")
            return {"insights": [], "lessons_learned": []}


# Global instance
experience_learning_system = ExperienceLearningSystem() 