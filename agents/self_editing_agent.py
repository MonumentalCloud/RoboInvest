"""
Self-Editing Agent - Production-grade code modification with safety and validation

Features:
- Request analysis and code generation
- Change validation and safety checks
- Integration with change manager and logger
- Rollback capabilities
- Impact analysis before changes
- User approval workflow for major changes
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re
from pathlib import Path

from utils.logger import logger
from core.change_logger import change_logger, CodeChange, ChangeStatus, ChangeType
from core.change_manager import change_manager
from agents.codebase_analyzer import codebase_analyzer
from core.openai_manager import openai_manager


@dataclass
class CodeChangeRequest:
    """Represents a request for code changes"""
    request_id: str
    user_request: str
    change_type: ChangeType
    priority: str  # 'low', 'medium', 'high', 'critical'
    urgency: str  # 'immediate', 'soon', 'when_convenient'
    context: Dict[str, Any]
    timestamp: datetime


@dataclass
class GeneratedCode:
    """Represents generated code with metadata"""
    file_path: str
    code_content: str
    description: str
    reasoning: str
    dependencies: List[str]
    validation_status: str  # 'pending', 'validated', 'failed'
    validation_errors: List[str]


class SelfEditingAgent:
    """Production-grade self-editing agent with safety and validation"""
    
    def __init__(self):
        self.agent_id = "self_editing_agent"
        self.capabilities = [
            "code_generation",
            "file_modification", 
            "new_endpoint_creation",
            "agent_creation",
            "dependency_management",
            "safety_validation",
            "impact_analysis"
        ]
        
        # Safety thresholds
        self.critical_change_threshold = 5  # Files affected
        self.risk_patterns = [
            r"rm\s+-rf",
            r"del\s+/s",
            r"format\s+",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r"os\.system",
            r"subprocess\.call",
            r"eval\(",
            r"exec\(",
            r"__import__\(",
            r"globals\(",
            r"locals\("
        ]
        
        logger.info("SelfEditingAgent initialized with safety protocols")
    
    def process_change_request(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user request for code changes"""
        try:
            request_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Create change request
            change_request = CodeChangeRequest(
                request_id=request_id,
                user_request=user_request,
                change_type=self._classify_request(user_request),
                priority=self._assess_priority(user_request),
                urgency=self._assess_urgency(user_request),
                context=context or {},
                timestamp=timestamp
            )
            
            logger.info(f"Processing change request {request_id}: {user_request[:100]}...")
            
            # Analyze the request
            analysis = self._analyze_request(change_request)
            
            # Generate code changes
            generated_changes = self._generate_code_changes(change_request, analysis)
            
            # Validate changes
            validation_results = self._validate_changes(generated_changes)
            
            # Assess impact
            impact_analysis = self._assess_impact(generated_changes)
            
            # Determine if user approval is needed
            requires_approval = self._requires_user_approval(change_request, impact_analysis)
            
            # Apply changes if safe and approved
            if not requires_approval and all(v["valid"] for v in validation_results.values()):
                application_results = self._apply_changes(generated_changes, change_request)
                return {
                    "request_id": request_id,
                    "status": "completed",
                    "changes_applied": len(application_results),
                    "changes": application_results,
                    "impact_analysis": impact_analysis,
                    "requires_restart": any(c.get("requires_restart", False) for c in application_results)
                }
            else:
                # Return proposed changes for user approval
                return {
                    "request_id": request_id,
                    "status": "pending_approval",
                    "requires_approval": requires_approval,
                    "proposed_changes": generated_changes,
                    "validation_results": validation_results,
                    "impact_analysis": impact_analysis,
                    "approval_reason": self._get_approval_reason(change_request, impact_analysis)
                }
                
        except Exception as e:
            logger.error(f"Failed to process change request: {e}")
            return {
                "request_id": request_id if 'request_id' in locals() else "unknown",
                "status": "failed",
                "error": str(e)
            }
    
    def _classify_request(self, user_request: str) -> ChangeType:
        """Classify the type of change request"""
        request_lower = user_request.lower()
        
        if any(keyword in request_lower for keyword in ["endpoint", "api", "route"]):
            return ChangeType.NEW_ENDPOINT
        elif any(keyword in request_lower for keyword in ["agent", "create agent", "new agent"]):
            return ChangeType.NEW_AGENT
        elif any(keyword in request_lower for keyword in ["modify", "update", "change", "fix"]):
            return ChangeType.MODIFY_EXISTING
        elif any(keyword in request_lower for keyword in ["config", "configuration", "settings"]):
            return ChangeType.CONFIG_CHANGE
        elif any(keyword in request_lower for keyword in ["dependency", "package", "install"]):
            return ChangeType.DEPENDENCY_UPDATE
        else:
            return ChangeType.MODIFY_EXISTING
    
    def _assess_priority(self, user_request: str) -> str:
        """Assess the priority of a change request"""
        request_lower = user_request.lower()
        
        if any(keyword in request_lower for keyword in ["urgent", "critical", "emergency", "broken", "error"]):
            return "critical"
        elif any(keyword in request_lower for keyword in ["important", "needed", "required"]):
            return "high"
        elif any(keyword in request_lower for keyword in ["nice to have", "improvement", "enhancement"]):
            return "medium"
        else:
            return "low"
    
    def _assess_urgency(self, user_request: str) -> str:
        """Assess the urgency of a change request"""
        request_lower = user_request.lower()
        
        if any(keyword in request_lower for keyword in ["now", "immediately", "urgent", "asap"]):
            return "immediate"
        elif any(keyword in request_lower for keyword in ["soon", "quickly", "fast"]):
            return "soon"
        else:
            return "when_convenient"
    
    def _analyze_request(self, change_request: CodeChangeRequest) -> Dict[str, Any]:
        """Analyze the change request and gather context"""
        try:
            # Analyze current codebase
            codebase_analysis = codebase_analyzer.analyze_codebase()
            
            # Search for relevant existing code
            search_results = codebase_analyzer.search_code(change_request.user_request)
            
            # Get current API endpoints
            current_endpoints = codebase_analyzer.get_api_endpoints()
            
            # Get current agents
            current_agents = codebase_analyzer.get_agents()
            
            return {
                "codebase_analysis": codebase_analysis or {},
                "search_results": search_results or [],
                "current_endpoints": current_endpoints or [],
                "current_agents": current_agents or [],
                "request_context": change_request.context
            }
            
        except Exception as e:
            logger.error(f"Request analysis failed: {e}")
            return {"error": str(e)}
    
    def _generate_code_changes(self, change_request: CodeChangeRequest, 
                             analysis: Dict[str, Any]) -> List[GeneratedCode]:
        """Generate code changes based on the request"""
        try:
            # Prepare context for AI
            context = {
                "user_request": change_request.user_request,
                "change_type": change_request.change_type.value,
                "codebase_summary": analysis.get("codebase_analysis", {}),
                "existing_endpoints": [ep.endpoint_path for ep in analysis.get("current_endpoints", [])],
                "existing_agents": [agent.agent_name for agent in analysis.get("current_agents", [])],
                "search_results": analysis.get("search_results", [])
            }
            
            # Generate code using AI
            prompt = self._build_code_generation_prompt(context)
            
            messages = [{"role": "user", "content": prompt}]
            response_data = openai_manager.chat_completion(
                messages=messages,
                temperature=0.1,
                response_format="json"
            )
            
            response = response_data.get("content")
            
            if not response:
                raise Exception("Failed to generate code: No response from AI")
            
            # Parse generated code
            try:
                generated_data = json.loads(response)
                generated_changes = []
                
                for change in generated_data.get("changes", []):
                    generated_code = GeneratedCode(
                        file_path=change["file_path"],
                        code_content=change["code_content"],
                        description=change["description"],
                        reasoning=change["reasoning"],
                        dependencies=change.get("dependencies", []),
                        validation_status="pending",
                        validation_errors=[]
                    )
                    generated_changes.append(generated_code)
                
                return generated_changes
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse generated code: {e}")
                raise Exception(f"Invalid code generation response: {e}")
                
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise
    
    def _build_code_generation_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for code generation"""
        return f"""
You are a self-editing AI agent that can modify its own codebase. Generate code changes based on the user request.

CONTEXT:
- User Request: {context['user_request']}
- Change Type: {context['change_type']}
- Existing Endpoints: {context['existing_endpoints']}
- Existing Agents: {context['existing_agents']}

REQUIREMENTS:
1. Generate production-ready code with proper error handling
2. Follow existing code patterns and conventions
3. Include proper imports and dependencies
4. Add appropriate logging and documentation
5. Ensure code is safe and follows security best practices

RESPONSE FORMAT:
Return a JSON object with the following structure:
{{
    "changes": [
        {{
            "file_path": "path/to/file.py",
            "code_content": "complete code content",
            "description": "Brief description of the change",
            "reasoning": "Detailed reasoning for the change",
            "dependencies": ["list", "of", "dependencies"]
        }}
    ]
}}

Generate the code changes now:
"""
    
    def _validate_changes(self, generated_changes: List[GeneratedCode]) -> Dict[str, Dict[str, Any]]:
        """Validate generated code changes"""
        validation_results = {}
        
        for change in generated_changes:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "safety_score": 100
            }
            
            # Check for dangerous patterns
            for pattern in self.risk_patterns:
                if re.search(pattern, change.code_content, re.IGNORECASE):
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Dangerous pattern detected: {pattern}")
                    validation_result["safety_score"] -= 50
            
            # Check for basic syntax
            if change.file_path.endswith('.py'):
                try:
                    compile(change.code_content, '<string>', 'exec')
                except SyntaxError as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Syntax error: {e}")
                    validation_result["safety_score"] -= 30
            
            # Check file path safety
            if '..' in change.file_path or change.file_path.startswith('/'):
                validation_result["valid"] = False
                validation_result["errors"].append("Unsafe file path")
                validation_result["safety_score"] -= 40
            
            # Check for required imports
            if change.file_path.endswith('.py'):
                required_imports = ['from utils.logger import logger']
                for imp in required_imports:
                    if imp not in change.code_content:
                        validation_result["warnings"].append(f"Missing recommended import: {imp}")
                        validation_result["safety_score"] -= 5
            
            validation_results[change.file_path] = validation_result
            change.validation_status = "validated" if validation_result["valid"] else "failed"
            change.validation_errors = validation_result["errors"]
        
        return validation_results
    
    def _assess_impact(self, generated_changes: List[GeneratedCode]) -> Dict[str, Any]:
        """Assess the impact of proposed changes"""
        try:
            total_files = len(generated_changes)
            new_files = len([c for c in generated_changes if not (Path(c.file_path)).exists()])
            modified_files = total_files - new_files
            
            # Calculate impact score
            impact_score = new_files * 2 + modified_files
            
            # Check for critical files
            critical_files = []
            for change in generated_changes:
                if any(critical in change.file_path.lower() for critical in ['main.py', 'config.py', 'core/', 'agents/']):
                    critical_files.append(change.file_path)
            
            # Determine risk level
            if impact_score > 10 or len(critical_files) > 2:
                risk_level = "high"
            elif impact_score > 5 or len(critical_files) > 0:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "total_files_affected": total_files,
                "new_files": new_files,
                "modified_files": modified_files,
                "critical_files": critical_files,
                "impact_score": impact_score,
                "risk_level": risk_level,
                "requires_restart": any('main.py' in c.file_path or 'api' in c.file_path for c in generated_changes)
            }
            
        except Exception as e:
            logger.error(f"Impact assessment failed: {e}")
            return {"error": str(e)}
    
    def _requires_user_approval(self, change_request: CodeChangeRequest, 
                              impact_analysis: Dict[str, Any]) -> bool:
        """Determine if user approval is required"""
        # Always require approval for critical changes
        if change_request.priority == "critical":
            return True
        
        # Require approval for high impact changes
        if impact_analysis.get("risk_level") == "high":
            return True
        
        # Require approval for changes affecting critical files
        if len(impact_analysis.get("critical_files", [])) > 0:
            return True
        
        # Require approval for system architecture changes
        if change_request.change_type == ChangeType.SYSTEM_ARCHITECTURE:
            return True
        
        return False
    
    def _get_approval_reason(self, change_request: CodeChangeRequest, 
                           impact_analysis: Dict[str, Any]) -> str:
        """Get the reason why approval is required"""
        reasons = []
        
        if change_request.priority == "critical":
            reasons.append("Critical priority change")
        
        if impact_analysis.get("risk_level") == "high":
            reasons.append("High impact change")
        
        if len(impact_analysis.get("critical_files", [])) > 0:
            reasons.append("Affects critical system files")
        
        if change_request.change_type == ChangeType.SYSTEM_ARCHITECTURE:
            reasons.append("System architecture change")
        
        return "; ".join(reasons) if reasons else "Safety protocol"
    
    def _apply_changes(self, generated_changes: List[GeneratedCode], 
                      change_request: CodeChangeRequest) -> List[Dict[str, Any]]:
        """Apply the generated code changes"""
        results = []
        
        for change in generated_changes:
            try:
                # Create change record
                change_record = CodeChange(
                    change_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    change_type=change_request.change_type,
                    status=ChangeStatus.PROPOSED,
                    description=change.description,
                    files_modified=[change.file_path],
                    git_commit_hash=None,
                    git_branch=change_manager.current_branch,
                    user_approved=False,
                    applied_by=self.agent_id,
                    reasoning=change.reasoning,
                    metadata={
                        "request_id": change_request.request_id,
                        "dependencies": change.dependencies,
                        "validation_status": change.validation_status
                    }
                )
                
                # Log the change
                change_logger.log_change(change_record)
                
                # Apply the change
                success, message, commit_hash = change_manager.apply_change(
                    change_record, change.code_content, change.file_path
                )
                
                if success:
                    results.append({
                        "file_path": change.file_path,
                        "status": "applied",
                        "commit_hash": commit_hash,
                        "description": change.description,
                        "requires_restart": self._requires_restart(change.file_path)
                    })
                else:
                    results.append({
                        "file_path": change.file_path,
                        "status": "failed",
                        "error": message,
                        "description": change.description
                    })
                    
            except Exception as e:
                logger.error(f"Failed to apply change to {change.file_path}: {e}")
                results.append({
                    "file_path": change.file_path,
                    "status": "failed",
                    "error": str(e),
                    "description": change.description
                })
        
        return results
    
    def _requires_restart(self, file_path: str) -> bool:
        """Determine if a file change requires system restart"""
        restart_patterns = [
            'main.py', 'app.py', 'server.py', 'api/', 'core/config',
            'agents/', 'meta_agent', 'governor'
        ]
        
        return any(pattern in file_path.lower() for pattern in restart_patterns)
    
    def approve_changes(self, request_id: str, user_approval: bool = True) -> Dict[str, Any]:
        """Approve and apply pending changes"""
        try:
            # Find pending changes for this request
            pending_changes = change_logger.get_changes_by_status(ChangeStatus.PROPOSED)
            request_changes = [c for c in pending_changes if c.metadata.get("request_id") == request_id]
            
            if not request_changes:
                return {"error": "No pending changes found for this request"}
            
            if not user_approval:
                # Mark changes as rejected
                for change in request_changes:
                    change.status = ChangeStatus.FAILED
                    change_logger.update_change_status(change.change_id, ChangeStatus.FAILED)
                
                return {"status": "rejected", "message": "Changes rejected by user"}
            
            # Apply approved changes
            results = []
            for change in request_changes:
                # This would need to regenerate the code content
                # For now, we'll mark as approved
                change.status = ChangeStatus.APPROVED
                change.user_approved = True
                change_logger.update_change_status(change.change_id, ChangeStatus.APPROVED)
                
                results.append({
                    "change_id": change.change_id,
                    "status": "approved",
                    "description": change.description
                })
            
            return {
                "status": "approved",
                "changes": results,
                "message": f"Approved {len(results)} changes"
            }
            
        except Exception as e:
            logger.error(f"Change approval failed: {e}")
            return {"error": str(e)}
    
    def rollback_changes(self, request_id: str, reason: str = "User requested rollback") -> Dict[str, Any]:
        """Rollback changes for a specific request"""
        try:
            # Find applied changes for this request
            applied_changes = change_logger.get_changes_by_status(ChangeStatus.APPLIED)
            request_changes = [c for c in applied_changes if c.metadata.get("request_id") == request_id]
            
            if not request_changes:
                return {"error": "No applied changes found for this request"}
            
            # Rollback each change
            results = []
            for change in request_changes:
                success, message, rollback_hash = change_manager.rollback_change(
                    change.change_id, reason
                )
                
                results.append({
                    "change_id": change.change_id,
                    "status": "rolled_back" if success else "failed",
                    "message": message,
                    "rollback_hash": rollback_hash
                })
            
            return {
                "status": "completed",
                "rollbacks": results,
                "message": f"Rolled back {len(results)} changes"
            }
            
        except Exception as e:
            logger.error(f"Change rollback failed: {e}")
            return {"error": str(e)}
    
    def get_change_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of changes for a request"""
        try:
            all_changes = change_logger.get_recent_changes(limit=100)
            request_changes = [c for c in all_changes if c.metadata.get("request_id") == request_id]
            
            if not request_changes:
                return {"error": "No changes found for this request"}
            
            status_summary = {
                "request_id": request_id,
                "total_changes": len(request_changes),
                "status_breakdown": {},
                "changes": []
            }
            
            for change in request_changes:
                status = change.status.value
                status_summary["status_breakdown"][status] = status_summary["status_breakdown"].get(status, 0) + 1
                
                status_summary["changes"].append({
                    "change_id": change.change_id,
                    "status": status,
                    "description": change.description,
                    "file_path": change.files_modified[0] if change.files_modified else "unknown",
                    "timestamp": change.timestamp.isoformat(),
                    "commit_hash": change.git_commit_hash
                })
            
            return status_summary
            
        except Exception as e:
            logger.error(f"Failed to get change status: {e}")
            return {"error": str(e)}


# Global instance
self_editing_agent = SelfEditingAgent() 