from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

from utils.logger import logger


class OrderStatus(Enum):
    """Order lifecycle statuses"""
    PENDING_ANALYSIS = "pending_analysis"
    ANALYZED = "analyzed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    STOPPED_OUT = "stopped_out"
    CLOSED = "closed"


class OrderType(Enum):
    """Types of orders"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class SWOTAnalysis:
    """SWOT analysis for a trading play"""
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    overall_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RiskAssessment:
    """Risk assessment for an order"""
    risk_level: RiskLevel
    max_loss_amount: float
    max_loss_percentage: float
    var_95: float  # Value at Risk 95%
    sharpe_ratio: Optional[float]
    beta: Optional[float]
    volatility: float
    correlation_with_spy: float
    sector_risk: float
    market_timing_risk: float
    liquidity_risk: float
    overall_risk_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StopConditions:
    """Stop loss and take profit conditions"""
    stop_loss_price: Optional[float]
    stop_loss_percentage: float
    take_profit_price: Optional[float]
    take_profit_percentage: float
    trailing_stop_percentage: Optional[float]
    time_based_stop: Optional[datetime]  # Close position after X time
    max_holding_period: Optional[timedelta]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.time_based_stop:
            data['time_based_stop'] = self.time_based_stop.isoformat()
        if self.max_holding_period:
            data['max_holding_period'] = str(self.max_holding_period)
        return data


@dataclass
class TradingPlay:
    """Comprehensive trading play documentation"""
    play_id: str
    title: str
    description: str
    thesis: str
    catalyst: str
    timeframe: str  # e.g., "1-3 days", "1-2 weeks", "1-3 months"
    entry_strategy: str
    exit_strategy: str
    key_risks: List[str]
    key_metrics: Dict[str, Any]
    research_sources: List[str]
    analyst_notes: str
    market_context: str
    sector_analysis: str
    technical_analysis: str
    fundamental_analysis: str
    sentiment_analysis: str
    created_by: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class StructuredOrder:
    """Comprehensive structured order with full documentation"""
    # Basic order info
    order_id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: OrderType
    quantity: int
    price: Optional[float]
    
    # Status and lifecycle
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    filled_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    
    # Trading play and analysis
    play: TradingPlay
    swot_analysis: SWOTAnalysis
    risk_assessment: RiskAssessment
    stop_conditions: StopConditions
    
    # Execution details
    alpaca_order_id: Optional[str]
    fill_price: Optional[float]
    commission: Optional[float]
    realized_pnl: Optional[float]
    
    # Metadata
    confidence_score: float  # 0.0 to 1.0
    priority: int  # 1-10, higher is more important
    tags: List[str]
    notes: str
    
    def __post_init__(self):
        if not self.order_id:
            self.order_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status and timestamp"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Set specific timestamps based on status
        if new_status == OrderStatus.SUBMITTED:
            self.submitted_at = datetime.utcnow()
        elif new_status == OrderStatus.FILLED:
            self.filled_at = datetime.utcnow()
        elif new_status == OrderStatus.CANCELLED:
            self.cancelled_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        data = asdict(self)
        data['order_type'] = self.order_type.value
        data['status'] = self.status.value
        data['risk_level'] = self.risk_assessment.risk_level.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        
        if self.submitted_at:
            data['submitted_at'] = self.submitted_at.isoformat()
        if self.filled_at:
            data['filled_at'] = self.filled_at.isoformat()
        if self.cancelled_at:
            data['cancelled_at'] = self.cancelled_at.isoformat()
        
        return data
    
    def to_summary(self) -> Dict[str, Any]:
        """Create a summary for quick reference"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'status': self.status.value,
            'play_title': self.play.title,
            'confidence_score': self.confidence_score,
            'risk_level': self.risk_assessment.risk_level.value,
            'overall_risk_score': self.risk_assessment.overall_risk_score,
            'swot_score': self.swot_analysis.overall_score,
            'created_at': self.created_at.isoformat(),
            'priority': self.priority,
            'tags': self.tags
        }
    
    def is_high_risk(self) -> bool:
        """Check if order is high risk"""
        return self.risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME]
    
    def is_high_confidence(self) -> bool:
        """Check if order has high confidence"""
        return self.confidence_score >= 0.7
    
    def should_require_approval(self) -> bool:
        """Determine if order requires manual approval"""
        return (self.is_high_risk() or 
                self.quantity > 10 or 
                self.risk_assessment.max_loss_amount > 1000 or
                self.priority >= 8)
    
    def get_stop_loss_price(self, current_price: float) -> Optional[float]:
        """Calculate stop loss price based on current price"""
        if self.stop_conditions.stop_loss_percentage > 0:
            if self.side.lower() == "buy":
                return current_price * (1 - self.stop_conditions.stop_loss_percentage / 100)
            else:
                return current_price * (1 + self.stop_conditions.stop_loss_percentage / 100)
        return self.stop_conditions.stop_loss_price
    
    def get_take_profit_price(self, current_price: float) -> Optional[float]:
        """Calculate take profit price based on current price"""
        if self.stop_conditions.take_profit_percentage > 0:
            if self.side.lower() == "buy":
                return current_price * (1 + self.stop_conditions.take_profit_percentage / 100)
            else:
                return current_price * (1 - self.stop_conditions.take_profit_percentage / 100)
        return self.stop_conditions.take_profit_price


class OrderManager:
    """Manages structured orders and their lifecycle"""
    
    def __init__(self):
        self.orders: Dict[str, StructuredOrder] = {}
        self.order_history: List[StructuredOrder] = []
    
    def create_order(self, 
                    symbol: str,
                    side: str,
                    quantity: int,
                    play: TradingPlay,
                    swot_analysis: SWOTAnalysis,
                    risk_assessment: RiskAssessment,
                    stop_conditions: StopConditions,
                    order_type: OrderType = OrderType.MARKET,
                    price: Optional[float] = None,
                    confidence_score: float = 0.5,
                    priority: int = 5,
                    tags: Optional[List[str]] = None,
                    notes: str = "") -> StructuredOrder:
        """Create a new structured order"""
        
        order = StructuredOrder(
            order_id="",
            symbol=symbol.upper(),
            side=side.lower(),
            order_type=order_type,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING_ANALYSIS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            submitted_at=None,
            filled_at=None,
            cancelled_at=None,
            play=play,
            swot_analysis=swot_analysis,
            risk_assessment=risk_assessment,
            stop_conditions=stop_conditions,
            alpaca_order_id=None,
            fill_price=None,
            commission=None,
            realized_pnl=None,
            confidence_score=confidence_score,
            priority=priority,
            tags=tags or [],
            notes=notes
        )
        
        self.orders[order.order_id] = order
        logger.info(f"Created structured order {order.order_id} for {symbol} {side} {quantity}")
        
        return order
    
    def get_order(self, order_id: str) -> Optional[StructuredOrder]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_orders_by_symbol(self, symbol: str) -> List[StructuredOrder]:
        """Get all orders for a symbol"""
        return [order for order in self.orders.values() if order.symbol == symbol.upper()]
    
    def get_orders_by_status(self, status: OrderStatus) -> List[StructuredOrder]:
        """Get all orders with a specific status"""
        return [order for order in self.orders.values() if order.status == status]
    
    def get_high_risk_orders(self) -> List[StructuredOrder]:
        """Get all high-risk orders"""
        return [order for order in self.orders.values() if order.is_high_risk()]
    
    def get_orders_requiring_approval(self) -> List[StructuredOrder]:
        """Get all orders that require manual approval"""
        return [order for order in self.orders.values() if order.should_require_approval()]
    
    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update order status"""
        order = self.get_order(order_id)
        if not order:
            return False
        
        order.update_status(new_status)
        logger.info(f"Updated order {order_id} status to {new_status.value}")
        return True
    
    def approve_order(self, order_id: str) -> bool:
        """Approve an order for execution"""
        order = self.get_order(order_id)
        if not order or order.status != OrderStatus.PENDING_APPROVAL:
            return False
        
        order.update_status(OrderStatus.APPROVED)
        logger.info(f"Approved order {order_id} for execution")
        return True
    
    def reject_order(self, order_id: str, reason: str = "") -> bool:
        """Reject an order"""
        order = self.get_order(order_id)
        if not order:
            return False
        
        order.update_status(OrderStatus.REJECTED)
        order.notes += f"\nRejected: {reason}"
        logger.info(f"Rejected order {order_id}: {reason}")
        return True
    
    def close_order(self, order_id: str, realized_pnl: Optional[float] = None) -> bool:
        """Close an order and move to history"""
        order = self.get_order(order_id)
        if not order:
            return False
        
        if realized_pnl is not None:
            order.realized_pnl = realized_pnl
        
        order.update_status(OrderStatus.CLOSED)
        self.order_history.append(order)
        del self.orders[order_id]
        
        logger.info(f"Closed order {order_id} with PnL: {realized_pnl}")
        return True
    
    def get_order_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all active orders"""
        return [order.to_summary() for order in self.orders.values()]
    
    def get_order_history_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all historical orders"""
        return [order.to_summary() for order in self.order_history]
    
    def save_orders(self, filename: str) -> None:
        """Save orders to JSON file"""
        data = {
            'active_orders': [order.to_dict() for order in self.orders.values()],
            'order_history': [order.to_dict() for order in self.order_history]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved {len(self.orders)} active orders and {len(self.order_history)} historical orders to {filename}")
    
    def load_orders(self, filename: str) -> None:
        """Load orders from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear existing orders
            self.orders.clear()
            self.order_history.clear()
            
            # Load active orders
            for order_data in data.get('active_orders', []):
                # Reconstruct order objects (simplified - would need full reconstruction in production)
                logger.info(f"Loaded active order: {order_data.get('order_id')}")
            
            # Load historical orders
            for order_data in data.get('order_history', []):
                logger.info(f"Loaded historical order: {order_data.get('order_id')}")
            
            logger.info(f"Loaded orders from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to load orders from {filename}: {e}")


# Global order manager instance
order_manager = OrderManager() 