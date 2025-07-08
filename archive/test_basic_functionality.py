#!/usr/bin/env python3
"""
Basic functionality test for the trading agent system.
Tests core LangGraph functionality without requiring external API keys.
"""

import sys
import os
from typing import Dict, Any

def test_imports():
    """Test that all core dependencies can be imported."""
    try:
        import langgraph
        import openai
        from dotenv import load_dotenv
        print("✅ Core dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_langgraph_basic():
    """Test basic LangGraph graph creation."""
    try:
        from langgraph.graph import StateGraph, END, START
        from typing_extensions import TypedDict
        
        # Define a simple state
        class TestState(TypedDict):
            message: str
            test: str
        
        # Create a simple test graph
        graph = StateGraph(TestState)
        
        # Add a simple test node
        def test_node(state: TestState) -> TestState:
            return {"message": state["message"], "test": "success"}
        
        graph.add_node("test_node", test_node)
        graph.add_edge(START, "test_node")
        graph.add_edge("test_node", END)
        
        # Compile and test
        compiled_graph = graph.compile()
        result = compiled_graph.invoke({"message": "Hello from test!", "test": ""})
        
        if result.get("test") == "success":
            print("✅ LangGraph basic functionality working")
            return True
        else:
            print("❌ LangGraph test failed")
            return False
            
    except Exception as e:
        print(f"❌ LangGraph test error: {e}")
        return False

def test_agent_imports():
    """Test that our agent modules can be imported."""
    try:
        # Add current directory to path to import our modules
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Test importing our agents (without instantiating to avoid API calls)
        from agents.world_monitor import WorldMonitorAgent
        from agents.simple_organic_strategy import SimpleOrganicStrategyAgent
        from agents.rag_playbook import RAGPlaybookAgent
        from agents.trade_executor import TradeExecutorAgent
        from agents.budget_agent import BudgetAgent
        from agents.research_planner import ResearchPlannerAgent
        from agents.action_executor import ActionExecutorAgent
        
        print("✅ All 7 agents imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Agent import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent test error: {e}")
        return False

def test_config_loading():
    """Test that configuration can be loaded."""
    try:
        from core.config import config
        
        # Test basic config attributes exist
        assert hasattr(config, 'symbols_to_watch')
        assert hasattr(config, 'openai_model')
        assert hasattr(config, 'alpaca_base_url')
        
        print("✅ Configuration loading successful")
        return True
        
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def main():
    """Run all basic functionality tests."""
    print("🧪 Running Basic Functionality Tests for Trading Agent System")
    print("=" * 60)
    
    tests = [
        ("Core Dependencies", test_imports),
        ("LangGraph Basic Functionality", test_langgraph_basic),
        ("Agent Module Imports", test_agent_imports),
        ("Configuration Loading", test_config_loading),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Your trading agent system is ready for configuration and deployment.")
        print("\n📋 Next Steps:")
        print("  1. Create a .env file with your API keys")
        print("  2. Run: source trading_venv/bin/activate")
        print("  3. Test with: python main.py (one-shot) or python bot_workflow.py (continuous)")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)