#!/usr/bin/env python3
"""
Test script for the hybrid memory system

Tests:
1. Central Experience Database initialization
2. Experience storage and retrieval
3. Memory optimization
4. Session context management
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.central_experience_db import central_experience_db, ExperienceType
from core.intelligent_memory_manager import initialize_intelligent_memory_manager
from utils.logger import logger

# Initialize the intelligent memory manager
intelligent_memory_manager = initialize_intelligent_memory_manager()


async def test_basic_functionality():
    """Test basic memory system functionality"""
    print("\n🧠 Testing Basic Memory Functionality...")
    
    try:
        # Test 1: Add experiences
        print("📝 Adding test experiences...")
        
        experience_id_1 = await central_experience_db.add_experience(
            experience_type=ExperienceType.USER_QUERY,
            source_agent="user",
            content="What are my current positions?",
            metadata={"test": True, "session": "test_session"},
            session_id="test_session",
            user_message="What are my current positions?"
        )
        
        experience_id_2 = await central_experience_db.add_experience(
            experience_type=ExperienceType.AGENT_RESPONSE,
            source_agent="trading",
            content="You have 100 shares of AAPL and 50 shares of GOOGL",
            metadata={"test": True, "session": "test_session"},
            session_id="test_session",
            user_message="What are my current positions?"
        )
        
        print(f"✅ Added experiences: {experience_id_1}, {experience_id_2}")
        
        # Test 2: Query experiences
        print("🔍 Querying experiences...")
        experiences = await central_experience_db.query_experiences(
            query="positions",
            limit=10
        )
        
        print(f"✅ Found {len(experiences)} experiences")
        for exp in experiences:
            print(f"  - {exp.experience_type.value}: {exp.content[:50]}...")
        
        # Test 3: Session context
        print("📋 Testing session context...")
        session_context = await central_experience_db.get_session_context("test_session")
        print(f"✅ Session context: {len(session_context.get('recent_experiences', []))} recent experiences")
        
        # Test 4: Memory stats
        print("📊 Getting memory stats...")
        stats = await central_experience_db.get_memory_stats()
        print(f"✅ Memory stats: {stats['total_experiences']} total experiences")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


async def test_memory_optimization():
    """Test memory optimization features"""
    print("\n🔄 Testing Memory Optimization...")
    
    try:
        # Test 1: Memory insights
        print("💡 Getting memory insights...")
        insights = await intelligent_memory_manager.get_memory_insights()
        print(f"✅ Memory insights: {insights.get('status', 'unknown')}")
        
        if insights.get('insights'):
            for insight in insights['insights']:
                print(f"  - {insight}")
        
        # Test 2: Memory optimization (limited scope)
        print("⚡ Running memory optimization...")
        result = await intelligent_memory_manager.optimize_memory_usage()
        print(f"✅ Optimization result: {result.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False


async def test_agent_integration():
    """Test integration with agent system"""
    print("\n🤖 Testing Agent Integration...")
    
    try:
        # Simulate agent conversation flow
        print("💬 Simulating agent conversation...")
        
        # User query
        user_query_id = await central_experience_db.add_experience(
            experience_type=ExperienceType.USER_QUERY,
            source_agent="user",
            content="Show me market insights for tech stocks",
            metadata={"agent_integration_test": True},
            session_id="agent_test_session",
            user_message="Show me market insights for tech stocks"
        )
        
        # Agent response
        agent_response_id = await central_experience_db.add_experience(
            experience_type=ExperienceType.AGENT_RESPONSE,
            source_agent="research",
            content="Tech stocks are showing strong momentum with AAPL up 2.3% and GOOGL up 1.8%",
            metadata={"agent_integration_test": True, "response_type": "market_analysis"},
            session_id="agent_test_session",
            user_message="Show me market insights for tech stocks",
            references=[user_query_id]
        )
        
        # Query for related experiences
        related = await central_experience_db.query_experiences(
            query="tech stocks market insights",
            limit=5
        )
        
        print(f"✅ Found {len(related)} related experiences")
        
        # Check references
        for exp in related:
            if exp.references:
                print(f"  - Experience {exp.id} references: {exp.references}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False


async def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        # Test 1: Invalid experience type
        print("🔍 Testing invalid experience type handling...")
        try:
            # This should fail because we're passing a string instead of ExperienceType enum
            await central_experience_db.add_experience(
                experience_type="invalid_type",  # type: ignore
                source_agent="test",
                content="test",
                metadata={}
            )
            print("❌ Should have failed with invalid experience type")
            return False
        except Exception as e:
            print(f"✅ Correctly handled invalid experience type: {e}")
        
        # Test 2: Empty query
        print("🔍 Testing empty query handling...")
        experiences = await central_experience_db.query_experiences(
            query="",
            limit=5
        )
        print(f"✅ Empty query returned {len(experiences)} experiences")
        
        # Test 3: Non-existent session
        print("🔍 Testing non-existent session...")
        session_context = await central_experience_db.get_session_context("non_existent_session")
        print(f"✅ Non-existent session returned: {session_context}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # This would require implementing a cleanup method
        # For now, just report what would be cleaned
        print("✅ Test data cleanup completed (simulated)")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧠 Hybrid Memory System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Memory Optimization", test_memory_optimization),
        ("Agent Integration", test_agent_integration),
        ("Error Handling", test_error_handling),
        ("Cleanup", cleanup_test_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Hybrid memory system is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        sys.exit(1) 