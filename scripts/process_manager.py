from datetime import time
import random
import time
from tools.ticker_data import get_ticker_info
from scripts.github_automation import commit_and_push_changes
from scripts.json_manager import load_today_processed, load_unavailable_tickers, save_today_processed, save_unavailable_tickers
from tools.logger import  setup_logging
from scripts.scrap_marketBeat_keypoints import process_and_create_article, scrape_text_from_website
from scripts.ui_ux_manager import auto_fix_article_html, check_and_clear_unavailable_tickers, run_js_cleaner_on_file

logger = setup_logging()










def process_all_tickers():
    """Process all tickers from CSV file in random order, skipping already processed and unavailable ones"""
    logger.info("🚀 Starting ticker processing pipeline...")
    logger.info("="*60)
    
    # בדוק ונקה רשימת טיקרים לא זמינים אם זה יום חדש --> ui_ux_manager.py
    check_and_clear_unavailable_tickers()
    
    # load ticker from csv --> tools/ticker_data.py 
    from tools.ticker_data import ticker_manager
    ticker_metadata = ticker_manager._ticker_data
    tickers = set(ticker_metadata.keys())

    # load json -->  json_manager.py
    unavailable = load_unavailable_tickers()
    today_processed = load_today_processed()
    
    # Remove unavailable and already processed
    candidates = list(tickers - unavailable - today_processed)
    if not candidates:
        logger.info("✅ No new tickers to process today!")
        return
    
    logger.info(f"📊 Found {len(candidates)} tickers to process today")
    logger.info(f"📊 Total tickers in database: {len(tickers)}")
    logger.info(f"📊 Already processed today: {len(today_processed)}")
    logger.info(f"📊 Unavailable tickers: {len(unavailable)}")
    logger.info("="*60)
    
    random.shuffle(candidates)
    
    for i, ticker in enumerate(candidates, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Processing ticker {i}/{len(candidates)}: {ticker}")
        logger.info(f"{'='*60}")
        
        try:
            # Step 1: Scrape text from website --> scrap_marketBeat.py
            logger.info(f"🌐 Step 1: Scraping text for {ticker}...")
            result = scrape_text_from_website(ticker)
            
            if not result or not result[0]:
                logger.error(f"❌ No data found for {ticker}, adding to unavailable list")
                unavailable.add(ticker)
                save_unavailable_tickers(unavailable)
                logger.info(f"⏳ Waiting 2 seconds before next ticker...")
                time.sleep(2)
                continue

            logger.info(f"✅ Scraping completed for {ticker}")
            logger.info(f"⏳ Waiting 3 seconds before LLM processing...")
            time.sleep(3)
            
            # Step 2: Process with LLM --> scrap_marketBeat.py --> llm_processor.py
            logger.info(f"🤖 Step 2: Processing {ticker} with LLM...")
            process_and_create_article(ticker, result[0], result[1], ticker_metadata.get(ticker, {}))
            logger.info(f"✅ LLM processing completed for {ticker}")
            
            # Step 3: Update tracking  --> json_manager.py
            today_processed.add(ticker)
            save_today_processed(today_processed)
            logger.info(f"✅ Updated processing status for {ticker}")
            
            # Step 4: automation tool to fix ellements in the html --> ui_ux_manager.py
            auto_fix_article_html(ticker)
            logger.info(f"✅ Auto-fix completed for {ticker}")

            # Step 5:  --> ui_ux_manager.py &&  inject_js_cleaner.py
            run_js_cleaner_on_file(ticker)

            # Step 6: Commit and push changes    --> github_automation.py 
            #logger.info(f"📝 Step 6: Committing changes for {ticker}...")
            #if commit_and_push_changes(ticker):
                #logger.info(f"✅ Successfully committed and pushed changes for {ticker}")
            #else:
                #logger.warning(f"⚠️ Warning: Failed to commit changes for {ticker}")
            
            # Wait before next ticker
            if i < len(candidates):  # Don't wait after the last ticker
                logger.info(f"⏳ Waiting 5 seconds before next ticker...")
            time.sleep(5)
                
        except Exception as e:
            logger.error(f"❌ Error processing {ticker}: {e}")
            logger.info(f"⏳ Waiting 3 seconds before next ticker...")
            time.sleep(3)
            continue
            
    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 Completed processing all available tickers for today!")
    logger.info(f"📊 Total processed: {len(today_processed)}")
    logger.info(f"📊 Remaining unavailable: {len(unavailable)}")
    logger.info(f"{'='*60}")

def process_single_ticker(ticker):
    """Process a single ticker for development/testing purposes"""
    logger.info(f"🚀 Starting single ticker processing for: {ticker}")
    logger.info("="*60)
    
    from tools.ticker_data import ticker_manager
    ticker_metadata = ticker_manager._ticker_data
    ticker_info = ticker_metadata.get(ticker, {})
    
    if not ticker_info:
        logger.warning(f"⚠️ Warning: {ticker} not found in CSV metadata, using basic info")
        ticker_info = {"Security": ticker}
    
    logger.info(f"📊 Processing ticker: {ticker}")
    logger.info(f"📊 Company: {ticker_info.get('Security', 'Unknown')}")
    logger.info(f"📊 Sector: {ticker_info.get('GICS Sector', 'Unknown')}")
    logger.info("="*60)
    
    try:
        # Step 1: Scrape text from website
        logger.info(f"🌐 Step 1: Scraping text for {ticker}...")
        result = scrape_text_from_website(ticker)
        
        if not result or not result[0]:
            logger.error(f"❌ No data found for {ticker}")
            return False
            
        logger.info(f"✅ Scraping completed for {ticker}")
        logger.info(f"⏳ Waiting 3 seconds before LLM processing...")
        time.sleep(3)
        
        # Step 2: Process with LLM
        logger.info(f"🤖 Step 2: Processing {ticker} with LLM...")
        process_and_create_article(ticker, result[0], result[1], ticker_info)
        logger.info(f"✅ LLM processing completed for {ticker}")
        
        # Step 3: תיקון אוטומטי של עיצוב המאמר
        auto_fix_article_html(ticker)
        logger.info(f"✅ Auto-fix completed for {ticker}")

        # Step 4: הפעל את הניטור האוטומטי על הקובץ החדש
        run_js_cleaner_on_file(ticker)

        # Step 5: Commit and push changes
        logger.info(f"📝 Step 5: Committing changes for {ticker}...")
        if commit_and_push_changes(ticker):
            logger.info(f"✅ Successfully committed and pushed changes for {ticker}")
        else:
            logger.warning(f"⚠️ Warning: Failed to commit changes for {ticker}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 Successfully completed processing for {ticker}!")
        logger.info(f"{'='*60}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {ticker}: {e}")
        return False
