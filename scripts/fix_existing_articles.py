#!/usr/bin/env python3
"""
Script to fix existing articles by converting markdown emphasis to HTML and adding line breaks.
"""

import os
import re
import glob
from pathlib import Path
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_article_text(text):
    """Convert markdown emphasis (**text**) to HTML <strong> tags and add line breaks."""
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Add line breaks for better readability
    text = text.replace('. ', '.<br>')
    text = text.replace('! ', '!<br>')
    text = text.replace('? ', '?<br>')
    return text

def process_html_file(file_path):
    """Process a single HTML file to fix markdown emphasis and add line breaks."""
    try:
        logger.info(f"Processing: {file_path}")
        
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all text content (excluding script and style tags)
        for element in soup.find_all(text=True):
            if element.parent and element.parent.name not in ['script', 'style']:
                # Format the text
                formatted_text = format_article_text(str(element))
                # Replace the text content
                element.replace_with(BeautifulSoup(formatted_text, 'html.parser'))
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        logger.info(f"✅ Successfully processed: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main function to process all HTML articles."""
    articles_dir = Path("articles")
    
    if not articles_dir.exists():
        logger.error(f"Articles directory not found: {articles_dir}")
        return
    
    # Find all HTML files
    html_files = list(articles_dir.glob("*.html"))
    
    if not html_files:
        logger.warning("No HTML files found in articles directory")
        return
    
    logger.info(f"Found {len(html_files)} HTML files to process")
    
    # Process each file
    successful = 0
    failed = 0
    
    for html_file in html_files:
        if process_html_file(html_file):
            successful += 1
        else:
            failed += 1
    
    logger.info(f"Processing complete!")
    logger.info(f"✅ Successfully processed: {successful} files")
    if failed > 0:
        logger.warning(f"❌ Failed to process: {failed} files")

def clean_repetitive_openings(text):
    """Remove repetitive opening phrases and improve article structure"""
    # Common repetitive patterns to remove
    patterns_to_remove = [
        r'חברת [^)]+ \(NASDAQ: [A-Z]+\) חווה תנודתיות בשיעורי המניות שלה',
        r'חברת [^)]+ \(NYSE: [A-Z]+\) חווה תנודתיות בשיעורי המניות שלה',
        r'חברת [^)]+ \(NASDAQ: [A-Z]+\) חווה תנודות בשוק',
        r'חברת [^)]+ \(NYSE: [A-Z]+\) חווה תנודות בשוק',
        r'חברת [^)]+ \(NASDAQ: [A-Z]+\) חווה תנודות בשיעורי המניות',
        r'חברת [^)]+ \(NYSE: [A-Z]+\) חווה תנודות בשיעורי המניות',
        r'חברת [^)]+ \(NASDAQ: [A-Z]+\) חווה תנודות',
        r'חברת [^)]+ \(NYSE: [A-Z]+\) חווה תנודות',
        r'חברת [^)]+ \(NASDAQ: [A-Z]+\) חווה',
        r'חברת [^)]+ \(NYSE: [A-Z]+\) חווה',
        r'מניות [A-Z]+ חוות תנודות בשוק',
        r'מניות [A-Z]+ חוות תנודתיות בשוק',
        r'מניות [A-Z]+ חוות תנודות',
        r'מניות [A-Z]+ חוות תנודתיות',
    ]
    
    # Remove repetitive patterns
    cleaned_text = text
    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
    
    # Replace with better opening
    ticker_match = re.search(r'\(NASDAQ: ([A-Z]+)\)|\(NYSE: ([A-Z]+)\)', text)
    if ticker_match:
        ticker = ticker_match.group(1) or ticker_match.group(2)
        
        # Find and replace the problematic opening paragraph
        problematic_patterns = [
            r'<p>מניות [A-Z]+ חוות תנודות בשוק, כאשר המשקיעים מתחשבים בגורמים חיוביים, נייטרליים ושליליים משפיעים על הביצועים\.</p>',
            r'<p>כאשר המשקיעים מתחשבים בגורמים חיוביים, נייטרליים ושליליים משפיעים על הביצועים\.</p>',
            r'<p>מניות [A-Z]+ חוות תנודות בשוק.*?</p>',
            r'<p>מניות [A-Z]+ חוות תנודתיות בשוק.*?</p>'
        ]
        
        better_opening = f"<p>מניות {ticker} מראות סימני תנועה בשוק, כאשר המשקיעים מתחשבים במגוון גורמים המשפיעים על הביצועים.</p>"
        
        for pattern in problematic_patterns:
            if re.search(pattern, cleaned_text, flags=re.IGNORECASE):
                cleaned_text = re.sub(pattern, better_opening, cleaned_text, flags=re.IGNORECASE)
                break
    
    # Fix any remaining issues with commas at the beginning
    cleaned_text = re.sub(r'<p>,\s*', '<p>', cleaned_text)
    cleaned_text = re.sub(r'<p>\s*,', '<p>', cleaned_text)
    
    # Clean up extra whitespace and punctuation
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\.\s*\.', '.', cleaned_text)
    cleaned_text = re.sub(r',\s*,', ',', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def fix_existing_cleaned_files():
    """Fix all existing cleaned text files by removing repetitive openings"""
    txt_dir = Path("txt")
    cleaned_files = list(txt_dir.glob("*_cleaned_*.txt"))
    
    logger.info(f"🔧 Found {len(cleaned_files)} cleaned files to fix")
    
    for file_path in cleaned_files:
        try:
            logger.info(f"🔧 Processing {file_path.name}")
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean repetitive openings
            cleaned_content = clean_repetitive_openings(content)
            
            # Write back the cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            logger.info(f"✅ Fixed {file_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    # Fix existing cleaned files
    fix_existing_cleaned_files()
    
    # Also fix existing HTML articles
    main() 