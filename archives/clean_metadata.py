import json
import re
import os
from datetime import datetime
from tools.logger import setup_logging

# Setup logging
logger = setup_logging()

# --- ניקוי סימונים והמרה ל-HTML ---
def convert_tagged_text_to_html(text):
    """
    Convert tagged text (#TITLE#, #SUBTITLE#, #PARA#) to valid HTML, preserving existing HTML tags.
    """
    if not text:
        return text
    # Normalize all markers to canonical form
    text = re.sub(r'#+\s*SUBTITLE#', '#SUBTITLE#', text)
    text = re.sub(r'#+\s*TITLE#', '#TITLE#', text)
    text = re.sub(r'#+\s*PARA#', '#PARA#', text)
    # Split text by markers, keeping the marker in the result
    parts = re.split(r'(#TITLE#|#SUBTITLE#|#PARA#)', text)
    html_lines = []
    current_tag = None
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part in ['#TITLE#', '#SUBTITLE#', '#PARA#']:
            current_tag = part
        else:
            if current_tag == '#TITLE#':
                html_lines.append(f"<h1>{part}</h1>")
            elif current_tag == '#SUBTITLE#':
                html_lines.append(f"<h2>{part}</h2>")
            elif current_tag == '#PARA#':
                html_lines.append(f"<p>{part}</p>")
            else:
                html_lines.append(part)
    return '\n'.join(html_lines)

def clean_html_content(html_content):
    """
    Clean HTML content from problematic markers and formatting, and convert markers to HTML tags
    """
    if not html_content:
        return html_content
    # Convert markers to HTML
    cleaned = convert_tagged_text_to_html(html_content)
    # Remove redundant ##
    cleaned = re.sub(r'##\s*', '', cleaned)
    cleaned = re.sub(r'#+\s*', '', cleaned)
    # Remove empty HTML tags
    cleaned = re.sub(r'<p>\s*</p>', '', cleaned)
    cleaned = re.sub(r'<h\d>\s*</h\d>', '', cleaned)
    # Remove multiple empty lines
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    return cleaned.strip()

def clean_summary_to_plain_text(summary):
    """
    Clean summary to plain text (no HTML, no markers), max 200 chars
    """
    if not summary:
        return summary
    # Remove markers
    summary = re.sub(r'#TITLE#|#SUBTITLE#|#PARA#|##+', ' ', summary)
    # Remove HTML tags
    summary = re.sub(r'<[^>]+>', ' ', summary)
    # Collapse whitespace
    summary = re.sub(r'\s+', ' ', summary)
    summary = summary.strip()
    # Truncate to 200 chars
    if len(summary) > 200:
        summary = summary[:200] + '...'
    return summary

def clean_metadata_file():
    """Clean the metadata JSON file"""
    try:
        metadata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'articles_metadata.json')
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cleaned_count = 0
        for article in data:
            if 'summary' in article and article['summary']:
                original_summary = article['summary']
                cleaned_summary = clean_summary_to_plain_text(original_summary)
                if cleaned_summary != original_summary:
                    article['summary'] = cleaned_summary
                    cleaned_count += 1
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Cleaned {cleaned_count} summaries in metadata file (plain text, max 200 chars)")
    except Exception as e:
        logger.error(f"❌ Error cleaning metadata: {e}")

if __name__ == "__main__":
    logger.info("🧹 Starting cleanup process...")
    clean_metadata_file()
    logger.info("✨ Cleanup completed!") 