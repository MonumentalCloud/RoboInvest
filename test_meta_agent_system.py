#!/usr/bin/env python3
"""
Test script to demonstrate the Meta-Agent System functionality.
"""

import asyncio
import json
from datetime import datetime
from agents.meta_agent_system import meta_agent
from agents.specialized_meta_agents import CodeEditorAgent, PromptEngineerAgent, SystemArchitectAgent, PerformanceAnalystAgent

async def test_meta_agent_system():
    """Test the meta-agent system functionality."""
    
    print("🤖 Testing Meta-Agent System...")
    
    # 1. Register some test agents
    print("\n📝 Registering test agents...")
    await meta_agent.register_agent("enhanced_autonomous_agent", {
        "type": "research",
        "specialization": "alpha_hunting",
        "capabilities": ["market_analysis", "insight_generation"],
        "dependencies": ["data_fetcher", "calculator"]
    })
    
    await meta_agent.register_agent("world_monitor_agent", {
        "type": "monitoring",
        "specialization": "market_monitoring",
        "capabilities": ["data_collection", "sentiment_analysis"],
        "dependencies": ["finnhub_client", "feedparser"]
    })
    
    await meta_agent.register_agent("trade_executor_agent", {
        "type": "execution",
        "specialization": "trade_execution",
        "capabilities": ["order_submission", "position_management"],
        "dependencies": ["alpaca_client"]
    })
    
    # 2. Test health monitoring
    print("\n🔍 Testing health monitoring...")
    await meta_agent._check_all_agent_health()
    
    # 3. Test system status
    print("\n📊 Getting system status...")
    status = meta_agent.get_system_status()
    print(f"System Status: {json.dumps(status, indent=2, default=str)}")
    
    # 4. Test daily report generation
    print("\n📋 Generating daily report...")
    daily_report = await meta_agent._generate_daily_report()
    print(f"Daily Report Summary:")
    print(f"  - Total Agents: {daily_report['system_health']['total_agents']}")
    print(f"  - Healthy Agents: {daily_report['system_health']['healthy_agents']}")
    print(f"  - Health Percentage: {daily_report['system_health']['health_percentage']:.1f}%")
    print(f"  - Critical Alerts: {daily_report['system_health']['critical_alerts']}")
    print(f"  - Total Insights Generated: {daily_report['performance_metrics']['total_insights_generated']}")
    print(f"  - Total Trades Executed: {daily_report['performance_metrics']['total_trades_executed']}")
    
    # 5. Test governance meeting
    print("\n🏛️ Testing governance meeting...")
    governance_decisions = await meta_agent._hold_governance_meeting(daily_report)
    print(f"Governance Decisions: {len(governance_decisions)}")
    for i, decision in enumerate(governance_decisions, 1):
        print(f"  {i}. {decision['description']} (Priority: {decision['priority']})")
    
    # 6. Test specialized meta-agents
    print("\n🔧 Testing specialized meta-agents...")
    
    # Code Editor Agent
    code_editor = CodeEditorAgent()
    code_analysis = await code_editor.analyze_system_code()
    print(f"Code Analysis:")
    print(f"  - Total Files: {code_analysis['total_files']}")
    print(f"  - Total Lines: {code_analysis['total_lines']}")
    print(f"  - Issues Found: {code_analysis['issues_found']}")
    print(f"  - Maintainability Score: {code_analysis['maintainability_score']:.1f}/10")
    
    # Performance Analyst Agent
    performance_analyst = PerformanceAnalystAgent()
    performance_report = await performance_analyst.generate_report()
    print(f"Performance Report:")
    print(f"  - Overall Performance: {performance_report['summary']['overall_performance']}")
    print(f"  - Critical Issues: {performance_report['summary']['critical_issues']}")
    print(f"  - Optimization Opportunities: {performance_report['summary']['optimization_opportunities']}")
    
    # 7. Test alert system
    print("\n🚨 Testing alert system...")
    await meta_agent._create_alert(
        meta_agent.system_alerts[0].priority,
        "test_agent",
        "test_alert",
        "This is a test alert for demonstration purposes",
        "No action required - this is just a test"
    )
    print(f"Active Alerts: {len([a for a in meta_agent.system_alerts if not a.resolved])}")
    
    # 8. Test self-healing
    print("\n🔄 Testing self-healing...")
    await meta_agent._self_healing_loop()
    
    print("\n✅ Meta-Agent System test completed!")
    
    return {
        "system_status": status,
        "daily_report": daily_report,
        "governance_decisions": governance_decisions,
        "code_analysis": code_analysis,
        "performance_report": performance_report
    }

async def test_specialized_agents():
    """Test individual specialized meta-agents."""
    
    print("\n🔧 Testing Specialized Meta-Agents...")
    
    # Test Code Editor Agent
    print("\n📝 Testing CodeEditorAgent...")
    code_editor = CodeEditorAgent()
    
    # Test prompt extraction
    print("  - Testing prompt extraction...")
    prompts = await code_editor._extract_prompts_from_agent("enhanced_autonomous_agent")
    print(f"    Found {len(prompts)} prompts")
    
    # Test Prompt Engineer Agent
    print("\n🔧 Testing PromptEngineerAgent...")
    prompt_engineer = PromptEngineerAgent()
    
    # Test prompt analysis
    print("  - Testing prompt analysis...")
    test_prompt = {
        "text": "Analyze the market data and generate insights",
        "line": 1,
        "pattern": "test"
    }
    prompt_issues = await prompt_engineer._analyze_single_prompt(test_prompt)
    print(f"    Found {len(prompt_issues)} issues in test prompt")
    
    # Test System Architect Agent
    print("\n🏗️ Testing SystemArchitectAgent...")
    system_architect = SystemArchitectAgent()
    
    # Test agent specification generation
    print("  - Testing agent specification generation...")
    test_decision = {
        "decision_type": "new_agent",
        "description": "Create a sentiment analysis agent",
        "priority": "medium",
        "estimated_impact": "medium"
    }
    spec = await system_architect._generate_agent_specification(test_decision)
    print(f"    Generated specification for: {spec.get('name', 'Unknown')}")
    
    # Test Performance Analyst Agent
    print("\n📊 Testing PerformanceAnalystAgent...")
    performance_analyst = PerformanceAnalystAgent()
    
    # Test metrics collection
    print("  - Testing metrics collection...")
    metrics = await performance_analyst._collect_performance_metrics()
    print(f"    Collected metrics for {len(metrics)} categories")
    
    # Test bottleneck identification
    print("  - Testing bottleneck identification...")
    bottlenecks = await performance_analyst._identify_bottlenecks(metrics)
    print(f"    Identified {len(bottlenecks)} bottlenecks")
    
    print("\n✅ Specialized Meta-Agents test completed!")

if __name__ == "__main__":
    print("🚀 Starting Meta-Agent System Tests...")
    
    # Run tests
    asyncio.run(test_meta_agent_system())
    asyncio.run(test_specialized_agents())
    
    print("\n🎉 All Meta-Agent System tests completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Integrate meta-agent system with existing background research service")
    print("2. Register all existing agents with the meta-agent")
    print("3. Enable continuous monitoring and self-healing")
    print("4. Start daily governance meetings")
    print("5. Add meta-agent dashboard to frontend") 