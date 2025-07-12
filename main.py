#!/usr/bin/env python3
"""
MarketBit - Automated Market Research System
Simple and straightforward ticker processing
"""

import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Import modules
from scripts.logger import setup_logging
from scripts.process_manager import process_single_ticker, process_all_tickers

# Setup logging
logger = setup_logging()

def main():
    """Simple main function - just process tickers"""
    print("🦛 MarketBit Research - Simple Mode")
    print("=" * 40)
    
    # Check if ticker was provided as argument
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        print(f"Processing single ticker: {ticker}")
        success = process_single_ticker(ticker)
        if success:
            print(f"✅ Successfully processed {ticker}")
        else:
            print(f"❌ Failed to process {ticker}")
    else:
        # No arguments - process all available tickers
        print("Processing all available tickers...")
        process_all_tickers()

if __name__ == "__main__":
    main()
