#!/usr/bin/env python3
"""
Test script for the Error Event Bus System

This script demonstrates how errors are captured, categorized, and handled
by the centralized error event bus.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.error_event_bus import error_event_bus, emit_error, ErrorSeverity, ErrorCategory
from utils.logger import logger


def test_basic_error_emission():
    """Test basic error emission"""
    print("🧪 Testing basic error emission...")
    
    try:
        # Simulate an Alpaca authentication error
        raise Exception("forbidden: invalid API key")
    except Exception as e:
        error_event = emit_error(
            error=e,
            source="test_script",
            context={"test_type": "alpaca_auth"},
            user_message="Show me my positions",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.ALPACA_CONNECTION
        )
        
        print(f"✅ Error emitted: {error_event.id}")
        print(f"   Severity: {error_event.severity.value}")
        print(f"   Category: {error_event.category.value}")
        print(f"   Auto-fixable: {error_event.auto_fixable}")


def test_network_error():
    """Test network error handling"""
    print("\n🧪 Testing network error...")
    
    try:
        raise Exception("connection timeout: network unreachable")
    except Exception as e:
        error_event = emit_error(
            error=e,
            source="test_script",
            context={"test_type": "network_error"},
            user_message="Get market data"
        )
        
        print(f"✅ Network error emitted: {error_event.id}")
        print(f"   Severity: {error_event.severity.value}")
        print(f"   Category: {error_event.category.value}")
        print(f"   Auto-fixable: {error_event.auto_fixable}")


def test_database_error():
    """Test database error handling"""
    print("\n🧪 Testing database error...")
    
    try:
        raise Exception("database connection refused")
    except Exception as e:
        error_event = emit_error(
            error=e,
            source="test_script",
            context={"test_type": "database_error"},
            user_message="Save trade data"
        )
        
        print(f"✅ Database error emitted: {error_event.id}")
        print(f"   Severity: {error_event.severity.value}")
        print(f"   Category: {error_event.category.value}")
        print(f"   Auto-fixable: {error_event.auto_fixable}")


def test_system_health():
    """Test system health summary"""
    print("\n🧪 Testing system health summary...")
    
    health_summary = error_event_bus.get_system_health_summary()
    print(f"System Status: {health_summary['status']}")
    print(f"Critical Errors: {health_summary['critical_errors']}")
    print(f"High Errors: {health_summary['high_errors']}")
    print(f"Medium Errors: {health_summary['medium_errors']}")
    print(f"Auto-fix Success Rate: {health_summary['auto_fix_success_rate']:.2%}")


def test_error_categorization():
    """Test automatic error categorization"""
    print("\n🧪 Testing automatic error categorization...")
    
    test_errors = [
        ("forbidden: invalid credentials", "auth_test"),
        ("connection timeout", "network_test"),
        ("database connection refused", "db_test"),
        ("api key not found", "config_test"),
        ("unknown error occurred", "unknown_test")
    ]
    
    for error_msg, test_name in test_errors:
        try:
            raise Exception(error_msg)
        except Exception as e:
            error_event = emit_error(
                error=e,
                source=test_name,
                context={"test_type": "auto_categorization"}
            )
            
            print(f"Error: {error_msg}")
            print(f"  → Detected Category: {error_event.category.value}")
            print(f"  → Detected Severity: {error_event.severity.value}")
            print(f"  → Auto-fixable: {error_event.auto_fixable}")
            print()


async def test_async_handling():
    """Test async error handling"""
    print("\n🧪 Testing async error handling...")
    
    try:
        raise Exception("async test error")
    except Exception as e:
        error_event = emit_error(
            error=e,
            source="async_test",
            context={"test_type": "async_handling"}
        )
        
        # Wait a bit for async handling
        await asyncio.sleep(1)
        
        print(f"✅ Async error handled: {error_event.id}")
        print(f"   Fix attempted: {error_event.fix_attempted}")
        print(f"   Fix successful: {error_event.fix_successful}")


def main():
    """Run all tests"""
    print("🚀 Error Event Bus Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    test_basic_error_emission()
    test_network_error()
    test_database_error()
    test_error_categorization()
    
    # Test system health
    test_system_health()
    
    # Test async handling
    asyncio.run(test_async_handling())
    
    # Show final summary
    print("\n📊 Final Error Summary:")
    print("=" * 50)
    
    recent_errors = error_event_bus.get_recent_errors(10)
    for error in recent_errors:
        print(f"ID: {error.id}")
        print(f"  Source: {error.source}")
        print(f"  Severity: {error.severity.value}")
        print(f"  Category: {error.category.value}")
        print(f"  Message: {error.error_message}")
        print(f"  Auto-fixable: {error.auto_fixable}")
        print(f"  Fix attempted: {error.fix_attempted}")
        print(f"  Fix successful: {error.fix_successful}")
        print()
    
    print("✅ Error Event Bus test completed!")


if __name__ == "__main__":
    main() 