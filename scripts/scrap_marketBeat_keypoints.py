from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
from scripts.filemanager import add_article_metadata, get_current_timestamp, get_current_date, create_safe_filename
from tools.ticker_data import build_title, get_company_logo_url
# Import copy_static_files from ui_ux_manager instead of main to avoid circular import
from scripts.ui_ux_manager import copy_static_files
from tools.logger import setup_logging, log_stage
# Initialize logger
logger = setup_logging()
from tools.html_template import  get_company_logo_url
from tools.llm_processor import process_with_contextual_prompt
from tools.text_processing import convert_tagged_text_to_html





def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
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




# Add the log_stage decorator to all major process functions
@log_stage("SCRAPE")
def scrape_text_from_website(ticker, output_dir="txt"):
    """Scrape text from website and save only clean text file with date"""
    url = f"https://www.marketbeat.com/stocks/NASDAQ/{ticker}/news/"
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

@log_stage("LLM")
def process_and_create_article(ticker, original_text, original_file_name=None, ticker_info=None, output_dir="txt"):
    """Process text with LLM and create article files"""
    try:
        ticker_info = ticker_info or {}
        
        # Add ticker to ticker_info for entity analysis
        ticker_info['ticker'] = ticker
        
        # Use the clean text for LLM processing
        if original_file_name:
            # Use the clean text file
            original_file_path = os.path.join(output_dir, original_file_name)
            with open(original_file_path, 'r', encoding='utf-8') as f:
                text_for_llm = f.read()
        else:
            text_for_llm = original_text
            
        logger.info(f"🤖 Processing {ticker} with aya-expanse:8b...")
        logger.info(f"🔍 Running entity analysis for {ticker}...")
        
        # Run entity analysis and save results
        try:
            from tools.entity_analyzer import get_entity_analyzer, save_entity_analysis
            analyzer = get_entity_analyzer()
            entity_analysis = analyzer.analyze_text(text_for_llm, ticker)
            if entity_analysis:
                save_entity_analysis(entity_analysis, ticker)
                logger.info(f"✅ Entity analysis completed for {ticker}")
            else:
                logger.warning(f"⚠️ No entity analysis results for {ticker}")
        except Exception as e:
            logger.warning(f"⚠️ Entity analysis failed for {ticker}: {e}")
        
        processed_text = process_with_contextual_prompt(text_for_llm, ticker_info)
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

        # Create HTML with processed content (not cleaned_text which is already HTML)
        logger.info(f"🎨 Creating HTML article for {ticker}...")
        formatted_content = convert_tagged_text_to_html(processed_text)
        logo_url = get_company_logo_url(ticker)
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

        # Extract title and summary for metadata - use the formatted HTML content for summary
        title = build_title(ticker)
        # Remove HTML tags for summary and take first 200 characters
        import re
        clean_summary = re.sub(r'<[^>]+>', '', formatted_content)
        summary = clean_summary[:200] + "..." if len(clean_summary) > 200 else clean_summary

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
    from tools.ticker_data import ticker_manager
    ticker_metadata = ticker_manager._ticker_data
    ticker_info = ticker_metadata.get(ticker, {})
    process_and_create_article(ticker, original_text, original_file_name, ticker_info=ticker_info, output_dir=output_dir)
    logger.info(f"✅ Process completed for {ticker}")
