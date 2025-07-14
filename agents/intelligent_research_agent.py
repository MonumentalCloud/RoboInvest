"""
Intelligent Research Agent - Uses LLM reasoning to analyze research data and provide insights
"""

import asyncio
import json
import os
import glob
from typing import AsyncGenerator, Dict, List, Any
from datetime import datetime

from .base_reasoning_agent import BaseReasoningAgent, ReasoningStep, StepType


class IntelligentResearchAgent(BaseReasoningAgent):
    """
    Research agent that uses LLM reasoning to analyze research data,
    generate insights, and provide streaming consciousness about the research process.
    """
    
    def __init__(self, openai_client=None):
        super().__init__(
            name="research_agent",
            description="Intelligent research agent that analyzes market data, generates insights, and provides streaming reasoning about research findings",
            openai_client=openai_client
        )
        
        # Add research-specific tools
        self.add_tool("scan_research_directories", self.scan_research_directories, 
                     "Scan all research data directories for available files")
        self.add_tool("load_research_file", self.load_research_file,
                     "Load and parse a specific research JSON file")
        self.add_tool("analyze_research_data", self.analyze_research_data,
                     "Use LLM to analyze research data and extract insights")
        self.add_tool("generate_research_summary", self.generate_research_summary,
                     "Generate a comprehensive summary of research findings")
        self.add_tool("identify_research_gaps", self.identify_research_gaps,
                     "Identify gaps in current research and suggest next steps")
        
    async def scan_research_directories(self) -> Dict[str, Any]:
        """Scan all research directories for available data files."""
        research_dirs = []
        research_files = []
        
        # Find all research directories
        for root, dirs, files in os.walk("data"):
            for dir_name in dirs:
                if "research" in dir_name.lower():
                    research_dirs.append(os.path.join(root, dir_name))
        
        # Find all research files
        for research_dir in research_dirs:
            json_files = glob.glob(os.path.join(research_dir, "*.json"))
            for file_path in json_files:
                file_info = {
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                research_files.append(file_info)
        
        return {
            "directories": research_dirs,
            "files": research_files,
            "total_files": len(research_files)
        }
    
    async def load_research_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse a research JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return {
                "success": True,
                "data": data,
                "file_path": file_path,
                "data_type": data.get("type", "unknown"),
                "timestamp": data.get("timestamp", "unknown")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def analyze_research_data(self, data: Dict[str, Any], data_type: str) -> str:
        """Use LLM to analyze research data and extract insights."""
        prompt = f"""
        Analyze this {data_type} research data and provide insights:
        
        Data: {json.dumps(data, indent=2)}
        
        Please provide:
        1. Key findings and insights
        2. Market trends identified
        3. Potential opportunities or risks
        4. Recommendations for further research
        
        Be specific and actionable in your analysis.
        """
        
        return await self.llm_think(prompt)
    
    async def generate_research_summary(self, all_data: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive summary of all research findings."""
        prompt = f"""
        Generate a comprehensive research summary based on this data:
        
        {json.dumps(all_data, indent=2)}
        
        Provide:
        1. Executive summary of key findings
        2. Market overview and trends
        3. Risk assessment
        4. Investment opportunities
        5. Recommendations for next steps
        
        Make this summary actionable and insightful for trading decisions.
        """
        
        return await self.llm_think(prompt)
    
    async def identify_research_gaps(self, available_data: Dict[str, Any]) -> str:
        """Identify gaps in current research and suggest next steps."""
        prompt = f"""
        Based on the available research data, identify gaps and suggest next steps:
        
        Available data: {json.dumps(available_data, indent=2)}
        
        Please identify:
        1. What research is missing or incomplete
        2. What additional data would be valuable
        3. Specific research tasks that should be prioritized
        4. Timeline for completing missing research
        
        Be specific about what research agents should focus on next.
        """
        
        return await self.llm_think(prompt)
    
    async def process_query(self, query: str, **kwargs) -> AsyncGenerator[ReasoningStep, None]:
        """
        Main method that processes research queries using LLM reasoning.
        Yields reasoning steps as the agent thinks and acts.
        """
        # Initial thought about the query
        initial_thought = await self.generate_reasoning_step(
            StepType.THOUGHT,
            f"Received research query: '{query}'. I need to understand what research data is available and analyze it to provide insights."
        )
        yield initial_thought
        
        # Step 1: Scan for available research data
        scan_step = await self.generate_reasoning_step(
            StepType.THOUGHT,
            "First, I'll scan all research directories to see what data is available."
        )
        yield scan_step
        
        try:
            research_scan = await self.use_tool("scan_research_directories")
            scan_result_step = await self.generate_reasoning_step(
                StepType.RESULT,
                f"Found {research_scan['total_files']} research files in {len(research_scan['directories'])} directories."
            )
            yield scan_result_step
            
            # Step 2: Decide what to do based on available data
            if research_scan['total_files'] == 0:
                # No research data available
                no_data_step = await self.generate_reasoning_step(
                    StepType.THOUGHT,
                    "No research data found. I should explain this and suggest how to generate research data."
                )
                yield no_data_step
                
                suggestion = await self.llm_think(
                    "The user asked about research progress but no research data files were found. "
                    "Provide a helpful response explaining this and suggesting how to generate research data."
                )
                
                final_step = await self.generate_reasoning_step(
                    StepType.RESULT,
                    suggestion
                )
                yield final_step
                
            else:
                # Research data available - analyze it
                analysis_step = await self.generate_reasoning_step(
                    StepType.THOUGHT,
                    f"Found research data. I'll analyze the most recent and relevant files to provide insights."
                )
                yield analysis_step
                
                # Load and analyze recent files
                recent_files = sorted(research_scan['files'], 
                                    key=lambda x: x['modified'], 
                                    reverse=True)[:5]
                
                all_analyzed_data = []
                
                for file_info in recent_files:
                    load_step = await self.generate_reasoning_step(
                        StepType.THOUGHT,
                        f"Loading and analyzing file: {file_info['name']}"
                    )
                    yield load_step
                    
                    file_data = await self.use_tool("load_research_file", file_path=file_info['path'])
                    
                    if file_data['success']:
                        analysis = await self.use_tool(
                            "analyze_research_data", 
                            data=file_data['data'],
                            data_type=file_data['data_type']
                        )
                        
                        all_analyzed_data.append({
                            "file": file_info['name'],
                            "type": file_data['data_type'],
                            "analysis": analysis
                        })
                        
                        analysis_result_step = await self.generate_reasoning_step(
                            StepType.RESULT,
                            f"Completed analysis of {file_info['name']}: {analysis[:200]}..."
                        )
                        yield analysis_result_step
                
                # Generate comprehensive summary
                summary_step = await self.generate_reasoning_step(
                    StepType.THOUGHT,
                    "Now I'll generate a comprehensive summary of all research findings."
                )
                yield summary_step
                
                summary = await self.use_tool("generate_research_summary", all_data=all_analyzed_data)
                
                # Identify research gaps
                gaps_step = await self.generate_reasoning_step(
                    StepType.THOUGHT,
                    "Identifying research gaps and suggesting next steps."
                )
                yield gaps_step
                
                gaps_analysis = await self.use_tool("identify_research_gaps", available_data=research_scan)
                
                # Generate intelligent final response using LLM
                final_response_prompt = f"""
                Based on the research analysis, generate a comprehensive and intelligent response.
                
                Research Data Summary:
                - Total files found: {research_scan['total_files']}
                - Directories scanned: {len(research_scan['directories'])}
                - Recent files analyzed: {len(recent_files)}
                
                Analysis Results:
                {summary}
                
                Research Gaps:
                {gaps_analysis}
                
                User Query: "{query}"
                
                Generate a helpful, intelligent response that:
                1. Directly addresses the user's query
                2. Provides actionable insights from the research data
                3. Explains the current state of research progress
                4. Offers specific recommendations for next steps
                5. Uses markdown formatting for clarity
                
                Be conversational and provide real value, not template responses.
                """
                
                final_response = await self.llm_think(final_response_prompt)
                
                final_step = await self.generate_reasoning_step(
                    StepType.RESULT,
                    final_response
                )
                yield final_step
                
        except Exception as e:
            error_step = await self.generate_reasoning_step(
                StepType.ERROR,
                f"Error during research analysis: {str(e)}"
            )
            yield error_step 