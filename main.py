from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
import shutil
import json
import re
import subprocess
from datetime import datetime
from scripts.html_template import create_html_content, get_company_logo_url
from scripts.llm_processor import process_with_gemma, convert_tagged_text_to_html
import random
import csv
import logging

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('marketbit.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def close_popup_if_present(driver):
    try:
        time.sleep(3)  # Reduced from 7 to 3 seconds
        popup = driver.find_element(By.CSS_SELECTOR, "div.bg-white")
        driver.execute_script("""
            arguments[0].style.display = 'none';
            arguments[0].remove();
        """, popup)
        logger.info("🧹 Closed popup")
    except Exception:
        logger.info("✅ No popup found or already closed.")

def find_summary_block(driver, ticker):
    """Find the AI summary block with the specific structure"""
    try:
        # Wait for the page to load - reduced wait time
        wait = WebDriverWait(driver, 5)  # Reduced from 10 to 5 seconds
        
        # Look for the AI summary block with the specific classes
        summary_selectors = [
            "div.border.rounded.p-3.font-small.mb-3.bg-light-blue.ai-summary",
            "div.ai-summary",
            "div.bg-light-blue.ai-summary",
            "div[class*='ai-summary']"
        ]
        
        for selector in summary_selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f"✅ Found AI summary block using selector: {selector}")
                return element
            except:
                continue
        
        # If specific selectors don't work, try to find by content pattern
        try:
            elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ai-summary') or contains(@class, 'bg-light-blue')]")
            for element in elements:
                if "AI Generated" in element.text or "Posted" in element.text:
                    logger.info("✅ Found AI summary block by content pattern")
                    return element
        except:
            pass
            
        logger.error(f"❌ Could not find AI summary block for {ticker}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error finding summary block: {e}")
        return None

def scrape_text_from_website(ticker, output_dir="txt"):
    """Scrape text from website and save only clean text file with date"""
    url = f"https://translate.google.com/translate?sl=en&tl=he&u=https://www.marketbeat.com/stocks/NASDAQ/{ticker}/news/"
    driver = start_driver()
    try:
        logger.info(f"🌐 Opening URL for {ticker}...")
        driver.get(url)
        time.sleep(1)

        close_popup_if_present(driver)

        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"🔍 Looking for AI summary block for {ticker}...")
        box = find_summary_block(driver, ticker)
        if box is None:
            raise Exception(f"No matching summary block found for {ticker}")

        # Extract only the clean text content
        summary_text = box.text
        logger.info(f"📄 Original text length: {len(summary_text)} characters")
        logger.info(f"📄 Original text preview: {summary_text[:100]}...")

        # Save only the clean text file with date
        current_date = get_current_date()
        original_file_name = f"{ticker}_original_{current_date}.txt"
        original_file_path = os.path.join(output_dir, original_file_name)
        
        with open(original_file_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        logger.info(f"✅ Original text for {ticker} saved → {original_file_path}")

        # Verify original file was saved correctly
        with open(original_file_path, 'r', encoding='utf-8') as f:
            saved_original = f.read()
        logger.info(f"✅ Verified original file: {len(saved_original)} characters")

        return summary_text, original_file_name
    except Exception as e:
        logger.error(f"❌ Error during scraping: {e}")
        return None, None
    finally:
        driver.quit()
        logger.info("🌐 Browser closed")

def extract_head_section(template_path="arcive/test_V_new_style.html"):
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    match = re.search(r'(<head[\s\S]*?</head>)', html, re.IGNORECASE)
    return match.group(1) if match else ""

def process_and_create_article(ticker, original_text, original_file_name=None, ticker_info=None, output_dir="txt"):
    """Process text with LLM and create article files"""
    try:
        ticker_info = ticker_info or {}
        
        # Use the clean text for LLM processing
        if original_file_name:
            # Use the clean text file
            original_file_path = os.path.join(output_dir, original_file_name)
            with open(original_file_path, 'r', encoding='utf-8') as f:
                text_for_llm = f.read()
        else:
            text_for_llm = original_text
            
        logger.info(f"🤖 Processing {ticker} with aya-expanse:8b...")
        processed_text = process_with_gemma(text_for_llm, ticker_info)
        logger.info(f"📄 Processed text length: {len(processed_text)} characters")
        logger.info(f"📄 Processed text preview: {processed_text[:100]}...")

        # Save processed text file with date in filename
        current_date = get_current_date()
        processed_file_name = f"{ticker}_processed_{current_date}.txt"
        processed_file_path = os.path.join(output_dir, processed_file_name)
        with open(processed_file_path, 'w', encoding='utf-8') as f:
            f.write(processed_text)
        logger.info(f"✅ Processed text for {ticker} saved → {processed_file_path}")

        # Verify processed file was saved correctly
        with open(processed_file_path, 'r', encoding='utf-8') as f:
            saved_processed = f.read()
        logger.info(f"✅ Verified processed file: {len(saved_processed)} characters")

        # במקום clean_processed_text, נשתמש ב-convert_tagged_text_to_html כדי להמיר רק סימונים ל-HTML
        cleaned_text = convert_tagged_text_to_html(processed_text)
        logger.info(f"🧹 Cleaned text length: {len(cleaned_text)} characters")
        
        # Save the cleaned file
        cleaned_file_name = f"{ticker}_cleaned_{current_date}.txt"
        cleaned_file_path = os.path.join(output_dir, cleaned_file_name)
        with open(cleaned_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        logger.info(f"✅ Cleaned text for {ticker} saved → {cleaned_file_path}")

        # Read original file for comparison
        if original_file_name:
            original_file_path = os.path.join(output_dir, original_file_name)
        else:
            original_file_path = os.path.join(output_dir, f"{ticker}_original.txt")
            
        with open(original_file_path, 'r', encoding='utf-8') as f:
            saved_original = f.read()

        # Check if files are different
        if saved_original.strip() == processed_text.strip():
            logger.warning("⚠️ WARNING: Original and processed files are identical!")
        else:
            logger.info("✅ Files are different - processing worked!")

        # Create articles directory if it doesn't exist
        articles_dir = "articles"
        os.makedirs(articles_dir, exist_ok=True)

        # Create safe filename with date
        safe_ticker = create_safe_filename(ticker)
        html_filename = f"{safe_ticker}_{current_date}.html"
        html_file_path = os.path.join(articles_dir, html_filename)

        # Create HTML with cleaned content and tags, pass extra info
        logger.info(f"🎨 Creating HTML article for {ticker}...")
        formatted_content = convert_tagged_text_to_html(cleaned_text)
        logo_url = get_company_logo_url(ticker, ticker_info)
        company_name = ticker_info.get('Security') or ticker
        dynamic_title = f"{company_name} ({ticker}) - מחקר כלכלי מתקדם | Hippopotamus Research"
        timestamp = get_current_timestamp()
        # Load the new template
        with open("article_template.html", "r", encoding="utf-8") as f:
            template = f.read()
        # Replace placeholders
        full_html = template.replace("{{TITLE}}", dynamic_title)
        full_html = full_html.replace("{{TICKER}}", ticker)
        full_html = full_html.replace("{{ARTICLE_BODY}}", formatted_content)
        full_html = full_html.replace("{{TIMESTAMP}}", timestamp)
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        # Copy static files (logo, x icon) to articles directory
        copy_static_files(articles_dir)

        # Extract title and summary for metadata
        title = f"{ticker}: למה המניה זזה היום?"
        summary = processed_text[:200] + "..." if len(processed_text) > 200 else processed_text

        # Add metadata (now without tags)
        add_article_metadata(ticker, title, html_filename, summary, ticker_info=ticker_info)
        logger.info(f"✅ Economic article for {ticker} saved → {html_file_path}")
        logger.info(f"✅ Article metadata added to articles_metadata.json")
    except Exception as e:
        logger.error(f"❌ Error during processing: {e}")

def capture_summary_exact(ticker, output_dir="txt"):
    """Main function to scrape and process"""
    logger.info(f"🚀 Starting process for {ticker}")
    # Step 1: Scrape text from website
    original_text, original_file_name = scrape_text_from_website(ticker, output_dir)
    if original_text is None:
        logger.error("❌ Failed to scrape text from website")
        return
    # Step 2: Process with LLM (after browser is closed)
    # נטען את המידע מה-CSV עבור הטיקר
    ticker_metadata = load_ticker_metadata()
    ticker_info = ticker_metadata.get(ticker, {})
    process_and_create_article(ticker, original_text, original_file_name, ticker_info=ticker_info, output_dir=output_dir)
    logger.info(f"✅ Process completed for {ticker}")

def copy_static_files(output_dir):
    """Copy static files (logo, x icon) to output directory"""
    try:
        static_dir = "static"
        if os.path.exists(static_dir):
            # Copy logo.png
            logo_src = os.path.join(static_dir, "logo.png")
            logo_dst = os.path.join(output_dir, "logo.png")
            if os.path.exists(logo_src):
                shutil.copy2(logo_src, logo_dst)
                logger.info(f"✅ Copied logo.png to {output_dir}")
            
            # Copy x.png
            x_src = os.path.join(static_dir, "x.png")
            x_dst = os.path.join(output_dir, "x.png")
            if os.path.exists(x_src):
                shutil.copy2(x_src, x_dst)
                logger.info(f"✅ Copied x.png to {output_dir}")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not copy static files: {e}")

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
                    new_entry = {
                        "ticker": ticker,
                        "title": f"{ticker}: למה המניה זזה היום?",
                        "filename": new_filename,
                        "timestamp": get_current_timestamp(),
                        "summary": f"ניתוח סיבתיות של תנועות מניה: {ticker} - ניתוח מעמיק של הצהרות הנהלה, עסקאות מוסדיות ומהלכים משפטיים."
                    }
                    metadata.append(new_entry)
                    logger.info(f"✅ Added new metadata for {ticker}")
        
        # Save updated metadata
        save_metadata(metadata)
        logger.info(f"✅ Migration completed for {len(existing_files)} articles")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")

def load_ticker_metadata():
    """Load ticker metadata from CSV into a dict: {ticker: {fields...}}"""
    csv_path = os.path.join("data", "flat-ui__data-Thu Jun 19 2025.csv")
    ticker_info = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row.get('Tickers')
                if ticker and ticker.strip():
                    ticker_info[ticker.strip()] = {
                        "Security": row.get("Security", "").strip(),
                        "GICS Sector": row.get("GICS Sector", "").strip(),
                        "GICS Sub-Industry": row.get("GICS Sub-Industry", "").strip(),
                        "Headquarters Location": row.get("Headquarters Location", "").strip()
                    }
    except Exception as e:
        logger.error(f"❌ Error loading ticker metadata from CSV: {e}")
    return ticker_info

def load_tickers_from_json():
    """Load tickers from JSON file"""
    try:
        with open('tickers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tickers', [])
    except Exception as e:
        logger.error(f"❌ Error loading tickers from JSON: {e}")
        return []

def commit_and_push_changes(ticker):
    """Commit and push changes to repository after processing a ticker"""
    try:
        logger.info(f"🔄 Committing changes for {ticker}...")
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Create commit message
        commit_message = f"הוספת כתבה חדשה: {ticker} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Try to push, if it fails due to upstream issue, set upstream and try again
        try:
            subprocess.run(['git', 'push'], check=True)
        except subprocess.CalledProcessError as e:
            if "no upstream branch" in str(e) or "set-upstream" in str(e):
                logger.info("🔄 Setting upstream branch and pushing...")
                subprocess.run(['git', 'push', '--set-upstream', 'origin', 'main'], check=True)
            else:
                raise e
        
        logger.info(f"✅ Successfully committed and pushed changes for {ticker}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error during git operations: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during commit: {e}")
        return False

def load_unavailable_tickers():
    """Load unavailable tickers from JSON file"""
    try:
        with open('processed_tickers/unavailable_tickers.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_unavailable_tickers(tickers):
    """Save unavailable tickers to JSON file"""
    with open('processed_tickers/unavailable_tickers.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(tickers)), f, ensure_ascii=False, indent=2)

def load_today_processed():
    """Load tickers processed today from JSON file"""
    today = datetime.now().strftime('%Y%m%d')
    fname = f'processed_tickers/processed_{today}.json'
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_today_processed(tickers):
    """Save today's processed tickers to JSON file"""
    today = datetime.now().strftime('%Y%m%d')
    fname = f'processed_tickers/processed_{today}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(tickers)), f, ensure_ascii=False, indent=2)

def process_all_tickers():
    """Process all tickers from CSV file in random order, skipping already processed and unavailable ones"""
    logger.info("🚀 Starting ticker processing pipeline...")
    logger.info("="*60)
    
    ticker_metadata = load_ticker_metadata()
    tickers = set(ticker_metadata.keys())
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
            # Step 1: Scrape text from website
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
            
            # Step 2: Process with LLM
            logger.info(f"🤖 Step 2: Processing {ticker} with LLM...")
            process_and_create_article(ticker, result[0], result[1], ticker_metadata.get(ticker, {}))
            logger.info(f"✅ LLM processing completed for {ticker}")
            
            # Step 3: Update tracking
            today_processed.add(ticker)
            save_today_processed(today_processed)
            logger.info(f"✅ Updated processing status for {ticker}")
            
            # Step 4: Commit and push changes
            logger.info(f"⏳ Waiting 3 seconds before committing changes...")
            time.sleep(3)
            logger.info(f"📝 Step 3: Committing changes for {ticker}...")
            
            if commit_and_push_changes(ticker):
                logger.info(f"✅ Successfully committed and pushed changes for {ticker}")
            else:
                logger.warning(f"⚠️ Warning: Failed to commit changes for {ticker}")
            
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

if __name__ == "__main__":
    process_all_tickers()
