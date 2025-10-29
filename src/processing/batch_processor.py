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
from tools.ticker_data import ticker_manager
from scripts.json_manager import (
    load_today_processed,
    load_unavailable_tickers,
    save_today_processed,
    save_unavailable_tickers
)
from scripts.ui_ux_manager import check_and_clear_unavailable_tickers
from scripts.github_automation import commit_and_push_changes
from src.core.types import Result

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
    
    def process_all_available_tickers(self) -> None:
        """
        Process all available tickers (replaces old process_all_tickers)
        מעבד את כל הטיקרים הזמינים (מחליף את process_all_tickers הישן)
        """
        logger.info("🚀 Starting ticker processing pipeline...")
        logger.info("=" * 60)
        
        # Check and clear unavailable tickers if new day
        check_and_clear_unavailable_tickers()
        
        # Load ticker data
        ticker_metadata = ticker_manager._ticker_data
        tickers = set(ticker_metadata.keys())
        
        # Load processed and unavailable tickers
        unavailable = load_unavailable_tickers()
        today_processed = load_today_processed()
        
        # Get candidates
        candidates = list(tickers - unavailable - today_processed)
        
        if not candidates:
            logger.info("✅ No new tickers to process today!")
            return
        
        logger.info(f"📊 Found {len(candidates)} tickers to process today")
        logger.info(f"📊 Total tickers in database: {len(tickers)}")
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
                ticker_info = ticker_metadata.get(ticker, {})
                
                # Process with pipeline
                result = self.pipeline.process_ticker(ticker, ticker_info)
                
                if result.is_err():
                    logger.error(f"❌ Failed to process {ticker}: {result.error}")
                    unavailable.add(ticker)
                    save_unavailable_tickers(unavailable)
                    
                    if i < len(candidates):
                        logger.info(f"⏳ Waiting 2 seconds before next ticker...")
                        time.sleep(2)
                    continue
                
                # Update tracking
                today_processed.add(ticker)
                save_today_processed(today_processed)
                logger.info(f"✅ Updated processing status for {ticker}")
                
                # Commit and push changes
                logger.info(f"📝 Committing changes for {ticker}...")
                if commit_and_push_changes(ticker):
                    logger.info(f"✅ Successfully committed and pushed changes for {ticker}")
                else:
                    logger.warning(f"⚠️ Warning: Failed to commit changes for {ticker}")
                
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

