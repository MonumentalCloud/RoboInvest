#!/usr/bin/env python3
"""
Test script to demonstrate the testing environment functionality.
"""

import os
import asyncio
from pathlib import Path

# Set testing mode
os.environ["TESTING_MODE"] = "true"

from agents.enhanced_meta_agent import enhanced_meta_agent, ImprovementType, ImprovementPriority
from agents.specialized_meta_agents import CodeEditorAgent, SystemArchitectAgent
from core.config import config

async def test_testing_environment():
    """Test the testing environment functionality."""
    print("🧪 Testing Environment Demo")
    print(f"Testing Mode: {config.testing_mode}")
    print(f"Agents Directory: {config.agents_dir}")
    print(f"Data Directory: {config.data_dir}")
    print(f"ChromaDB Path: {config.chroma_db_path}")
    
    # Create test directories
    Path(config.agents_dir).mkdir(exist_ok=True)
    Path(config.data_dir).mkdir(exist_ok=True)
    
    print("\n1. Testing improvement creation in testing mode...")
    
    # Create a test improvement (should be auto-approved in testing mode)
    await enhanced_meta_agent._create_improvement_suggestion(
        improvement_type=ImprovementType.PERFORMANCE,
        priority=ImprovementPriority.HIGH,
        title="Test Performance Optimization",
        description="This is a test improvement to verify testing mode works",
        affected_components=["test_agent_1", "test_agent_2"],
        estimated_impact={"performance": "high", "risk": "low"},
        implementation_plan={"steps": ["step1", "step2", "step3"]},
        confidence=0.9
    )
    
    print("✅ Test improvement created and auto-approved in testing mode")
    
    print("\n2. Testing agent creation in testing mode...")
    
    # Test creating a new agent in testing mode
    system_architect = SystemArchitectAgent()
    test_decision = {
        "type": "create_agent",
        "description": "Create a test agent for testing environment",
        "capabilities": ["test_capability_1", "test_capability_2"],
        "priority": "medium"
    }
    
    await system_architect.create_new_agent(test_decision)
    
    print("✅ Test agent creation completed in testing mode")
    
    print("\n3. Checking test environment files...")
    
    # List files in test directories
    test_agents = list(Path(config.agents_dir).glob("*.py"))
    print(f"Test agents created: {[f.name for f in test_agents]}")
    
    print("\n4. Testing code editing in testing mode...")
    
    # Test code editing in testing mode
    code_editor = CodeEditorAgent()
    test_analysis = await code_editor.analyze_system_code()
    print(f"System analysis completed: {test_analysis.get('total_files', 0)} files analyzed")
    
    print("\n✅ Testing environment demo completed successfully!")
    print("All operations were performed in the test environment without affecting production.")

if __name__ == "__main__":
    asyncio.run(test_testing_environment()) 