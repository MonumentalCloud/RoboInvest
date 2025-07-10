#!/usr/bin/env python3
"""
Test script to verify that the enhanced autonomous agent can generate insights.
"""

import asyncio
import json
from agents.enhanced_autonomous_agent import EnhancedAutonomousAgent
from utils.logger import logger

async def test_agent_insights():
    """Test that the agent can generate insights."""
    
    print("🧪 Testing Enhanced Autonomous Agent Insights Generation...")
    
    # Create agent
    agent = EnhancedAutonomousAgent("test_agent", "alpha_hunting")
    
    # Test research objective
    research_objective = "Identify short-term momentum opportunities in the current market"
    
    # Simple context
    context = {
        "symbols": ["SPY", "QQQ"],
        "market_session": "regular_hours",
        "focus_timeframe": "short_term"
    }
    
    print(f"🎯 Research Objective: {research_objective}")
    print(f"📊 Context: {json.dumps(context, indent=2)}")
    
    try:
        # Step 1: Generate hypotheses
        print("\n🔍 Step 1: Generating research hypotheses...")
        hypotheses = await agent._generate_research_hypotheses(research_objective, context)
        print(f"✅ Generated {len(hypotheses)} hypotheses:")
        for i, hypothesis in enumerate(hypotheses, 1):
            print(f"  {i}. {hypothesis}")
        
        # Step 2: Create research plans
        print(f"\n📋 Step 2: Creating research plans...")
        root_id = agent.decision_tree.create_root(
            content=f"Research Objective: {research_objective}",
            data={"objective": research_objective, "context": context or {}}
        )
        hypothesis_nodes = agent.decision_tree.expand_hypotheses(root_id, hypotheses)
        
        research_plans = []
        for hypothesis_id in hypothesis_nodes:
            plan = await agent._create_comprehensive_research_plan(hypothesis_id, context)
            research_plans.extend(plan)
        
        print(f"✅ Created {len(research_plans)} research plans:")
        for i, plan in enumerate(research_plans, 1):
            print(f"  {i}. {plan.get('description', 'No description')} (Tool: {plan.get('tool_name', 'unknown')})")
        
        # Step 3: Execute research plans
        print(f"\n⚡ Step 3: Executing research plans...")
        research_results = await agent._execute_parallel_research_plans(research_plans)
        
        print(f"✅ Executed {len(research_results)} research tasks:")
        for i, result in enumerate(research_results, 1):
            tool = result.get("tool", "unknown")
            confidence = result.get("confidence", 0)
            has_error = bool(result.get("error"))
            print(f"  {i}. Tool: {tool}, Confidence: {confidence:.2f}, Has Error: {has_error}")
            if has_error:
                print(f"     Error: {result.get('error', 'Unknown error')}")
        
        # Step 4: Analyze patterns
        print(f"\n🔍 Step 4: Analyzing research patterns...")
        pattern_analysis = await agent._analyze_research_patterns(research_results)
        
        print(f"✅ Pattern analysis results:")
        print(f"  Patterns found: {len(pattern_analysis.get('patterns', []))}")
        print(f"  Correlations found: {len(pattern_analysis.get('correlations', []))}")
        print(f"  Unique insights found: {len(pattern_analysis.get('unique_insights', []))}")
        
        # Step 5: Generate insights
        print(f"\n💡 Step 5: Generating competitive insights...")
        insights = await agent._generate_competitive_insights(pattern_analysis, research_objective)
        
        print(f"✅ Generated {len(insights)} insights:")
        for i, insight in enumerate(insights, 1):
            print(f"  {i}. {insight.get('insight', 'No insight text')}")
            print(f"     Confidence: {insight.get('confidence', 0):.2f}")
            print(f"     Competitive Edge: {insight.get('competitive_edge', 'None')}")
            print()
        
        # Step 6: Validate insights
        print(f"\n✅ Step 6: Validating insights...")
        validated_insights = await agent._validate_insights(insights, context)
        
        print(f"✅ Validated {len(validated_insights)} insights:")
        for i, insight in enumerate(validated_insights, 1):
            print(f"  {i}. {insight.get('insight', 'No insight text')}")
            print(f"     Validated Confidence: {insight.get('validated_confidence', 0):.2f}")
            print()
        
        # Final result
        print(f"\n🎯 Final Research Results:")
        print(f"📈 Insights generated: {len(validated_insights)}")
        print(f"🔍 Hypotheses explored: {len(hypothesis_nodes)}")
        print(f"📋 Research plans executed: {len(research_plans)}")
        print(f"⚡ Research tasks completed: {len(research_results)}")
        
        if validated_insights:
            print(f"\n💡 Generated Insights:")
            for i, insight in enumerate(validated_insights, 1):
                print(f"  {i}. {insight.get('insight', 'No insight text')}")
                print(f"     Confidence: {insight.get('validated_confidence', 0):.2f}")
                print(f"     Competitive Edge: {insight.get('competitive_edge', 'None')}")
                print()
        else:
            print("❌ No insights generated!")
            
            # Debug: Show what went wrong
            print(f"\n🔍 Debug Information:")
            print(f"  Research results with errors: {sum(1 for r in research_results if r.get('error'))}")
            print(f"  Research results without errors: {sum(1 for r in research_results if not r.get('error'))}")
            
            # Show some sample research results
            print(f"\n📊 Sample Research Results:")
            for i, result in enumerate(research_results[:3], 1):
                print(f"  Result {i}:")
                print(f"    Tool: {result.get('tool', 'unknown')}")
                print(f"    Confidence: {result.get('confidence', 0):.2f}")
                print(f"    Has Error: {bool(result.get('error'))}")
                if result.get('error'):
                    print(f"    Error: {result.get('error')}")
                else:
                    print(f"    Results keys: {list(result.get('results', {}).keys())}")
                print()
        
        return {
            "hypotheses": hypotheses,
            "research_plans": research_plans,
            "research_results": research_results,
            "pattern_analysis": pattern_analysis,
            "insights": insights,
            "validated_insights": validated_insights
        }
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_agent_insights()) 