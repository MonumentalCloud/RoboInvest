"""
AI Thinking Service
Generates real-time AI thoughts based on market data and autonomous alpha hunting.
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import random
import json
from concurrent.futures import ThreadPoolExecutor
import time

from core.openrouter_manager import openrouter_manager
from core.openai_manager import openai_manager
from core.config import config
from core.polygon_client import polygon_client
from agents.autonomous_alpha_hunter import AutonomousAlphaHunter
from agents.world_monitor import WorldMonitorAgent
from utils.logger import logger  # type: ignore


class AIThinkingService:
    """
    Service that generates real-time AI thoughts based on:
    1. Current market conditions
    2. Autonomous alpha hunting processes
    3. World monitor observations
    4. Real-time market data
    """
    
    def __init__(self):
        self.is_running = False
        self.current_thoughts: List[Dict[str, Any]] = []
        self.max_thoughts = 10
        self.thinking_interval = 3  # seconds between thoughts
        self.last_market_update = None
        self.market_cache = {}
        self.cache_duration = 30  # seconds
        
        # Initialize components
        self.alpha_hunter = AutonomousAlphaHunter()
        self.world_monitor = WorldMonitorAgent()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Track thinking contexts
        self.thinking_contexts = [
            "market_analysis",
            "alpha_discovery", 
            "risk_assessment",
            "sentiment_analysis",
            "technical_analysis",
            "fundamental_research",
            "correlation_analysis",
            "flow_analysis"
        ]
        
        # Track alpha hunting cycles
        self.last_alpha_hunt = None
        self.alpha_hunt_interval = 120  # Run alpha hunt every 2 minutes
        self.current_alpha_opportunities = []
        
    async def start_thinking(self):
        """Start the AI thinking process."""
        if self.is_running:
            logger.warning("AI thinking service already running")
            return
            
        self.is_running = True
        logger.info("AI thinking service started")
        
        # Initialize with a startup thought
        self._add_thought("AI research systems online - beginning market analysis...")
        
        # Start the thinking loop
        await self._thinking_loop()
        
    def stop_thinking(self):
        """Stop the AI thinking process."""
        self.is_running = False
        logger.info("AI thinking service stopped")
        
    async def _thinking_loop(self):
        """Main thinking loop that generates periodic thoughts."""
        while self.is_running:
            try:
                # Check if we should run alpha hunting cycle
                await self._check_alpha_hunting_cycle()
                
                # Generate a new thought
                thought = await self._generate_thought()
                if thought:
                    self._add_thought(thought)
                    
                # Wait before next thought
                await asyncio.sleep(self.thinking_interval)
                
            except Exception as e:
                logger.error(f"AI thinking loop error: {e}")
                await asyncio.sleep(self.thinking_interval)
                
    async def _check_alpha_hunting_cycle(self):
        """Check if it's time to run an alpha hunting cycle."""
        now = time.time()
        
        # Check if enough time has passed since last alpha hunt
        if (self.last_alpha_hunt is None or 
            now - self.last_alpha_hunt >= self.alpha_hunt_interval):
            
            try:
                self._add_thought("Initiating autonomous alpha hunting cycle...")
                
                # Run alpha hunting in executor to avoid blocking
                loop = asyncio.get_event_loop()
                alpha_result = await loop.run_in_executor(
                    self.executor,
                    self.alpha_hunter.hunt_for_alpha
                )
                
                # Update last hunt time
                self.last_alpha_hunt = now
                
                # Process alpha hunting results
                if alpha_result and alpha_result.get('confidence', 0) > 0.5:
                    symbol = alpha_result.get('primary_ticker', 'Unknown')
                    action = alpha_result.get('action', 'HOLD')
                    confidence = alpha_result.get('confidence', 0)
                    
                    self.current_alpha_opportunities = [alpha_result]
                    
                    thought = f"Alpha opportunity detected: {action} {symbol} with {confidence*100:.0f}% confidence"
                    self._add_thought(thought)
                    
                    # Add detailed analysis thought
                    thesis = alpha_result.get('alpha_thesis', '')
                    if thesis:
                        detail_thought = f"Analysis: {thesis[:100]}..." if len(thesis) > 100 else f"Analysis: {thesis}"
                        self._add_thought(detail_thought)
                        
                else:
                    self._add_thought("Alpha hunting cycle complete - no high-confidence opportunities found")
                    
            except Exception as e:
                logger.error(f"Alpha hunting cycle error: {e}")
                self._add_thought("Alpha hunting cycle encountered an error - continuing analysis...")
                
    async def _generate_thought(self) -> str:
        """Generate a single AI thought based on current market conditions."""
        try:
            # Get current market context
            market_context = await self._get_market_context()
            
            # Choose thinking context randomly, but bias towards alpha discovery if we have opportunities
            if self.current_alpha_opportunities and random.random() < 0.4:
                context_type = "alpha_discovery"
            else:
                context_type = random.choice(self.thinking_contexts)
            
            # Add alpha opportunities to market context
            if self.current_alpha_opportunities:
                market_context["current_alpha_opportunities"] = self.current_alpha_opportunities
            
            # Generate thought based on context
            if config.openrouter_use_for_thinking and openrouter_manager.enabled:
                thought = await self._generate_openrouter_thought(market_context, context_type)
            elif openai_manager.enabled:
                thought = await self._generate_openai_thought(market_context, context_type)
            else:
                thought = self._generate_fallback_thought(context_type)
                
            return thought
            
        except Exception as e:
            logger.error(f"Thought generation error: {e}")
            return self._generate_fallback_thought("error_recovery")
            
    async def _get_market_context(self) -> Dict[str, Any]:
        """Get current market context with caching."""
        now = time.time()
        
        # Check cache
        if (self.last_market_update and 
            now - self.last_market_update < self.cache_duration and
            self.market_cache):
            return self.market_cache
            
        try:
            # Get fresh market data
            context = {}
            
            # Get basic market data
            symbols = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
            for symbol in symbols:
                try:
                    quote = polygon_client.quote(symbol)
                    if quote:
                        current_price = quote.get("c", 0)
                        prev_close = quote.get("pc", 0)
                        change = current_price - prev_close if prev_close else 0
                        change_pct = (change / prev_close * 100) if prev_close else 0
                        
                        context[symbol] = {
                            "price": current_price,
                            "change": change,
                            "change_pct": change_pct,
                        }
                except:
                    continue
            
            # Get world monitor data (async)
            try:
                world_data = await self.world_monitor.observe()
                context["market_sentiment"] = world_data.get("sentiment", "neutral")
                context["market_overview"] = world_data.get("market", {})
            except Exception as e:
                logger.warning(f"World monitor error: {e}")
                context["market_sentiment"] = "neutral"
                
            # Cache the results
            self.market_cache = context
            self.last_market_update = now
            
            return context
            
        except Exception as e:
            logger.error(f"Market context error: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
            
    async def _generate_openrouter_thought(self, market_context: Dict[str, Any], context_type: str) -> str:
        """Generate thought using OpenRouter."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            thought = await loop.run_in_executor(
                self.executor,
                lambda: openrouter_manager.generate_thinking_thought(market_context)
            )
            
            # Add context prefix
            context_prefixes = {
                "market_analysis": "Market Analysis:",
                "alpha_discovery": "Alpha Discovery:",
                "risk_assessment": "Risk Assessment:",
                "sentiment_analysis": "Sentiment Analysis:",
                "technical_analysis": "Technical Analysis:",
                "fundamental_research": "Fundamental Research:",
                "correlation_analysis": "Correlation Analysis:",
                "flow_analysis": "Flow Analysis:"
            }
            
            prefix = context_prefixes.get(context_type, "Analysis:")
            return f"{prefix} {thought}"
            
        except Exception as e:
            logger.error(f"OpenRouter thought generation error: {e}")
            return self._generate_fallback_thought(context_type)
            
    async def _generate_openai_thought(self, market_context: Dict[str, Any], context_type: str) -> str:
        """Generate thought using OpenAI as backup."""
        try:
            prompt = f"""Generate a brief AI trading thought for {context_type}.
            
            Market Context: {json.dumps(market_context, indent=2)}
            
            Generate one specific, actionable thought (max 120 chars):"""
            
            messages = [
                {"role": "system", "content": "You are an AI trading analyst."},
                {"role": "user", "content": prompt}
            ]
            
            # Run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: openai_manager.chat_completion(messages, temperature=0.8)
            )
            
            thought = response.get("content", "").strip()
            if thought.startswith('"') and thought.endswith('"'):
                thought = thought[1:-1]
                
            return thought[:120] if len(thought) > 120 else thought
            
        except Exception as e:
            logger.error(f"OpenAI thought generation error: {e}")
            return self._generate_fallback_thought(context_type)
            
    def _generate_fallback_thought(self, context_type: str) -> str:
        """Generate fallback thought when AI services are unavailable."""
        fallback_thoughts = {
            "market_analysis": [
                "Analyzing market microstructure for arbitrage opportunities...",
                "Monitoring cross-asset correlations for regime changes...",
                "Evaluating sector rotation patterns and momentum signals...",
                "Tracking institutional order flow for positioning insights..."
            ],
            "alpha_discovery": [
                "Scanning alternative data sources for alpha opportunities...",
                "Identifying earnings revision patterns across sectors...",
                "Analyzing options flow for directional bias signals...",
                "Researching ESG momentum in clean energy sectors..."
            ],
            "risk_assessment": [
                "Evaluating portfolio delta exposure and hedging needs...",
                "Monitoring VIX term structure for volatility signals...",
                "Assessing correlation breakdown risks across positions...",
                "Calculating maximum drawdown scenarios for risk management..."
            ],
            "sentiment_analysis": [
                "Processing social sentiment data for contrarian signals...",
                "Analyzing insider trading patterns and SEC filings...",
                "Monitoring fund flows for institutional positioning...",
                "Tracking earnings guidance revisions and analyst sentiment..."
            ],
            "technical_analysis": [
                "Identifying key support/resistance levels across major indices...",
                "Analyzing volume patterns for institutional accumulation...",
                "Monitoring breakout setups in high-conviction names...",
                "Evaluating momentum divergence signals in sector leaders..."
            ],
            "fundamental_research": [
                "Analyzing Q4 earnings guidance and management commentary...",
                "Evaluating free cash flow growth across growth sectors...",
                "Researching competitive positioning in emerging markets...",
                "Assessing balance sheet strength for defensive positioning..."
            ],
            "correlation_analysis": [
                "Detecting unusual correlation patterns in equity sectors...",
                "Monitoring bond-equity correlation for regime identification...",
                "Analyzing currency impact on multinational earnings...",
                "Tracking commodity exposure across industrial names..."
            ],
            "flow_analysis": [
                "Analyzing dark pool activity in mega-cap technology...",
                "Monitoring ETF creation/redemption patterns...",
                "Tracking unusual options activity across sectors...",
                "Evaluating foreign investment flows into US markets..."
            ]
        }
        
        thoughts = fallback_thoughts.get(context_type, fallback_thoughts["market_analysis"])
        return random.choice(thoughts)
        
    def _add_thought(self, thought: str):
        """Add a new thought to the thinking process."""
        timestamp = datetime.now().isoformat()
        time_str = datetime.now().strftime("%H:%M:%S")
        
        new_thought = {
            "time": time_str,
            "thought": thought,
            "timestamp": timestamp
        }
        
        # Add to front of list
        self.current_thoughts.insert(0, new_thought)
        
        # Limit to max thoughts
        if len(self.current_thoughts) > self.max_thoughts:
            self.current_thoughts = self.current_thoughts[:self.max_thoughts]
            
        logger.info(f"AI Thought: {thought}")
        
    def get_current_thoughts(self) -> List[Dict[str, Any]]:
        """Get the current list of AI thoughts."""
        return self.current_thoughts.copy()
        
    def get_current_alpha_opportunities(self) -> List[Dict[str, Any]]:
        """Get current alpha opportunities discovered by the AI."""
        return self.current_alpha_opportunities.copy()
        
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the AI thinking service."""
        return {
            "is_running": self.is_running,
            "thought_count": len(self.current_thoughts),
            "last_update": self.last_market_update,
            "last_alpha_hunt": self.last_alpha_hunt,
            "alpha_opportunities_count": len(self.current_alpha_opportunities),
            "openrouter_enabled": openrouter_manager.enabled,
            "openai_enabled": openai_manager.enabled,
            "market_cache_size": len(self.market_cache)
        }


# Singleton instance
ai_thinking_service = AIThinkingService() 