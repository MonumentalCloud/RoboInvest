"""
Web Researcher Tool
Performs sentiment analysis and fundamental research using advanced web intelligence.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger  # type: ignore
from tools.web_intelligence_agent import web_intelligence_agent, WebIntelligenceResult


class WebResearcher:
    """
    Advanced web research tool that can:
    1. Search news and sentiment for specific tickers/themes
    2. Analyze fundamental information from web sources
    3. Cross-reference multiple sources for validation
    4. Generate comprehensive research reports
    """
    
    def __init__(self):
        self.use_llm = bool(config.openai_api_key)
        self.search_cache = {}
        self.cache_duration = 3600  # 1 hour cache
        self.web_agent_initialized = False
        
    async def research_opportunity(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Comprehensive research on an investment opportunity using advanced web intelligence.
        """
        try:
            logger.info(f"WebResearcher | Researching opportunity: {opportunity.get('theme', 'Unknown')}")
            
            # Initialize web intelligence agent if needed
            if not self.web_agent_initialized:
                await web_intelligence_agent.initialize()
                self.web_agent_initialized = True
            
            # Gather comprehensive web intelligence
            theme = opportunity.get('theme', 'investment opportunity')
            intelligence_result = await web_intelligence_agent.gather_intelligence(
                query=theme,
                tickers=tickers,
                max_pages=15
            )
            
            # Multi-faceted research approach
            research_results = {
                "opportunity": opportunity,
                "tickers": tickers,
                "web_intelligence": intelligence_result,
                "sentiment_analysis": intelligence_result.sentiment_analysis,
                "fundamental_analysis": await self._analyze_fundamentals_advanced(intelligence_result, tickers),
                "news_analysis": await self._analyze_news_advanced(intelligence_result, opportunity, tickers),
                "market_context": await self._get_market_context_advanced(intelligence_result, tickers),
                "risk_assessment": await self._assess_risks_advanced(intelligence_result, opportunity, tickers),
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate comprehensive report
            report = await self._generate_research_report_advanced(research_results)
            
            logger.info(f"WebResearcher | Research complete for {len(tickers)} tickers")
            return report
            
        except Exception as e:
            logger.error(f"WebResearcher research error: {e}")
            return self._fallback_research_advanced(opportunity, tickers)
    
    async def _analyze_fundamentals_advanced(self, intelligence_result: WebIntelligenceResult, tickers: List[str]) -> Dict[str, Any]:
        """
        Advanced fundamental analysis using web intelligence data.
        """
        if not self.use_llm:
            return {"analysis": "advanced", "confidence": 0.6}
        
        try:
            # Extract fundamental information from web intelligence
            fundamental_content = []
            for page in intelligence_result.pages[:5]:
                if any(ticker.lower() in page.content.lower() for ticker in tickers):
                    fundamental_content.append(f"Source: {page.source}\nContent: {page.content[:500]}...")
            
            if not fundamental_content:
                return {"analysis": "insufficient_data", "confidence": 0.2}
            
            # LLM analyzes fundamental data
            fundamental_prompt = f"""Analyze the fundamental strength of these tickers based on web intelligence data.
            
            Tickers: {tickers}
            
            Web Intelligence Data:
            {chr(10).join(fundamental_content)}
            
            Key Insights:
            {chr(10).join(intelligence_result.insights[:5])}
            
            Analyze:
            1. Financial health and performance indicators
            2. Business model strength and competitive advantages
            3. Market position and competitive landscape
            4. Growth prospects and catalysts
            5. Valuation attractiveness
            6. Key risks and concerns
            
            Respond in JSON:
            {{
                "financial_health": "strong/moderate/weak",
                "business_model": "analysis of business model",
                "competitive_position": "market position analysis",
                "growth_prospects": "growth outlook",
                "valuation": "attractive/fair/expensive",
                "key_catalysts": ["catalyst 1", "catalyst 2"],
                "key_risks": ["risk 1", "risk 2"],
                "overall_score": 0.0-1.0,
                "confidence": 0.0-1.0
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": fundamental_prompt}
            ], temperature=0.3)
            
            fundamentals = json.loads(response.get("content", "{}"))
            return fundamentals
            
        except Exception as e:
            logger.error(f"Advanced fundamental analysis error: {e}")
            return {"analysis": "error", "confidence": 0.2}
    
    async def _analyze_news_advanced(self, intelligence_result: WebIntelligenceResult, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Advanced news analysis using web intelligence data.
        """
        try:
            # Extract news-related content
            news_content = []
            for page in intelligence_result.pages:
                if any(word in page.title.lower() for word in ['news', 'breaking', 'announcement', 'report']):
                    news_content.append(f"Title: {page.title}\nContent: {page.content[:300]}...")
            
            return {
                "recent_news": news_content[:5],
                "news_sentiment": intelligence_result.sentiment_analysis,
                "key_developments": intelligence_result.insights[:3],
                "sources": intelligence_result.sources[:5],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Advanced news analysis error: {e}")
            return {"news_analysis": "error"}
    
    async def _get_market_context_advanced(self, intelligence_result: WebIntelligenceResult, tickers: List[str]) -> Dict[str, Any]:
        """
        Advanced market context analysis using web intelligence.
        """
        try:
            return {
                "market_sentiment": intelligence_result.sentiment_analysis,
                "risk_factors": intelligence_result.risk_factors,
                "opportunities": intelligence_result.opportunities,
                "key_insights": intelligence_result.insights,
                "sources_analyzed": len(intelligence_result.pages),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Advanced market context error: {e}")
            return {"market_context": "error"}
    
    async def _assess_risks_advanced(self, intelligence_result: WebIntelligenceResult, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Advanced risk assessment using web intelligence data.
        """
        try:
            return {
                "identified_risks": intelligence_result.risk_factors,
                "risk_sentiment": intelligence_result.sentiment_analysis,
                "risk_level": "high" if len(intelligence_result.risk_factors) > 3 else "medium" if len(intelligence_result.risk_factors) > 1 else "low",
                "mitigation_suggestions": self._generate_risk_mitigation(intelligence_result.risk_factors),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Advanced risk assessment error: {e}")
            return {"risk_assessment": "error"}
    
    def _generate_risk_mitigation(self, risks: List[str]) -> List[str]:
        """Generate risk mitigation suggestions."""
        mitigations = []
        for risk in risks[:3]:
            if "volatility" in risk.lower():
                mitigations.append("Consider position sizing and stop-loss orders")
            elif "earnings" in risk.lower():
                mitigations.append("Monitor earnings calendar and analyst expectations")
            elif "market" in risk.lower():
                mitigations.append("Diversify across sectors and asset classes")
            else:
                mitigations.append("Monitor closely and adjust position as needed")
        return mitigations
    
    async def _generate_research_report_advanced(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive research report using advanced web intelligence.
        """
        try:
            intelligence_result = research_results.get("web_intelligence")
            
            report = {
                "opportunity": research_results["opportunity"],
                "tickers": research_results["tickers"],
                "executive_summary": self._generate_executive_summary(research_results),
                "web_intelligence_summary": {
                    "pages_analyzed": len(intelligence_result.pages) if intelligence_result else 0,
                    "sources": intelligence_result.sources if intelligence_result else [],
                    "key_insights": intelligence_result.insights if intelligence_result else [],
                    "sentiment": intelligence_result.sentiment_analysis if intelligence_result else {},
                },
                "fundamental_analysis": research_results["fundamental_analysis"],
                "news_analysis": research_results["news_analysis"],
                "market_context": research_results["market_context"],
                "risk_assessment": research_results["risk_assessment"],
                "recommendations": self._generate_recommendations(research_results),
                "timestamp": research_results["timestamp"]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Advanced report generation error: {e}")
            return self._fallback_research_advanced(research_results["opportunity"], research_results["tickers"])
    
    def _generate_executive_summary(self, research_results: Dict[str, Any]) -> str:
        """Generate executive summary."""
        try:
            sentiment = research_results.get("sentiment_analysis", {})
            sentiment_text = sentiment.get("sentiment", "neutral")
            confidence = sentiment.get("confidence", 0.5)
            
            return f"Analysis shows {sentiment_text} sentiment (confidence: {confidence:.2f}) for {research_results['opportunity'].get('theme', 'opportunity')}. Key insights include {len(research_results.get('web_intelligence', {}).get('insights', []))} identified factors."
            
        except Exception as e:
            return "Executive summary generation failed"
    
    def _generate_recommendations(self, research_results: Dict[str, Any]) -> List[str]:
        """Generate investment recommendations."""
        try:
            recommendations = []
            sentiment = research_results.get("sentiment_analysis", {})
            
            if sentiment.get("sentiment") == "bullish":
                recommendations.append("Consider initiating or increasing position")
                recommendations.append("Monitor for entry opportunities on pullbacks")
            elif sentiment.get("sentiment") == "bearish":
                recommendations.append("Consider reducing position or waiting for better entry")
                recommendations.append("Monitor for reversal signals")
            else:
                recommendations.append("Maintain current position with close monitoring")
                recommendations.append("Wait for clearer directional signals")
            
            return recommendations
            
        except Exception as e:
            return ["Recommendations generation failed"]
    
    def _fallback_research_advanced(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """Fallback research when web intelligence fails."""
        return {
            "opportunity": opportunity,
            "tickers": tickers,
            "executive_summary": "Web intelligence gathering failed, using fallback analysis",
            "web_intelligence_summary": {
                "pages_analyzed": 0,
                "sources": [],
                "key_insights": ["Insufficient data for comprehensive analysis"],
                "sentiment": {"sentiment": "neutral", "confidence": 0.0},
            },
            "fundamental_analysis": {"analysis": "fallback", "confidence": 0.2},
            "news_analysis": {"news_analysis": "fallback"},
            "market_context": {"market_context": "fallback"},
            "risk_assessment": {"risk_assessment": "fallback"},
            "recommendations": ["Data gathering failed - manual research recommended"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_fundamentals(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Analyze fundamental information for the tickers.
        """
        if not self.use_llm:
            return {"analysis": "basic", "confidence": 0.4}
        
        try:
            fundamental_data = {}
            
            for ticker in tickers[:2]:  # Limit to 2 tickers for detailed analysis
                # Search for fundamental information
                search_queries = [
                    f"{ticker} earnings financial results",
                    f"{ticker} company fundamentals valuation",
                    f"{ticker} business model competitive advantage"
                ]
                
                ticker_results = []
                for query in search_queries:
                    results = self._web_search(query)
                    if results:
                        ticker_results.extend(results[:2])
                
                fundamental_data[ticker] = ticker_results
            
            if not any(fundamental_data.values()):
                return {"analysis": "insufficient_data", "confidence": 0.2}
            
            # LLM analyzes fundamental data
            fundamental_prompt = f"""Analyze the fundamental strength of these tickers based on web search results.
            
            Tickers: {tickers}
            
            Fundamental Data:
            {json.dumps(fundamental_data, indent=2)}
            
            Analyze:
            1. Financial health and performance
            2. Business model strength
            3. Competitive position
            4. Growth prospects
            5. Valuation attractiveness
            6. Key risks and catalysts
            
            Respond in JSON:
            {{
                "financial_health": "strong/moderate/weak",
                "business_model": "analysis of business model",
                "competitive_position": "market position analysis",
                "growth_prospects": "growth outlook",
                "valuation": "attractive/fair/expensive",
                "key_catalysts": ["catalyst 1", "catalyst 2"],
                "key_risks": ["risk 1", "risk 2"],
                "overall_score": 0.0-1.0,
                "confidence": 0.0-1.0
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": fundamental_prompt}
            ], temperature=0.3)
            
            fundamentals = json.loads(response.get("content", "{}"))
            return fundamentals
            
        except Exception as e:
            logger.error(f"Fundamental analysis error: {e}")
            return {"analysis": "error", "confidence": 0.2}
    
    def _analyze_news(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Analyze recent news for relevance to the opportunity.
        """
        try:
            # Search for recent news
            news_queries = [
                f"{opportunity.get('theme', '')} news recent",
                f"{' '.join(tickers)} breaking news",
                f"{opportunity.get('theme', '')} market impact news"
            ]
            
            news_results = []
            for query in news_queries:
                results = self._web_search(query, search_type="news")
                if results:
                    news_results.extend(results[:2])
            
            if not news_results:
                return {"news_impact": "minimal", "confidence": 0.3}
            
            if not self.use_llm:
                return {"news_impact": "moderate", "confidence": 0.4}
            
            # LLM analyzes news impact
            news_prompt = f"""Analyze the impact of recent news on this investment opportunity.
            
            Opportunity: {json.dumps(opportunity, indent=2)}
            Tickers: {tickers}
            
            Recent News:
            {json.dumps(news_results, indent=2)}
            
            Analyze:
            1. News relevance to opportunity
            2. Potential market impact
            3. Time-sensitive factors
            4. Conflicting information
            5. Market reaction predictions
            
            Respond in JSON:
            {{
                "relevance": "high/medium/low",
                "impact": "positive/negative/neutral",
                "time_sensitivity": "immediate/short-term/long-term",
                "key_developments": ["development 1", "development 2"],
                "market_reaction": "predicted market response",
                "confidence": 0.0-1.0
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": news_prompt}
            ], temperature=0.3)
            
            news_analysis = json.loads(response.get("content", "{}"))
            return news_analysis
            
        except Exception as e:
            logger.error(f"News analysis error: {e}")
            return {"news_impact": "error", "confidence": 0.2}
    
    def _get_market_context(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Get broader market context for the opportunity.
        """
        try:
            context_queries = [
                f"{' '.join(tickers)} sector performance",
                f"market conditions {datetime.now().strftime('%Y-%m')}",
                f"{' '.join(tickers)} peer comparison"
            ]
            
            context_results = []
            for query in context_queries:
                results = self._web_search(query)
                if results:
                    context_results.extend(results[:2])
            
            return {
                "sector_context": "market context analysis",
                "peer_comparison": "peer analysis",
                "market_conditions": "current market environment",
                "data_sources": len(context_results),
                "confidence": 0.6 if context_results else 0.3
            }
            
        except Exception as e:
            logger.error(f"Market context error: {e}")
            return {"context": "error", "confidence": 0.2}
    
    def _assess_risks(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Assess risks specific to this opportunity.
        """
        try:
            risk_queries = [
                f"{opportunity.get('theme', '')} investment risks",
                f"{' '.join(tickers)} stock risks challenges",
                f"{opportunity.get('theme', '')} market volatility"
            ]
            
            risk_results = []
            for query in risk_queries:
                results = self._web_search(query)
                if results:
                    risk_results.extend(results[:2])
            
            # Basic risk assessment
            risk_factors = opportunity.get('risk_factors', [])
            
            return {
                "identified_risks": risk_factors,
                "market_risks": ["market volatility", "sector rotation"],
                "specific_risks": ["company-specific risks"],
                "risk_level": "moderate",
                "mitigation_strategies": ["diversification", "position sizing"],
                "confidence": 0.5
            }
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {"risk_level": "unknown", "confidence": 0.2}
    
    def _web_search(self, query: str, search_type: str = "general") -> List[Dict[str, Any]]:
        """
        Perform web search using the web search wrapper.
        """
        try:
            from tools.web_search_wrapper import web_search_wrapper
            
            # Use the web search wrapper for actual search
            results = web_search_wrapper.search(query, max_results=5)
            
            return results
            
        except ImportError:
            logger.warning("Web search wrapper not available, using fallback")
            return []
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def _generate_research_report(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive research report.
        """
        if not self.use_llm:
            return research_results
        
        try:
            report_prompt = f"""Generate a comprehensive investment research report based on this analysis.
            
            Research Results:
            {json.dumps(research_results, indent=2)}
            
            Create a structured report with:
            1. Executive summary
            2. Investment thesis validation
            3. Risk/reward assessment
            4. Recommendation with confidence level
            5. Key actionable insights
            
            Respond in JSON:
            {{
                "executive_summary": "key findings summary",
                "thesis_validation": "opportunity validation",
                "risk_reward": "risk/reward analysis",
                "recommendation": "BUY/SELL/HOLD/RESEARCH",
                "confidence": 0.0-1.0,
                "key_insights": ["insight 1", "insight 2"],
                "action_items": ["action 1", "action 2"]
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": report_prompt}
            ], temperature=0.2)
            
            report = json.loads(response.get("content", "{}"))
            
            # Combine with original research
            return {**research_results, "report": report}
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return research_results
    
    def _fallback_research(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Fallback research when web research fails.
        """
        return {
            "opportunity": opportunity,
            "tickers": tickers,
            "sentiment_analysis": {"sentiment": "neutral", "confidence": 0.3},
            "fundamental_analysis": {"analysis": "basic", "confidence": 0.3},
            "news_analysis": {"news_impact": "minimal", "confidence": 0.3},
            "market_context": {"context": "limited", "confidence": 0.3},
            "risk_assessment": {"risk_level": "moderate", "confidence": 0.3},
            "report": {
                "executive_summary": "Limited research available",
                "recommendation": "RESEARCH",
                "confidence": 0.3
            }
        }


# Global instance
web_researcher = WebResearcher()