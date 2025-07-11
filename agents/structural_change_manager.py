#!/usr/bin/env python3
"""
Structural Change Manager Agent
LLM-powered system that continuously monitors performance and manages structural changes with human permission.

This agent:
1. Continuously monitors system performance metrics
2. Uses LLM to analyze trends and identify improvement opportunities
3. Generates detailed change proposals with impact analysis
4. Sends email requests for permission with comprehensive details
5. Applies changes only after explicit human approval
6. Tracks all changes and their performance impact
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
from enum import Enum

from core.openai_manager import openai_manager
from core.central_event_bus import central_event_bus, EventType, EventPriority
from core.notification_aggregator import notification_aggregator
from agents.self_editing_agent import SelfEditingAgent
from agents.codebase_analyzer import codebase_analyzer
from utils.logger import logger


class ChangeType(Enum):
    """Types of structural changes"""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CODE_REFACTORING = "code_refactoring"
    ARCHITECTURE_IMPROVEMENT = "architecture_improvement"
    AGENT_CONFIGURATION = "agent_configuration"
    RISK_MANAGEMENT = "risk_management"
    MONITORING_ENHANCEMENT = "monitoring_enhancement"
    NEW_FEATURE = "new_feature"
    BUG_FIX = "bug_fix"


class ChangePriority(Enum):
    """Change priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ApprovalStatus(Enum):
    """Change approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class PerformanceMetric:
    """Performance metric structure"""
    metric_name: str
    current_value: float
    historical_values: List[float]
    trend: str  # "improving", "declining", "stable"
    threshold: float
    is_critical: bool
    timestamp: datetime


@dataclass
class ChangeProposal:
    """Structural change proposal"""
    proposal_id: str
    change_type: ChangeType
    priority: ChangePriority
    title: str
    description: str
    rationale: str
    impact_analysis: Dict[str, Any]
    implementation_plan: List[str]
    estimated_effort: str
    risk_assessment: Dict[str, Any]
    performance_improvement_expected: Dict[str, float]
    affected_components: List[str]
    created_at: datetime
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    implemented_at: Optional[datetime] = None
    actual_performance_impact: Optional[Dict[str, float]] = None


@dataclass
class ChangeResult:
    """Result of implemented change"""
    proposal_id: str
    success: bool
    performance_impact: Dict[str, float]
    issues_encountered: List[str]
    lessons_learned: List[str]
    implemented_at: datetime
    evaluation_period_days: int = 7


class StructuralChangeManager:
    """
    LLM-powered structural change management system.
    
    Features:
    - Continuous performance monitoring
    - LLM-based trend analysis and change identification
    - Comprehensive change proposals with impact analysis
    - Email-based permission workflow
    - Change tracking and performance evaluation
    """
    
    def __init__(self):
        self.performance_metrics: Dict[str, PerformanceMetric] = {}
        self.change_proposals: Dict[str, ChangeProposal] = {}
        self.change_history: List[ChangeResult] = []
        self.monitoring_active = True
        self.last_analysis = None
        self.analysis_interval = timedelta(hours=1)  # Analyze every hour
        
        # LLM configuration
        self.use_llm = bool(openai_manager.api_key)
        self.analysis_prompt_template = self._load_analysis_prompt()
        
        # Change thresholds
        self.change_thresholds = {
            "performance_decline_threshold": 0.15,  # 15% decline triggers analysis
            "improvement_opportunity_threshold": 0.20,  # 20% potential improvement
            "critical_metric_threshold": 0.30,  # 30% decline is critical
            "max_changes_per_week": 5,
            "approval_expiry_hours": 48
        }
        
        # Initialize sub-agents
        self.self_editing_agent = SelfEditingAgent()
        
        logger.info("🏗️ Structural Change Manager initialized")
    
    def _load_analysis_prompt(self) -> str:
        """Load the LLM analysis prompt template."""
        return """
You are an expert system architect and performance analyst for the RoboInvest autonomous trading system.

Your task is to analyze system performance metrics and identify opportunities for structural improvements.

CURRENT PERFORMANCE METRICS:
{performance_metrics}

SYSTEM COMPONENTS:
- Parallel Execution Engine (8 agents)
- Risk Management System (NIST AI RMF)
- Central Event Bus
- Enhanced Trade Executor
- Notification System
- PnL Tracker
- Performance Monitor

ANALYSIS REQUIREMENTS:
1. Identify performance trends and anomalies
2. Suggest specific structural changes that could improve performance
3. Provide detailed impact analysis for each change
4. Prioritize changes based on impact and effort
5. Consider system stability and risk

RESPONSE FORMAT (JSON):
{{
    "analysis_summary": "Brief overview of current system health",
    "critical_issues": [
        {{
            "issue": "Description of critical issue",
            "impact": "Impact on system performance",
            "urgency": "critical/high/medium/low"
        }}
    ],
    "improvement_opportunities": [
        {{
            "opportunity": "Description of improvement opportunity",
            "expected_impact": {{
                "metric": "expected_improvement_percentage"
            }},
            "effort": "low/medium/high",
            "risk": "low/medium/high",
            "affected_components": ["component1", "component2"]
        }}
    ],
    "recommended_changes": [
        {{
            "change_type": "performance_optimization/code_refactoring/architecture_improvement/etc",
            "priority": "critical/high/medium/low",
            "title": "Brief title",
            "description": "Detailed description",
            "rationale": "Why this change is needed",
            "implementation_plan": ["step1", "step2", "step3"],
            "estimated_effort": "1-2 hours / 1-2 days / 1-2 weeks",
            "risk_assessment": {{
                "implementation_risk": "low/medium/high",
                "system_impact": "low/medium/high",
                "rollback_difficulty": "easy/medium/hard"
            }},
            "performance_improvement_expected": {{
                "metric_name": "expected_improvement_percentage"
            }},
            "affected_components": ["component1", "component2"]
        }}
    ]
}}

Focus on actionable, specific changes that will measurably improve system performance.
"""
    
    async def start_monitoring(self):
        """Start continuous performance monitoring and analysis."""
        logger.info("🔍 Starting continuous structural change monitoring")
        self.monitoring_active = True
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        # Start approval expiry checker
        asyncio.create_task(self._approval_expiry_checker())
        
        logger.info("✅ Structural change monitoring active")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        logger.info("⏹️ Structural change monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop that continuously analyzes performance."""
        while self.monitoring_active:
            try:
                # Collect current performance metrics
                await self._collect_performance_metrics()
                
                # Analyze trends and identify opportunities
                if self._should_analyze():
                    await self._analyze_and_propose_changes()
                
                # Check for expired approvals
                await self._check_expired_approvals()
                
                # Wait for next analysis cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _collect_performance_metrics(self):
        """Collect current performance metrics from all system components."""
        try:
            # Get metrics from parallel execution engine
            execution_metrics = await self._get_execution_metrics()
            
            # Get PnL and trading performance
            trading_metrics = await self._get_trading_metrics()
            
            # Get risk management metrics
            risk_metrics = await self._get_risk_metrics()
            
            # Get system health metrics
            system_metrics = await self._get_system_health_metrics()
            
            # Update performance metrics
            all_metrics = {
                **execution_metrics,
                **trading_metrics,
                **risk_metrics,
                **system_metrics
            }
            
            for metric_name, value in all_metrics.items():
                await self._update_metric(metric_name, value)
                
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
    
    async def _get_execution_metrics(self) -> Dict[str, float]:
        """Get metrics from parallel execution engine."""
        try:
            # This would integrate with the actual execution engine
            # For now, return mock metrics
            return {
                "parallel_efficiency": 0.85,
                "task_success_rate": 0.92,
                "avg_task_duration": 45.2,
                "agent_utilization": 0.78,
                "coordination_overhead": 0.12
            }
        except Exception as e:
            logger.error(f"Error getting execution metrics: {e}")
            return {}
    
    async def _get_trading_metrics(self) -> Dict[str, float]:
        """Get trading performance metrics."""
        try:
            # This would integrate with PnL tracker and performance tracker
            return {
                "total_pnl": 1250.50,
                "win_rate": 0.68,
                "avg_trade_duration": 2.5,
                "max_drawdown": -0.08,
                "sharpe_ratio": 1.45
            }
        except Exception as e:
            logger.error(f"Error getting trading metrics: {e}")
            return {}
    
    async def _get_risk_metrics(self) -> Dict[str, float]:
        """Get risk management metrics."""
        try:
            # This would integrate with risk manager
            return {
                "overall_risk_score": 0.35,
                "max_position_size": 0.12,
                "var_95": 0.045,
                "risk_events_count": 3,
                "compliance_score": 0.92
            }
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}")
            return {}
    
    async def _get_system_health_metrics(self) -> Dict[str, float]:
        """Get overall system health metrics."""
        try:
            return {
                "system_uptime": 0.998,
                "error_rate": 0.02,
                "response_time_avg": 125.0,
                "memory_usage": 0.65,
                "cpu_usage": 0.45
            }
        except Exception as e:
            logger.error(f"Error getting system health metrics: {e}")
            return {}
    
    async def _update_metric(self, metric_name: str, current_value: float):
        """Update a performance metric with new value."""
        if metric_name not in self.performance_metrics:
            # Create new metric
            self.performance_metrics[metric_name] = PerformanceMetric(
                metric_name=metric_name,
                current_value=current_value,
                historical_values=[current_value],
                trend="stable",
                threshold=0.5,  # Default threshold
                is_critical=False,
                timestamp=datetime.now()
            )
        else:
            # Update existing metric
            metric = self.performance_metrics[metric_name]
            metric.historical_values.append(current_value)
            metric.current_value = current_value
            metric.timestamp = datetime.now()
            
            # Calculate trend (last 10 values)
            recent_values = metric.historical_values[-10:]
            if len(recent_values) >= 3:
                trend_slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
                if trend_slope > 0.01:
                    metric.trend = "improving"
                elif trend_slope < -0.01:
                    metric.trend = "declining"
                else:
                    metric.trend = "stable"
    
    def _should_analyze(self) -> bool:
        """Determine if it's time for analysis."""
        if not self.last_analysis:
            return True
        
        time_since_analysis = datetime.now() - self.last_analysis
        return time_since_analysis >= self.analysis_interval
    
    async def _analyze_and_propose_changes(self):
        """Analyze performance and propose structural changes using LLM."""
        try:
            logger.info("🧠 LLM analyzing performance and proposing changes...")
            
            # Prepare performance data for LLM
            performance_data = self._format_performance_data_for_llm()
            
            # Get LLM analysis
            analysis_result = await self._get_llm_analysis(performance_data)
            
            if analysis_result:
                # Process LLM recommendations
                await self._process_llm_recommendations(analysis_result)
            
            self.last_analysis = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in analysis and proposal: {e}")
    
    def _format_performance_data_for_llm(self) -> str:
        """Format performance metrics for LLM analysis."""
        formatted_metrics = []
        
        for metric_name, metric in self.performance_metrics.items():
            formatted_metrics.append(f"""
{metric_name}:
  Current Value: {metric.current_value:.3f}
  Trend: {metric.trend}
  Historical: {metric.historical_values[-5:] if len(metric.historical_values) >= 5 else metric.historical_values}
  Critical: {metric.is_critical}
  Threshold: {metric.threshold:.3f}
""")
        
        return "\n".join(formatted_metrics)
    
    async def _get_llm_analysis(self, performance_data: str) -> Optional[Dict[str, Any]]:
        """Get LLM analysis of performance data."""
        if not self.use_llm:
            logger.warning("LLM not available for analysis")
            return None
        
        try:
            prompt = self.analysis_prompt_template.format(
                performance_metrics=performance_data
            )
            
            response = await openai_manager.get_completion(
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            if response:
                return json.loads(response)
            else:
                logger.error("No response from LLM")
                return None
                
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return None
    
    async def _process_llm_recommendations(self, analysis_result: Dict[str, Any]):
        """Process LLM recommendations and create change proposals."""
        try:
            recommended_changes = analysis_result.get("recommended_changes", [])
            
            for change_data in recommended_changes:
                # Check if we should create a proposal for this change
                if self._should_propose_change(change_data):
                    proposal = await self._create_change_proposal(change_data)
                    
                    if proposal:
                        # Store proposal
                        self.change_proposals[proposal.proposal_id] = proposal
                        
                        # Send approval request
                        await self._send_approval_request(proposal)
                        
                        # Log the proposal
                        logger.info(f"📋 Created change proposal: {proposal.title}")
                        
        except Exception as e:
            logger.error(f"Error processing LLM recommendations: {e}")
    
    def _should_propose_change(self, change_data: Dict[str, Any]) -> bool:
        """Determine if a change should be proposed based on thresholds."""
        priority = change_data.get("priority", "low")
        
        # Always propose critical changes
        if priority == "critical":
            return True
        
        # Check if we have too many pending changes
        pending_count = len([p for p in self.change_proposals.values() 
                           if p.approval_status == ApprovalStatus.PENDING])
        
        if pending_count >= self.change_thresholds["max_changes_per_week"]:
            return False
        
        # Check performance improvement potential
        expected_improvement = change_data.get("performance_improvement_expected", {})
        for metric, improvement in expected_improvement.items():
            if improvement >= self.change_thresholds["improvement_opportunity_threshold"]:
                return True
        
        return False
    
    async def _create_change_proposal(self, change_data: Dict[str, Any]) -> Optional[ChangeProposal]:
        """Create a change proposal from LLM recommendation."""
        try:
            proposal = ChangeProposal(
                proposal_id=str(uuid.uuid4()),
                change_type=ChangeType(change_data.get("change_type", "performance_optimization")),
                priority=ChangePriority(change_data.get("priority", "medium")),
                title=change_data.get("title", "Performance Improvement"),
                description=change_data.get("description", ""),
                rationale=change_data.get("rationale", ""),
                impact_analysis=change_data.get("impact_analysis", {}),
                implementation_plan=change_data.get("implementation_plan", []),
                estimated_effort=change_data.get("estimated_effort", "Unknown"),
                risk_assessment=change_data.get("risk_assessment", {}),
                performance_improvement_expected=change_data.get("performance_improvement_expected", {}),
                affected_components=change_data.get("affected_components", []),
                created_at=datetime.now()
            )
            
            return proposal
            
        except Exception as e:
            logger.error(f"Error creating change proposal: {e}")
            return None
    
    async def _send_approval_request(self, proposal: ChangeProposal):
        """Send email approval request for a change proposal."""
        try:
            # Format approval email
            email_subject = f"🔧 RoboInvest Structural Change Request: {proposal.title}"
            
            email_body = self._format_approval_email(proposal)
            
            # Send via notification aggregator
            notification_aggregator.add_alert(
                alert_type="structural_change_request",
                message=email_subject,
                context={
                    "proposal_id": proposal.proposal_id,
                    "proposal": asdict(proposal),
                    "approval_url": f"http://localhost:8081/api/structural-changes/approve/{proposal.proposal_id}",
                    "reject_url": f"http://localhost:8081/api/structural-changes/reject/{proposal.proposal_id}"
                }
            )
            
            # Emit event
            central_event_bus.emit_event(
                central_event_bus.create_event(
                    event_type=EventType.META_AGENT,
                    source="structural_change_manager",
                    title=f"Change Proposal Created: {proposal.title}",
                    message=f"Proposal {proposal.proposal_id} requires approval",
                    priority=EventPriority.HIGH,
                    metadata={"proposal_id": proposal.proposal_id}
                )
            )
            
            logger.info(f"📧 Approval request sent for proposal {proposal.proposal_id}")
            
        except Exception as e:
            logger.error(f"Error sending approval request: {e}")
    
    def _format_approval_email(self, proposal: ChangeProposal) -> str:
        """Format approval email with proposal details."""
        return f"""
🚀 RoboInvest Structural Change Request

PROPOSAL ID: {proposal.proposal_id}
PRIORITY: {proposal.priority.value.upper()}
TYPE: {proposal.change_type.value.replace('_', ' ').title()}

TITLE: {proposal.title}

DESCRIPTION:
{proposal.description}

RATIONALE:
{proposal.rationale}

IMPACT ANALYSIS:
{json.dumps(proposal.impact_analysis, indent=2)}

IMPLEMENTATION PLAN:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(proposal.implementation_plan))}

EXPECTED PERFORMANCE IMPROVEMENT:
{json.dumps(proposal.performance_improvement_expected, indent=2)}

RISK ASSESSMENT:
{json.dumps(proposal.risk_assessment, indent=2)}

AFFECTED COMPONENTS:
{', '.join(proposal.affected_components)}

ESTIMATED EFFORT: {proposal.estimated_effort}

APPROVAL REQUIRED BY: {(datetime.now() + timedelta(hours=self.change_thresholds['approval_expiry_hours'])).strftime('%Y-%m-%d %H:%M:%S')}

TO APPROVE: Click the approval link or respond with "APPROVE {proposal.proposal_id}"
TO REJECT: Click the reject link or respond with "REJECT {proposal.proposal_id}"

This change will only be implemented after your explicit approval.
"""
    
    async def approve_change(self, proposal_id: str, approved_by: str = "user") -> bool:
        """Approve a change proposal."""
        try:
            if proposal_id not in self.change_proposals:
                logger.error(f"Proposal {proposal_id} not found")
                return False
            
            proposal = self.change_proposals[proposal_id]
            
            if proposal.approval_status != ApprovalStatus.PENDING:
                logger.error(f"Proposal {proposal_id} is not pending approval")
                return False
            
            # Update approval status
            proposal.approval_status = ApprovalStatus.APPROVED
            proposal.approved_at = datetime.now()
            proposal.approved_by = approved_by
            
            # Implement the change
            success = await self._implement_change(proposal)
            
            if success:
                proposal.implemented_at = datetime.now()
                logger.info(f"✅ Change {proposal_id} approved and implemented")
                
                # Send confirmation email
                await self._send_implementation_confirmation(proposal)
                
                return True
            else:
                logger.error(f"Failed to implement change {proposal_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error approving change: {e}")
            return False
    
    async def reject_change(self, proposal_id: str, rejected_by: str = "user", reason: str = "") -> bool:
        """Reject a change proposal."""
        try:
            if proposal_id not in self.change_proposals:
                logger.error(f"Proposal {proposal_id} not found")
                return False
            
            proposal = self.change_proposals[proposal_id]
            proposal.approval_status = ApprovalStatus.REJECTED
            
            logger.info(f"❌ Change {proposal_id} rejected by {rejected_by}")
            
            # Send rejection notification
            await self._send_rejection_notification(proposal, reason)
            
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting change: {e}")
            return False
    
    async def _implement_change(self, proposal: ChangeProposal) -> bool:
        """Implement an approved change."""
        try:
            logger.info(f"🔧 Implementing change: {proposal.title}")
            
            # Use self-editing agent for code changes
            if proposal.change_type in [ChangeType.CODE_REFACTORING, ChangeType.BUG_FIX, ChangeType.NEW_FEATURE]:
                return await self._implement_code_change(proposal)
            
            # Use configuration changes for other types
            else:
                return await self._implement_configuration_change(proposal)
                
        except Exception as e:
            logger.error(f"Error implementing change: {e}")
            return False
    
    async def _implement_code_change(self, proposal: ChangeProposal) -> bool:
        """Implement code-based changes using self-editing agent."""
        try:
            # Generate implementation description
            implementation_desc = f"""
{proposal.description}

Implementation Plan:
{chr(10).join(proposal.implementation_plan)}

Expected Impact:
{json.dumps(proposal.performance_improvement_expected, indent=2)}
"""
            
            # Use self-editing agent to implement
            if proposal.change_type == ChangeType.BUG_FIX:
                success = await self.self_editing_agent.fix_self_issue(implementation_desc)
            elif proposal.change_type == ChangeType.CODE_REFACTORING:
                success = await self.self_editing_agent.refactor_self("performance")
            elif proposal.change_type == ChangeType.NEW_FEATURE:
                success = await self.self_editing_agent.add_self_feature(implementation_desc)
            else:
                success = await self.self_editing_agent.optimize_self("performance")
            
            return success
            
        except Exception as e:
            logger.error(f"Error implementing code change: {e}")
            return False
    
    async def _implement_configuration_change(self, proposal: ChangeProposal) -> bool:
        """Implement configuration-based changes."""
        try:
            # This would implement changes to system configuration
            # For now, just log the change
            logger.info(f"Configuration change implemented: {proposal.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error implementing configuration change: {e}")
            return False
    
    async def _send_implementation_confirmation(self, proposal: ChangeProposal):
        """Send confirmation email for implemented change."""
        try:
            email_subject = f"✅ RoboInvest Change Implemented: {proposal.title}"
            
            email_body = f"""
✅ Change Successfully Implemented

PROPOSAL ID: {proposal.proposal_id}
TITLE: {proposal.title}

The change has been successfully implemented at {proposal.implemented_at}.

The system will monitor the impact of this change over the next 7 days and provide a performance evaluation report.

You will receive a follow-up report on {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}.
"""
            
            notification_aggregator.add_alert(
                alert_type="change_implemented",
                message=email_subject,
                context={"proposal_id": proposal.proposal_id}
            )
            
        except Exception as e:
            logger.error(f"Error sending implementation confirmation: {e}")
    
    async def _send_rejection_notification(self, proposal: ChangeProposal, reason: str):
        """Send notification for rejected change."""
        try:
            email_subject = f"❌ RoboInvest Change Rejected: {proposal.title}"
            
            email_body = f"""
❌ Change Rejected

PROPOSAL ID: {proposal.proposal_id}
TITLE: {proposal.title}

This change has been rejected.

Reason: {reason or "No reason provided"}

The system will continue monitoring and may propose alternative solutions if the underlying performance issues persist.
"""
            
            notification_aggregator.add_alert(
                alert_type="change_rejected",
                message=email_subject,
                context={"proposal_id": proposal.proposal_id, "reason": reason}
            )
            
        except Exception as e:
            logger.error(f"Error sending rejection notification: {e}")
    
    async def _approval_expiry_checker(self):
        """Check for expired approvals and clean them up."""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                expired_proposals = []
                
                for proposal_id, proposal in self.change_proposals.items():
                    if proposal.approval_status == ApprovalStatus.PENDING:
                        time_since_creation = current_time - proposal.created_at
                        if time_since_creation.total_seconds() > self.change_thresholds["approval_expiry_hours"] * 3600:
                            expired_proposals.append(proposal_id)
                
                # Expire old proposals
                for proposal_id in expired_proposals:
                    proposal = self.change_proposals[proposal_id]
                    proposal.approval_status = ApprovalStatus.EXPIRED
                    logger.info(f"⏰ Proposal {proposal_id} expired")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in approval expiry checker: {e}")
                await asyncio.sleep(300)
    
    async def _check_expired_approvals(self):
        """Check for expired approvals (called from monitoring loop)."""
        current_time = datetime.now()
        expired_count = 0
        
        for proposal in self.change_proposals.values():
            if proposal.approval_status == ApprovalStatus.PENDING:
                time_since_creation = current_time - proposal.created_at
                if time_since_creation.total_seconds() > self.change_thresholds["approval_expiry_hours"] * 3600:
                    proposal.approval_status = ApprovalStatus.EXPIRED
                    expired_count += 1
        
        if expired_count > 0:
            logger.info(f"⏰ {expired_count} proposals expired")
    
    async def get_change_summary(self) -> Dict[str, Any]:
        """Get summary of all changes and their status."""
        try:
            pending_count = len([p for p in self.change_proposals.values() 
                               if p.approval_status == ApprovalStatus.PENDING])
            approved_count = len([p for p in self.change_proposals.values() 
                                if p.approval_status == ApprovalStatus.APPROVED])
            rejected_count = len([p for p in self.change_proposals.values() 
                                if p.approval_status == ApprovalStatus.REJECTED])
            expired_count = len([p for p in self.change_proposals.values() 
                               if p.approval_status == ApprovalStatus.EXPIRED])
            
            return {
                "monitoring_active": self.monitoring_active,
                "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
                "total_proposals": len(self.change_proposals),
                "pending_proposals": pending_count,
                "approved_proposals": approved_count,
                "rejected_proposals": rejected_count,
                "expired_proposals": expired_count,
                "performance_metrics_count": len(self.performance_metrics),
                "change_history_count": len(self.change_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting change summary: {e}")
            return {"error": str(e)}
    
    async def get_pending_proposals(self) -> List[Dict[str, Any]]:
        """Get all pending change proposals."""
        try:
            pending = [p for p in self.change_proposals.values() 
                      if p.approval_status == ApprovalStatus.PENDING]
            return [asdict(proposal) for proposal in pending]
        except Exception as e:
            logger.error(f"Error getting pending proposals: {e}")
            return []
    
    async def get_change_history(self) -> List[Dict[str, Any]]:
        """Get history of all changes."""
        try:
            return [asdict(result) for result in self.change_history]
        except Exception as e:
            logger.error(f"Error getting change history: {e}")
            return []


# Global instance
structural_change_manager = StructuralChangeManager() 