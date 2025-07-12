#!/usr/bin/env python3
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.llm_processor import process_with_contextual_prompt
from tools.ticker_data import get_ticker_info

def test_professional_prompt():
    # Read the COIN original text
    with open("txt/COIN_original_20250711.txt", "r", encoding="utf-8") as f:
        original_text = f.read()
    
    print("=== Testing Professional Prompt ===")
    print("Original text length:", len(original_text), "characters")
    print("\n" + "="*50 + "\n")
    
    # Get ticker info for COIN
    ticker_info = get_ticker_info("COIN")
    
    # Process with the professional LLM processor
    print("Processing with professional prompt...")
    result = process_with_contextual_prompt(
        text_block=original_text,
        ticker_info=ticker_info,
        metadata_path="data/articles_metadata.json"
    )
    
    print("=== Professional Result ===")
    print(result)
    print("\n" + "="*50)
    print(f"Result length: {len(result)} characters")

if __name__ == "__main__":
    test_professional_prompt()