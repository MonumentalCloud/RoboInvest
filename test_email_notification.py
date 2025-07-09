#!/usr/bin/env python3
"""
Test Email Notification System
Simple test to verify email notifications work with the configured credentials.
"""

import asyncio
from datetime import datetime
from agents.notification_system import notification_system
from utils.logger import logger

async def test_email_notification():
    """Test email notification functionality."""
    logger.info("📧 Testing email notification system...")
    
    # Test emergency alert via email
    logger.info("🚨 Testing emergency alert email...")
    await notification_system.send_emergency_alert(
        "email_test",
        "This is a test emergency alert to verify email notifications work",
        {
            "test_type": "email_verification",
            "timestamp": datetime.now().isoformat(),
            "system": "RoboInvest",
            "status": "testing"
        }
    )
    
    # Test daily report via email
    logger.info("📊 Testing daily report email...")
    test_report = {
        "system_health": {
            "total_agents": 8,
            "healthy_agents": 7,
            "health_percentage": 87.5,
            "critical_alerts": 0,
            "unresolved_alerts": 1,
            "degraded_agents": 1,
            "failing_agents": 0,
            "offline_agents": 0
        },
        "performance_metrics": {
            "avg_success_rate": 0.92,
            "total_insights_generated": 45,
            "total_trades_executed": 12,
            "system_uptime": "99.8%",
            "avg_response_time": 2.3
        },
        "recent_activities": {
            "code_changes_applied": 2,
            "optimizations_applied": 1,
            "agents_restarted": 0,
            "new_alerts": 1
        },
        "recommendations": [
            "System operating normally - continue monitoring for optimization opportunities",
            "Consider adding more specialized agents for enhanced coverage",
            "Review performance metrics for potential improvements"
        ]
    }
    
    await notification_system.send_daily_report(test_report)
    
    logger.info("✅ Email notification test completed!")
    logger.info("📧 Check your email inbox for test messages")
    logger.info("📧 If you don't see emails, check the logs above for error messages")

if __name__ == "__main__":
    try:
        asyncio.run(test_email_notification())
    except Exception as e:
        logger.error(f"❌ Email test failed: {e}")
        import traceback
        traceback.print_exc() 