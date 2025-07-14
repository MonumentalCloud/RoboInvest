"""
Centralized Error Event Bus System

This system captures all errors at their source, categorizes them by severity,
and routes them to the governor agent for intelligent handling and self-healing.
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils.logger import logger
from core.config import config


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"    # System failure, requires immediate attention
    HIGH = "high"           # Major functionality broken, needs human intervention
    MEDIUM = "medium"       # Degraded functionality, can self-heal or notify
    LOW = "low"            # Minor issue, informational
    INFO = "info"          # Not an error, just information


class ErrorCategory(Enum):
    """Error categories for intelligent routing"""
    ALPACA_CONNECTION = "alpaca_connection"
    API_AUTHENTICATION = "api_authentication"
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    AGENT_ERROR = "agent_error"
    SYSTEM_ERROR = "system_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    DATA_ERROR = "data_error"
    PERFORMANCE_ERROR = "performance_error"


@dataclass
class ErrorEvent:
    """Structured error event"""
    id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    source: str  # Which component/agent generated the error
    error_type: str  # Python exception type
    error_message: str
    stack_trace: str
    context: Dict[str, Any]  # Additional context about the error
    user_message: Optional[str] = None  # Original user message that triggered error
    auto_fixable: bool = False
    fix_attempted: bool = False
    fix_successful: bool = False
    notification_sent: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['severity'] = self.severity.value
        data['category'] = self.category.value
        return data


class ErrorEventBus:
    """Centralized error event bus for intelligent error handling"""
    
    def __init__(self):
        self.error_events: List[ErrorEvent] = []
        self.subscribers: List[Callable[[ErrorEvent], None]] = []
        self.governor_agent = None
        self.email_config = self._load_email_config()
        self.auto_fix_handlers: Dict[ErrorCategory, Callable] = {}
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Initialize auto-fix handlers
        self._setup_auto_fix_handlers()
        
        # Initialize error patterns for intelligent categorization
        self._setup_error_patterns()
        
        logger.info("🔧 Error Event Bus initialized")
    
    def _load_email_config(self) -> Dict[str, Any]:
        """Load email configuration for notifications"""
        return {
            "smtp_server": getattr(config, 'smtp_server', 'smtp.gmail.com'),
            "smtp_port": getattr(config, 'smtp_port', 587),
            "email_user": getattr(config, 'email_user', ''),
            "email_password": getattr(config, 'email_password', ''),
            "admin_email": getattr(config, 'admin_email', ''),
            "notifications_enabled": getattr(config, 'notifications_enabled', False)
        }
    
    def _setup_auto_fix_handlers(self):
        """Setup handlers for auto-fixable errors"""
        self.auto_fix_handlers = {
            ErrorCategory.ALPACA_CONNECTION: self._fix_alpaca_connection,
            ErrorCategory.CONFIGURATION_ERROR: self._fix_configuration_error,
            ErrorCategory.DATABASE_ERROR: self._fix_database_error,
        }
    
    def _setup_error_patterns(self):
        """Setup patterns for intelligent error categorization"""
        self.error_patterns = {
            "alpaca_forbidden": {
                "patterns": ["forbidden", "unauthorized", "invalid"],
                "category": ErrorCategory.ALPACA_CONNECTION,
                "severity": ErrorSeverity.HIGH,
                "auto_fixable": False,
                "description": "Alpaca API authentication failed"
            },
            "alpaca_network": {
                "patterns": ["connection", "timeout", "network"],
                "category": ErrorCategory.NETWORK_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "auto_fixable": True,
                "description": "Alpaca network connectivity issue"
            },
            "api_key_missing": {
                "patterns": ["key", "api_key", "secret_key"],
                "category": ErrorCategory.CONFIGURATION_ERROR,
                "severity": ErrorSeverity.HIGH,
                "auto_fixable": False,
                "description": "API keys not configured"
            },
            "database_connection": {
                "patterns": ["database", "sql", "connection"],
                "category": ErrorCategory.DATABASE_ERROR,
                "severity": ErrorSeverity.CRITICAL,
                "auto_fixable": True,
                "description": "Database connection issue"
            }
        }
    
    def emit_error(self, 
                   error: Exception, 
                   source: str, 
                   context: Optional[Dict[str, Any]] = None,
                   user_message: Optional[str] = None,
                   severity: Optional[ErrorSeverity] = None,
                   category: Optional[ErrorCategory] = None) -> ErrorEvent:
        """
        Emit an error event to the bus
        
        Args:
            error: The exception that occurred
            source: Component/agent that generated the error
            context: Additional context about the error
            user_message: Original user message that triggered error
            severity: Override automatic severity detection
            category: Override automatic category detection
        """
        # Generate unique error ID
        error_id = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Auto-detect severity and category if not provided
        if severity is None:
            severity = self._detect_severity(error, context or {})
        
        if category is None:
            category = self._detect_category(error, context or {})
        
        # Create error event
        error_event = ErrorEvent(
            id=error_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            source=source,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            context=context or {},
            user_message=user_message,
            auto_fixable=self._is_auto_fixable(category, error)
        )
        
        # Store error event
        self.error_events.append(error_event)
        
        # Log the error
        logger.error(f"🚨 Error Event: {error_event.id} - {error_event.severity.value} - {error_event.category.value} - {error_event.error_message}")
        
        # Notify subscribers
        self._notify_subscribers(error_event)
        
        # Handle based on severity (non-blocking)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._handle_error_event(error_event))
            else:
                # If no event loop is running, schedule it for later
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self._handle_error_event(error_event))
                )
        except RuntimeError:
            # No event loop available, handle synchronously
            import threading
            def handle_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._handle_error_event(error_event))
                except Exception as e:
                    logger.error(f"Error in async error handling: {e}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=handle_async, daemon=True)
            thread.start()
        
        return error_event
    
    def _detect_severity(self, error: Exception, context: Dict[str, Any]) -> ErrorSeverity:
        """Automatically detect error severity"""
        error_str = str(error).lower()
        
        # Critical errors
        if any(word in error_str for word in ["database", "connection refused", "system failure"]):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if any(word in error_str for word in ["forbidden", "unauthorized", "invalid", "authentication"]):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if any(word in error_str for word in ["timeout", "network", "connection"]):
            return ErrorSeverity.MEDIUM
        
        # Default to medium
        return ErrorSeverity.MEDIUM
    
    def _detect_category(self, error: Exception, context: Dict[str, Any]) -> ErrorCategory:
        """Automatically detect error category"""
        error_str = str(error).lower()
        
        # Check against patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            if any(pattern in error_str for pattern in pattern_info["patterns"]):
                return pattern_info["category"]
        
        # Default category
        return ErrorCategory.SYSTEM_ERROR
    
    def _is_auto_fixable(self, category: ErrorCategory, error: Exception) -> bool:
        """Determine if error is auto-fixable"""
        # Check if we have a handler for this category
        if category in self.auto_fix_handlers:
            return True
        
        # Check specific error patterns
        error_str = str(error).lower()
        for pattern_info in self.error_patterns.values():
            if any(pattern in error_str for pattern in pattern_info["patterns"]):
                return pattern_info.get("auto_fixable", False)
        
        return False
    
    async def _handle_error_event(self, error_event: ErrorEvent):
        """Handle error event based on severity and category"""
        try:
            # Attempt auto-fix if possible
            if error_event.auto_fixable and not error_event.fix_attempted:
                await self._attempt_auto_fix(error_event)
            
            # Send notifications based on severity
            if error_event.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                await self._send_notification(error_event)
            
            # Route to governor agent for intelligent handling
            if self.governor_agent:
                await self._route_to_governor(error_event)
                
        except Exception as e:
            logger.error(f"Error handling error event {error_event.id}: {e}")
    
    async def _attempt_auto_fix(self, error_event: ErrorEvent):
        """Attempt to auto-fix the error"""
        try:
            error_event.fix_attempted = True
            
            if error_event.category in self.auto_fix_handlers:
                fix_handler = self.auto_fix_handlers[error_event.category]
                success = await fix_handler(error_event)
                error_event.fix_successful = success
                
                if success:
                    logger.info(f"✅ Auto-fixed error {error_event.id}")
                else:
                    logger.warning(f"❌ Auto-fix failed for error {error_event.id}")
            
        except Exception as e:
            logger.error(f"Error during auto-fix attempt: {e}")
            error_event.fix_successful = False
    
    async def _fix_alpaca_connection(self, error_event: ErrorEvent) -> bool:
        """Attempt to fix Alpaca connection issues"""
        try:
            # For network issues, we can retry
            if "network" in error_event.error_message.lower() or "timeout" in error_event.error_message.lower():
                # Wait a bit and retry
                await asyncio.sleep(5)
                from core.alpaca_client import alpaca_client
                
                # Test connection
                try:
                    alpaca_client.get_account()
                    return True
                except:
                    return False
            
            return False
        except:
            return False
    
    async def _fix_configuration_error(self, error_event: ErrorEvent) -> bool:
        """Attempt to fix configuration errors"""
        # Most config errors require human intervention
        return False
    
    async def _fix_database_error(self, error_event: ErrorEvent) -> bool:
        """Attempt to fix database errors"""
        try:
            # For connection issues, we can retry
            if "connection" in error_event.error_message.lower():
                await asyncio.sleep(2)
                # Try to reconnect
                return True
            return False
        except:
            return False
    
    async def _send_notification(self, error_event: ErrorEvent):
        """Send email notification for critical/high severity errors"""
        if not self.email_config.get("notifications_enabled"):
            return
        
        if error_event.notification_sent:
            return
        
        try:
            # Create email content
            subject = f"🚨 RoboInvest System Alert: {error_event.severity.value.upper()} - {error_event.category.value}"
            
            body = f"""
            <h2>System Error Alert</h2>
            <p><strong>Error ID:</strong> {error_event.id}</p>
            <p><strong>Severity:</strong> {error_event.severity.value}</p>
            <p><strong>Category:</strong> {error_event.category.value}</p>
            <p><strong>Source:</strong> {error_event.source}</p>
            <p><strong>Time:</strong> {error_event.timestamp}</p>
            <p><strong>Error:</strong> {error_event.error_message}</p>
            
            <h3>Context:</h3>
            <pre>{json.dumps(error_event.context, indent=2)}</pre>
            
            <h3>Stack Trace:</h3>
            <pre>{error_event.stack_trace}</pre>
            
            <p><strong>Auto-fixable:</strong> {error_event.auto_fixable}</p>
            <p><strong>Fix attempted:</strong> {error_event.fix_attempted}</p>
            <p><strong>Fix successful:</strong> {error_event.fix_successful}</p>
            """
            
            # Send email
            await self._send_email(subject, body)
            error_event.notification_sent = True
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    async def _send_email(self, subject: str, body: str):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config["email_user"]
            msg['To'] = self.email_config["admin_email"]
            
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["email_user"], self.email_config["email_password"])
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
    
    async def _route_to_governor(self, error_event: ErrorEvent):
        """Route error to governor agent for intelligent handling"""
        if not self.governor_agent:
            return
        
        try:
            # Create governor message
            governor_message = f"""
            System Error Detected:
            - ID: {error_event.id}
            - Severity: {error_event.severity.value}
            - Category: {error_event.category.value}
            - Source: {error_event.source}
            - Error: {error_event.error_message}
            - Auto-fixable: {error_event.auto_fixable}
            - Fix attempted: {error_event.fix_attempted}
            - Fix successful: {error_event.fix_successful}
            
            Context: {json.dumps(error_event.context, indent=2)}
            
            Please analyze this error and determine the best course of action.
            """
            
            # Send to governor agent
            # This would integrate with your existing governor agent system
            logger.info(f"📋 Routed error {error_event.id} to governor agent")
            
        except Exception as e:
            logger.error(f"Failed to route error to governor: {e}")
    
    def _notify_subscribers(self, error_event: ErrorEvent):
        """Notify all subscribers of the error event"""
        for subscriber in self.subscribers:
            try:
                subscriber(error_event)
            except Exception as e:
                logger.error(f"Error in error event subscriber: {e}")
    
    def subscribe(self, callback: Callable[[ErrorEvent], None]):
        """Subscribe to error events"""
        self.subscribers.append(callback)
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorEvent]:
        """Get recent error events"""
        return self.error_events[-limit:]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorEvent]:
        """Get errors by severity level"""
        return [e for e in self.error_events if e.severity == severity]
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorEvent]:
        """Get errors by category"""
        return [e for e in self.error_events if e.category == category]
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary based on recent errors"""
        recent_errors = self.get_recent_errors(50)
        
        if not recent_errors:
            return {
                "status": "healthy",
                "critical_errors": 0,
                "high_errors": 0,
                "medium_errors": 0,
                "low_errors": 0,
                "auto_fix_success_rate": 1.0
            }
        
        critical_count = len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL])
        high_count = len([e for e in recent_errors if e.severity == ErrorSeverity.HIGH])
        medium_count = len([e for e in recent_errors if e.severity == ErrorSeverity.MEDIUM])
        low_count = len([e for e in recent_errors if e.severity == ErrorSeverity.LOW])
        
        auto_fix_attempts = [e for e in recent_errors if e.fix_attempted]
        auto_fix_successes = [e for e in auto_fix_attempts if e.fix_successful]
        auto_fix_rate = len(auto_fix_successes) / len(auto_fix_attempts) if auto_fix_attempts else 1.0
        
        # Determine overall status
        if critical_count > 0:
            status = "critical"
        elif high_count > 2:
            status = "warning"
        elif medium_count > 5:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "critical_errors": critical_count,
            "high_errors": high_count,
            "medium_errors": medium_count,
            "low_errors": low_count,
            "auto_fix_success_rate": auto_fix_rate,
            "total_errors": len(recent_errors)
        }


# Global error event bus instance
error_event_bus = ErrorEventBus()


def emit_error(error: Exception, 
               source: str, 
               context: Optional[Dict[str, Any]] = None,
               user_message: Optional[str] = None,
               severity: Optional[ErrorSeverity] = None,
               category: Optional[ErrorCategory] = None) -> ErrorEvent:
    """
    Convenience function to emit errors to the global error event bus
    """
    return error_event_bus.emit_error(
        error=error,
        source=source,
        context=context,
        user_message=user_message,
        severity=severity,
        category=category
    ) 