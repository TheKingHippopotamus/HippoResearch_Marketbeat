"""
Base scraper interface
ממשק בסיסי ל-scrapers
"""
from abc import ABC, abstractmethod
from src.core.types import Result


class BaseScraper(ABC):
    """
    Base class for all scrapers
    מחלקה בסיסית לכל ה-scrapers
    
    All scrapers must implement the scrape method
    כל scraper חייב ליישם את המת地 scrape
    """
    
    @abstractmethod
    def scrape(self, ticker: str) -> Result[str]:
        """
        Scrape content for a given ticker
        גורפ תוכן עבור טיקר נתון
        
        Args:
            ticker: Ticker symbol (e.g., "AAPL")
        
        Returns:
            Result containing scraped text or error message
        """
        pass

