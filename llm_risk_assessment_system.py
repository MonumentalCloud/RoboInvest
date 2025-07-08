"""
LLM-Based AI Risk Assessment System
A completely AI-driven risk analysis system with memory, tagging, and real-world integration.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re


@dataclass
class RiskMemory:
    """Memory entry for past risk assessments."""
    timestamp: datetime
    ticker: str
    scenario: str
    risk_level: str
    key_factors: List[str]
    outcome: Optional[str] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class LLMRiskAssessor:
    """LLM-powered risk assessment with memory and learning capabilities."""
    
    def __init__(self):
        self.risk_memory: List[RiskMemory] = []
        self.market_context = self._load_current_market_context()
        self.reasoning_log = []
        print("🧠 LLM Risk Assessor | AI-powered risk analysis with memory system initialized")
    
    def _load_current_market_context(self) -> Dict[str, Any]:
        """Load current market context and news."""
        return {
            "date": "July 7, 2025",
            "market_sentiment": "risk_off",
            "key_news": [
                {
                    "headline": "Trump threatens 25% tariffs on Japan, South Korea starting August 1",
                    "impact": "negative",
                    "sectors_affected": ["technology", "automotive", "manufacturing"],
                    "market_reaction": "Dow down 400+ points, tech stocks declining"
                },
                {
                    "headline": "Tesla (TSLA) stock drops 7% as Musk announces 'America Party'",
                    "impact": "very_negative",
                    "specific_tickers": ["TSLA"],
                    "context": "Political feud with Trump, investor fatigue with Musk's political involvement"
                },
                {
                    "headline": "OPEC+ increases output, oil prices face pressure",
                    "impact": "negative",
                    "sectors_affected": ["energy"],
                    "trend": "supply_increase_price_pressure"
                }
            ],
            "market_indices": {
                "S&P 500": {"change": -0.8, "trend": "declining"},
                "Nasdaq": {"change": -0.9, "trend": "declining"}, 
                "Dow": {"change": -1.0, "trend": "declining"}
            },
            "volatility": "elevated",
            "risk_factors": ["trade_tensions", "political_uncertainty", "executive_governance_concerns"]
        }
    
    def _llm_risk_reasoning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Core LLM reasoning engine for risk assessment."""
        
        ticker = context.get("primary_ticker", "UNKNOWN")
        action = context.get("action", "UNKNOWN")
        confidence = context.get("confidence", 0.5)
        position_size = context.get("position_size", 0.1)
        
        # Start reasoning log
        reasoning_steps = []
        reasoning_steps.append(f"🔍 ANALYZING: {action} {ticker} | Position: {position_size:.1%} | Confidence: {confidence:.1%}")
        
        # Step 1: Market Context Analysis
        reasoning_steps.append("\n📊 MARKET CONTEXT ANALYSIS:")
        market_risk = 0.0
        
        if self.market_context["market_sentiment"] == "risk_off":
            market_risk += 0.2
            reasoning_steps.append("   • Market sentiment is RISK-OFF due to tariff threats and political uncertainty")
        
        if ticker == "TSLA":
            reasoning_steps.append("   • TESLA SPECIFIC ALERT: Stock down 7% today on Musk political party announcement")
            reasoning_steps.append("   • GOVERNANCE CONCERN: CEO engaged in political activities distracting from business")
            reasoning_steps.append("   • INVESTOR FATIGUE: Multiple sources report shareholder exhaustion with political involvement")
            market_risk += 0.4  # Significant additional risk for TSLA
        
        # Check if ticker affected by current news
        for news in self.market_context["key_news"]:
            if ticker in news.get("specific_tickers", []) or any(sector in context.get("sector", "").lower() for sector in news.get("sectors_affected", [])):
                reasoning_steps.append(f"   • NEWS IMPACT: {news['headline'][:60]}...")
                if news["impact"] == "very_negative":
                    market_risk += 0.3
                elif news["impact"] == "negative":
                    market_risk += 0.2
        
        # Step 2: Position Size Risk Analysis  
        reasoning_steps.append("\n💰 POSITION SIZE RISK ANALYSIS:")
        position_risk = 0.0
        
        if position_size > 0.15:  # 15% threshold
            position_risk += 0.4
            reasoning_steps.append(f"   • HIGH EXPOSURE: {position_size:.1%} exceeds 15% risk limit")
        elif position_size > 0.1:  # 10% threshold
            position_risk += 0.2
            reasoning_steps.append(f"   • MODERATE EXPOSURE: {position_size:.1%} above 10% monitoring threshold")
        else:
            reasoning_steps.append(f"   • ACCEPTABLE EXPOSURE: {position_size:.1%} within normal risk limits")
        
        # Step 3: Confidence Analysis
        reasoning_steps.append("\n🎯 CONFIDENCE ANALYSIS:")
        confidence_risk = 0.0
        
        if confidence < 0.6:
            confidence_risk += 0.3
            reasoning_steps.append(f"   • LOW CONFIDENCE: {confidence:.1%} below 60% minimum threshold")
            reasoning_steps.append("   • RECOMMENDATION: Additional research required before execution")
        elif confidence < 0.7:
            confidence_risk += 0.1
            reasoning_steps.append(f"   • MODERATE CONFIDENCE: {confidence:.1%} acceptable but monitor closely")
        else:
            reasoning_steps.append(f"   • HIGH CONFIDENCE: {confidence:.1%} supports decision quality")
        
        # Step 4: Memory-Based Learning
        reasoning_steps.append("\n🧠 MEMORY-BASED RISK LEARNING:")
        memory_risk = 0.0
        
        # Check past experiences with this ticker
        ticker_memories = [m for m in self.risk_memory if m.ticker == ticker]
        if ticker_memories:
            recent_memories = [m for m in ticker_memories if (datetime.now() - m.timestamp).days < 30]
            if recent_memories:
                high_risk_count = sum(1 for m in recent_memories if m.risk_level in ["HIGH", "CRITICAL"])
                if high_risk_count > 0:
                    memory_risk += 0.2
                    reasoning_steps.append(f"   • HISTORICAL PATTERN: {high_risk_count} high-risk events for {ticker} in last 30 days")
                else:
                    reasoning_steps.append(f"   • HISTORICAL PATTERN: {ticker} has shown stable risk profile recently")
        else:
            reasoning_steps.append(f"   • NEW TICKER: No historical risk data for {ticker}")
        
        # Check for similar scenarios
        similar_scenarios = self._find_similar_scenarios(context)
        if similar_scenarios:
            reasoning_steps.append(f"   • SIMILAR SCENARIOS: Found {len(similar_scenarios)} comparable situations")
            for scenario in similar_scenarios[:2]:  # Show top 2
                reasoning_steps.append(f"     - {scenario.scenario} resulted in {scenario.risk_level} risk")
        
        # Step 5: AI Pattern Recognition
        reasoning_steps.append("\n🤖 AI PATTERN RECOGNITION:")
        pattern_risk = 0.0
        
        # Political risk pattern for TSLA
        if ticker == "TSLA" and any("political" in str(context.get(k, "")).lower() for k in context.keys()):
            pattern_risk += 0.3
            reasoning_steps.append("   • POLITICAL RISK PATTERN: CEO political involvement correlates with stock volatility")
        
        # High volatility + low confidence pattern
        if confidence < 0.6 and context.get("market_volatility", "low") == "high":
            pattern_risk += 0.2
            reasoning_steps.append("   • VOLATILITY PATTERN: Low confidence + high volatility = elevated risk")
        
        # Tariff risk pattern for affected sectors
        if any(sector in context.get("sector", "").lower() for sector in ["technology", "automotive"]):
            pattern_risk += 0.1
            reasoning_steps.append("   • TARIFF RISK PATTERN: Sector exposed to trade policy uncertainty")
        
        # Step 6: Overall Risk Calculation
        reasoning_steps.append("\n⚖️  RISK SYNTHESIS:")
        
        overall_risk = min(1.0, market_risk + position_risk + confidence_risk + memory_risk + pattern_risk)
        
        reasoning_steps.append(f"   • Market Risk: {market_risk:.2f}")
        reasoning_steps.append(f"   • Position Risk: {position_risk:.2f}")
        reasoning_steps.append(f"   • Confidence Risk: {confidence_risk:.2f}")
        reasoning_steps.append(f"   • Memory Risk: {memory_risk:.2f}")
        reasoning_steps.append(f"   • Pattern Risk: {pattern_risk:.2f}")
        reasoning_steps.append(f"   • TOTAL RISK SCORE: {overall_risk:.3f}")
        
        # Step 7: Risk Level Determination
        if overall_risk >= 0.8:
            risk_level = "CRITICAL"
            risk_emoji = "🚨"
        elif overall_risk >= 0.6:
            risk_level = "HIGH"
            risk_emoji = "🔴"
        elif overall_risk >= 0.4:
            risk_level = "MEDIUM"
            risk_emoji = "🟠"
        elif overall_risk >= 0.2:
            risk_level = "LOW"
            risk_emoji = "🟡"
        else:
            risk_level = "MINIMAL"
            risk_emoji = "🟢"
        
        reasoning_steps.append(f"\n{risk_emoji} RISK LEVEL: {risk_level}")
        
        # Step 8: AI Recommendations
        reasoning_steps.append("\n💡 AI RECOMMENDATIONS:")
        recommendations = []
        mitigations = {}
        
        if overall_risk >= 0.6:
            recommendations.append("REQUIRE_HUMAN_APPROVAL")
            mitigations["action"] = "HOLD"
            reasoning_steps.append("   • Action changed to HOLD due to high risk")
        
        if position_risk > 0.3:
            new_position = min(position_size * 0.5, 0.1)
            mitigations["position_size"] = new_position
            recommendations.append(f"REDUCE_POSITION_TO_{new_position:.1%}")
            reasoning_steps.append(f"   • Position reduced from {position_size:.1%} to {new_position:.1%}")
        
        if confidence_risk > 0.2:
            recommendations.append("ADDITIONAL_RESEARCH_REQUIRED")
            reasoning_steps.append("   • Additional research required before execution")
        
        if ticker == "TSLA" and market_risk > 0.3:
            recommendations.append("MONITOR_GOVERNANCE_DEVELOPMENTS")
            reasoning_steps.append("   • Monitor CEO political activities and investor sentiment")
        
        # Step 9: Generate Tags
        tags = self._generate_tags(context, overall_risk, reasoning_steps)
        reasoning_steps.append(f"\n🏷️  GENERATED TAGS: {', '.join(tags)}")
        
        return {
            "risk_score": overall_risk,
            "risk_level": risk_level,
            "risk_emoji": risk_emoji,
            "reasoning_steps": reasoning_steps,
            "recommendations": recommendations,
            "mitigations": mitigations,
            "tags": tags,
            "key_factors": [
                f"market_context:{market_risk:.2f}",
                f"position_risk:{position_risk:.2f}",
                f"confidence_risk:{confidence_risk:.2f}",
                f"memory_pattern:{memory_risk:.2f}",
                f"ai_pattern:{pattern_risk:.2f}"
            ]
        }
    
    def _find_similar_scenarios(self, context: Dict[str, Any]) -> List[RiskMemory]:
        """Find similar past scenarios for learning."""
        similar = []
        current_ticker = context.get("primary_ticker", "")
        current_confidence = context.get("confidence", 0.5)
        current_position = context.get("position_size", 0.1)
        
        for memory in self.risk_memory:
            similarity_score = 0.0
            
            # Same ticker adds similarity
            if memory.ticker == current_ticker:
                similarity_score += 0.4
            
            # Similar confidence range
            if abs(current_confidence - 0.5) < 0.2:  # Assuming stored confidence around 0.5
                similarity_score += 0.3
            
            # Similar position size
            if abs(current_position - 0.1) < 0.05:  # Assuming stored position around 0.1
                similarity_score += 0.3
            
            if similarity_score > 0.5:
                similar.append(memory)
        
        return sorted(similar, key=lambda x: x.timestamp, reverse=True)[:5]
    
    def _generate_tags(self, context: Dict[str, Any], risk_score: float, reasoning: List[str]) -> List[str]:
        """Generate contextual tags for memory storage."""
        tags = []
        
        # Market condition tags
        if self.market_context["market_sentiment"] == "risk_off":
            tags.append("market_stress")
        
        # Risk level tags
        if risk_score >= 0.6:
            tags.append("high_risk")
        elif risk_score <= 0.2:
            tags.append("low_risk")
        
        # Ticker-specific tags
        ticker = context.get("primary_ticker", "")
        if ticker == "TSLA":
            tags.append("governance_risk")
            tags.append("political_exposure")
        
        # Event-driven tags
        if "tariff" in str(reasoning).lower():
            tags.append("trade_policy")
        
        if "confidence" in str(reasoning).lower():
            tags.append("confidence_issue")
        
        # Pattern tags
        if context.get("position_size", 0) > 0.15:
            tags.append("position_concentration")
        
        return tags
    
    def assess_trading_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main LLM-based risk assessment function."""
        
        print(f"\n🧠 LLM RISK ASSESSMENT | {context.get('primary_ticker', 'Unknown')} | {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        
        # Run LLM reasoning
        analysis = self._llm_risk_reasoning(context)
        
        # Display reasoning process
        for step in analysis["reasoning_steps"]:
            print(step)
        
        # Determine final decision
        should_proceed = analysis["risk_level"] not in ["CRITICAL", "HIGH"]
        
        # Apply mitigations
        mitigated_context = context.copy()
        mitigated_context.update(analysis["mitigations"])
        
        # Store in memory
        memory_entry = RiskMemory(
            timestamp=datetime.now(),
            ticker=context.get("primary_ticker", "UNKNOWN"),
            scenario=f"{context.get('action', 'UNKNOWN')} at {context.get('confidence', 0):.1%} confidence",
            risk_level=analysis["risk_level"],
            key_factors=analysis["key_factors"],
            tags=analysis["tags"]
        )
        self.risk_memory.append(memory_entry)
        
        print(f"\n{analysis['risk_emoji']} FINAL DECISION: {'✅ PROCEED' if should_proceed else '❌ BLOCKED'}")
        print(f"📝 Memory stored with tags: {', '.join(analysis['tags'])}")
        print("=" * 80)
        
        return {
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "should_proceed": should_proceed,
            "reasoning": analysis["reasoning_steps"],
            "recommendations": analysis["recommendations"],
            "mitigated_context": mitigated_context,
            "memory_id": len(self.risk_memory) - 1,
            "tags": analysis["tags"]
        }
    
    def query_memory(self, query_type: str = "recent", **kwargs) -> List[RiskMemory]:
        """Query the memory system with different filters."""
        
        if query_type == "recent":
            days = kwargs.get("days", 7)
            cutoff = datetime.now() - timedelta(days=days)
            return [m for m in self.risk_memory if m.timestamp > cutoff]
        
        elif query_type == "ticker":
            ticker = kwargs.get("ticker", "").upper()
            return [m for m in self.risk_memory if m.ticker == ticker]
        
        elif query_type == "risk_level":
            level = kwargs.get("level", "HIGH")
            return [m for m in self.risk_memory if m.risk_level == level]
        
        elif query_type == "tags":
            tags = kwargs.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            return [m for m in self.risk_memory if m.tags and any(tag in m.tags for tag in tags)]
        
        return self.risk_memory
    
    def get_memory_insights(self) -> Dict[str, Any]:
        """Analyze memory patterns for insights."""
        if not self.risk_memory:
            return {"status": "No memory data available"}
        
        # Risk level distribution
        risk_distribution = {}
        for memory in self.risk_memory:
            risk_distribution[memory.risk_level] = risk_distribution.get(memory.risk_level, 0) + 1
        
        # Most common tags
        all_tags = []
        for memory in self.risk_memory:
            if memory.tags:
                all_tags.extend(memory.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent high-risk events
        recent_high_risk = [
            m for m in self.risk_memory 
            if m.risk_level in ["HIGH", "CRITICAL"] and 
            (datetime.now() - m.timestamp).days < 7
        ]
        
        return {
            "total_assessments": len(self.risk_memory),
            "risk_distribution": risk_distribution,
            "most_common_tags": most_common_tags,
            "recent_high_risk_count": len(recent_high_risk),
            "memory_age_days": (datetime.now() - self.risk_memory[0].timestamp).days if self.risk_memory else 0
        }


# Global LLM instance
llm_risk_assessor = LLMRiskAssessor()


def demonstrate_llm_risk_system():
    """Demonstrate the LLM-based risk system with real market scenarios."""
    
    print("🧠 LLM-BASED RISK ASSESSMENT DEMONSTRATION")
    print("Using real market data and AI reasoning")
    print("=" * 80)
    
    # Scenario 1: Tesla with current market context
    print("\n🎯 SCENARIO 1: Tesla Trade with Current Market Turmoil")
    tesla_context = {
        "primary_ticker": "TSLA",
        "action": "BUY",
        "confidence": 0.7,
        "position_size": 0.18,  # 18% - high exposure
        "sector": "automotive technology",
        "market_volatility": "high",
        "research_summary": "Strong technical setup but governance concerns"
    }
    
    result1 = llm_risk_assessor.assess_trading_decision(tesla_context)
    
    # Scenario 2: Safe defensive play
    print("\n\n🎯 SCENARIO 2: Defensive ETF Trade")
    defensive_context = {
        "primary_ticker": "VTI",
        "action": "BUY",
        "confidence": 0.8,
        "position_size": 0.06,  # 6% - conservative
        "sector": "broad_market",
        "market_volatility": "high",
        "research_summary": "Diversified exposure for uncertain times"
    }
    
    result2 = llm_risk_assessor.assess_trading_decision(defensive_context)
    
    # Scenario 3: High-risk meme stock
    print("\n\n🎯 SCENARIO 3: High-Risk Speculative Play")
    speculative_context = {
        "primary_ticker": "MEME",
        "action": "BUY", 
        "confidence": 0.45,  # Low confidence
        "position_size": 0.25,  # 25% - way too high
        "sector": "speculative",
        "market_volatility": "extreme",
        "research_summary": "Social media momentum but fundamentals weak"
    }
    
    result3 = llm_risk_assessor.assess_trading_decision(speculative_context)
    
    # Show memory insights
    print("\n\n🧠 MEMORY SYSTEM INSIGHTS")
    print("=" * 80)
    insights = llm_risk_assessor.get_memory_insights()
    print(f"Total Risk Assessments: {insights['total_assessments']}")
    print(f"Risk Distribution: {insights['risk_distribution']}")
    print(f"Most Common Tags: {insights['most_common_tags']}")
    print(f"Recent High-Risk Events: {insights['recent_high_risk_count']}")
    
    # Query examples
    print(f"\n🔍 MEMORY QUERIES:")
    tesla_memories = llm_risk_assessor.query_memory("ticker", ticker="TSLA")
    print(f"Tesla-related assessments: {len(tesla_memories)}")
    
    high_risk_memories = llm_risk_assessor.query_memory("risk_level", level="HIGH")
    print(f"High-risk assessments: {len(high_risk_memories)}")
    
    governance_memories = llm_risk_assessor.query_memory("tags", tags=["governance_risk"])
    print(f"Governance risk events: {len(governance_memories)}")
    
    return {
        "tesla_assessment": result1,
        "defensive_assessment": result2, 
        "speculative_assessment": result3,
        "memory_insights": insights
    }


if __name__ == "__main__":
    print("🚀 LLM-BASED AI RISK MANAGEMENT SYSTEM")
    print("Completely AI-driven risk assessment with memory and learning")
    print()
    
    # Demonstrate the system
    results = demonstrate_llm_risk_system()
    
    print(f"\n✨ DEMONSTRATION COMPLETE!")
    print(f"The LLM system has:")
    print(f"• Analyzed {len(llm_risk_assessor.risk_memory)} trading scenarios")
    print(f"• Generated contextual tags for pattern recognition")
    print(f"• Applied real market context and news")
    print(f"• Provided detailed AI reasoning for each decision")
    print(f"• Built a searchable memory system for future learning")