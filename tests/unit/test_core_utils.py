"""
Tests for core utilities
בדיקות ל-utilities בסיסיים
"""
from datetime import datetime
from src.core.utils import (
    get_current_date,
    get_current_timestamp,
    create_safe_filename,
    ensure_directory_exists,
    get_project_root
)


def test_get_current_date():
    """Test date formatting"""
    date = get_current_date()
    
    # Should be in YYYYMMDD format
    assert len(date) == 8
    assert date.isdigit()
    
    # Test custom format
    date_custom = get_current_date("%Y-%m-%d")
    assert "-" in date_custom


def test_get_current_timestamp():
    """Test timestamp formatting"""
    timestamp = get_current_timestamp()
    
    # Should contain date and time
    assert "/" in timestamp  # DD/MM/YYYY format
    assert ":" in timestamp  # HH:MM format


def test_create_safe_filename():
    """Test filename creation"""
    # Test basic ticker
    assert create_safe_filename("AAPL") == "AAPL"
    
    # Test with suffix
    filename = create_safe_filename("AAPL", "original")
    assert filename == "AAPL_original"
    
    # Test with special characters (should be replaced)
    filename = create_safe_filename("A-P.L", "test")
    assert "_" in filename
    assert filename.count("_") >= 2  # A-P.L has special chars


def test_get_project_root():
    """Test getting project root"""
    import os
    root = get_project_root()
    assert os.path.isabs(root)
    assert os.path.exists(root)

