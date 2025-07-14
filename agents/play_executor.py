from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from enum import Enum

from core.openai_manager import openai_manager
from core.structured_order import StructuredOrder, OrderStatus, OrderManager
from core.alpaca_client import alpaca_client
from agents.enhanced_trade_executor import enhanced_trade_executor
from core.play_reporting import play_reporting
from utils.logger import logger


class PlayStatus(Enum):
    """Status of a trading play execution"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERVENED = "intervened"
    ADAPTED = "adapted"


class InterventionType(Enum):
    """Types of interventions the play executor can make"""
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"
    TIMEOUT = "timeout"
    MARKET_CONDITION_CHANGE = "market_condition_change"
    NEWS_IMPACT = "news_impact"
    TECHNICAL_BREAKDOWN = "technical_breakdown"
    FUNDAMENTAL_CHANGE = "fundamental_change"
    VOLUME_ANOMALY = "volume_anomaly"
    CORRELATION_BREAKDOWN = "correlation_breakdown"
    SECTOR_ROTATION = "sector_rotation"


class PlayExecutorAgent:
    """Advanced agent that executes complex trading plays with intelligent intervention"""
    
    def __init__(self):
        self.active_plays: Dict[str, Dict[str, Any]] = {}
        self.play_history: List[Dict[str, Any]] = []
        self.intervention_thresholds = {
            "max_drawdown": 0.15,  # 15% max drawdown
            "timeout_hours": 24,   # 24 hour timeout
            "volume_threshold": 0.5,  # 50% volume drop
            "correlation_threshold": 0.3,  # 30% correlation breakdown
            "news_sentiment_threshold": -0.5,  # Negative sentiment threshold
            "technical_breakdown_threshold": 0.1  # 10% technical breakdown
        }
    
    def create_play_from_natural_language(self, 
                                         play_description: str,
                                         symbol: str,
                                         initial_quantity: int,
                                         market_data: Dict[str, Any],
                                         news_data: List[str],
                                         confidence_score: float = 0.7) -> Dict[str, Any]:
        """Create a structured play from natural language description"""
        
        # Parse the natural language play
        parsed_play = self._parse_natural_language_play(play_description, symbol)
        
        # Create the initial order
        order = enhanced_trade_executor.create_structured_trade(
            symbol=symbol,
            side=parsed_play["side"],
            quantity=initial_quantity,
            market_data=market_data,
            news_data=news_data,
            play_title=parsed_play["title"],
            play_description=parsed_play["description"],
            confidence_score=confidence_score,
            priority=parsed_play.get("priority", 5),
            tags=parsed_play.get("tags", []),
            notes=parsed_play.get("notes", "")
        )
        
        # Create play execution plan
        play = {
            "play_id": f"play_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "order_id": order.order_id,
            "symbol": symbol,
            "status": PlayStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "natural_language_description": play_description,
            "parsed_play": parsed_play,
            "execution_plan": self._create_execution_plan(parsed_play, order),
            "monitoring_conditions": self._create_monitoring_conditions(parsed_play),
            "intervention_history": [],
            "performance_metrics": {
                "entry_price": market_data.get("price", 0),
                "current_price": market_data.get("price", 0),
                "max_profit": 0,
                "max_drawdown": 0,
                "time_in_play": 0,
                "volume_trend": 0,
                "sentiment_trend": 0
            },
            "adaptation_history": []
        }
        
        self.active_plays[play["play_id"]] = play
        
        # Log to central reporting system
        play_reporting.log_play_creation(play)
        
        logger.info(f"Created play {play['play_id']} for {symbol}: {parsed_play['title']}")
        
        return play
    
    def _parse_natural_language_play(self, description: str, symbol: str) -> Dict[str, Any]:
        """Parse natural language play description into structured format"""
        
        if openai_manager.enabled:
            return self._llm_parse_play(description, symbol)
        else:
            return self._heuristic_parse_play(description, symbol)
    
    def _llm_parse_play(self, description: str, symbol: str) -> Dict[str, Any]:
        """Use LLM to parse natural language play"""
        
        prompt = f"""
You are a professional trading play analyst. Parse the following natural language trading play into a structured format.

Play Description: {description}
Symbol: {symbol}

Extract and structure the following information:
1. Play title (concise)
2. Side (buy/sell)
3. Entry strategy
4. Exit strategy
5. Key catalysts/triggers
6. Risk factors
7. Success criteria
8. Timeframe
9. Priority (1-10)
10. Tags (relevant categories)

Respond in JSON format with these exact keys: title, side, entry_strategy, exit_strategy, catalysts, risks, success_criteria, timeframe, priority, tags, description
"""
        
        try:
            result = openai_manager.chat_completion([
                {"role": "system", "content": "You are a professional trading play analyst. Provide structured analysis."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            parsed = json.loads(result["content"] or "{}")
            
            # Validate and set defaults
            parsed.setdefault("side", "buy")
            parsed.setdefault("priority", 5)
            parsed.setdefault("tags", [])
            parsed.setdefault("timeframe", "1-5 days")
            
            return parsed
            
        except Exception as e:
            logger.warning(f"LLM play parsing failed: {e}, using heuristic")
            return self._heuristic_parse_play(description, symbol)
    
    def _heuristic_parse_play(self, description: str, symbol: str) -> Dict[str, Any]:
        """Heuristic parsing of natural language play"""
        
        description_lower = description.lower()
        
        # Determine side
        side = "buy"
        if any(word in description_lower for word in ["sell", "short", "bearish", "down", "decline"]):
            side = "sell"
        
        # Extract key information
        title = f"{symbol} {side.upper()} Play"
        if "momentum" in description_lower:
            title += " - Momentum"
        elif "breakout" in description_lower:
            title += " - Breakout"
        elif "earnings" in description_lower:
            title += " - Earnings"
        
        # Determine timeframe
        timeframe = "1-5 days"
        if "swing" in description_lower:
            timeframe = "1-2 weeks"
        elif "long" in description_lower or "position" in description_lower:
            timeframe = "1-3 months"
        
        # Extract tags
        tags = []
        if "momentum" in description_lower:
            tags.append("momentum")
        if "breakout" in description_lower:
            tags.append("breakout")
        if "earnings" in description_lower:
            tags.append("earnings")
        if "technical" in description_lower:
            tags.append("technical")
        if "fundamental" in description_lower:
            tags.append("fundamental")
        
        return {
            "title": title,
            "side": side,
            "entry_strategy": f"Market order based on {description[:50]}...",
            "exit_strategy": "Stop loss and take profit based on risk assessment",
            "catalysts": ["Market analysis", "Technical indicators"],
            "risks": ["Market volatility", "Unexpected news"],
            "success_criteria": ["Price moves in expected direction", "Volume confirmation"],
            "timeframe": timeframe,
            "priority": 5,
            "tags": tags,
            "description": description
        }
    
    def _create_execution_plan(self, parsed_play: Dict[str, Any], order: StructuredOrder) -> Dict[str, Any]:
        """Create detailed execution plan for the play"""
        
        return {
            "phases": [
                {
                    "phase": "entry",
                    "description": "Initial position entry",
                    "conditions": ["Market order executed"],
                    "next_phase": "monitoring"
                },
                {
                    "phase": "monitoring",
                    "description": "Active monitoring and adjustment",
                    "conditions": ["Position active", "Within timeframe"],
                    "next_phase": "exit"
                },
                {
                    "phase": "exit",
                    "description": "Position exit based on criteria",
                    "conditions": ["Stop loss hit", "Take profit hit", "Time expired", "Manual exit"]
                }
            ],
            "adjustments": [
                {
                    "trigger": "positive_momentum",
                    "action": "add_position",
                    "conditions": ["Price up 5%", "Volume increasing", "Positive news"]
                },
                {
                    "trigger": "negative_momentum",
                    "action": "reduce_position",
                    "conditions": ["Price down 3%", "Volume decreasing", "Negative news"]
                }
            ],
            "exit_triggers": [
                {
                    "type": "stop_loss",
                    "condition": "Price hits stop loss",
                    "action": "immediate_exit"
                },
                {
                    "type": "take_profit",
                    "condition": "Price hits take profit",
                    "action": "immediate_exit"
                },
                {
                    "type": "timeout",
                    "condition": "Timeframe expired",
                    "action": "evaluate_and_exit"
                },
                {
                    "type": "catalyst_failure",
                    "condition": "Expected catalyst doesn't materialize",
                    "action": "evaluate_and_exit"
                }
            ]
        }
    
    def _create_monitoring_conditions(self, parsed_play: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring conditions for the play"""
        
        return {
            "price_monitoring": {
                "track_entry_price": True,
                "track_high_low": True,
                "track_momentum": True,
                "alert_thresholds": {
                    "profit_target": 0.10,  # 10% profit
                    "stop_loss": 0.05,      # 5% loss
                    "momentum_threshold": 0.03  # 3% move
                }
            },
            "volume_monitoring": {
                "track_volume_trend": True,
                "track_volume_spikes": True,
                "alert_thresholds": {
                    "volume_drop": 0.5,     # 50% volume drop
                    "volume_spike": 2.0     # 200% volume spike
                }
            },
            "news_monitoring": {
                "track_sentiment": True,
                "track_catalyst_news": True,
                "alert_thresholds": {
                    "negative_sentiment": -0.5,
                    "positive_sentiment": 0.5
                }
            },
            "technical_monitoring": {
                "track_support_resistance": True,
                "track_breakouts": True,
                "track_correlation": True,
                "alert_thresholds": {
                    "support_break": 0.02,  # 2% below support
                    "resistance_break": 0.02,  # 2% above resistance
                    "correlation_break": 0.3   # 30% correlation breakdown
                }
            }
        }
    
    def monitor_and_execute_play(self, play_id: str, current_market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and execute a trading play with intelligent intervention"""
        
        if play_id not in self.active_plays:
            return {"error": "Play not found"}
        
        play = self.active_plays[play_id]
        order = enhanced_trade_executor.order_manager.get_order(play["order_id"])
        
        if not order:
            return {"error": "Order not found"}
        
        # If play is already intervened or completed, return current status
        if play["status"] in [PlayStatus.INTERVENED, PlayStatus.COMPLETED, PlayStatus.FAILED]:
            return {
                "status": "play_completed",
                "play_status": play["status"].value,
                "performance": play["performance_metrics"]
            }
        
        # Update performance metrics
        self._update_performance_metrics(play, current_market_data)
        
        # Log performance update to central reporting
        play_reporting.log_performance_update(play_id, play["performance_metrics"])
        
        # Check for interventions
        intervention = self._check_for_intervention(play, order, current_market_data)
        
        if intervention:
            self._execute_intervention(play, order, intervention, current_market_data)
            return {
                "status": "intervention_executed",
                "intervention": intervention,
                "play_status": play["status"].value
            }
        
        # Check for adaptations
        adaptation = self._check_for_adaptation(play, order, current_market_data)
        
        if adaptation:
            self._execute_adaptation(play, order, adaptation, current_market_data)
            return {
                "status": "adaptation_executed",
                "adaptation": adaptation,
                "play_status": play["status"].value
            }
        
        # Check for completion
        if self._check_play_completion(play, order, current_market_data):
            self._complete_play(play, order)
            return {
                "status": "play_completed",
                "play_status": play["status"].value
            }
        
        return {
            "status": "play_active",
            "play_status": play["status"].value,
            "performance": play["performance_metrics"]
        }
    
    def _update_performance_metrics(self, play: Dict[str, Any], market_data: Dict[str, Any]) -> None:
        """Update performance metrics for the play"""
        
        current_price = market_data.get("price", 0)
        entry_price = play["performance_metrics"]["entry_price"]
        
        if entry_price > 0:
            # Calculate P&L
            if play["parsed_play"]["side"] == "buy":
                pnl_pct = (current_price - entry_price) / entry_price
            else:
                pnl_pct = (entry_price - current_price) / entry_price
            
            # Update metrics
            play["performance_metrics"]["current_price"] = current_price
            play["performance_metrics"]["pnl_pct"] = pnl_pct
            
            # Track max profit and drawdown
            if pnl_pct > play["performance_metrics"]["max_profit"]:
                play["performance_metrics"]["max_profit"] = pnl_pct
            
            if pnl_pct < play["performance_metrics"]["max_drawdown"]:
                play["performance_metrics"]["max_drawdown"] = pnl_pct
            
            # Update time in play
            time_in_play = (datetime.utcnow() - play["created_at"]).total_seconds() / 3600
            play["performance_metrics"]["time_in_play"] = time_in_play
    
    def _check_for_intervention(self, play: Dict[str, Any], order: StructuredOrder, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if intervention is needed"""
        
        # Check stop loss
        if order.stop_conditions.stop_loss_price:
            current_price = market_data.get("price", 0)
            if play["parsed_play"]["side"] == "buy" and current_price <= order.stop_conditions.stop_loss_price:
                return {
                    "type": InterventionType.STOP_LOSS_HIT,
                    "reason": f"Price {current_price} hit stop loss {order.stop_conditions.stop_loss_price}",
                    "action": "exit_position"
                }
            elif play["parsed_play"]["side"] == "sell" and current_price >= order.stop_conditions.stop_loss_price:
                return {
                    "type": InterventionType.STOP_LOSS_HIT,
                    "reason": f"Price {current_price} hit stop loss {order.stop_conditions.stop_loss_price}",
                    "action": "exit_position"
                }
        
        # Check take profit
        if order.stop_conditions.take_profit_price:
            current_price = market_data.get("price", 0)
            if play["parsed_play"]["side"] == "buy" and current_price >= order.stop_conditions.take_profit_price:
                return {
                    "type": InterventionType.TAKE_PROFIT_HIT,
                    "reason": f"Price {current_price} hit take profit {order.stop_conditions.take_profit_price}",
                    "action": "exit_position"
                }
            elif play["parsed_play"]["side"] == "sell" and current_price <= order.stop_conditions.take_profit_price:
                return {
                    "type": InterventionType.TAKE_PROFIT_HIT,
                    "reason": f"Price {current_price} hit take profit {order.stop_conditions.take_profit_price}",
                    "action": "exit_position"
                }
        
        # Check timeout
        time_in_play = play["performance_metrics"]["time_in_play"]
        if time_in_play > self.intervention_thresholds["timeout_hours"]:
            return {
                "type": InterventionType.TIMEOUT,
                "reason": f"Play timeout after {time_in_play:.1f} hours",
                "action": "evaluate_and_exit"
            }
        
        # Check max drawdown
        max_drawdown = abs(play["performance_metrics"]["max_drawdown"])
        if max_drawdown > self.intervention_thresholds["max_drawdown"]:
            return {
                "type": InterventionType.MARKET_CONDITION_CHANGE,
                "reason": f"Max drawdown {max_drawdown:.1%} exceeded threshold {self.intervention_thresholds['max_drawdown']:.1%}",
                "action": "reduce_position"
            }
        
        # Check volume anomaly
        volume = market_data.get("volume", 0)
        avg_volume = market_data.get("avg_volume", volume)
        if avg_volume > 0 and volume / avg_volume < self.intervention_thresholds["volume_threshold"]:
            return {
                "type": InterventionType.VOLUME_ANOMALY,
                "reason": f"Volume {volume} significantly below average {avg_volume}",
                "action": "monitor_closely"
            }
        
        return None
    
    def _check_for_adaptation(self, play: Dict[str, Any], order: StructuredOrder, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if play adaptation is needed"""
        
        # Check for positive momentum that suggests adding to position
        pnl_pct = play["performance_metrics"].get("pnl_pct", 0)
        if pnl_pct > 0.05:  # 5% profit
            return {
                "type": "add_position",
                "reason": f"Positive momentum with {pnl_pct:.1%} profit",
                "action": "increase_position_size"
            }
        
        # Check for negative momentum that suggests reducing position
        if pnl_pct < -0.03:  # 3% loss
            return {
                "type": "reduce_position",
                "reason": f"Negative momentum with {pnl_pct:.1%} loss",
                "action": "reduce_position_size"
            }
        
        return None
    
    def _execute_intervention(self, play: Dict[str, Any], order: StructuredOrder, intervention: Dict[str, Any], market_data: Dict[str, Any]) -> None:
        """Execute intervention based on market conditions"""
        
        intervention["timestamp"] = datetime.utcnow().isoformat()
        play["intervention_history"].append(intervention)
        
        # Log intervention to central reporting system
        play_reporting.log_intervention(play["play_id"], intervention, market_data)
        
        if intervention["action"] == "exit_position":
            # Close the position
            enhanced_trade_executor.close_order(order.order_id)
            play["status"] = PlayStatus.COMPLETED
            play["completed_at"] = datetime.utcnow()
            
            # Set exit price from current market data
            current_price = play["performance_metrics"]["current_price"]
            play["performance_metrics"]["exit_price"] = current_price
            
            # Log completion to central reporting
            final_pnl = play["performance_metrics"].get("pnl_pct", 0.0)
            play_reporting.log_play_completion(play["play_id"], current_price, final_pnl)
            
            logger.info(f"Intervention executed: {intervention['reason']}")
            
        elif intervention["action"] == "reduce_position":
            # Reduce position size
            current_quantity = order.quantity
            new_quantity = max(1, current_quantity // 2)  # Reduce by half
            if new_quantity < current_quantity:
                # Create new order with reduced quantity
                logger.info(f"Reducing position from {current_quantity} to {new_quantity}")
                # This would require implementing position adjustment logic
        
        elif intervention["action"] == "monitor_closely":
            # Increase monitoring frequency
            logger.info(f"Increased monitoring due to: {intervention['reason']}")
        
        play["updated_at"] = datetime.utcnow()
    
    def _execute_adaptation(self, play: Dict[str, Any], order: StructuredOrder, adaptation: Dict[str, Any], market_data: Dict[str, Any]) -> None:
        """Execute play adaptation"""
        
        adaptation["timestamp"] = datetime.utcnow().isoformat()
        play["adaptation_history"].append(adaptation)
        
        # Log adaptation to central reporting system
        play_reporting.log_adaptation(play["play_id"], adaptation, market_data)
        
        if adaptation["action"] == "increase_position_size":
            # Add to position
            logger.info(f"Adapting play: {adaptation['reason']}")
            # This would require implementing position addition logic
        
        elif adaptation["action"] == "reduce_position_size":
            # Reduce position
            logger.info(f"Adapting play: {adaptation['reason']}")
            # This would require implementing position reduction logic
        
        play["updated_at"] = datetime.utcnow()
    
    def _check_play_completion(self, play: Dict[str, Any], order: StructuredOrder, market_data: Dict[str, Any]) -> bool:
        """Check if play should be completed"""
        
        # Check if order is already closed
        if order.status in [OrderStatus.CLOSED, OrderStatus.CANCELLED]:
            return True
        
        # Check if timeframe has expired
        time_in_play = play["performance_metrics"]["time_in_play"]
        timeframe_hours = self._parse_timeframe_to_hours(play["parsed_play"]["timeframe"])
        
        if time_in_play > timeframe_hours:
            return True
        
        return False
    
    def _parse_timeframe_to_hours(self, timeframe: str) -> float:
        """Parse timeframe string to hours"""
        
        timeframe_lower = timeframe.lower()
        
        if "day" in timeframe_lower:
            days = 1
            if "2" in timeframe_lower or "two" in timeframe_lower:
                days = 2
            elif "3" in timeframe_lower or "three" in timeframe_lower:
                days = 3
            elif "5" in timeframe_lower or "five" in timeframe_lower:
                days = 5
            return days * 24
        
        elif "week" in timeframe_lower:
            weeks = 1
            if "2" in timeframe_lower or "two" in timeframe_lower:
                weeks = 2
            return weeks * 7 * 24
        
        elif "month" in timeframe_lower:
            months = 1
            if "3" in timeframe_lower or "three" in timeframe_lower:
                months = 3
            return months * 30 * 24
        
        return 24  # Default to 1 day
    
    def _complete_play(self, play: Dict[str, Any], order: StructuredOrder) -> None:
        """Complete the trading play"""
        
        play["status"] = PlayStatus.COMPLETED
        play["completed_at"] = datetime.utcnow()
        play["updated_at"] = datetime.utcnow()
        
        # Log completion to central reporting system
        exit_price = play["performance_metrics"].get("current_price", 0.0)
        final_pnl = play["performance_metrics"].get("pnl_pct", 0.0)
        play_reporting.log_play_completion(play["play_id"], exit_price, final_pnl)
        
        # Move to history
        self.play_history.append(play)
        del self.active_plays[play["play_id"]]
        
        logger.info(f"Play {play['play_id']} completed")
    
    def get_play_summary(self, play_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a play"""
        
        if play_id in self.active_plays:
            play = self.active_plays[play_id]
        else:
            # Check history
            play = next((p for p in self.play_history if p["play_id"] == play_id), None)
        
        if not play:
            return None
        
        return {
            "play_id": play["play_id"],
            "symbol": play["symbol"],
            "status": play["status"].value,
            "title": play["parsed_play"]["title"],
            "side": play["parsed_play"]["side"],
            "created_at": play["created_at"].isoformat(),
            "updated_at": play["updated_at"].isoformat(),
            "performance": play["performance_metrics"],
            "interventions": len(play["intervention_history"]),
            "adaptations": len(play["adaptation_history"])
        }
    
    def get_all_plays_summary(self) -> Dict[str, Any]:
        """Get summary of all plays"""
        
        active_plays = [self.get_play_summary(play_id) for play_id in self.active_plays.keys()]
        historical_plays = [self.get_play_summary(play["play_id"]) for play in self.play_history]
        
        # Calculate statistics
        total_active = len(active_plays)
        total_historical = len(historical_plays)
        
        if historical_plays:
            avg_performance = sum(p["performance"]["pnl_pct"] for p in historical_plays if p) / total_historical
            successful_plays = sum(1 for p in historical_plays if p and p["performance"]["pnl_pct"] > 0)
            success_rate = successful_plays / total_historical if total_historical > 0 else 0
        else:
            avg_performance = 0
            success_rate = 0
        
        return {
            "active_plays": active_plays,
            "historical_plays": historical_plays,
            "statistics": {
                "total_active": total_active,
                "total_historical": total_historical,
                "average_performance": avg_performance,
                "success_rate": success_rate
            }
        }


# Global play executor instance
play_executor = PlayExecutorAgent() 