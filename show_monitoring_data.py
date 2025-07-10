#!/usr/bin/env python3
"""
Show Real Monitoring Data
Display the actual data stored in the agent monitoring database.
"""

import sqlite3
import json
from datetime import datetime

def show_monitoring_data():
    """Display all monitoring data from the database."""
    
    conn = sqlite3.connect("agent_monitoring.db")
    cursor = conn.cursor()
    
    print("🔍 REAL AGENT MONITORING DATA")
    print("=" * 50)
    
    # Show agent heartbeats
    print("\n📊 AGENT HEARTBEATS:")
    print("-" * 30)
    cursor.execute("SELECT agent_name, status, timestamp, memory_usage, cpu_usage FROM agent_heartbeats ORDER BY timestamp DESC LIMIT 10")
    heartbeats = cursor.fetchall()
    
    for heartbeat in heartbeats:
        agent_name, status, timestamp, memory, cpu = heartbeat
        print(f"🤖 {agent_name}: {status} at {timestamp}")
        print(f"   Memory: {memory:.1f}%, CPU: {cpu:.1f}%")
    
    # Show agent metrics
    print("\n📈 AGENT METRICS:")
    print("-" * 30)
    cursor.execute("SELECT agent_name, metric_type, value, timestamp FROM agent_metrics ORDER BY timestamp DESC LIMIT 15")
    metrics = cursor.fetchall()
    
    for metric in metrics:
        agent_name, metric_type, value, timestamp = metric
        try:
            value_data = json.loads(value)
            if metric_type == "performance":
                operation = value_data.get("operation", "unknown")
                duration = value_data.get("duration", 0)
                success = value_data.get("success", True)
                print(f"⚡ {agent_name} - {operation}: {duration:.2f}s ({'✅' if success else '❌'})")
            elif metric_type == "output":
                output_type = value_data.get("type", "unknown")
                print(f"📤 {agent_name} - {output_type}: {str(value_data)[:50]}...")
        except:
            print(f"📊 {agent_name} - {metric_type}: {value[:50]}...")
    
    # Show agent errors
    print("\n🚨 AGENT ERRORS:")
    print("-" * 30)
    cursor.execute("SELECT agent_name, error_type, error_message, severity, timestamp FROM agent_errors ORDER BY timestamp DESC LIMIT 10")
    errors = cursor.fetchall()
    
    for error in errors:
        agent_name, error_type, error_message, severity, timestamp = error
        print(f"❌ {agent_name} - {error_type} ({severity}): {error_message}")
        print(f"   Time: {timestamp}")
    
    # Show system summary
    print("\n🏥 SYSTEM SUMMARY:")
    print("-" * 30)
    
    # Count agents
    cursor.execute("SELECT COUNT(DISTINCT agent_name) FROM agent_heartbeats")
    total_agents = cursor.fetchone()[0]
    
    # Count healthy agents
    cursor.execute("SELECT COUNT(DISTINCT agent_name) FROM agent_heartbeats WHERE status = 'active'")
    healthy_agents = cursor.fetchone()[0]
    
    # Count errors
    cursor.execute("SELECT COUNT(*) FROM agent_errors")
    total_errors = cursor.fetchone()[0]
    
    # Count critical errors
    cursor.execute("SELECT COUNT(*) FROM agent_errors WHERE severity = 'critical'")
    critical_errors = cursor.fetchone()[0]
    
    print(f"Total Agents: {total_agents}")
    print(f"Healthy Agents: {healthy_agents}")
    print(f"Total Errors: {total_errors}")
    print(f"Critical Errors: {critical_errors}")
    print(f"Health Percentage: {(healthy_agents/total_agents*100):.1f}%" if total_agents > 0 else "Health Percentage: 0%")
    
    conn.close()

if __name__ == "__main__":
    show_monitoring_data() 