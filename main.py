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
import csv

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

def process_and_create_article(ticker, original_text, original_file_name=None, ticker_info=None, output_dir="txt"):
    """Process text with LLM and create article files, including causal tags and extra metadata"""
    try:
        ticker_info = ticker_info or {}
        # קרא תמיד מהקובץ אם יש original_file_name
        if original_file_name:
            original_file_path = os.path.join(output_dir, original_file_name)
            with open(original_file_path, 'r', encoding='utf-8') as f:
                text_for_llm = f.read()
        else:
            text_for_llm = original_text
        print(f"🤖 Processing {ticker} with aya-expanse:8b...")
        processed_text = process_with_gemma(text_for_llm, ticker_info)
        print(f"📄 Processed text length: {len(processed_text)} characters")
        print(f"📄 Processed text preview: {processed_text[:100]}...")
        tags = []
        print(f"🏷️ Tags: {tags}")

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
        if saved_original.strip() == processed_text.strip():
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

        # Create HTML with processed content and tags, pass extra info
        html_content, ticker_badge_with_logo = create_html_content(ticker, processed_text, ticker_info=ticker_info)
        
        # Create the full HTML page with the ticker badge in the header
        full_html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>דוח ניתוח סיבתיות - {ticker}</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{
            --primary-color: #1a1a2e;
            --secondary-color: #16213e;
            --accent-color: #0f3460;
            --highlight-color: #e94560;
            --text-light: #ffffff;
            --text-dark: #1a1a2e;
            --gradient-primary: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            --gradient-accent: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
            --shadow-primary: 0 20px 40px rgba(26, 26, 46, 0.15);
            --shadow-accent: 0 10px 30px rgba(233, 69, 96, 0.3);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Heebo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--gradient-primary);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
            color: var(--text-light);
            line-height: 1.6;
            position: relative;
            overflow-x: hidden;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(233, 69, 96, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(15, 52, 96, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(22, 33, 62, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }}
        
        .container {{
            max-width: 98vw;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: var(--shadow-primary);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .header {{
            background: var(--gradient-primary);
            color: var(--text-light);
            padding: 0;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(circle at 30% 30%, rgba(233, 69, 96, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 70% 70%, rgba(15, 52, 96, 0.2) 0%, transparent 50%);
            animation: float 6s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-20px) rotate(180deg); }}
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
            padding: 40px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .logo-section {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .logo-container {{
            position: relative;
            width: 120px;
            height: 120px;
            background: var(--gradient-accent);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-accent);
            animation: pulse 2s ease-in-out infinite;
            overflow: hidden;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .logo-container::before {{
            content: '';
            position: absolute;
            top: -5px;
            left: -5px;
            right: -5px;
            bottom: -5px;
            background: var(--gradient-accent);
            border-radius: 50%;
            z-index: -1;
            opacity: 0.3;
            animation: pulse 2s ease-in-out infinite reverse;
        }}
        
        .logo-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 50%;
            display: block;
        }}
        
        .logo-image img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 50%;
        }}
        
        .brand-info {{
            text-align: right;
        }}
        
        .brand-name {{
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 5px;
            background: linear-gradient(45deg, #ffffff, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .brand-subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .social-section {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .twitter-link {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.1);
            padding: 12px 20px;
            border-radius: 25px;
            text-decoration: none;
            color: var(--text-light);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .twitter-link:hover {{
            background: rgba(233, 69, 96, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(233, 69, 96, 0.3);
        }}
        
        .twitter-icon {{
            width: 20px;
            height: 20px;
            object-fit: contain;
        }}
        
        .ticker-badge {{
            background: var(--gradient-accent);
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 1.1em;
            box-shadow: var(--shadow-accent);
            display: inline-flex;
            align-items: center;
        }}
        
        .content {{
            padding: 50px 40px;
            color: var(--text-dark);
        }}
        
        .article-content {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            border-left: 5px solid var(--highlight-color);
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            position: relative;
        }}
        
        .article-content::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-accent);
            border-radius: 15px 15px 0 0;
        }}
        
        .article-content p {{
            margin-bottom: 20px;
            text-align: justify;
            line-height: 1.8;
            font-size: 1.05em;
        }}
        
        .article-content p:last-child {{
            margin-bottom: 0;
        }}
        
        .section-header {{
            color: var(--accent-color);
            font-size: 1.4em;
            font-weight: 600;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--highlight-color);
            position: relative;
        }}
        
        .section-header::before {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 50px;
            height: 2px;
            background: var(--gradient-accent);
        }}
        
        .section-header:first-child {{
            margin-top: 0;
        }}
        
        .highlight-box {{
            background: var(--gradient-primary);
            color: var(--text-light);
            padding: 25px;
            border-radius: 12px;
            margin: 25px 0;
            box-shadow: var(--shadow-primary);
            position: relative;
            overflow: hidden;
        }}
        
        .highlight-box::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            transform: translateX(-100%);
            animation: shine 3s ease-in-out infinite;
        }}
        
        @keyframes shine {{
            0% {{ transform: translateX(-100%); }}
            50% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .highlight-box strong {{
            color: var(--highlight-color);
        }}
        
        .footer {{
            background: var(--gradient-primary);
            padding: 30px;
            text-align: center;
            color: var(--text-light);
            position: relative;
        }}
        
        .footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--gradient-accent);
        }}
        
        .timestamp {{
            color: var(--highlight-color);
            font-weight: 500;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .source {{
            font-style: italic;
            opacity: 0.8;
            font-size: 0.95em;
        }}
        
        .disclaimer {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid #fdcb6e;
            border-radius: 12px;
            padding: 20px;
            margin-top: 30px;
            font-size: 0.95em;
            color: #856404;
            position: relative;
        }}
        
        .disclaimer::before {{
            content: '⚠️';
            position: absolute;
            top: -10px;
            right: 20px;
            background: #fff3cd;
            padding: 0 10px;
            font-size: 1.2em;
        }}
        
        .disclaimer strong {{
            color: #856404;
        }}
        
        .disclaimer h3 {{
            color: var(--accent-color);
            margin-top: 15px;
            font-size: 1.2em;
        }}
        
        .back-home-btn {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: var(--gradient-accent);
            color: var(--text-light);
            font-weight: 600;
            font-size: 1.1em;
            padding: 12px 28px;
            border: none;
            border-radius: 30px;
            box-shadow: var(--shadow-accent);
            text-decoration: none;
            margin: 30px 0 20px 0;
            transition: background 0.2s, transform 0.2s;
            cursor: pointer;
        }}
        .back-home-btn:hover {{
            background: var(--highlight-color);
            color: #fff;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 8px 24px rgba(233, 69, 96, 0.25);
        }}
        .back-home-btn i {{
            font-size: 1.2em;
        }}
        
        .scroll-hint {{
            display: none;
            text-align: center;
            color: var(--highlight-color);
            font-size: 1.1em;
            margin-bottom: 10px;
            opacity: 0.85;
            user-select: none;
            pointer-events: none;
            font-weight: 500;
            letter-spacing: 0.02em;
        }}
        .scroll-hint i {{
            font-size: 1.5em;
            vertical-align: middle;
            margin: 0 5px;
            animation: bounce-x 1.5s infinite;
        }}
        @keyframes bounce-x {{
            0%, 100% {{ transform: translateX(0); }}
            50% {{ transform: translateX(12px); }}
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .header-content {{
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }}
            .brand-info {{
                text-align: center;
            }}
            .brand-name {{
                font-size: 1.8em;
            }}
            .content {{
                padding: 30px 20px;
                font-size: 1em;
            }}
            .article-content {{
                padding: 10px 0 0 0;
                background: none;
                border-radius: 0;
                border: none;
                box-shadow: none;
                word-spacing: 0.05em;
            }}
            .article-content p, .article-content h3, .article-content span, .article-content strong, .article-content em {{
                word-spacing: 0.05em;
            }}
            .logo-container {{
                width: 80px;
                height: 80px;
            }}
            .logo-image {{
                width: 70px;
                height: 70px;
            }}
            .back-home-btn {{
                width: 100%;
                justify-content: center;
                font-size: 1em;
                padding: 12px 0;
            }}
        }}
        .tags-bar {{
            margin-bottom: 24px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .tag-badge {{
            background: linear-gradient(90deg, #e94560 0%, #0f3460 100%);
            color: #fff;
            border-radius: 16px;
            padding: 6px 16px;
            font-size: 1em;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(233,69,96,0.08);
            letter-spacing: 0.02em;
            display: inline-block;
            margin-bottom: 2px;
            border: none;
            outline: none;
            transition: background 0.2s;
        }}
        .tag-badge:hover {{
            background: linear-gradient(90deg, #0f3460 0%, #e94560 100%);
        }}
        .company-badges-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 18px;
            overflow-x: auto;
            padding-bottom: 2px;
            scrollbar-width: thin;
        }}
        .company-badge {{
            background: linear-gradient(90deg, #0f3460 0%, #e94560 100%);
            color: #fff;
            border-radius: 16px;
            padding: 6px 16px;
            font-size: 1em;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(15,52,96,0.08);
            letter-spacing: 0.02em;
            display: inline-block;
            margin-bottom: 2px;
            border: none;
            outline: none;
            transition: background 0.2s;
            white-space: nowrap;
        }}
        .company-badge:hover {{
            background: linear-gradient(90deg, #e94560 0%, #0f3460 100%);
        }}
        @media (max-width: 768px) {{
            .company-badges-bar {{
                gap: 7px;
                margin-bottom: 12px;
                padding-bottom: 4px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            .company-badge {{
                font-size: 0.95em;
                padding: 5px 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-container">
                        <img src="logo.png" alt="Logo" class="logo-image">
                    </div>
                    <div class="brand-info">
                        <div class="brand-name">Hippopotamus Research</div>
                        <div class="brand-subtitle">ניתוח סיבתיות של תנועות מניה</div>
                    </div>
                </div>
                
                <div class="social-section">
                    {ticker_badge_with_logo}
                    <a href="https://x.com/LmlyhNyr" class="twitter-link" target="_blank">
                        <img src="x.png" alt="X (Twitter)" class="twitter-icon">
                        <span>עקבו אחרינו</span>
                    </a>
                </div>
            </div>
        </div>
        
        <div class="content">
            <a href="../index.html" class="back-home-btn"><i class="fas fa-home"></i> חזרה לדף הבית</a>
            <div class="scroll-hint"><i class="fas fa-angle-double-left"></i> גלול לצדדים <i class="fas fa-angle-double-right"></i></div>
            <div class="newsletter-section" style="margin: 0 auto 30px auto; max-width: 600px; text-align: center;">
                <h3 style="color: var(--accent-color); margin-bottom: 10px; font-size: 1.2em;">הצטרפו לרשימת התפוצה שלנו</h3>
                <iframe
                    scrolling="no"
                    style="width:100%!important;height:220px;border:1px #ccc solid !important;border-radius:12px;background:#fff;"
                    src="https://buttondown.com/nirstam?as_embed=true"
                ></iframe>
            </div>
            <div class="article-content">
                {html_content}
            </div>
            
            <div class="disclaimer">
                <strong>הסתייגות משפטית:</strong>
                המידע הנ״ל מבוסס על מקורות מידע שונים ועלול להשתנות בכל עת. המידע המוזכר בכתבה זו מוגבל לצורך מחקר והנאה ואין לראות בכתוב המלצה להשקעה. יש להתייעץ עם יועץ פיננסי לפני קבלת החלטות השקעה.
                <br><br>
                <strong>הערה:</strong> הניתוח נוצר באמצעות מודל בינה מלאכותית ועלול לכלול שגיאות כתיב או ניסוח. אנו מתנצלים מראש על אי-הדיוקים האפשריים.
                <br><br>
                <strong>מקורות המידע:</strong> Finviz, Briefing.com, Zacks, Alpha Vantage, Quandl,MarketBeat
                <h3>Hippopotamus Research</h3>
            </div>
        </div>
        
        <div class="footer">
            <div class="timestamp">נוצר ב: {get_current_timestamp()}</div>
            <div class="source">מקורות: Finviz, Briefing.com, Zacks, Alpha Vantage, Quandl,MarketBeat | ניתוח באמצעות aya-expanse:8b</div>
        </div>
    </div>
</body>
</html>'''
        
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        # Copy static files (logo, x icon) to articles directory
        copy_static_files(articles_dir)

        # Extract title and summary for metadata
        title = f"{ticker}: למה המניה זזה היום?"
        summary = processed_text[:200] + "..." if len(processed_text) > 200 else processed_text

        # Add metadata (now with tags and extra info)
        add_article_metadata(ticker, title, html_filename, summary, tags, ticker_info)
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
    # נטען את המידע מה-CSV עבור הטיקר
    ticker_metadata = load_ticker_metadata()
    ticker_info = ticker_metadata.get(ticker, {})
    process_and_create_article(ticker, original_text, original_file_name, ticker_info, output_dir)
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
        print(f"❌ Error loading ticker metadata from CSV: {e}")
    return ticker_info

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
    """Process all tickers from CSV file in random order, skipping already processed and unavailable ones"""
    ticker_metadata = load_ticker_metadata()
    tickers = set(ticker_metadata.keys())
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
            # Process the ticker (scraping needs only ticker)
            result = scrape_text_from_website(ticker)
            if not result or not result[0]:
                print(f"❌ No data found for {ticker}, adding to unavailable list.")
                unavailable.add(ticker)
                save_unavailable_tickers(unavailable)
                continue
            # Step 2: Process with LLM (after browser is closed)
            # Pass metadata for richer processing
            process_and_create_article(ticker, result[0], result[1], ticker_metadata.get(ticker, {}))
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
