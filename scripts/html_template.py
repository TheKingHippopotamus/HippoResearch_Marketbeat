import os
import re
import json
from datetime import datetime
import sys

# הוספת הנתיב הראשי למערכת כדי שנוכל לקרוא את קובץ ה-CSV
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# קריאת מיפוי טיקרים לסקטורים - עם טיפול במקרה שהקובץ לא קיים
sector_map = {}
csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "flat-ui__data-Thu Jun 19 2025.csv")
if os.path.exists(csv_path):
    try:
        import pandas as pd
        sector_map_df = pd.read_csv(csv_path)
        sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))
    except Exception as e:
        print(f"⚠️ Warning: Could not load sector mapping: {e}")
else:
    print("⚠️ Warning: CSV file not found, sector mapping will be empty")

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

from scripts.llm_processor import convert_tagged_text_to_html

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
    <div class="newsletter-section" style="margin:12px auto 20px auto;max-width:260px;padding:0;background:none;border:none;box-shadow:none;border-radius:0;position:relative;z-index:2;">
        <h3 style="font-weight:400;opacity:0.5;font-size:0.85em;margin-bottom:2px;margin-top:0;color:var(--accent-color);">הצטרפו לרשימת התפוצה שלנו</h3>
        <iframe class="newsletter-iframe" scrolling="no" style="height:110px;width:100%;border:none;background:none;box-shadow:none;border-radius:0;" src="https://buttondown.com/nirstam?as_embed=true"></iframe>
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