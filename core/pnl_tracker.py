"""
PnL Tracker that calculates real profit and loss from trades.
Tracks open positions and calculates realized/unrealized PnL.
"""

import json
import pathlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from utils.logger import logger  # type: ignore
from core.config import config


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    quantity: int
    entry_price: float
    entry_time: datetime
    side: str  # 'BUY' or 'SELL'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "side": self.side
        }


@dataclass
class ClosedTrade:
    """Represents a closed trade with PnL."""
    symbol: str
    quantity: int
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    side: str
    pnl: float
    pnl_pct: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat(),
            "side": self.side,
            "pnl": self.pnl,
            "pnl_pct": self.pnl_pct
        }


class PnLTracker:
    """Tracks positions and calculates PnL accurately."""
    
    def __init__(self):
        self.positions_file = pathlib.Path("positions.json")
        self.trades_file = pathlib.Path("closed_trades.jsonl")
        
        # Load existing positions
        self.open_positions: Dict[str, Position] = self._load_positions()
        
        # Load closed trades
        self.closed_trades: List[ClosedTrade] = self._load_closed_trades()
    
    def _load_positions(self) -> Dict[str, Position]:
        """Load open positions from file."""
        try:
            if self.positions_file.exists():
                with self.positions_file.open() as f:
                    data = json.load(f)
                    positions = {}
                    for symbol, pos_data in data.items():
                        positions[symbol] = Position(
                            symbol=pos_data["symbol"],
                            quantity=pos_data["quantity"],
                            entry_price=pos_data["entry_price"],
                            entry_time=datetime.fromisoformat(pos_data["entry_time"]),
                            side=pos_data["side"]
                        )
                    return positions
        except Exception as e:
            logger.error(f"Error loading positions: {e}")
        return {}
    
    def _load_closed_trades(self) -> List[ClosedTrade]:
        """Load closed trades from file."""
        try:
            if self.trades_file.exists():
                trades = []
                with self.trades_file.open() as f:
                    for line in f:
                        if line.strip():
                            trade_data = json.loads(line)
                            trades.append(ClosedTrade(
                                symbol=trade_data["symbol"],
                                quantity=trade_data["quantity"],
                                entry_price=trade_data["entry_price"],
                                exit_price=trade_data["exit_price"],
                                entry_time=datetime.fromisoformat(trade_data["entry_time"]),
                                exit_time=datetime.fromisoformat(trade_data["exit_time"]),
                                side=trade_data["side"],
                                pnl=trade_data["pnl"],
                                pnl_pct=trade_data["pnl_pct"]
                            ))
                return trades
        except Exception as e:
            logger.error(f"Error loading closed trades: {e}")
        return []
    
    def _save_positions(self):
        """Save current positions to file."""
        try:
            data = {symbol: pos.to_dict() for symbol, pos in self.open_positions.items()}
            with self.positions_file.open('w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving positions: {e}")
    
    def _save_closed_trade(self, trade: ClosedTrade):
        """Save a closed trade to file."""
        try:
            with self.trades_file.open('a') as f:
                f.write(json.dumps(trade.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Error saving closed trade: {e}")
    
    def process_trade(self, trade_data: Dict[str, Any], current_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Process a trade and calculate PnL.
        
        Args:
            trade_data: Trade information with symbol, action, quantity, price
            current_price: Current market price (if not provided in trade_data)
            
        Returns:
            Updated trade data with PnL information
        """
        try:
            symbol = trade_data.get("symbol", "SPY")
            action = trade_data.get("action", "").upper()
            quantity = trade_data.get("quantity", 1)
            price = trade_data.get("price") or current_price
            
            if not price:
                logger.warning(f"No price available for {symbol}, cannot calculate PnL")
                return {**trade_data, "pnl": 0, "pnl_pct": 0}
            
            if action == "BUY":
                return self._process_buy(symbol, quantity, price, trade_data)
            elif action == "SELL":
                return self._process_sell(symbol, quantity, price, trade_data)
            else:
                return {**trade_data, "pnl": 0, "pnl_pct": 0}
                
        except Exception as e:
            logger.error(f"Error processing trade: {e}")
            return {**trade_data, "pnl": 0, "pnl_pct": 0}
    
    def _process_buy(self, symbol: str, quantity: int, price: float, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a BUY order."""
        # Check if we have an existing short position to close
        if symbol in self.open_positions and self.open_positions[symbol].side == "SELL":
            return self._close_position(symbol, quantity, price, trade_data)
        
        # Check if we're adding to an existing long position
        if symbol in self.open_positions and self.open_positions[symbol].side == "BUY":
            return self._add_to_position(symbol, quantity, price, trade_data)
        
        # Open new long position
        return self._open_position(symbol, quantity, price, "BUY", trade_data)
    
    def _process_sell(self, symbol: str, quantity: int, price: float, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a SELL order."""
        # Check if we have an existing long position to close
        if symbol in self.open_positions and self.open_positions[symbol].side == "BUY":
            return self._close_position(symbol, quantity, price, trade_data)
        
        # Check if we're adding to an existing short position
        if symbol in self.open_positions and self.open_positions[symbol].side == "SELL":
            return self._add_to_position(symbol, quantity, price, trade_data)
        
        # Open new short position
        return self._open_position(symbol, quantity, price, "SELL", trade_data)
    
    def _open_position(self, symbol: str, quantity: int, price: float, side: str, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Open a new position."""
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price,
            entry_time=datetime.now(),
            side=side
        )
        
        self.open_positions[symbol] = position
        self._save_positions()
        
        logger.info(f"PnL | Opened {side} position: {quantity} shares of {symbol} at ${price}")
        
        return {
            **trade_data,
            "pnl": 0,  # No PnL on opening
            "pnl_pct": 0,
            "position_status": "opened",
            "entry_price": price
        }
    
    def _close_position(self, symbol: str, quantity: int, price: float, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Close an existing position."""
        if symbol not in self.open_positions:
            logger.warning(f"No position found for {symbol}")
            return {**trade_data, "pnl": 0, "pnl_pct": 0}
        
        position = self.open_positions[symbol]
        
        # Calculate PnL based on position side
        if position.side == "BUY":
            # Long position: profit when price goes up
            pnl = (price - position.entry_price) * min(quantity, position.quantity)
        else:
            # Short position: profit when price goes down
            pnl = (position.entry_price - price) * min(quantity, position.quantity)
        
        pnl_pct = (pnl / (position.entry_price * min(quantity, position.quantity))) * 100
        
        # Create closed trade record
        closed_trade = ClosedTrade(
            symbol=symbol,
            quantity=min(quantity, position.quantity),
            entry_price=position.entry_price,
            exit_price=price,
            entry_time=position.entry_time,
            exit_time=datetime.now(),
            side=position.side,
            pnl=pnl,
            pnl_pct=pnl_pct
        )
        
        self.closed_trades.append(closed_trade)
        self._save_closed_trade(closed_trade)
        
        # Update or remove position
        if quantity >= position.quantity:
            # Fully closed
            del self.open_positions[symbol]
            logger.info(f"PnL | Closed position: {symbol} PnL: ${pnl:.2f} ({pnl_pct:.2f}%)")
        else:
            # Partially closed
            position.quantity -= quantity
            logger.info(f"PnL | Partially closed position: {symbol} PnL: ${pnl:.2f} ({pnl_pct:.2f}%)")
        
        self._save_positions()
        
        return {
            **trade_data,
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "position_status": "closed",
            "entry_price": position.entry_price,
            "exit_price": price
        }
    
    def _add_to_position(self, symbol: str, quantity: int, price: float, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add to an existing position (average down/up)."""
        position = self.open_positions[symbol]
        
        # Calculate new average price
        total_quantity = position.quantity + quantity
        total_cost = (position.entry_price * position.quantity) + (price * quantity)
        new_avg_price = total_cost / total_quantity
        
        # Update position
        position.quantity = total_quantity
        position.entry_price = new_avg_price
        
        self._save_positions()
        
        logger.info(f"PnL | Added to position: {symbol} new avg price: ${new_avg_price:.2f}")
        
        return {
            **trade_data,
            "pnl": 0,  # No realized PnL on adding
            "pnl_pct": 0,
            "position_status": "added",
            "new_avg_price": new_avg_price
        }
    
    def get_unrealized_pnl(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculate unrealized PnL for open positions."""
        unrealized_pnl = {}
        total_unrealized = 0
        
        for symbol, position in self.open_positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                if position.side == "BUY":
                    pnl = (current_price - position.entry_price) * position.quantity
                else:
                    pnl = (position.entry_price - current_price) * position.quantity
                
                pnl_pct = (pnl / (position.entry_price * position.quantity)) * 100
                
                unrealized_pnl[symbol] = {
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl_pct, 2),
                    "quantity": position.quantity,
                    "entry_price": position.entry_price,
                    "current_price": current_price,
                    "side": position.side
                }
                
                total_unrealized += pnl
        
        return {
            "positions": unrealized_pnl,
            "total_unrealized_pnl": round(total_unrealized, 2)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        if not self.closed_trades:
            return {
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0
            }
        
        total_pnl = sum(trade.pnl for trade in self.closed_trades)
        winning_trades = [trade for trade in self.closed_trades if trade.pnl > 0]
        losing_trades = [trade for trade in self.closed_trades if trade.pnl < 0]
        
        win_rate = len(winning_trades) / len(self.closed_trades) * 100
        avg_win = sum(trade.pnl for trade in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(trade.pnl for trade in losing_trades) / len(losing_trades) if losing_trades else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            "total_trades": len(self.closed_trades),
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "open_positions": len(self.open_positions)
        }


# Global instance
pnl_tracker = PnLTracker()