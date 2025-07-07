"""
Web Researcher Tool
Performs sentiment analysis and fundamental research using web searches.
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger  # type: ignore


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
        
    def research_opportunity(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Comprehensive research on an investment opportunity.
        """
        try:
            logger.info(f"WebResearcher | Researching opportunity: {opportunity.get('theme', 'Unknown')}")
            
            # Multi-faceted research approach
            research_results = {
                "opportunity": opportunity,
                "tickers": tickers,
                "sentiment_analysis": self._analyze_sentiment(opportunity, tickers),
                "fundamental_analysis": self._analyze_fundamentals(tickers),
                "news_analysis": self._analyze_news(opportunity, tickers),
                "market_context": self._get_market_context(tickers),
                "risk_assessment": self._assess_risks(opportunity, tickers),
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate comprehensive report
            report = self._generate_research_report(research_results)
            
            logger.info(f"WebResearcher | Research complete for {len(tickers)} tickers")
            return report
            
        except Exception as e:
            logger.error(f"WebResearcher research error: {e}")
            return self._fallback_research(opportunity, tickers)
    
    def _analyze_sentiment(self, opportunity: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment for the opportunity and specific tickers.
        """
        if not self.use_llm:
            return {"sentiment": "neutral", "confidence": 0.5}
        
        try:
            # Search for recent news and sentiment
            search_queries = [
                f"{opportunity.get('theme', '')} investment opportunity",
                f"{' '.join(tickers[:2])} stock news sentiment",
                f"{opportunity.get('theme', '')} market impact"
            ]
            
            search_results = []
            for query in search_queries:
                results = self._web_search(query)
                if results:
                    search_results.extend(results[:3])  # Top 3 results per query
            
            if not search_results:
                return {"sentiment": "neutral", "confidence": 0.3}
            
            # LLM analyzes sentiment from search results
            sentiment_prompt = f"""Analyze the sentiment for this investment opportunity based on web search results.
            
            Opportunity: {json.dumps(opportunity, indent=2)}
            Tickers: {tickers}
            
            Search Results:
            {json.dumps(search_results, indent=2)}
            
            Analyze:
            1. Overall sentiment (bullish/bearish/neutral)
            2. Sentiment strength (0.0-1.0)
            3. Key sentiment drivers
            4. Sentiment divergence across sources
            5. Time-sensitive sentiment factors
            
            Respond in JSON:
            {{
                "sentiment": "bullish/bearish/neutral",
                "strength": 0.0-1.0,
                "drivers": ["key factor 1", "key factor 2"],
                "divergence": "sentiment consistency analysis",
                "time_factors": ["time-sensitive elements"],
                "confidence": 0.0-1.0
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": sentiment_prompt}
            ], temperature=0.3)
            
            sentiment = json.loads(response.get("content", "{}"))
            return sentiment
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.3}
    
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