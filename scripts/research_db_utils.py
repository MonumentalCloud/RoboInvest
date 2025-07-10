#!/usr/bin/env python3
"""
Utility functions for accessing and managing research databases.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

class ResearchDBManager:
    def __init__(self, db_dir="research_databases"):
        self.db_dir = Path(db_dir)
        self.tracks = [
            "alpha_discovery",
            "market_monitoring", 
            "sentiment_tracking",
            "technical_analysis",
            "risk_assessment",
            "deep_research"
        ]
    
    def get_db_path(self, track: str) -> Path:
        """Get the database path for a specific track"""
        return self.db_dir / f"{track}.db"
    
    def get_table_name(self, track: str) -> str:
        """Get the table name for a specific track"""
        table_map = {
            "alpha_discovery": "alpha_opportunities",
            "market_monitoring": "market_data",
            "sentiment_tracking": "sentiment_data",
            "technical_analysis": "technical_data",
            "risk_assessment": "risk_data",
            "deep_research": "research_data"
        }
        return table_map.get(track, "data")
    
    def query_track(self, track: str, limit: int = 100, days_back: int = 7) -> List[Dict[str, Any]]:
        """Query data from a specific research track"""
        db_path = self.get_db_path(track)
        if not db_path.exists():
            return []
        
        table_name = self.get_table_name(track)
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"""
        SELECT * FROM {table_name} 
        WHERE timestamp >= ? 
        ORDER BY timestamp DESC 
        LIMIT ?
        """
        
        cursor.execute(query, (cutoff_date, limit))
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_latest_data(self, track: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the latest data from a specific track"""
        return self.query_track(track, limit=limit, days_back=30)
    
    def get_alpha_opportunities(self, min_confidence: float = 0.6, limit: int = 50) -> List[Dict[str, Any]]:
        """Get high-confidence alpha opportunities"""
        db_path = self.get_db_path("alpha_discovery")
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM alpha_opportunities 
        WHERE confidence >= ? 
        ORDER BY confidence DESC, timestamp DESC 
        LIMIT ?
        """
        
        cursor.execute(query, (min_confidence, limit))
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_risk_alerts(self, risk_level: str = "high", limit: int = 20) -> List[Dict[str, Any]]:
        """Get high-risk alerts"""
        db_path = self.get_db_path("risk_assessment")
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM risk_data 
        WHERE risk_level = ? 
        ORDER BY risk_score DESC, timestamp DESC 
        LIMIT ?
        """
        
        cursor.execute(query, (risk_level, limit))
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_sentiment_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get sentiment analysis summary"""
        db_path = self.get_db_path("sentiment_tracking")
        if not db_path.exists():
            return {}
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            AVG(sentiment_score) as avg_sentiment,
            COUNT(*) as total_entries,
            MIN(sentiment_score) as min_sentiment,
            MAX(sentiment_score) as max_sentiment
        FROM sentiment_data 
        WHERE timestamp >= ?
        """
        
        cursor.execute(query, (cutoff_date,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                "avg_sentiment": row[0],
                "total_entries": row[1],
                "min_sentiment": row[2],
                "max_sentiment": row[3],
                "period_days": days_back
            }
        return {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics for all databases"""
        stats = {}
        
        for track in self.tracks:
            db_path = self.get_db_path(track)
            if db_path.exists():
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                table_name = self.get_table_name(track)
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT MAX(timestamp) FROM {table_name}")
                latest = cursor.fetchone()[0]
                
                conn.close()
                
                size_mb = db_path.stat().st_size / (1024 * 1024)
                
                stats[track] = {
                    "record_count": count,
                    "latest_entry": latest,
                    "size_mb": round(size_mb, 2)
                }
            else:
                stats[track] = {"record_count": 0, "latest_entry": None, "size_mb": 0}
        
        return stats
    
    def export_to_csv(self, track: str, output_file: Optional[str] = None) -> Optional[str]:
        """Export a track's data to CSV"""
        if output_file is None:
            output_file = f"{track}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        data = self.query_track(track, limit=10000, days_back=365)  # Export last year
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
            return output_file
        return None
    
    def cleanup_old_records(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old records from all databases"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        deleted_counts = {}
        
        for track in self.tracks:
            db_path = self.get_db_path(track)
            if db_path.exists():
                table_name = self.get_table_name(track)
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Count records before deletion
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                before_count = cursor.fetchone()[0]
                
                # Delete old records
                cursor.execute(f"DELETE FROM {table_name} WHERE timestamp < ?", (cutoff_date,))
                deleted_count = cursor.rowcount
                
                # Count records after deletion
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                after_count = cursor.fetchone()[0]
                
                conn.commit()
                conn.close()
                
                deleted_counts[track] = deleted_count
                print(f"🗑️  {track}: Deleted {deleted_count} old records ({before_count} -> {after_count})")
        
        return deleted_counts

def main():
    """Demo the database utilities"""
    db_manager = ResearchDBManager()
    
    print("📊 Research Database Manager")
    print("=" * 40)
    
    # Show database statistics
    print("\n📈 Database Statistics:")
    stats = db_manager.get_database_stats()
    for track, stat in stats.items():
        print(f"  {track}: {stat['record_count']} records, {stat['size_mb']} MB")
    
    # Show latest alpha opportunities
    print("\n🎯 Latest Alpha Opportunities:")
    opportunities = db_manager.get_alpha_opportunities(min_confidence=0.5, limit=5)
    for opp in opportunities:
        print(f"  • {opp.get('content', 'N/A')[:50]}... (Confidence: {opp.get('confidence', 0):.2f})")
    
    # Show risk alerts
    print("\n⚠️  High Risk Alerts:")
    risks = db_manager.get_risk_alerts(risk_level="high", limit=3)
    for risk in risks:
        print(f"  • {risk.get('content', 'N/A')[:50]}... (Risk: {risk.get('risk_score', 0):.2f})")
    
    # Show sentiment summary
    print("\n😊 Sentiment Summary (Last 7 days):")
    sentiment = db_manager.get_sentiment_summary(days_back=7)
    if sentiment and sentiment.get('avg_sentiment') is not None:
        print(f"  Average: {sentiment.get('avg_sentiment', 0):.3f}")
        print(f"  Total entries: {sentiment.get('total_entries', 0)}")
        print(f"  Range: {sentiment.get('min_sentiment', 0):.3f} to {sentiment.get('max_sentiment', 0):.3f}")
    else:
        print("  No sentiment data available")

if __name__ == "__main__":
    main() 