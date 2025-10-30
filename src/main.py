"""
New main entry point for MarketBit (optional - old main.py still works)
נקודת כניסה ראשית חדשה ל-MarketBit (אופציונלי - main.py הישן עדיין עובד)
"""
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing.pipeline import TickerProcessingPipeline
from src.core.types import Result
from src.core.logging import setup_logging
from src.data.repositories.ticker_repository import get_ticker_repository

logger = setup_logging()


def main():
    """Main entry point using new pipeline"""
    print("🦛 MarketBit Research - New Pipeline")
    print("=" * 40)
    
    # Check if ticker was provided as argument
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        print(f"Processing single ticker: {ticker}")
        
        # Get ticker info
        ticker_repo = get_ticker_repository()
        ticker_info = ticker_repo.get_ticker_info(ticker)
        if not ticker_info:
            ticker_info = {'ticker': ticker}
        
        # Process with new pipeline
        pipeline = TickerProcessingPipeline()
        result = pipeline.process_ticker(ticker, ticker_info)
        
        if result.is_ok():
            print(f"✅ Successfully processed {ticker}")
            print(f"📄 Article: {result.data.get('html_filepath', 'N/A')}")
            return 0
        else:
            print(f"❌ Failed to process {ticker}: {result.error}")
            return 1
    else:
        # Process all available tickers
        print("Processing all available tickers...")
        from src.processing.batch_processor import BatchProcessor
        
        batch_processor = BatchProcessor()
        batch_processor.process_all_available_tickers()
        return 0


if __name__ == "__main__":
    sys.exit(main())

