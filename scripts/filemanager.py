
import csv
import json
import re
from tools.logger import setup_logging
import time, os
from datetime import datetime
logger = setup_logging()


# הפונקציה build_title עכשיו מיובאת מהמודול המרכזי
from tools.ticker_data import build_title



def create_safe_filename(ticker):
    """Create a safe filename from ticker symbol"""
    # Convert to uppercase and replace special characters
    safe_ticker = re.sub(r'[^A-Z0-9]', '_', ticker.upper())
    return safe_ticker

def get_current_timestamp():
    """Get current timestamp in the required format"""
    return datetime.now().strftime("%d/%m/%Y %H:%M")

def get_current_date():
    """Get current date in YYYYMMDD format"""
    return datetime.now().strftime("%Y%m%d")

def load_metadata():
    """Load existing metadata from JSON file"""
    metadata_file = os.path.join("data", "articles_metadata.json")
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Warning: Could not load metadata: {e}")
    return []



def save_metadata(metadata):
    """Save metadata to JSON file"""
    metadata_file = os.path.join("data", "articles_metadata.json")
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Metadata saved to {metadata_file}")
    except Exception as e:
        logger.error(f"❌ Error saving metadata: {e}")


def add_article_metadata(ticker, title, filename, summary, tags=None, ticker_info=None):
    """Add new article metadata to the JSON file, including tags and extra info"""
    metadata = load_metadata()
    new_article = {
        "ticker": ticker,
        "title": title,
        "filename": filename,
        "timestamp": get_current_timestamp(),
        "summary": summary,
        "tags": tags or []
    }
    if ticker_info:
        new_article.update(ticker_info)
    metadata.append(new_article)
    save_metadata(metadata)
    return new_article


def migrate_existing_articles():
    """Migrate existing articles to new naming format with dates"""
    try:
        articles_dir = "articles"
        if not os.path.exists(articles_dir):
            logger.warning("⚠️ Articles directory not found")
            return
        
        # Find existing article files
        existing_files = []
        for file in os.listdir(articles_dir):
            if file.endswith('_article.html'):
                ticker = file.replace('_article.html', '')
                existing_files.append((ticker, file))
        
        if not existing_files:
            logger.info("✅ No existing articles to migrate")
            return
        
        logger.info(f"🔄 Found {len(existing_files)} existing articles to migrate")
        
        # Load current metadata
        metadata = load_metadata()
        
        # Migrate each file
        for ticker, old_filename in existing_files:
            # Create new filename with current date
            safe_ticker = create_safe_filename(ticker)
            current_date = get_current_date()
            new_filename = f"{safe_ticker}_{current_date}.html"
            
            old_path = os.path.join(articles_dir, old_filename)
            new_path = os.path.join(articles_dir, new_filename)
            
            # Rename file
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                logger.info(f"✅ Renamed {old_filename} → {new_filename}")
                
                # Update metadata
                # Find existing metadata entry
                existing_entry = None
                for entry in metadata:
                    if entry.get('filename') == old_filename:
                        existing_entry = entry
                        break
                
                if existing_entry:
                    # Update filename and timestamp
                    existing_entry['filename'] = new_filename
                    existing_entry['timestamp'] = get_current_timestamp()
                    logger.info(f"✅ Updated metadata for {ticker}")
                else:
                    # Create new metadata entry
                    from tools.ticker_data import ticker_manager
                    ticker_metadata = ticker_manager._ticker_data
                    ticker_info = ticker_metadata.get(ticker, {})
                    
                    # Use the new title format (using the build_title function from central module)
                    title = build_title(ticker)
                    new_entry = {
                        "ticker": ticker,
                        "title": title,
                        "filename": new_filename,
                        "timestamp": get_current_timestamp(),
                        "summary": f"מחפשים את הסיבה לתנועות בשוק : {ticker} - ניתוח מעמיק של הצהרות הנהלה, עסקאות מוסדיות ומהלכים משפטיים."
                    }
                    metadata.append(new_entry)
                    logger.info(f"✅ Added new metadata for {ticker}")
        
        # Save updated metadata
        save_metadata(metadata)
        logger.info(f"✅ Migration completed for {len(existing_files)} articles")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")

# הפונקציה load_ticker_metadata עכשיו מיובאת מהמודול המרכזי
from tools.ticker_data import get_ticker_info, ticker_manager

def load_tickers_from_json():
    """Load tickers from JSON file"""
    try:
        with open('tickers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tickers', [])
    except Exception as e:
        logger.error(f"❌ Error loading tickers from JSON: {e}")
        return []    