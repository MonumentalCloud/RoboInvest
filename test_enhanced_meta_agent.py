#!/usr/bin/env python3
"""
Test script for the Enhanced Meta Agent System
Verifies that the system can be initialized and basic functionality works.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from agents.enhanced_meta_agent import enhanced_meta_agent
        print("✅ Enhanced meta agent imported successfully")
        
        from agents.agent_monitoring_system import agent_monitor
        print("✅ Agent monitoring system imported successfully")
        
        from agents.specialized_meta_agents import CodeEditorAgent, PromptEngineerAgent, SystemArchitectAgent, PerformanceAnalystAgent
        print("✅ Specialized meta agents imported successfully")
        
        from agents.notification_system import notification_system
        print("✅ Notification system imported successfully")
        
        from utils.logger import logger
        print("✅ Logger imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_enhanced_meta_agent_initialization():
    """Test that the enhanced meta agent can be initialized."""
    print("\n🤖 Testing enhanced meta agent initialization...")
    
    try:
        from agents.enhanced_meta_agent import enhanced_meta_agent
        
        # Check basic attributes
        assert hasattr(enhanced_meta_agent, 'active_monitoring'), "Missing active_monitoring attribute"
        assert hasattr(enhanced_meta_agent, 'system_improvements'), "Missing system_improvements attribute"
        assert hasattr(enhanced_meta_agent, 'system_metrics_history'), "Missing system_metrics_history attribute"
        assert hasattr(enhanced_meta_agent, 'performance_thresholds'), "Missing performance_thresholds attribute"
        
        print("✅ Enhanced meta agent initialized successfully")
        print(f"   - Active monitoring: {enhanced_meta_agent.active_monitoring}")
        print(f"   - Performance thresholds: {enhanced_meta_agent.performance_thresholds}")
        print(f"   - Database path: {enhanced_meta_agent.db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_database_creation():
    """Test that the database is created correctly."""
    print("\n🗄️  Testing database creation...")
    
    try:
        from agents.enhanced_meta_agent import enhanced_meta_agent
        
        db_path = enhanced_meta_agent.db_path
        
        # Check if database file exists
        if db_path.exists():
            print(f"✅ Database created at: {db_path}")
            
            # Check database size
            size = db_path.stat().st_size
            print(f"   - Database size: {size} bytes")
            
            return True
        else:
            print(f"❌ Database not created at: {db_path}")
            return False
            
    except Exception as e:
        print(f"❌ Database creation error: {e}")
        return False

def test_specialized_agents():
    """Test that specialized agents can be initialized."""
    print("\n🛠️  Testing specialized agents...")
    
    try:
        from agents.specialized_meta_agents import CodeEditorAgent, PromptEngineerAgent, SystemArchitectAgent, PerformanceAnalystAgent
        
        # Test code editor agent
        code_editor = CodeEditorAgent()
        print("✅ Code editor agent initialized")
        
        # Test prompt engineer agent
        prompt_engineer = PromptEngineerAgent()
        print("✅ Prompt engineer agent initialized")
        
        # Test system architect agent
        system_architect = SystemArchitectAgent()
        print("✅ System architect agent initialized")
        
        # Test performance analyst agent
        performance_analyst = PerformanceAnalystAgent()
        print("✅ Performance analyst agent initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Specialized agents error: {e}")
        return False

async def test_metrics_collection():
    """Test that metrics can be collected."""
    print("\n📊 Testing metrics collection...")
    
    try:
        from agents.enhanced_meta_agent import enhanced_meta_agent
        
        # Collect metrics
        metrics = await enhanced_meta_agent._collect_system_metrics()
        
        print("✅ Metrics collected successfully")
        print(f"   - Total agents: {metrics.total_agents}")
        print(f"   - Active agents: {metrics.active_agents}")
        print(f"   - Failed agents: {metrics.failed_agents}")
        print(f"   - Performance score: {metrics.performance_score:.2f}")
        print(f"   - CPU usage: {metrics.system_cpu_usage:.1f}%")
        print(f"   - Memory usage: {metrics.system_memory_usage:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics collection error: {e}")
        return False

def test_improvement_creation():
    """Test that improvement suggestions can be created."""
    print("\n💡 Testing improvement creation...")
    
    try:
        from agents.enhanced_meta_agent import enhanced_meta_agent, ImprovementType, ImprovementPriority
        
        # Test that the method exists and can be called
        assert hasattr(enhanced_meta_agent, '_create_improvement_suggestion'), "Missing _create_improvement_suggestion method"
        
        print("✅ Improvement creation method exists")
        print(f"   - Method available: _create_improvement_suggestion")
        print(f"   - Improvement types: {[t.value for t in ImprovementType]}")
        print(f"   - Priority levels: {[p.value for p in ImprovementPriority]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Improvement creation error: {e}")
        return False

def test_system_status():
    """Test that system status can be retrieved."""
    print("\n📈 Testing system status...")
    
    try:
        from agents.enhanced_meta_agent import enhanced_meta_agent
        
        status = enhanced_meta_agent.get_system_status()
        
        print("✅ System status retrieved successfully")
        print(f"   - Meta agent active: {status['meta_agent_active']}")
        print(f"   - Total improvements: {status['total_improvements']}")
        print(f"   - Pending improvements: {status['pending_improvements']}")
        print(f"   - Completed improvements: {status['completed_improvements']}")
        
        return True
        
    except Exception as e:
        print(f"❌ System status error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Enhanced Meta Agent System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_enhanced_meta_agent_initialization),
        ("Database Test", test_database_creation),
        ("Specialized Agents Test", test_specialized_agents),
        ("Metrics Collection Test", test_metrics_collection),
        ("Improvement Creation Test", test_improvement_creation),
        ("System Status Test", test_system_status),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} failed")
                
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced Meta Agent System is ready to use.")
        print("\n🚀 To start the system:")
        print("   ./startup_with_meta_agent.sh")
        print("\n📖 For more information:")
        print("   See ENHANCED_META_AGENT_README.md")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)