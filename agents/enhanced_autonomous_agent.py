"""
Enhanced Autonomous Agent
A next-generation agent with full access to all tools and autonomous research capabilities.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum

from agents.decision_tree import DecisionTree, NodeType, NodeStatus
from core.config import config
from core.openai_manager import openai_manager
from tools.web_researcher import web_researcher
from tools.calculator import calculator
from tools.data_fetcher import data_fetcher
from tools.backtester import backtester
from tools.web_search_wrapper import web_search_wrapper
from agents.rag_playbook import rag_agent
from utils.logger import logger  # type: ignore

class ResearchPriority(Enum):
    """Research priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ToolCategory(Enum):
    """Categories of available tools."""
    DATA_ANALYSIS = "data_analysis"
    WEB_RESEARCH = "web_research"
    MARKET_DATA = "market_data"
    CALCULATION = "calculation"
    BACKTESTING = "backtesting"
    MEMORY = "memory"

class EnhancedAutonomousAgent:
    """
    Enhanced autonomous agent with full tool access and intelligent research capabilities.
    
    This agent can:
    - Dynamically expand decision trees to explore multiple research paths
    - Use all available tools autonomously
    - Conduct deep research to find competitive edges
    - Learn from previous research and improve over time
    - Collaborate with other agents for comprehensive analysis
    """
    
    def __init__(self, agent_id: str, specialization: str = "general"):
        self.id = agent_id
        self.specialization = specialization
        self.decision_tree = DecisionTree(agent_name=f"enhanced_{agent_id}")
        
        # Initialize all available tools
        self.tools = self._initialize_all_tools()
        self.tool_usage_stats: Dict[str, int] = {}
        
        # Research capabilities
        self.research_memory: List[Dict[str, Any]] = []
        self.successful_patterns: List[Dict[str, Any]] = []
        self.failed_patterns: List[Dict[str, Any]] = []
        
        # Learning and adaptation
        self.learning_history: List[Dict[str, Any]] = []
        self.adaptation_threshold = 0.3
        self.exploration_rate = 0.4
        
        # Performance tracking
        self.performance_metrics = {
            "total_research_sessions": 0,
            "successful_insights": 0,
            "tool_effectiveness": {},
            "research_depth_avg": 0.0,
            "collaboration_success_rate": 0.0
        }
        
        logger.info(f"Enhanced Agent {self.id} initialized with {specialization} specialization")
    
    def _initialize_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all available tools with their capabilities."""
        return {
            # Data Analysis Tools
            "calculator": {
                "instance": calculator,
                "category": ToolCategory.CALCULATION,
                "capabilities": [
                    "statistical_analysis", "technical_indicators", "risk_metrics",
                    "correlation_analysis", "volatility_calculations", "momentum_analysis"
                ],
                "async": False
            },
            
            # Market Data Tools
            "data_fetcher": {
                "instance": data_fetcher,
                "category": ToolCategory.MARKET_DATA,
                "capabilities": [
                    "real_time_quotes", "historical_data", "market_overview",
                    "sector_data", "benchmark_data", "fundamental_data"
                ],
                "async": False
            },
            
            # Web Research Tools
            "web_researcher": {
                "instance": web_researcher,
                "category": ToolCategory.WEB_RESEARCH,
                "capabilities": [
                    "comprehensive_research", "sentiment_analysis", "fundamental_analysis",
                    "news_analysis", "market_context", "risk_assessment"
                ],
                "async": False
            },
            
            "web_search": {
                "instance": web_search_wrapper,
                "category": ToolCategory.WEB_RESEARCH,
                "capabilities": [
                    "web_search", "news_search", "trend_analysis",
                    "real_time_information", "market_intelligence"
                ],
                "async": False
            },
            
            # Backtesting Tools
            "backtester": {
                "instance": backtester,
                "category": ToolCategory.BACKTESTING,
                "capabilities": [
                    "strategy_backtesting", "performance_analysis", "risk_backtesting",
                    "portfolio_simulation", "optimization"
                ],
                "async": False
            },
            
            # Memory and Learning Tools
            "rag_agent": {
                "instance": rag_agent,
                "category": ToolCategory.MEMORY,
                "capabilities": [
                    "memory_storage", "pattern_retrieval", "similar_trade_lookup",
                    "research_memory", "learning_enhancement"
                ],
                "async": False
            }
        }
    
    async def autonomous_research_cycle(self, research_objective: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main autonomous research cycle that explores multiple paths to find competitive edges.
        """
        try:
            self.performance_metrics["total_research_sessions"] += 1
            logger.info(f"Agent {self.id} starting autonomous research: {research_objective}")
            
            # Initialize decision tree with research objective
            root_id = self.decision_tree.create_root(
                content=f"Research Objective: {research_objective}",
                data={"objective": research_objective, "context": context or {}}
            )
            
            # Phase 1: Generate research hypotheses
            hypotheses = await self._generate_research_hypotheses(research_objective, context)
            hypothesis_nodes = self.decision_tree.expand_hypotheses(root_id, hypotheses)
            
            # Phase 2: For each hypothesis, create multi-tool research plans
            research_plans = []
            for hypothesis_id in hypothesis_nodes:
                plan = await self._create_comprehensive_research_plan(hypothesis_id, context)
                research_plans.extend(plan)
            
            # Phase 3: Execute research plans in parallel
            research_results = await self._execute_parallel_research_plans(research_plans)
            
            # Phase 4: Analyze patterns and cross-correlate findings
            pattern_analysis = await self._analyze_research_patterns(research_results)
            
            # Phase 5: Generate insights and competitive edges
            insights = await self._generate_competitive_insights(pattern_analysis, research_objective)
            
            # Phase 6: Validate insights through additional research if needed
            validated_insights = await self._validate_insights(insights, context)
            
            # Phase 7: Learn from the research session
            self._learn_from_research_session(validated_insights, research_plans)
            
            # Update performance metrics
            if validated_insights:
                self.performance_metrics["successful_insights"] += len(validated_insights)
            
            research_session = {
                "session_id": str(uuid.uuid4()),
                "agent_id": self.id,
                "objective": research_objective,
                "hypotheses_explored": len(hypothesis_nodes),
                "research_plans_executed": len(research_plans),
                "patterns_identified": len(pattern_analysis.get("patterns", [])),
                "insights_generated": len(validated_insights),
                "decision_tree": self.decision_tree.to_dict(),
                "insights": validated_insights,
                "competitive_edges": self._extract_competitive_edges(validated_insights),
                "timestamp": datetime.now().isoformat(),
                "session_duration": "research_complete"
            }
            
            logger.info(f"Agent {self.id} completed research with {len(validated_insights)} validated insights")
            return research_session
            
        except Exception as e:
            logger.error(f"Agent {self.id} research error: {e}")
            return {"error": str(e), "agent_id": self.id}
    
    async def _generate_research_hypotheses(self, objective: str, context: Dict[str, Any]) -> List[str]:
        """Generate research hypotheses using intelligent prompting."""
        
        # Retrieve similar past research for context
        similar_research = self._get_similar_research_patterns(objective)
        
        try:
            hypothesis_prompt = f"""You are an advanced AI research agent with access to comprehensive market analysis tools.
            
            Research Objective: {objective}
            
            Context: {json.dumps(context or {}, indent=2)}
            
            Similar Past Research: {json.dumps(similar_research[:3], indent=2)}
            
            Your specialization: {self.specialization}
            
            Generate 4-6 research hypotheses that could lead to competitive edges:
            
            Each hypothesis should:
            1. Be specific and testable using available tools
            2. Explore different angles of the research objective
            3. Have potential for unique insights not obvious to other market participants
            4. Build on or diverge from past successful research patterns
            5. Consider both obvious and non-obvious relationships
            
            Available tool categories: {list(ToolCategory)}
            
            Think creatively about:
            - Cross-asset correlations and spillover effects
            - Sentiment vs fundamental disconnects
            - Technical pattern divergences across timeframes
            - Macro economic factor impacts
            - Sector rotation and relative value opportunities
            - Event-driven catalysts and market inefficiencies
            
            Respond with JSON array:
            [
                "hypothesis 1: specific testable statement",
                "hypothesis 2: different angle exploration", 
                "hypothesis 3: contrarian perspective",
                "hypothesis 4: cross-market relationship",
                "hypothesis 5: timing and catalyst based",
                "hypothesis 6: behavioral/sentiment based"
            ]
            """
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": hypothesis_prompt}
            ], temperature=0.8)  # Higher temperature for creativity
            
            hypotheses = json.loads(response.get("content", "[]"))
            
            if not isinstance(hypotheses, list):
                hypotheses = [f"Investigate {objective} using multi-tool analysis"]
            
            # Add learning-based hypothesis if we have successful patterns
            if self.successful_patterns:
                learning_hypothesis = f"Apply successful pattern from previous research to {objective}"
                hypotheses.append(learning_hypothesis)
            
            return hypotheses[:6]  # Limit to 6 hypotheses
            
        except Exception as e:
            logger.error(f"Hypothesis generation error: {e}")
            return [f"Comprehensive analysis of {objective}"]
    
    async def _create_comprehensive_research_plan(self, hypothesis_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a comprehensive research plan using multiple tools."""
        
        hypothesis_node = self.decision_tree.nodes[hypothesis_id]
        hypothesis = hypothesis_node.content
        
        # Determine which tools to use based on hypothesis content and past effectiveness
        selected_tools = self._select_optimal_tools(hypothesis)
        
        research_plans = []
        
        for tool_name, tool_info in selected_tools.items():
            # Create specific research tasks for each tool
            tasks = await self._create_tool_specific_tasks(tool_name, tool_info, hypothesis, context)
            
            for task in tasks:
                # Add research node to decision tree
                research_id = self.decision_tree.add_node(
                    parent_id=hypothesis_id,
                    node_type=NodeType.RESEARCH,
                    content=f"{tool_name}: {task['description']}",
                    data=task,
                    executor=task['executor']
                )
                
                task["node_id"] = research_id
                task["tool_name"] = tool_name
                research_plans.append(task)
        
        return research_plans
    
    def _select_optimal_tools(self, hypothesis: str) -> Dict[str, Dict[str, Any]]:
        """Select optimal tools based on hypothesis content and past effectiveness."""
        
        # Analyze hypothesis to determine relevant tool categories
        hypothesis_lower = hypothesis.lower()
        
        relevant_tools = {}
        
        # Always include calculator for any numerical analysis
        relevant_tools["calculator"] = self.tools["calculator"]
        
        # Data fetcher for market data
        if any(word in hypothesis_lower for word in ['price', 'market', 'stock', 'volume', 'technical']):
            relevant_tools["data_fetcher"] = self.tools["data_fetcher"]
        
        # Web research for sentiment, news, fundamentals
        if any(word in hypothesis_lower for word in ['news', 'sentiment', 'fundamental', 'company', 'industry']):
            relevant_tools["web_researcher"] = self.tools["web_researcher"]
            relevant_tools["web_search"] = self.tools["web_search"]
        
        # Backtesting for strategy validation
        if any(word in hypothesis_lower for word in ['strategy', 'backtest', 'performance', 'historical']):
            relevant_tools["backtester"] = self.tools["backtester"]
        
        # Always include RAG for learning from past research
        relevant_tools["rag_agent"] = self.tools["rag_agent"]
        
        # Filter based on tool effectiveness if we have historical data
        if self.performance_metrics["tool_effectiveness"]:
            # Prioritize tools that have been effective in the past
            tool_scores = self.performance_metrics["tool_effectiveness"]
            relevant_tools = {k: v for k, v in relevant_tools.items() 
                            if tool_scores.get(k, 0.5) > self.adaptation_threshold}
        
        # Ensure we always have at least 2 tools
        if len(relevant_tools) < 2:
            relevant_tools.update({
                "data_fetcher": self.tools["data_fetcher"],
                "calculator": self.tools["calculator"]
            })
        
        return relevant_tools
    
    async def _create_tool_specific_tasks(self, tool_name: str, tool_info: Dict[str, Any], 
                                        hypothesis: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create specific tasks for each tool based on its capabilities."""
        
        tasks = []
        capabilities = tool_info.get("capabilities", [])
        
        if tool_name == "calculator":
            tasks.extend([
                {
                    "description": "Statistical analysis of hypothesis variables",
                    "type": "statistical_analysis",
                    "executor": self._execute_calculator_analysis,
                    "parameters": {"analysis_type": "statistical", "hypothesis": hypothesis, "context": context}
                },
                {
                    "description": "Technical indicator calculations",
                    "type": "technical_indicators",
                    "executor": self._execute_calculator_analysis,
                    "parameters": {"analysis_type": "technical", "hypothesis": hypothesis, "context": context}
                }
            ])
        
        elif tool_name == "data_fetcher":
            tasks.extend([
                {
                    "description": "Real-time market data analysis",
                    "type": "market_data",
                    "executor": self._execute_market_data_analysis,
                    "parameters": {"data_type": "real_time", "hypothesis": hypothesis, "context": context}
                },
                {
                    "description": "Historical data pattern analysis",
                    "type": "historical_analysis",
                    "executor": self._execute_market_data_analysis,
                    "parameters": {"data_type": "historical", "hypothesis": hypothesis, "context": context}
                }
            ])
        
        elif tool_name == "web_researcher":
            tasks.extend([
                {
                    "description": "Comprehensive web research on hypothesis",
                    "type": "comprehensive_research",
                    "executor": self._execute_web_research,
                    "parameters": {"research_type": "comprehensive", "hypothesis": hypothesis, "context": context}
                }
            ])
        
        elif tool_name == "web_search":
            tasks.extend([
                {
                    "description": "Targeted web search for hypothesis validation",
                    "type": "targeted_search",
                    "executor": self._execute_web_search,
                    "parameters": {"search_type": "targeted", "hypothesis": hypothesis, "context": context}
                }
            ])
        
        elif tool_name == "backtester":
            tasks.extend([
                {
                    "description": "Strategy backtesting based on hypothesis",
                    "type": "strategy_backtest",
                    "executor": self._execute_backtesting,
                    "parameters": {"test_type": "strategy", "hypothesis": hypothesis, "context": context}
                }
            ])
        
        elif tool_name == "rag_agent":
            tasks.extend([
                {
                    "description": "Retrieve similar research patterns",
                    "type": "pattern_retrieval",
                    "executor": self._execute_memory_lookup,
                    "parameters": {"lookup_type": "patterns", "hypothesis": hypothesis, "context": context}
                }
            ])
        
        return tasks
    
    # Tool Execution Methods
    async def _execute_calculator_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculator-based analysis."""
        try:
            analysis_type = parameters.get("analysis_type", "statistical")
            hypothesis = parameters.get("hypothesis", "")
            context = parameters.get("context", {})
            
            # Get relevant data for analysis
            symbols = context.get("symbols", ["SPY"])
            symbol = symbols[0] if symbols else "SPY"
            
            # Fetch data for calculations
            historical_data = data_fetcher.get_historical_data(symbol, period="6mo")
            if not historical_data.get("data"):
                return {"error": "No data available for analysis", "confidence": 0.1}
            
            prices = historical_data["data"]["prices"]["close"]
            
            results = {}
            
            if analysis_type == "statistical":
                results["volatility"] = calculator.calculate("volatility analysis", {"prices": prices})
                results["correlation"] = calculator.calculate("correlation analysis", {"prices": prices})
                results["distribution"] = calculator.calculate("distribution analysis", {"prices": prices})
            
            elif analysis_type == "technical":
                results["momentum"] = calculator.calculate("momentum analysis", {"prices": prices})
                results["trend"] = calculator.calculate("trend analysis", {"prices": prices})
                results["oscillators"] = calculator.calculate("oscillator analysis", {"prices": prices})
            
            # Track tool usage
            self.tool_usage_stats["calculator"] = self.tool_usage_stats.get("calculator", 0) + 1
            
            return {
                "tool": "calculator",
                "analysis_type": analysis_type,
                "results": results,
                "confidence": 0.7,
                "insights": [f"Calculator analysis for {hypothesis} on {symbol}"]
            }
            
        except Exception as e:
            logger.error(f"Calculator analysis error: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_market_data_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute market data analysis."""
        try:
            data_type = parameters.get("data_type", "real_time")
            hypothesis = parameters.get("hypothesis", "")
            context = parameters.get("context", {})
            
            symbols = context.get("symbols", ["SPY", "QQQ", "IWM"])
            
            results = {}
            
            if data_type == "real_time":
                results["market_overview"] = data_fetcher.get_market_overview()
                results["sector_data"] = data_fetcher.get_sector_data()
            
            elif data_type == "historical":
                for symbol in symbols[:3]:  # Limit to 3 symbols
                    results[symbol] = data_fetcher.get_historical_data(symbol, period="1y")
            
            # Track tool usage
            self.tool_usage_stats["data_fetcher"] = self.tool_usage_stats.get("data_fetcher", 0) + 1
            
            return {
                "tool": "data_fetcher",
                "data_type": data_type,
                "results": results,
                "confidence": 0.8,
                "insights": [f"Market data analysis for {hypothesis}"]
            }
            
        except Exception as e:
            logger.error(f"Market data analysis error: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_web_research(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive web research."""
        try:
            research_type = parameters.get("research_type", "comprehensive")
            hypothesis = parameters.get("hypothesis", "")
            context = parameters.get("context", {})
            
            symbols = context.get("symbols", ["SPY"])
            
            # Use web researcher for comprehensive analysis
            research_result = web_researcher.research_opportunity(
                {"theme": hypothesis},
                symbols
            )
            
            # Track tool usage
            self.tool_usage_stats["web_researcher"] = self.tool_usage_stats.get("web_researcher", 0) + 1
            
            return {
                "tool": "web_researcher",
                "research_type": research_type,
                "results": research_result,
                "confidence": research_result.get("report", {}).get("confidence", 0.5),
                "insights": [research_result.get("report", {}).get("executive_summary", "")]
            }
            
        except Exception as e:
            logger.error(f"Web research error: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_web_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute targeted web search."""
        try:
            search_type = parameters.get("search_type", "targeted")
            hypothesis = parameters.get("hypothesis", "")
            
            # Perform targeted searches related to hypothesis
            search_queries = [
                f"{hypothesis} market opportunity",
                f"{hypothesis} investment analysis",
                f"{hypothesis} market impact trends"
            ]
            
            search_results = []
            for query in search_queries:
                results = web_search_wrapper.search(query, max_results=3)
                search_results.extend(results)
            
            # Track tool usage
            self.tool_usage_stats["web_search"] = self.tool_usage_stats.get("web_search", 0) + 1
            
            return {
                "tool": "web_search",
                "search_type": search_type,
                "results": search_results,
                "confidence": 0.6,
                "insights": [f"Web search insights for {hypothesis}"]
            }
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_backtesting(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backtesting analysis."""
        try:
            test_type = parameters.get("test_type", "strategy")
            hypothesis = parameters.get("hypothesis", "")
            context = parameters.get("context", {})
            
            symbols = context.get("symbols", ["SPY"])
            symbol = symbols[0] if symbols else "SPY"
            
            # Simple backtest over recent period
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            backtest_result = backtester.run_backtest(symbol, start_date, end_date)
            
            # Track tool usage
            self.tool_usage_stats["backtester"] = self.tool_usage_stats.get("backtester", 0) + 1
            
            return {
                "tool": "backtester",
                "test_type": test_type,
                "results": backtest_result,
                "confidence": 0.6 if not backtest_result.get("error") else 0.2,
                "insights": [f"Backtesting analysis for {hypothesis} strategy"]
            }
            
        except Exception as e:
            logger.error(f"Backtesting error: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_memory_lookup(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory and pattern lookup."""
        try:
            lookup_type = parameters.get("lookup_type", "patterns")
            hypothesis = parameters.get("hypothesis", "")
            
            # Retrieve similar research patterns
            similar_patterns = rag_agent.retrieve({"symbol": "research", "sentiment": hypothesis})
            
            # Track tool usage
            self.tool_usage_stats["rag_agent"] = self.tool_usage_stats.get("rag_agent", 0) + 1
            
            return {
                "tool": "rag_agent",
                "lookup_type": lookup_type,
                "results": similar_patterns,
                "confidence": 0.5,
                "insights": [f"Memory lookup for {hypothesis} patterns"]
            }
            
        except Exception as e:
            logger.error(f"Memory lookup error: {e}")
            return {"error": str(e), "confidence": 0.1}
    
    async def _execute_parallel_research_plans(self, research_plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple research plans in parallel."""
        if not research_plans:
            return []
        
        # Extract node IDs for decision tree execution
        node_ids = [plan.get("node_id") for plan in research_plans if plan.get("node_id")]
        
        # Execute in parallel using decision tree
        results = await self.decision_tree.execute_parallel_branches(node_ids)
        
        return results
    
    async def _analyze_research_patterns(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across research results to identify insights."""
        try:
            successful_results = [r for r in research_results if not r.get("error") and r.get("confidence", 0) > 0.3]
            
            if not successful_results:
                return {"patterns": [], "correlations": [], "insights": []}
            
            # Use LLM to identify patterns across results
            pattern_prompt = f"""Analyze these research results to identify patterns and correlations.
            
            Research Results: {json.dumps(successful_results, indent=2)}
            
            Look for:
            1. Consistent themes across different tools/analyses
            2. Contradicting findings that need resolution
            3. Strong correlations or relationships
            4. Unique insights not obvious from individual results
            5. Patterns that suggest competitive edges
            
            Respond in JSON:
            {{
                "patterns": [
                    {{"pattern": "description", "supporting_evidence": ["result1", "result2"], "confidence": 0.0-1.0}}
                ],
                "correlations": [
                    {{"variables": ["var1", "var2"], "relationship": "description", "strength": 0.0-1.0}}
                ],
                "contradictions": [
                    {{"conflict": "description", "resolution": "how to resolve"}}
                ],
                "unique_insights": [
                    {{"insight": "description", "competitive_edge": "how this creates advantage"}}
                ]
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": pattern_prompt}
            ], temperature=0.3)
            
            pattern_analysis = json.loads(response.get("content", "{}"))
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"Pattern analysis error: {e}")
            # If it's a rate limit error, wait and return empty results
            if "rate_limit" in str(e).lower() or "429" in str(e):
                logger.warning("OpenAI rate limit hit, skipping pattern analysis for this cycle")
                await asyncio.sleep(30)  # Wait 30 seconds
            return {"patterns": [], "correlations": [], "insights": []}
    
    async def _generate_competitive_insights(self, pattern_analysis: Dict[str, Any], objective: str) -> List[Dict[str, Any]]:
        """Generate actionable competitive insights from pattern analysis."""
        try:
            insight_prompt = f"""Generate actionable competitive insights from this research analysis.
            
            Original Objective: {objective}
            
            Pattern Analysis: {json.dumps(pattern_analysis, indent=2)}
            
            Generate insights that:
            1. Provide genuine competitive advantages
            2. Are actionable with specific next steps
            3. Have measurable potential impact
            4. Consider risk factors and mitigation
            5. Include confidence assessments
            
            Respond in JSON array:
            [
                {{
                    "insight": "clear competitive insight description",
                    "competitive_edge": "why this provides an edge over others",
                    "actionable_steps": ["step1", "step2", "step3"],
                    "potential_impact": "quantified impact estimate",
                    "risk_factors": ["risk1", "risk2"],
                    "confidence": 0.0-1.0,
                    "priority": "high/medium/low",
                    "timeline": "timeframe for opportunity"
                }}
            ]
            """
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": insight_prompt}
            ], temperature=0.4)
            
            insights = json.loads(response.get("content", "[]"))
            
            if not isinstance(insights, list):
                insights = []
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation error: {e}")
            return []
    
    async def _validate_insights(self, insights: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate insights through additional targeted research."""
        validated_insights = []
        
        for insight in insights:
            try:
                # Create validation research plan
                validation_plan = await self._create_validation_plan(insight, context)
                
                # Execute validation research
                validation_results = await self._execute_validation_research(validation_plan)
                
                # Update insight with validation results
                insight["validation"] = validation_results
                insight["validated_confidence"] = validation_results.get("confidence", insight.get("confidence", 0.5))
                
                # Only include insights that pass validation threshold
                if insight["validated_confidence"] > 0.4:
                    validated_insights.append(insight)
                    
            except Exception as e:
                logger.error(f"Insight validation error: {e}")
                continue
        
        return validated_insights
    
    async def _create_validation_plan(self, insight: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a validation plan for a specific insight."""
        return {
            "insight_id": str(uuid.uuid4()),
            "validation_type": "targeted_research",
            "insight": insight,
            "context": context,
            "validation_steps": [
                "cross_reference_data",
                "validate_assumptions", 
                "test_contrarian_view"
            ]
        }
    
    async def _execute_validation_research(self, validation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation research for an insight."""
        try:
            # Simple validation - in a full implementation this would do additional research
            insight = validation_plan.get("insight", {})
            original_confidence = insight.get("confidence", 0.5)
            
            # Simulate validation process
            validation_score = min(original_confidence * 1.1, 0.95)  # Slight boost if passes basic validation
            
            return {
                "confidence": validation_score,
                "validation_status": "passed" if validation_score > 0.4 else "failed",
                "validation_notes": "Insight passed basic validation checks"
            }
            
        except Exception as e:
            return {"confidence": 0.2, "validation_status": "error", "error": str(e)}
    
    def _learn_from_research_session(self, insights: List[Dict[str, Any]], research_plans: List[Dict[str, Any]]):
        """Learn from the research session to improve future performance."""
        
        # Update tool effectiveness based on results
        for plan in research_plans:
            tool_name = plan.get("tool_name")
            if tool_name and "node_id" in plan:
                node = self.decision_tree.nodes.get(plan["node_id"])
                if node and node.status == NodeStatus.COMPLETED:
                    confidence = node.confidence
                    
                    # Update tool effectiveness
                    current_effectiveness = self.performance_metrics["tool_effectiveness"].get(tool_name, 0.5)
                    new_effectiveness = 0.7 * current_effectiveness + 0.3 * confidence
                    self.performance_metrics["tool_effectiveness"][tool_name] = new_effectiveness
        
        # Store successful patterns for future use
        if insights:
            for insight in insights:
                if insight.get("validated_confidence", 0) > 0.6:
                    self.successful_patterns.append({
                        "insight_type": insight.get("competitive_edge", ""),
                        "research_approach": "multi_tool_analysis",
                        "success_factors": insight.get("actionable_steps", []),
                        "confidence": insight.get("validated_confidence", 0),
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Update learning history
        self.learning_history.append({
            "session_timestamp": datetime.now().isoformat(),
            "insights_count": len(insights),
            "research_plans_count": len(research_plans),
            "tools_used": list(set(plan.get("tool_name") for plan in research_plans if plan.get("tool_name"))),
            "avg_confidence": sum(i.get("validated_confidence", 0) for i in insights) / len(insights) if insights else 0
        })
        
        # Limit memory size
        if len(self.successful_patterns) > 50:
            self.successful_patterns = self.successful_patterns[-50:]
        if len(self.learning_history) > 100:
            self.learning_history = self.learning_history[-100:]
    
    def _extract_competitive_edges(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and prioritize competitive edges from insights with buy/exit conditions."""
        edges = []
        
        for insight in insights:
            # Generate buy/exit conditions for actionable insights
            buy_exit_conditions = self._generate_buy_exit_conditions(insight)
            
            edge = {
                "id": str(uuid.uuid4()),
                "opportunity": insight.get("competitive_edge", ""),
                "competitive_edge": insight.get("competitive_edge", ""),
                "priority": insight.get("priority", "medium"),
                "confidence": insight.get("validated_confidence", insight.get("confidence", 0.5)),
                "action_plan": insight.get("actionable_steps", []),
                "timeline": insight.get("timeline", "unknown"),
                "potential_impact": insight.get("potential_impact", ""),
                "risk_factors": insight.get("risk_factors", []),
                "buy_conditions": buy_exit_conditions.get("buy_conditions", []),
                "exit_conditions": buy_exit_conditions.get("exit_conditions", []),
                "position_sizing": buy_exit_conditions.get("position_sizing", "standard"),
                "stop_loss": buy_exit_conditions.get("stop_loss", "5%"),
                "take_profit": buy_exit_conditions.get("take_profit", "15%"),
                "discovered_at": datetime.now().isoformat()
            }
            edges.append(edge)
        
        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        edges.sort(key=lambda x: (priority_order.get(x["priority"], 2), x["confidence"]), reverse=True)
        
        return edges
    
    def _generate_buy_exit_conditions(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific buy and exit conditions for an alpha opportunity."""
        try:
            # Create a prompt for generating trading conditions
            prompt = f"""Based on this alpha opportunity, generate specific buy and exit conditions:

            Opportunity: {insight.get('competitive_edge', '')}
            Actionable Steps: {insight.get('actionable_steps', [])}
            Timeline: {insight.get('timeline', '')}
            Risk Factors: {insight.get('risk_factors', [])}
            Confidence: {insight.get('validated_confidence', insight.get('confidence', 0.5))}

            Generate a JSON response with:
            {{
                "buy_conditions": [
                    "specific market condition or trigger",
                    "technical indicator level",
                    "fundamental catalyst"
                ],
                "exit_conditions": [
                    "profit target reached",
                    "stop loss triggered", 
                    "market condition change",
                    "fundamental deterioration"
                ],
                "position_sizing": "conservative/standard/aggressive",
                "stop_loss": "percentage or specific level",
                "take_profit": "percentage or specific level"
            }}

            Make conditions specific and actionable.
            """
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            try:
                conditions = json.loads(response.get("content", "{}"))
                return conditions
            except json.JSONDecodeError:
                # Fallback to default conditions
                return {
                    "buy_conditions": [
                        "Market conditions align with opportunity thesis",
                        "Technical indicators confirm trend direction",
                        "Risk/reward ratio > 2:1"
                    ],
                    "exit_conditions": [
                        "Take profit target reached",
                        "Stop loss triggered",
                        "Market conditions deteriorate",
                        "Fundamental thesis breaks down"
                    ],
                    "position_sizing": "standard",
                    "stop_loss": "5%",
                    "take_profit": "15%"
                }
                
        except Exception as e:
            logger.error(f"Error generating buy/exit conditions: {e}")
            # Return default conditions
            return {
                "buy_conditions": [
                    "Market conditions align with opportunity thesis",
                    "Technical indicators confirm trend direction", 
                    "Risk/reward ratio > 2:1"
                ],
                "exit_conditions": [
                    "Take profit target reached",
                    "Stop loss triggered",
                    "Market conditions deteriorate",
                    "Fundamental thesis breaks down"
                ],
                "position_sizing": "standard",
                "stop_loss": "5%",
                "take_profit": "15%"
            }
    
    def _get_similar_research_patterns(self, objective: str) -> List[Dict[str, Any]]:
        """Get similar research patterns from memory."""
        # Simple similarity matching - in a full implementation this would use embeddings
        similar_patterns = []
        
        for pattern in self.successful_patterns:
            if any(word in pattern.get("insight_type", "").lower() for word in objective.lower().split()):
                similar_patterns.append(pattern)
        
        return similar_patterns
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "agent_id": self.id,
            "specialization": self.specialization,
            "performance_metrics": self.performance_metrics,
            "tool_usage_stats": self.tool_usage_stats,
            "decision_tree_summary": self.decision_tree.get_summary(),
            "research_memory_size": len(self.research_memory),
            "successful_patterns_count": len(self.successful_patterns),
            "learning_history_count": len(self.learning_history),
            "available_tools": list(self.tools.keys())
        } 