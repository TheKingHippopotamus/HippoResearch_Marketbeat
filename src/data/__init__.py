"""
Data layer - scrapers, repositories, models
שכבת נתונים - scrapers, repositories, models
"""
from src.data.scrapers.base import BaseScraper
from src.data.scrapers.marketbeat import MarketBeatScraper

__all__ = ['BaseScraper', 'MarketBeatScraper']

