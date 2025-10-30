"""
LLM service for text generation and processing
שירות LLM ליצירת ועיבוד טקסט
"""
import requests
import json
import logging
from typing import Optional, Dict, Any

from src.config.settings import get_settings
from src.core.types import Result
from src.core.exceptions import LLMProcessingError

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with LLM API
    שירות לאינטראקציה עם LLM API
    """
    
    def __init__(self):
        """Initialize LLM service with settings"""
        self.settings = get_settings()
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Result[str]:
        """
        Generate text using LLM
        יוצר טקסט באמצעות LLM
        
        Args:
            prompt: Input prompt for LLM
            temperature: Temperature setting (defaults to config)
            top_p: Top-p setting (defaults to config)
            max_tokens: Maximum tokens (defaults to config)
            **kwargs: Additional options
        
        Returns:
            Result with generated text or error
        """
        try:
            # Build options - handle both num_predict (Ollama) and max_tokens
            options = {
                "temperature": temperature or self.settings.llm_temperature,
                "top_p": top_p or self.settings.llm_top_p,
                "num_predict": max_tokens or self.settings.max_tokens_default,
                **kwargs
            }
            
            payload = {
                "model": self.settings.llm_model,
                "prompt": prompt,
                "options": options,
                "stream": False
            }
            
            logger.info(f"🤖 Sending request to LLM: {self.settings.llm_endpoint}")
            
            response = requests.post(
                self.settings.llm_endpoint,
                json=payload,
                timeout=self.settings.llm_timeout
            )
            
            response.raise_for_status()
            
            # Parse response using the same method as old code
            generated_text = self.parse_ollama_response(response)
            
            if not generated_text or len(generated_text.strip()) == 0:
                return Result.err("Empty response from LLM")
            
            logger.info(f"✅ LLM generated {len(generated_text)} characters")
            return Result.ok(generated_text)
            
        except requests.exceptions.Timeout:
            error_msg = f"LLM request timeout after {self.settings.llm_timeout}s"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"LLM request failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error in LLM service: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
    
    def parse_ollama_response(self, response) -> str:
        """
        Parse Ollama response format (supports both response object and text)
        מפענח תגובה בפורמט Ollama
        
        Args:
            response: requests.Response object or string
        
        Returns:
            Parsed text
        """
        try:
            # If it's a response object (from requests)
            if hasattr(response, 'json'):
                # Try standard JSON first
                try:
                    raw_text = response.json().get('response', '')
                    if raw_text:
                        return self._format_output(raw_text)
                except (json.JSONDecodeError, ValueError):
                    # Try NDJSON (newline-delimited JSON)
                    lines = response.text.strip().splitlines()
                    for line in lines:
                        try:
                            obj = json.loads(line)
                            if 'response' in obj:
                                return self._format_output(obj['response'])
                        except (json.JSONDecodeError, ValueError):
                            continue
                    # Fallback: return raw text
                    return self._format_output(response.text)
            
            # If it's a string
            elif isinstance(response, str):
                try:
                    data = json.loads(response)
                    if isinstance(data, dict) and 'response' in data:
                        return self._format_output(data['response'])
                except json.JSONDecodeError:
                    # Try NDJSON
                    lines = response.strip().splitlines()
                    for line in lines:
                        try:
                            obj = json.loads(line)
                            if isinstance(obj, dict) and 'response' in obj:
                                return self._format_output(obj['response'])
                        except json.JSONDecodeError:
                            continue
                return self._format_output(response)
            
            return ""
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing Ollama response: {e}")
            return str(response) if response else ""
    
    def _format_output(self, text: str) -> str:
        """
        Format LLM output (convert markdown to HTML, etc.)
        עיצוב פלט LLM
        """
        if not text:
            return ""
        
        # Convert **text** to <strong>text</strong>
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        return text

