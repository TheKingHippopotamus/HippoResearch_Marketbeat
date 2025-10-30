"""
Processing pipeline for ticker analysis
Pipeline לעיבוד ניתוח טיקרים
"""
import time
import logging
import os
from typing import Dict, Any, Optional

from src.data.scrapers.marketbeat import MarketBeatScraper
from src.services.entity_service import EntityAnalysisService
from src.services.article_processor import ArticleProcessorService
from src.processing.article_generator import ArticleHTMLGenerator
from src.config.settings import get_settings
from src.core.types import Result
from src.core.exceptions import ProcessingError
from src.core.utils import get_current_date, ensure_directory_exists

logger = logging.getLogger(__name__)


class TickerProcessingPipeline:
    """
    Main processing pipeline for ticker analysis
    Pipeline ראשי לעיבוד ניתוח טיקרים
    """
    
    def __init__(self):
        """Initialize pipeline with all services"""
        self.settings = get_settings()
        self.scraper = MarketBeatScraper()
        self.entity_service = EntityAnalysisService()
        self.article_processor = ArticleProcessorService()
        self.html_generator = ArticleHTMLGenerator()
    
    def process_ticker(
        self,
        ticker: str,
        ticker_info: Optional[Dict[str, Any]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Process a single ticker through the full pipeline
        מעבד טיקר בודד דרך כל ה-pipeline
        
        Args:
            ticker: Ticker symbol
            ticker_info: Optional ticker metadata
        
        Returns:
            Result with processing results or error
        """
        logger.info(f"🚀 Starting pipeline for {ticker}")
        logger.info("=" * 60)
        
        context = {
            'ticker': ticker,
            'ticker_info': ticker_info or {},
            'timestamp': get_current_date()
        }
        
        # Step 1: Scraping
        logger.info(f"🌐 Step 1: Scraping text for {ticker}...")
        scrape_result = self.scraper.scrape_and_save(ticker, self.settings.txt_dir)
        if scrape_result.is_err():
            return Result.err(f"Scraping failed: {scrape_result.error}")
        
        text, filename = scrape_result.data
        context['scraped_text'] = text
        context['original_filename'] = filename
        logger.info(f"✅ Scraping completed: {len(text)} characters")
        
        # Wait before LLM
        if self.settings.wait_before_llm > 0:
            logger.info(f"⏳ Waiting {self.settings.wait_before_llm}s before LLM processing...")
            time.sleep(self.settings.wait_before_llm)
        
        # Step 2: Entity Analysis
        logger.info(f"🔍 Step 2: Running entity analysis for {ticker}...")
        entity_result = self.entity_service.analyze_and_save(text, ticker)
        if entity_result.is_err():
            logger.warning(f"⚠️ Entity analysis failed: {entity_result.error}, continuing...")
        else:
            context['entity_analysis'] = entity_result.data
            context['entity_analysis_path'] = f"{self.settings.entity_analyzer_db}/{ticker}_entity_analysis_{get_current_date()}.json"
        
        # Step 3: Article Processing
        logger.info(f"🤖 Step 3: Processing {ticker} with LLM...")
        article_result = self.article_processor.process_with_contextual_prompt(
            text_block=text,
            ticker_info=ticker_info or {'ticker': ticker},
            metadata_path=context.get('entity_analysis_path'),
            original_text=text
        )
        
        if article_result.is_err():
            return Result.err(f"Article processing failed: {article_result.error}")
        
        context['processed_article'] = article_result.data
        logger.info(f"✅ LLM processing completed: {len(article_result.data)} characters")
        
        # Save processed text file (required for auto_fix_article_html)
        try:
            processed_filename = f"{ticker}_processed_{get_current_date()}.txt"
            processed_filepath = os.path.join(self.settings.txt_dir, processed_filename)
            ensure_directory_exists(self.settings.txt_dir)
            with open(processed_filepath, 'w', encoding='utf-8') as f:
                f.write(article_result.data)
            logger.info(f"✅ Processed text saved for {ticker} → {processed_filepath}")
            context['processed_filepath'] = processed_filepath
        except Exception as e:
            logger.warning(f"⚠️ Failed to save processed text file: {e}")
        
        # Step 4: Generate HTML
        logger.info(f"🎨 Step 4: Generating HTML article for {ticker}...")
        html_result = self.html_generator.generate_html_article(
            ticker=ticker,
            processed_text=article_result.data,
            ticker_info=ticker_info
        )
        
        if html_result.is_err():
            logger.warning(f"⚠️ HTML generation failed: {html_result.error}, continuing...")
        else:
            context['html_filepath'] = html_result.data
            logger.info(f"✅ HTML article generated: {html_result.data}")
            
            # Step 5: Post-processing (auto-fix and JS cleaner)
            logger.info(f"🔧 Step 5: Post-processing HTML for {ticker}...")
            try:
                from src.processing.post_processor import get_post_processor
                post_processor = get_post_processor()
                
                # Auto-fix article HTML
                if post_processor.auto_fix_article_html(ticker):
                    logger.info(f"✅ Auto-fix completed for {ticker}")
                
                # Run JS cleaner
                if post_processor.run_js_cleaner(ticker):
                    logger.info(f"✅ JS cleaner completed for {ticker}")
            except Exception as e:
                logger.warning(f"⚠️ Post-processing failed: {e}, continuing...")
        
        logger.info(f"🎉 Pipeline completed successfully for {ticker}")
        return Result.ok(context)

