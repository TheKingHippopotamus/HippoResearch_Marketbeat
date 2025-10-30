"""
JSON data repository for managing processed tickers and tracking data
Repository לניהול טיקרים מעובדים ונתוני מעקב
"""
import os
import json
import logging
from typing import Set, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.config.settings import get_settings
from src.core.utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class JSONRepository:
    """
    Repository for JSON-based data storage
    Repository לאחסון נתונים מבוסס JSON
    """
    
    def __init__(self):
        """Initialize JSON repository"""
        self.settings = get_settings()
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        directories = [
            self.settings.processed_tickers_dir,
            self.settings.entity_analyzer_db
        ]
        for directory in directories:
            ensure_directory_exists(directory)
    
    def load_processed_tickers(self, date: Optional[str] = None) -> Set[str]:
        """
        Load set of processed tickers for a date
        טוען רשימת טיקרים מעובדים לתאריך
        
        Args:
            date: Date string (YYYYMMDD), defaults to today
        
        Returns:
            Set of ticker symbols
        """
        if date is None:
            from src.core.utils import get_current_date
            date = get_current_date()
        
        filepath = os.path.join(
            self.settings.processed_tickers_dir,
            f"processed_{date}.json"
        )
        
        if not os.path.exists(filepath):
            return set()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('tickers', []))
        except Exception as e:
            logger.warning(f"⚠️ Error loading processed tickers: {e}")
            return set()
    
    def save_processed_tickers(self, tickers: Set[str], date: Optional[str] = None) -> bool:
        """
        Save set of processed tickers for a date
        שומר רשימת טיקרים מעובדים לתאריך
        
        Args:
            tickers: Set of ticker symbols
            date: Date string (YYYYMMDD), defaults to today
        
        Returns:
            True if saved successfully
        """
        if date is None:
            from src.core.utils import get_current_date
            date = get_current_date()
        
        filepath = os.path.join(
            self.settings.processed_tickers_dir,
            f"processed_{date}.json"
        )
        
        try:
            ensure_directory_exists(self.settings.processed_tickers_dir)
            data = {
                'date': date,
                'tickers': sorted(list(tickers)),
                'count': len(tickers),
                'updated_at': datetime.now().isoformat()
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ Error saving processed tickers: {e}")
            return False
    
    def load_unavailable_tickers(self) -> Set[str]:
        """
        Load set of unavailable tickers
        טוען רשימת טיקרים לא זמינים
        
        Returns:
            Set of ticker symbols
        """
        filepath = os.path.join(
            self.settings.processed_tickers_dir,
            "unavailable_tickers.json"
        )
        
        if not os.path.exists(filepath):
            return set()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('tickers', []))
        except Exception as e:
            logger.warning(f"⚠️ Error loading unavailable tickers: {e}")
            return set()
    
    def save_unavailable_tickers(self, tickers: Set[str]) -> bool:
        """
        Save set of unavailable tickers
        שומר רשימת טיקרים לא זמינים
        
        Args:
            tickers: Set of ticker symbols
        
        Returns:
            True if saved successfully
        """
        filepath = os.path.join(
            self.settings.processed_tickers_dir,
            "unavailable_tickers.json"
        )
        
        try:
            ensure_directory_exists(self.settings.processed_tickers_dir)
            data = {
                'tickers': sorted(list(tickers)),
                'count': len(tickers),
                'updated_at': datetime.now().isoformat()
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ Error saving unavailable tickers: {e}")
            return False
    
    def clear_unavailable_tickers_if_new_day(self) -> bool:
        """
        Clear unavailable tickers if new day
        מנקה טיקרים לא זמינים אם יום חדש
        
        Returns:
            True if cleared
        """
        from src.core.utils import get_current_date
        today = get_current_date()
        
        last_clear_file = os.path.join(
            self.settings.processed_tickers_dir,
            "last_clear_date.txt"
        )
        
        try:
            if os.path.exists(last_clear_file):
                with open(last_clear_file, 'r') as f:
                    last_date = f.read().strip()
                if last_date == today:
                    return False  # Already cleared today
            
            # Clear unavailable tickers
            self.save_unavailable_tickers(set())
            
            # Update last clear date
            with open(last_clear_file, 'w') as f:
                f.write(today)
            
            logger.info(f"✅ Cleared unavailable tickers for new day: {today}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error clearing unavailable tickers: {e}")
            return False


# Global instance
_json_repository: Optional[JSONRepository] = None


def get_json_repository() -> JSONRepository:
    """
    Get global JSON repository instance (singleton)
    מקבל instance גלובלי של repository (singleton)
    
    Returns:
        JSONRepository instance
    """
    global _json_repository
    if _json_repository is None:
        _json_repository = JSONRepository()
    return _json_repository


