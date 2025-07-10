#!/usr/bin/env python3
"""
Cleanup script for research data JSON files.
Organizes data into separate databases for each research track.
"""

import os
import json
import sqlite3
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResearchDataCleaner:
    def __init__(self, research_data_dir="research_data"):
        self.research_data_dir = Path(research_data_dir)
        self.db_dir = Path("research_databases")
        self.db_dir.mkdir(exist_ok=True)
        
        # Research tracks
        self.tracks = [
            "alpha_discovery",
            "market_monitoring", 
            "sentiment_tracking",
            "technical_analysis",
            "risk_assessment",
            "deep_research"
        ]
        
        # Initialize databases
        self.init_databases()
    
    def init_databases(self):
        """Initialize SQLite databases for each research track"""
        for track in self.tracks:
            db_path = self.db_dir / f"{track}.db"
            logger.info(f"Initializing database: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables for each track
            if track == "alpha_discovery":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alpha_opportunities (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        track TEXT,
                        content TEXT,
                        confidence REAL,
                        status TEXT,
                        metadata TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
            elif track == "market_monitoring":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_data (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        track TEXT,
                        content TEXT,
                        data_type TEXT,
                        status TEXT,
                        metadata TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
            elif track == "sentiment_tracking":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sentiment_data (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        track TEXT,
                        content TEXT,
                        sentiment_score REAL,
                        source TEXT,
                        status TEXT,
                        metadata TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
            elif track == "technical_analysis":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS technical_data (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        track TEXT,
                        content TEXT,
                        indicator_type TEXT,
                        status TEXT,
                        metadata TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
            elif track == "risk_assessment":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS risk_data (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        track TEXT,
                        content TEXT,
                        risk_level TEXT,
                        risk_score REAL,
                        status TEXT,
                        metadata TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
            elif track == "deep_research":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS research_data (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        track TEXT,
                        content TEXT,
                        research_type TEXT,
                        status TEXT,
                        metadata TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
            
            conn.commit()
            conn.close()
    
    def get_file_info(self, file_path):
        """Extract timestamp and track info from filename"""
        filename = file_path.name
        parts = filename.replace('.json', '').split('_')
        
        if len(parts) >= 3:
            track = parts[0]
            if len(parts) >= 4:
                # Format: track_YYYYMMDD_HHMMSS
                date_str = f"{parts[1]}_{parts[2]}"
                try:
                    timestamp = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    return track, timestamp
                except ValueError:
                    pass
        
        # Fallback: try to parse from file content
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # Try to find timestamp in the data
                    for key in ['timestamp', 'created_at', 'updated_at']:
                        if key in data:
                            try:
                                timestamp = datetime.fromisoformat(data[key].replace('Z', '+00:00'))
                                return track, timestamp
                            except:
                                pass
        except:
            pass
        
        return None, None
    
    def import_json_to_db(self, file_path, track):
        """Import JSON data into the appropriate database"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            db_path = self.db_dir / f"{track}.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if isinstance(data, dict):
                # Single record
                self._insert_record(cursor, track, data)
            elif isinstance(data, list):
                # Multiple records
                for record in data:
                    self._insert_record(cursor, track, record)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error importing {file_path}: {e}")
            return False
    
    def _insert_record(self, cursor, track, record):
        """Insert a record into the appropriate table"""
        if not isinstance(record, dict):
            return
        
        # Extract common fields
        record_id = record.get('id', record.get('node_id', str(hash(str(record)))))
        timestamp = record.get('timestamp', record.get('created_at', datetime.now().isoformat()))
        content = record.get('content', record.get('title', ''))
        status = record.get('status', 'unknown')
        metadata = json.dumps(record.get('metadata', record.get('data', {})))
        created_at = record.get('created_at', timestamp)
        updated_at = record.get('updated_at', timestamp)
        
        # Track-specific fields
        if track == "alpha_discovery":
            confidence = record.get('confidence', 0.0)
            cursor.execute('''
                INSERT OR REPLACE INTO alpha_opportunities 
                (id, timestamp, track, content, confidence, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, timestamp, track, content, confidence, status, metadata, created_at, updated_at))
        
        elif track == "market_monitoring":
            data_type = record.get('type', 'market_data')
            cursor.execute('''
                INSERT OR REPLACE INTO market_data 
                (id, timestamp, track, content, data_type, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, timestamp, track, content, data_type, status, metadata, created_at, updated_at))
        
        elif track == "sentiment_tracking":
            sentiment_score = record.get('sentiment_score', 0.0)
            source = record.get('source', 'unknown')
            cursor.execute('''
                INSERT OR REPLACE INTO sentiment_data 
                (id, timestamp, track, content, sentiment_score, source, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, timestamp, track, content, sentiment_score, source, status, metadata, created_at, updated_at))
        
        elif track == "technical_analysis":
            indicator_type = record.get('type', 'technical')
            cursor.execute('''
                INSERT OR REPLACE INTO technical_data 
                (id, timestamp, track, content, indicator_type, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, timestamp, track, content, indicator_type, status, metadata, created_at, updated_at))
        
        elif track == "risk_assessment":
            risk_level = record.get('risk_level', 'medium')
            risk_score = record.get('risk_score', 0.5)
            cursor.execute('''
                INSERT OR REPLACE INTO risk_data 
                (id, timestamp, track, content, risk_level, risk_score, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, timestamp, track, content, risk_level, risk_score, status, metadata, created_at, updated_at))
        
        elif track == "deep_research":
            research_type = record.get('type', 'research')
            cursor.execute('''
                INSERT OR REPLACE INTO research_data 
                (id, timestamp, track, content, research_type, status, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, timestamp, track, content, research_type, status, metadata, created_at, updated_at))
    
    def cleanup_old_files(self, keep_days=7):
        """Remove old JSON files, keeping only the most recent ones"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Keep only the latest file for each track
        latest_files = {}
        
        for file_path in self.research_data_dir.glob("*.json"):
            track, timestamp = self.get_file_info(file_path)
            
            if track and timestamp:
                if track not in latest_files or timestamp > latest_files[track][1]:
                    latest_files[track] = (file_path, timestamp)
        
        # Remove old files, keeping only the latest
        removed_count = 0
        for file_path in self.research_data_dir.glob("*.json"):
            track, timestamp = self.get_file_info(file_path)
            
            if track and timestamp:
                # Keep only the latest file for each track
                if file_path != latest_files.get(track, (None, None))[0]:
                    logger.info(f"Removing old file: {file_path}")
                    file_path.unlink()
                    removed_count += 1
            else:
                # Remove files that can't be parsed
                logger.info(f"Removing unparseable file: {file_path}")
                file_path.unlink()
                removed_count += 1
        
        logger.info(f"Removed {removed_count} old files")
        return removed_count
    
    def process_all_files(self):
        """Process all JSON files and import them into databases"""
        processed_count = 0
        error_count = 0
        
        for file_path in self.research_data_dir.glob("*.json"):
            track, timestamp = self.get_file_info(file_path)
            
            if track and track in self.tracks:
                logger.info(f"Processing {file_path} -> {track}")
                if self.import_json_to_db(file_path, track):
                    processed_count += 1
                else:
                    error_count += 1
            else:
                logger.warning(f"Skipping {file_path} - unknown track: {track}")
        
        logger.info(f"Processed {processed_count} files successfully, {error_count} errors")
        return processed_count, error_count
    
    def create_backup(self):
        """Create a backup of the research_data directory"""
        backup_dir = Path(f"research_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if self.research_data_dir.exists():
            shutil.copytree(self.research_data_dir, backup_dir)
            logger.info(f"Created backup: {backup_dir}")
            return backup_dir
        return None

def main():
    """Main cleanup process"""
    cleaner = ResearchDataCleaner()
    
    print("🧹 Research Data Cleanup Tool")
    print("=" * 50)
    
    # Create backup first
    print("📦 Creating backup...")
    backup_dir = cleaner.create_backup()
    
    # Process all files
    print("🔄 Processing JSON files...")
    processed, errors = cleaner.process_all_files()
    
    # Clean up old files
    print("🗑️  Cleaning up old files...")
    removed = cleaner.cleanup_old_files(keep_days=1)  # Keep only 1 day of files
    
    print("\n✅ Cleanup Complete!")
    print(f"📊 Processed: {processed} files")
    print(f"❌ Errors: {errors} files")
    print(f"🗑️  Removed: {removed} old files")
    print(f"💾 Databases created in: research_databases/")
    print(f"📦 Backup created: {backup_dir}")
    
    # Show database sizes
    print("\n📈 Database Statistics:")
    for track in cleaner.tracks:
        db_path = cleaner.db_dir / f"{track}.db"
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"  {track}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main() 