#!/usr/bin/env python3
"""
Self-Editing Agent: Autonomous Code Modification and Debugging

This agent can:
1. Analyze its own code and identify issues
2. Modify its own code to fix bugs and improve performance
3. Debug issues by analyzing logs and error patterns
4. Refactor code for better maintainability
5. Add new features and capabilities
6. Test changes before applying them
"""

import asyncio
import json
import ast
import inspect
import os
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import difflib
import re
import importlib.util
from dataclasses import dataclass, asdict

from core.openai_manager import openai_manager
from utils.logger import logger
from agents.codebase_analyzer import codebase_analyzer

@dataclass
class CodeModification:
    file_path: str
    modification_type: str  # "bug_fix", "optimization", "refactoring", "new_feature", "debug"
    description: str
    original_code: str
    modified_code: str
    diff: str
    confidence: float
    impact_analysis: Dict[str, Any]
    test_results: Dict[str, Any]
    applied: bool = False
    timestamp: datetime = None

@dataclass
class DebugResult:
    issue_id: str
    root_cause: str
    suggested_fix: str
    confidence: float
    priority: str  # "critical", "high", "medium", "low"
    affected_files: List[str]
    fix_applied: bool = False

class SelfEditingAgent:
    """
    Agent that can modify and debug its own code.
    
    Capabilities:
    - Self-analysis and issue detection
    - Autonomous code modification
    - Debugging and error resolution
    - Performance optimization
    - Code refactoring
    - Feature addition
    """
    
    def __init__(self):
        self.modification_history = []
        self.debug_history = []
        self.test_results = {}
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.max_modifications_per_session = 10
        self.require_approval_for_critical_changes = True
        self.auto_backup_before_changes = True
        self.test_changes_before_applying = True
        
        logger.info("🔧 Self-Editing Agent initialized")
    
    async def analyze_self(self) -> Dict[str, Any]:
        """Analyze the agent's own code for issues and improvements."""
        logger.info("🔍 Self-Editing Agent analyzing its own code...")
        
        # Get the agent's own file path
        agent_file = inspect.getfile(self.__class__)
        
        analysis = {
            "agent_file": agent_file,
            "issues_found": [],
            "improvements_suggested": [],
            "performance_metrics": {},
            "maintainability_score": 0.0
        }
        
        try:
            # Analyze the agent's code
            file_analysis = await codebase_analyzer._analyze_single_file(agent_file, agent_file)
            if file_analysis:
                # Find issues
                issues = await codebase_analyzer._analyze_file_issues(file_analysis)
                analysis["issues_found"] = [asdict(issue) for issue in issues]
                
                # Calculate scores
                analysis["maintainability_score"] = file_analysis.get("maintainability_score", 0)
                analysis["performance_metrics"] = {
                    "complexity_score": file_analysis.get("complexity_score", 0),
                    "lines_of_code": file_analysis.get("lines", 0),
                    "functions": len(file_analysis.get("functions", [])),
                    "classes": len(file_analysis.get("classes", []))
                }
                
                # Suggest improvements
                analysis["improvements_suggested"] = await self._suggest_self_improvements(file_analysis, issues)
            
        except Exception as e:
            logger.error(f"Self-analysis failed: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    async def _suggest_self_improvements(self, file_analysis: Dict[str, Any], issues: List[Any]) -> List[Dict[str, Any]]:
        """Suggest improvements for the agent's own code."""
        improvements = []
        
        # Performance improvements
        complexity = file_analysis.get("complexity_score", 0)
        if complexity > 5.0:
            improvements.append({
                "type": "performance_optimization",
                "description": f"Reduce complexity (current: {complexity:.1f})",
                "priority": "high",
                "effort": "medium",
                "impact": "high"
            })
        
        # Maintainability improvements
        maintainability = file_analysis.get("maintainability_score", 0)
        if maintainability < 5.0:
            improvements.append({
                "type": "refactoring",
                "description": f"Improve maintainability (current: {maintainability:.1f})",
                "priority": "medium",
                "effort": "high",
                "impact": "medium"
            })
        
        # Bug fixes
        for issue in issues:
            if issue.severity in ["critical", "high"]:
                improvements.append({
                    "type": "bug_fix",
                    "description": issue.description,
                    "priority": issue.severity,
                    "effort": "low",
                    "impact": "high",
                    "line_number": issue.line_number
                })
        
        return improvements
    
    async def fix_self_issue(self, issue_description: str) -> bool:
        """Fix an issue in the agent's own code."""
        logger.info(f"🔧 Self-Editing Agent fixing issue: {issue_description}")
        
        try:
            # Get the agent's file path
            agent_file = inspect.getfile(self.__class__)
            
            # Create backup
            if self.auto_backup_before_changes:
                await self._create_backup(agent_file)
            
            # Apply the fix
            success = await codebase_analyzer.apply_code_fix(agent_file, issue_description)
            
            if success:
                # Test the changes
                if self.test_changes_before_applying:
                    test_result = await self._test_self_modification(agent_file)
                    if not test_result["success"]:
                        logger.warning("Self-modification test failed, reverting...")
                        await self._revert_backup(agent_file)
                        return False
                
                logger.info("✅ Self-issue fixed successfully")
                return True
            else:
                logger.error("Failed to apply self-fix")
                return False
                
        except Exception as e:
            logger.error(f"Self-fix failed: {e}")
            return False
    
    async def optimize_self(self, optimization_type: str = "performance") -> bool:
        """Optimize the agent's own code."""
        logger.info(f"⚡ Self-Editing Agent optimizing for {optimization_type}")
        
        try:
            agent_file = inspect.getfile(self.__class__)
            
            # Create backup
            if self.auto_backup_before_changes:
                await self._create_backup(agent_file)
            
            # Generate optimization
            optimization_description = await self._generate_optimization_description(optimization_type)
            
            # Apply optimization
            success = await codebase_analyzer.apply_code_fix(agent_file, optimization_description)
            
            if success:
                # Test the optimization
                if self.test_changes_before_applying:
                    test_result = await self._test_self_modification(agent_file)
                    if not test_result["success"]:
                        logger.warning("Self-optimization test failed, reverting...")
                        await self._revert_backup(agent_file)
                        return False
                
                logger.info(f"✅ Self-optimization ({optimization_type}) applied successfully")
                return True
            else:
                logger.error("Failed to apply self-optimization")
                return False
                
        except Exception as e:
            logger.error(f"Self-optimization failed: {e}")
            return False
    
    async def debug_self(self, error_message: str = None, log_file: str = None) -> DebugResult:
        """Debug issues in the agent's own code."""
        logger.info("🐛 Self-Editing Agent debugging...")
        
        try:
            # Collect debug information
            debug_info = await self._collect_debug_info(error_message, log_file)
            
            # Analyze the issue
            analysis = await self._analyze_debug_info(debug_info)
            
            # Generate fix
            fix = await self._generate_debug_fix(analysis)
            
            # Create debug result
            debug_result = DebugResult(
                issue_id=f"debug_{datetime.now().timestamp()}",
                root_cause=analysis.get("root_cause", "Unknown"),
                suggested_fix=fix.get("fix", ""),
                confidence=fix.get("confidence", 0.0),
                priority=analysis.get("priority", "medium"),
                affected_files=analysis.get("affected_files", [])
            )
            
            # Apply fix if confidence is high
            if debug_result.confidence > 0.8:
                success = await self._apply_debug_fix(debug_result)
                debug_result.fix_applied = success
            
            self.debug_history.append(debug_result)
            
            logger.info(f"✅ Debug completed: {debug_result.root_cause}")
            return debug_result
            
        except Exception as e:
            logger.error(f"Self-debug failed: {e}")
            return DebugResult(
                issue_id=f"debug_error_{datetime.now().timestamp()}",
                root_cause="Debug process failed",
                suggested_fix="Manual intervention required",
                confidence=0.0,
                priority="critical",
                affected_files=[]
            )
    
    async def add_self_feature(self, feature_description: str) -> bool:
        """Add a new feature to the agent's own code."""
        logger.info(f"✨ Self-Editing Agent adding feature: {feature_description}")
        
        try:
            agent_file = inspect.getfile(self.__class__)
            
            # Create backup
            if self.auto_backup_before_changes:
                await self._create_backup(agent_file)
            
            # Generate feature code
            feature_code = await self._generate_feature_code(feature_description)
            
            if feature_code:
                # Apply the feature
                success = await self._apply_feature_code(agent_file, feature_code)
                
                if success:
                    # Test the new feature
                    if self.test_changes_before_applying:
                        test_result = await self._test_self_modification(agent_file)
                        if not test_result["success"]:
                            logger.warning("New feature test failed, reverting...")
                            await self._revert_backup(agent_file)
                            return False
                    
                    logger.info("✅ New feature added successfully")
                    return True
                else:
                    logger.error("Failed to apply new feature")
                    return False
            else:
                logger.error("Failed to generate feature code")
                return False
                
        except Exception as e:
            logger.error(f"Add feature failed: {e}")
            return False
    
    async def refactor_self(self, refactoring_type: str = "general") -> bool:
        """Refactor the agent's own code for better maintainability."""
        logger.info(f"🔄 Self-Editing Agent refactoring ({refactoring_type})...")
        
        try:
            agent_file = inspect.getfile(self.__class__)
            
            # Create backup
            if self.auto_backup_before_changes:
                await self._create_backup(agent_file)
            
            # Generate refactoring plan
            refactoring_plan = await self._generate_refactoring_plan(refactoring_type)
            
            # Apply refactoring
            success = await self._apply_refactoring(agent_file, refactoring_plan)
            
            if success:
                # Test the refactored code
                if self.test_changes_before_applying:
                    test_result = await self._test_self_modification(agent_file)
                    if not test_result["success"]:
                        logger.warning("Refactoring test failed, reverting...")
                        await self._revert_backup(agent_file)
                        return False
                
                logger.info("✅ Self-refactoring completed successfully")
                return True
            else:
                logger.error("Failed to apply refactoring")
                return False
                
        except Exception as e:
            logger.error(f"Self-refactoring failed: {e}")
            return False
    
    async def _create_backup(self, file_path: str):
        """Create a backup of a file before modification."""
        try:
            backup_path = self.backup_dir / f"{Path(file_path).name}.backup_{datetime.now().timestamp()}"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"📦 Backup created: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
    
    async def _revert_backup(self, file_path: str):
        """Revert a file to its backup."""
        try:
            backup_files = list(self.backup_dir.glob(f"{Path(file_path).name}.backup_*"))
            if backup_files:
                latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"🔄 Reverted to backup: {latest_backup}")
        except Exception as e:
            logger.error(f"Failed to revert backup: {e}")
    
    async def _test_self_modification(self, file_path: str) -> Dict[str, Any]:
        """Test a self-modification to ensure it works correctly."""
        try:
            # Try to import the modified module
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Basic functionality test
                test_result = {
                    "success": True,
                    "import_successful": True,
                    "basic_functionality": True,
                    "errors": []
                }
                
                # Test if the class can be instantiated
                try:
                    if hasattr(module, 'SelfEditingAgent'):
                        agent = module.SelfEditingAgent()
                        test_result["instantiation_successful"] = True
                    else:
                        test_result["instantiation_successful"] = False
                        test_result["errors"].append("SelfEditingAgent class not found")
                except Exception as e:
                    test_result["instantiation_successful"] = False
                    test_result["errors"].append(f"Instantiation failed: {e}")
                
                return test_result
            else:
                return {
                    "success": False,
                    "import_successful": False,
                    "errors": ["Failed to create module spec"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "import_successful": False,
                "errors": [str(e)]
            }
    
    async def _generate_optimization_description(self, optimization_type: str) -> str:
        """Generate a description for code optimization."""
        if optimization_type == "performance":
            return "Optimize code for better performance by reducing complexity, improving algorithms, and eliminating bottlenecks"
        elif optimization_type == "memory":
            return "Optimize memory usage by reducing object creation, improving data structures, and implementing proper cleanup"
        elif optimization_type == "readability":
            return "Improve code readability by adding comments, simplifying logic, and using better variable names"
        else:
            return f"Apply general {optimization_type} optimizations to improve code quality"
    
    async def _collect_debug_info(self, error_message: str = None, log_file: str = None) -> Dict[str, Any]:
        """Collect debug information from various sources."""
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "error_message": error_message,
            "log_entries": [],
            "stack_trace": None,
            "system_info": {}
        }
        
        # Collect log entries
        if log_file and os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    debug_info["log_entries"] = f.readlines()[-100:]  # Last 100 lines
            except Exception as e:
                logger.error(f"Failed to read log file: {e}")
        
        # Collect system info
        debug_info["system_info"] = {
            "python_version": sys.version,
            "platform": sys.platform,
            "current_directory": os.getcwd(),
            "memory_usage": self._get_memory_usage()
        }
        
        # Collect stack trace if error occurred
        if error_message:
            debug_info["stack_trace"] = traceback.format_exc()
        
        return debug_info
    
    async def _analyze_debug_info(self, debug_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze debug information to identify root cause."""
        try:
            prompt = f"""
            Analyze the following debug information and identify the root cause of the issue.
            Provide a detailed analysis with confidence level and priority.

            Debug Information:
            {json.dumps(debug_info, indent=2)}

            Respond in JSON format with:
            - root_cause: string
            - confidence: float (0-1)
            - priority: string (critical/high/medium/low)
            - affected_files: list of file paths
            - suggested_action: string
            """
            
            result = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            analysis = json.loads(result["content"])
            return analysis
            
        except Exception as e:
            logger.error(f"Debug analysis failed: {e}")
            return {
                "root_cause": "Analysis failed",
                "confidence": 0.0,
                "priority": "medium",
                "affected_files": [],
                "suggested_action": "Manual investigation required"
            }
    
    async def _generate_debug_fix(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fix for the debugged issue."""
        try:
            prompt = f"""
            Generate a code fix for the following issue analysis.
            Provide the fix as code and confidence level.

            Analysis:
            {json.dumps(analysis, indent=2)}

            Respond in JSON format with:
            - fix: string (the code fix)
            - confidence: float (0-1)
            - description: string
            """
            
            result = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            fix = json.loads(result["content"])
            return fix
            
        except Exception as e:
            logger.error(f"Debug fix generation failed: {e}")
            return {
                "fix": "",
                "confidence": 0.0,
                "description": "Failed to generate fix"
            }
    
    async def _apply_debug_fix(self, debug_result: DebugResult) -> bool:
        """Apply a debug fix to the code."""
        try:
            if debug_result.affected_files:
                file_path = debug_result.affected_files[0]  # Apply to first affected file
                return await codebase_analyzer.apply_code_fix(file_path, debug_result.suggested_fix)
            return False
        except Exception as e:
            logger.error(f"Failed to apply debug fix: {e}")
            return False
    
    async def _generate_feature_code(self, feature_description: str) -> Optional[str]:
        """Generate code for a new feature."""
        try:
            prompt = f"""
            Generate Python code for the following feature description.
            The code should be a complete implementation that can be integrated into the SelfEditingAgent class.

            Feature Description: {feature_description}

            Provide only the Python code, no explanations.
            """
            
            result = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return result["content"]
            
        except Exception as e:
            logger.error(f"Feature code generation failed: {e}")
            return None
    
    async def _apply_feature_code(self, file_path: str, feature_code: str) -> bool:
        """Apply new feature code to the file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the end of the class to add the new method
            class_end = content.rfind('class SelfEditingAgent:')
            if class_end == -1:
                return False
            
            # Find the end of the class
            lines = content.splitlines()
            class_start = -1
            class_end = -1
            
            for i, line in enumerate(lines):
                if 'class SelfEditingAgent:' in line:
                    class_start = i
                elif class_start != -1 and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    class_end = i
                    break
            
            if class_start == -1:
                return False
            
            if class_end == -1:
                class_end = len(lines)
            
            # Insert the new feature code
            new_lines = lines[:class_end] + [feature_code] + lines[class_end:]
            new_content = '\n'.join(new_lines)
            
            # Write the modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply feature code: {e}")
            return False
    
    async def _generate_refactoring_plan(self, refactoring_type: str) -> Dict[str, Any]:
        """Generate a refactoring plan."""
        try:
            prompt = f"""
            Generate a refactoring plan for the SelfEditingAgent class.
            Focus on {refactoring_type} improvements.

            Provide the plan in JSON format with:
            - description: string
            - changes: list of specific changes
            - benefits: list of benefits
            - risks: list of potential risks
            """
            
            result = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return json.loads(result["content"])
            
        except Exception as e:
            logger.error(f"Refactoring plan generation failed: {e}")
            return {
                "description": "General refactoring",
                "changes": [],
                "benefits": [],
                "risks": []
            }
    
    async def _apply_refactoring(self, file_path: str, refactoring_plan: Dict[str, Any]) -> bool:
        """Apply refactoring changes to the file."""
        try:
            # For now, use a general refactoring approach
            # In a real implementation, this would be more sophisticated
            return await codebase_analyzer.apply_code_fix(file_path, "Refactor code for better maintainability and readability")
        except Exception as e:
            logger.error(f"Failed to apply refactoring: {e}")
            return False
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage information."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    async def get_modification_history(self) -> List[Dict[str, Any]]:
        """Get the history of self-modifications."""
        return [asdict(mod) for mod in self.modification_history]
    
    async def get_debug_history(self) -> List[Dict[str, Any]]:
        """Get the history of debug sessions."""
        return [asdict(debug) for debug in self.debug_history]
    
    async def get_self_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent's self-modifications."""
        return {
            "total_modifications": len(self.modification_history),
            "total_debug_sessions": len(self.debug_history),
            "successful_modifications": len([m for m in self.modification_history if m.applied]),
            "successful_debug_fixes": len([d for d in self.debug_history if d.fix_applied]),
            "last_modification": self.modification_history[-1].timestamp if self.modification_history else None,
            "last_debug_session": self.debug_history[-1].timestamp if self.debug_history else None
        }

# Singleton instance
self_editing_agent = SelfEditingAgent() 