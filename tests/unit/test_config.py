"""
Tests for configuration management
בדיקות לניהול הגדרות
"""
import pytest
from src.config.settings import Settings, get_settings


def test_settings_loads():
    """Test that settings can be loaded"""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_settings_defaults():
    """Test that settings have correct defaults"""
    settings = get_settings()
    
    assert settings.llm_endpoint == "http://localhost:11434/api/generate"
    assert settings.llm_model == "aya-expanse:8b"
    assert settings.llm_temperature == 0.9
    assert settings.llm_top_p == 0.9
    assert settings.llm_timeout == 300


def test_settings_singleton():
    """Test that get_settings returns the same instance"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_paths():
    """Test that directory paths are set"""
    settings = get_settings()
    
    assert settings.data_dir == "data"
    assert settings.articles_dir == "articles"
    assert settings.txt_dir == "txt"
    assert settings.logs_dir == "logs-tracker"

