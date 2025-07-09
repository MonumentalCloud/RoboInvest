"""
Autonomous Alpha Hunter Agent
Scans the world for investment opportunities rather than trading fixed tickers.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from core.config import config
from core.openai_manager import openai_manager
from tools.calculator import calculator
from tools.data_fetcher import data_fetcher
from utils.logger import logger  # type: ignore


class AutonomousAlphaHunter:
    """
    Advanced autonomous agent that discovers alpha opportunities by:
    1. Scanning global events and trends
    2. Identifying potential investment opportunities  
    3. Researching and discovering relevant tickers
    4. Creating dynamic short-term strategies
    """
    
    def __init__(self):
        self.use_llm = bool(config.openai_api_key)
        self.temperature = 0.4
        self.research_memory = []
        self.opportunity_pipeline = []
        
    def hunt_for_alpha(self) -> Dict[str, Any]:
        """
        Main alpha hunting workflow:
        1. Scan global landscape for opportunities
        2. Research and validate opportunities  
        3. Identify specific tickers and strategies
        4. Create actionable investment thesis
        """
        try:
            logger.info("AlphaHunter | Starting autonomous alpha hunting scan")
            
            # Step 1: Global opportunity scanning
            opportunities = self._scan_global_opportunities()
            
            # Step 2: Research and validate top opportunities
            validated_opportunities = self._research_opportunities(opportunities)
            
            # Step 3: Create investment strategies
            strategies = self._create_investment_strategies(validated_opportunities)
            
            # Step 4: Select best opportunity for action
            selected_strategy = self._select_best_strategy(strategies)
            
            logger.info(f"AlphaHunter | Selected strategy: {selected_strategy.get('thesis', 'No strategy')}")
            
            return selected_strategy
            
        except Exception as e:
            logger.error(f"AlphaHunter error: {e}")
            return self._fallback_strategy()
    
    def _scan_global_opportunities(self) -> List[Dict[str, Any]]:
        """
        Scan global trends, events, and market conditions for alpha opportunities.
        Uses LLM to think creatively about potential opportunities.
        """
        if not self.use_llm:
            return self._fallback_opportunities()
        
        try:
            # Get current market context
            market_overview = data_fetcher.get_market_overview()
            
            # LLM prompt for creative opportunity scanning
            scan_prompt = """You are a world-class investment research analyst with access to global markets.
            Your task is to identify 3-5 potential alpha opportunities by analyzing current conditions.
            
            Think creatively about:
            - Emerging trends and disruptions
            - Policy changes and regulations  
            - Seasonal patterns and events
            - Technological breakthroughs
            - Geopolitical developments
            - Market inefficiencies
            - Sector rotations
            
            Current market context:
            """ + json.dumps(market_overview, indent=2) + """
            
            For each opportunity, provide:
            1. Opportunity theme/thesis
            2. Why it might create alpha
            3. Potential time horizon (days/weeks)
            4. Risk factors
            5. How to research further
            
            Respond with JSON array of opportunities:
            [
                {
                    "theme": "opportunity description",
                    "thesis": "why this creates alpha",
                    "timeframe": "days/weeks timeline", 
                    "risk_factors": ["risk1", "risk2"],
                    "research_steps": ["step1", "step2"],
                    "confidence": 0.0-1.0
                }
            ]"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": scan_prompt}
            ], temperature=self.temperature)
            
            # Handle both dict and string response formats
            if isinstance(response, dict):
                content = response.get("content", "[]")
            else:
                content = response or "[]"
            
            try:
                opportunities = json.loads(content)
                
                # Ensure opportunities is a list
                if not isinstance(opportunities, list):
                    logger.warning(f"Opportunities parsing returned non-list: {type(opportunities)}")
                    return self._fallback_opportunities()
                
                logger.info(f"AlphaHunter | Identified {len(opportunities)} potential opportunities")
                return opportunities
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in opportunity scanning: {e}")
                return self._fallback_opportunities()
            
        except Exception as e:
            logger.error(f"Opportunity scanning error: {e}")
            return self._fallback_opportunities()
    
    def _research_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Research and validate the most promising opportunities.
        """
        if not opportunities:
            return []
        
        validated = []
        
        # Take top 3 opportunities by confidence
        top_opportunities = sorted(opportunities, key=lambda x: x.get('confidence', 0), reverse=True)[:3]
        
        for opp in top_opportunities:
            try:
                validation = self._validate_opportunity(opp)
                if validation.get('is_valid', False):
                    validated.append({**opp, **validation})
                    
            except Exception as e:
                logger.error(f"Research error for {opp.get('theme', 'unknown')}: {e}")
                continue
        
        logger.info(f"AlphaHunter | Validated {len(validated)} opportunities")
        return validated
    
    def _validate_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a specific opportunity through research and analysis.
        """
        if not self.use_llm:
            return {"is_valid": True, "tickers": ["SPY"], "strategy": "hold"}
        
        try:
            # LLM research and validation
            validation_prompt = f"""You are validating an investment opportunity. 
            
            Opportunity: {json.dumps(opportunity, indent=2)}
            
            Your task:
            1. Identify 2-3 specific tickers that would benefit from this opportunity
            2. Explain the connection between the opportunity and these tickers
            3. Assess if this opportunity is actionable in the next 1-4 weeks
            4. Rate the opportunity strength (0.0-1.0)
            5. Suggest specific strategy (buy/short/pairs trade/etc.)
            
            Focus on:
            - Specific, tradeable securities (stocks, ETFs, sectors)
            - Clear catalyst timeline
            - Risk/reward assessment
            - Why others might miss this opportunity
            
            Respond in JSON:
            {{
                "is_valid": true/false,
                "tickers": ["TICKER1", "TICKER2"],
                "ticker_rationale": "why these tickers benefit",
                "opportunity_strength": 0.0-1.0,
                "strategy": "specific strategy description",
                "catalysts": ["catalyst1", "catalyst2"],
                "timeline": "specific timeline",
                "risk_assessment": "key risks"
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": validation_prompt}
            ], temperature=0.3)  # Lower temperature for more focused analysis
            
            # Handle both dict and string response formats
            if isinstance(response, dict):
                content = response.get("content", "{}")
            else:
                content = response or "{}"
            
            try:
                validation = json.loads(content)
                
                # Ensure validation is a dictionary
                if not isinstance(validation, dict):
                    logger.warning(f"Validation parsing returned non-dict: {type(validation)}")
                    return {"is_valid": False}
                
                return validation
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in validation: {e}")
                return {"is_valid": False}
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"is_valid": False}
    
    def _create_investment_strategies(self, validated_opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create specific, actionable investment strategies from validated opportunities.
        """
        strategies = []
        
        for opp in validated_opportunities:
            try:
                strategy = self._build_strategy(opp)
                if strategy:
                    strategies.append(strategy)
                    
            except Exception as e:
                logger.error(f"Strategy creation error: {e}")
                continue
        
        return strategies
    
    def _build_strategy(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build a detailed trading strategy from an opportunity.
        """
        if not self.use_llm:
            return None
        
        try:
            tickers = opportunity.get('tickers', [])
            if not tickers:
                return None
            
            # Get fundamental data for the tickers
            ticker_data = {}
            for ticker in tickers[:2]:  # Limit to 2 tickers for analysis
                try:
                    data = data_fetcher.get_historical_data(ticker, period="3mo")
                    if data.get('data'):
                        ticker_data[ticker] = data
                except Exception:
                    continue
            
            # LLM creates detailed strategy
            strategy_prompt = f"""Create a detailed trading strategy for this opportunity:
            
            Opportunity: {json.dumps(opportunity, indent=2)}
            
            Ticker Data: {json.dumps(ticker_data, indent=2)}
            
            Create a strategy with:
            1. Primary ticker to trade
            2. Position type (long/short/pairs)
            3. Entry criteria and timing
            4. Position sizing (% of portfolio)
            5. Stop loss and take profit levels
            6. Time horizon and exit strategy
            7. Why this creates alpha vs market
            
            Respond in JSON:
            {{
                "primary_ticker": "MAIN_TICKER",
                "action": "BUY/SELL/PAIRS",
                "position_size": 0.05-0.15,
                "entry_criteria": "specific entry conditions",
                "stop_loss": percentage,
                "take_profit": percentage,
                "time_horizon": "days/weeks",
                "alpha_thesis": "why this beats market",
                "confidence": 0.0-1.0,
                "risk_level": "LOW/MEDIUM/HIGH"
            }}"""
            
            response = openai_manager.chat_completion([
                {"role": "user", "content": strategy_prompt}
            ], temperature=0.2)
            
            # Handle both dict and string response formats
            if isinstance(response, dict):
                content = response.get("content", "{}")
            else:
                content = response or "{}"
            
            try:
                strategy = json.loads(content)
                
                # Ensure strategy is a dictionary
                if not isinstance(strategy, dict):
                    logger.warning(f"Strategy parsing returned non-dict: {type(strategy)}")
                    return None
                
                # Add opportunity context
                strategy["opportunity_theme"] = opportunity.get("theme", "Unknown")
                strategy["research_basis"] = opportunity.get("thesis", "")
                strategy["catalysts"] = opportunity.get("catalysts", [])
                
                return strategy
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in strategy building: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Strategy building error: {e}")
            return None
    
    def _select_best_strategy(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best strategy from available options.
        """
        if not strategies:
            return self._fallback_strategy()
        
        # Filter out any non-dictionary strategies
        valid_strategies = [s for s in strategies if isinstance(s, dict)]
        
        if not valid_strategies:
            logger.warning("No valid strategies found, using fallback")
            return self._fallback_strategy()
        
        # Score strategies based on confidence, risk-adjusted potential
        def strategy_score(strategy):
            confidence = strategy.get('confidence', 0.5)
            risk_multiplier = {"LOW": 1.2, "MEDIUM": 1.0, "HIGH": 0.8}.get(
                strategy.get('risk_level', 'MEDIUM'), 1.0
            )
            position_size = strategy.get('position_size', 0.05)
            
            return confidence * risk_multiplier * (1 + position_size)
        
        best_strategy = max(valid_strategies, key=strategy_score)
        
        return best_strategy
    
    def _fallback_opportunities(self) -> List[Dict[str, Any]]:
        """Fallback opportunities when LLM is unavailable."""
        return [
            {
                "theme": "Market momentum continuation",
                "thesis": "Current market trends may continue short-term",
                "timeframe": "1-2 weeks",
                "confidence": 0.4,
                "risk_factors": ["Trend reversal"],
                "research_steps": ["Check technical indicators"]
            }
        ]
    
    def _fallback_strategy(self) -> Dict[str, Any]:
        """Fallback strategy when autonomous hunting fails."""
        return {
            "primary_ticker": "SPY",
            "action": "HOLD",
            "position_size": 0.0,
            "confidence": 0.3,
            "alpha_thesis": "Conservative fallback - hold market",
            "opportunity_theme": "Market neutral",
            "time_horizon": "1 week",
            "risk_level": "LOW"
        }


# Global instance
autonomous_alpha_hunter = AutonomousAlphaHunter()