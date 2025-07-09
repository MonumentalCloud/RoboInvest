#!/usr/bin/env python3
"""
Notification System for Meta-Agent
Real notification system for emergencies and daily reports.
"""

import asyncio
import json
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from utils.logger import logger

class NotificationSystem:
    """
    Real notification system for the meta-agent.
    
    Features:
    - SMS alerts for critical emergencies
    - Daily email reports
    - Slack/Discord webhook notifications
    - Configurable notification levels
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.notification_history = []
        self.daily_report_sent = False
        self.last_daily_report = None
        
        # Initialize notification channels
        self.sms_enabled = bool(self.config.get("sms", {}).get("enabled", False))
        self.email_enabled = bool(self.config.get("email", {}).get("enabled", False))
        self.slack_enabled = bool(self.config.get("slack", {}).get("enabled", False))
        
        logger.info("📱 Notification System initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notification configuration."""
        config_path = Path("notification_config.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load notification config: {e}")
        
        # Default configuration
        default_config = {
            "sms": {
                "enabled": False,
                "provider": "twilio",
                "account_sid": "",
                "auth_token": "",
                "from_number": "",
                "to_number": ""
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_email": ""
            },
            "slack": {
                "enabled": False,
                "webhook_url": ""
            },
            "notification_levels": {
                "critical": ["sms", "email", "slack"],
                "high": ["email", "slack"],
                "medium": ["email"],
                "low": ["email"]
            },
            "daily_report_time": "18:00",  # 6 PM
            "emergency_thresholds": {
                "critical_errors": 5,
                "offline_agents": 2,
                "system_health_below": 70
            }
        }
        
        # Save default config
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"📝 Created default notification config: {config_path}")
        return default_config
    
    async def send_emergency_alert(self, alert_type: str, message: str, context: Dict[str, Any] = None):
        """Send emergency alert via SMS and other channels."""
        logger.critical(f"🚨 EMERGENCY ALERT: {alert_type} - {message}")
        
        # Format emergency message
        emergency_msg = f"""
🚨 ROBOTINVEST EMERGENCY ALERT 🚨

Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Message: {message}

Context: {json.dumps(context, indent=2) if context else 'None'}

System requires immediate attention.
        """.strip()
        
        # Send via all critical channels
        tasks = []
        
        if self.sms_enabled:
            tasks.append(self._send_sms(emergency_msg))
        
        if self.email_enabled:
            tasks.append(self._send_email("🚨 RoboInvest Emergency Alert", emergency_msg))
        
        if self.slack_enabled:
            tasks.append(self._send_slack_alert(emergency_msg))
        
        # Execute all notifications
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Notification failed: {result}")
                else:
                    logger.info(f"Emergency notification sent via channel {i}")
        
        # Record notification
        self.notification_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "emergency",
            "alert_type": alert_type,
            "message": message,
            "context": context,
            "channels": ["sms", "email", "slack"] if self.sms_enabled and self.email_enabled and self.slack_enabled else []
        })
    
    async def send_daily_report(self, report_data: Dict[str, Any]):
        """Send daily system report."""
        logger.info("📊 Sending daily system report")
        
        # Format daily report
        report = self._format_daily_report(report_data)
        
        # Send via email and Slack
        tasks = []
        
        if self.email_enabled:
            tasks.append(self._send_email("📊 RoboInvest Daily System Report", report))
        
        if self.slack_enabled:
            tasks.append(self._send_slack_report(report))
        
        # Execute notifications
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Daily report notification failed: {result}")
                else:
                    logger.info(f"Daily report sent via channel {i}")
        
        # Update daily report status
        self.daily_report_sent = True
        self.last_daily_report = datetime.now()
        
        # Record notification
        self.notification_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "daily_report",
            "report_data": report_data,
            "channels": ["email", "slack"] if self.email_enabled and self.slack_enabled else []
        })
    
    def _format_daily_report(self, report_data: Dict[str, Any]) -> str:
        """Format comprehensive investor letter for notification."""
        
        # Check if this is an investor letter format
        if "executive_summary" in report_data:
            return self._format_investor_letter(report_data)
        
        # Fall back to basic daily report format
        system_health = report_data.get("system_health", {})
        performance = report_data.get("performance_metrics", {})
        activities = report_data.get("recent_activities", {})
        
        report = f"""
📊 ROBOTINVEST DAILY SYSTEM REPORT
Date: {datetime.now().strftime('%Y-%m-%d')}
Time: {datetime.now().strftime('%H:%M:%S')}

🏥 SYSTEM HEALTH
Total Agents: {system_health.get('total_agents', 0)}
Healthy Agents: {system_health.get('healthy_agents', 0)}
Health Percentage: {system_health.get('health_percentage', 0):.1f}%
Critical Alerts: {system_health.get('critical_alerts', 0)}
Unresolved Alerts: {system_health.get('unresolved_alerts', 0)}

📈 PERFORMANCE METRICS
Average Success Rate: {performance.get('avg_success_rate', 0):.2f}
Total Insights Generated: {performance.get('total_insights_generated', 0)}
Total Trades Executed: {performance.get('total_trades_executed', 0)}
System Uptime: {performance.get('system_uptime', 'Unknown')}
Average Response Time: {performance.get('avg_response_time', 0):.2f}s

🔄 RECENT ACTIVITIES
Code Changes Applied: {activities.get('code_changes_applied', 0)}
Optimizations Applied: {activities.get('optimizations_applied', 0)}
Agents Restarted: {activities.get('agents_restarted', 0)}
New Alerts: {activities.get('new_alerts', 0)}

💡 RECOMMENDATIONS
{chr(10).join(report_data.get('recommendations', ['No recommendations']))}

🔍 DETAILED METRICS
{json.dumps(report_data, indent=2)}
        """.strip()
        
        return report
    
    def _format_investor_letter(self, report_data: Dict[str, Any]) -> str:
        """Format comprehensive investor letter."""
        
        # Executive Summary
        executive_summary = report_data.get("executive_summary", "")
        
        # System Performance
        system_perf = report_data.get("system_performance", {})
        
        # Research Insights
        research_insights = report_data.get("research_insights", [])
        high_confidence_insights = [i for i in research_insights if float(i.get("confidence", "0%").rstrip("%")) > 80]
        
        # Trading Positions
        trading_positions = report_data.get("trading_positions", [])
        total_pnl = sum(float(pos.get("pnl", "$0").replace("$", "").replace(",", "")) for pos in trading_positions)
        profitable_positions = len([p for p in trading_positions if float(p.get("pnl", "$0").replace("$", "").replace(",", "")) > 0])
        
        # Risk Assessments
        risk_assessments = report_data.get("risk_assessments", [])
        critical_risks = [r for r in risk_assessments if r.get("severity") == "critical"]
        
        # Market Opportunities
        market_opportunities = report_data.get("market_opportunities", [])
        
        # Trading Plays
        trading_plays = report_data.get("trading_plays", [])
        
        # AI Insights
        ai_insights = report_data.get("ai_insights", {})
        
        # Recommendations
        recommendations = report_data.get("recommendations", [])
        
        report = f"""
📈 ROBOTINVEST INVESTOR LETTER
Date: {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}
Time: {report_data.get('time', datetime.now().strftime('%H:%M:%S'))}
Report ID: {report_data.get('report_id', 'N/A')}

🎯 EXECUTIVE SUMMARY
{executive_summary}

🏥 SYSTEM PERFORMANCE
Overall Health: {system_perf.get('overall_health', 'N/A')}
Total Agents: {system_perf.get('total_agents', 0)}
Active Research Agents: {system_perf.get('active_research_agents', 0)}
Total Insights Generated: {system_perf.get('total_insights_generated', 0)}
Total Positions: {system_perf.get('total_positions', 0)}
System Uptime: {system_perf.get('system_uptime', 'N/A')}
Average Response Time: {system_perf.get('average_response_time', 0):.2f}s

🔍 RESEARCH INSIGHTS ({len(research_insights)} total, {len(high_confidence_insights)} high confidence)
"""
        
        # Add top research insights
        for i, insight in enumerate(research_insights[:5]):  # Top 5 insights
            report += f"""
{i+1}. {insight.get('symbol', 'N/A')} - {insight.get('type', 'N/A')}
   Confidence: {insight.get('confidence', 'N/A')}
   Expected Return: {insight.get('expected_return', 'N/A')}
   Risk Level: {insight.get('risk_level', 'N/A')}
   Reasoning: {insight.get('reasoning', 'N/A')[:100]}...
   Agent: {insight.get('agent', 'N/A')}
"""
        
        report += f"""
📊 TRADING POSITIONS ({len(trading_positions)} total, {profitable_positions} profitable)
Total P&L: ${total_pnl:.2f}
"""
        
        # Add top trading positions
        for i, position in enumerate(trading_positions[:5]):  # Top 5 positions
            report += f"""
{i+1}. {position.get('symbol', 'N/A')} - {position.get('type', 'N/A')}
   Entry: {position.get('entry_price', 'N/A')} | Current: {position.get('current_price', 'N/A')}
   Quantity: {position.get('quantity', 'N/A')} | P&L: {position.get('pnl', 'N/A')} ({position.get('pnl_percentage', 'N/A')})
   Reasoning: {position.get('reasoning', 'N/A')[:80]}...
"""
        
        report += f"""
⚠️ RISK ASSESSMENTS ({len(risk_assessments)} total, {len(critical_risks)} critical)
"""
        
        # Add critical risks
        for i, risk in enumerate(critical_risks[:3]):  # Top 3 critical risks
            report += f"""
{i+1}. {risk.get('type', 'N/A')} - {risk.get('severity', 'N/A')}
   Description: {risk.get('description', 'N/A')[:100]}...
   Affected: {', '.join(risk.get('affected_symbols', []))}
   Mitigation: {risk.get('mitigation', 'N/A')[:80]}...
"""
        
        report += f"""
🎯 MARKET OPPORTUNITIES ({len(market_opportunities)} identified)
"""
        
        # Add top opportunities
        for i, opportunity in enumerate(market_opportunities[:3]):  # Top 3 opportunities
            report += f"""
{i+1}. {opportunity.get('symbol', 'N/A')} - {opportunity.get('type', 'N/A')}
   Confidence: {opportunity.get('confidence', 'N/A')}
   Expected Return: {opportunity.get('expected_return', 'N/A')}
   Risk Level: {opportunity.get('risk_level', 'N/A')}
   Source: {opportunity.get('source_agent', 'N/A')}
"""
        
        report += f"""
🎮 TRADING PLAYS ({len(trading_plays)} active)
"""
        
        # Add top trading plays
        for i, play in enumerate(trading_plays[:3]):  # Top 3 plays
            report += f"""
{i+1}. {play.get('symbol', 'N/A')} - {play.get('strategy', 'N/A')}
   Entry: {play.get('entry_price', 'N/A')} | Target: {play.get('target_price', 'N/A')}
   Stop Loss: {play.get('stop_loss', 'N/A')} | Timeframe: {play.get('timeframe', 'N/A')}
   Confidence: {play.get('confidence', 'N/A')} | Risk: {play.get('risk_level', 'N/A')}
   Source: {play.get('source', 'N/A')}
"""
        
        report += f"""
🤖 AI INSIGHTS
Market Sentiment: {ai_insights.get('market_sentiment', 'N/A')}
System Performance: {ai_insights.get('system_performance', 'N/A')}
Risk Level: {ai_insights.get('risk_level', 'N/A')}
AI Analysis: {ai_insights.get('ai_analysis', 'N/A')[:200]}...

💡 RECOMMENDATIONS
"""
        
        for i, rec in enumerate(recommendations[:5]):  # Top 5 recommendations
            report += f"{i+1}. {rec}\n"
        
        report += f"""

📊 PERFORMANCE METRICS
{json.dumps(report_data.get('performance_metrics', {}), indent=2)}

---
Generated by RoboInvest Autonomous Trading System
Real-time data from {system_perf.get('total_agents', 0)} AI agents
        """.strip()
        
        return report
    
    async def _send_sms(self, message: str) -> bool:
        """Send SMS via Twilio."""
        if not self.sms_enabled:
            return False
        
        try:
            sms_config = self.config["sms"]
            
            # Twilio SMS
            if sms_config["provider"] == "twilio":
                url = f"https://api.twilio.com/2010-04-01/Accounts/{sms_config['account_sid']}/Messages.json"
                
                data = {
                    "From": sms_config["from_number"],
                    "To": sms_config["to_number"],
                    "Body": message
                }
                
                response = requests.post(
                    url,
                    data=data,
                    auth=(sms_config["account_sid"], sms_config["auth_token"])
                )
                
                if response.status_code == 201:
                    logger.info("📱 SMS sent successfully")
                    return True
                else:
                    logger.error(f"📱 SMS failed: {response.status_code} - {response.text}")
                    return False
            
            # Add other SMS providers here
            else:
                logger.error(f"📱 Unsupported SMS provider: {sms_config['provider']}")
                return False
                
        except Exception as e:
            logger.error(f"📱 SMS error: {e}")
            return False
    
    async def _send_email(self, subject: str, message: str) -> bool:
        """Send email notification."""
        if not self.email_enabled:
            return False
        
        try:
            email_config = self.config["email"]
            
            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = email_config["to_email"]
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["from_email"], email_config["to_email"], text)
            server.quit()
            
            logger.info("📧 Email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"📧 Email error: {e}")
            return False
    
    async def _send_slack_alert(self, message: str) -> bool:
        """Send Slack alert."""
        if not self.slack_enabled:
            return False
        
        try:
            slack_config = self.config["slack"]
            
            payload = {
                "text": message,
                "username": "RoboInvest Meta-Agent",
                "icon_emoji": ":robot_face:"
            }
            
            response = requests.post(slack_config["webhook_url"], json=payload)
            
            if response.status_code == 200:
                logger.info("💬 Slack alert sent successfully")
                return True
            else:
                logger.error(f"💬 Slack alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"💬 Slack error: {e}")
            return False
    
    async def _send_slack_report(self, report: str) -> bool:
        """Send Slack daily report."""
        if not self.slack_enabled:
            return False
        
        try:
            slack_config = self.config["slack"]
            
            payload = {
                "text": report,
                "username": "RoboInvest Daily Report",
                "icon_emoji": ":chart_with_upwards_trend:"
            }
            
            response = requests.post(slack_config["webhook_url"], json=payload)
            
            if response.status_code == 200:
                logger.info("💬 Slack report sent successfully")
                return True
            else:
                logger.error(f"💬 Slack report failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"💬 Slack report error: {e}")
            return False
    
    def should_send_daily_report(self) -> bool:
        """Check if it's time to send daily report."""
        if not self.last_daily_report:
            return True
        
        # Check if it's been more than 24 hours
        time_since_last = datetime.now() - self.last_daily_report
        return time_since_last.total_seconds() > 86400  # 24 hours
    
    def check_emergency_conditions(self, system_health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if emergency conditions are met."""
        emergencies = []
        thresholds = self.config["emergency_thresholds"]
        
        # Check critical errors
        if system_health.get("critical_alerts", 0) >= thresholds["critical_errors"]:
            emergencies.append({
                "type": "critical_errors",
                "message": f"Critical errors threshold exceeded: {system_health['critical_alerts']}",
                "context": {"critical_alerts": system_health["critical_alerts"]}
            })
        
        # Check offline agents
        if system_health.get("offline_agents", 0) >= thresholds["offline_agents"]:
            emergencies.append({
                "type": "offline_agents",
                "message": f"Too many agents offline: {system_health['offline_agents']}",
                "context": {"offline_agents": system_health["offline_agents"]}
            })
        
        # Check system health
        if system_health.get("health_percentage", 100) < thresholds["system_health_below"]:
            emergencies.append({
                "type": "system_health",
                "message": f"System health below threshold: {system_health['health_percentage']:.1f}%",
                "context": {"health_percentage": system_health["health_percentage"]}
            })
        
        return emergencies
    
    def get_notification_history(self) -> List[Dict[str, Any]]:
        """Get notification history."""
        return self.notification_history

# Global notification system instance
notification_system = NotificationSystem() 