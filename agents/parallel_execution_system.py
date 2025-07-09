"""
Parallel Execution System
Advanced system for coordinating multiple agents working in parallel to maximize efficiency and insights.
"""

import asyncio
import json
import uuid
import time
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import threading
from queue import Queue, PriorityQueue
from dataclasses import dataclass, field

from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
from agents.multi_agent_orchestrator import MultiAgentOrchestrator, AgentRole
from core.config import config
from utils.logger import logger  # type: ignore

class ExecutionPriority(Enum):
    """Execution priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class ResourceType(Enum):
    """Types of system resources."""
    CPU = "cpu"
    MEMORY = "memory"
    API_CALLS = "api_calls"
    NETWORK = "network"
    STORAGE = "storage"

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExecutionTask:
    """Individual execution task."""
    task_id: str
    agent_id: str
    objective: str
    context: Dict[str, Any]
    priority: ExecutionPriority
    resource_requirements: Dict[ResourceType, float]
    estimated_duration: float
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __lt__(self, other):
        """For priority queue ordering."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.estimated_duration < other.estimated_duration

@dataclass
class ResourcePool:
    """System resource pool management."""
    max_concurrent_tasks: int = 8
    max_api_calls_per_minute: int = 60
    max_memory_usage: float = 0.8  # 80% of available memory
    api_call_count: int = 0
    api_call_reset_time: datetime = field(default_factory=datetime.now)
    active_tasks: int = 0
    memory_usage: float = 0.0
    
    def can_allocate(self, requirements: Dict[ResourceType, float]) -> bool:
        """Check if resources can be allocated for a task."""
        if self.active_tasks >= self.max_concurrent_tasks:
            return False
        
        # Check API rate limits
        now = datetime.now()
        if now - self.api_call_reset_time > timedelta(minutes=1):
            self.api_call_count = 0
            self.api_call_reset_time = now
        
        required_api_calls = requirements.get(ResourceType.API_CALLS, 1)
        if self.api_call_count + required_api_calls > self.max_api_calls_per_minute:
            return False
        
        # Check memory
        required_memory = requirements.get(ResourceType.MEMORY, 0.1)
        if self.memory_usage + required_memory > self.max_memory_usage:
            return False
        
        return True
    
    def allocate(self, requirements: Dict[ResourceType, float]):
        """Allocate resources for a task."""
        self.active_tasks += 1
        self.api_call_count += requirements.get(ResourceType.API_CALLS, 1)
        self.memory_usage += requirements.get(ResourceType.MEMORY, 0.1)
    
    def release(self, requirements: Dict[ResourceType, float]):
        """Release resources after task completion."""
        self.active_tasks = max(0, self.active_tasks - 1)
        self.memory_usage = max(0, self.memory_usage - requirements.get(ResourceType.MEMORY, 0.1))

class ParallelExecutionEngine:
    """
    Advanced parallel execution engine for coordinating multiple AI agents.
    
    Features:
    - Dynamic task scheduling and prioritization
    - Resource management and allocation
    - Dependency resolution
    - Load balancing across agents
    - Performance monitoring and optimization
    - Fault tolerance and recovery
    """
    
    def __init__(self, max_agents: int = 8):
        self.max_agents = max_agents
        self.agents: Dict[str, EnhancedAutonomousAgent] = {}
        self.orchestrator = MultiAgentOrchestrator(max_agents)
        
        # Task management
        self.task_queue = PriorityQueue()
        self.completed_tasks: Dict[str, ExecutionTask] = {}
        self.running_tasks: Dict[str, ExecutionTask] = {}
        self.task_dependencies: Dict[str, Set[str]] = {}
        
        # Resource management
        self.resource_pool = ResourcePool()
        self.load_balancer = LoadBalancer()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.execution_stats = {
            "total_tasks_executed": 0,
            "total_execution_time": 0.0,
            "avg_task_duration": 0.0,
            "success_rate": 0.0,
            "parallel_efficiency": 0.0
        }
        
        # Coordination mechanisms
        self.coordination_lock = threading.Lock()
        self.agent_coordination_channels: Dict[str, Queue] = {}
        self.shared_insights: Dict[str, Any] = {}
        
        logger.info(f"Parallel Execution Engine initialized with capacity for {max_agents} agents")
    
    def initialize_agent_pool(self, specializations: List[str] = None) -> Dict[str, str]:
        """Initialize a pool of enhanced autonomous agents."""
        
        default_specializations = [
            "alpha_hunting", "market_analysis", "sentiment_analysis", 
            "technical_analysis", "fundamental_research", "risk_assessment",
            "strategy_validation", "execution_optimization"
        ]
        
        specializations = specializations or default_specializations
        created_agents = {}
        
        for i, specialization in enumerate(specializations[:self.max_agents]):
            agent_id = f"enhanced_{specialization}_{i+1}"
            agent = EnhancedAutonomousAgent(agent_id, specialization)
            self.agents[agent_id] = agent
            
            # Initialize coordination channel
            self.agent_coordination_channels[agent_id] = Queue()
            
            created_agents[agent_id] = specialization
            
        logger.info(f"Initialized {len(self.agents)} enhanced autonomous agents")
        return created_agents
    
    async def execute_parallel_research_mission(self, 
                                              mission_objective: str,
                                              context: Dict[str, Any] = None,
                                              priority: ExecutionPriority = ExecutionPriority.NORMAL) -> Dict[str, Any]:
        """
        Execute a comprehensive research mission using multiple agents in parallel.
        """
        try:
            mission_id = str(uuid.uuid4())
            mission_start_time = time.time()
            
            logger.info(f"Starting parallel research mission: {mission_objective}")
            
            # Phase 1: Mission decomposition and task creation
            tasks = await self._decompose_mission_into_tasks(mission_objective, context, priority)
            
            # Phase 2: Dependency resolution and scheduling
            execution_plan = self._resolve_dependencies_and_schedule(tasks)
            
            # Phase 3: Parallel execution with coordination
            execution_results = await self._execute_coordinated_parallel_tasks(execution_plan)
            
            # Phase 4: Results synthesis and insight integration
            mission_synthesis = await self._synthesize_mission_results(execution_results, mission_objective)
            
            # Phase 5: Performance analysis and learning
            performance_analysis = self._analyze_mission_performance(execution_results, mission_start_time)
            
            mission_result = {
                "mission_id": mission_id,
                "objective": mission_objective,
                "execution_plan": execution_plan,
                "agent_results": execution_results,
                "synthesis": mission_synthesis,
                "performance": performance_analysis,
                "timestamp": datetime.now().isoformat(),
                "duration": time.time() - mission_start_time
            }
            
            # Update global stats
            self.execution_stats["total_tasks_executed"] += len(tasks)
            
            logger.info(f"Mission completed: {len(execution_results)} agents, {len(mission_synthesis.get('insights', []))} insights")
            return mission_result
            
        except Exception as e:
            logger.error(f"Mission execution error: {e}")
            return {"error": str(e), "mission_id": mission_id}
    
    async def _decompose_mission_into_tasks(self, 
                                          objective: str, 
                                          context: Dict[str, Any],
                                          priority: ExecutionPriority) -> List[ExecutionTask]:
        """Decompose mission into specific tasks for different agents."""
        
        tasks = []
        
        # Create specialized tasks based on available agents
        for agent_id, agent in self.agents.items():
            
            # Customize objective based on agent specialization
            specialized_objective = self._customize_objective_for_agent(objective, agent.specialization)
            
            # Estimate resource requirements
            resource_requirements = self._estimate_resource_requirements(agent.specialization)
            
            # Estimate duration based on complexity and agent performance
            estimated_duration = self._estimate_task_duration(specialized_objective, agent)
            
            task = ExecutionTask(
                task_id=str(uuid.uuid4()),
                agent_id=agent_id,
                objective=specialized_objective,
                context=context or {},
                priority=priority,
                resource_requirements=resource_requirements,
                estimated_duration=estimated_duration
            )
            
            tasks.append(task)
        
        # Add inter-agent coordination tasks if needed
        if len(tasks) > 2:
            coordination_task = ExecutionTask(
                task_id=str(uuid.uuid4()),
                agent_id="coordination_engine",
                objective="Coordinate insights across agents",
                context={"coordination_type": "insight_sharing"},
                priority=ExecutionPriority.HIGH,
                resource_requirements={ResourceType.CPU: 0.2, ResourceType.MEMORY: 0.1},
                estimated_duration=30.0,
                dependencies=[task.task_id for task in tasks]
            )
            tasks.append(coordination_task)
        
        return tasks
    
    def _customize_objective_for_agent(self, base_objective: str, specialization: str) -> str:
        """Customize objective based on agent specialization."""
        
        specialization_prompts = {
            "alpha_hunting": f"Hunt for unique alpha opportunities related to: {base_objective}",
            "market_analysis": f"Analyze current market conditions and trends for: {base_objective}",
            "sentiment_analysis": f"Analyze sentiment and narrative dynamics around: {base_objective}",
            "technical_analysis": f"Perform technical analysis and pattern recognition for: {base_objective}",
            "fundamental_research": f"Conduct fundamental research and valuation analysis for: {base_objective}",
            "risk_assessment": f"Assess risks and potential downsides related to: {base_objective}",
            "strategy_validation": f"Validate and optimize strategies related to: {base_objective}",
            "execution_optimization": f"Optimize execution and timing strategies for: {base_objective}"
        }
        
        return specialization_prompts.get(specialization, base_objective)
    
    def _estimate_resource_requirements(self, specialization: str) -> Dict[ResourceType, float]:
        """Estimate resource requirements based on specialization."""
        
        base_requirements = {
            ResourceType.CPU: 0.3,
            ResourceType.MEMORY: 0.2,
            ResourceType.API_CALLS: 5,
            ResourceType.NETWORK: 0.1
        }
        
        # Adjust based on specialization
        multipliers = {
            "alpha_hunting": {ResourceType.API_CALLS: 2.0, ResourceType.CPU: 1.5},
            "market_analysis": {ResourceType.API_CALLS: 1.5, ResourceType.MEMORY: 1.3},
            "sentiment_analysis": {ResourceType.API_CALLS: 2.5, ResourceType.NETWORK: 1.5},
            "technical_analysis": {ResourceType.CPU: 2.0, ResourceType.MEMORY: 1.5},
            "fundamental_research": {ResourceType.API_CALLS: 3.0, ResourceType.NETWORK: 2.0},
            "risk_assessment": {ResourceType.CPU: 1.5, ResourceType.MEMORY: 1.3},
            "strategy_validation": {ResourceType.CPU: 1.8, ResourceType.MEMORY: 1.4},
            "execution_optimization": {ResourceType.CPU: 1.2, ResourceType.MEMORY: 1.1}
        }
        
        spec_multipliers = multipliers.get(specialization, {})
        
        for resource_type in base_requirements:
            base_requirements[resource_type] *= spec_multipliers.get(resource_type, 1.0)
        
        return base_requirements
    
    def _estimate_task_duration(self, objective: str, agent: EnhancedAutonomousAgent) -> float:
        """Estimate task duration based on complexity and agent performance."""
        
        # Base duration estimate (in seconds)
        base_duration = 120.0  # 2 minutes
        
        # Adjust based on objective complexity
        complexity_keywords = ['comprehensive', 'detailed', 'in-depth', 'thorough']
        if any(keyword in objective.lower() for keyword in complexity_keywords):
            base_duration *= 1.5
        
        # Adjust based on agent performance history
        avg_confidence = agent.performance_metrics.get("avg_confidence", 0.5)
        if avg_confidence > 0.7:
            base_duration *= 0.8  # High-performing agents are faster
        elif avg_confidence < 0.4:
            base_duration *= 1.3  # Lower-performing agents take longer
        
        return base_duration
    
    def _resolve_dependencies_and_schedule(self, tasks: List[ExecutionTask]) -> Dict[str, Any]:
        """Resolve task dependencies and create optimal execution schedule."""
        
        # Create dependency graph
        dependency_graph = {}
        for task in tasks:
            dependency_graph[task.task_id] = {
                "task": task,
                "dependencies": set(task.dependencies),
                "dependents": set()
            }
        
        # Build reverse dependencies
        for task_id, task_info in dependency_graph.items():
            for dep_id in task_info["dependencies"]:
                if dep_id in dependency_graph:
                    dependency_graph[dep_id]["dependents"].add(task_id)
        
        # Create execution waves (groups of tasks that can run in parallel)
        execution_waves = []
        remaining_tasks = set(dependency_graph.keys())
        
        while remaining_tasks:
            # Find tasks with no unresolved dependencies
            current_wave = []
            for task_id in list(remaining_tasks):
                task_info = dependency_graph[task_id]
                unresolved_deps = task_info["dependencies"] & remaining_tasks
                
                if not unresolved_deps:
                    current_wave.append(task_info["task"])
                    remaining_tasks.remove(task_id)
            
            if not current_wave:
                # Circular dependency or error
                logger.warning("Circular dependency detected, adding remaining tasks")
                current_wave = [dependency_graph[task_id]["task"] for task_id in remaining_tasks]
                remaining_tasks.clear()
            
            execution_waves.append(current_wave)
        
        return {
            "execution_waves": execution_waves,
            "total_tasks": len(tasks),
            "estimated_total_duration": sum(wave[0].estimated_duration for wave in execution_waves),
            "max_parallelism": max(len(wave) for wave in execution_waves),
            "dependency_graph": dependency_graph
        }
    
    async def _execute_coordinated_parallel_tasks(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tasks in parallel with coordination and resource management."""
        
        execution_waves = execution_plan["execution_waves"]
        all_results = {}
        
        for wave_idx, wave_tasks in enumerate(execution_waves):
            logger.info(f"Executing wave {wave_idx + 1}/{len(execution_waves)} with {len(wave_tasks)} tasks")
            
            # Wait for resource availability
            available_tasks = []
            for task in wave_tasks:
                if self.resource_pool.can_allocate(task.resource_requirements):
                    available_tasks.append(task)
                    self.resource_pool.allocate(task.resource_requirements)
                    task.status = TaskStatus.QUEUED
                else:
                    # If resources not available, queue for later
                    self.task_queue.put(task)
            
            # Execute available tasks in parallel
            if available_tasks:
                wave_results = await self._execute_task_wave(available_tasks)
                all_results.update(wave_results)
                
                # Release resources
                for task in available_tasks:
                    self.resource_pool.release(task.resource_requirements)
            
            # Handle queued tasks
            await self._process_queued_tasks()
        
        return all_results
    
    async def _execute_task_wave(self, tasks: List[ExecutionTask]) -> Dict[str, Any]:
        """Execute a wave of tasks in parallel."""
        
        # Create async tasks for parallel execution
        async_tasks = []
        for task in tasks:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            
            if task.agent_id == "coordination_engine":
                async_task = self._execute_coordination_task(task)
            else:
                async_task = self._execute_agent_task(task)
            
            async_tasks.append(async_task)
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Process results
        wave_results = {}
        for task, result in zip(tasks, results):
            task.end_time = datetime.now()
            
            if isinstance(result, Exception):
                task.status = TaskStatus.FAILED
                task.error = str(result)
                logger.error(f"Task {task.task_id} failed: {result}")
            else:
                task.status = TaskStatus.COMPLETED
                task.result = result
                
            wave_results[task.agent_id] = task
            self.running_tasks[task.task_id] = task
        
        return wave_results
    
    async def _execute_agent_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute a task using a specific agent."""
        
        agent = self.agents.get(task.agent_id)
        if not agent:
            raise ValueError(f"Agent {task.agent_id} not found")
        
        # Execute the autonomous research cycle
        result = await agent.autonomous_research_cycle(task.objective, task.context)
        
        # Add coordination information to shared insights
        if result and not result.get("error"):
            self.shared_insights[task.agent_id] = {
                "insights": result.get("insights", []),
                "competitive_edges": result.get("competitive_edges", []),
                "confidence": result.get("synthesis", {}).get("overall_confidence", 0.5),
                "timestamp": datetime.now().isoformat()
            }
        
        return result
    
    async def _execute_coordination_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute a coordination task to integrate insights across agents."""
        
        try:
            # Collect insights from all agents
            agent_insights = []
            for agent_id, insight_data in self.shared_insights.items():
                agent_insights.append({
                    "agent_id": agent_id,
                    "specialization": self.agents[agent_id].specialization,
                    **insight_data
                })
            
            if not agent_insights:
                return {"coordination_result": "No insights available for coordination"}
            
            # Use orchestrator to synthesize insights
            coordination_result = await self.orchestrator._synthesize_agent_results(
                {agent["agent_id"]: agent for agent in agent_insights},
                task.context
            )
            
            return {
                "coordination_result": coordination_result,
                "agents_coordinated": len(agent_insights),
                "coordination_type": task.context.get("coordination_type", "insight_sharing")
            }
            
        except Exception as e:
            logger.error(f"Coordination task error: {e}")
            return {"error": str(e)}
    
    async def _process_queued_tasks(self):
        """Process tasks waiting in the queue when resources become available."""
        
        processed_tasks = []
        
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                
                if self.resource_pool.can_allocate(task.resource_requirements):
                    self.resource_pool.allocate(task.resource_requirements)
                    
                    # Execute task
                    result = await self._execute_task_wave([task])
                    processed_tasks.append(result)
                    
                    self.resource_pool.release(task.resource_requirements)
                else:
                    # Put back in queue if resources still not available
                    self.task_queue.put(task)
                    break
                    
            except Exception as e:
                logger.error(f"Error processing queued task: {e}")
                break
        
        return processed_tasks
    
    async def _synthesize_mission_results(self, 
                                        execution_results: Dict[str, Any], 
                                        mission_objective: str) -> Dict[str, Any]:
        """Synthesize results from all agents into comprehensive mission insights."""
        
        try:
            # Extract successful results
            successful_results = {}
            for agent_id, task in execution_results.items():
                if task.status == TaskStatus.COMPLETED and task.result and not task.result.get("error"):
                    successful_results[agent_id] = task.result
            
            if not successful_results:
                return {"synthesis": "No successful results to synthesize"}
            
            # Use orchestrator for synthesis
            synthesis_result = await self.orchestrator._synthesize_agent_results(
                successful_results, 
                {"mission_objective": mission_objective}
            )
            
            # Add mission-level insights
            mission_insights = {
                "mission_objective": mission_objective,
                "agents_participated": len(successful_results),
                "total_insights_generated": sum(
                    len(result.get("insights", [])) 
                    for result in successful_results.values()
                ),
                "synthesis": synthesis_result,
                "cross_agent_patterns": self._identify_cross_agent_patterns(successful_results),
                "confidence_distribution": self._analyze_confidence_distribution(successful_results)
            }
            
            return mission_insights
            
        except Exception as e:
            logger.error(f"Mission synthesis error: {e}")
            return {"synthesis_error": str(e)}
    
    def _identify_cross_agent_patterns(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns that appear across multiple agents."""
        
        patterns = []
        
        # Extract all insights from all agents
        all_insights = []
        for agent_id, result in results.items():
            agent_insights = result.get("insights", [])
            for insight in agent_insights:
                all_insights.append({
                    "agent_id": agent_id,
                    "agent_specialization": self.agents[agent_id].specialization,
                    "insight": insight
                })
        
        # Simple pattern matching (in a full implementation, this would use NLP)
        common_themes = {}
        for insight_data in all_insights:
            insight = insight_data["insight"]
            insight_text = str(insight.get("insight", "")).lower()
            
            # Extract key terms
            key_terms = insight_text.split()[:5]  # Simple keyword extraction
            
            for term in key_terms:
                if len(term) > 4:  # Ignore short words
                    if term not in common_themes:
                        common_themes[term] = []
                    common_themes[term].append(insight_data)
        
        # Identify themes mentioned by multiple agents
        for theme, mentions in common_themes.items():
            if len(mentions) > 1:
                patterns.append({
                    "theme": theme,
                    "mentioned_by": len(mentions),
                    "agents": [m["agent_id"] for m in mentions],
                    "specializations": [m["agent_specialization"] for m in mentions]
                })
        
        return patterns
    
    def _analyze_confidence_distribution(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence distribution across agent results."""
        
        confidences = []
        by_specialization = {}
        
        for agent_id, result in results.items():
            agent_spec = self.agents[agent_id].specialization
            agent_confidence = result.get("synthesis", {}).get("overall_confidence", 0.5)
            
            confidences.append(agent_confidence)
            
            if agent_spec not in by_specialization:
                by_specialization[agent_spec] = []
            by_specialization[agent_spec].append(agent_confidence)
        
        return {
            "overall_avg": sum(confidences) / len(confidences) if confidences else 0,
            "overall_min": min(confidences) if confidences else 0,
            "overall_max": max(confidences) if confidences else 0,
            "by_specialization": {
                spec: {
                    "avg": sum(confs) / len(confs),
                    "count": len(confs)
                }
                for spec, confs in by_specialization.items()
            }
        }
    
    def _analyze_mission_performance(self, execution_results: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Analyze performance metrics for the mission."""
        
        total_duration = time.time() - start_time
        successful_tasks = sum(1 for task in execution_results.values() if task.status == TaskStatus.COMPLETED)
        total_tasks = len(execution_results)
        
        # Calculate parallel efficiency
        total_sequential_time = sum(
            (task.end_time - task.start_time).total_seconds()
            for task in execution_results.values()
            if task.start_time and task.end_time
        )
        
        parallel_efficiency = total_sequential_time / (total_duration * total_tasks) if total_duration > 0 else 0
        
        return {
            "total_duration": total_duration,
            "successful_tasks": successful_tasks,
            "total_tasks": total_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "parallel_efficiency": min(parallel_efficiency, 1.0),
            "avg_task_duration": total_sequential_time / total_tasks if total_tasks > 0 else 0,
            "resource_utilization": {
                "max_concurrent_tasks": self.resource_pool.active_tasks,
                "api_calls_used": self.resource_pool.api_call_count
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        
        return {
            "execution_engine": {
                "active_agents": len(self.agents),
                "running_tasks": len(self.running_tasks),
                "queued_tasks": self.task_queue.qsize(),
                "execution_stats": self.execution_stats
            },
            "resource_pool": {
                "active_tasks": self.resource_pool.active_tasks,
                "max_concurrent": self.resource_pool.max_concurrent_tasks,
                "api_calls_used": self.resource_pool.api_call_count,
                "memory_usage": self.resource_pool.memory_usage
            },
            "agents": {
                agent_id: agent.get_agent_status()
                for agent_id, agent in self.agents.items()
            },
            "shared_insights": len(self.shared_insights),
            "coordination_channels": len(self.agent_coordination_channels)
        }

# Helper classes
class LoadBalancer:
    """Load balancer for distributing tasks across agents."""
    
    def __init__(self):
        self.agent_loads: Dict[str, float] = {}
        self.agent_performance: Dict[str, float] = {}
    
    def get_optimal_agent(self, available_agents: List[str], task_requirements: Dict[str, Any]) -> str:
        """Get the optimal agent for a task based on load and performance."""
        if not available_agents:
            return None
        
        # Simple load balancing - choose agent with lowest current load
        return min(available_agents, key=lambda agent_id: self.agent_loads.get(agent_id, 0))

class PerformanceMonitor:
    """Monitor and analyze system performance."""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.performance_trends: Dict[str, List[float]] = {}
    
    def record_performance(self, metrics: Dict[str, Any]):
        """Record performance metrics."""
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            **metrics
        })
        
        # Limit history size
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

# Global parallel execution engine
execution_engine = ParallelExecutionEngine()

# Initialize agent pool on import
agent_pool = execution_engine.initialize_agent_pool()
logger.info(f"Parallel Execution System initialized with {len(agent_pool)} agents") 