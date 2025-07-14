#!/usr/bin/env python3
"""
Agent Monitoring System
Real-time monitoring and reporting system for all agents in the RoboInvest ecosystem.

This system:
1. Collects real-time metrics from all running agents
2. Tracks agent performance, errors, and outputs
3. Provides centralized monitoring for the meta-agent
4. Stores historical data for trend analysis
5. Enables real-time alerting and health checks
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import queue
import psutil
import os

from utils.logger import logger

class MetricType(Enum):
    PERFORMANCE = "performance"
    ERROR = "error"
    OUTPUT = "output"
    HEALTH = "health"
    RESOURCE = "resource"

@dataclass
class AgentMetric:
    agent_name: str
    metric_type: MetricType
    timestamp: datetime
    value: Any
    metadata: Dict[str, Any]

@dataclass
class AgentHeartbeat:
    agent_name: str
    timestamp: datetime
    status: str  # "active", "idle", "error", "offline"
    last_activity: datetime
    memory_usage: float
    cpu_usage: float
    custom_metrics: Dict[str, Any]

@dataclass
class AgentError:
    agent_name: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    severity: str  # "critical", "high", "medium", "low"

class AgentMonitoringSystem:
    """
    Centralized monitoring system for all agents.
    
    Features:
    - Real-time metric collection
    - Agent heartbeat monitoring
    - Error tracking and alerting
    - Performance analytics
    - Historical data storage
    - Resource usage monitoring
    """
    
    def __init__(self, db_path: str = "agent_monitoring.db"):
        self.db_path = db_path
        self.metrics_queue = queue.Queue()
        self.heartbeats = {}
        self.errors = []
        self.performance_data = {}
        
        # Initialize database
        self._init_database()
        
        # Start monitoring threads
        self.monitoring_active = True
        self.metrics_thread = threading.Thread(target=self._metrics_processor, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.resource_thread = threading.Thread(target=self._resource_monitor, daemon=True)
        
        self.metrics_thread.start()
        self.heartbeat_thread.start()
        self.resource_thread.start()
        
        logger.info("🔍 Agent Monitoring System initialized")
    
    def _init_database(self):
        """Initialize SQLite database for storing metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_heartbeats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                memory_usage REAL,
                cpu_usage REAL,
                custom_metrics TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT,
                severity TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_name ON agent_metrics(agent_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_heartbeats_agent_name ON agent_heartbeats(agent_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_errors_agent_name ON agent_errors(agent_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_errors_severity ON agent_errors(severity)')
        
        conn.commit()
        conn.close()
    
    def register_agent(self, agent_name: str, agent_info: Dict[str, Any]):
        """Register an agent for monitoring."""
        self.heartbeats[agent_name] = {
            "info": agent_info,
            "registered_at": datetime.now(),
            "last_heartbeat": datetime.now(),
            "status": "active",
            "error_count": 0,
            "success_count": 0
        }
        logger.info(f"📝 Registered agent for monitoring: {agent_name}")
    
    def record_metric(self, agent_name: str, metric_type: MetricType, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric for an agent."""
        metric = AgentMetric(
            agent_name=agent_name,
            metric_type=metric_type,
            timestamp=datetime.now(),
            value=value,
            metadata=metadata or {}
        )
        
        self.metrics_queue.put(metric)
    
    def record_error(self, agent_name: str, error_type: str, error_message: str, 
                    stack_trace: str = "", context: Optional[Dict[str, Any]] = None, severity: str = "medium"):
        """Record an error for an agent."""
        error = AgentError(
            agent_name=agent_name,
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {},
            severity=severity
        )
        
        self.errors.append(error)
        
        # Update agent error count
        if agent_name in self.heartbeats:
            self.heartbeats[agent_name]["error_count"] += 1
        
        # Store in database
        self._store_error(error)
        
        logger.error(f"🚨 Agent {agent_name} error: {error_message}")
    
    def record_success(self, agent_name: str, operation: str, duration: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record a successful operation for an agent."""
        self.record_metric(
            agent_name=agent_name,
            metric_type=MetricType.PERFORMANCE,
            value={
                "operation": operation,
                "status": "success",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            },
            metadata=metadata
        )
        
        # Update agent success count
        if agent_name in self.heartbeats:
            self.heartbeats[agent_name]["success_count"] += 1
    
    def record_output(self, agent_name: str, output_type: str, output_data: Any, metadata: Dict[str, Any] = None):
        """Record an output from an agent."""
        self.record_metric(
            agent_name=agent_name,
            metric_type=MetricType.OUTPUT,
            value={
                "type": output_type,
                "data": output_data,
                "timestamp": datetime.now().isoformat()
            },
            metadata=metadata
        )
    
    def update_heartbeat(self, agent_name: str, status: str = "active", custom_metrics: Dict[str, Any] = None):
        """Update agent heartbeat."""
        if agent_name not in self.heartbeats:
            logger.warning(f"Agent {agent_name} not registered for monitoring")
            return
        
        # Get process resource usage if available
        memory_usage = 0.0
        cpu_usage = 0.0
        
        try:
            # Try to get process info for the agent
            process = psutil.Process()
            memory_usage = process.memory_percent()
            cpu_usage = process.cpu_percent()
        except:
            pass
        
        heartbeat = AgentHeartbeat(
            agent_name=agent_name,
            timestamp=datetime.now(),
            status=status,
            last_activity=datetime.now(),
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            custom_metrics=custom_metrics or {}
        )
        
        self.heartbeats[agent_name]["last_heartbeat"] = datetime.now()
        self.heartbeats[agent_name]["status"] = status
        
        # Store in database
        self._store_heartbeat(heartbeat)
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get current status of an agent."""
        if agent_name not in self.heartbeats:
            return None
        
        agent_data = self.heartbeats[agent_name]
        last_heartbeat = agent_data["last_heartbeat"]
        
        # Calculate time since last heartbeat
        time_since_heartbeat = datetime.now() - last_heartbeat
        
        # Determine health status
        if time_since_heartbeat > timedelta(minutes=5):
            health = "offline"
        elif agent_data["error_count"] > 10:
            health = "failing"
        elif agent_data["error_count"] > 5:
            health = "degraded"
        else:
            health = "healthy"
        
        # Calculate success rate
        total_operations = agent_data["success_count"] + agent_data["error_count"]
        success_rate = agent_data["success_count"] / max(total_operations, 1)
        
        # Get recent metrics
        recent_metrics = self._get_recent_metrics(agent_name, hours=1)
        
        return {
            "name": agent_name,
            "health": health,
            "status": agent_data["status"],
            "last_heartbeat": last_heartbeat.isoformat(),
            "time_since_heartbeat": time_since_heartbeat.total_seconds(),
            "error_count": agent_data["error_count"],
            "success_count": agent_data["success_count"],
            "success_rate": success_rate,
            "recent_metrics": recent_metrics,
            "registered_at": agent_data["registered_at"].isoformat()
        }
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents."""
        return {
            agent_name: self.get_agent_status(agent_name)
            for agent_name in self.heartbeats.keys()
        }
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        all_statuses = self.get_all_agent_statuses()
        
        total_agents = len(all_statuses)
        healthy_agents = len([s for s in all_statuses.values() if s and s["health"] == "healthy"])
        degraded_agents = len([s for s in all_statuses.values() if s and s["health"] == "degraded"])
        failing_agents = len([s for s in all_statuses.values() if s and s["health"] == "failing"])
        offline_agents = len([s for s in all_statuses.values() if s and s["health"] == "offline"])
        
        # Get recent errors
        recent_errors = self._get_recent_errors(hours=24)
        
        return {
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "degraded_agents": degraded_agents,
            "failing_agents": failing_agents,
            "offline_agents": offline_agents,
            "health_percentage": (healthy_agents / total_agents * 100) if total_agents > 0 else 0,
            "recent_errors": len(recent_errors),
            "critical_errors": len([e for e in recent_errors if e["severity"] == "critical"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def _metrics_processor(self):
        """Background thread to process metrics queue."""
        while self.monitoring_active:
            try:
                # Process metrics in batches
                metrics_batch = []
                for _ in range(100):  # Process up to 100 metrics at once
                    try:
                        metric = self.metrics_queue.get_nowait()
                        metrics_batch.append(metric)
                    except queue.Empty:
                        break
                
                if metrics_batch:
                    self._store_metrics_batch(metrics_batch)
                
                time.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Metrics processor error: {e}")
                time.sleep(5)
    
    def _heartbeat_monitor(self):
        """Background thread to monitor agent heartbeats."""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                for agent_name, agent_data in self.heartbeats.items():
                    last_heartbeat = agent_data["last_heartbeat"]
                    time_since_heartbeat = current_time - last_heartbeat
                    
                    # Mark as offline if no heartbeat for 5 minutes
                    if time_since_heartbeat > timedelta(minutes=5):
                        if agent_data["status"] != "offline":
                            logger.warning(f"Agent {agent_name} appears offline (no heartbeat for {time_since_heartbeat.total_seconds():.0f}s)")
                            agent_data["status"] = "offline"
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                time.sleep(60)
    
    def _resource_monitor(self):
        """Background thread to monitor system resources."""
        while self.monitoring_active:
            try:
                # Monitor system resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                # Record system metrics
                self.record_metric(
                    agent_name="system",
                    metric_type=MetricType.RESOURCE,
                    value={
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_percent,
                        "disk_percent": disk_percent,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                time.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Resource monitor error: {e}")
                time.sleep(120)
    
    def _store_metrics_batch(self, metrics: List[AgentMetric]):
        """Store a batch of metrics in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in metrics:
            cursor.execute('''
                INSERT INTO agent_metrics (agent_name, metric_type, timestamp, value, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                metric.agent_name,
                metric.metric_type.value,
                metric.timestamp.isoformat(),
                json.dumps(metric.value),
                json.dumps(metric.metadata)
            ))
        
        conn.commit()
        conn.close()
    
    def _store_heartbeat(self, heartbeat: AgentHeartbeat):
        """Store a heartbeat in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_heartbeats (agent_name, timestamp, status, last_activity, memory_usage, cpu_usage, custom_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            heartbeat.agent_name,
            heartbeat.timestamp.isoformat(),
            heartbeat.status,
            heartbeat.last_activity.isoformat(),
            heartbeat.memory_usage,
            heartbeat.cpu_usage,
            json.dumps(heartbeat.custom_metrics)
        ))
        
        conn.commit()
        conn.close()
    
    def _store_error(self, error: AgentError):
        """Store an error in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_errors (agent_name, timestamp, error_type, error_message, stack_trace, context, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            error.agent_name,
            error.timestamp.isoformat(),
            error.error_type,
            error.error_message,
            error.stack_trace,
            json.dumps(error.context),
            error.severity
        ))
        
        conn.commit()
        conn.close()
    
    def _get_recent_metrics(self, agent_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent metrics for an agent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT metric_type, value, metadata, timestamp
            FROM agent_metrics
            WHERE agent_name = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (agent_name, cutoff_time))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "metric_type": row[0],
                "value": json.loads(row[1]),
                "metadata": json.loads(row[2]),
                "timestamp": row[3]
            })
        
        conn.close()
        return results
    
    def _get_recent_errors(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent errors."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT agent_name, error_type, error_message, severity, timestamp
            FROM agent_errors
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (cutoff_time,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "agent_name": row[0],
                "error_type": row[1],
                "error_message": row[2],
                "severity": row[3],
                "timestamp": row[4]
            })
        
        conn.close()
        return results
    
    def shutdown(self):
        """Shutdown the monitoring system."""
        self.monitoring_active = False
        logger.info("🛑 Agent Monitoring System shutdown")

# Global monitoring system instance
agent_monitor = AgentMonitoringSystem()

# Convenience functions for agents to use
def record_agent_metric(agent_name: str, metric_type: str, value: Any, metadata: Dict[str, Any] = None):
    """Record a metric for an agent."""
    agent_monitor.record_metric(agent_name, MetricType(metric_type), value, metadata)

def record_agent_error(agent_name: str, error_type: str, error_message: str, 
                      stack_trace: str = "", context: Dict[str, Any] = None, severity: str = "medium"):
    """Record an error for an agent."""
    agent_monitor.record_error(agent_name, error_type, error_message, stack_trace, context, severity)

def record_agent_success(agent_name: str, operation: str, duration: float = None, metadata: Dict[str, Any] = None):
    """Record a successful operation for an agent."""
    agent_monitor.record_success(agent_name, operation, duration, metadata)

def record_agent_output(agent_name: str, output_type: str, output_data: Any, metadata: Dict[str, Any] = None):
    """Record an output from an agent."""
    agent_monitor.record_output(agent_name, output_type, output_data, metadata)

def update_agent_heartbeat(agent_name: str, status: str = "active", custom_metrics: Dict[str, Any] = None):
    """Update agent heartbeat."""
    agent_monitor.update_heartbeat(agent_name, status, custom_metrics) 