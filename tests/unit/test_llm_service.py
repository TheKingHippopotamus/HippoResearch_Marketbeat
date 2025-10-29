"""
Tests for LLM service
בדיקות לשירות LLM
"""
import pytest
from unittest.mock import Mock, patch

from src.services.llm_service import LLMService


@pytest.fixture
def llm_service():
    """Create an LLM service instance for testing"""
    return LLMService()


def test_llm_service_initialization(llm_service):
    """Test that LLM service initializes correctly"""
    assert llm_service is not None
    assert llm_service.settings is not None


@patch('src.services.llm_service.requests.post')
def test_llm_service_generate_success(mock_post, llm_service):
    """Test successful LLM generation (mocked)"""
    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {'response': 'Generated text'}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    result = llm_service.generate("Test prompt")
    
    assert result.is_ok()
    assert result.data == 'Generated text'


@patch('src.services.llm_service.requests.post')
def test_llm_service_generate_timeout(mock_post, llm_service):
    """Test LLM service timeout handling"""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout()
    
    result = llm_service.generate("Test prompt")
    
    assert result.is_err()
    assert "timeout" in result.error.lower()


@patch('src.services.llm_service.requests.post')
def test_llm_service_empty_response(mock_post, llm_service):
    """Test handling of empty LLM response"""
    mock_response = Mock()
    mock_response.json.return_value = {'response': ''}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    result = llm_service.generate("Test prompt")
    
    assert result.is_err()
    assert "empty" in result.error.lower()


def test_llm_service_parse_response(llm_service):
    """Test response parsing"""
    # Test standard JSON
    json_response = '{"response": "test"}'
    parsed = llm_service.parse_ollama_response(json_response)
    assert parsed == "test"
    
    # Test raw text
    raw_text = "just text"
    parsed = llm_service.parse_ollama_response(raw_text)
    assert parsed == "just text"

