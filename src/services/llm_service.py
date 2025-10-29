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
            payload = {
                "model": self.settings.llm_model,
                "prompt": prompt,
                "options": {
                    "temperature": temperature or self.settings.llm_temperature,
                    "top_p": top_p or self.settings.llm_top_p,
                    "num_predict": max_tokens or self.settings.max_tokens_default,
                    **kwargs
                },
                "stream": False
            }
            
            logger.info(f"🤖 Sending request to LLM: {self.settings.llm_endpoint}")
            
            response = requests.post(
                self.settings.llm_endpoint,
                json=payload,
                timeout=self.settings.llm_timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            generated_text = response_data.get('response', '')
            
            if not generated_text:
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
    
    def parse_ollama_response(self, response_text: str) -> str:
        """
        Parse Ollama response format
        מפענח תגובה בפורמט Ollama
        
        Args:
            response_text: Raw response text
        
        Returns:
            Parsed text
        """
        try:
            # Try standard JSON
            data = json.loads(response_text)
            if isinstance(data, dict) and 'response' in data:
                return data['response']
            return response_text
        except json.JSONDecodeError:
            # Try NDJSON (newline-delimited JSON)
            lines = response_text.strip().splitlines()
            for line in lines:
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and 'response' in obj:
                        return obj['response']
                except json.JSONDecodeError:
                    continue
            # Fallback: return raw text
            return response_text

