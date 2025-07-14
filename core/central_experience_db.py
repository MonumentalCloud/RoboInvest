"""
Central Experience Database System

Hybrid memory architecture combining:
- ChromaDB for semantic (vector) search and recall
- SQLite for structured events, session context, and cross-agent memory
- LLM-based intelligent pruning and importance scoring
"""

import asyncio
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import threading
import queue

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger


class ExperienceType(Enum):
    """Types of experiences stored in the central database"""
    USER_QUERY = "user_query"
    AGENT_RESPONSE = "agent_response"
    VISUALIZATION = "visualization"
    TRADE_EXECUTION = "trade_execution"
    MARKET_INSIGHT = "market_insight"
    SYSTEM_ERROR = "system_error"
    AGENT_LEARNING = "agent_learning"
    SESSION_CONTEXT = "session_context"
    REFERENCE_RESOLUTION = "reference_resolution"


class MemoryTier(Enum):
    """Memory tiers for intelligent retention"""
    HOT = "hot"           # Recent, frequently accessed
    WARM = "warm"         # Important but less recent
    COLD = "cold"         # Archived, rarely accessed
    PRUNED = "pruned"     # Marked for deletion


@dataclass
class Experience:
    """Structured experience data"""
    id: str
    timestamp: datetime
    experience_type: ExperienceType
    source_agent: str
    content: str
    metadata: Dict[str, Any]
    importance_score: float
    memory_tier: MemoryTier
    session_id: Optional[str] = None
    user_message: Optional[str] = None
    references: List[str] = None  # IDs of related experiences
    
    def __post_init__(self):
        if self.references is None:
            self.references = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['experience_type'] = self.experience_type.value
        data['memory_tier'] = self.memory_tier.value
        return data


class CentralExperienceDB:
    """Central experience database with hybrid storage and intelligent pruning"""
    
    def __init__(self, db_path: str = "data/central_experience.db"):
        self.db_path = db_path
        self.chroma_client = None
        self.chroma_collection = None
        self.sqlite_conn = None
        self.embedding_function = None
        
        # Memory management
        self.pruning_queue = queue.Queue()
        self.pruning_thread = None
        self.pruning_interval = 3600  # 1 hour
        
        # Initialize databases
        self._init_databases()
        self._start_pruning_thread()
        
        logger.info("🧠 Central Experience DB initialized")
    
    def _init_databases(self):
        """Initialize both ChromaDB and SQLite databases"""
        # Initialize ChromaDB
        try:
            if config.openai_api_key:
                self.embedding_function = OpenAIEmbeddingFunction(
                    api_key=config.openai_api_key, 
                    model_name="text-embedding-3-small"
                )
                self.chroma_client = chromadb.PersistentClient(path=config.chroma_db_path)
                self.chroma_collection = self.chroma_client.get_or_create_collection(
                    "central_experiences", 
                    embedding_function=self.embedding_function
                )
                logger.info("✅ ChromaDB initialized with OpenAI embeddings")
            else:
                logger.warning("⚠️ OpenAI key not set - ChromaDB disabled")
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
        
        # Initialize SQLite
        try:
            self.sqlite_conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._create_sqlite_tables()
            logger.info("✅ SQLite database initialized")
        except Exception as e:
            logger.error(f"❌ SQLite initialization failed: {e}")
    
    def _create_sqlite_tables(self):
        """Create SQLite tables for structured data"""
        cursor = self.sqlite_conn.cursor()
        
        # Main experiences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                experience_type TEXT NOT NULL,
                source_agent TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                importance_score REAL NOT NULL,
                memory_tier TEXT NOT NULL,
                session_id TEXT,
                user_message TEXT,
                experience_references TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Session context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_contexts (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                current_context TEXT,
                recent_experiences TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Memory management table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_experiences INTEGER,
                hot_memory_count INTEGER,
                warm_memory_count INTEGER,
                cold_memory_count INTEGER,
                pruned_count INTEGER,
                last_pruning TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON experiences(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_experience_type ON experiences(experience_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_agent ON experiences(source_agent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_tier ON experiences(memory_tier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON experiences(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance_score ON experiences(importance_score)")
        
        self.sqlite_conn.commit()
    
    async def add_experience(self, 
                           experience_type: ExperienceType,
                           source_agent: str,
                           content: str,
                           metadata: Dict[str, Any],
                           session_id: Optional[str] = None,
                           user_message: Optional[str] = None,
                           references: List[str] = None) -> str:
        """
        Add a new experience to both ChromaDB and SQLite
        
        Returns:
            Experience ID
        """
        experience_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Get LLM-based importance score
        importance_score = await self._calculate_importance_score(
            content, experience_type, metadata
        )
        
        # Determine initial memory tier
        memory_tier = self._determine_memory_tier(importance_score, experience_type)
        
        # Create experience object
        experience = Experience(
            id=experience_id,
            timestamp=timestamp,
            experience_type=experience_type,
            source_agent=source_agent,
            content=content,
            metadata=metadata,
            importance_score=importance_score,
            memory_tier=memory_tier,
            session_id=session_id,
            user_message=user_message,
            references=references or []
        )
        
        # Store in SQLite
        await self._store_in_sqlite(experience)
        
        # Store in ChromaDB (if available)
        if self.chroma_collection:
            await self._store_in_chromadb(experience)
        
        # Update session context if session_id provided
        if session_id:
            await self._update_session_context(session_id, experience)
        
        # Queue for pruning consideration
        self.pruning_queue.put(experience)
        
        logger.info(f"💾 Experience stored: {experience_id} (score: {importance_score:.2f}, tier: {memory_tier.value})")
        
        return experience_id
    
    async def _calculate_importance_score(self, content: str, experience_type: ExperienceType, metadata: Dict[str, Any]) -> float:
        """Use LLM to calculate importance score (1-10) for an experience"""
        try:
            prompt = f"""
            Rate this experience's importance (1-10) for an autonomous trading system:
            
            Experience Type: {experience_type.value}
            Content: {content[:500]}...
            Metadata: {json.dumps(metadata, indent=2)}
            
            Consider:
            - User value and relevance (how useful is this to the user?)
            - System learning potential (does this help the system improve?)
            - Market/trading significance (is this related to trading decisions?)
            - Uniqueness of insight (is this new or unique information?)
            - Long-term utility (will this be useful in the future?)
            
            Return only a number between 1-10, where:
            10 = Critical insight, unique learning, high user value
            7-9 = Important information, good learning potential
            4-6 = Useful but not critical
            1-3 = Low value, routine, or redundant
            
            Score: """
            
            response = await openai_manager.get_completion(prompt, max_tokens=10)
            
            # Extract numeric score
            try:
                score = float(response.strip())
                return max(1.0, min(10.0, score))  # Clamp between 1-10
            except ValueError:
                # Fallback scoring based on type and content
                return self._fallback_importance_score(experience_type, content)
                
        except Exception as e:
            logger.error(f"Error calculating importance score: {e}")
            return self._fallback_importance_score(experience_type, content)
    
    def _fallback_importance_score(self, experience_type: ExperienceType, content: str) -> float:
        """Fallback importance scoring when LLM is unavailable"""
        base_scores = {
            ExperienceType.TRADE_EXECUTION: 8.0,
            ExperienceType.MARKET_INSIGHT: 7.0,
            ExperienceType.AGENT_LEARNING: 6.0,
            ExperienceType.VISUALIZATION: 5.0,
            ExperienceType.USER_QUERY: 4.0,
            ExperienceType.AGENT_RESPONSE: 3.0,
            ExperienceType.SYSTEM_ERROR: 6.0,
            ExperienceType.SESSION_CONTEXT: 2.0,
            ExperienceType.REFERENCE_RESOLUTION: 3.0
        }
        
        base_score = base_scores.get(experience_type, 3.0)
        
        # Adjust based on content length and keywords
        content_lower = content.lower()
        if any(word in content_lower for word in ['error', 'failed', 'critical']):
            base_score += 1.0
        if any(word in content_lower for word in ['profit', 'gain', 'success']):
            base_score += 0.5
        if len(content) > 500:
            base_score += 0.5
        
        return min(10.0, base_score)
    
    def _determine_memory_tier(self, importance_score: float, experience_type: ExperienceType) -> MemoryTier:
        """Determine initial memory tier based on importance score and type"""
        if importance_score >= 8.0:
            return MemoryTier.HOT
        elif importance_score >= 5.0:
            return MemoryTier.WARM
        else:
            return MemoryTier.COLD
    
    async def _store_in_sqlite(self, experience: Experience):
        """Store experience in SQLite database"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT INTO experiences 
            (id, timestamp, experience_type, source_agent, content, metadata, 
             importance_score, memory_tier, session_id, user_message, experience_references)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            experience.id,
            experience.timestamp.isoformat(),
            experience.experience_type.value,
            experience.source_agent,
            experience.content,
            json.dumps(experience.metadata),
            experience.importance_score,
            experience.memory_tier.value,
            experience.session_id,
            experience.user_message,
            json.dumps(experience.references)
        ))
        self.sqlite_conn.commit()
    
    async def _store_in_chromadb(self, experience: Experience):
        """Store experience in ChromaDB for semantic search"""
        try:
            # Create document for semantic search
            document = f"{experience.content}\n\nType: {experience.experience_type.value}\nAgent: {experience.source_agent}"
            
            self.chroma_collection.add(
                documents=[document],
                metadatas=[{
                    "id": experience.id,
                    "type": experience.experience_type.value,
                    "agent": experience.source_agent,
                    "timestamp": experience.timestamp.isoformat(),
                    "importance": experience.importance_score,
                    "tier": experience.memory_tier.value
                }],
                ids=[experience.id]
            )
        except Exception as e:
            logger.error(f"Error storing in ChromaDB: {e}")
    
    async def query_experiences(self, 
                              query: str, 
                              limit: int = 10, 
                              experience_types: Optional[List[ExperienceType]] = None,
                              min_importance: float = 0.0) -> List[Experience]:
        """
        Query experiences using semantic search (ChromaDB) and structured filters (SQLite)
        """
        experiences = []
        
        # Try semantic search first (if ChromaDB available)
        if self.chroma_collection:
            try:
                semantic_results = self.chroma_collection.query(
                    query_texts=[query],
                    n_results=limit * 2  # Get more results for filtering
                )
                
                if semantic_results['ids'] and semantic_results['ids'][0]:
                    # Get full experience data from SQLite
                    experience_ids = semantic_results['ids'][0]
                    sqlite_results = await self._get_experiences_by_ids(experience_ids)
                    experiences.extend(sqlite_results)
            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
        
        # Fallback to SQLite search if ChromaDB failed or no results
        if not experiences:
            experiences = await self._search_sqlite(query, limit, experience_types, min_importance)
        
        # Sort by importance and recency
        experiences.sort(key=lambda x: (x.importance_score, x.timestamp), reverse=True)
        
        return experiences[:limit]
    
    async def _search_sqlite(self, 
                           query: str, 
                           limit: int, 
                           experience_types: Optional[List[ExperienceType]] = None,
                           min_importance: float = 0.0) -> List[Experience]:
        """Search experiences in SQLite using text search"""
        cursor = self.sqlite_conn.cursor()
        
        # Build query
        sql = """
            SELECT * FROM experiences 
            WHERE content LIKE ? AND importance_score >= ?
        """
        params = [f"%{query}%", min_importance]
        
        if experience_types:
            placeholders = ','.join(['?' for _ in experience_types])
            sql += f" AND experience_type IN ({placeholders})"
            params.extend([t.value for t in experience_types])
        
        sql += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        return [self._row_to_experience(row) for row in rows]
    
    async def _get_experiences_by_ids(self, experience_ids: List[str]) -> List[Experience]:
        """Get experiences by their IDs"""
        if not experience_ids:
            return []
        
        cursor = self.sqlite_conn.cursor()
        placeholders = ','.join(['?' for _ in experience_ids])
        cursor.execute(f"SELECT * FROM experiences WHERE id IN ({placeholders})", experience_ids)
        rows = cursor.fetchall()
        
        return [self._row_to_experience(row) for row in rows]
    
    def _row_to_experience(self, row: Tuple) -> Experience:
        """Convert SQLite row to Experience object"""
        return Experience(
            id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            experience_type=ExperienceType(row[2]),
            source_agent=row[3],
            content=row[4],
            metadata=json.loads(row[5]),
            importance_score=row[6],
            memory_tier=MemoryTier(row[7]),
            session_id=row[8],
            user_message=row[9],
            references=json.loads(row[10]) if row[10] else []
        )
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get current session context"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT current_context, recent_experiences 
            FROM session_contexts 
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                "current_context": json.loads(row[0]) if row[0] else {},
                "recent_experiences": json.loads(row[1]) if row[1] else []
            }
        return {"current_context": {}, "recent_experiences": []}
    
    async def _update_session_context(self, session_id: str, experience: Experience):
        """Update session context with new experience"""
        cursor = self.sqlite_conn.cursor()
        
        # Get current context
        current_context = await self.get_session_context(session_id)
        recent_experiences = current_context["recent_experiences"]
        
        # Add new experience to recent list (keep last 10)
        recent_experiences.append({
            "id": experience.id,
            "type": experience.experience_type.value,
            "content": experience.content[:200] + "..." if len(experience.content) > 200 else experience.content,
            "timestamp": experience.timestamp.isoformat()
        })
        
        if len(recent_experiences) > 10:
            recent_experiences = recent_experiences[-10:]
        
        # Update or insert session context
        cursor.execute("""
            INSERT OR REPLACE INTO session_contexts 
            (session_id, current_context, recent_experiences, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            json.dumps(current_context["current_context"]),
            json.dumps(recent_experiences),
            datetime.now().isoformat()
        ))
        
        self.sqlite_conn.commit()
    
    def _start_pruning_thread(self):
        """Start background thread for intelligent pruning"""
        self.pruning_thread = threading.Thread(target=self._pruning_worker, daemon=True)
        self.pruning_thread.start()
    
    def _pruning_worker(self):
        """Background worker for intelligent pruning"""
        while True:
            try:
                # Process pruning queue
                while not self.pruning_queue.empty():
                    experience = self.pruning_queue.get_nowait()
                    # Queue for LLM-based pruning analysis
                    asyncio.create_task(self._analyze_for_pruning(experience))
                
                # Periodic pruning
                asyncio.create_task(self._periodic_pruning())
                
                # Sleep
                threading.Event().wait(self.pruning_interval)
                
            except Exception as e:
                logger.error(f"Error in pruning worker: {e}")
                threading.Event().wait(60)  # Wait 1 minute on error
    
    async def _analyze_for_pruning(self, experience: Experience):
        """Analyze experience for potential pruning using LLM"""
        try:
            # Only analyze experiences that are older than 1 hour
            if datetime.now() - experience.timestamp < timedelta(hours=1):
                return
            
            prompt = f"""
            Analyze this experience for potential pruning:
            
            Experience: {experience.content[:300]}...
            Type: {experience.experience_type.value}
            Importance Score: {experience.importance_score}
            Age: {(datetime.now() - experience.timestamp).total_seconds() / 3600:.1f} hours
            
            Consider:
            1. Is this information still relevant and useful?
            2. Is this redundant with other experiences?
            3. Has this been superseded by newer information?
            4. Is this routine/trivial information?
            
            Return one of:
            - KEEP: Important, unique, still relevant
            - DOWNGRADE: Less important than initially scored
            - PRUNE: Redundant, outdated, or trivial
            
            Decision: """
            
            response = await openai_manager.get_completion(prompt, max_tokens=20)
            decision = response.strip().upper()
            
            if decision == "PRUNE":
                await self._prune_experience(experience.id)
            elif decision == "DOWNGRADE":
                await self._downgrade_experience(experience.id)
                
        except Exception as e:
            logger.error(f"Error in pruning analysis: {e}")
    
    async def _periodic_pruning(self):
        """Periodic pruning of old, low-importance experiences"""
        try:
            cursor = self.sqlite_conn.cursor()
            
            # Prune experiences older than 30 days with low importance
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute("""
                UPDATE experiences 
                SET memory_tier = 'pruned' 
                WHERE timestamp < ? AND importance_score < 3.0 AND memory_tier != 'hot'
            """, (cutoff_date,))
            
            # Archive cold memory older than 7 days
            cold_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                UPDATE experiences 
                SET memory_tier = 'cold' 
                WHERE timestamp < ? AND memory_tier = 'warm' AND importance_score < 6.0
            """, (cold_cutoff,))
            
            self.sqlite_conn.commit()
            
            # Update memory stats
            await self._update_memory_stats()
            
        except Exception as e:
            logger.error(f"Error in periodic pruning: {e}")
    
    async def _prune_experience(self, experience_id: str):
        """Mark experience for deletion"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            UPDATE experiences 
            SET memory_tier = 'pruned' 
            WHERE id = ?
        """, (experience_id,))
        self.sqlite_conn.commit()
        
        # Remove from ChromaDB
        if self.chroma_collection:
            try:
                self.chroma_collection.delete(ids=[experience_id])
            except Exception as e:
                logger.error(f"Error removing from ChromaDB: {e}")
    
    async def _downgrade_experience(self, experience_id: str):
        """Downgrade experience to lower memory tier"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            UPDATE experiences 
            SET memory_tier = 'cold', importance_score = importance_score * 0.8
            WHERE id = ?
        """, (experience_id,))
        self.sqlite_conn.commit()
    
    async def _update_memory_stats(self):
        """Update memory statistics"""
        cursor = self.sqlite_conn.cursor()
        
        # Get counts by tier
        cursor.execute("""
            SELECT memory_tier, COUNT(*) 
            FROM experiences 
            GROUP BY memory_tier
        """)
        
        tier_counts = dict(cursor.fetchall())
        
        cursor.execute("""
            INSERT INTO memory_stats 
            (total_experiences, hot_memory_count, warm_memory_count, cold_memory_count, pruned_count, last_pruning)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sum(tier_counts.values()),
            tier_counts.get('hot', 0),
            tier_counts.get('warm', 0),
            tier_counts.get('cold', 0),
            tier_counts.get('pruned', 0),
            datetime.now().isoformat()
        ))
        
        self.sqlite_conn.commit()
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_stats 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            return {
                "total_experiences": row[1],
                "hot_memory_count": row[2],
                "warm_memory_count": row[3],
                "cold_memory_count": row[4],
                "pruned_count": row[5],
                "last_pruning": row[6],
                "created_at": row[7]
            }
        
        return {
            "total_experiences": 0,
            "hot_memory_count": 0,
            "warm_memory_count": 0,
            "cold_memory_count": 0,
            "pruned_count": 0,
            "last_pruning": None,
            "created_at": None
        }
    
    async def cleanup_pruned_data(self):
        """Permanently remove pruned experiences"""
        cursor = self.sqlite_conn.cursor()
        
        # Get pruned experience IDs
        cursor.execute("SELECT id FROM experiences WHERE memory_tier = 'pruned'")
        pruned_ids = [row[0] for row in cursor.fetchall()]
        
        if pruned_ids:
            # Remove from SQLite
            placeholders = ','.join(['?' for _ in pruned_ids])
            cursor.execute(f"DELETE FROM experiences WHERE id IN ({placeholders})", pruned_ids)
            
            # Remove from ChromaDB
            if self.chroma_collection:
                try:
                    self.chroma_collection.delete(ids=pruned_ids)
                except Exception as e:
                    logger.error(f"Error removing from ChromaDB: {e}")
            
            self.sqlite_conn.commit()
            logger.info(f"🧹 Cleaned up {len(pruned_ids)} pruned experiences")


# Global instance
central_experience_db = CentralExperienceDB() 