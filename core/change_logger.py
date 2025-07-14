"""
Change Logger - Production-grade logging for all code modifications

Tracks:
- All code changes with timestamps
- Git commit hashes for rollback
- Change validation status
- User approvals
- Rollback history
- Change metadata and reasoning
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from utils.logger import logger


class ChangeStatus(Enum):
    """Status of a code change"""
    PROPOSED = "proposed"
    APPROVED = "approved"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ChangeType(Enum):
    """Type of code change"""
    NEW_ENDPOINT = "new_endpoint"
    NEW_AGENT = "new_agent"
    MODIFY_EXISTING = "modify_existing"
    CONFIG_CHANGE = "config_change"
    DEPENDENCY_UPDATE = "dependency_update"
    SYSTEM_ARCHITECTURE = "system_architecture"


@dataclass
class CodeChange:
    """Represents a single code change"""
    change_id: str
    timestamp: datetime
    change_type: ChangeType
    status: ChangeStatus
    description: str
    files_modified: List[str]
    git_commit_hash: Optional[str]
    git_branch: str
    user_approved: bool
    applied_by: str  # "system" or "user"
    reasoning: str
    metadata: Dict[str, Any]
    rollback_commit_hash: Optional[str] = None
    rollback_timestamp: Optional[datetime] = None
    rollback_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "change_id": self.change_id,
            "timestamp": self.timestamp.isoformat(),
            "change_type": self.change_type.value,
            "status": self.status.value,
            "description": self.description,
            "files_modified": self.files_modified,
            "git_commit_hash": self.git_commit_hash,
            "git_branch": self.git_branch,
            "user_approved": self.user_approved,
            "applied_by": self.applied_by,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
            "rollback_commit_hash": self.rollback_commit_hash,
            "rollback_timestamp": self.rollback_timestamp.isoformat() if self.rollback_timestamp else None,
            "rollback_reason": self.rollback_reason
        }


class ChangeLogger:
    """Production-grade change logging system"""
    
    def __init__(self, db_path: str = "data/change_log.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the change logging database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS code_changes (
                    change_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    description TEXT NOT NULL,
                    files_modified TEXT NOT NULL,
                    git_commit_hash TEXT,
                    git_branch TEXT NOT NULL,
                    user_approved BOOLEAN NOT NULL,
                    applied_by TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    rollback_commit_hash TEXT,
                    rollback_timestamp TEXT,
                    rollback_reason TEXT
                )
            """)
            
            # Create indexes for efficient querying
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON code_changes(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON code_changes(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_change_type ON code_changes(change_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_git_commit ON code_changes(git_commit_hash)")
            
            conn.commit()
    
    def log_change(self, change: CodeChange) -> bool:
        """Log a code change to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO code_changes 
                    (change_id, timestamp, change_type, status, description, files_modified,
                     git_commit_hash, git_branch, user_approved, applied_by, reasoning, metadata,
                     rollback_commit_hash, rollback_timestamp, rollback_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    change.change_id,
                    change.timestamp.isoformat(),
                    change.change_type.value,
                    change.status.value,
                    change.description,
                    json.dumps(change.files_modified),
                    change.git_commit_hash,
                    change.git_branch,
                    change.user_approved,
                    change.applied_by,
                    change.reasoning,
                    json.dumps(change.metadata),
                    change.rollback_commit_hash,
                    change.rollback_timestamp.isoformat() if change.rollback_timestamp else None,
                    change.rollback_reason
                ))
                conn.commit()
            
            logger.info(f"Change logged: {change.change_id} - {change.description}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log change {change.change_id}: {e}")
            return False
    
    def update_change_status(self, change_id: str, status: ChangeStatus, 
                           git_commit_hash: Optional[str] = None) -> bool:
        """Update the status of a logged change"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if git_commit_hash:
                    conn.execute("""
                        UPDATE code_changes 
                        SET status = ?, git_commit_hash = ?
                        WHERE change_id = ?
                    """, (status.value, git_commit_hash, change_id))
                else:
                    conn.execute("""
                        UPDATE code_changes 
                        SET status = ?
                        WHERE change_id = ?
                    """, (status.value, change_id))
                conn.commit()
            
            logger.info(f"Change {change_id} status updated to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update change {change_id}: {e}")
            return False
    
    def log_rollback(self, change_id: str, rollback_commit_hash: str, 
                    rollback_reason: str) -> bool:
        """Log a rollback operation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE code_changes 
                    SET status = ?, rollback_commit_hash = ?, rollback_timestamp = ?, rollback_reason = ?
                    WHERE change_id = ?
                """, (
                    ChangeStatus.ROLLED_BACK.value,
                    rollback_commit_hash,
                    datetime.utcnow().isoformat(),
                    rollback_reason,
                    change_id
                ))
                conn.commit()
            
            logger.info(f"Rollback logged for change {change_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log rollback for {change_id}: {e}")
            return False
    
    def get_change(self, change_id: str) -> Optional[CodeChange]:
        """Get a specific change by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM code_changes WHERE change_id = ?
                """, (change_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_change(row)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get change {change_id}: {e}")
            return None
    
    def get_recent_changes(self, limit: int = 50) -> List[CodeChange]:
        """Get recent changes ordered by timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM code_changes 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                
                return [self._row_to_change(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get recent changes: {e}")
            return []
    
    def get_changes_by_status(self, status: ChangeStatus) -> List[CodeChange]:
        """Get all changes with a specific status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM code_changes 
                    WHERE status = ?
                    ORDER BY timestamp DESC
                """, (status.value,))
                rows = cursor.fetchall()
                
                return [self._row_to_change(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get changes by status {status}: {e}")
            return []
    
    def get_changes_by_type(self, change_type: ChangeType) -> List[CodeChange]:
        """Get all changes of a specific type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM code_changes 
                    WHERE change_type = ?
                    ORDER BY timestamp DESC
                """, (change_type.value,))
                rows = cursor.fetchall()
                
                return [self._row_to_change(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get changes by type {change_type}: {e}")
            return []
    
    def _row_to_change(self, row: tuple) -> CodeChange:
        """Convert database row to CodeChange object"""
        return CodeChange(
            change_id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            change_type=ChangeType(row[2]),
            status=ChangeStatus(row[3]),
            description=row[4],
            files_modified=json.loads(row[5]),
            git_commit_hash=row[6],
            git_branch=row[7],
            user_approved=bool(row[8]),
            applied_by=row[9],
            reasoning=row[10],
            metadata=json.loads(row[11]),
            rollback_commit_hash=row[12],
            rollback_timestamp=datetime.fromisoformat(row[13]) if row[13] else None,
            rollback_reason=row[14]
        )
    
    def get_change_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all changes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total changes
                total = conn.execute("SELECT COUNT(*) FROM code_changes").fetchone()[0]
                
                # Changes by status
                status_counts = {}
                for status in ChangeStatus:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM code_changes WHERE status = ?",
                        (status.value,)
                    ).fetchone()[0]
                    status_counts[status.value] = count
                
                # Changes by type
                type_counts = {}
                for change_type in ChangeType:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM code_changes WHERE change_type = ?",
                        (change_type.value,)
                    ).fetchone()[0]
                    type_counts[change_type.value] = count
                
                # Recent activity (last 24 hours)
                yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
                recent = conn.execute(
                    "SELECT COUNT(*) FROM code_changes WHERE timestamp > ?",
                    (yesterday,)
                ).fetchone()[0]
                
                return {
                    "total_changes": total,
                    "status_breakdown": status_counts,
                    "type_breakdown": type_counts,
                    "recent_activity_24h": recent,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get change summary: {e}")
            return {
                "total_changes": 0,
                "status_breakdown": {},
                "type_breakdown": {},
                "recent_activity_24h": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global instance
change_logger = ChangeLogger() 