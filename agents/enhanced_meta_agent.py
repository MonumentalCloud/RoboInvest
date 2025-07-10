#!/usr/bin/env python3
"""
Enhanced Meta Agent: Continuous System Monitor and Improvement Coordinator

This enhanced meta agent provides:
1. Continuous monitoring of all agents and system components
2. Real-time performance analysis and bottleneck detection
3. Automated improvement suggestions and implementation
4. Coordination with code fixing agents and administrative agents
5. System-wide optimization and self-healing capabilities
6. Predictive maintenance and proactive issue resolution
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import psutil
import os
import sys

from core.openai_manager import openai_manager
from utils.logger import logger
from agents.agent_monitoring_system import agent_monitor
from agents.specialized_meta_agents import CodeEditorAgent, PromptEngineerAgent, SystemArchitectAgent, PerformanceAnalystAgent
from agents.meta_agent_system import MetaAgent, AgentHealth, SystemPriority, SystemAlert
from agents.notification_system import notification_system
from core.notification_aggregator import notification_aggregator

class ImprovementType(Enum):
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    SCALABILITY = "scalability"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    FUNCTIONALITY = "functionality"

class ImprovementPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SystemImprovement:
    id: str
    type: ImprovementType
    priority: ImprovementPriority
    title: str
    description: str
    affected_components: List[str]
    estimated_impact: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    confidence: float
    created_at: datetime
    status: str = "pending"  # pending, approved, in_progress, completed, rejected
    assigned_agent: Optional[str] = None
    completion_time: Optional[datetime] = None

@dataclass
class SystemMetrics:
    timestamp: datetime
    total_agents: int
    active_agents: int
    failed_agents: int
    avg_response_time: float
    avg_success_rate: float
    system_cpu_usage: float
    system_memory_usage: float
    total_errors: int
    total_insights: int
    research_cycles_completed: int
    performance_score: float

class EnhancedMetaAgent:
    """
    Enhanced meta agent that continuously monitors and improves the multiagent system.
    
    Key capabilities:
    - Real-time system monitoring and health assessment
    - Performance bottleneck detection and analysis
    - Automated improvement suggestion generation
    - Coordination with specialized agents for implementation
    - Predictive maintenance and proactive optimization
    - System-wide optimization strategies
    """
    
    def __init__(self):
        self.meta_agent = MetaAgent()
        self.code_editor = CodeEditorAgent()
        self.prompt_engineer = PromptEngineerAgent()
        self.system_architect = SystemArchitectAgent()
        self.performance_analyst = PerformanceAnalystAgent()
        
        # System state tracking
        self.system_improvements: List[SystemImprovement] = []
        self.system_metrics_history: List[SystemMetrics] = []
        self.active_monitoring = False
        self.improvement_queue: List[SystemImprovement] = []
        
        # Monitoring configuration
        self.monitoring_interval = 30  # seconds
        self.metrics_retention_hours = 24
        self.improvement_threshold = 0.7  # confidence threshold for auto-implementation
        
        # Performance thresholds
        self.performance_thresholds = {
            "response_time": 30.0,  # seconds
            "success_rate": 0.3,  # Lowered from 0.8 to 0.3 (30%) to prevent false alerts during startup
            "cpu_usage": 80.0,  # percentage
            "memory_usage": 85.0,  # percentage
            "error_rate": 0.1  # percentage
        }
        
        # Initialize database
        self.db_path = Path("meta_agent_data/enhanced_meta_agent.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
        logger.info("🚀 Enhanced Meta Agent initialized")
    
    def _init_database(self):
        """Initialize database for storing system improvements and metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System improvements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_improvements (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                affected_components TEXT NOT NULL,
                estimated_impact TEXT NOT NULL,
                implementation_plan TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                assigned_agent TEXT,
                completion_time TEXT
            )
        ''')
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_agents INTEGER NOT NULL,
                active_agents INTEGER NOT NULL,
                failed_agents INTEGER NOT NULL,
                avg_response_time REAL NOT NULL,
                avg_success_rate REAL NOT NULL,
                system_cpu_usage REAL NOT NULL,
                system_memory_usage REAL NOT NULL,
                total_errors INTEGER NOT NULL,
                total_insights INTEGER NOT NULL,
                research_cycles_completed INTEGER NOT NULL,
                performance_score REAL NOT NULL
            )
        ''')
        
        # Agent performance history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                response_time REAL,
                success_rate REAL,
                error_count INTEGER,
                insights_generated INTEGER,
                memory_usage REAL,
                cpu_usage REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_continuous_monitoring(self):
        """Start the continuous monitoring and improvement system."""
        logger.info("🔍 Starting continuous system monitoring...")
        
        self.active_monitoring = True
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._continuous_monitoring_loop()),
            asyncio.create_task(self._improvement_analysis_loop()),
            asyncio.create_task(self._performance_optimization_loop()),
            asyncio.create_task(self._predictive_maintenance_loop()),
            asyncio.create_task(self._coordination_loop())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _continuous_monitoring_loop(self):
        """Main monitoring loop that continuously tracks system health."""
        while self.active_monitoring:
            try:
                # Collect current system metrics
                metrics = await self._collect_system_metrics()
                self.system_metrics_history.append(metrics)
                
                # Store metrics in database
                await self._store_system_metrics(metrics)
                
                # Analyze for immediate issues
                await self._analyze_system_health(metrics)
                
                # Update agent performance history
                await self._update_agent_performance_history()
                
                # Clean up old metrics
                await self._cleanup_old_metrics()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics."""
        try:
            # Get agent statuses
            agent_statuses = agent_monitor.get_all_agent_statuses()
            total_agents = len(agent_statuses)
            active_agents = len([a for a in agent_statuses.values() if a.get("status") == "active"])
            failed_agents = len([a for a in agent_statuses.values() if a.get("status") == "error"])
            
            # Calculate averages
            response_times = [a.get("avg_response_time", 0) for a in agent_statuses.values()]
            success_rates = [a.get("success_rate", 0) for a in agent_statuses.values()]
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
            
            # System resource usage
            system_cpu_usage = psutil.cpu_percent(interval=1)
            system_memory_usage = psutil.virtual_memory().percent
            
            # Get error and insight counts
            total_errors = sum(a.get("error_count", 0) for a in agent_statuses.values())
            total_insights = sum(a.get("insights_generated", 0) for a in agent_statuses.values())
            
            # Research cycles (from background service)
            research_cycles_completed = await self._get_research_cycles_count()
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(
                avg_response_time, avg_success_rate, system_cpu_usage, 
                system_memory_usage, total_errors, total_agents
            )
            
            return SystemMetrics(
                timestamp=datetime.now(),
                total_agents=total_agents,
                active_agents=active_agents,
                failed_agents=failed_agents,
                avg_response_time=avg_response_time,
                avg_success_rate=avg_success_rate,
                system_cpu_usage=system_cpu_usage,
                system_memory_usage=system_memory_usage,
                total_errors=total_errors,
                total_insights=total_insights,
                research_cycles_completed=research_cycles_completed,
                performance_score=performance_score
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                total_agents=0,
                active_agents=0,
                failed_agents=0,
                avg_response_time=0,
                avg_success_rate=0,
                system_cpu_usage=0,
                system_memory_usage=0,
                total_errors=0,
                total_insights=0,
                research_cycles_completed=0,
                performance_score=0
            )
    
    def _calculate_performance_score(self, response_time: float, success_rate: float, 
                                   cpu_usage: float, memory_usage: float, 
                                   total_errors: int, total_agents: int) -> float:
        """Calculate overall system performance score (0-100)."""
        if total_agents == 0:
            return 0
        
        # Normalize metrics
        response_score = max(0, 100 - (response_time / self.performance_thresholds["response_time"]) * 100)
        success_score = success_rate * 100
        cpu_score = max(0, 100 - cpu_usage)
        memory_score = max(0, 100 - memory_usage)
        error_score = max(0, 100 - (total_errors / total_agents) * 1000)  # Penalize errors heavily
        
        # Weighted average
        weights = {
            "response": 0.2,
            "success": 0.3,
            "cpu": 0.15,
            "memory": 0.15,
            "error": 0.2
        }
        
        score = (
            response_score * weights["response"] +
            success_score * weights["success"] +
            cpu_score * weights["cpu"] +
            memory_score * weights["memory"] +
            error_score * weights["error"]
        )
        
        return min(100, max(0, score))
    
    async def _analyze_system_health(self, metrics: SystemMetrics):
        """Analyze system health and create alerts if needed."""
        # Check for critical issues
        if metrics.failed_agents > 0:
            await self._create_improvement_suggestion(
                ImprovementType.RELIABILITY,
                ImprovementPriority.CRITICAL,
                f"Agent Failure Recovery",
                f"Detected {metrics.failed_agents} failed agents. Immediate recovery needed.",
                ["agent_monitoring_system", "meta_agent_system"],
                {"reliability_impact": "critical", "recovery_time": "immediate"},
                {"action": "restart_failed_agents", "priority": "immediate"},
                0.95
            )
        
        # Check performance thresholds
        if metrics.avg_response_time > self.performance_thresholds["response_time"]:
            await self._create_improvement_suggestion(
                ImprovementType.PERFORMANCE,
                ImprovementPriority.HIGH,
                "Response Time Optimization",
                f"Average response time ({metrics.avg_response_time:.2f}s) exceeds threshold ({self.performance_thresholds['response_time']}s)",
                ["all_agents", "orchestrator"],
                {"performance_impact": "high", "user_experience": "degraded"},
                {"action": "optimize_response_times", "focus": "bottleneck_analysis"},
                0.85
            )
        
        # Only create improvement suggestions if agents are actually running
        if metrics.total_agents > 0 and metrics.avg_success_rate < self.performance_thresholds["success_rate"]:
            await self._create_improvement_suggestion(
                ImprovementType.RELIABILITY,
                ImprovementPriority.HIGH,
                "Success Rate Improvement",
                f"Average success rate ({metrics.avg_success_rate:.2%}) below threshold ({self.performance_thresholds['success_rate']:.2%})",
                ["all_agents", "error_handling"],
                {"reliability_impact": "high", "user_confidence": "degraded"},
                {"action": "improve_error_handling", "focus": "root_cause_analysis"},
                0.9
            )
        
        # Check resource usage
        if metrics.system_cpu_usage > self.performance_thresholds["cpu_usage"]:
            await self._create_improvement_suggestion(
                ImprovementType.EFFICIENCY,
                ImprovementPriority.MEDIUM,
                "CPU Usage Optimization",
                f"System CPU usage ({metrics.system_cpu_usage:.1f}%) exceeds threshold ({self.performance_thresholds['cpu_usage']}%)",
                ["system_resources", "agent_efficiency"],
                {"efficiency_impact": "medium", "scalability": "limited"},
                {"action": "optimize_cpu_usage", "focus": "resource_management"},
                0.8
            )
    
    async def _improvement_analysis_loop(self):
        """Analyze system patterns and generate improvement suggestions."""
        while self.active_monitoring:
            try:
                # Analyze recent metrics for patterns
                if len(self.system_metrics_history) >= 10:
                    await self._analyze_performance_patterns()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Improvement analysis error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_performance_patterns(self):
        """Analyze performance patterns to identify trends and issues."""
        recent_metrics = self.system_metrics_history[-20:]  # Last 20 data points
        
        # Analyze trends
        performance_trend = self._calculate_trend([m.performance_score for m in recent_metrics])
        response_time_trend = self._calculate_trend([m.avg_response_time for m in recent_metrics])
        success_rate_trend = self._calculate_trend([m.avg_success_rate for m in recent_metrics])
        
        # Detect degrading performance
        if performance_trend < -5:  # Performance declining by more than 5 points
            await self._create_improvement_suggestion(
                ImprovementType.PERFORMANCE,
                ImprovementPriority.HIGH,
                "Performance Degradation Trend",
                f"System performance declining (trend: {performance_trend:.1f} points). Proactive optimization needed.",
                ["system_wide", "performance_monitoring"],
                {"trend_impact": "negative", "urgency": "high"},
                {"action": "investigate_degradation", "focus": "trend_analysis"},
                0.9
            )
        
        # Detect improving performance
        if performance_trend > 5:
            logger.info(f"🎉 System performance improving (trend: {performance_trend:.1f} points)")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend of values (positive = improving, negative = declining)."""
        if len(values) < 2:
            return 0
        
        # Simple linear trend calculation
        x_values = list(range(len(values)))
        y_values = values
        
        n = len(values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope * n  # Total change over the period
    
    async def _create_improvement_suggestion(self, improvement_type: ImprovementType, 
                                           priority: ImprovementPriority, title: str, 
                                           description: str, affected_components: List[str],
                                           estimated_impact: Dict[str, Any], 
                                           implementation_plan: Dict[str, Any], 
                                           confidence: float):
        """Create a new system improvement suggestion."""
        improvement = SystemImprovement(
            id=f"improvement_{int(time.time())}_{len(self.system_improvements)}",
            type=improvement_type,
            priority=priority,
            title=title,
            description=description,
            affected_components=affected_components,
            estimated_impact=estimated_impact,
            implementation_plan=implementation_plan,
            confidence=confidence,
            created_at=datetime.now()
        )
        
        self.system_improvements.append(improvement)
        self.improvement_queue.append(improvement)
        
        # Store in database
        await self._store_improvement(improvement)
        
        logger.info(f"💡 Created improvement suggestion: {title} (Priority: {priority.value})")
        
        # Send notification for high-priority improvements only if system is operational
        if priority in [ImprovementPriority.CRITICAL, ImprovementPriority.HIGH]:
            # Check if system has active agents before sending alerts
            if len(self.system_metrics_history) > 0:
                latest_metrics = self.system_metrics_history[-1]
                if latest_metrics.total_agents > 0 and latest_metrics.active_agents > 0:
                    notification_aggregator.add_alert(
                        "system_improvement",
                        f"High-priority improvement: {title}",
                        {
                            "improvement_id": improvement.id,
                            "priority": priority.value,
                            "type": improvement_type.value,
                            "description": description
                        }
                    )
                else:
                    logger.info(f"⚠️  Suppressing alert '{title}' - system not fully operational (agents: {latest_metrics.total_agents}, active: {latest_metrics.active_agents})")
            else:
                logger.info(f"⚠️  Suppressing alert '{title}' - no system metrics available yet")
    
    async def _performance_optimization_loop(self):
        """Continuously optimize system performance."""
        while self.active_monitoring:
            try:
                # Process improvement queue
                await self._process_improvement_queue()
                
                # Apply automatic optimizations for high-confidence improvements
                await self._apply_automatic_optimizations()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Performance optimization error: {e}")
                await asyncio.sleep(30)
    
    async def _process_improvement_queue(self):
        """Process the queue of improvement suggestions."""
        for improvement in self.improvement_queue[:]:  # Copy list to avoid modification during iteration
            if improvement.status == "pending":
                # Assign to appropriate agent based on type
                if improvement.type == ImprovementType.PERFORMANCE:
                    improvement.assigned_agent = "performance_analyst"
                elif improvement.type in [ImprovementType.RELIABILITY, ImprovementType.SECURITY]:
                    improvement.assigned_agent = "code_editor"
                elif improvement.type == ImprovementType.EFFICIENCY:
                    improvement.assigned_agent = "prompt_engineer"
                elif improvement.type == ImprovementType.SCALABILITY:
                    improvement.assigned_agent = "system_architect"
                
                improvement.status = "in_progress"
                
                # Update database
                await self._update_improvement_status(improvement)
                
                logger.info(f"🔄 Processing improvement: {improvement.title} (Assigned to: {improvement.assigned_agent})")
    
    async def _apply_automatic_optimizations(self):
        """Apply automatic optimizations for high-confidence improvements."""
        for improvement in self.system_improvements:
            if (improvement.status == "in_progress" and 
                improvement.confidence >= self.improvement_threshold and
                improvement.priority in [ImprovementPriority.CRITICAL, ImprovementPriority.HIGH]):
                
                try:
                    await self._implement_improvement(improvement)
                    improvement.status = "completed"
                    improvement.completion_time = datetime.now()
                    
                    await self._update_improvement_status(improvement)
                    
                    logger.info(f"✅ Automatically implemented improvement: {improvement.title}")
                    
                except Exception as e:
                    logger.error(f"Failed to implement improvement {improvement.title}: {e}")
                    improvement.status = "failed"
                    await self._update_improvement_status(improvement)
    
    async def _implement_improvement(self, improvement: SystemImprovement):
        """Implement a specific improvement."""
        if improvement.assigned_agent == "performance_analyst":
            await self.performance_analyst.apply_optimization(improvement.implementation_plan)
        
        elif improvement.assigned_agent == "code_editor":
            await self.code_editor.apply_improvement(improvement.implementation_plan)
        
        elif improvement.assigned_agent == "prompt_engineer":
            await self.prompt_engineer.apply_optimization(improvement.implementation_plan)
        
        elif improvement.assigned_agent == "system_architect":
            await self.system_architect.apply_optimization(improvement.implementation_plan)
    
    async def _predictive_maintenance_loop(self):
        """Predictive maintenance to prevent issues before they occur."""
        while self.active_monitoring:
            try:
                # Analyze historical data for predictive insights
                if len(self.system_metrics_history) >= 50:
                    await self._predict_potential_issues()
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logger.error(f"Predictive maintenance error: {e}")
                await asyncio.sleep(60)
    
    async def _predict_potential_issues(self):
        """Predict potential issues based on historical patterns."""
        # This would use more sophisticated ML models in a real implementation
        # For now, we'll use simple pattern recognition
        
        recent_metrics = self.system_metrics_history[-30:]  # Last 30 data points
        
        # Check for memory leak patterns
        memory_values = [m.system_memory_usage for m in recent_metrics]
        if self._detect_increasing_trend(memory_values, threshold=2.0):
            await self._create_improvement_suggestion(
                ImprovementType.EFFICIENCY,
                ImprovementPriority.MEDIUM,
                "Potential Memory Leak Detection",
                "Detected increasing memory usage pattern. Preventive optimization recommended.",
                ["memory_management", "resource_cleanup"],
                {"preventive_impact": "high", "cost_savings": "significant"},
                {"action": "memory_optimization", "focus": "leak_prevention"},
                0.75
            )
        
        # Check for CPU usage patterns
        cpu_values = [m.system_cpu_usage for m in recent_metrics]
        if self._detect_increasing_trend(cpu_values, threshold=1.5):
            await self._create_improvement_suggestion(
                ImprovementType.PERFORMANCE,
                ImprovementPriority.MEDIUM,
                "CPU Usage Trend Analysis",
                "Detected increasing CPU usage pattern. Performance optimization recommended.",
                ["cpu_optimization", "efficiency_improvement"],
                {"performance_impact": "medium", "scalability": "improved"},
                {"action": "cpu_optimization", "focus": "efficiency_improvement"},
                0.7
            )
    
    def _detect_increasing_trend(self, values: List[float], threshold: float) -> bool:
        """Detect if values are showing an increasing trend."""
        if len(values) < 10:
            return False
        
        # Calculate trend over last 10 values
        recent_values = values[-10:]
        trend = self._calculate_trend(recent_values)
        
        return trend > threshold
    
    async def _coordination_loop(self):
        """Coordinate with other agents and administrative systems."""
        while self.active_monitoring:
            try:
                # Generate periodic reports
                await self._generate_system_report()
                
                # Coordinate with administrative agents
                await self._coordinate_with_admin_agents()
                
                # Update system status
                await self._update_system_status()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Coordination error: {e}")
                await asyncio.sleep(60)
    
    async def _generate_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report."""
        if not self.system_metrics_history:
            return {}
        
        latest_metrics = self.system_metrics_history[-1]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "performance_score": latest_metrics.performance_score,
                "active_agents": latest_metrics.active_agents,
                "failed_agents": latest_metrics.failed_agents,
                "success_rate": latest_metrics.avg_success_rate,
                "response_time": latest_metrics.avg_response_time
            },
            "resource_usage": {
                "cpu_usage": latest_metrics.system_cpu_usage,
                "memory_usage": latest_metrics.system_memory_usage
            },
            "activity_metrics": {
                "total_insights": latest_metrics.total_insights,
                "research_cycles": latest_metrics.research_cycles_completed,
                "total_errors": latest_metrics.total_errors
            },
            "improvements": {
                "pending": len([i for i in self.system_improvements if i.status == "pending"]),
                "in_progress": len([i for i in self.system_improvements if i.status == "in_progress"]),
                "completed": len([i for i in self.system_improvements if i.status == "completed"])
            },
            "recommendations": await self._generate_recommendations()
        }
        
        # Save report
        report_path = Path("meta_agent_data/system_reports")
        report_path.mkdir(exist_ok=True)
        
        with open(report_path / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    async def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on current system state."""
        recommendations = []
        
        if not self.system_metrics_history:
            return recommendations
        
        latest_metrics = self.system_metrics_history[-1]
        
        # Performance recommendations
        if latest_metrics.performance_score < 70:
            recommendations.append({
                "type": "performance_optimization",
                "priority": "high",
                "description": "System performance below optimal levels. Consider implementing performance improvements.",
                "action": "review_performance_metrics"
            })
        
        # Reliability recommendations
        if latest_metrics.failed_agents > 0:
            recommendations.append({
                "type": "reliability_improvement",
                "priority": "critical",
                "description": f"{latest_metrics.failed_agents} agents are failing. Immediate attention required.",
                "action": "restart_failed_agents"
            })
        
        # Efficiency recommendations
        if latest_metrics.system_cpu_usage > 70:
            recommendations.append({
                "type": "efficiency_optimization",
                "priority": "medium",
                "description": "High CPU usage detected. Consider optimizing resource usage.",
                "action": "optimize_cpu_usage"
            })
        
        return recommendations
    
    async def _coordinate_with_admin_agents(self):
        """Coordinate with administrative agents for system-wide decisions."""
        # This would interface with administrative agents in a real implementation
        # For now, we'll log coordination activities
        
        if self.system_improvements:
            critical_improvements = [i for i in self.system_improvements 
                                   if i.priority == ImprovementPriority.CRITICAL and i.status == "pending"]
            
            if critical_improvements:
                logger.info(f"🚨 Coordinating with admin agents for {len(critical_improvements)} critical improvements")
                
                # Send to administrative agents for review
                for improvement in critical_improvements:
                    notification_aggregator.add_alert(
                        "admin_review_required",
                        f"Critical improvement requires admin review: {improvement.title}",
                        asdict(improvement)
                    )
    
    async def _update_system_status(self):
        """Update overall system status."""
        status = {
            "meta_agent_status": "active" if self.active_monitoring else "inactive",
            "monitoring_active": self.active_monitoring,
            "total_improvements": len(self.system_improvements),
            "pending_improvements": len([i for i in self.system_improvements if i.status == "pending"]),
            "completed_improvements": len([i for i in self.system_improvements if i.status == "completed"]),
            "last_metrics_collection": self.system_metrics_history[-1].timestamp.isoformat() if self.system_metrics_history else None
        }
        
        # Save status
        status_path = Path("meta_agent_data/system_status.json")
        status_path.parent.mkdir(exist_ok=True)
        
        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2, default=str)
    
    async def _store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, total_agents, active_agents, failed_agents, avg_response_time,
                 avg_success_rate, system_cpu_usage, system_memory_usage, total_errors,
                 total_insights, research_cycles_completed, performance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.total_agents,
                metrics.active_agents,
                metrics.failed_agents,
                metrics.avg_response_time,
                metrics.avg_success_rate,
                metrics.system_cpu_usage,
                metrics.system_memory_usage,
                metrics.total_errors,
                metrics.total_insights,
                metrics.research_cycles_completed,
                metrics.performance_score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing system metrics: {e}")
    
    async def _store_improvement(self, improvement: SystemImprovement):
        """Store improvement in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_improvements 
                (id, type, priority, title, description, affected_components,
                 estimated_impact, implementation_plan, confidence, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                improvement.id,
                improvement.type.value,
                improvement.priority.value,
                improvement.title,
                improvement.description,
                json.dumps(improvement.affected_components),
                json.dumps(improvement.estimated_impact),
                json.dumps(improvement.implementation_plan),
                improvement.confidence,
                improvement.created_at.isoformat(),
                improvement.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing improvement: {e}")
    
    async def _update_improvement_status(self, improvement: SystemImprovement):
        """Update improvement status in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE system_improvements 
                SET status = ?, assigned_agent = ?, completion_time = ?
                WHERE id = ?
            ''', (
                improvement.status,
                improvement.assigned_agent,
                improvement.completion_time.isoformat() if improvement.completion_time else None,
                improvement.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating improvement status: {e}")
    
    async def _get_research_cycles_count(self) -> int:
        """Get count of completed research cycles."""
        try:
            # This would query the research service database
            # For now, return a placeholder
            return 0
        except Exception as e:
            logger.error(f"Error getting research cycles count: {e}")
            return 0
    
    async def _update_agent_performance_history(self):
        """Update agent performance history in database."""
        try:
            agent_statuses = agent_monitor.get_all_agent_statuses()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for agent_name, status in agent_statuses.items():
                cursor.execute('''
                    INSERT INTO agent_performance_history 
                    (agent_name, timestamp, response_time, success_rate, error_count,
                     insights_generated, memory_usage, cpu_usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agent_name,
                    datetime.now().isoformat(),
                    status.get("avg_response_time", 0),
                    status.get("success_rate", 0),
                    status.get("error_count", 0),
                    status.get("insights_generated", 0),
                    status.get("memory_usage", 0),
                    status.get("cpu_usage", 0)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating agent performance history: {e}")
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics data."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clean up old system metrics
            cursor.execute('''
                DELETE FROM system_metrics 
                WHERE timestamp < ?
            ''', (cutoff_time.isoformat(),))
            
            # Clean up old agent performance history
            cursor.execute('''
                DELETE FROM agent_performance_history 
                WHERE timestamp < ?
            ''', (cutoff_time.isoformat(),))
            
            conn.commit()
            conn.close()
            
            # Clean up in-memory metrics
            self.system_metrics_history = [
                m for m in self.system_metrics_history 
                if m.timestamp > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "meta_agent_active": self.active_monitoring,
            "total_improvements": len(self.system_improvements),
            "pending_improvements": len([i for i in self.system_improvements if i.status == "pending"]),
            "in_progress_improvements": len([i for i in self.system_improvements if i.status == "in_progress"]),
            "completed_improvements": len([i for i in self.system_improvements if i.status == "completed"]),
            "latest_metrics": asdict(self.system_metrics_history[-1]) if self.system_metrics_history else None,
            "performance_score": self.system_metrics_history[-1].performance_score if self.system_metrics_history else 0
        }
    
    def stop_monitoring(self):
        """Stop the continuous monitoring system."""
        logger.info("🛑 Stopping enhanced meta agent monitoring...")
        self.active_monitoring = False

# Global instance
enhanced_meta_agent = EnhancedMetaAgent()