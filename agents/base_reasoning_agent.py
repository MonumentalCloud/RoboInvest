"""
Base Reasoning Agent - LangGraph-style LLM reasoning with streaming consciousness
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncGenerator, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import openai
from openai import AsyncOpenAI


class StepType(Enum):
    THOUGHT = "thought"
    TOOL_USE = "tool_use"
    AGENT_CALL = "agent_call"
    REFLECTION = "reflection"
    DECISION = "decision"
    RESULT = "result"
    ERROR = "error"


@dataclass
class ReasoningStep:
    step_type: StepType
    content: str
    timestamp: float
    step_id: str
    parent_step_id: Optional[str] = None
    tool_used: Optional[str] = None
    tool_input: Optional[Dict] = None
    tool_output: Optional[Any] = None
    agent_called: Optional[str] = None
    confidence: Optional[float] = None
    next_action: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class BaseReasoningAgent(ABC):
    """
    Base class for all reasoning agents that use LLM-based decision making
    and streaming consciousness.
    """
    
    def __init__(self, name: str, description: str, openai_client: Optional[AsyncOpenAI] = None):
        self.name = name
        self.description = description
        self.openai_client = openai_client or AsyncOpenAI()
        self.available_tools: Dict[str, Callable] = {}
        self.available_agents: Dict[str, 'BaseReasoningAgent'] = {}
        self.reasoning_chain: List[ReasoningStep] = []
        self.context: Dict[str, Any] = {}
        
    def add_tool(self, name: str, tool_func: Callable, description: str):
        """Add a tool that this agent can use."""
        self.available_tools[name] = tool_func
        self.context[f"tool_{name}"] = description
        
    def add_agent(self, name: str, agent: 'BaseReasoningAgent'):
        """Add another agent that this agent can call."""
        self.available_agents[name] = agent
        self.context[f"agent_{name}"] = agent.description
        
    async def generate_reasoning_step(self, 
                                    step_type: StepType, 
                                    content: str, 
                                    parent_step_id: Optional[str] = None,
                                    **kwargs) -> ReasoningStep:
        """Generate a reasoning step with unique ID."""
        step = ReasoningStep(
            step_type=step_type,
            content=content,
            timestamp=time.time(),
            step_id=f"{self.name}_{len(self.reasoning_chain)}_{int(time.time() * 1000)}",
            parent_step_id=parent_step_id,
            **kwargs
        )
        self.reasoning_chain.append(step)
        return step
        
    async def llm_think(self, 
                       prompt: str, 
                       context: Optional[Dict] = None,
                       system_prompt: Optional[str] = None) -> str:
        """Use LLM to generate reasoning or decisions."""
        full_context = {**self.context, **(context or {})}
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context about available tools and agents
        if self.available_tools:
            tools_desc = "\n".join([f"- {name}: {self.context.get(f'tool_{name}', 'No description')}" 
                                  for name in self.available_tools.keys()])
            messages.append({"role": "system", "content": f"Available tools:\n{tools_desc}"})
            
        if self.available_agents:
            agents_desc = "\n".join([f"- {name}: {self.context.get(f'agent_{name}', 'No description')}" 
                                   for name in self.available_agents.keys()])
            messages.append({"role": "system", "content": f"Available agents:\n{agents_desc}"})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content or "No response generated"
        except Exception as e:
            return f"LLM reasoning failed: {str(e)}"
    
    async def decide_next_action(self, 
                               current_situation: str, 
                               available_options: List[str]) -> str:
        """Use LLM to decide what to do next."""
        prompt = f"""
        Current situation: {current_situation}
        
        Available options:
        {chr(10).join([f"{i+1}. {option}" for i, option in enumerate(available_options)])}
        
        Based on the current situation and available options, what should I do next?
        Respond with just the number of the option you choose and a brief explanation.
        """
        
        decision = await self.llm_think(prompt)
        return decision
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a tool and record the reasoning step."""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
            
        step = await self.generate_reasoning_step(
            StepType.TOOL_USE,
            f"Using tool '{tool_name}' with parameters: {kwargs}",
            tool_used=tool_name,
            tool_input=kwargs
        )
        
        try:
            result = await self.available_tools[tool_name](**kwargs)
            step.tool_output = result
            step.content += f"\nResult: {result}"
            return result
        except Exception as e:
            step.step_type = StepType.ERROR
            step.content += f"\nError: {str(e)}"
            raise
    
    async def call_agent(self, agent_name: str, message: str, **kwargs) -> Any:
        """Call another agent and record the reasoning step."""
        if agent_name not in self.available_agents:
            raise ValueError(f"Agent '{agent_name}' not available")
            
        step = await self.generate_reasoning_step(
            StepType.AGENT_CALL,
            f"Calling agent '{agent_name}' with message: {message}",
            agent_called=agent_name,
            tool_input={"message": message, **kwargs}
        )
        
        try:
            agent = self.available_agents[agent_name]
            result = await agent.process_query(message, **kwargs)
            step.tool_output = result
            step.content += f"\nAgent response: {result}"
            return result
        except Exception as e:
            step.step_type = StepType.ERROR
            step.content += f"\nError: {str(e)}"
            raise
    
    async def reflect_on_progress(self, current_goal: str) -> str:
        """Use LLM to reflect on current progress and decide next steps."""
        prompt = f"""
        Current goal: {current_goal}
        
        Reasoning chain so far:
        {chr(10).join([f"- {step.step_type.value}: {step.content}" for step in self.reasoning_chain[-5:]])}
        
        Based on this progress, what should I do next? Should I:
        1. Continue with current approach
        2. Try a different approach
        3. Ask for help from another agent
        4. Consider the goal achieved
        
        Explain your reasoning.
        """
        
        reflection = await self.llm_think(prompt)
        await self.generate_reasoning_step(
            StepType.REFLECTION,
            reflection
        )
        return reflection
    
    @abstractmethod
    async def process_query(self, query: str, **kwargs) -> AsyncGenerator[ReasoningStep, None]:
        """
        Main method that processes a query using LLM reasoning.
        Should yield ReasoningStep objects as the agent thinks and acts.
        """
        pass
    
    async def get_reasoning_chain(self) -> List[ReasoningStep]:
        """Get the complete reasoning chain for this agent."""
        return self.reasoning_chain.copy()
    
    async def clear_reasoning_chain(self):
        """Clear the reasoning chain (useful for new conversations)."""
        self.reasoning_chain = [] 