import time
import re

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

def clean_text_for_html(text):
    """Clean and format text for HTML display"""
    # Remove markdown symbols and clean up formatting
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # Remove # headers
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)  # Convert **bold** to HTML
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)  # Convert *italic* to HTML
    text = re.sub(r'^\s*[-•]\s*', '• ', text, flags=re.MULTILINE)  # Clean bullet points
    
    # Split into paragraphs and clean up
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            # If it looks like a header (short, ends with colon, or all caps)
            if len(para) < 100 and (para.endswith(':') or para.isupper() or para.startswith('##')):
                cleaned_paragraphs.append(f'<h2 class="section-header">{para.replace("##", "").strip()}</h2>')
            else:
                cleaned_paragraphs.append(f'<p>{para}</p>')
    
    return '\n'.join(cleaned_paragraphs)

def create_html_content(ticker, summary_text, ticker_info=None):
    """Create a beautifully formatted HTML content for the institutional research report, with company logo badge."""
    # Use the improved markdown to HTML conversion
    from llm_processor import convert_markdown_to_html
    
    formatted_content = convert_markdown_to_html(summary_text)
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