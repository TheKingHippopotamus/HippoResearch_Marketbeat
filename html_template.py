import time
import re

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
                cleaned_paragraphs.append(f'<h3 class="section-header">{para.replace("##", "").strip()}</h3>')
            else:
                cleaned_paragraphs.append(f'<p>{para}</p>')
    
    return '\n'.join(cleaned_paragraphs)

def create_html_content(ticker, summary_text, ticker_info=None):
    """Create a beautifully formatted HTML content for the institutional research report, with only the clean report text (no badges, no tags, no JSON remnants)."""
    formatted_content = clean_text_for_html(summary_text)
    # Build HTML with only the clean report text
    html = f'''
    <div class="article-container">
        <div class="article-content-text">
            {formatted_content}
        </div>
    </div>
    '''
    return html