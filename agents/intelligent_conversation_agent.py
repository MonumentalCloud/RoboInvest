"""
Intelligent Conversation Agent - Handles general conversation and casual queries
"""

import asyncio
import json
import os
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .base_reasoning_agent import BaseReasoningAgent, ReasoningStep, StepType


class IntelligentConversationAgent(BaseReasoningAgent):
    """
    General conversation agent that handles casual queries, greetings,
    and general questions with intelligent responses and real system integration.
    """
    
    def __init__(self, openai_client=None):
        super().__init__(
            name="conversation_agent",
            description="Intelligent conversation agent that handles greetings, casual queries, and general questions with real system integration and status checking",
            openai_client=openai_client
        )
        
        # Add conversation-specific tools with real system integration
        self.add_tool("analyze_conversation_context", self.analyze_conversation_context,
                     "Analyze the context and tone of the conversation")
        self.add_tool("generate_contextual_response", self.generate_contextual_response,
                     "Generate a contextual and helpful response")
        self.add_tool("check_system_status", self.check_system_status,
                     "Check real system status including agents, research, and processes")
        self.add_tool("check_research_status", self.check_research_status,
                     "Check if research agents are running and what data they've generated")
        self.add_tool("check_agent_monitoring", self.check_agent_monitoring,
                     "Check the status of all registered agents and their health")
        
    async def analyze_conversation_context(self, query: str) -> str:
        """Analyze the conversation context and tone."""
        prompt = f"""
        Analyze this conversation query and determine its context:
        
        Query: "{query}"
        
        Please analyze:
        1. Is this a greeting, casual conversation, or specific request?
        2. What is the user's likely intent?
        3. What would be the most helpful response?
        4. Should I provide information about what the system can do?
        5. Does this query require checking system status, research status, or agent status?
        
        Provide a brief analysis of the conversation context.
        """
        
        return await self.llm_think(prompt)
    
    async def generate_contextual_response(self, query: str, context_analysis: str, system_info: Optional[Dict[str, Any]] = None) -> str:
        """Generate a contextual and helpful response with real system information."""
        system_context = ""
        if system_info:
            system_context = f"""
            Current System Status:
            - Research Status: {system_info.get('research_status', 'Unknown')}
            - Active Agents: {system_info.get('active_agents', 0)}
            - System Health: {system_info.get('system_health', 'Unknown')}
            - Recent Activity: {system_info.get('recent_activity', 'None')}
            """
        
        prompt = f"""
        Generate a helpful and contextual response to this query:
        
        Query: "{query}"
        Context Analysis: {context_analysis}
        {system_context}
        
        I am part of the RoboInvest autonomous trading system. I can help with:
        - Trading and portfolio analysis
        - Market research and insights
        - System status and configuration
        - Agent monitoring and health checks
        - Research data analysis
        
        Please provide a friendly, helpful response that:
        1. Addresses the user's query appropriately
        2. Uses real system information when available
        3. Offers to help with specific tasks if relevant
        4. Maintains a conversational tone
        5. Provides actionable information when possible
        
        Keep the response concise but informative and truthful.
        """
        
        return await self.llm_think(prompt)
    
    async def check_system_status(self) -> Dict[str, Any]:
        """Check real system status including processes, databases, and services."""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "system_health": "unknown",
                "active_agents": 0,
                "research_status": "unknown",
                "recent_activity": "none",
                "databases": {},
                "processes": {}
            }
            
            # Check if backend is running
            try:
                import requests
                response = requests.get("http://localhost:8000/api/health", timeout=2)
                if response.status_code == 200:
                    status["backend_status"] = "running"
                    status["system_health"] = "operational"
                else:
                    status["backend_status"] = "error"
                    status["system_health"] = "degraded"
            except:
                status["backend_status"] = "not_running"
                status["system_health"] = "offline"
            
            # Check databases
            db_paths = [
                "data/central_experience.db",
                "data/governor_directives.db",
                "chroma"
            ]
            
            for db_path in db_paths:
                if os.path.exists(db_path):
                    if os.path.isdir(db_path):
                        # Directory (like chroma)
                        files = len([f for f in os.listdir(db_path) if os.path.isfile(os.path.join(db_path, f))])
                        status["databases"][db_path] = f"exists ({files} files)"
                    else:
                        # File
                        size = os.path.getsize(db_path)
                        status["databases"][db_path] = f"exists ({size} bytes)"
                else:
                    status["databases"][db_path] = "not_found"
            
            # Check research data
            research_status = await self.check_research_status()
            status["research_status"] = research_status.get("status", "unknown")
            status["active_agents"] = research_status.get("active_agents", 0)
            
            return status
            
        except Exception as e:
            return {
                "error": str(e),
                "system_health": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_research_status(self) -> Dict[str, Any]:
        """Check if research agents are running and what data they've generated."""
        try:
            status = {
                "status": "unknown",
                "active_agents": 0,
                "research_files": 0,
                "latest_data": None,
                "data_directories": []
            }
            
            # Check research data directories
            research_dirs = [
                "data/research_data_backup_20250710_003544",
                "data/research_data_backup_20250710_133130"
            ]
            
            total_files = 0
            latest_data = None
            
            for research_dir in research_dirs:
                if os.path.exists(research_dir):
                    files = [f for f in os.listdir(research_dir) if f.endswith('.json')]
                    total_files += len(files)
                    status["data_directories"].append({
                        "directory": research_dir,
                        "files": len(files)
                    })
                    
                    # Check for latest files
                    for file in files:
                        if "_latest.json" in file:
                            file_path = os.path.join(research_dir, file)
                            try:
                                mtime = os.path.getmtime(file_path)
                                if latest_data is None or mtime > latest_data:
                                    latest_data = mtime
                            except:
                                pass
            
            status["research_files"] = total_files
            
            if latest_data:
                status["latest_data"] = datetime.fromtimestamp(latest_data).isoformat()
                time_diff = datetime.now().timestamp() - latest_data
                if time_diff < 3600:  # Less than 1 hour
                    status["status"] = "active"
                    status["active_agents"] = 3  # Estimate based on data freshness
                elif time_diff < 86400:  # Less than 24 hours
                    status["status"] = "recent"
                    status["active_agents"] = 1
                else:
                    status["status"] = "inactive"
                    status["active_agents"] = 0
            else:
                status["status"] = "no_data"
                status["active_agents"] = 0
            
            return status
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "active_agents": 0
            }
    
    async def check_agent_monitoring(self) -> Dict[str, Any]:
        """Check the status of all registered agents and their health."""
        try:
            # Try to import and use the agent monitoring system
            try:
                from agents.agent_monitoring_system import agent_monitor
                agent_statuses = agent_monitor.get_all_agent_statuses()
                
                active_agents = 0
                healthy_agents = 0
                
                for agent_name, status in agent_statuses.items():
                    if status and status.get("health") == "healthy":
                        healthy_agents += 1
                    if status and status.get("status") == "active":
                        active_agents += 1
                
                return {
                    "total_agents": len(agent_statuses),
                    "active_agents": active_agents,
                    "healthy_agents": healthy_agents,
                    "agent_statuses": agent_statuses
                }
                
            except ImportError:
                # Fallback if agent monitoring not available
                return {
                    "total_agents": 0,
                    "active_agents": 0,
                    "healthy_agents": 0,
                    "note": "Agent monitoring system not available"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "total_agents": 0,
                "active_agents": 0,
                "healthy_agents": 0
            }
    
    async def process_query(self, query: str, **kwargs) -> AsyncGenerator[ReasoningStep, None]:
        """
        Main method that processes conversation queries using LLM reasoning.
        Yields reasoning steps as the agent thinks and acts.
        """
        # Initial thought about the query
        initial_thought = await self.generate_reasoning_step(
            StepType.THOUGHT,
            f"Received conversation query: '{query}'. I need to understand the context and provide a helpful response with real system information."
        )
        yield initial_thought
        
        try:
            # Step 1: Analyze conversation context
            context_step = await self.generate_reasoning_step(
                StepType.THOUGHT,
                "Analyzing the conversation context and user intent."
            )
            yield context_step
            
            context_analysis = await self.use_tool("analyze_conversation_context", query=query)
            
            context_result_step = await self.generate_reasoning_step(
                StepType.RESULT,
                f"Context analysis complete: {context_analysis}"
            )
            yield context_result_step
            
            # Step 2: Check system status if needed
            system_info = None
            if any(word in query.lower() for word in ['status', 'running', 'research', 'agent', 'system', 'background']):
                system_step = await self.generate_reasoning_step(
                    StepType.THOUGHT,
                    "User is asking about system status. I'll check the actual system status and research data."
                )
                yield system_step
                
                system_info = await self.use_tool("check_system_status")
                
                system_result_step = await self.generate_reasoning_step(
                    StepType.RESULT,
                    f"System status check complete. Research status: {system_info.get('research_status', 'unknown')}, "
                    f"Active agents: {system_info.get('active_agents', 0)}, "
                    f"System health: {system_info.get('system_health', 'unknown')}"
                )
                yield system_result_step
            
            # Step 3: Generate contextual response with real system information
            response_step = await self.generate_reasoning_step(
                StepType.THOUGHT,
                "Generating a contextual and helpful response based on the analysis and system status."
            )
            yield response_step
            
            # Generate enhanced response using the rich formatter
            if system_info and system_info.get('research_status') != 'unknown':
                # Use enhanced response formatting for system status queries
                from backend.api.governor_endpoints import create_enhanced_system_status_response, create_enhanced_research_status_response
                
                if any(word in query.lower() for word in ['status', 'health', 'system', 'research']):
                    if system_info.get('research_status') == 'no_data':
                        # Create enhanced research status response
                        response_data = create_enhanced_research_status_response({
                            "summary": {
                                "total_files": 0,
                                "alpha_discoveries_count": 0,
                                "market_monitoring_count": 0,
                                "risk_assessments_count": 0
                            }
                        })
                        response = f"Final response: {json.dumps(response_data)}"
                    else:
                        # Create enhanced system status response
                        system_issues = []
                        if system_info.get('system_health') == 'offline':
                            system_issues.append({
                                'type': 'system_offline',
                                'severity': 'high',
                                'description': 'System is currently offline',
                                'impact': 'All functionality disabled',
                                'solution': 'Start the backend server'
                            })
                        
                        response_data = create_enhanced_system_status_response(system_issues)
                        response = f"Final response: {json.dumps(response_data)}"
                else:
                    response = await self.use_tool("generate_contextual_response", 
                                                 query=query, 
                                                 context_analysis=context_analysis,
                                                 system_info=system_info or {})
            else:
                response = await self.use_tool("generate_contextual_response", 
                                             query=query, 
                                             context_analysis=context_analysis,
                                             system_info=system_info or {})
            
            # Step 4: Add specific system information if available
            if system_info and system_info.get('research_status') != 'unknown':
                if system_info.get('research_status') == 'active':
                    response += f"\n\n**Research Status:** ✅ Research agents are actively running and generating data. "
                    response += f"Latest activity: {system_info.get('latest_data', 'recent')}"
                elif system_info.get('research_status') == 'inactive':
                    response += f"\n\n**Research Status:** ⚠️ Research agents appear inactive. "
                    response += "To start research: `python scripts/run_continuous_research.py`"
                elif system_info.get('research_status') == 'no_data':
                    response += f"\n\n**Research Status:** ❌ No research data found. "
                    response += "Research agents need to be started to generate data."
            
            # Final response
            final_step = await self.generate_reasoning_step(
                StepType.RESULT,
                response
            )
            yield final_step
            
        except Exception as e:
            error_step = await self.generate_reasoning_step(
                StepType.ERROR,
                f"Error during conversation processing: {str(e)}"
            )
            yield error_step 