"""
Enhanced Strategy Agent that uses LLM for analytical thinking 
while delegating numerical calculations to proper tools.
"""

from typing import Any, Dict, List, Optional
import json
from datetime import datetime, timedelta

from core.config import config
from core.openai_manager import openai_manager
from tools.calculator import calculator
from tools.data_fetcher import data_fetcher
from utils.logger import logger  # type: ignore


class EnhancedStrategyAgent:
    """
    Advanced strategy agent that combines LLM analytical thinking
    with proper numerical analysis tools.
    """
    
    def __init__(self):
        self.use_llm = bool(config.openai_api_key)
        self.temperature = 0.3
        self.analysis_cache = {}
        
    def __call__(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for the strategy agent."""
        try:
            logger.info("EnhancedStrategy | Starting comprehensive analysis")
            
            # Step 1: Get enhanced market data
            enhanced_data = self._gather_enhanced_data(observation)
            
            # Step 2: Perform technical analysis using calculator
            technical_analysis = self._perform_technical_analysis(enhanced_data)
            
            # Step 3: LLM interprets all data and makes strategic decision
            decision = self._llm_strategic_decision(observation, enhanced_data, technical_analysis)
            
            # Step 4: Risk assessment using calculator
            risk_assessment = self._calculate_risk_metrics(decision, enhanced_data)
            
            # Step 5: Final decision with risk adjustment
            final_decision = self._finalize_decision(decision, risk_assessment)
            
            logger.info(f"EnhancedStrategy | Final decision: {final_decision['action']} {final_decision['symbol']} (confidence: {final_decision['confidence']:.2f})")
            
            return final_decision
            
        except Exception as e:
            logger.error(f"EnhancedStrategy | Error: {e}")
            return self._fallback_decision(observation)
    
    def _gather_enhanced_data(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Gather comprehensive market data for analysis."""
        try:
            # Get current market overview
            market_overview = data_fetcher.get_market_overview()
            
            # Get sector data for context
            sector_data = data_fetcher.get_sector_data(period="3mo")
            
            # Get benchmark data
            benchmark_data = data_fetcher.get_benchmark_data(period="6mo")
            
            # Get historical data for symbols of interest
            symbols = observation.get('symbols', ['SPY', 'QQQ', 'IWM'])
            historical_data = data_fetcher.get_multiple_symbols(symbols, period="1y")
            
            enhanced_data = {
                "market_overview": market_overview,
                "sector_data": sector_data,
                "benchmark_data": benchmark_data,
                "historical_data": historical_data,
                "observation": observation,
                "timestamp": datetime.now().isoformat()
            }
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Enhanced data gathering error: {e}")
            return {"error": str(e), "observation": observation}
    
    def _perform_technical_analysis(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use calculator to perform technical analysis."""
        try:
            analysis_results = {}
            
            # Analyze each symbol in historical data
            historical_data = enhanced_data.get("historical_data", {})
            
            for symbol, data in historical_data.items():
                if data.get("error") or not data.get("data"):
                    continue
                    
                prices = data["data"]["prices"]["close"]
                
                # Calculate technical indicators
                technical_result = calculator.calculate(
                    "technical analysis",
                    {"prices": prices}
                )
                
                # Calculate volatility
                volatility_result = calculator.calculate(
                    "volatility analysis",
                    {"prices": prices}
                )
                
                # Calculate recent performance
                recent_prices = prices[-30:]  # Last 30 days
                monthly_return = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100) if len(recent_prices) > 1 else 0
                
                analysis_results[symbol] = {
                    "technical_indicators": technical_result.get("result", {}),
                    "volatility_metrics": volatility_result.get("result", {}),
                    "monthly_return": monthly_return,
                    "current_price": prices[-1] if prices else 0
                }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return {"error": str(e)}
    
    def _llm_strategic_decision(self, observation: Dict[str, Any], enhanced_data: Dict[str, Any], technical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for strategic thinking and decision making."""
        if not self.use_llm:
            return self._fallback_decision(observation)
        
        try:
            # Prepare comprehensive context for LLM
            context = {
                "market_overview": enhanced_data.get("market_overview", {}),
                "technical_analysis": technical_analysis,
                "current_sentiment": observation.get("sentiment", "neutral"),
                "news_headlines": observation.get("headlines", []),
                "market_conditions": self._assess_market_conditions(enhanced_data)
            }
            
            system_prompt = """You are an expert quantitative trader with deep market knowledge. 
            You will be provided with comprehensive market data and technical analysis.
            
            Your task is to:
            1. Analyze the overall market conditions
            2. Interpret the technical indicators
            3. Consider sentiment and news impact
            4. Make a strategic trading decision
            
            IMPORTANT: All numerical calculations have already been performed by specialized tools.
            Focus on INTERPRETING the data and making strategic decisions.
            
            Respond in JSON format with:
            {
                "action": "BUY/SELL/HOLD",
                "symbol": "symbol to trade",
                "confidence": 0.0-1.0,
                "reasoning": "detailed explanation of your analysis",
                "key_factors": ["factor1", "factor2", "factor3"],
                "risk_level": "LOW/MEDIUM/HIGH"
            }"""
            
            user_message = f"""
            Market Context:
            {json.dumps(context, indent=2)}
            
            Based on this comprehensive analysis, what is your strategic trading decision?
            Focus on interpreting the data rather than recalculating anything.
            """
            
            response = openai_manager.chat_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ], temperature=self.temperature)
            
            # Parse the response
            if isinstance(response, dict) and "content" in response:
                decision = json.loads(response["content"])
            else:
                decision = response
            
            # Validate decision structure
            required_fields = ["action", "symbol", "confidence", "reasoning"]
            if not all(field in decision for field in required_fields):
                raise ValueError("Invalid decision structure")
            
            return decision
            
        except Exception as e:
            logger.error(f"LLM strategic decision error: {e}")
            return self._fallback_decision(observation)
    
    def _calculate_risk_metrics(self, decision: Dict[str, Any], enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk metrics for the proposed decision."""
        try:
            symbol = decision.get("symbol", "SPY")
            action = decision.get("action", "HOLD")
            
            if action == "HOLD":
                return {"risk_score": 0.0, "max_loss": 0.0, "volatility_risk": 0.0}
            
            # Get historical data for the symbol
            historical_data = enhanced_data.get("historical_data", {}).get(symbol, {})
            
            if not historical_data.get("data"):
                return {"risk_score": 0.5, "max_loss": 5.0, "volatility_risk": 0.3}
            
            prices = historical_data["data"]["prices"]["close"]
            
            # Calculate volatility risk
            volatility_result = calculator.calculate(
                "volatility analysis",
                {"prices": prices}
            )
            
            # Calculate potential drawdown
            drawdown_result = calculator.calculate(
                "drawdown analysis",
                {"prices": prices}
            )
            
            # Calculate correlation with market
            benchmark_data = enhanced_data.get("benchmark_data", {})
            correlation_risk = 0.5  # Default
            
            if benchmark_data.get("data"):
                benchmark_prices = benchmark_data["data"]["prices"]["close"]
                # Align the lengths
                min_length = min(len(prices), len(benchmark_prices))
                correlation_result = calculator.calculate(
                    "correlation analysis",
                    {
                        "series1": prices[-min_length:],
                        "series2": benchmark_prices[-min_length:]
                    }
                )
                correlation_risk = abs(correlation_result.get("result", {}).get("correlation", 0.5))
            
            # Combine risk factors
            volatility_risk = volatility_result.get("result", {}).get("realized_volatility", 0.2)
            max_drawdown = abs(drawdown_result.get("result", {}).get("max_drawdown", 0.1))
            
            # Calculate overall risk score
            risk_score = (volatility_risk * 0.4 + max_drawdown * 0.4 + correlation_risk * 0.2)
            
            return {
                "risk_score": min(risk_score, 1.0),
                "volatility_risk": volatility_risk,
                "max_drawdown": max_drawdown,
                "correlation_risk": correlation_risk,
                "position_size_suggestion": self._calculate_position_size(risk_score)
            }
            
        except Exception as e:
            logger.error(f"Risk calculation error: {e}")
            return {"risk_score": 0.5, "max_loss": 5.0, "volatility_risk": 0.3}
    
    def _calculate_position_size(self, risk_score: float) -> float:
        """Calculate suggested position size based on risk."""
        # Kelly Criterion inspired position sizing
        base_size = 0.05  # 5% of portfolio
        
        if risk_score < 0.2:
            return base_size * 2.0  # Low risk: larger position
        elif risk_score < 0.4:
            return base_size * 1.5  # Medium-low risk
        elif risk_score < 0.6:
            return base_size  # Medium risk: base size
        elif risk_score < 0.8:
            return base_size * 0.5  # High risk: smaller position
        else:
            return base_size * 0.25  # Very high risk: very small position
    
    def _finalize_decision(self, decision: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the decision with risk adjustments."""
        try:
            risk_score = risk_assessment.get("risk_score", 0.5)
            
            # Adjust confidence based on risk
            original_confidence = decision.get("confidence", 0.5)
            risk_adjusted_confidence = original_confidence * (1 - risk_score * 0.5)
            
            # If risk is too high, convert to HOLD
            if risk_score > 0.8:
                decision["action"] = "HOLD"
                decision["reasoning"] += f" [Risk Override: Risk score {risk_score:.2f} too high]"
                risk_adjusted_confidence = 0.3
            
            # Add risk information to decision
            final_decision = {
                **decision,
                "confidence": max(0.1, min(0.95, risk_adjusted_confidence)),
                "risk_assessment": risk_assessment,
                "position_size": risk_assessment.get("position_size_suggestion", 0.05),
                "timestamp": datetime.now().isoformat()
            }
            
            return final_decision
            
        except Exception as e:
            logger.error(f"Decision finalization error: {e}")
            return decision
    
    def _assess_market_conditions(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall market conditions."""
        try:
            market_overview = enhanced_data.get("market_overview", {})
            
            # VIX-based market regime
            vix_level = market_overview.get("vix_level", 20)
            market_sentiment = market_overview.get("market_sentiment", "normal")
            
            # Major indices performance
            indices = market_overview.get("indices", {})
            spy_change = indices.get("SPY", {}).get("daily_change_pct", 0)
            
            conditions = {
                "market_regime": "bull" if spy_change > 1 else "bear" if spy_change < -1 else "neutral",
                "volatility_regime": "high" if vix_level > 25 else "low" if vix_level < 15 else "normal",
                "sentiment": market_sentiment,
                "trend_strength": abs(spy_change),
                "overall_assessment": "favorable" if spy_change > 0 and vix_level < 25 else "unfavorable" if spy_change < -2 else "neutral"
            }
            
            return conditions
            
        except Exception as e:
            logger.error(f"Market condition assessment error: {e}")
            return {"overall_assessment": "neutral", "market_regime": "neutral"}
    
    def _fallback_decision(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decision when LLM is unavailable."""
        sentiment = observation.get("sentiment", "neutral")
        
        if sentiment == "bullish":
            action = "BUY"
            confidence = 0.6
        elif sentiment == "bearish":
            action = "SELL"
            confidence = 0.6
        else:
            action = "HOLD"
            confidence = 0.4
        
        return {
            "action": action,
            "symbol": "SPY",
            "confidence": confidence,
            "reasoning": f"Fallback decision based on {sentiment} sentiment",
            "risk_level": "MEDIUM",
            "position_size": 0.05
        }


# Global instance
enhanced_strategy_agent = EnhancedStrategyAgent()