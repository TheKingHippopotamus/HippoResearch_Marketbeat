"""
Ticker data repository - loads and manages ticker metadata
Repository לנתוני טיקרים - טוען ומנהל metadata של טיקרים
"""
import os
import csv
import logging
from typing import Dict, Any, Optional, Set
from pathlib import Path

from src.config.settings import get_settings
from src.core.types import Result

logger = logging.getLogger(__name__)


class TickerRepository:
    """
    Repository for ticker data and metadata
    Repository לנתוני ומטא-דאטה של טיקרים
    """
    
    def __init__(self):
        """Initialize ticker repository"""
        self.settings = get_settings()
        self._ticker_data: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
        self._load_data()
    
    def _load_data(self) -> None:
        """Load ticker data from CSV file"""
        if self._loaded:
            return
        
        csv_path = self.settings.ticker_data_file
        if not os.path.exists(csv_path):
            logger.warning(f"⚠️ Ticker data file not found: {csv_path}")
            self._loaded = True
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ticker = row.get('Ticker', '').strip().upper()
                    if ticker:
                        self._ticker_data[ticker] = {
                            'ticker': ticker,
                            'security': row.get('Security', ticker),
                            'gics_sector': row.get('GICS Sector', 'Unknown'),
                            'gics_sub_industry': row.get('GICS Sub-Industry', 'Unknown'),
                            'headquarters': row.get('Headquarters Location', 'Unknown'),
                            'founded': row.get('Date First Added', 'Unknown'),
                            'cik': row.get('CIK', ''),
                            # Include all other fields
                            **{k: v for k, v in row.items() 
                               if k not in ['Ticker', 'Security', 'GICS Sector', 
                                           'GICS Sub-Industry', 'Headquarters Location', 
                                           'Date First Added', 'CIK']}
                        }
            
            logger.info(f"✅ Loaded data for {len(self._ticker_data)} tickers from CSV")
            self._loaded = True
            
        except Exception as e:
            logger.error(f"❌ Error loading ticker data: {e}")
            self._loaded = True  # Mark as loaded even on error to prevent retries
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker information
        מקבל מידע על טיקר
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            Ticker info dict or None if not found
        """
        ticker = ticker.upper().strip()
        return self._ticker_data.get(ticker)
    
    def get_all_tickers(self) -> Set[str]:
        """
        Get all available ticker symbols
        מקבל את כל סימולי הטיקרים הזמינים
        
        Returns:
            Set of ticker symbols
        """
        return set(self._ticker_data.keys())
    
    def ticker_exists(self, ticker: str) -> bool:
        """
        Check if ticker exists in data
        בודק אם טיקר קיים בנתונים
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            True if ticker exists
        """
        return ticker.upper().strip() in self._ticker_data
    
    def get_sector_info(self, ticker: str) -> Dict[str, str]:
        """
        Get sector and industry information
        מקבל מידע על סקטור ותעשייה
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            Dict with sector and industry info
        """
        info = self.get_ticker_info(ticker)
        if not info:
            return {'sector': 'Unknown', 'industry': 'Unknown'}
        
        return {
            'sector': info.get('gics_sector', 'Unknown'),
            'industry': info.get('gics_sub_industry', 'Unknown')
        }
    
    def search_tickers(self, query: str, max_results: int = 20) -> list[Dict[str, Any]]:
        """
        Search tickers by name or symbol
        מחפש טיקרים לפי שם או סימול
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of matching ticker info dicts
        """
        query = query.upper().strip()
        results = []
        
        for ticker, info in self._ticker_data.items():
            if query in ticker or query in info.get('security', '').upper():
                results.append(info)
                if len(results) >= max_results:
                    break
        
        return results


# Global instance
_ticker_repository: Optional[TickerRepository] = None


def get_ticker_repository() -> TickerRepository:
    """
    Get global ticker repository instance (singleton)
    מקבל instance גלובלי של repository (singleton)
    
    Returns:
        TickerRepository instance
    """
    global _ticker_repository
    if _ticker_repository is None:
        _ticker_repository = TickerRepository()
    return _ticker_repository


