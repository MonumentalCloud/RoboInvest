from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

from core.alpaca_client import alpaca_client
from core.structured_order import (
    StructuredOrder, OrderManager, OrderStatus, OrderType, 
    TradingPlay, SWOTAnalysis, RiskAssessment, StopConditions
)
from agents.swot_analyzer import swot_analyzer
from agents.risk_assessor import risk_assessor
from utils.logger import logger


class EnhancedTradeExecutorAgent:
    """Enhanced trade executor that uses structured orders with comprehensive analysis"""
    
    def __init__(self):
        self.order_manager = OrderManager()
        self.use_structured_orders = True
        self.auto_approve_low_risk = True
        self.auto_approve_high_confidence = True
        self.max_position_size = 1000  # Maximum position value in dollars
        self.max_risk_per_trade = 0.02  # Maximum 2% risk per trade
    
    def create_structured_trade(self,
                              symbol: str,
                              side: str,
                              quantity: int,
                              market_data: Dict[str, Any],
                              news_data: List[str],
                              technical_indicators: Optional[Dict[str, Any]] = None,
                              fundamental_data: Optional[Dict[str, Any]] = None,
                              sector_data: Optional[Dict[str, Any]] = None,
                              market_context: Optional[Dict[str, Any]] = None,
                              play_title: str = "",
                              play_description: str = "",
                              confidence_score: float = 0.5,
                              priority: int = 5,
                              tags: Optional[List[str]] = None,
                              notes: str = "") -> StructuredOrder:
        """Create a comprehensive structured trade with full analysis"""
        
        # Validate inputs
        if not symbol or not side or quantity <= 0:
            raise ValueError("Invalid trade parameters")
        
        current_price = market_data.get("price", 0)
        if current_price <= 0:
            raise ValueError("Invalid current price")
        
        position_value = quantity * current_price
        if position_value > self.max_position_size:
            logger.warning(f"Position value ${position_value:.2f} exceeds max size ${self.max_position_size}")
        
        # Perform SWOT analysis
        swot_analysis = swot_analyzer.analyze_opportunity(
            symbol=symbol,
            market_data=market_data,
            news_data=news_data,
            technical_indicators=technical_indicators,
            fundamental_data=fundamental_data,
            sector_data=sector_data
        )
        
        # Perform risk assessment
        risk_assessment = risk_assessor.assess_risk(
            symbol=symbol,
            quantity=quantity,
            current_price=current_price,
            market_data=market_data,
            historical_data=market_data.get("historical_data"),
            sector_data=sector_data,
            market_context=market_context
        )
        
        # Create stop conditions
        stop_conditions = self._create_stop_conditions(
            symbol=symbol,
            side=side,
            current_price=current_price,
            risk_assessment=risk_assessment,
            swot_analysis=swot_analysis
        )
        
        # Create trading play
        play = TradingPlay(
            play_id=f"play_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            title=play_title or f"{side.upper()} {symbol} - {swot_analysis.overall_score:.2f}",
            description=play_description or f"Automated trade based on market analysis",
            thesis=f"SWOT Score: {swot_analysis.overall_score:.2f}, Risk Level: {risk_assessment.risk_level.value}",
            catalyst="Market analysis and technical indicators",
            timeframe="1-5 days",
            entry_strategy=f"Market order at current price ${current_price:.2f}",
            exit_strategy=f"Stop loss at {stop_conditions.stop_loss_percentage}%, Take profit at {stop_conditions.take_profit_percentage}%",
            key_risks=[risk_assessment.risk_level.value],
            key_metrics={
                "swot_score": swot_analysis.overall_score,
                "risk_score": risk_assessment.overall_risk_score,
                "volatility": risk_assessment.volatility,
                "var_95": risk_assessment.var_95
            },
            research_sources=["Market data", "News sentiment", "Technical analysis"],
            analyst_notes=notes,
            market_context=str(market_context) if market_context else "Standard market conditions",
            sector_analysis=str(sector_data) if sector_data else "Sector analysis not available",
            technical_analysis=str(technical_indicators) if technical_indicators else "Technical analysis not available",
            fundamental_analysis=str(fundamental_data) if fundamental_data else "Fundamental analysis not available",
            sentiment_analysis=f"News sentiment: {len(news_data)} headlines analyzed",
            created_by="EnhancedTradeExecutorAgent",
            created_at=datetime.utcnow()
        )
        
        # Create structured order
        order = self.order_manager.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            play=play,
            swot_analysis=swot_analysis,
            risk_assessment=risk_assessment,
            stop_conditions=stop_conditions,
            order_type=OrderType.MARKET,
            confidence_score=confidence_score,
            priority=priority,
            tags=tags or [],
            notes=notes
        )
        
        logger.info(f"Created structured order {order.order_id} for {symbol} {side} {quantity}")
        logger.info(f"SWOT Score: {swot_analysis.overall_score:.2f}, Risk Level: {risk_assessment.risk_level.value}")
        
        return order
    
    def _create_stop_conditions(self,
                               symbol: str,
                               side: str,
                               current_price: float,
                               risk_assessment: RiskAssessment,
                               swot_analysis: SWOTAnalysis) -> StopConditions:
        """Create appropriate stop conditions based on risk assessment"""
        
        # Base stop loss percentage based on risk level
        base_stop_loss = {
            "low": 3.0,
            "medium": 5.0,
            "high": 8.0,
            "extreme": 12.0
        }.get(risk_assessment.risk_level.value, 5.0)
        
        # Adjust based on SWOT score
        if swot_analysis.overall_score > 0.5:
            # More confident trade - tighter stops
            stop_loss_pct = base_stop_loss * 0.8
            take_profit_pct = base_stop_loss * 2.0  # 2:1 reward-to-risk
        elif swot_analysis.overall_score < -0.5:
            # Less confident trade - wider stops
            stop_loss_pct = base_stop_loss * 1.2
            take_profit_pct = base_stop_loss * 1.5
        else:
            # Neutral confidence
            stop_loss_pct = base_stop_loss
            take_profit_pct = base_stop_loss * 1.8
        
        # Calculate specific prices
        if side.lower() == "buy":
            stop_loss_price = current_price * (1 - stop_loss_pct / 100)
            take_profit_price = current_price * (1 + take_profit_pct / 100)
        else:
            stop_loss_price = current_price * (1 + stop_loss_pct / 100)
            take_profit_price = current_price * (1 - take_profit_pct / 100)
        
        return StopConditions(
            stop_loss_price=stop_loss_price,
            stop_loss_percentage=stop_loss_pct,
            take_profit_price=take_profit_price,
            take_profit_percentage=take_profit_pct,
            trailing_stop_percentage=None,  # Could be implemented later
            time_based_stop=datetime.utcnow() + timedelta(days=5),  # 5-day max hold
            max_holding_period=timedelta(days=5)
        )
    
    def execute_order(self, order: StructuredOrder) -> Dict[str, Any]:
        """Execute a structured order"""
        
        # Check if order should be auto-approved
        if self._should_auto_approve(order):
            self.order_manager.approve_order(order.order_id)
            logger.info(f"Auto-approved order {order.order_id}")
        else:
            # Require manual approval
            self.order_manager.update_order_status(order.order_id, OrderStatus.PENDING_APPROVAL)
            logger.info(f"Order {order.order_id} requires manual approval")
            return {
                "status": "pending_approval",
                "order_id": order.order_id,
                "reason": "Order requires manual approval due to risk level or size"
            }
        
        # Check if Alpaca is ready
        if not alpaca_client.is_ready():
            logger.warning("Alpaca not configured - cannot execute order")
            return {
                "status": "error",
                "order_id": order.order_id,
                "reason": "Alpaca client not configured"
            }
        
        # Execute the order
        try:
            alpaca_order = alpaca_client.submit_order(
                symbol=order.symbol,
                qty=order.quantity,
                side=order.side
            )
            
            if alpaca_order:
                # Update order with Alpaca order ID
                order.alpaca_order_id = alpaca_order.get("id")
                order.update_status(OrderStatus.SUBMITTED)
                
                logger.info(f"Successfully submitted order {order.order_id} to Alpaca")
                
                return {
                    "status": "submitted",
                    "order_id": order.order_id,
                    "alpaca_order_id": order.alpaca_order_id,
                    "symbol": order.symbol,
                    "side": order.side,
                    "quantity": order.quantity,
                    "swot_score": order.swot_analysis.overall_score,
                    "risk_level": order.risk_assessment.risk_level.value,
                    "stop_loss": order.stop_conditions.stop_loss_price,
                    "take_profit": order.stop_conditions.take_profit_price
                }
            else:
                order.update_status(OrderStatus.REJECTED)
                return {
                    "status": "rejected",
                    "order_id": order.order_id,
                    "reason": "Alpaca order submission failed"
                }
                
        except Exception as e:
            logger.error(f"Error executing order {order.order_id}: {e}")
            order.update_status(OrderStatus.REJECTED)
            return {
                "status": "error",
                "order_id": order.order_id,
                "reason": f"Execution error: {str(e)}"
            }
    
    def _should_auto_approve(self, order: StructuredOrder) -> bool:
        """Determine if order should be auto-approved"""
        
        # Auto-approve low-risk orders
        if self.auto_approve_low_risk and order.risk_assessment.risk_level.value in ["low", "medium"]:
            return True
        
        # Auto-approve high-confidence orders
        if self.auto_approve_high_confidence and order.confidence_score >= 0.8:
            return True
        
        # Auto-approve small positions
        position_value = order.quantity * (order.price or 0)
        if position_value < 100:  # Small positions
            return True
        
        # Require approval for high-risk or large positions
        return False
    
    def get_order_summary(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of an order"""
        order = self.order_manager.get_order(order_id)
        if not order:
            return None
        
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "status": order.status.value,
            "play_title": order.play.title,
            "swot_score": order.swot_analysis.overall_score,
            "risk_level": order.risk_assessment.risk_level.value,
            "confidence_score": order.confidence_score,
            "created_at": order.created_at.isoformat(),
            "stop_loss": order.stop_conditions.stop_loss_price,
            "take_profit": order.stop_conditions.take_profit_price,
            "max_loss_amount": order.risk_assessment.max_loss_amount,
            "var_95": order.risk_assessment.var_95
        }
    
    def get_all_orders_summary(self) -> Dict[str, Any]:
        """Get summary of all orders"""
        active_orders = self.order_manager.get_order_summaries()
        historical_orders = self.order_manager.get_order_history_summaries()
        
        # Calculate statistics
        total_active = len(active_orders)
        total_historical = len(historical_orders)
        
        if active_orders:
            avg_swot_score = sum(order.get("swot_score", 0) for order in active_orders) / total_active
            risk_distribution = {}
            for order in active_orders:
                risk_level = order.get("risk_level", "unknown")
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        else:
            avg_swot_score = 0
            risk_distribution = {}
        
        return {
            "active_orders": active_orders,
            "historical_orders": historical_orders,
            "statistics": {
                "total_active": total_active,
                "total_historical": total_historical,
                "average_swot_score": avg_swot_score,
                "risk_distribution": risk_distribution
            }
        }
    
    def approve_order(self, order_id: str) -> bool:
        """Approve an order for execution"""
        return self.order_manager.approve_order(order_id)
    
    def reject_order(self, order_id: str, reason: str = "") -> bool:
        """Reject an order"""
        return self.order_manager.reject_order(order_id, reason)
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        order = self.order_manager.get_order(order_id)
        if not order:
            return False
        
        # Cancel in Alpaca if it was submitted
        if order.alpaca_order_id and alpaca_client.is_ready():
            try:
                # This would require implementing cancel_order in alpaca_client
                logger.info(f"Cancelling Alpaca order {order.alpaca_order_id}")
            except Exception as e:
                logger.error(f"Error cancelling Alpaca order: {e}")
        
        order.update_status(OrderStatus.CANCELLED)
        return True
    
    def close_order(self, order_id: str, realized_pnl: Optional[float] = None) -> bool:
        """Close an order and move to history"""
        return self.order_manager.close_order(order_id, realized_pnl)
    
    def get_orders_requiring_approval(self) -> List[Dict[str, Any]]:
        """Get all orders that require manual approval"""
        orders = self.order_manager.get_orders_requiring_approval()
        return [order.to_summary() for order in orders]
    
    def get_high_risk_orders(self) -> List[Dict[str, Any]]:
        """Get all high-risk orders"""
        orders = self.order_manager.get_high_risk_orders()
        return [order.to_summary() for order in orders]
    
    def save_orders(self, filename: str = "structured_orders.json") -> None:
        """Save all orders to file"""
        self.order_manager.save_orders(filename)
    
    def load_orders(self, filename: str = "structured_orders.json") -> None:
        """Load orders from file"""
        self.order_manager.load_orders(filename)


# Global enhanced trade executor instance
enhanced_trade_executor = EnhancedTradeExecutorAgent() 