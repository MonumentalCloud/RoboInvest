#!/usr/bin/env python3
"""
Enhanced Meta Agent API Endpoints
Provides REST API endpoints for monitoring and controlling the enhanced meta agent.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from agents.enhanced_meta_agent import enhanced_meta_agent
from utils.logger import logger

router = APIRouter(prefix="/api/meta-agent", tags=["Enhanced Meta Agent"])

@router.get("/status")
async def get_meta_agent_status():
    """Get the current status of the enhanced meta agent."""
    try:
        status = enhanced_meta_agent.get_system_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting meta agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_system_metrics(hours: int = 24):
    """Get system metrics for the specified time period."""
    try:
        # Get metrics from database
        import sqlite3
        db_path = Path("meta_agent_data/enhanced_meta_agent.db")
        
        if not db_path.exists():
            return {
                "status": "success",
                "data": [],
                "message": "No metrics data available yet"
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get metrics from last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT timestamp, total_agents, active_agents, failed_agents, 
                   avg_response_time, avg_success_rate, system_cpu_usage, 
                   system_memory_usage, total_errors, total_insights, 
                   research_cycles_completed, performance_score
            FROM system_metrics 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff_time.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append({
                "timestamp": row[0],
                "total_agents": row[1],
                "active_agents": row[2],
                "failed_agents": row[3],
                "avg_response_time": row[4],
                "avg_success_rate": row[5],
                "system_cpu_usage": row[6],
                "system_memory_usage": row[7],
                "total_errors": row[8],
                "total_insights": row[9],
                "research_cycles_completed": row[10],
                "performance_score": row[11]
            })
        
        return {
            "status": "success",
            "data": metrics,
            "count": len(metrics),
            "time_period_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/improvements")
async def get_system_improvements(status: Optional[str] = None):
    """Get system improvement suggestions."""
    try:
        import sqlite3
        db_path = Path("meta_agent_data/enhanced_meta_agent.db")
        
        if not db_path.exists():
            return {
                "status": "success",
                "data": [],
                "message": "No improvements data available yet"
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT id, type, priority, title, description, affected_components,
                       estimated_impact, implementation_plan, confidence, created_at, 
                       status, assigned_agent, completion_time
                FROM system_improvements 
                WHERE status = ?
                ORDER BY created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT id, type, priority, title, description, affected_components,
                       estimated_impact, implementation_plan, confidence, created_at, 
                       status, assigned_agent, completion_time
                FROM system_improvements 
                ORDER BY created_at DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        improvements = []
        for row in rows:
            improvements.append({
                "id": row[0],
                "type": row[1],
                "priority": row[2],
                "title": row[3],
                "description": row[4],
                "affected_components": json.loads(row[5]) if row[5] else [],
                "estimated_impact": json.loads(row[6]) if row[6] else {},
                "implementation_plan": json.loads(row[7]) if row[7] else {},
                "confidence": row[8],
                "created_at": row[9],
                "status": row[10],
                "assigned_agent": row[11],
                "completion_time": row[12]
            })
        
        return {
            "status": "success",
            "data": improvements,
            "count": len(improvements),
            "filtered_by_status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting system improvements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improvements/{improvement_id}/approve")
async def approve_improvement(improvement_id: str):
    """Approve a system improvement for implementation."""
    try:
        # Find the improvement
        improvement = None
        for imp in enhanced_meta_agent.system_improvements:
            if imp.id == improvement_id:
                improvement = imp
                break
        
        if not improvement:
            raise HTTPException(status_code=404, detail="Improvement not found")
        
        if improvement.status != "pending":
            raise HTTPException(status_code=400, detail=f"Improvement is not pending (current status: {improvement.status})")
        
        # Approve the improvement
        improvement.status = "approved"
        
        # Update database
        import sqlite3
        db_path = Path("meta_agent_data/enhanced_meta_agent.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE system_improvements 
            SET status = ?
            WHERE id = ?
        ''', ("approved", improvement_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Approved improvement: {improvement.title}")
        
        return {
            "status": "success",
            "message": f"Improvement '{improvement.title}' approved for implementation",
            "improvement_id": improvement_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving improvement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improvements/{improvement_id}/reject")
async def reject_improvement(improvement_id: str, reason: str = "No reason provided"):
    """Reject a system improvement."""
    try:
        # Find the improvement
        improvement = None
        for imp in enhanced_meta_agent.system_improvements:
            if imp.id == improvement_id:
                improvement = imp
                break
        
        if not improvement:
            raise HTTPException(status_code=404, detail="Improvement not found")
        
        if improvement.status != "pending":
            raise HTTPException(status_code=400, detail=f"Improvement is not pending (current status: {improvement.status})")
        
        # Reject the improvement
        improvement.status = "rejected"
        
        # Update database
        import sqlite3
        db_path = Path("meta_agent_data/enhanced_meta_agent.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE system_improvements 
            SET status = ?
            WHERE id = ?
        ''', ("rejected", improvement_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"❌ Rejected improvement: {improvement.title} (Reason: {reason})")
        
        return {
            "status": "success",
            "message": f"Improvement '{improvement.title}' rejected",
            "improvement_id": improvement_id,
            "reason": reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting improvement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/control/start")
async def start_meta_agent():
    """Start the enhanced meta agent monitoring."""
    try:
        if enhanced_meta_agent.active_monitoring:
            return {
                "status": "success",
                "message": "Enhanced meta agent is already running"
            }
        
        # Start monitoring in background
        asyncio.create_task(enhanced_meta_agent.start_continuous_monitoring())
        
        return {
            "status": "success",
            "message": "Enhanced meta agent monitoring started"
        }
        
    except Exception as e:
        logger.error(f"Error starting meta agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/control/stop")
async def stop_meta_agent():
    """Stop the enhanced meta agent monitoring."""
    try:
        if not enhanced_meta_agent.active_monitoring:
            return {
                "status": "success",
                "message": "Enhanced meta agent is not running"
            }
        
        enhanced_meta_agent.stop_monitoring()
        
        return {
            "status": "success",
            "message": "Enhanced meta agent monitoring stopped"
        }
        
    except Exception as e:
        logger.error(f"Error stopping meta agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_system_reports():
    """Get available system reports."""
    try:
        reports_dir = Path("meta_agent_data/system_reports")
        
        if not reports_dir.exists():
            return {
                "status": "success",
                "data": [],
                "message": "No reports available yet"
            }
        
        reports = []
        for report_file in reports_dir.glob("system_report_*.json"):
            try:
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                
                reports.append({
                    "filename": report_file.name,
                    "timestamp": report_data.get("timestamp", ""),
                    "performance_score": report_data.get("system_health", {}).get("performance_score", 0),
                    "active_agents": report_data.get("system_health", {}).get("active_agents", 0),
                    "failed_agents": report_data.get("system_health", {}).get("failed_agents", 0)
                })
            except Exception as e:
                logger.error(f"Error reading report {report_file}: {e}")
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "status": "success",
            "data": reports,
            "count": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Error getting system reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{filename}")
async def get_system_report(filename: str):
    """Get a specific system report."""
    try:
        report_path = Path("meta_agent_data/system_reports") / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        return {
            "status": "success",
            "data": report_data,
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-performance")
async def get_agent_performance(agent_name: Optional[str] = None, hours: int = 24):
    """Get agent performance history."""
    try:
        import sqlite3
        db_path = Path("meta_agent_data/enhanced_meta_agent.db")
        
        if not db_path.exists():
            return {
                "status": "success",
                "data": [],
                "message": "No performance data available yet"
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if agent_name:
            cursor.execute('''
                SELECT agent_name, timestamp, response_time, success_rate, 
                       error_count, insights_generated, memory_usage, cpu_usage
                FROM agent_performance_history 
                WHERE agent_name = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (agent_name, cutoff_time.isoformat()))
        else:
            cursor.execute('''
                SELECT agent_name, timestamp, response_time, success_rate, 
                       error_count, insights_generated, memory_usage, cpu_usage
                FROM agent_performance_history 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        performance_data = []
        for row in rows:
            performance_data.append({
                "agent_name": row[0],
                "timestamp": row[1],
                "response_time": row[2],
                "success_rate": row[3],
                "error_count": row[4],
                "insights_generated": row[5],
                "memory_usage": row[6],
                "cpu_usage": row[7]
            })
        
        return {
            "status": "success",
            "data": performance_data,
            "count": len(performance_data),
            "filtered_by_agent": agent_name,
            "time_period_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-analysis")
async def trigger_system_analysis():
    """Manually trigger a system analysis."""
    try:
        # This would trigger an immediate analysis
        # For now, we'll just return a success message
        logger.info("🔍 Manual system analysis triggered")
        
        return {
            "status": "success",
            "message": "System analysis triggered",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering system analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_meta_agent_health():
    """Get detailed health information about the meta agent."""
    try:
        health_info = {
            "meta_agent_active": enhanced_meta_agent.active_monitoring,
            "monitoring_interval_seconds": enhanced_meta_agent.monitoring_interval,
            "metrics_retention_hours": enhanced_meta_agent.metrics_retention_hours,
            "improvement_threshold": enhanced_meta_agent.improvement_threshold,
            "performance_thresholds": enhanced_meta_agent.performance_thresholds,
            "total_improvements": len(enhanced_meta_agent.system_improvements),
            "metrics_history_count": len(enhanced_meta_agent.system_metrics_history),
            "improvement_queue_count": len(enhanced_meta_agent.improvement_queue),
            "database_path": str(enhanced_meta_agent.db_path),
            "database_exists": enhanced_meta_agent.db_path.exists(),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "data": health_info
        }
        
    except Exception as e:
        logger.error(f"Error getting meta agent health: {e}")
        raise HTTPException(status_code=500, detail=str(e))