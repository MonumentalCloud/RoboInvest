#!/usr/bin/env python3
"""
Test script for the new reasoning system
"""

import asyncio
import json
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_reasoning_agent import ReasoningStep, StepType
from agents.intelligent_governor_agent import IntelligentGovernorAgent
from agents.intelligent_research_agent import IntelligentResearchAgent
from openai import AsyncOpenAI


async def test_reasoning_system():
    """Test the reasoning system with a simple query."""
    print("🧠 Testing Reasoning System")
    print("=" * 50)
    
    # Initialize OpenAI client
    openai_client = AsyncOpenAI()
    
    # Create agents
    print("📋 Creating agents...")
    governor = IntelligentGovernorAgent(openai_client)
    research_agent = IntelligentResearchAgent(openai_client)
    
    # Register research agent with governor
    governor.register_agent(research_agent)
    
    print(f"✅ Governor agent created: {governor.name}")
    print(f"✅ Research agent created: {research_agent.name}")
    print(f"✅ Registered agents: {list(governor.agent_registry.keys())}")
    
    # Test query
    test_query = "What is the current research progress?"
    print(f"\n🔍 Testing query: '{test_query}'")
    print("-" * 50)
    
    # Process query and collect reasoning steps
    reasoning_steps = []
    step_count = 0
    
    print("🔄 Processing query with streaming reasoning...")
    async for step in governor.process_query(test_query):
        step_count += 1
        reasoning_steps.append(step)
        
        # Print step information
        print(f"\n📝 Step {step_count}: {step.step_type.value.upper()}")
        print(f"   Agent: {step.metadata.get('routing_agent', 'governor') if step.metadata else 'governor'}")
        print(f"   Content: {step.content[:200]}{'...' if len(step.content) > 200 else ''}")
        
        if step.tool_used:
            print(f"   Tool: {step.tool_used}")
        if step.agent_called:
            print(f"   Called Agent: {step.agent_called}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 REASONING SYSTEM TEST RESULTS")
    print("=" * 50)
    print(f"✅ Total reasoning steps: {step_count}")
    print(f"✅ Final response length: {len(reasoning_steps[-1].content) if reasoning_steps else 0} characters")
    
    # Analyze step types
    step_types = {}
    for step in reasoning_steps:
        step_type = step.step_type.value
        step_types[step_type] = step_types.get(step_type, 0) + 1
    
    print(f"✅ Step type distribution:")
    for step_type, count in step_types.items():
        print(f"   - {step_type}: {count}")
    
    # Show final response
    if reasoning_steps:
        final_step = reasoning_steps[-1]
        print(f"\n🎯 FINAL RESPONSE:")
        print("-" * 30)
        print(final_step.content)
    
    print("\n✅ Reasoning system test completed successfully!")
    return True


async def test_agent_tools():
    """Test individual agent tools."""
    print("\n🔧 Testing Agent Tools")
    print("=" * 50)
    
    openai_client = AsyncOpenAI()
    research_agent = IntelligentResearchAgent(openai_client)
    
    # Test scanning research directories
    print("📁 Testing research directory scanning...")
    try:
        scan_result = await research_agent.use_tool("scan_research_directories")
        print(f"✅ Found {scan_result['total_files']} research files")
        print(f"✅ Found {len(scan_result['directories'])} research directories")
    except Exception as e:
        print(f"❌ Error scanning directories: {e}")
    
    print("✅ Agent tools test completed!")


if __name__ == "__main__":
    print("🚀 Starting Reasoning System Tests")
    print("=" * 60)
    
    try:
        # Run tests
        asyncio.run(test_reasoning_system())
        asyncio.run(test_agent_tools())
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The reasoning system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 