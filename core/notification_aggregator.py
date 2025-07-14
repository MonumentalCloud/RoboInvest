import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from utils.logger import logger
from agents.notification_system import send_email_notification

DB_PATH = "notification_buffer.db"

class NotificationAggregatorAgent:
    def __init__(self, db_path: str = DB_PATH, digest_interval_minutes: int = 60):
        self.db_path = db_path
        self.digest_interval = timedelta(minutes=digest_interval_minutes)
        self.lock = threading.Lock()
        self._init_db()
        self.last_digest_sent = None
        self.running = False

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT,
                    context_hash TEXT,
                    message TEXT,
                    context TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    count INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
            conn.close()

    def add_alert(self, alert_type: str, message: str, context: Dict[str, Any]):
        context_str = str(context)
        context_hash = str(hash(f"{alert_type}:{context_str}"))
        now = datetime.now().isoformat()
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Check for existing alert
            cursor.execute('''
                SELECT id, count FROM alerts WHERE alert_type = ? AND context_hash = ?
            ''', (alert_type, context_hash))
            row = cursor.fetchone()
            if row:
                alert_id, count = row
                cursor.execute('''
                    UPDATE alerts SET last_seen = ?, count = ? WHERE id = ?
                ''', (now, count + 1, alert_id))
            else:
                cursor.execute('''
                    INSERT INTO alerts (alert_type, context_hash, message, context, first_seen, last_seen, count)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                ''', (alert_type, context_hash, message, context_str, now, now))
            conn.commit()
            conn.close()

    def summarize_and_send(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT alert_type, message, context, first_seen, last_seen, count FROM alerts
            ''')
            alerts = cursor.fetchall()
            if not alerts:
                conn.close()
                return
            # Build summary
            summary_lines = [
                f"🚨 RoboInvest Emergency Digest 🚨",
                f"Time: {datetime.now().isoformat()}\n",
                f"Total unique alert types: {len(alerts)}\n"
            ]
            for alert in alerts:
                alert_type, message, context, first_seen, last_seen, count = alert
                summary_lines.append(f"Type: {alert_type}")
                summary_lines.append(f"Count: {count}")
                summary_lines.append(f"First Seen: {first_seen}")
                summary_lines.append(f"Last Seen: {last_seen}")
                summary_lines.append(f"Message: {message}")
                summary_lines.append(f"Context: {context}")
                summary_lines.append("-")
            summary = "\n".join(summary_lines)
            # Send summary email (can be extended to Slack/SMS)
            send_email_notification(
                subject="🚨 RoboInvest Emergency Digest 🚨",
                body=summary
            )
            logger.info("Sent emergency digest email.")
            # Clear alerts after sending
            cursor.execute('DELETE FROM alerts')
            conn.commit()
            conn.close()
            self.last_digest_sent = datetime.now()

    def start_background_loop(self):
        if self.running:
            return
        self.running = True
        def loop():
            while self.running:
                now = datetime.now()
                if (self.last_digest_sent is None or
                    now - self.last_digest_sent >= self.digest_interval):
                    self.summarize_and_send()
                time.sleep(60)  # Check every minute
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def stop(self):
        self.running = False

# Global instance
notification_aggregator = NotificationAggregatorAgent() 