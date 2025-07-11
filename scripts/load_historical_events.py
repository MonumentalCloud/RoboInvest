#!/usr/bin/env python3
"""
Load Historical Events Script
Loads historical research data from backup directories into the central events database.
This ensures the frontend displays the last 100 historical streams on startup.
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from core.central_event_bus import central_event_bus, EventType, EventPriority, create_event
from utils.logger import logger

class HistoricalEventLoader:
    def __init__(self):
        self.data_dir = Path("data")
        self.backup_dirs = [
            "research_data_backup_20250710_094129",
            "research_data_backup_20250710_133130"
        ]
        self.events_loaded = 0
        
    async def load_historical_events(self, max_events: int = 1000):
        """Load historical events from backup directories into the central events database"""
        logger.info("🔄 Starting historical event loading...")
        
        # Start the central event bus if not already started
        try:
            await central_event_bus.start()
        except:
            pass  # Already started
        
        all_events = []
        
        # Load from all backup directories
        for backup_dir in self.backup_dirs:
            backup_path = self.data_dir / backup_dir
            if backup_path.exists():
                logger.info(f"📁 Loading from {backup_dir}")
                events = self._load_from_backup_directory(backup_path)
                all_events.extend(events)
                logger.info(f"✅ Loaded {len(events)} events from {backup_dir}")
            else:
                logger.warning(f"⚠️ Backup directory not found: {backup_dir}")
        
        # Sort events by timestamp (oldest first)
        all_events.sort(key=lambda x: x.get('timestamp', ''))
        
        # Limit to max_events
        if len(all_events) > max_events:
            all_events = all_events[-max_events:]  # Keep the most recent
        
        # Load events into the central event bus
        for event_data in all_events:
            try:
                self._create_event_from_historical_data(event_data)
                self.events_loaded += 1
            except Exception as e:
                logger.error(f"❌ Error loading event: {e}")
        
        logger.info(f"✅ Successfully loaded {self.events_loaded} historical events")
        return self.events_loaded
    
    def _load_from_backup_directory(self, backup_path: Path) -> List[Dict[str, Any]]:
        """Load events from a backup directory"""
        events = []
        
        # Look for JSON files in the backup directory
        for json_file in backup_path.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Convert different file types to events
                if "alpha_discovery" in json_file.name:
                    events.extend(self._convert_alpha_discovery_to_events(data, json_file.name))
                elif "deep_research" in json_file.name:
                    events.extend(self._convert_deep_research_to_events(data, json_file.name))
                elif "market_monitoring" in json_file.name:
                    events.extend(self._convert_market_monitoring_to_events(data, json_file.name))
                else:
                    # Generic conversion for other files
                    events.extend(self._convert_generic_to_events(data, json_file.name))
                    
            except Exception as e:
                logger.error(f"❌ Error loading {json_file}: {e}")
        
        return events
    
    def _convert_alpha_discovery_to_events(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Convert alpha discovery data to events"""
        events = []
        
        # Extract timestamp from filename
        timestamp = self._extract_timestamp_from_filename(filename)
        
        # Create main alpha discovery event
        if isinstance(data, dict) and data.get('insights'):
            insights = data['insights']
            for i, insight in enumerate(insights[:5]):  # Limit to first 5 insights
                event_data = {
                    'timestamp': timestamp,
                    'event_type': 'ai_thought',
                    'source': 'alpha_discovery',
                    'title': f"Alpha Discovery: {insight.get('title', 'Alpha Opportunity')}",
                    'message': insight.get('description', str(insight)),
                    'priority': 'high',
                    'metadata': {
                        'confidence': insight.get('confidence', 0.7),
                        'symbols': insight.get('symbols', []),
                        'insight_id': i,
                        'original_file': filename
                    }
                }
                events.append(event_data)
        
        return events
    
    def _convert_deep_research_to_events(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Convert deep research data to events"""
        events = []
        timestamp = self._extract_timestamp_from_filename(filename)
        
        if isinstance(data, dict):
            # Create research event
            event_data = {
                'timestamp': timestamp,
                'event_type': 'ai_thought',
                'source': 'deep_research',
                'title': f"Deep Research: {data.get('title', 'Research Analysis')}",
                'message': data.get('summary', str(data)),
                'priority': 'medium',
                'metadata': {
                    'research_type': data.get('type', 'analysis'),
                    'original_file': filename
                }
            }
            events.append(event_data)
        
        return events
    
    def _convert_market_monitoring_to_events(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Convert market monitoring data to events"""
        events = []
        timestamp = self._extract_timestamp_from_filename(filename)
        
        if isinstance(data, dict):
            # Create market monitoring event
            event_data = {
                'timestamp': timestamp,
                'event_type': 'research',
                'source': 'market_monitoring',
                'title': f"Market Update: {data.get('market_sentiment', 'Market Analysis')}",
                'message': data.get('summary', str(data)),
                'priority': 'medium',
                'metadata': {
                    'sentiment': data.get('market_sentiment', 'neutral'),
                    'original_file': filename
                }
            }
            events.append(event_data)
        
        return events
    
    def _convert_generic_to_events(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Convert generic data to events"""
        events = []
        timestamp = self._extract_timestamp_from_filename(filename)
        
        # Create generic event
        event_data = {
            'timestamp': timestamp,
            'event_type': 'info',
            'source': 'historical_loader',
            'title': f"Historical Data: {filename}",
            'message': f"Loaded historical data from {filename}",
            'priority': 'low',
            'metadata': {
                'original_file': filename,
                'data_type': 'historical'
            }
        }
        events.append(event_data)
        
        return events
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """Extract timestamp from filename like 'alpha_discovery_20250709_202713.json'"""
        try:
            # Look for pattern like _20250709_202713
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                date_part = parts[-2]
                time_part = parts[-1]
                if len(date_part) == 8 and len(time_part) == 6:  # YYYYMMDD_HHMMSS
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    hour = time_part[:2]
                    minute = time_part[2:4]
                    second = time_part[4:6]
                    return f"{year}-{month}-{day}T{hour}:{minute}:{second}"
        except:
            pass
        
        # Fallback to current time
        return datetime.now().isoformat()
    
    def _create_event_from_historical_data(self, event_data: Dict[str, Any]):
        """Create an event in the central event bus from historical data"""
        try:
            # Parse timestamp
            timestamp_str = event_data.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            # Create event
            event = create_event(
                event_type=EventType(event_data.get('event_type', 'SYSTEM_UPDATE')),
                source=event_data.get('source', 'historical_loader'),
                title=event_data.get('title', 'Historical Event'),
                message=event_data.get('message', ''),
                priority=EventPriority(event_data.get('priority', 'LOW')),
                metadata=event_data.get('metadata', {})
            )
            
            # Store in database
            central_event_bus.emit_event(event)
            
        except Exception as e:
            logger.error(f"❌ Error creating event: {e}")
    
    def get_loaded_events_count(self) -> int:
        """Get the count of events in the database"""
        try:
            with sqlite3.connect(central_event_bus.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM events")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error getting event count: {e}")
            return 0

async def main():
    """Main function to load historical events"""
    loader = HistoricalEventLoader()
    
    # Check current event count
    initial_count = loader.get_loaded_events_count()
    logger.info(f"📊 Initial event count: {initial_count}")
    
    # Load historical events
    loaded_count = await loader.load_historical_events(max_events=1000)
    
    # Check final event count
    final_count = loader.get_loaded_events_count()
    logger.info(f"📊 Final event count: {final_count}")
    logger.info(f"📊 New events loaded: {loaded_count}")
    
    if loaded_count > 0:
        logger.info("✅ Historical events loaded successfully!")
        logger.info("🔄 The frontend should now display historical streams on startup.")
    else:
        logger.warning("⚠️ No historical events were loaded.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 