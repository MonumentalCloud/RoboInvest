from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import math

from core.openai_manager import openai_manager
from core.structured_order import RiskAssessment, RiskLevel
from core.finnhub_client import finnhub_client
from utils.logger import logger


class RiskAssessorAgent:
    """Agent that performs comprehensive risk assessment on trading opportunities"""
    
    def __init__(self):
        self.use_llm = bool(openai_manager.enabled)
        self.risk_thresholds = {
            "low": {"max_loss_pct": 2.0, "var_95": 1.0, "volatility": 0.15},
            "medium": {"max_loss_pct": 5.0, "var_95": 2.5, "volatility": 0.25},
            "high": {"max_loss_pct": 10.0, "var_95": 5.0, "volatility": 0.35},
            "extreme": {"max_loss_pct": 15.0, "var_95": 7.5, "volatility": 0.50}
        }
    
    def assess_risk(self,
                   symbol: str,
                   quantity: int,
                   current_price: float,
                   market_data: Dict[str, Any],
                   historical_data: Optional[List[Dict[str, Any]]] = None,
                   sector_data: Optional[Dict[str, Any]] = None,
                   market_context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        
        # Calculate basic risk metrics
        position_value = quantity * current_price
        max_loss_amount = position_value * 0.15  # Assume 15% max loss for now
        max_loss_percentage = 15.0
        
        # Calculate volatility from historical data
        volatility = self._calculate_volatility(historical_data) if historical_data else 0.25
        
        # Calculate VaR (Value at Risk)
        var_95 = self._calculate_var_95(position_value, volatility)
        
        # Calculate correlation with SPY
        correlation_with_spy = self._calculate_correlation_with_spy(symbol, historical_data)
        
        # Assess sector risk
        sector_risk = self._assess_sector_risk(symbol, sector_data)
        
        # Assess market timing risk
        market_timing_risk = self._assess_market_timing_risk(market_context)
        
        # Assess liquidity risk
        liquidity_risk = self._assess_liquidity_risk(symbol, market_data)
        
        # Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk_score(
            volatility, var_95, sector_risk, market_timing_risk, liquidity_risk
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_risk_score)
        
        # Calculate Sharpe ratio (simplified)
        sharpe_ratio = self._calculate_sharpe_ratio(historical_data) if historical_data else None
        
        # Calculate beta (simplified)
        beta = self._calculate_beta(symbol, historical_data) if historical_data else None
        
        return RiskAssessment(
            risk_level=risk_level,
            max_loss_amount=max_loss_amount,
            max_loss_percentage=max_loss_percentage,
            var_95=var_95,
            sharpe_ratio=sharpe_ratio,
            beta=beta,
            volatility=volatility,
            correlation_with_spy=correlation_with_spy,
            sector_risk=sector_risk,
            market_timing_risk=market_timing_risk,
            liquidity_risk=liquidity_risk,
            overall_risk_score=overall_risk_score
        )
    
    def _calculate_volatility(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate historical volatility"""
        if not historical_data or len(historical_data) < 2:
            return 0.25  # Default volatility
        
        # Extract prices and calculate returns
        prices = [day.get("close", 0) for day in historical_data if day.get("close")]
        if len(prices) < 2:
            return 0.25
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if not returns:
            return 0.25
        
        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance)
        
        # Annualize (assuming daily data)
        annualized_volatility = volatility * math.sqrt(252)
        
        return min(annualized_volatility, 1.0)  # Cap at 100%
    
    def _calculate_var_95(self, position_value: float, volatility: float) -> float:
        """Calculate 95% Value at Risk"""
        # Simplified VaR calculation: 1.645 * volatility * position_value
        var_95 = 1.645 * volatility * position_value
        return min(var_95, position_value * 0.5)  # Cap at 50% of position
    
    def _calculate_correlation_with_spy(self, symbol: str, historical_data: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate correlation with SPY"""
        # This would require SPY historical data for proper calculation
        # For now, return estimated correlation based on sector
        sector_correlations = {
            "AAPL": 0.7, "MSFT": 0.8, "GOOGL": 0.75, "AMZN": 0.8,
            "TSLA": 0.6, "NVDA": 0.7, "META": 0.75, "NFLX": 0.65
        }
        return sector_correlations.get(symbol, 0.7)
    
    def _assess_sector_risk(self, symbol: str, sector_data: Optional[Dict[str, Any]]) -> float:
        """Assess sector-specific risk"""
        # Sector risk scores (0.0 to 1.0, higher = more risky)
        sector_risks = {
            "technology": 0.6,
            "healthcare": 0.5,
            "financial": 0.7,
            "energy": 0.8,
            "consumer": 0.4,
            "industrial": 0.6,
            "materials": 0.7,
            "utilities": 0.3,
            "real_estate": 0.6,
            "communication": 0.5
        }
        
        # Try to determine sector from symbol or data
        if sector_data and "sector" in sector_data:
            sector = sector_data["sector"].lower()
            return sector_risks.get(sector, 0.5)
        
        # Default sector risk
        return 0.5
    
    def _assess_market_timing_risk(self, market_context: Optional[Dict[str, Any]]) -> float:
        """Assess market timing risk"""
        if not market_context:
            return 0.5  # Neutral risk
        
        # Extract market indicators
        vix = market_context.get("vix", 20)
        market_sentiment = market_context.get("sentiment", "neutral")
        market_volatility = market_context.get("volatility", 0.2)
        
        # Calculate timing risk
        timing_risk = 0.5  # Base risk
        
        # VIX-based adjustment
        if vix > 30:
            timing_risk += 0.2  # High volatility = higher timing risk
        elif vix < 15:
            timing_risk -= 0.1  # Low volatility = lower timing risk
        
        # Sentiment-based adjustment
        if market_sentiment == "bearish":
            timing_risk += 0.1
        elif market_sentiment == "bullish":
            timing_risk -= 0.05
        
        # Volatility-based adjustment
        if market_volatility > 0.3:
            timing_risk += 0.15
        
        return max(0.0, min(1.0, timing_risk))
    
    def _assess_liquidity_risk(self, symbol: str, market_data: Dict[str, Any]) -> float:
        """Assess liquidity risk"""
        # Extract volume and bid-ask spread data
        volume = market_data.get("volume", 0)
        avg_volume = market_data.get("avg_volume", volume)
        
        # Calculate liquidity score
        if volume == 0 or avg_volume == 0:
            return 0.8  # High liquidity risk if no volume data
        
        # Volume ratio (current vs average)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
        
        # Liquidity risk based on volume
        if volume_ratio > 2.0:
            liquidity_risk = 0.2  # High volume = low risk
        elif volume_ratio > 1.0:
            liquidity_risk = 0.4  # Normal volume = moderate risk
        elif volume_ratio > 0.5:
            liquidity_risk = 0.6  # Low volume = higher risk
        else:
            liquidity_risk = 0.8  # Very low volume = high risk
        
        # Adjust for large-cap vs small-cap
        if symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]:
            liquidity_risk *= 0.7  # Large caps are more liquid
        
        return max(0.0, min(1.0, liquidity_risk))
    
    def _calculate_overall_risk_score(self,
                                    volatility: float,
                                    var_95: float,
                                    sector_risk: float,
                                    market_timing_risk: float,
                                    liquidity_risk: float) -> float:
        """Calculate overall risk score (0.0 to 1.0)"""
        
        # Weighted average of risk components
        weights = {
            "volatility": 0.25,
            "var_95": 0.20,
            "sector_risk": 0.20,
            "market_timing": 0.15,
            "liquidity": 0.20
        }
        
        # Normalize VaR to 0-1 scale (assuming max 20% of position)
        normalized_var = min(var_95 / 0.2, 1.0)
        
        overall_score = (
            volatility * weights["volatility"] +
            normalized_var * weights["var_95"] +
            sector_risk * weights["sector_risk"] +
            market_timing_risk * weights["market_timing"] +
            liquidity_risk * weights["liquidity"]
        )
        
        return max(0.0, min(1.0, overall_score))
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on overall risk score"""
        if risk_score < 0.3:
            return RiskLevel.LOW
        elif risk_score < 0.5:
            return RiskLevel.MEDIUM
        elif risk_score < 0.7:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME
    
    def _calculate_sharpe_ratio(self, historical_data: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate Sharpe ratio (simplified)"""
        if not historical_data or len(historical_data) < 30:
            return None
        
        # Calculate returns
        prices = [day.get("close", 0) for day in historical_data if day.get("close")]
        if len(prices) < 30:
            return None
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if len(returns) < 29:
            return None
        
        # Calculate mean return and standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return None
        
        # Annualize (assuming daily data)
        annualized_return = mean_return * 252
        annualized_std = std_dev * math.sqrt(252)
        
        # Risk-free rate (simplified)
        risk_free_rate = 0.02  # 2% annual
        
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        return sharpe_ratio
    
    def _calculate_beta(self, symbol: str, historical_data: Optional[List[Dict[str, Any]]]) -> Optional[float]:
        """Calculate beta relative to market (simplified)"""
        # This would require market data for proper calculation
        # For now, return estimated betas
        estimated_betas = {
            "AAPL": 1.2, "MSFT": 1.1, "GOOGL": 1.0, "AMZN": 1.3,
            "TSLA": 1.8, "NVDA": 1.5, "META": 1.2, "NFLX": 1.4
        }
        return estimated_betas.get(symbol, 1.0)
    
    def get_risk_summary(self, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Get a summary of risk assessment for reporting"""
        return {
            "risk_level": risk_assessment.risk_level.value,
            "overall_risk_score": risk_assessment.overall_risk_score,
            "max_loss_amount": risk_assessment.max_loss_amount,
            "max_loss_percentage": risk_assessment.max_loss_percentage,
            "var_95": risk_assessment.var_95,
            "volatility": risk_assessment.volatility,
            "sharpe_ratio": risk_assessment.sharpe_ratio,
            "beta": risk_assessment.beta,
            "correlation_with_spy": risk_assessment.correlation_with_spy,
            "sector_risk": risk_assessment.sector_risk,
            "market_timing_risk": risk_assessment.market_timing_risk,
            "liquidity_risk": risk_assessment.liquidity_risk,
            "risk_breakdown": {
                "volatility_contribution": risk_assessment.volatility * 0.25,
                "var_contribution": min(risk_assessment.var_95 / 0.2, 1.0) * 0.20,
                "sector_contribution": risk_assessment.sector_risk * 0.20,
                "timing_contribution": risk_assessment.market_timing_risk * 0.15,
                "liquidity_contribution": risk_assessment.liquidity_risk * 0.20
            }
        }
    
    def compare_risk_assessments(self, assessments: List[RiskAssessment]) -> Dict[str, Any]:
        """Compare multiple risk assessments"""
        if not assessments:
            return {"error": "No assessments to compare"}
        
        # Calculate aggregate metrics
        avg_risk_score = sum(assessment.overall_risk_score for assessment in assessments) / len(assessments)
        avg_volatility = sum(assessment.volatility for assessment in assessments) / len(assessments)
        avg_var_95 = sum(assessment.var_95 for assessment in assessments) / len(assessments)
        
        # Find riskiest and safest
        riskiest = max(assessments, key=lambda x: x.overall_risk_score)
        safest = min(assessments, key=lambda x: x.overall_risk_score)
        
        # Count by risk level
        risk_level_counts = {}
        for level in RiskLevel:
            risk_level_counts[level.value] = sum(
                1 for assessment in assessments if assessment.risk_level == level
            )
        
        return {
            "average_risk_score": avg_risk_score,
            "average_volatility": avg_volatility,
            "average_var_95": avg_var_95,
            "riskiest_assessment": {
                "risk_score": riskiest.overall_risk_score,
                "risk_level": riskiest.risk_level.value
            },
            "safest_assessment": {
                "risk_score": safest.overall_risk_score,
                "risk_level": safest.risk_level.value
            },
            "risk_level_distribution": risk_level_counts,
            "assessment_count": len(assessments)
        }


# Global risk assessor instance
risk_assessor = RiskAssessorAgent() 