import os
from typing import Optional
# from pydantic import BaseSettings  # removed to avoid pydantic v2 change
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration for the Organic Investment Bot"""
    
    def __init__(self):
        # Alpaca Paper Trading
        self.alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "")
        self.alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "")
        self.alpaca_base_url: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        
        # OpenAI
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.openai_model: str = "gpt-4o-mini"  # Using mini for cost efficiency
        self.openai_cheaper_model: str = os.getenv("OPENAI_CHEAPER_MODEL", "gpt-4o-mini")
        self.openai_daily_budget_usd: float = float(os.getenv("OPENAI_DAILY_BUDGET", "0.10"))  # $0.10 default budget
        self.openai_budget_ceiling: float = float(os.getenv("OPENAI_BUDGET_CEILING", "1.00"))
        self.openai_gain_factor: float = float(os.getenv("OPENAI_GAIN_FACTOR", "0.3"))
        self.openai_budget_step_max: float = float(os.getenv("OPENAI_BUDGET_STEP_MAX", "0.20"))
        self.openai_drawdown_cutoff: float = float(os.getenv("OPENAI_DRAWDOWN_CUTOFF", "0.1"))
        
        # ChromaDB
        self.chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma")
        
        # Trading Settings
        self.paper_trading: bool = True
        self.max_position_size: float = 0.05  # 5% of portfolio per trade
        self.max_daily_loss: float = 0.02  # 2% daily loss limit
        
        # Market Data
        self.symbols_to_watch: list = ["SPY", "QQQ", "IWM", "GLD", "TLT"]  # ETFs for diversification
        self.market_hours_start: str = "09:30"
        self.market_hours_end: str = "16:00"
        
        # News and Sentiment
        self.news_sources: list = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.marketwatch.com/rss/topstories",
        ]
        
        # RAG Settings
        self.max_similar_trades: int = 5
        self.similarity_threshold: float = 0.7
        
        # Logging
        self.log_level: str = "INFO"
        self.log_file: str = "organic_bot.log"

        # Finnhub
        self.finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")

# Global config instance
config = Config() 