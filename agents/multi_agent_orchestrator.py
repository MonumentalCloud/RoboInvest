"""
Multi-Agent Orchestrator
Coordinates autonomous agents working in parallel to hunt for alpha opportunities.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from enum import Enum
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.decision_tree import DecisionTree, NodeType, NodeStatus
from core.config import config
from core.openai_manager import openai_manager
from tools.web_researcher import web_researcher
from tools.calculator import calculator
from tools.data_fetcher import data_fetcher
from tools.backtester import backtester
from agents.rag_playbook import rag_agent
from utils.logger import logger  # type: ignore

class AgentRole(Enum):
    """Specialized agent roles in the system."""
    ALPHA_HUNTER = "alpha_hunter"
    MARKET_SCANNER = "market_scanner"
    SENTIMENT_ANALYST = "sentiment_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    FUNDAMENTAL_RESEARCHER = "fundamental_researcher"
    RISK_ASSESSOR = "risk_assessor"
    STRATEGY_VALIDATOR = "strategy_validator"
    EXECUTION_COORDINATOR = "execution_coordinator"

class AgentStatus(Enum):
    """Agent status in the orchestrator."""
    IDLE = "idle"
    THINKING = "thinking"
    RESEARCHING = "researching" 
    ANALYZING = "analyzing"
    COLLABORATING = "collaborating"
    REPORTING = "reporting"

class AutonomousAgent:
    """Individual autonomous agent with specialized capabilities."""
    
    def __init__(self, agent_id: str, role: AgentRole, orchestrator=None):
        self.id = agent_id
        self.role = role
        self.orchestrator = orchestrator
        self.decision_tree = DecisionTree(agent_name=f"{role.value}_{agent_id}")
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Dict[str, Any]] = None
        self.capabilities = self._define_capabilities()
        self.tools = self._initialize_tools()
        self.memory: List[Dict[str, Any]] = []
        self.collaboration_history: List[Dict[str, Any]] = []
        self.performance_stats = {
            "tasks_completed": 0,
            "successful_insights": 0,
            "collaboration_count": 0,
            "avg_confidence": 0.5
        }
        
    def _define_capabilities(self) -> List[str]:
        """Define agent capabilities based on role."""
        capability_map = {
            AgentRole.ALPHA_HUNTER: [
                "opportunity_scanning", "trend_analysis", "creative_thinking",
                "pattern_recognition", "market_inefficiency_detection"
            ],
            AgentRole.MARKET_SCANNER: [
                "real_time_monitoring", "price_action_analysis", "volume_analysis",
                "sector_scanning", "momentum_detection"
            ],
            AgentRole.SENTIMENT_ANALYST: [
                "news_analysis", "social_sentiment", "market_psychology",
                "event_impact_analysis", "narrative_construction"
            ],
            AgentRole.TECHNICAL_ANALYST: [
                "chart_pattern_recognition", "indicator_analysis", "backtesting",
                "statistical_analysis", "quantitative_modeling"
            ],
            AgentRole.FUNDAMENTAL_RESEARCHER: [
                "company_analysis", "financial_statement_analysis", "competitive_analysis",
                "industry_research", "valuation_modeling"
            ],
            AgentRole.RISK_ASSESSOR: [
                "risk_modeling", "scenario_analysis", "portfolio_impact",
                "correlation_analysis", "stress_testing"
            ],
            AgentRole.STRATEGY_VALIDATOR: [
                "strategy_testing", "performance_validation", "risk_adjustment",
                "optimization", "robustness_testing"
            ],
            AgentRole.EXECUTION_COORDINATOR: [
                "trade_planning", "execution_optimization", "market_impact_analysis",
                "timing_optimization", "order_management"
            ]
        }
        return capability_map.get(self.role, [])
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize tools based on agent capabilities."""
        return {
            "web_researcher": web_researcher,
            "calculator": calculator,
            "data_fetcher": data_fetcher,
            "backtester": backtester,
            "rag_agent": rag_agent,
            "openai_manager": openai_manager
        }
    
    async def think_and_act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main thinking and action cycle for the agent."""
        try:
            self.status = AgentStatus.THINKING
            logger.info(f"Agent {self.id} ({self.role.value}) starting thinking cycle")
            
            # Create root thinking node
            root_id = self.decision_tree.create_root(
                content=f"Analyze opportunity: {context.get('objective', 'Market analysis')}",
                data=context
            )
            
            # Generate hypotheses based on role and context
            hypotheses = await self._generate_hypotheses(context)
            hypothesis_nodes = self.decision_tree.expand_hypotheses(root_id, hypotheses)
            
            # For each hypothesis, create research paths
            research_tasks = []
            for hypothesis_id in hypothesis_nodes:
                tasks = await self._create_research_tasks(hypothesis_id, context)
                research_tasks.extend(tasks)
            
            # Execute research tasks in parallel
            self.status = AgentStatus.RESEARCHING
            research_results = await self._execute_parallel_research(research_tasks)
            
            # Analyze results and form conclusions
            self.status = AgentStatus.ANALYZING
            conclusions = await self._analyze_and_conclude(research_results, context)
            
            # Update performance stats
            self._update_performance_stats(conclusions)
            
            self.status = AgentStatus.IDLE
            logger.info(f"Agent {self.id} completed analysis with {len(conclusions)} insights")
            
            return {
                "agent_id": self.id,
                "role": self.role.value,
                "insights": conclusions,
                "decision_tree": self.decision_tree.to_dict(),
                "confidence": self.decision_tree.best_confidence,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent {self.id} error: {e}")
            self.status = AgentStatus.IDLE
            return {"agent_id": self.id, "error": str(e)}
    
    async def _generate_hypotheses(self, context: Dict[str, Any]) -> List[str]:
        """Generate hypotheses based on agent role and context."""
        
        role_specific_prompts = {
            AgentRole.ALPHA_HUNTER: "What unique investment opportunities might be hidden in current market conditions?",
            AgentRole.MARKET_SCANNER: "What unusual patterns or anomalies are present in current market data?",
            AgentRole.SENTIMENT_ANALYST: "How might current news and sentiment create trading opportunities?",
            AgentRole.TECHNICAL_ANALYST: "What technical patterns suggest potential price movements?",
            AgentRole.FUNDAMENTAL_RESEARCHER: "What fundamental factors might drive future performance?",
            AgentRole.RISK_ASSESSOR: "What risks are being overlooked by the market?",
            AgentRole.STRATEGY_VALIDATOR: "How can we validate and improve current strategies?",
            AgentRole.EXECUTION_COORDINATOR: "What's the optimal way to execute identified opportunities?"
        }
        
        base_prompt = role_specific_prompts.get(self.role, "What insights can be derived from this context?")
        
        try:
            hypothesis_prompt = f"""You are a {self.role.value} agent with expertise in {', '.join(self.capabilities)}.
            
            Context: {json.dumps(context, indent=2)}
            
            {base_prompt}
            
            Generate 3-5 specific, actionable hypotheses that leverage your expertise.
            Each hypothesis should be:
            1. Specific and testable
            2. Relevant to finding alpha opportunities
            3. Aligned with your role capabilities
            
            Respond with a JSON array of hypothesis strings:
            ["hypothesis 1", "hypothesis 2", "hypothesis 3"]
            """
            
            response = await openai_manager.chat_completion([
                {"role": "user", "content": hypothesis_prompt}
            ], temperature=0.7)
            
            hypotheses = json.loads(response.get("content", "[]"))
            
            if not isinstance(hypotheses, list):
                hypotheses = ["Analyze current market conditions for opportunities"]
                
            return hypotheses[:5]  # Limit to 5 hypotheses
            
        except Exception as e:
            logger.error(f"Hypothesis generation error for {self.id}: {e}")
            return [f"Investigate {self.role.value} opportunities in current market"]
    
    async def _create_research_tasks(self, hypothesis_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create specific research tasks for a hypothesis."""
        
        hypothesis_node = self.decision_tree.nodes[hypothesis_id]
        hypothesis_content = hypothesis_node.content
        
        # Define research tasks based on capabilities
        task_generators = {
            "opportunity_scanning": self._create_opportunity_scan_task,
            "news_analysis": self._create_news_analysis_task,
            "technical_analysis": self._create_technical_analysis_task,
            "fundamental_analysis": self._create_fundamental_analysis_task,
            "risk_analysis": self._create_risk_analysis_task,
            "backtesting": self._create_backtesting_task
        }
        
        tasks = []
        
        # Generate tasks based on agent capabilities
        for capability in self.capabilities[:3]:  # Limit to top 3 capabilities
            if capability in task_generators:
                task = await task_generators[capability](hypothesis_content, context)
                if task:
                    # Add research node to decision tree
                    research_id = self.decision_tree.add_node(
                        parent_id=hypothesis_id,
                        node_type=NodeType.RESEARCH,
                        content=task["description"],
                        data=task,
                        executor=task["executor"]
                    )
                    task["node_id"] = research_id
                    tasks.append(task)
        
        return tasks
    
    async def _create_opportunity_scan_task(self, hypothesis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create opportunity scanning task."""
        return {
            "type": "opportunity_scan",
            "description": f"Scan for opportunities related to: {hypothesis}",
            "hypothesis": hypothesis,
            "context": context,
            "executor": self._execute_opportunity_scan
        }
    
    async def _create_news_analysis_task(self, hypothesis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create news analysis task."""
        return {
            "type": "news_analysis",
            "description": f"Analyze news impact on: {hypothesis}",
            "hypothesis": hypothesis,
            "context": context,
            "executor": self._execute_news_analysis
        }
    
    async def _create_technical_analysis_task(self, hypothesis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create technical analysis task."""
        return {
            "type": "technical_analysis",
            "description": f"Technical analysis for: {hypothesis}",
            "hypothesis": hypothesis,
            "context": context,
            "executor": self._execute_technical_analysis
        }
    
    async def _create_fundamental_analysis_task(self, hypothesis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fundamental analysis task."""
        return {
            "type": "fundamental_analysis",
            "description": f"Fundamental analysis for: {hypothesis}",
            "hypothesis": hypothesis,
            "context": context,
            "executor": self._execute_fundamental_analysis
        }
    
    async def _create_risk_analysis_task(self, hypothesis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk analysis task."""
        return {
            "type": "risk_analysis",
            "description": f"Risk assessment for: {hypothesis}",
            "hypothesis": hypothesis,
            "context": context,
            "executor": self._execute_risk_analysis
        }
    
    async def _create_backtesting_task(self, hypothesis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create backtesting task."""
        return {
            "type": "backtesting",
            "description": f"Backtest strategy for: {hypothesis}",
            "hypothesis": hypothesis,
            "context": context,
            "executor": self._execute_backtesting
        }
    
    # Task Executors
    async def _execute_opportunity_scan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute opportunity scanning."""
        try:
            hypothesis = task_data.get("hypothesis", "")
            
            # Use web researcher to scan for opportunities
            research_result = web_researcher.research_opportunity(
                {"theme": hypothesis}, 
                task_data.get("context", {}).get("symbols", ["SPY"])
            )
            
            return {
                "type": "opportunity_scan",
                "result": research_result,
                "confidence": research_result.get("report", {}).get("confidence", 0.5),
                "insights": [research_result.get("report", {}).get("executive_summary", "")]
            }
            
        except Exception as e:
            return {"type": "opportunity_scan", "error": str(e), "confidence": 0.1}
    
    async def _execute_news_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute news analysis."""
        try:
            hypothesis = task_data.get("hypothesis", "")
            
            # Search for relevant news
            news_results = web_researcher._web_search(hypothesis + " market impact news")
            
            if not news_results:
                return {"type": "news_analysis", "result": "No relevant news found", "confidence": 0.3}
            
            # Analyze news impact using LLM
            analysis_prompt = f"""Analyze the market impact of this news for the hypothesis: {hypothesis}
            
            News Results: {json.dumps(news_results[:3], indent=2)}
            
            Provide analysis in JSON:
            {{
                "sentiment": "bullish/bearish/neutral",
                "impact_level": "high/medium/low", 
                "key_insights": ["insight1", "insight2"],
                "confidence": 0.0-1.0
            }}"""
            
            response = await openai_manager.chat_completion([
                {"role": "user", "content": analysis_prompt}
            ], temperature=0.3)
            
            analysis = json.loads(response.get("content", "{}"))
            
            return {
                "type": "news_analysis",
                "result": analysis,
                "confidence": analysis.get("confidence", 0.5),
                "insights": analysis.get("key_insights", [])
            }
            
        except Exception as e:
            return {"type": "news_analysis", "error": str(e), "confidence": 0.1}
    
    async def _execute_technical_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute technical analysis."""
        try:
            symbols = task_data.get("context", {}).get("symbols", ["SPY"])
            symbol = symbols[0] if symbols else "SPY"
            
            # Get historical data
            historical_data = data_fetcher.get_historical_data(symbol, period="6mo")
            
            if not historical_data.get("data"):
                return {"type": "technical_analysis", "error": "No data available", "confidence": 0.1}
            
            # Perform technical calculations
            prices = historical_data["data"]["prices"]["close"]
            
            volatility_result = calculator.calculate("volatility analysis", {"prices": prices})
            momentum_result = calculator.calculate("momentum analysis", {"prices": prices})
            
            return {
                "type": "technical_analysis",
                "result": {
                    "volatility": volatility_result,
                    "momentum": momentum_result,
                    "symbol": symbol
                },
                "confidence": 0.7,
                "insights": [f"Technical analysis for {symbol} completed"]
            }
            
        except Exception as e:
            return {"type": "technical_analysis", "error": str(e), "confidence": 0.1}
    
    async def _execute_fundamental_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fundamental analysis."""
        try:
            symbols = task_data.get("context", {}).get("symbols", ["SPY"])
            hypothesis = task_data.get("hypothesis", "")
            
            # Use web researcher for fundamental analysis
            research_result = web_researcher._analyze_fundamentals(symbols[:2])
            
            return {
                "type": "fundamental_analysis",
                "result": research_result,
                "confidence": research_result.get("confidence", 0.5),
                "insights": [f"Fundamental analysis for {symbols} related to {hypothesis}"]
            }
            
        except Exception as e:
            return {"type": "fundamental_analysis", "error": str(e), "confidence": 0.1}
    
    async def _execute_risk_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute risk analysis."""
        try:
            symbols = task_data.get("context", {}).get("symbols", ["SPY"])
            symbol = symbols[0] if symbols else "SPY"
            
            # Get historical data for risk calculations
            historical_data = data_fetcher.get_historical_data(symbol, period="1y")
            
            if not historical_data.get("data"):
                return {"type": "risk_analysis", "error": "No data available", "confidence": 0.1}
            
            prices = historical_data["data"]["prices"]["close"]
            
            # Calculate risk metrics
            volatility_result = calculator.calculate("volatility analysis", {"prices": prices})
            drawdown_result = calculator.calculate("drawdown analysis", {"prices": prices})
            
            return {
                "type": "risk_analysis",
                "result": {
                    "volatility_metrics": volatility_result,
                    "drawdown_metrics": drawdown_result,
                    "symbol": symbol
                },
                "confidence": 0.6,
                "insights": [f"Risk analysis for {symbol} shows volatility and drawdown patterns"]
            }
            
        except Exception as e:
            return {"type": "risk_analysis", "error": str(e), "confidence": 0.1}
    
    async def _execute_backtesting(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backtesting."""
        try:
            symbols = task_data.get("context", {}).get("symbols", ["SPY"])
            symbol = symbols[0] if symbols else "SPY"
            
            # Simple backtest over last 3 months
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            backtest_result = backtester.run_backtest(symbol, start_date, end_date)
            
            return {
                "type": "backtesting",
                "result": backtest_result,
                "confidence": 0.6 if not backtest_result.get("error") else 0.2,
                "insights": [f"Backtesting analysis for {symbol} strategy"]
            }
            
        except Exception as e:
            return {"type": "backtesting", "error": str(e), "confidence": 0.1}
    
    async def _execute_parallel_research(self, research_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute research tasks in parallel."""
        if not research_tasks:
            return []
        
        # Extract node IDs for parallel execution
        node_ids = [task.get("node_id") for task in research_tasks if task.get("node_id")]
        
        # Execute nodes in parallel using decision tree
        results = await self.decision_tree.execute_parallel_branches(node_ids)
        
        return results
    
    async def _analyze_and_conclude(self, research_results: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze research results and form conclusions."""
        try:
            if not research_results:
                return []
            
            # Filter successful results
            successful_results = [r for r in research_results if not r.get("error")]
            
            if not successful_results:
                return []
            
            # Synthesize insights using LLM
            synthesis_prompt = f"""You are a {self.role.value} agent synthesizing research results.
            
            Research Results: {json.dumps(successful_results, indent=2)}
            
            Original Context: {json.dumps(context, indent=2)}
            
            Synthesize the results into actionable insights:
            1. Key findings from the research
            2. Investment implications
            3. Risk considerations
            4. Recommended actions
            5. Confidence assessment
            
            Respond in JSON:
            {{
                "key_findings": ["finding1", "finding2"],
                "investment_implications": "implications text",
                "risk_considerations": "risk text", 
                "recommended_actions": ["action1", "action2"],
                "overall_confidence": 0.0-1.0,
                "priority": "high/medium/low"
            }}"""
            
            response = await openai_manager.chat_completion([
                {"role": "user", "content": synthesis_prompt}
            ], temperature=0.2)
            
            synthesis = json.loads(response.get("content", "{}"))
            
            # Create conclusion node in decision tree
            conclusion_id = self.decision_tree.add_node(
                parent_id=self.decision_tree.root_id,
                node_type=NodeType.DECISION,
                content="Final synthesis and recommendations",
                data=synthesis
            )
            
            # Update node with results
            if conclusion_id:
                conclusion_node = self.decision_tree.nodes[conclusion_id]
                conclusion_node.result = synthesis
                conclusion_node.confidence = synthesis.get("overall_confidence", 0.5)
                conclusion_node.status = NodeStatus.COMPLETED
            
            # Find best path
            self.decision_tree.find_best_path()
            
            return [synthesis]
            
        except Exception as e:
            logger.error(f"Analysis synthesis error for {self.id}: {e}")
            return []
    
    def _update_performance_stats(self, conclusions: List[Dict[str, Any]]):
        """Update agent performance statistics."""
        self.performance_stats["tasks_completed"] += 1
        
        if conclusions:
            self.performance_stats["successful_insights"] += len(conclusions)
            
            # Update average confidence
            confidences = [c.get("overall_confidence", 0.5) for c in conclusions]
            if confidences:
                current_avg = self.performance_stats["avg_confidence"]
                new_avg = sum(confidences) / len(confidences)
                # Exponential moving average
                self.performance_stats["avg_confidence"] = 0.7 * current_avg + 0.3 * new_avg

class MultiAgentOrchestrator:
    """Orchestrates multiple autonomous agents working in parallel."""
    
    def __init__(self, max_agents: int = 8):
        self.max_agents = max_agents
        self.agents: Dict[str, AutonomousAgent] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.collaboration_network: Dict[str, Set[str]] = {}
        self.shared_memory: Dict[str, Any] = {}
        self.orchestration_stats = {
            "total_orchestrations": 0,
            "successful_collaborations": 0,
            "insights_generated": 0
        }
        
    def initialize_agent_swarm(self) -> Dict[str, str]:
        """Initialize the agent swarm with specialized roles."""
        
        agent_configs = [
            ("alpha_01", AgentRole.ALPHA_HUNTER),
            ("scanner_01", AgentRole.MARKET_SCANNER),
            ("sentiment_01", AgentRole.SENTIMENT_ANALYST),
            ("technical_01", AgentRole.TECHNICAL_ANALYST),
            ("fundamental_01", AgentRole.FUNDAMENTAL_RESEARCHER),
            ("risk_01", AgentRole.RISK_ASSESSOR),
            ("validator_01", AgentRole.STRATEGY_VALIDATOR),
            ("executor_01", AgentRole.EXECUTION_COORDINATOR)
        ]
        
        created_agents = {}
        
        for agent_id, role in agent_configs[:self.max_agents]:
            agent = AutonomousAgent(agent_id, role, self)
            self.agents[agent_id] = agent
            created_agents[agent_id] = role.value
            
            # Initialize collaboration network
            self.collaboration_network[agent_id] = set()
            
        logger.info(f"Orchestrator | Initialized {len(self.agents)} autonomous agents")
        return created_agents
    
    async def orchestrate_alpha_hunt(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate parallel alpha hunting across all agents."""
        try:
            self.orchestration_stats["total_orchestrations"] += 1
            
            logger.info("Orchestrator | Starting parallel alpha hunt")
            
            # Prepare context for each agent
            agent_contexts = self._prepare_agent_contexts(market_context)
            
            # Launch all agents in parallel
            agent_tasks = {}
            for agent_id, context in agent_contexts.items():
                if agent_id in self.agents:
                    task = asyncio.create_task(
                        self.agents[agent_id].think_and_act(context)
                    )
                    agent_tasks[agent_id] = task
            
            # Wait for all agents to complete
            logger.info(f"Orchestrator | Launched {len(agent_tasks)} parallel agents")
            agent_results = {}
            
            for agent_id, task in agent_tasks.items():
                try:
                    result = await task
                    agent_results[agent_id] = result
                except Exception as e:
                    logger.error(f"Agent {agent_id} failed: {e}")
                    agent_results[agent_id] = {"agent_id": agent_id, "error": str(e)}
            
            # Synthesize results across agents
            synthesis = await self._synthesize_agent_results(agent_results, market_context)
            
            # Update orchestration stats
            successful_agents = len([r for r in agent_results.values() if not r.get("error")])
            self.orchestration_stats["successful_collaborations"] += successful_agents
            
            total_insights = sum(len(r.get("insights", [])) for r in agent_results.values())
            self.orchestration_stats["insights_generated"] += total_insights
            
            logger.info(f"Orchestrator | Completed with {successful_agents}/{len(agent_tasks)} successful agents")
            
            return {
                "orchestration_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "agent_results": agent_results,
                "synthesis": synthesis,
                "stats": {
                    "successful_agents": successful_agents,
                    "total_agents": len(agent_tasks),
                    "total_insights": total_insights
                }
            }
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return {"error": str(e)}
    
    def _prepare_agent_contexts(self, market_context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Prepare specialized contexts for each agent based on their role."""
        base_context = {
            "timestamp": datetime.now().isoformat(),
            "market_overview": market_context.get("market", {}),
            "symbols": market_context.get("symbols", ["SPY", "QQG", "IWM"])
        }
        
        agent_contexts = {}
        
        for agent_id, agent in self.agents.items():
            context = base_context.copy()
            
            # Add role-specific context
            if agent.role == AgentRole.ALPHA_HUNTER:
                context["objective"] = "Scan for unique alpha opportunities in current market"
                context["focus"] = "creative opportunity identification"
                
            elif agent.role == AgentRole.MARKET_SCANNER:
                context["objective"] = "Monitor real-time market patterns and anomalies"
                context["focus"] = "price action and volume analysis"
                
            elif agent.role == AgentRole.SENTIMENT_ANALYST:
                context["objective"] = "Analyze market sentiment and news impact"
                context["focus"] = "sentiment and narrative analysis"
                context["news"] = market_context.get("news", [])
                
            elif agent.role == AgentRole.TECHNICAL_ANALYST:
                context["objective"] = "Identify technical patterns and signals"
                context["focus"] = "chart patterns and indicators"
                
            elif agent.role == AgentRole.FUNDAMENTAL_RESEARCHER:
                context["objective"] = "Research fundamental drivers and valuations"
                context["focus"] = "company and sector fundamentals"
                
            elif agent.role == AgentRole.RISK_ASSESSOR:
                context["objective"] = "Assess risks and potential downsides"
                context["focus"] = "risk identification and mitigation"
                
            elif agent.role == AgentRole.STRATEGY_VALIDATOR:
                context["objective"] = "Validate and optimize trading strategies"
                context["focus"] = "strategy testing and improvement"
                
            elif agent.role == AgentRole.EXECUTION_COORDINATOR:
                context["objective"] = "Plan optimal trade execution"
                context["focus"] = "execution planning and optimization"
            
            agent_contexts[agent_id] = context
            
        return agent_contexts
    
    async def _synthesize_agent_results(self, agent_results: Dict[str, Any], market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from multiple agents into actionable intelligence."""
        try:
            # Filter successful results
            successful_results = {k: v for k, v in agent_results.items() if not v.get("error")}
            
            if not successful_results:
                return {"synthesis": "No successful agent results to synthesize"}
            
            # Extract insights from all agents
            all_insights = []
            confidence_scores = []
            
            for agent_id, result in successful_results.items():
                insights = result.get("insights", [])
                confidence = result.get("confidence", 0.5)
                
                all_insights.extend(insights)
                confidence_scores.append(confidence)
            
            if not all_insights:
                return {"synthesis": "No insights generated by agents"}
            
            # Use LLM to synthesize insights
            synthesis_prompt = f"""You are the master orchestrator synthesizing insights from {len(successful_results)} specialized AI agents.
            
            Agent Results: {json.dumps(successful_results, indent=2)}
            
            Market Context: {json.dumps(market_context, indent=2)}
            
            Synthesize the collective intelligence into:
            1. Top 3 alpha opportunities identified
            2. Consensus view across agents
            3. Conflicting viewpoints and how to resolve them
            4. Recommended action plan with priorities
            5. Overall confidence assessment
            6. Risk factors to monitor
            
            Respond in JSON:
            {{
                "top_opportunities": [
                    {{"opportunity": "description", "supporting_agents": ["agent1"], "confidence": 0.0-1.0}},
                    {{"opportunity": "description", "supporting_agents": ["agent2"], "confidence": 0.0-1.0}},
                    {{"opportunity": "description", "supporting_agents": ["agent3"], "confidence": 0.0-1.0}}
                ],
                "consensus_view": "overall market consensus",
                "conflicting_views": "areas of disagreement and resolution",
                "action_plan": [
                    {{"action": "description", "priority": "high/medium/low", "timeline": "timeframe"}}
                ],
                "overall_confidence": 0.0-1.0,
                "risk_factors": ["risk1", "risk2"],
                "next_steps": ["step1", "step2"]
            }}"""
            
            response = await openai_manager.chat_completion([
                {"role": "user", "content": synthesis_prompt}
            ], temperature=0.2)
            
            synthesis = json.loads(response.get("content", "{}"))
            
            # Add metadata
            synthesis["meta"] = {
                "participating_agents": len(successful_results),
                "total_insights": len(all_insights),
                "avg_agent_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5,
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {"synthesis_error": str(e)}
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator and all agents."""
        agent_status = {}
        
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "role": agent.role.value,
                "status": agent.status.value,
                "performance": agent.performance_stats,
                "current_task": agent.current_task.get("type") if agent.current_task else None,
                "tree_summary": agent.decision_tree.get_summary()
            }
        
        return {
            "orchestrator_stats": self.orchestration_stats,
            "total_agents": len(self.agents),
            "agent_status": agent_status,
            "shared_memory_size": len(self.shared_memory)
        }


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()

# Initialize agent swarm on import
agent_swarm = orchestrator.initialize_agent_swarm()
logger.info(f"MultiAgentOrchestrator | Initialized with roles: {list(agent_swarm.values())}") 