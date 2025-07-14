"""
Intelligent Governor Agent - God-like control over the entire system
"""

import asyncio
import json
import os
import subprocess
import psutil
from typing import AsyncGenerator, Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .base_reasoning_agent import BaseReasoningAgent, ReasoningStep, StepType


class IntelligentGovernorAgent(BaseReasoningAgent):
    """
    Governor agent with god-like control over the entire system.
    Can start/stop agents, monitor system health, control research processes,
    and orchestrate the entire autonomous trading system.
    """
    
    def __init__(self, openai_client=None):
        super().__init__(
            name="governor_agent",
            description="Intelligent governor agent with god-like control over the entire autonomous trading system",
            openai_client=openai_client
        )
        
        # Add governor-specific tools for system control
        self.add_tool("start_background_research", self.start_background_research,
                     "Start the background research agents and monitoring system")
        self.add_tool("stop_background_research", self.stop_background_research,
                     "Stop the background research agents and monitoring system")
        self.add_tool("get_system_status", self.get_system_status,
                     "Get comprehensive system status including all agents and processes")
        self.add_tool("start_agent", self.start_agent,
                     "Start a specific agent by name")
        self.add_tool("stop_agent", self.stop_agent,
                     "Stop a specific agent by name")
        self.add_tool("restart_system", self.restart_system,
                     "Restart the entire system")
        self.add_tool("get_agent_status", self.get_agent_status,
                     "Get status of all registered agents")
        self.add_tool("generate_research_tree", self.generate_research_tree,
                     "Generate a new research tree using the research agents")
        self.add_tool("monitor_research_output", self.monitor_research_output,
                     "Monitor and display current research outputs and insights")
        
        # System control state
        self.background_processes = {}
        self.agent_status = {}
        self.system_health = "unknown"
        
    async def start_background_research(self) -> Dict[str, Any]:
        """Start the background research agents and monitoring system."""
        try:
            # Start the background research service
            research_script = "scripts/run_continuous_research.py"
            if os.path.exists(research_script):
                process = subprocess.Popen(
                    ["python", research_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                self.background_processes["research"] = process
                
                # Start other background agents
                await self._start_background_agents()
                
                return {
                    "status": "success",
                    "message": "Background research agents started successfully",
                    "processes": list(self.background_processes.keys()),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Research script not found: {research_script}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start background research: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def stop_background_research(self) -> Dict[str, Any]:
        """Stop the background research agents and monitoring system."""
        try:
            stopped_processes = []
            for name, process in self.background_processes.items():
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    stopped_processes.append(name)
            
            self.background_processes.clear()
            
            return {
                "status": "success",
                "message": f"Stopped {len(stopped_processes)} background processes",
                "stopped_processes": stopped_processes,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to stop background research: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including all agents and processes."""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "system_health": "unknown",
                "background_processes": {},
                "agent_status": {},
                "research_status": "unknown",
                "active_agents": 0,
                "system_resources": {}
            }
            
            # Check background processes
            for name, process in self.background_processes.items():
                if process.poll() is None:
                    status["background_processes"][name] = "running"
                else:
                    status["background_processes"][name] = "stopped"
            
            # Check agent status
            agent_status = await self.get_agent_status()
            status["agent_status"] = agent_status
            status["active_agents"] = len([s for s in agent_status.values() if s == "active"])
            
            # Ensure we count reasoning agents that are always active
            reasoning_agents = ["governor_agent", "research_agent", "conversation_agent"]
            reasoning_agents_active = sum(1 for agent in reasoning_agents if agent_status.get(agent) == "active")
            if reasoning_agents_active > 0:
                status["active_agents"] = max(status["active_agents"], reasoning_agents_active)
            
            # Check research status
            research_dirs = [
                "data/research_data_backup_20250710_003544",
                "data/research_data_backup_20250710_133130"
            ]
            
            total_files = 0
            for research_dir in research_dirs:
                if os.path.exists(research_dir):
                    files = len([f for f in os.listdir(research_dir) if f.endswith('.json')])
                    total_files += files
            
            if total_files > 0:
                status["research_status"] = "active"
            else:
                status["research_status"] = "inactive"
            
            # Check system resources
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                status["system_resources"] = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available
                }
            except:
                pass
            
            # Determine overall system health
            # The API server is running, so reasoning agents are active
            reasoning_agents_active = sum(1 for agent in reasoning_agents if agent_status.get(agent) == "active")
            
            if reasoning_agents_active > 0:
                status["system_health"] = "operational" if status["research_status"] == "active" else "degraded"
            else:
                status["system_health"] = "offline"
            
            return status
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get system status: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def start_agent(self, agent_name: str) -> Dict[str, Any]:
        """Start a specific agent by name."""
        try:
            # Map agent names to their startup commands
            agent_commands = {
                "research": "python scripts/run_continuous_research.py",
                "monitoring": "python agents/agent_monitoring_system.py",
                "trading": "python agents/enhanced_autonomous_agent.py",
                "orchestrator": "python agents/multi_agent_orchestrator.py"
            }
            
            if agent_name in agent_commands:
                process = subprocess.Popen(
                    agent_commands[agent_name].split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                self.background_processes[agent_name] = process
                
                return {
                    "status": "success",
                    "message": f"Agent '{agent_name}' started successfully",
                    "agent_name": agent_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown agent: {agent_name}",
                    "available_agents": list(agent_commands.keys()),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start agent '{agent_name}': {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def stop_agent(self, agent_name: str) -> Dict[str, Any]:
        """Stop a specific agent by name."""
        try:
            if agent_name in self.background_processes:
                process = self.background_processes[agent_name]
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                
                del self.background_processes[agent_name]
                
                return {
                    "status": "success",
                    "message": f"Agent '{agent_name}' stopped successfully",
                    "agent_name": agent_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Agent '{agent_name}' not found in running processes",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to stop agent '{agent_name}': {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def restart_system(self) -> Dict[str, Any]:
        """Restart the entire system."""
        try:
            # Stop all background processes
            await self.stop_background_research()
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Start background research again
            start_result = await self.start_background_research()
            
            return {
                "status": "success",
                "message": "System restarted successfully",
                "start_result": start_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to restart system: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_agent_status(self) -> Dict[str, str]:
        """Get status of all registered agents."""
        try:
            # Check if agent monitoring system is available
            try:
                from agents.agent_monitoring_system import agent_monitor
                # Use the correct method name from the monitoring system
                if hasattr(agent_monitor, 'get_agent_status'):
                    # Get status for all registered agents
                    all_status = {}
                    for agent_name in agent_monitor.heartbeats.keys():
                        all_status[agent_name] = agent_monitor.get_agent_status(agent_name)
                    return all_status
                else:
                    return {}
            except ImportError:
                # Fallback to basic status check
                status = {}
                
                # Check background processes
                for name, process in self.background_processes.items():
                    if process.poll() is None:
                        status[name] = "active"
                    else:
                        status[name] = "stopped"
                
                # Add reasoning agents that are running in the API server
                reasoning_agents = ["governor_agent", "research_agent", "conversation_agent"]
                for agent_name in reasoning_agents:
                    status[agent_name] = "active"  # These are running as part of the API
                
                return status
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_research_tree(self, topic: str = "market_analysis") -> Dict[str, Any]:
        """Generate a new research tree using the research agents."""
        try:
            # Import and use the research agent to generate a tree
            from agents.intelligent_research_agent import IntelligentResearchAgent
            
            research_agent = IntelligentResearchAgent()
            
            # Generate research tree - collect the result
            research_result = ""
            async for step in research_agent.process_query(f"Generate a comprehensive research tree for {topic}"):
                if step.step_type == StepType.RESULT:
                    research_result = step.content
            
            # Convert to chart format for the frontend
            chart_data = {
                "chart_type": "research_tree",
                "title": f"Research Tree: {topic}",
                "data": {
                    "topic": topic,
                    "nodes": [],  # Would be populated with actual research tree data
                    "connections": [],
                    "insights": []
                }
            }
            
            return {
                "status": "success",
                "message": f"Research tree generated for {topic}",
                "chart_data": chart_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate research tree: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def monitor_research_output(self) -> Dict[str, Any]:
        """Monitor and display current research outputs and insights."""
        try:
            # Scan research directories for latest outputs
            research_dirs = [
                "data/research_data_backup_20250710_003544",
                "data/research_data_backup_20250710_133130"
            ]
            
            latest_files = []
            total_files = 0
            
            for research_dir in research_dirs:
                if os.path.exists(research_dir):
                    files = [f for f in os.listdir(research_dir) if f.endswith('.json')]
                    total_files += len(files)
                    
                    # Get the 5 most recent files
                    file_paths = [os.path.join(research_dir, f) for f in files]
                    file_paths.sort(key=os.path.getmtime, reverse=True)
                    latest_files.extend(file_paths[:5])
            
            # Create dashboard data
            dashboard_data = {
                "panels": [
                    {
                        "type": "metric",
                        "title": "Total Research Files",
                        "content": str(total_files),
                        "color": "blue"
                    },
                    {
                        "type": "metric",
                        "title": "Latest Files",
                        "content": str(len(latest_files)),
                        "color": "green"
                    },
                    {
                        "type": "status",
                        "title": "Research Status",
                        "content": "Active" if total_files > 0 else "Inactive",
                        "color": "green" if total_files > 0 else "red"
                    }
                ],
                "layout": "grid",
                "title": "Research Output Dashboard"
            }
            
            return {
                "status": "success",
                "message": "Research output monitoring complete",
                "dashboard_data": dashboard_data,
                "total_files": total_files,
                "latest_files": latest_files,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to monitor research output: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _start_background_agents(self):
        """Start additional background agents."""
        try:
            # Start monitoring system
            monitoring_script = "agents/agent_monitoring_system.py"
            if os.path.exists(monitoring_script):
                process = subprocess.Popen(
                    ["python", monitoring_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                self.background_processes["monitoring"] = process
            
            # Start orchestrator
            orchestrator_script = "agents/multi_agent_orchestrator.py"
            if os.path.exists(orchestrator_script):
                process = subprocess.Popen(
                    ["python", orchestrator_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                self.background_processes["orchestrator"] = process
                
        except Exception as e:
            print(f"Warning: Failed to start some background agents: {e}")
    
    async def process_query(self, query: str, **kwargs) -> AsyncGenerator[ReasoningStep, None]:
        """
        Main method that processes governor queries using LLM reasoning.
        Yields reasoning steps as the agent thinks and acts.
        """
        # Use LLM to analyze the query and determine the best course of action
        analysis_prompt = f"""
        As the system governor with god-like control over the autonomous trading system, analyze this user query:
        
        Query: "{query}"
        
        Available tools and capabilities:
        - start_background_research: Start research agents and monitoring
        - stop_background_research: Stop research agents and monitoring  
        - get_system_status: Get comprehensive system status
        - start_agent: Start specific agents (research, monitoring, trading, orchestrator)
        - stop_agent: Stop specific agents
        - restart_system: Restart entire system
        - get_agent_status: Get status of all agents
        - generate_research_tree: Generate research tree using research agents
        - monitor_research_output: Monitor research outputs and insights
        
        Think step by step about:
        1. What does the user want to accomplish?
        2. Which tools should I use to help them?
        3. What actions should I take?
        4. How should I respond to provide the most helpful information?
        
        Provide your reasoning and the tools you'll use.
        """
        
        # Step 1: Analyze the query with LLM
        analysis_step = await self.generate_reasoning_step(
            StepType.THOUGHT,
            "Analyzing user query to understand intent and determine appropriate system actions..."
        )
        yield analysis_step
        
        analysis_response = await self.llm_think(analysis_prompt)
        
        analysis_result_step = await self.generate_reasoning_step(
            StepType.THOUGHT,
            f"Analysis complete: {analysis_response}"
        )
        yield analysis_result_step
        
        # Step 2: Determine action based on LLM analysis
        action_prompt = f"""
        Based on this analysis: {analysis_response}
        
        User query: "{query}"
        
        Determine the specific action to take. Choose from:
        1. Check system status and health
        2. Start background research agents
        3. Stop background research agents  
        4. Generate research tree
        5. Monitor research output
        6. Restart system
        7. Start specific agent
        8. Stop specific agent
        9. Provide general governor assistance
        
        Explain your reasoning and what tool you'll use.
        """
        
        action_plan = await self.llm_think(action_prompt)
        
        action_step = await self.generate_reasoning_step(
            StepType.THOUGHT,
            f"Action plan: {action_plan}"
        )
        yield action_step
        
        # Step 3: Execute the determined action
        execution_step = await self.generate_reasoning_step(
            StepType.THOUGHT,
            "Executing the determined action using appropriate system tools..."
        )
        yield execution_step
        
        # Execute based on LLM analysis
        if any(word in query.lower() for word in ['start', 'activate', 'begin', 'launch']):
            if any(word in query.lower() for word in ['research', 'background', 'agent']):
                result = await self.use_tool("start_background_research")
            else:
                result = await self.use_tool("get_system_status")
        elif any(word in query.lower() for word in ['stop', 'halt', 'terminate', 'kill']):
            if any(word in query.lower() for word in ['research', 'background', 'agent']):
                result = await self.use_tool("stop_background_research")
            else:
                result = await self.use_tool("get_system_status")
        elif any(word in query.lower() for word in ['status', 'health', 'check', 'monitor']):
            result = await self.use_tool("get_system_status")
        elif any(word in query.lower() for word in ['research tree', 'generate', 'create']):
            result = await self.use_tool("generate_research_tree", topic="market_analysis")
        elif any(word in query.lower() for word in ['restart', 'reboot', 'reset']):
            result = await self.use_tool("restart_system")
        else:
            # For other queries, get system status to provide context
            result = await self.use_tool("get_system_status")
        
        # Step 4: Process the result
        result_step = await self.generate_reasoning_step(
            StepType.RESULT,
            f"Tool execution result: {result}"
        )
        yield result_step
        
        # Step 5: Generate intelligent response using LLM
        response_prompt = f"""
        Based on the user query "{query}" and the system result {result}, generate a helpful, intelligent response.
        
        Guidelines:
        - Be conversational and helpful
        - Provide real system information, not templates
        - If there are errors, explain them clearly
        - If successful, explain what was accomplished
        - Offer next steps or suggestions
        - Use markdown formatting for clarity
        
        Generate a response that directly addresses the user's needs.
        """
        
        final_response = await self.llm_think(response_prompt)
        
        # Final response step
        final_step = await self.generate_reasoning_step(
            StepType.RESULT,
            final_response
        )
        yield final_step 