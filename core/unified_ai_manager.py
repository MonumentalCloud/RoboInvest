"""
Unified AI Manager
Provides a single interface for AI operations, using OpenRouter as primary with OpenAI as fallback.
"""

from __future__ import annotations

from typing import Any, Dict, List
import json
from datetime import datetime

from core.openrouter_manager import openrouter_manager
from core.openai_manager import openai_manager
from core.config import config
from utils.logger import logger  # type: ignore


class UnifiedAIManager:
    """
    Unified AI manager that routes requests to the best available AI service.
    Priority: OpenRouter (free/cheap) -> OpenAI (as fallback)
    """
    
    def __init__(self):
        self.primary_service = "openrouter"
        self.fallback_service = "openai"
        
    def chat_completion(self, messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 150) -> Dict[str, Any]:
        """
        Generate chat completion using the best available AI service.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict with content, model, and usage info
        """
        
        # Try OpenRouter first (primary service)
        if openrouter_manager.enabled:
            try:
                response = openrouter_manager.chat_completion(messages, temperature)
                
                logger.info(f"UnifiedAI | Using OpenRouter ({openrouter_manager.model})")
                return response
                
            except Exception as e:
                logger.warning(f"UnifiedAI | OpenRouter failed: {e}, falling back to OpenAI")
        
        # Fallback to OpenAI (but avoid JSON mode for simple chat)
        if openai_manager.enabled:
            try:
                # Convert to OpenAI compatible format if needed
                openai_messages = []
                for msg in messages:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        openai_messages.append({
                            "role": str(msg["role"]),
                            "content": str(msg["content"])
                        })
                
                # Use a custom OpenAI call without JSON mode for simple responses
                import openai
                import json
                
                client_response = openai.chat.completions.create(  # type: ignore
                    model=openai_manager.primary_model,
                    messages=openai_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Track usage manually
                usage = client_response.usage
                total_tokens = usage.total_tokens if usage else 0
                from core.openai_manager import _usage_tracker
                _usage_tracker.add(openai_manager.primary_model, total_tokens)
                
                response = {
                    "content": client_response.choices[0].message.content,
                    "model": openai_manager.primary_model,
                    "usage": _usage_tracker.summary(),
                }
                
                logger.info(f"UnifiedAI | Using OpenAI ({openai_manager.primary_model})")
                return response
                
            except Exception as e:
                logger.error(f"UnifiedAI | Both OpenRouter and OpenAI failed: {e}")
                raise RuntimeError("All AI services unavailable")
        
        raise RuntimeError("No AI services configured or available")
    
    def generate_json_response(self, messages: List[Dict[str, Any]], temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate a JSON response from the AI service.
        Handles JSON parsing and validation.
        """
        try:
            response = self.chat_completion(messages, temperature)
            content = response.get("content", "{}")
            
            # Try to parse as JSON
            try:
                json_data = json.loads(content)
                return json_data
            except json.JSONDecodeError as e:
                logger.warning(f"UnifiedAI | JSON parse error: {e}, content: {content}")
                # Try to extract JSON from content if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group())
                        return json_data
                    except:
                        pass
                
                # Return empty dict if JSON parsing fails
                return {}
                
        except Exception as e:
            logger.error(f"UnifiedAI | JSON response generation failed: {e}")
            return {}
    
    def generate_simple_response(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a simple text response from a single prompt.
        """
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_completion(messages, temperature)
            return response.get("content", "").strip()
            
        except Exception as e:
            logger.error(f"UnifiedAI | Simple response generation failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if any AI service is available."""
        return openrouter_manager.enabled or openai_manager.enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all AI services."""
        return {
            "primary_service": self.primary_service,
            "fallback_service": self.fallback_service,
            "openrouter_enabled": openrouter_manager.enabled,
            "openrouter_usage": openrouter_manager.usage() if openrouter_manager.enabled else {},
            "openai_enabled": openai_manager.enabled,
            "openai_usage": openai_manager.usage() if openai_manager.enabled else {},
            "available": self.is_available()
        }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get combined usage summary from all services."""
        summary = {
            "total_cost": 0.0,
            "services": {}
        }
        
        if openrouter_manager.enabled:
            or_usage = openrouter_manager.usage()
            summary["services"]["openrouter"] = or_usage
            summary["total_cost"] += or_usage.get("cost_usd", 0)
        
        if openai_manager.enabled:
            ai_usage = openai_manager.usage()
            summary["services"]["openai"] = ai_usage
            summary["total_cost"] += ai_usage.get("cost_usd", 0)
        
        summary["total_cost"] = round(summary["total_cost"], 4)
        return summary


# Singleton instance
unified_ai_manager = UnifiedAIManager() 