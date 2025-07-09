# RoboInvest Notification System Overview

## 🚨 Real-Time Emergency Alerts & Daily Reports

The RoboInvest notification system provides real-time SMS alerts for emergencies and daily email reports, ensuring you're always informed about your autonomous trading system's status.

## 📱 Features

### Emergency Alerts
- **SMS Alerts**: Instant text messages for critical issues
- **Email Alerts**: Detailed emergency notifications
- **Slack/Discord**: Team notifications via webhooks
- **Configurable Thresholds**: Set your own emergency conditions

### Daily Reports
- **Comprehensive System Health**: Agent status, performance metrics
- **Performance Analytics**: Success rates, insights generated, trades executed
- **Recent Activities**: Code changes, optimizations, agent restarts
- **AI Recommendations**: Automated suggestions for improvements

### Smart Monitoring
- **Real-Time Health Checks**: Continuous monitoring of all agents
- **Automatic Threshold Detection**: Triggers alerts when conditions are met
- **Historical Tracking**: Complete notification history
- **Multi-Channel Delivery**: Redundant notification paths

## 🔧 Setup Instructions

### 1. SMS Alerts (Twilio)

To receive SMS alerts on your phone:

1. **Sign up for Twilio**:
   - Go to [twilio.com](https://www.twilio.com)
   - Create a free account
   - Get your Account SID and Auth Token

2. **Get a Twilio Phone Number**:
   - Purchase a phone number in your Twilio console
   - This will be your "from" number

3. **Update Configuration**:
   ```json
   {
     "sms": {
       "enabled": true,
       "provider": "twilio",
       "account_sid": "YOUR_ACTUAL_ACCOUNT_SID",
       "auth_token": "YOUR_ACTUAL_AUTH_TOKEN",
       "from_number": "YOUR_TWILIO_PHONE_NUMBER",
       "to_number": "YOUR_PHONE_NUMBER"
     }
   }
   ```

### 2. Email Reports (Gmail)

To receive daily email reports:

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"

3. **Update Configuration**:
   ```json
   {
     "email": {
       "enabled": true,
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "username": "your.email@gmail.com",
       "password": "YOUR_APP_PASSWORD",
       "from_email": "your.email@gmail.com",
       "to_email": "your.email@gmail.com"
     }
   }
   ```

### 3. Slack/Discord Notifications

For team notifications:

1. **Create Webhook**:
   - Slack: Create a webhook in your workspace
   - Discord: Create a webhook in your server

2. **Update Configuration**:
   ```json
   {
     "slack": {
       "enabled": true,
       "webhook_url": "YOUR_WEBHOOK_URL"
     }
   }
   ```

## 🚨 Emergency Conditions

The system automatically triggers emergency alerts when:

- **Critical Errors**: 5+ critical errors in the system
- **Offline Agents**: 2+ agents go offline
- **System Health**: Overall health drops below 70%
- **Agent Failures**: Individual agents fail repeatedly
- **Health Check Failures**: Monitoring system can't reach agents

### Emergency Alert Example
```
🚨 ROBOTINVEST EMERGENCY ALERT 🚨

Type: agent_failure
Time: 2025-07-10 15:30:45
Message: Agent trade_executor_agent is failing with 3 errors

Context: {
  "agent_name": "trade_executor_agent",
  "error_count": 3,
  "success_rate": 0.45,
  "last_heartbeat": "2025-07-10T15:30:45.123456"
}

System requires immediate attention.
```

## 📊 Daily Report Example

```
📊 ROBOTINVEST DAILY SYSTEM REPORT
Date: 2025-07-10
Time: 18:00:00

🏥 SYSTEM HEALTH
Total Agents: 8
Healthy Agents: 7
Health Percentage: 87.5%
Critical Alerts: 0
Unresolved Alerts: 1

📈 PERFORMANCE METRICS
Average Success Rate: 0.92
Total Insights Generated: 45
Total Trades Executed: 12
System Uptime: 99.8%
Average Response Time: 2.3s

🔄 RECENT ACTIVITIES
Code Changes Applied: 2
Optimizations Applied: 1
Agents Restarted: 0
New Alerts: 1

💡 RECOMMENDATIONS
- System operating normally - continue monitoring for optimization opportunities
- Consider adding more specialized agents for enhanced coverage
- Review performance metrics for potential improvements
```

## 🔧 Configuration Options

### Emergency Thresholds
```json
{
  "emergency_thresholds": {
    "critical_errors": 5,        // Alert after 5+ critical errors
    "offline_agents": 2,         // Alert after 2+ agents offline
    "system_health_below": 70    // Alert when health < 70%
  }
}
```

### Notification Levels
```json
{
  "notification_levels": {
    "critical": ["sms", "email", "slack"],  // All channels for emergencies
    "high": ["email", "slack"],             // Email + Slack for high priority
    "medium": ["email"],                    // Email only for medium
    "low": ["email"]                        // Email only for low
  }
}
```

### Daily Report Schedule
```json
{
  "daily_report_time": "18:00"  // Send daily report at 6 PM
}
```

## 🧪 Testing the System

### Test Emergency Alert
```python
from agents.notification_system import notification_system

# Test emergency alert (will send SMS if configured)
await notification_system.send_emergency_alert(
    "test_emergency",
    "This is a test emergency alert",
    {"test": True, "timestamp": "2025-07-10T15:30:45"}
)
```

### Test Daily Report
```python
# Test daily report (will send email if configured)
test_report = {
    "system_health": {
        "total_agents": 8,
        "healthy_agents": 7,
        "health_percentage": 87.5,
        "critical_alerts": 0
    },
    "performance_metrics": {
        "avg_success_rate": 0.92,
        "total_insights_generated": 45,
        "total_trades_executed": 12
    },
    "recent_activities": {
        "code_changes_applied": 2,
        "optimizations_applied": 1,
        "agents_restarted": 0,
        "new_alerts": 1
    },
    "recommendations": ["System operating normally"]
}

await notification_system.send_daily_report(test_report)
```

## 🔍 Monitoring Integration

The notification system is fully integrated with the meta-agent:

### Automatic Emergency Detection
```python
# Meta-agent automatically checks for emergencies
system_health = agent_monitor.get_system_health_summary()
emergencies = notification_system.check_emergency_conditions(system_health)

for emergency in emergencies:
    await notification_system.send_emergency_alert(
        emergency["type"],
        emergency["message"],
        emergency["context"]
    )
```

### Automatic Daily Reports
```python
# Meta-agent sends daily reports automatically
if notification_system.should_send_daily_report():
    daily_report = await meta_agent._generate_daily_report()
    await notification_system.send_daily_report(daily_report)
```

## 📱 Notification History

All notifications are logged and can be retrieved:

```python
# Get notification history
history = notification_system.get_notification_history()

for notification in history:
    print(f"{notification['timestamp']}: {notification['type']}")
```

## 🛡️ Security Considerations

1. **API Keys**: Store Twilio credentials securely
2. **App Passwords**: Use Gmail app passwords, not regular passwords
3. **Webhook URLs**: Keep Slack/Discord webhook URLs private
4. **Rate Limiting**: System respects API rate limits
5. **Error Handling**: Failed notifications are logged but don't crash the system

## 🔧 Troubleshooting

### SMS Not Working
- Verify Twilio credentials are correct
- Check phone number format (+1234567890)
- Ensure Twilio account has credits
- Check Twilio console for error logs

### Email Not Working
- Verify Gmail app password is correct
- Check 2-factor authentication is enabled
- Ensure SMTP settings are correct
- Check Gmail security settings

### No Notifications
- Verify notification channels are enabled in config
- Check system logs for error messages
- Ensure meta-agent is running
- Verify emergency thresholds are appropriate

## 📈 Performance Impact

- **Minimal Overhead**: Notifications are asynchronous
- **Rate Limited**: Respects API rate limits
- **Non-Blocking**: Failed notifications don't affect trading
- **Efficient**: Only sends when conditions are met

## 🎯 Best Practices

1. **Start with Email**: Enable email notifications first
2. **Add SMS for Critical**: Use SMS only for true emergencies
3. **Test Regularly**: Test notifications monthly
4. **Monitor Costs**: Track Twilio usage and costs
5. **Review Thresholds**: Adjust emergency thresholds based on experience
6. **Backup Channels**: Use multiple notification channels for redundancy

## 🚀 Getting Started

1. **Copy the configuration template**:
   ```bash
   cp notification_config.json notification_config.json.backup
   ```

2. **Edit the configuration** with your real credentials

3. **Test the system**:
   ```bash
   python test_real_agent_monitoring.py
   ```

4. **Monitor the logs** for notification activity

5. **Adjust thresholds** based on your system's behavior

The notification system ensures you're always informed about your autonomous trading system's health and performance, with real-time alerts for emergencies and comprehensive daily reports for ongoing monitoring. 