import os
import json
from typing import Optional, Any, Union
# from pydantic import BaseSettings  # removed to avoid pydantic v2 change
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration for the Organic Investment Bot"""
    
    def __init__(self):
        # Load JSON config if it exists
        self._json_config = self._load_json_config()
        
        # Alpaca Paper Trading
        self.alpaca_api_key: str = str(self._get_config("trading.alpaca_api_key", "ALPACA_API_KEY", ""))
        self.alpaca_secret_key: str = str(self._get_config("trading.alpaca_secret_key", "ALPACA_SECRET_KEY", ""))
        self.alpaca_base_url: str = str(self._get_config("trading.alpaca_base_url", "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"))
        
        # OpenAI
        self.openai_api_key: str = str(self._get_config("openai.api_key", "OPENAI_API_KEY", ""))
        self.openai_model: str = str(self._get_config("openai.model", "OPENAI_MODEL", "gpt-4o-mini"))
        self.openai_cheaper_model: str = str(self._get_config("openai.cheaper_model", "OPENAI_CHEAPER_MODEL", "gpt-4o-mini"))
        self.openai_daily_budget_usd: float = float(self._get_config("openai.daily_budget_usd", "OPENAI_DAILY_BUDGET", 0.10))
        self.openai_budget_ceiling: float = float(self._get_config("openai.budget_ceiling", "OPENAI_BUDGET_CEILING", 1.00))
        self.openai_gain_factor: float = float(self._get_config("openai.gain_factor", "OPENAI_GAIN_FACTOR", 0.3))
        self.openai_budget_step_max: float = float(self._get_config("openai.budget_step_max", "OPENAI_BUDGET_STEP_MAX", 0.20))
        self.openai_drawdown_cutoff: float = float(self._get_config("openai.drawdown_cutoff", "OPENAI_DRAWDOWN_CUTOFF", 0.1))
        
        # OpenRouter
        self.openrouter_api_key: str = str(self._get_config("openrouter.api_key", "OPENROUTER_API_KEY", ""))
        self.openrouter_model: str = str(self._get_config("openrouter.model", "OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free"))
        self.openrouter_base_url: str = str(self._get_config("openrouter.base_url", "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
        self.openrouter_daily_budget_usd: float = float(self._get_config("openrouter.daily_budget_usd", "OPENROUTER_DAILY_BUDGET", 0.05))
        self.openrouter_use_for_thinking: bool = bool(self._get_config("openrouter.use_for_thinking", "OPENROUTER_USE_FOR_THINKING", True))
        
        # ChromaDB
        self.chroma_db_path: str = str(self._get_config("database.chroma_db_path", "CHROMA_DB_PATH", "./chroma"))
        
        # Trading Settings
        self.paper_trading: bool = bool(self._get_config("trading.paper_trading", "PAPER_TRADING", True))
        self.max_position_size: float = float(self._get_config("trading.max_position_size", "MAX_POSITION_SIZE", 0.05))
        self.max_daily_loss: float = float(self._get_config("trading.max_daily_loss", "MAX_DAILY_LOSS", 0.02))
        
        # Market Data
        symbols_default = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
        self.symbols_to_watch: list = self._get_config("market_data.symbols_to_watch", "SYMBOLS_TO_WATCH", symbols_default)
        self.market_hours_start: str = str(self._get_config("market_data.market_hours_start", "MARKET_HOURS_START", "09:30"))
        self.market_hours_end: str = str(self._get_config("market_data.market_hours_end", "MARKET_HOURS_END", "16:00"))
        
        # News and Sentiment
        news_default = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.marketwatch.com/rss/topstories",
        ]
        self.news_sources: list = self._get_config("news.sources", "NEWS_SOURCES", news_default)
        
        # RAG Settings
        self.max_similar_trades: int = int(self._get_config("rag.max_similar_trades", "MAX_SIMILAR_TRADES", 5))
        self.similarity_threshold: float = float(self._get_config("rag.similarity_threshold", "SIMILARITY_THRESHOLD", 0.7))
        
        # Logging
        self.log_level: str = str(self._get_config("logging.level", "LOG_LEVEL", "INFO"))
        self.log_file: str = str(self._get_config("logging.file", "LOG_FILE", "organic_bot.log"))

        # Polygon.io
        self.polygon_api_key: str = str(self._get_config("market_data.polygon_api_key", "POLYGON_API_KEY", ""))

    def _load_json_config(self) -> dict:
        """Load configuration from config.json if it exists"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    content = f.read()
                    # Substitute environment variables in the format ${VAR_NAME}
                    import re
                    def replace_env_var(match):
                        var_name = match.group(1)
                        return os.getenv(var_name, match.group(0))  # Return original if env var not found
                    
                    content = re.sub(r'\$\{([^}]+)\}', replace_env_var, content)
                    return json.loads(content)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
        return {}

    def _get_config(self, json_path: str, env_var: str, default: Any) -> Any:
        """Get configuration value from JSON file, environment variable, or default"""
        # Try JSON config first
        if self._json_config:
            try:
                value = self._json_config
                for key in json_path.split('.'):
                    value = value[key]
                return value
            except (KeyError, TypeError):
                pass
        
        # Fall back to environment variable
        env_value = os.getenv(env_var)
        if env_value is not None:
            return env_value
            
        # Use default
        return default

# Global config instance
config = Config() 