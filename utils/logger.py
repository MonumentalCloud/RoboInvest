from __future__ import annotations

import sys
from loguru import logger  # type: ignore

# Lazy import of config to avoid circular
try:
    from core.config import config
except Exception:
    class _Temp:
        log_level = "INFO"
        log_file = "organic_bot.log"
    config = _Temp()


def setup_logger() -> None:
    """Configure root logger once."""

    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True,
    )
    logger.add(
        config.log_file,
        rotation="7 days",
        level=config.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )


# Initialise immediately
setup_logger()

def log_trade(trade_data: dict):
    """Log trade information"""
    logger.info(f"TRADE: {trade_data}")

def log_market_observation(observation: dict):
    """Log market observation"""
    logger.info(f"MARKET: {observation}")

def log_learning(learning_data: dict):
    """Log learning/pattern recognition"""
    logger.info(f"LEARNING: {learning_data}")

def log_error(error: str, context: str = ""):
    """Log errors with context"""
    logger.error(f"ERROR [{context}]: {error}")

def log_warning(warning: str, context: str = ""):
    """Log warnings with context"""
    logger.warning(f"WARNING [{context}]: {warning}") 