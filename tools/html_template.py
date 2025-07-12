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

# שימוש במודול המרכזי לנתוני טיקרים
from tools.ticker_data import get_ticker_info, get_company_logo_url
# שימוש בפונקציית המרת טקסט ל-HTML ממודול ייעודי
from tools.text_processing import convert_tagged_text_to_html

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

# הפונקציה get_company_logo_url עכשיו מיובאת מהמודול המרכזי

def create_html_content(ticker, summary_text, ticker_info=None):
    """Create the article body HTML (without <head> or <style>), with company logo badge and styled newsletter section."""
    formatted_content = convert_tagged_text_to_html(summary_text)
    logo_url = get_company_logo_url(ticker)
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

def create_marketbeat_html(ticker, content, ticker_info=None):
    """
    יוצר HTML עם הדגשות צבעוניות למבנה MarketBeat
    """
    company_name = ticker_info.get('Security') if ticker_info else ticker
    logo_url = get_company_logo_url(ticker)
    
    # ניתוח התוכן לפי מבנה MarketBeat
    sections = parse_marketbeat_sections(content)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - ניתוח שוק</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 20px;
        }}
        .logo {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            margin-bottom: 15px;
        }}
        .main-title {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }}
        .sentiment-section {{
            margin: 25px 0;
            padding: 20px;
            border-radius: 8px;
            border-right: 5px solid;
        }}
        .sentiment-positive {{
            background-color: #d4edda;
            border-color: #27ae60;
        }}
        .sentiment-neutral {{
            background-color: #fff3cd;
            border-color: #f39c12;
        }}
        .sentiment-negative {{
            background-color: #f8d7da;
            border-color: #e74c3c;
        }}
        .sentiment-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .sentiment-positive .sentiment-title {{
            color: #155724;
        }}
        .sentiment-neutral .sentiment-title {{
            color: #856404;
        }}
        .sentiment-negative .sentiment-title {{
            color: #721c24;
        }}
        .sentiment-icon {{
            margin-left: 10px;
            font-size: 1.2rem;
        }}
        .content-paragraph {{
            font-size: 1rem;
            line-height: 1.7;
            margin: 10px 0;
            color: #495057;
        }}
        .timestamp {{
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{logo_url}" alt="{company_name}" class="logo" onerror="this.style.display='none'">
            <h1 class="main-title">{company_name}</h1>
        </div>
"""
    
    # הוספת סקציות לפי סנטימנט
    for sentiment_type, content_list in sections.items():
        if content_list:
            sentiment_class = f"sentiment-{sentiment_type}"
            sentiment_title = {
                'positive': 'נקודות חיוביות',
                'neutral': 'נקודות נייטרליות', 
                'negative': 'נקודות שליליות'
            }[sentiment_type]
            
            sentiment_icon = {
                'positive': '✅',
                'neutral': '⚖️',
                'negative': '⚠️'
            }[sentiment_type]
            
            html_content += f"""
        <div class="sentiment-section {sentiment_class}">
            <h2 class="sentiment-title">
                {sentiment_title}
                <span class="sentiment-icon">{sentiment_icon}</span>
            </h2>
"""
            
            for paragraph in content_list:
                html_content += f'            <p class="content-paragraph">{paragraph}</p>\n'
            
            html_content += "        </div>\n"
    
    html_content += f"""
        <div class="timestamp">
            נוצר ב-{datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def parse_marketbeat_sections(content):
    """
    מנתח את התוכן לפי מבנה MarketBeat ומחזיר מילון של סקציות
    """
    sections = {
        'positive': [],
        'neutral': [],
        'negative': []
    }
    
    lines = content.split('\n')
    current_sentiment = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Positive Sentiment:'):
            current_sentiment = 'positive'
        elif line.startswith('Neutral Sentiment:'):
            current_sentiment = 'neutral'
        elif line.startswith('Negative Sentiment:'):
            current_sentiment = 'negative'
        elif line.startswith('Posted') or line.startswith('AI Generated'):
            continue
        elif line and current_sentiment:
            sections[current_sentiment].append(line)
    
    return sections 