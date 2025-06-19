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
from html_template import create_html_content
from llm_processor import process_with_gemma
import random

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
        print("🧹 Closed popup")
    except Exception:
        print("✅ No popup found or already closed.")

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
                print(f"✅ Found AI summary block using selector: {selector}")
                return element
            except:
                continue
        
        # If specific selectors don't work, try to find by content pattern
        try:
            elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ai-summary') or contains(@class, 'bg-light-blue')]")
            for element in elements:
                if "AI Generated" in element.text or "Posted" in element.text:
                    print("✅ Found AI summary block by content pattern")
                    return element
        except:
            pass
            
        print(f"❌ Could not find AI summary block for {ticker}")
        return None
        
    except Exception as e:
        print(f"❌ Error finding summary block: {e}")
        return None

def scrape_text_from_website(ticker, output_dir="txt"):
    """Scrape text from website and save original file with date, also in /data"""
    url = f"https://translate.google.com/translate?sl=en&tl=he&u=https://www.marketbeat.com/stocks/NASDAQ/{ticker}/news/"
    driver = start_driver()
    try:
        driver.get(url)
        time.sleep(1)  # Reduced from 1.5 to 1 second

        close_popup_if_present(driver)

        os.makedirs(output_dir, exist_ok=True)
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)

        box = find_summary_block(driver, ticker)
        if box is None:
            raise Exception(f"No matching summary block found for {ticker}")

        # Extract the text content from the summary block
        summary_text = box.text
        print(f"📄 Original text length: {len(summary_text)} characters")
        print(f"📄 Original text preview: {summary_text[:100]}...")

        # Save original text file with date in filename
        current_date = get_current_date()
        original_file_name = f"{ticker}_original_{current_date}.txt"
        original_file_path = os.path.join(output_dir, original_file_name)
        with open(original_file_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"✅ Original text for {ticker} saved → {original_file_path}")

        # Also save a copy in /data
        data_file_path = os.path.join(data_dir, original_file_name)
        with open(data_file_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"✅ Original text for {ticker} also saved → {data_file_path}")

        # Verify original file was saved correctly
        with open(original_file_path, 'r', encoding='utf-8') as f:
            saved_original = f.read()
        print(f"✅ Verified original file: {len(saved_original)} characters")

        return summary_text, original_file_name
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return None, None
    finally:
        driver.quit()
        print("�� Browser closed")

def process_and_create_article(ticker, original_text, original_file_name=None, output_dir="txt"):
    """Process text with LLM and create article files"""
    try:
        # Process with LLM
        print(f"🤖 Processing {ticker} with aya-expanse:8b...")
        processed_text = process_with_gemma(original_text, ticker)
        print(f"📄 Processed text length: {len(processed_text)} characters")
        print(f"📄 Processed text preview: {processed_text[:100]}...")

        # Save processed text file with date in filename
        current_date = get_current_date()
        processed_file_name = f"{ticker}_processed_{current_date}.txt"
        processed_file_path = os.path.join(output_dir, processed_file_name)
        with open(processed_file_path, 'w', encoding='utf-8') as f:
            f.write(processed_text)
        print(f"✅ Processed text for {ticker} saved → {processed_file_path}")

        # Verify processed file was saved correctly
        with open(processed_file_path, 'r', encoding='utf-8') as f:
            saved_processed = f.read()
        print(f"✅ Verified processed file: {len(saved_processed)} characters")

        # Read original file for comparison (use new filename if provided)
        if original_file_name:
            original_file_path = os.path.join(output_dir, original_file_name)
        else:
            original_file_path = os.path.join(output_dir, f"{ticker}_original.txt")
        with open(original_file_path, 'r', encoding='utf-8') as f:
            saved_original = f.read()

        # Check if files are different
        if saved_original.strip() == saved_processed.strip():
            print("⚠️ WARNING: Original and processed files are identical!")
        else:
            print("✅ Files are different - processing worked!")

        # Create articles directory if it doesn't exist
        articles_dir = "articles"
        os.makedirs(articles_dir, exist_ok=True)

        # Create safe filename with date
        safe_ticker = create_safe_filename(ticker)
        html_filename = f"{safe_ticker}_{current_date}.html"
        html_file_path = os.path.join(articles_dir, html_filename)

        # Create HTML with processed content
        html_content = create_html_content(ticker, processed_text)
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Copy static files (logo, x icon) to articles directory
        copy_static_files(articles_dir)

        # Extract title and summary for metadata
        title = f"{ticker}: למה המניה זזה היום?"
        summary = processed_text[:200] + "..." if len(processed_text) > 200 else processed_text

        # Add metadata
        add_article_metadata(ticker, title, html_filename, summary)
        print(f"✅ Economic article for {ticker} saved → {html_file_path}")
        print(f"✅ Article metadata added to articles_metadata.json")
    except Exception as e:
        print(f"❌ Error during processing: {e}")

def capture_summary_exact(ticker, output_dir="txt"):
    """Main function to scrape and process"""
    print(f"🚀 Starting process for {ticker}")
    # Step 1: Scrape text from website
    original_text, original_file_name = scrape_text_from_website(ticker, output_dir)
    if original_text is None:
        print("❌ Failed to scrape text from website")
        return
    # Step 2: Process with LLM (after browser is closed)
    process_and_create_article(ticker, original_text, original_file_name, output_dir)
    print(f"✅ Process completed for {ticker}")

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
                print(f"✅ Copied logo.png to {output_dir}")
            
            # Copy x.png
            x_src = os.path.join(static_dir, "x.png")
            x_dst = os.path.join(output_dir, "x.png")
            if os.path.exists(x_src):
                shutil.copy2(x_src, x_dst)
                print(f"✅ Copied x.png to {output_dir}")
    except Exception as e:
        print(f"⚠️ Warning: Could not copy static files: {e}")

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
    metadata_file = "articles_metadata.json"
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load metadata: {e}")
    return []

def save_metadata(metadata):
    """Save metadata to JSON file"""
    metadata_file = "articles_metadata.json"
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"✅ Metadata saved to {metadata_file}")
    except Exception as e:
        print(f"❌ Error saving metadata: {e}")

def add_article_metadata(ticker, title, filename, summary):
    """Add new article metadata to the JSON file"""
    metadata = load_metadata()
    
    new_article = {
        "ticker": ticker,
        "title": title,
        "filename": filename,
        "timestamp": get_current_timestamp(),
        "summary": summary
    }
    
    metadata.append(new_article)
    save_metadata(metadata)
    return new_article

def migrate_existing_articles():
    """Migrate existing articles to new naming format with dates"""
    try:
        articles_dir = "articles"
        if not os.path.exists(articles_dir):
            print("⚠️ Articles directory not found")
            return
        
        # Find existing article files
        existing_files = []
        for file in os.listdir(articles_dir):
            if file.endswith('_article.html'):
                ticker = file.replace('_article.html', '')
                existing_files.append((ticker, file))
        
        if not existing_files:
            print("✅ No existing articles to migrate")
            return
        
        print(f"🔄 Found {len(existing_files)} existing articles to migrate")
        
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
                print(f"✅ Renamed {old_filename} → {new_filename}")
                
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
                    print(f"✅ Updated metadata for {ticker}")
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
                    print(f"✅ Added new metadata for {ticker}")
        
        # Save updated metadata
        save_metadata(metadata)
        print(f"✅ Migration completed for {len(existing_files)} articles")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")

def load_tickers_from_json():
    """Load tickers from JSON file"""
    try:
        with open('tickers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tickers', [])
    except Exception as e:
        print(f"❌ Error loading tickers from JSON: {e}")
        return []

def commit_and_push_changes(ticker):
    """Commit and push changes to repository after processing a ticker"""
    try:
        print(f"🔄 Committing changes for {ticker}...")
        
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
                print("🔄 Setting upstream branch and pushing...")
                subprocess.run(['git', 'push', '--set-upstream', 'origin', 'main'], check=True)
            else:
                raise e
        
        print(f"✅ Successfully committed and pushed changes for {ticker}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during git operations: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during commit: {e}")
        return False

def load_unavailable_tickers():
    """Load unavailable tickers from JSON file"""
    try:
        with open('unavailable_tickers.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_unavailable_tickers(tickers):
    """Save unavailable tickers to JSON file"""
    with open('unavailable_tickers.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(tickers)), f, ensure_ascii=False, indent=2)

def load_today_processed():
    """Load tickers processed today from JSON file"""
    today = datetime.now().strftime('%Y%m%d')
    fname = f'processed_{today}.json'
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_today_processed(tickers):
    """Save today's processed tickers to JSON file"""
    today = datetime.now().strftime('%Y%m%d')
    fname = f'processed_{today}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(tickers)), f, ensure_ascii=False, indent=2)

def process_all_tickers():
    """Process all tickers from JSON file in random order, skipping already processed and unavailable ones"""
    tickers = set(load_tickers_from_json())
    unavailable = load_unavailable_tickers()
    today_processed = load_today_processed()
    
    # Remove unavailable and already processed
    candidates = list(tickers - unavailable - today_processed)
    if not candidates:
        print("✅ No new tickers to process today!")
        return
    
    print(f"🚀 {len(candidates)} tickers left to process today.")
    random.shuffle(candidates)
    
    for ticker in candidates:
        print(f"\n{'='*50}")
        print(f"📊 Processing ticker: {ticker}")
        print(f"{'='*50}")
        try:
            # Process the ticker
            result = scrape_text_from_website(ticker)
            if result is None:
                print(f"❌ No data found for {ticker}, adding to unavailable list.")
                unavailable.add(ticker)
                save_unavailable_tickers(unavailable)
                continue
            # Step 2: Process with LLM (after browser is closed)
            process_and_create_article(ticker, result[0], result[1])
            today_processed.add(ticker)
            save_today_processed(today_processed)
            print("⏳ Waiting 3 seconds before committing...")
            time.sleep(3)
            if commit_and_push_changes(ticker):
                print(f"✅ Successfully completed processing for {ticker}")
            else:
                print(f"⚠️ Warning: Failed to commit changes for {ticker}")
            print("⏳ Waiting 5 seconds before next ticker...")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            continue
    print(f"\n🎉 Completed processing all available tickers for today!")

if __name__ == "__main__":
    process_all_tickers()
