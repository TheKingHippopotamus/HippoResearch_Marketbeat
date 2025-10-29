"""
Common utilities used across the application
Utilities משותפים לכל המערכת
"""
from datetime import datetime
import re
import os
from typing import Optional


def get_current_date(format_str: str = "%Y%m%d") -> str:
    """
    Get current date in specified format
    מקבל תאריך נוכחי בפורמט המבוקש
    
    Args:
        format_str: Date format string (default: YYYYMMDD)
    
    Returns:
        Formatted date string
    """
    return datetime.now().strftime(format_str)


def get_current_timestamp(format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Get current timestamp in specified format
    מקבל timestamp נוכחי בפורמט המבוקש
    
    Args:
        format_str: Timestamp format string
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_str)


def create_safe_filename(ticker: str, suffix: Optional[str] = None) -> str:
    """
    Create a safe filename from ticker symbol
    יוצר שם קובץ בטוח מסימול טיקר
    
    Args:
        ticker: Ticker symbol (e.g., "AAPL")
        suffix: Optional suffix to add (e.g., "original", "processed")
    
    Returns:
        Safe filename string
    """
    safe_ticker = re.sub(r'[^A-Z0-9]', '_', ticker.upper())
    
    if suffix:
        return f"{safe_ticker}_{suffix}"
    return safe_ticker


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't
    מוודא שתיקיה קיימת, יוצר אותה אם לא
    
    Args:
        directory_path: Path to directory
    """
    os.makedirs(directory_path, exist_ok=True)


def get_project_root() -> str:
    """
    Get the project root directory
    מקבל את תיקיית הבסיס של הפרויקט
    
    Returns:
        Path to project root
    """
    # This file is in src/core, so project root is 2 levels up
    current_file = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

