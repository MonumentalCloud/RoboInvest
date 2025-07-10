from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import threading

from utils.logger import logger


class PlayReportingSystem:
    """Central reporting system for play executor actions and outcomes"""
    
    def __init__(self, db_path: str = "play_reporting.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the reporting database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create plays table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plays (
                    play_id TEXT PRIMARY KEY,
                    order_id TEXT,
                    symbol TEXT,
                    status TEXT,
                    natural_language_description TEXT,
                    parsed_play TEXT,
                    execution_plan TEXT,
                    monitoring_conditions TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    completed_at TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    quantity INTEGER,
                    side TEXT,
                    timeframe TEXT,
                    priority INTEGER,
                    tags TEXT,
                    confidence_score REAL
                )
            ''')
            
            # Create interventions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    play_id TEXT,
                    intervention_type TEXT,
                    reason TEXT,
                    action TEXT,
                    timestamp TEXT,
                    market_data TEXT,
                    manual BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (play_id) REFERENCES plays (play_id)
                )
            ''')
            
            # Create adaptations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    play_id TEXT,
                    adaptation_type TEXT,
                    reason TEXT,
                    action TEXT,
                    timestamp TEXT,
                    market_data TEXT,
                    FOREIGN KEY (play_id) REFERENCES plays (play_id)
                )
            ''')
            
            # Create performance_metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    play_id TEXT,
                    timestamp TEXT,
                    current_price REAL,
                    pnl_pct REAL,
                    max_profit REAL,
                    max_drawdown REAL,
                    time_in_play_hours REAL,
                    volume_trend REAL,
                    sentiment_trend REAL,
                    FOREIGN KEY (play_id) REFERENCES plays (play_id)
                )
            ''')
            
            # Create market_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    play_id TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (play_id) REFERENCES plays (play_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Play reporting database initialized: {self.db_path}")
    
    def log_play_creation(self, play: Dict[str, Any]):
        """Log a new play creation"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO plays (
                        play_id, order_id, symbol, status, natural_language_description,
                        parsed_play, execution_plan, monitoring_conditions, created_at,
                        updated_at, entry_price, quantity, side, timeframe, priority,
                        tags, confidence_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    play["play_id"],
                    play["order_id"],
                    play["symbol"],
                    play["status"].value,
                    play["natural_language_description"],
                    json.dumps(play["parsed_play"]),
                    json.dumps(play["execution_plan"]),
                    json.dumps(play["monitoring_conditions"]),
                    play["created_at"].isoformat(),
                    play["updated_at"].isoformat(),
                    play["performance_metrics"]["entry_price"],
                    play.get("quantity", 0),
                    play["parsed_play"]["side"],
                    play["parsed_play"]["timeframe"],
                    play["parsed_play"]["priority"],
                    json.dumps(play["parsed_play"]["tags"]),
                    play.get("confidence_score", 0.0)
                ))
                
                conn.commit()
                logger.info(f"Logged play creation: {play['play_id']}")
                
            except Exception as e:
                logger.error(f"Error logging play creation: {e}")
            finally:
                conn.close()
    
    def log_intervention(self, play_id: str, intervention: Dict[str, Any], market_data: Dict[str, Any]):
        """Log an intervention on a play"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO interventions (
                        play_id, intervention_type, reason, action, timestamp,
                        market_data, manual
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    play_id,
                    intervention["type"].value if hasattr(intervention["type"], "value") else str(intervention["type"]),
                    intervention["reason"],
                    intervention["action"],
                    intervention.get("timestamp", datetime.now().isoformat()),
                    json.dumps(market_data),
                    intervention.get("manual", False)
                ))
                
                # Update play status
                cursor.execute('''
                    UPDATE plays SET status = ?, updated_at = ?
                    WHERE play_id = ?
                ''', (
                    "intervened",
                    datetime.now().isoformat(),
                    play_id
                ))
                
                conn.commit()
                logger.info(f"Logged intervention for play {play_id}: {intervention['reason']}")
                
            except Exception as e:
                logger.error(f"Error logging intervention: {e}")
            finally:
                conn.close()
    
    def log_adaptation(self, play_id: str, adaptation: Dict[str, Any], market_data: Dict[str, Any]):
        """Log an adaptation on a play"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO adaptations (
                        play_id, adaptation_type, reason, action, timestamp, market_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    play_id,
                    adaptation["type"],
                    adaptation["reason"],
                    adaptation["action"],
                    adaptation.get("timestamp", datetime.now().isoformat()),
                    json.dumps(market_data)
                ))
                
                conn.commit()
                logger.info(f"Logged adaptation for play {play_id}: {adaptation['reason']}")
                
            except Exception as e:
                logger.error(f"Error logging adaptation: {e}")
            finally:
                conn.close()
    
    def log_performance_update(self, play_id: str, performance_metrics: Dict[str, Any]):
        """Log performance metrics update"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO performance_metrics (
                        play_id, timestamp, current_price, pnl_pct, max_profit,
                        max_drawdown, time_in_play_hours, volume_trend, sentiment_trend
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    play_id,
                    datetime.now().isoformat(),
                    performance_metrics.get("current_price", 0.0),
                    performance_metrics.get("pnl_pct", 0.0),
                    performance_metrics.get("max_profit", 0.0),
                    performance_metrics.get("max_drawdown", 0.0),
                    performance_metrics.get("time_in_play", 0.0),
                    performance_metrics.get("volume_trend", 0.0),
                    performance_metrics.get("sentiment_trend", 0.0)
                ))
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Error logging performance update: {e}")
            finally:
                conn.close()
    
    def log_play_completion(self, play_id: str, exit_price: float, final_pnl: float):
        """Log play completion"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE plays SET 
                        status = ?, 
                        completed_at = ?, 
                        updated_at = ?, 
                        exit_price = ?
                    WHERE play_id = ?
                ''', (
                    "completed",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    exit_price,
                    play_id
                ))
                
                conn.commit()
                logger.info(f"Logged play completion: {play_id} with P&L: {final_pnl:.2%}")
                
            except Exception as e:
                logger.error(f"Error logging play completion: {e}")
            finally:
                conn.close()
    
    def update_existing_plays_to_completed(self):
        """Update existing intervened plays that should be completed"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Find intervened plays without exit prices
                cursor.execute('''
                    SELECT play_id, entry_price FROM plays 
                    WHERE status = 'intervened' AND exit_price IS NULL
                ''')
                
                intervened_plays = cursor.fetchall()
                
                for play_id, entry_price in intervened_plays:
                    # For intervened plays, assume they were closed at entry price (break-even)
                    # This is a conservative approach for historical data
                    cursor.execute('''
                        UPDATE plays SET 
                            status = ?, 
                            completed_at = ?, 
                            updated_at = ?, 
                            exit_price = ?
                        WHERE play_id = ?
                    ''', (
                        "completed",
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        entry_price,  # Assume break-even for intervened plays
                        play_id
                    ))
                
                conn.commit()
                logger.info(f"Updated {len(intervened_plays)} intervened plays to completed status")
                
            except Exception as e:
                logger.error(f"Error updating intervened plays: {e}")
            finally:
                conn.close()
    
    def log_market_event(self, play_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log market events that affect plays"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO market_events (
                        play_id, event_type, event_data, timestamp
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    play_id,
                    event_type,
                    json.dumps(event_data),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Error logging market event: {e}")
            finally:
                conn.close()
    
    def get_play_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get play history with interventions and adaptations"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    SELECT p.*, 
                           COUNT(i.id) as intervention_count,
                           COUNT(a.id) as adaptation_count
                    FROM plays p
                    LEFT JOIN interventions i ON p.play_id = i.play_id
                    LEFT JOIN adaptations a ON p.play_id = a.play_id
                    GROUP BY p.play_id
                    ORDER BY p.created_at DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                plays = []
                for row in rows:
                    play_dict = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    if play_dict["parsed_play"]:
                        play_dict["parsed_play"] = json.loads(play_dict["parsed_play"])
                    if play_dict["execution_plan"]:
                        play_dict["execution_plan"] = json.loads(play_dict["execution_plan"])
                    if play_dict["monitoring_conditions"]:
                        play_dict["monitoring_conditions"] = json.loads(play_dict["monitoring_conditions"])
                    if play_dict["tags"]:
                        play_dict["tags"] = json.loads(play_dict["tags"])
                    
                    plays.append(play_dict)
                
                return plays
                
            except Exception as e:
                logger.error(f"Error getting play history: {e}")
                return []
            finally:
                conn.close()
    
    def get_play_details(self, play_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific play"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Get play info
                cursor.execute('SELECT * FROM plays WHERE play_id = ?', (play_id,))
                play_row = cursor.fetchone()
                
                if not play_row:
                    return None
                
                columns = [description[0] for description in cursor.description]
                play_dict = dict(zip(columns, play_row))
                
                # Parse JSON fields
                if play_dict["parsed_play"]:
                    play_dict["parsed_play"] = json.loads(play_dict["parsed_play"])
                if play_dict["execution_plan"]:
                    play_dict["execution_plan"] = json.loads(play_dict["execution_plan"])
                if play_dict["monitoring_conditions"]:
                    play_dict["monitoring_conditions"] = json.loads(play_dict["monitoring_conditions"])
                if play_dict["tags"]:
                    play_dict["tags"] = json.loads(play_dict["tags"])
                
                # Get interventions
                cursor.execute('SELECT * FROM interventions WHERE play_id = ? ORDER BY timestamp', (play_id,))
                intervention_rows = cursor.fetchall()
                intervention_columns = [description[0] for description in cursor.description]
                play_dict["interventions"] = [
                    dict(zip(intervention_columns, row)) for row in intervention_rows
                ]
                
                # Get adaptations
                cursor.execute('SELECT * FROM adaptations WHERE play_id = ? ORDER BY timestamp', (play_id,))
                adaptation_rows = cursor.fetchall()
                adaptation_columns = [description[0] for description in cursor.description]
                play_dict["adaptations"] = [
                    dict(zip(adaptation_columns, row)) for row in adaptation_rows
                ]
                
                # Get performance metrics
                cursor.execute('SELECT * FROM performance_metrics WHERE play_id = ? ORDER BY timestamp', (play_id,))
                performance_rows = cursor.fetchall()
                performance_columns = [description[0] for description in cursor.description]
                play_dict["performance_history"] = [
                    dict(zip(performance_columns, row)) for row in performance_rows
                ]
                
                return play_dict
                
            except Exception as e:
                logger.error(f"Error getting play details: {e}")
                return None
            finally:
                conn.close()
    
    def get_play_statistics(self) -> Dict[str, Any]:
        """Get comprehensive play statistics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Basic counts
                cursor.execute('SELECT COUNT(*) FROM plays')
                total_plays = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM plays WHERE status = "active"')
                active_plays = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM plays WHERE status = "completed"')
                completed_plays = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM plays WHERE status = "intervened"')
                intervened_plays = cursor.fetchone()[0]
                
                # Performance statistics
                cursor.execute('''
                    SELECT 
                        AVG(CASE WHEN exit_price > entry_price THEN (exit_price - entry_price) / entry_price ELSE 0 END) as avg_profit,
                        AVG(CASE WHEN exit_price < entry_price THEN (entry_price - exit_price) / entry_price ELSE 0 END) as avg_loss,
                        COUNT(CASE WHEN exit_price > entry_price THEN 1 END) as profitable_plays,
                        COUNT(CASE WHEN exit_price < entry_price THEN 1 END) as losing_plays
                    FROM plays 
                    WHERE status = "completed" AND exit_price IS NOT NULL
                ''')
                
                perf_row = cursor.fetchone()
                if perf_row:
                    avg_profit, avg_loss, profitable_count, losing_count = perf_row
                else:
                    avg_profit = avg_loss = profitable_count = losing_count = 0
                
                # Intervention statistics
                cursor.execute('SELECT COUNT(*) FROM interventions')
                total_interventions = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM adaptations')
                total_adaptations = cursor.fetchone()[0]
                
                return {
                    "total_plays": total_plays,
                    "active_plays": active_plays,
                    "completed_plays": completed_plays,
                    "intervened_plays": intervened_plays,
                    "profitable_plays": profitable_count,
                    "losing_plays": losing_count,
                    "avg_profit": avg_profit or 0.0,
                    "avg_loss": avg_loss or 0.0,
                    "total_interventions": total_interventions,
                    "total_adaptations": total_adaptations,
                    "success_rate": profitable_count / (profitable_count + losing_count) if (profitable_count + losing_count) > 0 else 0.0
                }
                
            except Exception as e:
                logger.error(f"Error getting play statistics: {e}")
                return {}
            finally:
                conn.close()


# Global instance
play_reporting = PlayReportingSystem() 