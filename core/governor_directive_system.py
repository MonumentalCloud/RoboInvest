"""
Governor Directive System - Central Context Manager & Directive Propagation

This system serves as the single source of truth for:
1. Human Governor directives and system changes
2. Context propagation to all agents
3. System-wide parameter updates
4. Mission alignment and governance
5. Real-time directive streaming to frontend

The flow: Human Governor → Governor Agent → Meta Agents → Specialized Agents
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
import uuid
from contextlib import asynccontextmanager

from utils.logger import logger
from core.central_event_bus import central_event_bus, EventType, EventPriority, capture_meta_agent_event


class DirectiveType(Enum):
    """Types of directives that can be issued"""
    MISSION_UPDATE = "mission_update"
    STRATEGY_CHANGE = "strategy_change"
    RISK_ADJUSTMENT = "risk_adjustment"
    AGENT_CONFIG = "agent_config"
    SYSTEM_PARAMETER = "system_parameter"
    RESEARCH_PRIORITY = "research_priority"
    TRADING_RULES = "trading_rules"
    EMERGENCY_STOP = "emergency_stop"
    PERFORMANCE_TARGET = "performance_target"
    GOVERNANCE_RULE = "governance_rule"


class DirectivePriority(Enum):
    """Directive priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DirectiveStatus(Enum):
    """Status of directive propagation"""
    PENDING = "pending"
    PROPAGATING = "propagating"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class GovernorDirective:
    """Standardized governor directive structure"""
    directive_id: str
    directive_type: DirectiveType
    priority: DirectivePriority
    timestamp: datetime
    source: str  # "human_governor" or "governor_agent"
    title: str
    description: str
    payload: Dict[str, Any]
    target_agents: List[str]  # Empty list means all agents
    status: DirectiveStatus
    acknowledgments: Dict[str, datetime]  # agent_id -> timestamp
    completion_reports: Dict[str, Dict[str, Any]]  # agent_id -> report
    metadata: Dict[str, Any]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "directive_id": self.directive_id,
            "directive_type": self.directive_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "payload": self.payload,
            "target_agents": self.target_agents,
            "status": self.status.value,
            "acknowledgments": {k: v.isoformat() for k, v in self.acknowledgments.items()},
            "completion_reports": self.completion_reports,
            "metadata": self.metadata,
            "tags": self.tags
        }


@dataclass
class SystemContext:
    """Current system context that all agents should be aware of"""
    mission: str
    current_strategy: str
    risk_parameters: Dict[str, Any]
    performance_targets: Dict[str, Any]
    active_directives: List[str]  # directive IDs
    system_mode: str  # "normal", "conservative", "aggressive", "emergency"
    governance_rules: Dict[str, Any]
    research_priorities: List[str]
    trading_rules: Dict[str, Any]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "mission": self.mission,
            "current_strategy": self.current_strategy,
            "risk_parameters": self.risk_parameters,
            "performance_targets": self.performance_targets,
            "active_directives": self.active_directives,
            "system_mode": self.system_mode,
            "governance_rules": self.governance_rules,
            "research_priorities": self.research_priorities,
            "trading_rules": self.trading_rules,
            "last_updated": self.last_updated.isoformat()
        }


class GovernorDirectiveSystem:
    """Central directive system that manages and propagates governor directives"""
    
    def __init__(self, db_path: str = "data/governor_directives.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Directive storage
        self.directives: Dict[str, GovernorDirective] = {}
        self.active_directives: List[str] = []
        
        # System context
        self.system_context = SystemContext(
            mission="Discover the smartest and greatest upside that nobody is looking at",
            current_strategy="organic_alpha_hunting",
            risk_parameters={
                "max_position_size": 0.02,  # 2% of portfolio
                "max_daily_loss": 0.05,     # 5% daily loss limit
                "correlation_threshold": 0.7,
                "volatility_threshold": 0.3
            },
            performance_targets={
                "daily_return_target": 0.01,  # 1% daily target
                "sharpe_ratio_target": 1.5,
                "max_drawdown": 0.15
            },
            active_directives=[],
            system_mode="normal",
            governance_rules={
                "require_email_approval": True,
                "auto_reject_high_risk_low_upside": True,
                "max_concurrent_positions": 10
            },
            research_priorities=["alpha_discovery", "market_anomalies", "sentiment_analysis"],
            trading_rules={
                "paper_trading_only": True,
                "min_confidence_threshold": 0.7,
                "max_holding_period": 30  # days
            },
            last_updated=datetime.utcnow()
        )
        
        # Subscribers for real-time updates
        self.directive_subscribers: List[Callable[[GovernorDirective], None]] = []
        self.context_subscribers: List[Callable[[SystemContext], None]] = []
        
        # Database connection
        self._init_database()
        
        # Directive processing queue
        self.directive_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        # Context update lock
        self.context_lock = threading.Lock()
        
        logger.info("👑 Governor Directive System initialized")
    
    def _init_database(self):
        """Initialize SQLite database for directive storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Directives table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS directives (
                        directive_id TEXT PRIMARY KEY,
                        directive_type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        source TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        target_agents TEXT NOT NULL,
                        status TEXT NOT NULL,
                        acknowledgments TEXT NOT NULL,
                        completion_reports TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # System context table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_context (
                        context_id TEXT PRIMARY KEY,
                        mission TEXT NOT NULL,
                        current_strategy TEXT NOT NULL,
                        risk_parameters TEXT NOT NULL,
                        performance_targets TEXT NOT NULL,
                        active_directives TEXT NOT NULL,
                        system_mode TEXT NOT NULL,
                        governance_rules TEXT NOT NULL,
                        research_priorities TEXT NOT NULL,
                        trading_rules TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_directive_type ON directives(directive_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_directive_status ON directives(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_directive_source ON directives(source)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_directive_timestamp ON directives(timestamp)")
                
                conn.commit()
                logger.info(f"📊 Governor directive database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize governor directive database: {e}")
    
    async def start(self):
        """Start the directive processing loop"""
        if self.processing_task is None:
            self.processing_task = asyncio.create_task(self._process_directives())
            logger.info("👑 Governor Directive System started")
    
    async def stop(self):
        """Stop the directive processing loop"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
            logger.info("👑 Governor Directive System stopped")
    
    async def _process_directives(self):
        """Process directives from the queue"""
        while True:
            try:
                directive = await self.directive_queue.get()
                await self._propagate_directive(directive)
                self.directive_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing directive: {e}")
    
    async def _propagate_directive(self, directive: GovernorDirective):
        """Propagate directive to target agents"""
        try:
            directive.status = DirectiveStatus.PROPAGATING
            await self._store_directive(directive)
            
            # Emit system event
            capture_meta_agent_event(
                "directive_issued",
                "governor_system",
                f"Directive '{directive.title}' issued to {len(directive.target_agents)} agents",
                {"directive_id": directive.directive_id, "type": directive.directive_type.value}
            )
            
            # Notify subscribers
            self._notify_directive_subscribers(directive)
            
            # Update system context if needed
            if directive.directive_type in [DirectiveType.MISSION_UPDATE, DirectiveType.STRATEGY_CHANGE, 
                                          DirectiveType.RISK_ADJUSTMENT, DirectiveType.SYSTEM_PARAMETER]:
                await self._update_system_context(directive)
            
            logger.info(f"👑 Directive '{directive.title}' propagated to {len(directive.target_agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to propagate directive: {e}")
            directive.status = DirectiveStatus.FAILED
            await self._store_directive(directive)
    
    async def _update_system_context(self, directive: GovernorDirective):
        """Update system context based on directive"""
        with self.context_lock:
            if directive.directive_type == DirectiveType.MISSION_UPDATE:
                self.system_context.mission = directive.payload.get("mission", self.system_context.mission)
            elif directive.directive_type == DirectiveType.STRATEGY_CHANGE:
                self.system_context.current_strategy = directive.payload.get("strategy", self.system_context.current_strategy)
            elif directive.directive_type == DirectiveType.RISK_ADJUSTMENT:
                self.system_context.risk_parameters.update(directive.payload.get("risk_parameters", {}))
            elif directive.directive_type == DirectiveType.SYSTEM_PARAMETER:
                # Update any system parameter
                for key, value in directive.payload.items():
                    if hasattr(self.system_context, key):
                        setattr(self.system_context, key, value)
            
            self.system_context.active_directives = [d for d in self.active_directives if d in self.directives]
            self.system_context.last_updated = datetime.utcnow()
            
            # Store updated context
            await self._store_system_context()
            
            # Notify context subscribers
            self._notify_context_subscribers()
    
    async def _store_directive(self, directive: GovernorDirective):
        """Store directive in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO directives 
                    (directive_id, directive_type, priority, timestamp, source, title, description, 
                     payload, target_agents, status, acknowledgments, completion_reports, metadata, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    directive.directive_id,
                    directive.directive_type.value,
                    directive.priority.value,
                    directive.timestamp.isoformat(),
                    directive.source,
                    directive.title,
                    directive.description,
                    json.dumps(directive.payload),
                    json.dumps(directive.target_agents),
                    directive.status.value,
                    json.dumps({k: v.isoformat() for k, v in directive.acknowledgments.items()}),
                    json.dumps(directive.completion_reports),
                    json.dumps(directive.metadata),
                    json.dumps(directive.tags)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store directive: {e}")
    
    async def _store_system_context(self):
        """Store system context in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO system_context 
                    (context_id, mission, current_strategy, risk_parameters, performance_targets,
                     active_directives, system_mode, governance_rules, research_priorities, trading_rules, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "current",
                    self.system_context.mission,
                    self.system_context.current_strategy,
                    json.dumps(self.system_context.risk_parameters),
                    json.dumps(self.system_context.performance_targets),
                    json.dumps(self.system_context.active_directives),
                    self.system_context.system_mode,
                    json.dumps(self.system_context.governance_rules),
                    json.dumps(self.system_context.research_priorities),
                    json.dumps(self.system_context.trading_rules),
                    self.system_context.last_updated.isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store system context: {e}")
    
    def subscribe_to_directives(self, callback: Callable[[GovernorDirective], None]):
        """Subscribe to directive updates"""
        self.directive_subscribers.append(callback)
    
    def unsubscribe_from_directives(self, callback: Callable[[GovernorDirective], None]):
        """Unsubscribe from directive updates"""
        if callback in self.directive_subscribers:
            self.directive_subscribers.remove(callback)
    
    def subscribe_to_context(self, callback: Callable[[SystemContext], None]):
        """Subscribe to context updates"""
        self.context_subscribers.append(callback)
    
    def unsubscribe_from_context(self, callback: Callable[[SystemContext], None]):
        """Unsubscribe from context updates"""
        if callback in self.context_subscribers:
            self.context_subscribers.remove(callback)
    
    def _notify_directive_subscribers(self, directive: GovernorDirective):
        """Notify all directive subscribers"""
        for callback in self.directive_subscribers:
            try:
                callback(directive)
            except Exception as e:
                logger.error(f"Error in directive subscriber callback: {e}")
    
    def _notify_context_subscribers(self):
        """Notify all context subscribers"""
        for callback in self.context_subscribers:
            try:
                callback(self.system_context)
            except Exception as e:
                logger.error(f"Error in context subscriber callback: {e}")
    
    async def issue_directive(self, 
                            directive_type: DirectiveType,
                            title: str,
                            description: str,
                            payload: Dict[str, Any],
                            target_agents: Optional[List[str]] = None,
                            priority: DirectivePriority = DirectivePriority.MEDIUM,
                            source: str = "human_governor",
                            metadata: Optional[Dict[str, Any]] = None,
                            tags: Optional[List[str]] = None) -> str:
        """Issue a new directive"""
        
        directive_id = f"directive_{uuid.uuid4().hex[:8]}"
        
        directive = GovernorDirective(
            directive_id=directive_id,
            directive_type=directive_type,
            priority=priority,
            timestamp=datetime.utcnow(),
            source=source,
            title=title,
            description=description,
            payload=payload,
            target_agents=target_agents or [],
            status=DirectiveStatus.PENDING,
            acknowledgments={},
            completion_reports={},
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Store directive
        self.directives[directive_id] = directive
        if directive.status == DirectiveStatus.PENDING:
            self.active_directives.append(directive_id)
        
        # Queue for processing
        await self.directive_queue.put(directive)
        
        logger.info(f"👑 Directive '{title}' issued (ID: {directive_id})")
        return directive_id
    
    def acknowledge_directive(self, directive_id: str, agent_id: str) -> bool:
        """Acknowledge receipt of a directive"""
        if directive_id not in self.directives:
            return False
        
        directive = self.directives[directive_id]
        directive.acknowledgments[agent_id] = datetime.utcnow()
        
        # Update status if all target agents have acknowledged
        if directive.target_agents and all(agent in directive.acknowledgments for agent in directive.target_agents):
            directive.status = DirectiveStatus.ACKNOWLEDGED
        
        asyncio.create_task(self._store_directive(directive))
        return True
    
    def report_directive_completion(self, directive_id: str, agent_id: str, report: Dict[str, Any]) -> bool:
        """Report completion of a directive"""
        if directive_id not in self.directives:
            return False
        
        directive = self.directives[directive_id]
        directive.completion_reports[agent_id] = report
        
        # Update status if all target agents have completed
        if directive.target_agents and all(agent in directive.completion_reports for agent in directive.target_agents):
            directive.status = DirectiveStatus.COMPLETED
            if directive_id in self.active_directives:
                self.active_directives.remove(directive_id)
        
        asyncio.create_task(self._store_directive(directive))
        return True
    
    def get_system_context(self) -> SystemContext:
        """Get current system context"""
        return self.system_context
    
    def get_active_directives(self) -> List[GovernorDirective]:
        """Get all active directives"""
        return [self.directives[did] for did in self.active_directives if did in self.directives]
    
    def get_directive(self, directive_id: str) -> Optional[GovernorDirective]:
        """Get a specific directive"""
        return self.directives.get(directive_id)
    
    def get_directives_for_agent(self, agent_id: str) -> List[GovernorDirective]:
        """Get all directives targeting a specific agent"""
        return [
            directive for directive in self.directives.values()
            if not directive.target_agents or agent_id in directive.target_agents
        ]
    
    @asynccontextmanager
    async def context_update(self):
        """Context manager for updating system context"""
        with self.context_lock:
            try:
                yield self.system_context
                self.system_context.last_updated = datetime.utcnow()
                await self._store_system_context()
                self._notify_context_subscribers()
            except Exception as e:
                logger.error(f"Error in context update: {e}")
                raise


# Global instance
governor_directive_system = GovernorDirectiveSystem()


# Convenience functions for issuing common directives
async def update_mission(new_mission: str, source: str = "human_governor") -> str:
    """Update the system mission"""
    return await governor_directive_system.issue_directive(
        directive_type=DirectiveType.MISSION_UPDATE,
        title="Mission Update",
        description=f"System mission updated to: {new_mission}",
        payload={"mission": new_mission},
        source=source
    )

async def update_strategy(new_strategy: str, strategy_params: Dict[str, Any], source: str = "human_governor") -> str:
    """Update the trading strategy"""
    return await governor_directive_system.issue_directive(
        directive_type=DirectiveType.STRATEGY_CHANGE,
        title="Strategy Change",
        description=f"Trading strategy updated to: {new_strategy}",
        payload={"strategy": new_strategy, "parameters": strategy_params},
        source=source
    )

async def adjust_risk_parameters(risk_params: Dict[str, Any], source: str = "human_governor") -> str:
    """Adjust risk parameters"""
    return await governor_directive_system.issue_directive(
        directive_type=DirectiveType.RISK_ADJUSTMENT,
        title="Risk Parameter Adjustment",
        description="Risk parameters have been adjusted",
        payload={"risk_parameters": risk_params},
        source=source
    )

async def emergency_stop(reason: str, source: str = "human_governor") -> str:
    """Emergency stop all trading"""
    return await governor_directive_system.issue_directive(
        directive_type=DirectiveType.EMERGENCY_STOP,
        title="Emergency Stop",
        description=f"Emergency stop initiated: {reason}",
        payload={"reason": reason, "stop_all_trading": True},
        priority=DirectivePriority.EMERGENCY,
        source=source
    )

async def update_research_priorities(priorities: List[str], source: str = "human_governor") -> str:
    """Update research priorities"""
    return await governor_directive_system.issue_directive(
        directive_type=DirectiveType.RESEARCH_PRIORITY,
        title="Research Priority Update",
        description="Research priorities have been updated",
        payload={"research_priorities": priorities},
        source=source
    ) 