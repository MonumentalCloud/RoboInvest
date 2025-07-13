from __future__ import annotations

"""ActionExecutorAgent: AI-powered task executor with LLM reasoning.

Currently supports:
    - news_dive  → stores research memory with AI analysis
    - trade_signal → forwards to TradeExecutorAgent with AI validation
    - custom_tasks → AI-generated task execution

Returns the result dict that downstream nodes can use.
"""
from typing import Any, Dict

from core.openai_manager import openai_manager
from agents.rag_playbook import rag_agent
from agents.trade_executor import TradeExecutorAgent
from utils.logger import logger  # type: ignore

trade_executor = TradeExecutorAgent()


class ActionExecutorAgent:
    """AI-powered task executor that uses LLM reasoning for task execution decisions."""

    def __call__(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        payload = task.get("payload", {})
        logger.info(f"Executing task {task_type}")

        # AI-powered task analysis
        execution_plan = self._analyze_task_execution(task)
        
        if not execution_plan.get("should_execute", True):
            logger.info(f"AI rejected task execution: {execution_plan.get('reasoning', 'No reason provided')}")
            return {
                "status": "rejected", 
                "task": task, 
                "reasoning": execution_plan.get("reasoning", "AI rejected execution")
            }

        # Execute based on task type with AI enhancement
        if task_type == "news_dive":
            return self._execute_news_dive(payload, execution_plan)
        elif task_type == "trade_signal":
            return self._execute_trade_signal(payload, execution_plan)
        else:
            return self._execute_custom_task(task, execution_plan)

    def _analyze_task_execution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze whether and how to execute the task."""
        try:
            prompt = f"""You are an AI task execution analyst. Analyze this task for execution:

Task: {task}

Consider:
1. Task priority and urgency
2. Resource requirements
3. Potential risks and benefits
4. Execution timing
5. Dependencies and prerequisites

Respond in JSON format:
{{
    "should_execute": true/false,
    "reasoning": "detailed explanation",
    "execution_priority": "high/medium/low",
    "estimated_duration": "time estimate",
    "required_resources": ["list", "of", "resources"],
    "risk_assessment": "risk level and concerns",
    "optimization_suggestions": ["list", "of", "suggestions"]
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a task execution analyst. Be thorough and strategic in your analysis."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            try:
                import json
                analysis = json.loads(response["content"] or "{}")
                return analysis
            except Exception as parse_exc:
                logger.warning(f"ActionExecutor | JSON parse error: {parse_exc}")
                return {"should_execute": True, "reasoning": "Fallback: proceeding with execution"}

        except Exception as e:
            logger.warning(f"ActionExecutor | LLM analysis failed: {e}")
            return {"should_execute": True, "reasoning": "LLM unavailable, proceeding with execution"}

    def _execute_news_dive(self, payload: Dict[str, Any], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute news dive with AI-enhanced analysis."""
        try:
            # AI-enhanced news analysis
            enhanced_payload = self._enhance_news_analysis(payload)
            
            # Store with AI insights
            rag_agent.store_research(enhanced_payload)
            
            return {
                "status": "executed", 
                "task": {"type": "news_dive", "payload": enhanced_payload},
                "ai_enhancements": execution_plan.get("optimization_suggestions", []),
                "execution_quality": "ai_enhanced"
            }
        except Exception as e:
            logger.error(f"News dive execution error: {e}")
            return {"status": "error", "task": payload, "error": str(e)}

    def _execute_trade_signal(self, payload: Dict[str, Any], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade signal with AI validation."""
        try:
            # AI-enhanced trade signal
            enhanced_payload = self._enhance_trade_signal(payload, execution_plan)
            
            # Execute trade
            res = trade_executor({**enhanced_payload, "source": "ai_enhanced_planner"})
            
            return {
                "status": "executed", 
                "trade_result": res,
                "ai_enhancements": execution_plan.get("optimization_suggestions", []),
                "execution_quality": "ai_enhanced"
            }
        except Exception as e:
            logger.error(f"Trade signal execution error: {e}")
            return {"status": "error", "task": payload, "error": str(e)}

    def _execute_custom_task(self, task: Dict[str, Any], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom tasks with AI guidance."""
        try:
            # AI-generated task execution
            custom_result = self._generate_custom_execution(task, execution_plan)
            
            return {
                "status": "executed",
                "task": task,
                "custom_result": custom_result,
                "ai_guidance": execution_plan.get("optimization_suggestions", []),
                "execution_quality": "ai_generated"
            }
        except Exception as e:
            logger.error(f"Custom task execution error: {e}")
            return {"status": "error", "task": task, "error": str(e)}

    def _enhance_news_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance news analysis."""
        try:
            headline = payload.get("headline", "")
            symbol = payload.get("symbol", "")
            
            prompt = f"""Analyze this news headline for trading implications:

Headline: {headline}
Symbol: {symbol}

Provide enhanced analysis in JSON format:
{{
    "sentiment_score": -1.0 to 1.0,
    "impact_magnitude": "high/medium/low",
    "time_horizon": "short/medium/long",
    "key_insights": ["list", "of", "insights"],
    "trading_implications": ["list", "of", "implications"],
    "risk_factors": ["list", "of", "risks"],
    "confidence": 0.0-1.0
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a financial news analyst. Be objective and thorough."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)

            try:
                import json
                analysis = json.loads(response["content"] or "{}")
                return {**payload, "ai_analysis": analysis}
            except Exception as parse_exc:
                logger.warning(f"News analysis enhancement failed: {parse_exc}")
                return payload

        except Exception as e:
            logger.warning(f"News analysis enhancement failed: {e}")
            return payload

    def _enhance_trade_signal(self, payload: Dict[str, Any], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance trade signal."""
        try:
            prompt = f"""Enhance this trade signal with additional analysis:

Original Signal: {payload}
Execution Plan: {execution_plan}

Provide enhanced signal in JSON format:
{{
    "enhanced_confidence": 0.0-1.0,
    "position_sizing": "recommended size",
    "entry_timing": "optimal timing",
    "stop_loss": "suggested stop loss",
    "take_profit": "suggested take profit",
    "risk_adjustments": ["list", "of", "adjustments"],
    "market_context": "current market conditions"
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a trade signal optimizer. Be conservative and thorough."},
                {"role": "user", "content": prompt}
            ], temperature=0.2)

            try:
                import json
                enhancement = json.loads(response["content"] or "{}")
                return {**payload, "ai_enhancement": enhancement}
            except Exception as parse_exc:
                logger.warning(f"Trade signal enhancement failed: {parse_exc}")
                return payload

        except Exception as e:
            logger.warning(f"Trade signal enhancement failed: {e}")
            return payload

    def _generate_custom_execution(self, task: Dict[str, Any], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom task execution using AI."""
        try:
            prompt = f"""Generate execution plan for this custom task:

Task: {task}
Execution Plan: {execution_plan}

Provide execution details in JSON format:
{{
    "execution_steps": ["step1", "step2", "step3"],
    "expected_outcome": "description",
    "success_metrics": ["metric1", "metric2"],
    "fallback_plan": "alternative approach",
    "completion_criteria": "success criteria"
}}"""

            response = openai_manager.chat_completion([
                {"role": "system", "content": "You are a task execution planner. Be practical and thorough."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            try:
                import json
                execution = json.loads(response["content"] or "{}")
                return execution
            except Exception as parse_exc:
                logger.warning(f"Custom execution generation failed: {parse_exc}")
                return {"status": "generated", "steps": ["basic_execution"]}

        except Exception as e:
            logger.warning(f"Custom execution generation failed: {e}")
            return {"status": "fallback", "steps": ["basic_execution"]} 