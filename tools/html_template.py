import os
import re
import json
from datetime import datetime
import sys
from tools.logger import setup_logging

# Setup logging
logger = setup_logging()

# הוספת הנתיב הראשי למערכת כדי שנוכל לקרוא את קובץ ה-CSV
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# קריאת מיפוי טיקרים לסקטורים - עם טיפול במקרה שהקובץ לא קיים
sector_map = {}
csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "flat-ui__data.csv")
if os.path.exists(csv_path):
    try:
        import pandas as pd
        sector_map_df = pd.read_csv(csv_path)
        sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not load sector mapping: {e}")
else:
    logger.warning("⚠️ Warning: CSV file not found, sector mapping will be empty")

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

from tools.llm_processor import convert_tagged_text_to_html

def get_company_logo_url(ticker, ticker_info=None):
    """Generate a logo URL for a given ticker using Clearbit's logo API"""
    if ticker_info and 'Security' in ticker_info:
        # Use the company name from CSV to generate a better domain
        company_name = ticker_info['Security']
        
        # Convert company name to domain format
        # Remove common words and clean up
        domain_name = company_name.lower()
        domain_name = re.sub(r'\s+(inc\.?|corp\.?|company|co\.?|ltd\.?|llc|plc|group|holdings|technologies|systems|solutions|international|enterprises|ventures|partners|associates|&|and)', '', domain_name)
        domain_name = re.sub(r'[^\w\s-]', '', domain_name)  # Remove special characters
        domain_name = re.sub(r'\s+', '', domain_name)  # Remove spaces
        
        # Add .com extension
        return f"https://logo.clearbit.com/{domain_name}.com"
    else:
        # Fallback to ticker-based domain
        company_domain = f"{ticker.lower()}.com"
        return f"https://logo.clearbit.com/{company_domain}"

def create_html_content(ticker, summary_text, ticker_info=None):
    """Create the article body HTML (without <head> or <style>), with company logo badge and styled newsletter section."""
    formatted_content = convert_tagged_text_to_html(summary_text)
    logo_url = get_company_logo_url(ticker, ticker_info)
    ticker_badge_with_logo = f'''
    <div class="ticker-badge">
        <img src="{logo_url}" alt="{ticker} logo" class="company-logo" style="width: 20px; height: 20px; margin-left: 8px; border-radius: 3px; vertical-align: middle;">
        {ticker}
    </div>
    '''
    newsletter_html = '''
    <div class="newsletter-section" style="margin: 0 auto 24px auto; max-width: 400px; text-align: center;">
        <div style="font-size: 1em; color: var(--accent-color); margin-bottom: 6px; font-weight: 500; opacity: 0.85;">
            הצטרפו לעדכונים במייל
        </div>
        <iframe
            scrolling="no"
            style="width:100%!important; height:120px; border:none!important; border-radius:12px; background:#fff; box-shadow:0 2px 8px rgba(15,52,96,0.07);"
            src="https://buttondown.com/nirstam?as_embed=true"
            title="הרשמה לניוזלטר"
        ></iframe>
    </div>
    '''
    html = f'''
    <div class="article-container">
        {newsletter_html}
        <div class="article-content-text">
            {formatted_content}
        </div>
    </div>
    '''
    return html, ticker_badge_with_logo 