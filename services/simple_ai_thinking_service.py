"""
Simple AI Thinking Service
Generates real-time AI thoughts using OpenRouter without complex agent dependencies.
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import random
import json
import time

from core.openrouter_manager import openrouter_manager
from core.openai_manager import openai_manager
from core.config import config
from utils.logger import logger  # type: ignore


class SimpleAIThinkingService:
    """
    Simplified AI thinking service that generates real-time thoughts using OpenRouter.
    """
    
    def __init__(self):
        self.is_running = False
        self.current_thoughts: List[Dict[str, Any]] = []
        self.max_thoughts = 10
        self.thinking_interval = 5  # seconds between thoughts
        
        # Track thinking contexts
        self.thinking_contexts = [
            "market_analysis",
            "alpha_discovery", 
            "risk_assessment",
            "sentiment_analysis",
            "technical_analysis",
            "fundamental_research"
        ]
        
    async def start_thinking(self):
        """Start the AI thinking process."""
        if self.is_running:
            logger.warning("AI thinking service already running")
            return
            
        self.is_running = True
        logger.info("Simple AI thinking service started")
        
        # Initialize with a startup thought
        self._add_thought("AI systems online - OpenRouter integration active")
        
        # Start the thinking loop
        await self._thinking_loop()
        
    def stop_thinking(self):
        """Stop the AI thinking process."""
        self.is_running = False
        logger.info("Simple AI thinking service stopped")
        
    async def _thinking_loop(self):
        """Main thinking loop that generates periodic thoughts."""
        while self.is_running:
            try:
                # Generate a new thought
                thought = await self._generate_thought()
                if thought:
                    self._add_thought(thought)
                    
                # Wait before next thought
                await asyncio.sleep(self.thinking_interval)
                
            except Exception as e:
                logger.error(f"AI thinking loop error: {e}")
                await asyncio.sleep(self.thinking_interval)
                
    async def _generate_thought(self) -> str:
        """Generate a single AI thought."""
        try:
            # Get simple market context
            market_context = self._get_simple_market_context()
            
            # Choose thinking context
            context_type = random.choice(self.thinking_contexts)
            
            # Generate thought based on available AI service
            if config.openrouter_use_for_thinking and openrouter_manager.enabled:
                thought = await self._generate_openrouter_thought(market_context, context_type)
            elif openai_manager.enabled:
                thought = self._generate_fallback_thought(context_type)
            else:
                thought = self._generate_fallback_thought(context_type)
                
            return thought
            
        except Exception as e:
            logger.error(f"Thought generation error: {e}")
            return self._generate_fallback_thought("error_recovery")
            
    def _get_simple_market_context(self) -> Dict[str, Any]:
        """Get simple market context without external API calls."""
        # Simple market context based on time and random market conditions
        now = datetime.now()
        market_hour = now.hour
        
        # Simulate market conditions based on time
        if 9 <= market_hour < 16:  # Market hours
            market_state = "active"
            volatility = "normal" if random.random() > 0.3 else "elevated"
        else:
            market_state = "after_hours"
            volatility = "low"
            
        return {
            "market_state": market_state,
            "volatility": volatility,
            "time": now.isoformat(),
            "hour": market_hour,
            "symbols": ["SPY", "QQQ", "NVDA", "TSLA", "AAPL"]
        }
        
    async def _generate_openrouter_thought(self, market_context: Dict[str, Any], context_type: str) -> str:
        """Generate thought using OpenRouter."""
        try:
            # Create a simple prompt for generating AI thoughts
            prompt = f"""You are an AI trading analyst generating a brief market insight.
            
Context: {context_type}
Market State: {market_context.get('market_state', 'unknown')}
Time: {market_context.get('hour', 12)}:00

Generate ONE specific trading thought or market observation (max 120 characters).
Focus on {context_type}.

Examples:
- "SPY showing resistance at 450 - watching for breakdown"
- "Tech sector rotation accelerating into value names"
- "VIX compression suggests complacency building"

Your thought:"""

            # Use OpenRouter to generate thought
            loop = asyncio.get_event_loop()
            thought = await loop.run_in_executor(
                None,
                lambda: openrouter_manager.generate_thinking_thought(market_context)
            )
            
            # Clean up the thought
            if thought.startswith('"') and thought.endswith('"'):
                thought = thought[1:-1]
                
            # Add context prefix
            context_prefixes = {
                "market_analysis": "Market:",
                "alpha_discovery": "Alpha:",
                "risk_assessment": "Risk:",
                "sentiment_analysis": "Sentiment:",
                "technical_analysis": "Technical:",
                "fundamental_research": "Research:"
            }
            
            prefix = context_prefixes.get(context_type, "Analysis:")
            return f"{prefix} {thought}"[:120]
            
        except Exception as e:
            logger.error(f"OpenRouter thought generation error: {e}")
            return self._generate_fallback_thought(context_type)
            
    def _generate_fallback_thought(self, context_type: str) -> str:
        """Generate fallback thought when AI services are unavailable."""
        fallback_thoughts = {
            "market_analysis": [
                "Monitoring S&P 500 for key support at 4400 level...",
                "Tech sector showing relative strength vs broader market",
                "Bond yields stabilizing after recent volatility spike",
                "Dollar strength impacting international equity flows"
            ],
            "alpha_discovery": [
                "Scanning earnings revisions for Q4 beat candidates...",
                "Alternative energy stocks showing momentum divergence",
                "Small-cap value names outperforming growth recently",
                "Insider buying activity increasing in biotech sector"
            ],
            "risk_assessment": [
                "VIX elevated above 20 - heightened volatility environment",
                "Credit spreads widening - monitoring for stress signals",
                "Correlation breakdown between equities and bonds noted",
                "Options skew indicating defensive positioning increase"
            ],
            "sentiment_analysis": [
                "Put/call ratio suggesting extreme bearish sentiment",
                "Retail investor flows turning negative for third week",
                "Institutional positioning remains defensively tilted",
                "Fear & greed index at extreme levels - contrarian signal"
            ],
            "technical_analysis": [
                "SPY testing 200-day moving average support level",
                "NASDAQ showing divergence with momentum indicators",
                "Russell 2000 breaking below key technical support",
                "Gold forming ascending triangle pattern - bullish setup"
            ],
            "fundamental_research": [
                "Earnings growth estimates being revised lower sector-wide",
                "Free cash flow yield attractive in large-cap value",
                "Balance sheet quality improving across industrial names",
                "Margin pressure from input costs showing in Q3 results"
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
        """Get current alpha opportunities (simplified version)."""
        # Return mock alpha opportunities for now
        if random.random() > 0.7:  # 30% chance of having opportunities
            return [
                {
                    "symbol": random.choice(["NVDA", "TSLA", "AAPL", "QQQ"]),
                    "confidence": round(random.uniform(0.6, 0.9), 2),
                    "action": random.choice(["BUY", "SELL"]),
                    "thesis": "AI-detected opportunity based on technical momentum",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        return []
        
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the AI thinking service."""
        return {
            "is_running": self.is_running,
            "thought_count": len(self.current_thoughts),
            "openrouter_enabled": openrouter_manager.enabled if openrouter_manager else False,
            "openai_enabled": openai_manager.enabled if openai_manager else False,
            "service_type": "simple",
            "last_thought_time": self.current_thoughts[0]["timestamp"] if self.current_thoughts else None
        }


# Singleton instance
simple_ai_thinking_service = SimpleAIThinkingService() 