"""
Batch processing for multiple tickers
עיבוד אצווה למספר טיקרים
"""
import random
import time
import logging
from typing import Set, List, Dict, Any

from src.processing.pipeline import TickerProcessingPipeline
from src.config.settings import get_settings
from src.data.repositories.ticker_repository import get_ticker_repository
from src.data.repositories.json_repository import get_json_repository

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Batch processor for processing multiple tickers
    מעבד אצווה לעיבוד מספר טיקרים
    """
    
    def __init__(self):
        """Initialize batch processor"""
        self.settings = get_settings()
        self.pipeline = TickerProcessingPipeline()
        self.ticker_repo = get_ticker_repository()
        self.json_repo = get_json_repository()
    
    def process_all_available_tickers(self) -> None:
        """
        Process all available tickers
        מעבד את כל הטיקרים הזמינים
        """
        logger.info("🚀 Starting ticker processing pipeline...")
        logger.info("=" * 60)
        
        # Check and clear unavailable tickers if new day
        self.json_repo.clear_unavailable_tickers_if_new_day()
        
        # Load ticker data
        all_tickers = self.ticker_repo.get_all_tickers()
        
        # Load processed and unavailable tickers
        unavailable = self.json_repo.load_unavailable_tickers()
        today_processed = self.json_repo.load_processed_tickers()
        
        # Get candidates
        candidates = list(all_tickers - unavailable - today_processed)
        
        if not candidates:
            logger.info("✅ No new tickers to process today!")
            return
        
        logger.info(f"📊 Found {len(candidates)} tickers to process today")
        logger.info(f"📊 Total tickers in database: {len(all_tickers)}")
        logger.info(f"📊 Already processed today: {len(today_processed)}")
        logger.info(f"📊 Unavailable tickers: {len(unavailable)}")
        logger.info("=" * 60)
        
        # Shuffle for random order
        random.shuffle(candidates)
        
        # Process each ticker
        for i, ticker in enumerate(candidates, 1):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"🔄 Processing ticker {i}/{len(candidates)}: {ticker}")
            logger.info(f"{'=' * 60}")
            
            try:
                # Get ticker info
                ticker_info = self.ticker_repo.get_ticker_info(ticker)
                if not ticker_info:
                    ticker_info = {'ticker': ticker}
                
                # Process with pipeline
                result = self.pipeline.process_ticker(ticker, ticker_info)
                
                if result.is_err():
                    logger.error(f"❌ Failed to process {ticker}: {result.error}")
                    unavailable.add(ticker)
                    self.json_repo.save_unavailable_tickers(unavailable)
                    
                    if i < len(candidates):
                        logger.info(f"⏳ Waiting 2 seconds before next ticker...")
                        time.sleep(2)
                    continue
                
                # Update tracking
                today_processed.add(ticker)
                self.json_repo.save_processed_tickers(today_processed)
                logger.info(f"✅ Updated processing status for {ticker}")
                
                # Wait before next ticker
                if i < len(candidates):
                    wait_time = self.settings.wait_between_tickers
                    logger.info(f"⏳ Waiting {wait_time} seconds before next ticker...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"❌ Error processing {ticker}: {e}")
                if i < len(candidates):
                    logger.info(f"⏳ Waiting 3 seconds before next ticker...")
                    time.sleep(3)
                continue
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"🎉 Completed processing all available tickers for today!")
        logger.info(f"📊 Total processed: {len(today_processed)}")
        logger.info(f"📊 Remaining unavailable: {len(unavailable)}")
        logger.info(f"{'=' * 60}")
