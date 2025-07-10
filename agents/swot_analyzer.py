from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from core.openai_manager import openai_manager
from core.structured_order import SWOTAnalysis
from utils.logger import logger


class SWOTAnalyzerAgent:
    """Agent that performs comprehensive SWOT analysis on trading opportunities"""
    
    def __init__(self):
        self.use_llm = bool(openai_manager.enabled)
    
    def analyze_opportunity(self, 
                          symbol: str,
                          market_data: Dict[str, Any],
                          news_data: List[str],
                          technical_indicators: Optional[Dict[str, Any]] = None,
                          fundamental_data: Optional[Dict[str, Any]] = None,
                          sector_data: Optional[Dict[str, Any]] = None) -> SWOTAnalysis:
        """Perform comprehensive SWOT analysis on a trading opportunity"""
        
        if self.use_llm:
            return self._llm_swot_analysis(symbol, market_data, news_data, 
                                         technical_indicators, fundamental_data, sector_data)
        else:
            return self._heuristic_swot_analysis(symbol, market_data, news_data)
    
    def _llm_swot_analysis(self,
                          symbol: str,
                          market_data: Dict[str, Any],
                          news_data: List[str],
                          technical_indicators: Optional[Dict[str, Any]] = None,
                          fundamental_data: Optional[Dict[str, Any]] = None,
                          sector_data: Optional[Dict[str, Any]] = None) -> SWOTAnalysis:
        """Use LLM to perform SWOT analysis"""
        
        # Prepare context data
        context = {
            "symbol": symbol,
            "market_data": market_data,
            "news_headlines": news_data[:10],  # Limit to 10 most recent
            "technical_indicators": technical_indicators or {},
            "fundamental_data": fundamental_data or {},
            "sector_data": sector_data or {}
        }
        
        prompt = """
You are a senior investment analyst performing a comprehensive SWOT analysis for a trading opportunity.

Given the market data, news, and technical/fundamental information, analyze the trading opportunity and provide:

1. STRENGTHS: List 3-5 key strengths that support this trade
2. WEAKNESSES: List 3-5 key weaknesses or concerns
3. OPPORTUNITIES: List 3-5 potential opportunities or catalysts
4. THREATS: List 3-5 potential threats or risks
5. OVERALL_SCORE: A score from -1.0 to 1.0 where:
   - 1.0 = Extremely bullish opportunity
   - 0.0 = Neutral
   - -1.0 = Extremely bearish opportunity
6. CONFIDENCE: Your confidence in this analysis (0.0 to 1.0)

Respond in JSON format with these exact keys: strengths, weaknesses, opportunities, threats, overall_score, confidence

Context data:
{context}
"""
        
        try:
            result = openai_manager.chat_completion([
                {"role": "system", "content": "You are a professional investment analyst. Provide objective, data-driven SWOT analysis."},
                {"role": "user", "content": prompt.format(context=json.dumps(context, indent=2))}
            ], temperature=0.3)
            
            # Parse the response
            try:
                data = json.loads(result["content"] or "{}")
            except json.JSONDecodeError as e:
                logger.warning(f"SWOT Analyzer | JSON parse error: {e}")
                return self._heuristic_swot_analysis(symbol, market_data, news_data)
            
            # Validate and create SWOT analysis
            return SWOTAnalysis(
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                opportunities=data.get("opportunities", []),
                threats=data.get("threats", []),
                overall_score=float(data.get("overall_score", 0.0)),
                confidence=float(data.get("confidence", 0.5))
            )
            
        except Exception as e:
            logger.warning(f"SWOT Analyzer | LLM error: {e}, falling back to heuristic")
            return self._heuristic_swot_analysis(symbol, market_data, news_data)
    
    def _heuristic_swot_analysis(self,
                                symbol: str,
                                market_data: Dict[str, Any],
                                news_data: List[str]) -> SWOTAnalysis:
        """Fallback heuristic SWOT analysis"""
        
        # Extract key metrics
        price_change = market_data.get("change_pct", 0)
        current_price = market_data.get("price", 0)
        pe_ratio = market_data.get("pe")
        pb_ratio = market_data.get("pb")
        valuation = market_data.get("valuation", "fair")
        
        # Analyze news sentiment
        positive_keywords = ["rally", "gain", "surge", "up", "positive", "beat", "strong", "growth"]
        negative_keywords = ["drop", "fall", "plunge", "down", "negative", "miss", "weak", "decline"]
        
        positive_news = sum(1 for headline in news_data 
                          if any(keyword in headline.lower() for keyword in positive_keywords))
        negative_news = sum(1 for headline in news_data 
                           if any(keyword in headline.lower() for keyword in negative_keywords))
        
        # Generate SWOT components
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # Strengths
        if price_change > 0:
            strengths.append(f"Positive price momentum ({price_change:.2f}% gain)")
        if valuation == "under":
            strengths.append("Undervalued based on P/E and P/B ratios")
        if positive_news > negative_news:
            strengths.append(f"Positive news sentiment ({positive_news} positive vs {negative_news} negative)")
        
        # Weaknesses
        if price_change < 0:
            weaknesses.append(f"Negative price momentum ({price_change:.2f}% decline)")
        if valuation == "over":
            weaknesses.append("Overvalued based on P/E and P/B ratios")
        if negative_news > positive_news:
            weaknesses.append(f"Negative news sentiment ({negative_news} negative vs {positive_news} positive)")
        
        # Opportunities
        if price_change < -5:
            opportunities.append("Significant price decline may present buying opportunity")
        if positive_news > 0:
            opportunities.append("Positive news flow suggests potential upside")
        
        # Threats
        if price_change > 10:
            threats.append("Significant price increase may lead to profit-taking")
        if negative_news > 0:
            threats.append("Negative news flow suggests potential downside")
        
        # Calculate overall score
        overall_score = 0.0
        if price_change > 0:
            overall_score += min(price_change / 10, 0.3)  # Cap at 0.3
        else:
            overall_score -= min(abs(price_change) / 10, 0.3)
        
        if valuation == "under":
            overall_score += 0.2
        elif valuation == "over":
            overall_score -= 0.2
        
        if positive_news > negative_news:
            overall_score += 0.1
        elif negative_news > positive_news:
            overall_score -= 0.1
        
        # Clamp score to [-1, 1]
        overall_score = max(-1.0, min(1.0, overall_score))
        
        # Calculate confidence based on data quality
        confidence = 0.5  # Base confidence
        if market_data:
            confidence += 0.2
        if news_data:
            confidence += 0.2
        if pe_ratio and pb_ratio:
            confidence += 0.1
        
        confidence = min(1.0, confidence)
        
        return SWOTAnalysis(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            overall_score=overall_score,
            confidence=confidence
        )
    
    def analyze_sector_swot(self, sector: str, sector_data: Dict[str, Any]) -> SWOTAnalysis:
        """Perform SWOT analysis on a sector"""
        
        # This would be similar to the symbol analysis but focused on sector-level data
        # For now, return a basic analysis
        return SWOTAnalysis(
            strengths=["Sector analysis not yet implemented"],
            weaknesses=[],
            opportunities=[],
            threats=[],
            overall_score=0.0,
            confidence=0.3
        )
    
    def compare_swot_analyses(self, analyses: List[SWOTAnalysis]) -> Dict[str, Any]:
        """Compare multiple SWOT analyses and provide insights"""
        
        if not analyses:
            return {"error": "No analyses to compare"}
        
        # Calculate aggregate scores
        avg_score = sum(analysis.overall_score for analysis in analyses) / len(analyses)
        avg_confidence = sum(analysis.confidence for analysis in analyses) / len(analyses)
        
        # Find best and worst opportunities
        best_analysis = max(analyses, key=lambda x: x.overall_score)
        worst_analysis = min(analyses, key=lambda x: x.overall_score)
        
        # Aggregate common themes
        all_strengths = []
        all_weaknesses = []
        all_opportunities = []
        all_threats = []
        
        for analysis in analyses:
            all_strengths.extend(analysis.strengths)
            all_weaknesses.extend(analysis.weaknesses)
            all_opportunities.extend(analysis.opportunities)
            all_threats.extend(analysis.threats)
        
        return {
            "average_score": avg_score,
            "average_confidence": avg_confidence,
            "best_opportunity_score": best_analysis.overall_score,
            "worst_opportunity_score": worst_analysis.overall_score,
            "common_strengths": list(set(all_strengths)),
            "common_weaknesses": list(set(all_weaknesses)),
            "common_opportunities": list(set(all_opportunities)),
            "common_threats": list(set(all_threats)),
            "analysis_count": len(analyses)
        }


# Global SWOT analyzer instance
swot_analyzer = SWOTAnalyzerAgent() 