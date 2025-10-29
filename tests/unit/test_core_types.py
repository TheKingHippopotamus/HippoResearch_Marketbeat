"""
Tests for core types (Result)
בדיקות ל-types בסיסיים
"""
import pytest
from src.core.types import Result


def test_result_ok():
    """Test successful result"""
    result = Result.ok("test_data")
    
    assert result.is_ok() is True
    assert result.is_err() is False
    assert result.data == "test_data"
    assert result.error is None


def test_result_err():
    """Test error result"""
    result = Result.err("test_error")
    
    assert result.is_ok() is False
    assert result.is_err() is True
    assert result.data is None
    assert result.error == "test_error"


def test_result_unwrap():
    """Test unwrap on successful result"""
    result = Result.ok("test_data")
    assert result.unwrap() == "test_data"


def test_result_unwrap_error():
    """Test unwrap raises on error result"""
    result = Result.err("test_error")
    
    with pytest.raises(ValueError):
        result.unwrap()


def test_result_unwrap_or():
    """Test unwrap_or returns default on error"""
    result = Result.err("test_error")
    assert result.unwrap_or("default") == "default"
    
    result = Result.ok("test_data")
    assert result.unwrap_or("default") == "test_data"

