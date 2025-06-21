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
    """Create a beautifully formatted HTML content for the institutional research report, with company logo badge."""
    # Use the improved tagged text to HTML conversion
    formatted_content = convert_tagged_text_to_html(summary_text)
    logo_url = get_company_logo_url(ticker, ticker_info)
    
    # Create ticker badge with logo for the header
    ticker_badge_with_logo = f'''
    <div class="ticker-badge">
        <img src="{logo_url}" alt="{ticker} logo" class="company-logo" style="width: 20px; height: 20px; margin-left: 8px; border-radius: 3px; vertical-align: middle;">
        {ticker}
    </div>
    '''
    
    # Build HTML with ticker badge in header and content
    html = f'''
    <style>
        .ticker-badge {{
            display: inline-flex;
            align-items: center;
            background: var(--gradient-accent);
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 1.1em;
            box-shadow: var(--shadow-accent);
        }}
        .company-logo {{
            width: 20px;
            height: 20px;
            margin-left: 8px;
            border-radius: 3px;
            vertical-align: middle;
        }}
        .article-content h1 {{
            font-size: 1.8em;
            font-weight: 700;
            color: var(--accent-color);
            margin: 20px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--highlight-color);
        }}
        .article-content h2 {{
            font-size: 1.4em;
            font-weight: 600;
            color: var(--accent-color);
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--highlight-color);
        }}
        .article-content h3 {{
            font-size: 1.2em;
            font-weight: 600;
            color: var(--accent-color);
            margin: 20px 0 10px 0;
        }}
        .article-content p {{
            font-size: 1.05em;
            line-height: 1.7;
            margin-bottom: 15px;
            text-align: justify;
        }}
    </style>
    <div class="article-container">
        <div class="article-content-text">
            {formatted_content}
        </div>
    </div>
    '''
    return html, ticker_badge_with_logo 