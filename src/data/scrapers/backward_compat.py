"""
Backward compatibility wrapper for old scraping functions
Wrapper לתאימות אחורה לפונקציות scraping ישנות
"""
import os
from typing import Optional, Tuple
from src.data.scrapers.marketbeat import MarketBeatScraper
from src.core.utils import get_current_date
import logging

logger = logging.getLogger(__name__)


def scrape_text_from_website(ticker: str, output_dir: str = "txt") -> Tuple[Optional[str], Optional[str]]:
    """
    Original function signature for backward compatibility
    פונקציה מקורית לתאימות אחורה
    
    This function maintains the old API while using the new scraper internally
    הפונקציה שומרת על ה-API הישן תוך שימוש ב-scraper החדש
    
    Args:
        ticker: Ticker symbol
        output_dir: Directory to save output file
    
    Returns:
        Tuple of (text, filename) or (None, None) on error
    """
    try:
        scraper = MarketBeatScraper()
        result = scraper.scrape_and_save(ticker, output_dir)
        
        if result.is_err():
            logger.error(f"❌ Scraping failed: {result.error}")
            return None, None
        
        return result.data  # Returns (text, filename) tuple
        
    except Exception as e:
        logger.error(f"❌ Error in scrape_text_from_website: {e}")
        return None, None

