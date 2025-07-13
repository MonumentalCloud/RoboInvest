#!/usr/bin/env python3
"""
Rollback Manager: Handles system snapshots and rollbacks
"""

import os
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import tarfile
import tempfile

from utils.logger import logger
from core.config import config

class RollbackManager:
    """Manages system snapshots and rollbacks."""
    
    def __init__(self):
        self.snapshots_dir = Path("backups/snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_db = self.snapshots_dir / "snapshots.json"
        self._init_snapshots_db()
    
    def _init_snapshots_db(self):
        """Initialize the snapshots database."""
        if not self.snapshots_db.exists():
            with open(self.snapshots_db, 'w') as f:
                json.dump({"snapshots": []}, f, indent=2)
    
    def create_snapshot(self, description: str, change_type: str = "manual") -> str:
        """Create a system snapshot before making changes."""
        try:
            timestamp = datetime.now().isoformat()
            snapshot_id = f"snapshot_{timestamp.replace(':', '-').replace('.', '-')}"
            snapshot_dir = self.snapshots_dir / snapshot_id
            snapshot_dir.mkdir(exist_ok=True)
            
            logger.info(f"📸 Creating snapshot: {snapshot_id}")
            
            # Create codebase snapshot
            self._snapshot_codebase(snapshot_dir)
            
            # Create database snapshot
            self._snapshot_databases(snapshot_dir)
            
            # Create metadata
            metadata = {
                "id": snapshot_id,
                "timestamp": timestamp,
                "description": description,
                "change_type": change_type,
                "files": {
                    "codebase": "codebase.tar.gz",
                    "databases": "databases.tar.gz",
                    "metadata": "metadata.json"
                }
            }
            
            # Save metadata
            with open(snapshot_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update snapshots database
            self._add_snapshot_to_db(metadata)
            
            logger.info(f"✅ Snapshot created: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create snapshot: {e}")
            raise
    
    def _snapshot_codebase(self, snapshot_dir: Path):
        """Create a snapshot of the codebase."""
        codebase_tar = snapshot_dir / "codebase.tar.gz"
        
        with tarfile.open(codebase_tar, "w:gz") as tar:
            # Add agents directory
            if Path("agents").exists():
                tar.add("agents", arcname="agents")
            
            # Add core directory
            if Path("core").exists():
                tar.add("core", arcname="core")
            
            # Add utils directory
            if Path("utils").exists():
                tar.add("utils", arcname="utils")
            
            # Add backend directory
            if Path("backend").exists():
                tar.add("backend", arcname="backend")
            
            # Add main files
            for file in ["main.py", "autonomous_trading_system.py", "bot_workflow.py"]:
                if Path(file).exists():
                    tar.add(file)
    
    def _snapshot_databases(self, snapshot_dir: Path):
        """Create a snapshot of databases."""
        databases_tar = snapshot_dir / "databases.tar.gz"
        
        with tarfile.open(databases_tar, "w:gz") as tar:
            # Add ChromaDB
            if Path(config.chroma_db_path).exists():
                tar.add(config.chroma_db_path, arcname="chroma")
            
            # Add meta agent database
            meta_db_path = Path("meta_agent_data/enhanced_meta_agent.db")
            if meta_db_path.exists():
                tar.add(meta_db_path, arcname="meta_agent.db")
            
            # Add other data files
            for data_file in ["performance.jsonl", "context/"]:
                if Path(data_file).exists():
                    tar.add(data_file)
    
    def _add_snapshot_to_db(self, metadata: Dict[str, Any]):
        """Add snapshot metadata to the database."""
        with open(self.snapshots_db, 'r') as f:
            data = json.load(f)
        
        data["snapshots"].append(metadata)
        
        with open(self.snapshots_db, 'w') as f:
            json.dump(data, f, indent=2)
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots."""
        try:
            with open(self.snapshots_db, 'r') as f:
                data = json.load(f)
            return data.get("snapshots", [])
        except Exception as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []
    
    def rollback_to_snapshot(self, snapshot_id: str) -> bool:
        """Rollback to a specific snapshot."""
        try:
            logger.info(f"🔄 Rolling back to snapshot: {snapshot_id}")
            
            # Find snapshot
            snapshots = self.list_snapshots()
            snapshot = next((s for s in snapshots if s["id"] == snapshot_id), None)
            
            if not snapshot:
                logger.error(f"Snapshot not found: {snapshot_id}")
                return False
            
            snapshot_dir = self.snapshots_dir / snapshot_id
            
            if not snapshot_dir.exists():
                logger.error(f"Snapshot directory not found: {snapshot_dir}")
                return False
            
            # Restore codebase
            self._restore_codebase(snapshot_dir)
            
            # Restore databases
            self._restore_databases(snapshot_dir)
            
            logger.info(f"✅ Successfully rolled back to snapshot: {snapshot_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def _restore_codebase(self, snapshot_dir: Path):
        """Restore codebase from snapshot."""
        codebase_tar = snapshot_dir / "codebase.tar.gz"
        
        if codebase_tar.exists():
            with tarfile.open(codebase_tar, "r:gz") as tar:
                tar.extractall(path=".")
                logger.info("✅ Codebase restored")
    
    def _restore_databases(self, snapshot_dir: Path):
        """Restore databases from snapshot."""
        databases_tar = snapshot_dir / "databases.tar.gz"
        
        if databases_tar.exists():
            with tarfile.open(databases_tar, "r:gz") as tar:
                tar.extractall(path=".")
                logger.info("✅ Databases restored")
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot."""
        try:
            # Remove snapshot directory
            snapshot_dir = self.snapshots_dir / snapshot_id
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            
            # Remove from database
            with open(self.snapshots_db, 'r') as f:
                data = json.load(f)
            
            data["snapshots"] = [s for s in data["snapshots"] if s["id"] != snapshot_id]
            
            with open(self.snapshots_db, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Snapshot deleted: {snapshot_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete snapshot: {e}")
            return False

# Global instance
rollback_manager = RollbackManager() 