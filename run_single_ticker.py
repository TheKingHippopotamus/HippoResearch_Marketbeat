#!/usr/bin/env python3
"""
סקריפט להרצת טיקר אחד בלבד לפיתוח ובדיקה
Usage: python run_single_ticker.py TICKER
Example: python run_single_ticker.py AAPL
"""

import sys
import os
from scripts.process_manager import process_single_ticker
from scripts.logger import setup_logging

def main():
    # Setup logging
    logger = setup_logging()
    
    # Check if ticker was provided
    if len(sys.argv) != 2:
        print("❌ Error: Please provide a ticker symbol")
        print("Usage: python run_single_ticker.py TICKER")
        print("Example: python run_single_ticker.py AAPL")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    print(f"🎯 Starting single ticker processing for: {ticker}")
    print("="*50)
    
    # Process the ticker
    success = process_single_ticker(ticker)
    
    if success:
        print(f"\n✅ Successfully completed processing for {ticker}")
    else:
        print(f"\n❌ Failed to process {ticker}")
        sys.exit(1)

if __name__ == "__main__":
    main() 