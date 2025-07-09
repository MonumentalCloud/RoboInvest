#!/usr/bin/env python3
"""
Agent Monitoring Decorators
Decorators that automatically integrate agents with the monitoring system.

Usage:
    @monitor_agent("research_agent")
    class ResearchAgent:
        @record_operation("market_analysis")
        async def analyze_market(self, data):
            # Agent logic here
            pass
        
        @record_output("insight")
        def generate_insight(self, data):
            # Generate insight
            return insight
"""

import functools
import time
import traceback
from typing import Any, Callable, Dict, Optional
from datetime import datetime

from agents.agent_monitoring_system import (
    agent_monitor, record_agent_metric, record_agent_error, 
    record_agent_success, record_agent_output, update_agent_heartbeat
)
from utils.logger import logger

def monitor_agent(agent_name: str):
    """
    Class decorator to automatically register an agent with the monitoring system.
    
    Args:
        agent_name: Name of the agent for monitoring
    """
    def decorator(cls):
        # Register the agent with monitoring system
        agent_monitor.register_agent(agent_name, {
            "class": cls.__name__,
            "module": cls.__module__,
            "registered_at": datetime.now().isoformat()
        })
        
        # Add monitoring methods to the class
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def monitored_init(self, *args, **kwargs):
            self._agent_name = agent_name
            self._start_time = datetime.now()
            
            # Update heartbeat on initialization
            update_agent_heartbeat(agent_name, "active", {
                "initialized": True,
                "start_time": self._start_time.isoformat()
            })
            
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Record successful initialization
            record_agent_success(agent_name, "initialization", None, {
                "class": cls.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
        
        cls.__init__ = monitored_init
        
        # Add heartbeat update method
        def update_heartbeat(self, status: str = "active", custom_metrics: Optional[Dict[str, Any]] = None):
            """Update agent heartbeat."""
            update_agent_heartbeat(agent_name, status, custom_metrics)
        
        cls.update_heartbeat = update_heartbeat
        
        # Add error recording method
        def record_error(self, error_type: str, error_message: str, 
                        stack_trace: str = "", context: Optional[Dict[str, Any]] = None, 
                        severity: str = "medium"):
            """Record an error for this agent."""
            record_agent_error(agent_name, error_type, error_message, stack_trace, context, severity)
        
        cls.record_error = record_error
        
        # Add success recording method
        def record_success(self, operation: str, duration: Optional[float] = None, 
                          metadata: Optional[Dict[str, Any]] = None):
            """Record a successful operation for this agent."""
            record_agent_success(agent_name, operation, duration, metadata)
        
        cls.record_success = record_success
        
        # Add output recording method
        def record_output(self, output_type: str, output_data: Any, 
                         metadata: Optional[Dict[str, Any]] = None):
            """Record an output from this agent."""
            record_agent_output(agent_name, output_type, output_data, metadata)
        
        cls.record_output = record_output
        
        logger.info(f"🔍 Added monitoring to agent class: {cls.__name__}")
        return cls
    
    return decorator

def record_operation(operation_name: str):
    """
    Method decorator to automatically record operation execution.
    
    Args:
        operation_name: Name of the operation being performed
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            
            try:
                # Update heartbeat before operation
                if hasattr(self, 'update_heartbeat'):
                    self.update_heartbeat("active", {"current_operation": operation_name})
                
                # Execute the function
                result = func(self, *args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Record success
                if hasattr(self, 'record_success'):
                    self.record_success(operation_name, duration, {
                        "args_count": len(args),
                        "kwargs_count": len(kwargs),
                        "result_type": type(result).__name__
                    })
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time
                
                # Record error
                if hasattr(self, 'record_error'):
                    self.record_error(
                        error_type=type(e).__name__,
                        error_message=str(e),
                        stack_trace=traceback.format_exc(),
                        context={
                            "operation": operation_name,
                            "duration": duration,
                            "args_count": len(args),
                            "kwargs_count": len(kwargs)
                        },
                        severity="high"
                    )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

def record_output_decorator(output_type: str):
    """
    Method decorator to automatically record outputs.
    
    Args:
        output_type: Type of output being generated
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the function
            result = func(self, *args, **kwargs)
            
            # Record the output
            if hasattr(self, 'record_output'):
                self.record_output(output_type, result, {
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                    "result_type": type(result).__name__
                })
            
            return result
        
        return wrapper
    return decorator

def monitor_performance(operation_name: str):
    """
    Method decorator to monitor performance metrics.
    
    Args:
        operation_name: Name of the operation for performance tracking
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute the function
                result = func(self, *args, **kwargs)
                
                # Calculate performance metrics
                duration = time.time() - start_time
                
                # Record performance metric
                if hasattr(self, '_agent_name'):
                    record_agent_metric(
                        self._agent_name,
                        "performance",
                        {
                            "operation": operation_name,
                            "duration": duration,
                            "timestamp": datetime.now().isoformat(),
                            "success": True
                        },
                        {
                            "args_count": len(args),
                            "kwargs_count": len(kwargs),
                            "result_type": type(result).__name__
                        }
                    )
                
                return result
                
            except Exception as e:
                # Calculate performance metrics
                duration = time.time() - start_time
                
                # Record performance metric for failed operation
                if hasattr(self, '_agent_name'):
                    record_agent_metric(
                        self._agent_name,
                        "performance",
                        {
                            "operation": operation_name,
                            "duration": duration,
                            "timestamp": datetime.now().isoformat(),
                            "success": False,
                            "error": str(e)
                        },
                        {
                            "args_count": len(args),
                            "kwargs_count": len(kwargs),
                            "error_type": type(e).__name__
                        }
                    )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

def auto_heartbeat(interval_seconds: int = 30):
    """
    Method decorator to automatically update heartbeat during long-running operations.
    
    Args:
        interval_seconds: How often to update heartbeat during operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            last_heartbeat = start_time
            
            # Create a wrapper that updates heartbeat periodically
            def heartbeat_wrapper():
                nonlocal last_heartbeat
                current_time = time.time()
                if current_time - last_heartbeat >= interval_seconds:
                    if hasattr(self, 'update_heartbeat'):
                        self.update_heartbeat("active", {
                            "operation": func.__name__,
                            "elapsed_time": current_time - start_time
                        })
                    last_heartbeat = current_time
            
            try:
                # Execute the function with periodic heartbeat updates
                result = func(self, *args, **kwargs)
                
                # Final heartbeat update
                if hasattr(self, 'update_heartbeat'):
                    self.update_heartbeat("active", {
                        "operation": func.__name__,
                        "completed": True,
                        "total_duration": time.time() - start_time
                    })
                
                return result
                
            except Exception as e:
                # Final heartbeat update on error
                if hasattr(self, 'update_heartbeat'):
                    self.update_heartbeat("error", {
                        "operation": func.__name__,
                        "error": str(e),
                        "total_duration": time.time() - start_time
                    })
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

# Convenience function for manual monitoring
def monitor_function_call(agent_name: str, function_name: str):
    """
    Decorator for standalone functions to monitor their execution.
    
    Args:
        agent_name: Name of the agent/component
        function_name: Name of the function being monitored
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Update heartbeat
                update_agent_heartbeat(agent_name, "active", {
                    "function": function_name,
                    "status": "executing"
                })
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Record success
                record_agent_success(agent_name, function_name, duration, {
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                    "result_type": type(result).__name__
                })
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time
                
                # Record error
                record_agent_error(
                    agent_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=traceback.format_exc(),
                    context={
                        "function": function_name,
                        "duration": duration,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    },
                    severity="high"
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator 