"""
Central Event Bus for RoboInvest System

Captures and broadcasts all system events from:
- AI thoughts (broadcast_ai_thought)
- System logs (logger calls)
- Trade events (structured orders)
- Play events (play executor)
- Meta-agent events
- Notification events
- Performance events
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
import uuid

from utils.logger import logger


class EventType(Enum):
    """Types of events that can be captured"""
    AI_THOUGHT = "ai_thought"
    SYSTEM_LOG = "system_log"
    TRADE_EVENT = "trade_event"
    PLAY_EVENT = "play_event"
    META_AGENT = "meta_agent"
    NOTIFICATION = "notification"
    PERFORMANCE = "performance"
    RESEARCH = "research"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SystemEvent:
    """Standardized system event structure"""
    event_id: str
    event_type: EventType
    priority: EventPriority
    timestamp: datetime
    source: str
    title: str
    message: str
    metadata: Dict[str, Any]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "tags": self.tags
        }


class CentralEventBus:
    """Central event bus that captures and stores all system events"""
    
    def __init__(self, db_path: str = "data/central_events.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Event storage
        self.events: List[SystemEvent] = []
        self.max_events = 10000  # Keep last 10k events in memory
        
        # Subscribers for real-time updates
        self.subscribers: List[Callable[[SystemEvent], None]] = []
        
        # Database connection
        self._init_database()
        
        # Event processing queue
        self.event_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        logger.info("🚌 Central Event Bus initialized")
    
    def _init_database(self):
        """Initialize SQLite database for event storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Events table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        source TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Research trees table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS research_trees (
                        tree_id TEXT PRIMARY KEY,
                        agent_name TEXT NOT NULL,
                        track_name TEXT NOT NULL,
                        root_id TEXT NOT NULL,
                        tree_data TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Research tree nodes table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS research_tree_nodes (
                        node_id TEXT PRIMARY KEY,
                        tree_id TEXT NOT NULL,
                        parent_id TEXT,
                        node_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        metadata TEXT,
                        confidence REAL,
                        progress INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tree_id) REFERENCES research_trees(tree_id),
                        FOREIGN KEY (parent_id) REFERENCES research_tree_nodes(node_id)
                    )
                """)
                
                # Create indexes for efficient querying
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON events(source)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON events(priority)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tree_agent ON research_trees(agent_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tree_track ON research_trees(track_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_node_tree ON research_tree_nodes(tree_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_node_parent ON research_tree_nodes(parent_id)")
                
                conn.commit()
                logger.info(f"📊 Event and research database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    async def start(self):
        """Start the event processing loop"""
        if self.processing_task is None:
            self.processing_task = asyncio.create_task(self._process_events())
            logger.info("🚌 Central Event Bus started")
    
    async def stop(self):
        """Stop the event processing loop"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
            logger.info("🚌 Central Event Bus stopped")
    
    async def _process_events(self):
        """Process events from the queue"""
        while True:
            try:
                event = await self.event_queue.get()
                await self._store_event(event)
                self._notify_subscribers(event)
                self.event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    def emit_event(self, event: SystemEvent):
        """Emit an event to the bus (non-blocking)"""
        try:
            # Add to memory cache
            self.events.append(event)
            if len(self.events) > self.max_events:
                self.events.pop(0)  # Remove oldest event
            
            # Add to processing queue
            asyncio.create_task(self.event_queue.put(event))
        except Exception as e:
            logger.error(f"Error emitting event: {e}")
    
    async def _store_event(self, event: SystemEvent):
        """Store event in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (event_id, event_type, priority, timestamp, source, title, message, metadata, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.event_type.value,
                    event.priority.value,
                    event.timestamp.isoformat(),
                    event.source,
                    event.title,
                    event.message,
                    json.dumps(event.metadata),
                    json.dumps(event.tags)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store event: {e}")
    
    def subscribe(self, callback: Callable[[SystemEvent], None]):
        """Subscribe to real-time event updates"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[SystemEvent], None]):
        """Unsubscribe from real-time event updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _notify_subscribers(self, event: SystemEvent):
        """Notify all subscribers of a new event"""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")
    
    def get_recent_events(self, limit: int = 100, event_types: Optional[List[EventType]] = None) -> List[Dict[str, Any]]:
        """Get recent events from memory cache"""
        events = self.events
        
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        # Return most recent events
        recent_events = events[-limit:] if len(events) > limit else events
        return [e.to_dict() for e in recent_events]
    
    def get_events_from_db(self, 
                          limit: int = 100, 
                          event_types: Optional[List[str]] = None,
                          sources: Optional[List[str]] = None,
                          since: Optional[datetime] = None,
                          until: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get events from database with filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if event_types:
                    placeholders = ','.join(['?' for _ in event_types])
                    query += f" AND event_type IN ({placeholders})"
                    params.extend(event_types)
                
                if sources:
                    placeholders = ','.join(['?' for _ in sources])
                    query += f" AND source IN ({placeholders})"
                    params.extend(sources)
                
                if since:
                    query += " AND timestamp >= ?"
                    params.append(since.isoformat())
                
                if until:
                    query += " AND timestamp <= ?"
                    params.append(until.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = {
                        "event_id": row[0],
                        "event_type": row[1],
                        "priority": row[2],
                        "timestamp": row[3],
                        "source": row[4],
                        "title": row[5],
                        "message": row[6],
                        "metadata": json.loads(row[7]),
                        "tags": json.loads(row[8]),
                        "created_at": row[9]
                    }
                    events.append(event)
                
                return events
        except Exception as e:
            logger.error(f"Failed to get events from database: {e}")
            return []
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Event statistics
                total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                events_by_type = dict(conn.execute("""
                    SELECT event_type, COUNT(*) FROM events GROUP BY event_type
                """).fetchall())
                events_by_priority = dict(conn.execute("""
                    SELECT priority, COUNT(*) FROM events GROUP BY priority
                """).fetchall())
                events_by_source = dict(conn.execute("""
                    SELECT source, COUNT(*) FROM events GROUP BY source
                """).fetchall())
                
                # Research tree statistics
                total_trees = conn.execute("SELECT COUNT(*) FROM research_trees").fetchone()[0]
                total_nodes = conn.execute("SELECT COUNT(*) FROM research_tree_nodes").fetchone()[0]
                trees_by_agent = dict(conn.execute("""
                    SELECT agent_name, COUNT(*) FROM research_trees GROUP BY agent_name
                """).fetchall())
                
                return {
                    "total_events": total_events,
                    "events_by_type": events_by_type,
                    "events_by_priority": events_by_priority,
                    "events_by_source": events_by_source,
                    "total_research_trees": total_trees,
                    "total_research_nodes": total_nodes,
                    "trees_by_agent": trees_by_agent,
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to get event statistics: {e}")
            return {}
    
    def _clean_for_json(self, obj: Any) -> Any:
        """Clean object for JSON serialization by removing non-serializable items"""
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items() 
                   if not k.startswith('_') and not callable(v)}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)  # Convert other types to string

    def save_research_tree(self, tree_id: str, agent_name: str, track_name: str, root_id: str, tree_data: Dict[str, Any]):
        """Save a research tree to the database"""
        try:
            # Clean the tree_data for JSON serialization
            cleaned_tree_data = self._clean_for_json(tree_data)
            
            with sqlite3.connect(self.db_path) as conn:
                # Save tree metadata
                conn.execute("""
                    INSERT OR REPLACE INTO research_trees (tree_id, agent_name, track_name, root_id, tree_data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tree_id,
                    agent_name,
                    track_name,
                    root_id,
                    json.dumps(cleaned_tree_data),
                    datetime.now().isoformat()
                ))
                
                # Save tree nodes
                if 'nodes' in tree_data:
                    for node_id, node_data in tree_data['nodes'].items():
                        conn.execute("""
                            INSERT OR REPLACE INTO research_tree_nodes 
                            (node_id, tree_id, parent_id, node_type, title, content, status, metadata, confidence, progress, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            node_id,
                            tree_id,
                            node_data.get('parent_id'),
                            node_data.get('type', 'unknown'),
                            node_data.get('title', node_data.get('content', '')),
                            node_data.get('content', ''),
                            node_data.get('status', 'pending'),
                            json.dumps(self._clean_for_json(node_data.get('metadata', {}))),
                            node_data.get('confidence'),
                            node_data.get('progress', 0),
                            datetime.now().isoformat()
                        ))
                
                conn.commit()
                logger.info(f"📊 Saved research tree {tree_id} to database")
        except Exception as e:
            logger.error(f"Failed to save research tree: {e}")
    
    def get_research_trees(self, agent_name: Optional[str] = None, track_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get research trees from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM research_trees WHERE 1=1"
                params = []
                
                if agent_name:
                    query += " AND agent_name = ?"
                    params.append(agent_name)
                
                if track_name:
                    query += " AND track_name = ?"
                    params.append(track_name)
                
                query += " ORDER BY created_at DESC"
                
                trees = []
                for row in conn.execute(query, params).fetchall():
                    tree_data = json.loads(row[4])  # tree_data column
                    trees.append({
                        "tree_id": row[0],
                        "agent_name": row[1],
                        "track_name": row[2],
                        "root_id": row[3],
                        "tree_data": tree_data,
                        "status": row[5],
                        "created_at": row[6],
                        "updated_at": row[7]
                    })
                
                return trees
        except Exception as e:
            logger.error(f"Failed to get research trees: {e}")
            return []
    
    def get_research_tree_nodes(self, tree_id: str) -> List[Dict[str, Any]]:
        """Get all nodes for a specific research tree"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                nodes = []
                for row in conn.execute("""
                    SELECT * FROM research_tree_nodes WHERE tree_id = ? ORDER BY created_at
                """, (tree_id,)).fetchall():
                    nodes.append({
                        "id": row[0],
                        "tree_id": row[1],
                        "parent": row[2],
                        "type": row[3],
                        "title": row[4],
                        "content": row[5],
                        "status": row[6],
                        "metadata": json.loads(row[7]) if row[7] else {},
                        "confidence": row[8],
                        "progress": row[9],
                        "timestamp": row[10]
                    })
                
                return nodes
        except Exception as e:
            logger.error(f"Failed to get research tree nodes: {e}")
            return [] 


# Global event bus instance
central_event_bus = CentralEventBus()


# Event creation helpers
def create_event(event_type: EventType, 
                source: str, 
                title: str, 
                message: str, 
                priority: EventPriority = EventPriority.MEDIUM,
                metadata: Optional[Dict[str, Any]] = None,
                tags: Optional[List[str]] = None) -> SystemEvent:
    """Create a new system event"""
    return SystemEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        priority=priority,
        timestamp=datetime.now(),
        source=source,
        title=title,
        message=message,
        metadata=metadata or {},
        tags=tags or []
    )


def emit_system_event(event_type: EventType,
                     source: str,
                     title: str,
                     message: str,
                     priority: EventPriority = EventPriority.MEDIUM,
                     metadata: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None):
    """Emit a system event to the central bus"""
    event = create_event(event_type, source, title, message, priority, metadata, tags)
    central_event_bus.emit_event(event)


# Integration with existing systems
def capture_ai_thought(thought_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
    """Capture AI thoughts from broadcast_ai_thought"""
    priority = EventPriority.HIGH if "error" in thought_type.lower() else EventPriority.MEDIUM
    tags = ["ai", "thought", thought_type]
    
    emit_system_event(
        event_type=EventType.AI_THOUGHT,
        source="ai_system",
        title=f"AI Thought: {thought_type}",
        message=content,
        priority=priority,
        metadata=metadata or {},
        tags=tags
    )


def capture_log_event(level: str, message: str, context: str = "system"):
    """Capture log events from logger"""
    event_type_map = {
        "error": EventType.ERROR,
        "warning": EventType.WARNING,
        "info": EventType.INFO,
        "debug": EventType.INFO
    }
    
    priority_map = {
        "error": EventPriority.HIGH,
        "warning": EventPriority.MEDIUM,
        "info": EventPriority.LOW,
        "debug": EventPriority.LOW
    }
    
    event_type = event_type_map.get(level, EventType.INFO)
    priority = priority_map.get(level, EventPriority.LOW)
    
    emit_system_event(
        event_type=event_type,
        source=context,
        title=f"{level.upper()}: {context}",
        message=message,
        priority=priority,
        tags=[level, context]
    )


def capture_trade_event(event_type: str, symbol: str, action: str, quantity: int, metadata: Optional[Dict[str, Any]] = None):
    """Capture trade events from structured orders"""
    emit_system_event(
        event_type=EventType.TRADE_EVENT,
        source="trade_executor",
        title=f"Trade: {action} {quantity} {symbol}",
        message=f"Executed {action} order for {quantity} shares of {symbol}",
        priority=EventPriority.HIGH,
        metadata=metadata or {},
        tags=["trade", action.lower(), symbol]
    )


def capture_play_event(event_type: str, play_id: str, action: str, metadata: Optional[Dict[str, Any]] = None):
    """Capture play events from play executor"""
    emit_system_event(
        event_type=EventType.PLAY_EVENT,
        source="play_executor",
        title=f"Play {action}: {play_id}",
        message=f"Play {play_id} {action}",
        priority=EventPriority.MEDIUM,
        metadata=metadata or {},
        tags=["play", action.lower(), play_id]
    )


def capture_meta_agent_event(event_type: str, agent_name: str, message: str, metadata: Optional[Dict[str, Any]] = None):
    """Capture meta-agent events"""
    emit_system_event(
        event_type=EventType.META_AGENT,
        source=f"meta_agent_{agent_name}",
        title=f"Meta Agent: {event_type}",
        message=message,
        priority=EventPriority.MEDIUM,
        metadata=metadata or {},
        tags=["meta_agent", agent_name, event_type.lower()]
    )


def capture_notification_event(notification_type: str, channel: str, message: str, metadata: Optional[Dict[str, Any]] = None):
    """Capture notification events"""
    emit_system_event(
        event_type=EventType.NOTIFICATION,
        source="notification_system",
        title=f"Notification: {notification_type}",
        message=f"Sent {notification_type} via {channel}: {message}",
        priority=EventPriority.MEDIUM,
        metadata=metadata or {},
        tags=["notification", notification_type.lower(), channel]
    )


def capture_performance_event(metric: str, value: float, context: str = "system", metadata: Optional[Dict[str, Any]] = None):
    """Capture performance events"""
    emit_system_event(
        event_type=EventType.PERFORMANCE,
        source=context,
        title=f"Performance: {metric}",
        message=f"{metric}: {value}",
        priority=EventPriority.LOW,
        metadata=metadata or {},
        tags=["performance", metric.lower(), context]
    )


def capture_research_event(event_type: str, research_id: str, message: str, metadata: Optional[Dict[str, Any]] = None):
    """Capture research events"""
    emit_system_event(
        event_type=EventType.RESEARCH,
        source="research_system",
        title=f"Research: {event_type}",
        message=message,
        priority=EventPriority.MEDIUM,
        metadata=metadata or {},
        tags=["research", event_type.lower(), research_id]
    ) 