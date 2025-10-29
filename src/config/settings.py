"""
Application settings and configuration
הגדרות ותצורת המערכת

All configuration values are loaded from environment variables or .env file
כל הערכים נטענים מ-environment variables או מקובץ .env
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    try:
        from pydantic import BaseSettings
    except ImportError:
        from pydantic import BaseModel as BaseSettings

from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings
    הגדרות המערכת
    """
    
    # ==================== LLM Settings ====================
    # הגדרות LLM
    
    llm_endpoint: str = Field(
        default="http://localhost:11434/api/generate",
        description="LLM API endpoint URL"
    )
    
    llm_model: str = Field(
        default="aya-expanse:8b",
        description="LLM model name to use"
    )
    
    llm_temperature: float = Field(
        default=0.9,
        ge=0.0,
        le=2.0,
        description="LLM temperature (creativity level)"
    )
    
    llm_top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="LLM top_p parameter"
    )
    
    llm_timeout: int = Field(
        default=300,
        ge=10,
        description="LLM request timeout in seconds"
    )
    
    # ==================== Scraping Settings ====================
    # הגדרות גריפת אתרים
    
    marketbeat_url_template: str = Field(
        default="https://www.marketbeat.com/stocks/NASDAQ/{ticker}/news/",
        description="MarketBeat URL template for scraping"
    )
    
    selenium_timeout: int = Field(
        default=10,
        ge=1,
        description="Selenium wait timeout in seconds"
    )
    
    popup_wait_time: int = Field(
        default=3,
        ge=0,
        description="Time to wait for popup to appear (seconds)"
    )
    
    # ==================== Processing Settings ====================
    # הגדרות עיבוד
    
    retry_attempts: int = Field(
        default=3,
        ge=1,
        description="Number of retry attempts for failed operations"
    )
    
    wait_between_tickers: int = Field(
        default=5,
        ge=0,
        description="Wait time between processing tickers (seconds)"
    )
    
    wait_before_llm: int = Field(
        default=3,
        ge=0,
        description="Wait time before LLM processing (seconds)"
    )
    
    max_tokens_default: int = Field(
        default=2000,
        ge=100,
        description="Default maximum tokens for LLM output"
    )
    
    max_tokens_short: int = Field(
        default=1000,
        ge=100,
        description="Maximum tokens for short articles"
    )
    
    max_tokens_long: int = Field(
        default=3000,
        ge=100,
        description="Maximum tokens for long articles"
    )
    
    # ==================== Directory Paths ====================
    # נתיבי תיקיות
    
    data_dir: str = Field(default="data")
    articles_dir: str = Field(default="articles")
    txt_dir: str = Field(default="txt")
    entity_analyzer_db: str = Field(default="entityAnalyzer_DB")
    logs_dir: str = Field(default="logs-tracker")
    processed_tickers_dir: str = Field(default="processed_tickers")
    templates_dir: str = Field(default="templates")
    static_dir: str = Field(default="static")
    
    # ==================== File Settings ====================
    # הגדרות קבצים
    
    articles_metadata_file: str = Field(default="data/articles_metadata.json")
    ticker_data_file: str = Field(default="data/flat-ui__data.csv")
    hebrew_vocabulary_file: str = Field(default="data/hebrew_vocabulary.json")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance (singleton)
    מקבל instance גלובלי של הגדרות (singleton)
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

