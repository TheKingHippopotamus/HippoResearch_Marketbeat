#!/usr/bin/env python3
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.llm_processor import process_with_length_control, process_with_contextual_prompt
from tools.ticker_data import get_ticker_info

def test_token_control():
    # Read the COIN original text
    with open("txt/COIN_original_20250711.txt", "r", encoding="utf-8") as f:
        original_text = f.read()
    
    print("=== Testing Token Length Control ===")
    print("Original text length:", len(original_text), "characters")
    print("\n" + "="*50 + "\n")
    
    # Get ticker info for COIN
    ticker_info = get_ticker_info("COIN")
    
    # Test different lengths
    lengths_to_test = [
        ("short", 1000),
        ("default", 2000),
        ("long", 3000),
        ("custom", 1500)
    ]
    
    for length_type, max_words in lengths_to_test:
        print(f"\n--- Testing {length_type} length ({max_words} words) ---")
        
        if length_type == "custom":
            result = process_with_contextual_prompt(
                text_block=original_text,
                ticker_info=ticker_info,
                metadata_path="data/articles_metadata.json",
                max_tokens=max_words
            )
        else:
            result = process_with_length_control(
                text_block=original_text,
                ticker_info=ticker_info,
                metadata_path="data/articles_metadata.json",
                target_length=length_type
            )
        
        word_count = len(result.split())
        print(f"Result: {word_count} words")
        print(f"First 200 characters: {result[:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_token_control() 