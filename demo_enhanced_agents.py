#!/usr/bin/env python3
"""
Demo: Enhanced Autonomous Agents
Demonstration of the enhanced multi-agent system with parallel execution and decision trees.
"""

import asyncio
import json
from datetime import datetime

from enhanced_trading_system import enhanced_trading_system
from agents.parallel_execution_system import execution_engine
from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
from utils.logger import logger  # type: ignore

async def demo_enhanced_agent_capabilities():
    """Demo individual enhanced agent capabilities."""
    
    print("\n" + "="*60)
    print("ENHANCED AUTONOMOUS AGENT DEMO")
    print("="*60)
    
    # Create a single enhanced agent for demo
    demo_agent = EnhancedAutonomousAgent("demo_agent", "alpha_hunting")
    
    print(f"\n1. Agent Initialization:")
    print(f"   Agent ID: {demo_agent.id}")
    print(f"   Specialization: {demo_agent.specialization}")
    print(f"   Available Tools: {list(demo_agent.tools.keys())}")
    print(f"   Capabilities: {demo_agent.tools['calculator']['capabilities'][:3]}...")
    
    # Demo autonomous research cycle
    print(f"\n2. Autonomous Research Cycle:")
    research_objective = "Identify momentum opportunities in current market conditions"
    
    print(f"   Research Objective: {research_objective}")
    print(f"   Starting research cycle...")
    
    research_result = await demo_agent.autonomous_research_cycle(
        research_objective=research_objective,
        context={"symbols": ["SPY", "QQQ"], "focus": "short-term momentum"}
    )
    
    if research_result.get("error"):
        print(f"   ❌ Research failed: {research_result['error']}")
    else:
        print(f"   ✅ Research completed successfully!")
        print(f"   Hypotheses explored: {research_result.get('hypotheses_explored', 0)}")
        print(f"   Research plans executed: {research_result.get('research_plans_executed', 0)}")
        print(f"   Insights generated: {research_result.get('insights_generated', 0)}")
    
    # Demo decision tree
    print(f"\n3. Decision Tree Analysis:")
    tree_summary = demo_agent.decision_tree.get_summary()
    print(f"   Tree ID: {tree_summary['tree_id']}")
    print(f"   Total nodes: {tree_summary['total_nodes']}")
    print(f"   Node types: {tree_summary['by_type']}")
    print(f"   Best confidence: {tree_summary['best_confidence']:.3f}")
    
    return research_result

async def demo_parallel_execution():
    """Demo parallel execution system."""
    
    print("\n" + "="*60)
    print("PARALLEL EXECUTION SYSTEM DEMO")
    print("="*60)
    
    print(f"\n1. System Status:")
    system_status = execution_engine.get_system_status()
    print(f"   Active agents: {system_status['execution_engine']['active_agents']}")
    print(f"   Agent specializations: {list(execution_engine.agents.keys())[:3]}...")
    
    print(f"\n2. Parallel Mission Execution:")
    mission_objective = "Analyze market sentiment and technical patterns for alpha opportunities"
    
    print(f"   Mission: {mission_objective}")
    print(f"   Launching parallel agents...")
    
    try:
        mission_result = await execution_engine.execute_parallel_research_mission(
            mission_objective=mission_objective,
            context={"symbols": ["SPY", "QQQ", "IWM"], "timeframe": "short-term"}
        )
        
        if mission_result.get("error"):
            print(f"   ❌ Mission failed: {mission_result['error']}")
        else:
            print(f"   ✅ Mission completed!")
            stats = mission_result.get("stats", {})
            print(f"   Successful agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)}")
            print(f"   Total insights: {stats.get('total_insights', 0)}")
            
            # Show agent results summary
            agent_results = mission_result.get("agent_results", {})
            print(f"\n   Agent Results Summary:")
            for agent_id, result in list(agent_results.items())[:3]:  # Show first 3
                if hasattr(result, 'status') and hasattr(result, 'result'):
                    status = "✅" if result.status.value == "completed" else "❌"
                    insights_count = len(result.result.get("insights", [])) if result.result else 0
                    print(f"     {status} {agent_id}: {insights_count} insights")
        
        return mission_result
        
    except Exception as e:
        print(f"   ❌ Mission execution error: {e}")
        return {"error": str(e)}

async def demo_full_alpha_hunt():
    """Demo full alpha hunting system."""
    
    print("\n" + "="*60)
    print("FULL ALPHA HUNTING SYSTEM DEMO")
    print("="*60)
    
    print(f"\n1. System Initialization:")
    init_result = enhanced_trading_system.initialize_system()
    if init_result["status"] == "success":
        print(f"   ✅ System initialized successfully")
        print(f"   Enhanced agents: {init_result['execution_engine']['active_agents']}")
        print(f"   Orchestrator agents: {init_result['orchestrator']['total_agents']}")
    else:
        print(f"   ❌ Initialization failed: {init_result.get('error')}")
        return init_result
    
    print(f"\n2. Alpha Hunt Execution:")
    print(f"   Focus areas: Technology sector, Interest rate opportunities")
    print(f"   Priority: High")
    print(f"   Starting comprehensive alpha hunt...")
    
    alpha_hunt_result = await enhanced_trading_system.hunt_for_alpha(
        focus_areas=["technology sector momentum", "interest rate arbitrage opportunities"],
        priority="high"
    )
    
    if alpha_hunt_result.get("error"):
        print(f"   ❌ Alpha hunt failed: {alpha_hunt_result['error']}")
        return alpha_hunt_result
    
    print(f"   ✅ Alpha hunt completed!")
    
    # Show results summary
    opportunities = alpha_hunt_result.get("alpha_opportunities", [])
    performance = alpha_hunt_result.get("system_performance", {})
    
    print(f"\n3. Results Summary:")
    print(f"   Alpha opportunities identified: {len(opportunities)}")
    print(f"   Successful missions: {performance.get('successful_missions', 0)}")
    print(f"   Total insights generated: {performance.get('total_insights_generated', 0)}")
    print(f"   System efficiency: {performance.get('system_efficiency', 0):.3f} insights/second")
    
    # Show top opportunities
    if opportunities:
        print(f"\n4. Top Alpha Opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):  # Top 3
            print(f"   {i}. {opp['description']}")
            print(f"      Confidence: {opp['confidence']:.2f}")
            print(f"      Risk Level: {opp['risk_level']}")
            print(f"      Timing: {opp['timing']}")
    
    return alpha_hunt_result

async def demo_system_status():
    """Demo system status and monitoring."""
    
    print("\n" + "="*60)
    print("SYSTEM STATUS & MONITORING")
    print("="*60)
    
    # Get comprehensive system status
    system_status = enhanced_trading_system.get_system_status()
    
    print(f"\n1. Overall System Status:")
    print(f"   System initialized: {system_status['system_initialized']}")
    print(f"   Session count: {system_status['session_count']}")
    print(f"   Alpha opportunities tracked: {system_status['alpha_opportunities_tracked']}")
    
    print(f"\n2. Execution Engine Status:")
    engine_status = system_status['execution_engine_status']['execution_engine']
    print(f"   Active agents: {engine_status['active_agents']}")
    print(f"   Running tasks: {engine_status['running_tasks']}")
    print(f"   Queued tasks: {engine_status['queued_tasks']}")
    
    print(f"\n3. Resource Pool Status:")
    resource_status = system_status['execution_engine_status']['resource_pool']
    print(f"   Active tasks: {resource_status['active_tasks']}/{resource_status['max_concurrent']}")
    print(f"   API calls used: {resource_status['api_calls_used']}")
    print(f"   Memory usage: {resource_status['memory_usage']:.1%}")
    
    print(f"\n4. Recent Performance:")
    recent_perf = system_status['recent_performance']
    if recent_perf.get('note'):
        print(f"   {recent_perf['note']}")
    else:
        print(f"   Recent sessions: {recent_perf['recent_sessions']}")
        print(f"   Opportunities identified: {recent_perf['total_opportunities_identified']}")
        print(f"   Avg confidence: {recent_perf['avg_opportunity_confidence']:.3f}")
    
    return system_status

async def main():
    """Run all demos."""
    
    print("🤖 ENHANCED AUTONOMOUS AGENTS DEMONSTRATION")
    print("Showcasing next-generation AI agents with parallel execution and decision trees")
    
    try:
        # Demo 1: Individual agent capabilities
        await demo_enhanced_agent_capabilities()
        
        # Demo 2: Parallel execution system
        await demo_parallel_execution()
        
        # Demo 3: Full alpha hunting system
        await demo_full_alpha_hunt()
        
        # Demo 4: System monitoring
        await demo_system_status()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("✅ Autonomous agent research cycles")
        print("✅ Dynamic decision tree expansion")
        print("✅ Parallel multi-agent coordination")
        print("✅ Full tool integration (web research, data analysis, backtesting)")
        print("✅ Intelligent insight synthesis")
        print("✅ Real-time alpha opportunity hunting")
        print("✅ Performance monitoring and optimization")
        
        print(f"\nTimestamp: {datetime.now().isoformat()}")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main()) 