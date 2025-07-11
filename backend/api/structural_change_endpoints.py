#!/usr/bin/env python3
"""
API Endpoints for Structural Change Manager
Handles approval requests, status queries, and change management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from agents.structural_change_manager import structural_change_manager
from core.central_event_bus import central_event_bus, EventType, EventPriority, create_event
from utils.logger import logger

router = APIRouter(prefix="/api/structural-changes", tags=["structural-changes"])


@router.get("/status")
async def get_structural_change_status():
    """Get overall status of structural change management system."""
    try:
        summary = await structural_change_manager.get_change_summary()
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting structural change status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/pending")
async def get_pending_proposals():
    """Get all pending change proposals."""
    try:
        proposals = await structural_change_manager.get_pending_proposals()
        return {
            "status": "success",
            "data": proposals,
            "count": len(proposals),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting pending proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}")
async def get_proposal_details(proposal_id: str):
    """Get details of a specific change proposal."""
    try:
        if proposal_id not in structural_change_manager.change_proposals:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        proposal = structural_change_manager.change_proposals[proposal_id]
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal.proposal_id,
                "change_type": proposal.change_type.value,
                "priority": proposal.priority.value,
                "title": proposal.title,
                "description": proposal.description,
                "rationale": proposal.rationale,
                "impact_analysis": proposal.impact_analysis,
                "implementation_plan": proposal.implementation_plan,
                "estimated_effort": proposal.estimated_effort,
                "risk_assessment": proposal.risk_assessment,
                "performance_improvement_expected": proposal.performance_improvement_expected,
                "affected_components": proposal.affected_components,
                "created_at": proposal.created_at.isoformat(),
                "approval_status": proposal.approval_status.value,
                "approved_at": proposal.approved_at.isoformat() if proposal.approved_at else None,
                "approved_by": proposal.approved_by,
                "implemented_at": proposal.implemented_at.isoformat() if proposal.implemented_at else None
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting proposal details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve/{proposal_id}")
async def approve_change(proposal_id: str, background_tasks: BackgroundTasks):
    """Approve a change proposal."""
    try:
        # Add approval to background tasks
        background_tasks.add_task(structural_change_manager.approve_change, proposal_id, "api_user")
        
        # Emit event
        event = create_event(
            event_type=EventType.META_AGENT,
            source="structural_change_api",
            title=f"Change Approved: {proposal_id}",
            message=f"Proposal {proposal_id} approved via API",
            priority=EventPriority.HIGH,
            metadata={"proposal_id": proposal_id, "approved_by": "api_user"}
        )
        central_event_bus.emit_event(event)
        
        return {
            "status": "success",
            "message": f"Proposal {proposal_id} approved and queued for implementation",
            "proposal_id": proposal_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error approving change: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject/{proposal_id}")
async def reject_change(proposal_id: str, reason: Optional[str] = None, background_tasks: BackgroundTasks = None):
    """Reject a change proposal."""
    try:
        # Add rejection to background tasks
        if background_tasks:
            background_tasks.add_task(structural_change_manager.reject_change, proposal_id, "api_user", reason or "")
        else:
            await structural_change_manager.reject_change(proposal_id, "api_user", reason or "")
        
        # Emit event
        event = create_event(
            event_type=EventType.META_AGENT,
            source="structural_change_api",
            title=f"Change Rejected: {proposal_id}",
            message=f"Proposal {proposal_id} rejected via API",
            priority=EventPriority.MEDIUM,
            metadata={"proposal_id": proposal_id, "rejected_by": "api_user", "reason": reason}
        )
        central_event_bus.emit_event(event)
        
        return {
            "status": "success",
            "message": f"Proposal {proposal_id} rejected",
            "proposal_id": proposal_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error rejecting change: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_change_history():
    """Get history of all changes."""
    try:
        history = await structural_change_manager.get_change_history()
        return {
            "status": "success",
            "data": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting change history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-monitoring")
async def start_structural_change_monitoring():
    """Start the structural change monitoring system."""
    try:
        await structural_change_manager.start_monitoring()
        
        # Emit event
        event = create_event(
            event_type=EventType.META_AGENT,
            source="structural_change_api",
            title="Structural Change Monitoring Started",
            message="Continuous performance monitoring and change proposal system activated",
            priority=EventPriority.HIGH
        )
        central_event_bus.emit_event(event)
        
        return {
            "status": "success",
            "message": "Structural change monitoring started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-monitoring")
async def stop_structural_change_monitoring():
    """Stop the structural change monitoring system."""
    try:
        await structural_change_manager.stop_monitoring()
        
        # Emit event
        event = create_event(
            event_type=EventType.META_AGENT,
            source="structural_change_api",
            title="Structural Change Monitoring Stopped",
            message="Continuous performance monitoring and change proposal system deactivated",
            priority=EventPriority.MEDIUM
        )
        central_event_bus.emit_event(event)
        
        return {
            "status": "success",
            "message": "Structural change monitoring stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-metrics")
async def get_performance_metrics():
    """Get current performance metrics being monitored."""
    try:
        metrics = {}
        for metric_name, metric in structural_change_manager.performance_metrics.items():
            metrics[metric_name] = {
                "current_value": metric.current_value,
                "trend": metric.trend,
                "historical_values": metric.historical_values[-10:],  # Last 10 values
                "threshold": metric.threshold,
                "is_critical": metric.is_critical,
                "timestamp": metric.timestamp.isoformat()
            }
        
        return {
            "status": "success",
            "data": metrics,
            "count": len(metrics),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/force-analysis")
async def force_performance_analysis():
    """Force an immediate performance analysis and change proposal generation."""
    try:
        # Force analysis
        await structural_change_manager._analyze_and_propose_changes()
        
        # Emit event
        event = create_event(
            event_type=EventType.META_AGENT,
            source="structural_change_api",
            title="Forced Performance Analysis",
            message="Manual performance analysis triggered",
            priority=EventPriority.MEDIUM
        )
        central_event_bus.emit_event(event)
        
        return {
            "status": "success",
            "message": "Performance analysis completed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error forcing analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_structural_change_config():
    """Get current configuration of the structural change manager."""
    try:
        config = {
            "change_thresholds": structural_change_manager.change_thresholds,
            "analysis_interval_hours": structural_change_manager.analysis_interval.total_seconds() / 3600,
            "use_llm": structural_change_manager.use_llm,
            "monitoring_active": structural_change_manager.monitoring_active
        }
        
        return {
            "status": "success",
            "data": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/update")
async def update_structural_change_config(config_update: Dict[str, Any]):
    """Update configuration of the structural change manager."""
    try:
        # Update change thresholds
        if "change_thresholds" in config_update:
            structural_change_manager.change_thresholds.update(config_update["change_thresholds"])
        
        # Update analysis interval
        if "analysis_interval_hours" in config_update:
            hours = config_update["analysis_interval_hours"]
            structural_change_manager.analysis_interval = timedelta(hours=hours)
        
        # Emit event
        event = create_event(
            event_type=EventType.META_AGENT,
            source="structural_change_api",
            title="Configuration Updated",
            message="Structural change manager configuration modified",
            priority=EventPriority.MEDIUM,
            metadata={"config_update": config_update}
        )
        central_event_bus.emit_event(event)
        
        return {
            "status": "success",
            "message": "Configuration updated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 