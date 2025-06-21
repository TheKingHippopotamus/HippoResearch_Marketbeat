#!/usr/bin/env python3
"""
Script to clean all existing articles from problematic markers and formatting
"""

import os
import re
import logging
from pathlib import Path
from scripts.llm_processor import clean_processed_text

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('clean_articles.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

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
    Clean HTML content from problematic markers and formatting, and convert markers to HTML tags.
    Does NOT remove existing HTML tags!
    """
    if not html_content:
        return html_content
    # Convert only raw markers to HTML
    cleaned = convert_tagged_text_to_html(html_content)
    # Remove only raw marker leftovers (##), but NOT HTML tags
    cleaned = re.sub(r'##\s*', '', cleaned)
    cleaned = re.sub(r'#+\s*', '', cleaned)
    # Remove empty HTML tags (optional)
    cleaned = re.sub(r'<p>\s*</p>', '', cleaned)
    cleaned = re.sub(r'<h\d>\s*</h\d>', '', cleaned)
    # Remove multiple empty lines
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    return cleaned.strip()

def clean_article_file(file_path):
    """
    Clean a single article file
    """
    try:
        logger.info(f"🧹 Cleaning file: {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        logger.info(f"📄 Original file size: {original_size} characters")
        
        # Clean the content
        cleaned_content = clean_html_content(content)
        cleaned_size = len(cleaned_content)
        logger.info(f"📄 Cleaned file size: {cleaned_size} characters")
        
        # Check if cleaning made any changes
        if cleaned_content != content:
            # Create backup
            backup_path = str(file_path) + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"💾 Backup created: {backup_path}")
            
            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            logger.info(f"✅ File cleaned and saved: {file_path}")
            
            return True
        else:
            logger.info(f"ℹ️ No changes needed for: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error cleaning {file_path}: {e}")
        return False

def clean_all_articles():
    """
    Clean all HTML articles in the articles directory
    """
    articles_dir = Path("articles")
    
    if not articles_dir.exists():
        logger.error(f"❌ Articles directory not found: {articles_dir}")
        return
    
    # Find all HTML files
    html_files = list(articles_dir.glob("*.html"))
    
    if not html_files:
        logger.info("ℹ️ No HTML files found in articles directory")
        return
    
    logger.info(f"🚀 Starting to clean {len(html_files)} HTML files...")
    logger.info("="*60)
    
    cleaned_count = 0
    skipped_count = 0
    error_count = 0
    
    for html_file in html_files:
        # Skip backup files
        if html_file.name.endswith('.backup') or html_file.name.endswith('.bak'):
            logger.info(f"⏭️ Skipping backup file: {html_file.name}")
            skipped_count += 1
            continue
            
        if clean_article_file(html_file):
            cleaned_count += 1
        else:
            error_count += 1
    
    logger.info("="*60)
    logger.info(f"🎉 Cleaning completed!")
    logger.info(f"📊 Files cleaned: {cleaned_count}")
    logger.info(f"📊 Files skipped: {skipped_count}")
    logger.info(f"📊 Files with errors: {error_count}")
    logger.info(f"📊 Total processed: {len(html_files)}")

def show_cleaning_preview():
    """
    Show a preview of what will be cleaned without making changes
    """
    articles_dir = Path("articles")
    
    if not articles_dir.exists():
        logger.error(f"❌ Articles directory not found: {articles_dir}")
        return
    
    # Find all HTML files
    html_files = list(articles_dir.glob("*.html"))
    
    if not html_files:
        logger.info("ℹ️ No HTML files found in articles directory")
        return
    
    logger.info(f"🔍 Preview mode - found {len(html_files)} HTML files")
    logger.info("="*60)
    
    files_with_issues = 0
    
    for html_file in html_files[:5]:  # Check first 5 files
        if html_file.name.endswith('.backup') or html_file.name.endswith('.bak'):
            continue
            
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for problematic markers
            has_title_marker = 'TITLE#' in content
            has_subtitle_marker = 'SUBTITLE#' in content
            has_para_marker = 'PARA#' in content
            has_hash_markers = '##' in content
            
            if has_title_marker or has_subtitle_marker or has_para_marker or has_hash_markers:
                files_with_issues += 1
                logger.info(f"⚠️ {html_file.name}:")
                if has_title_marker:
                    logger.info(f"   - Contains TITLE# markers")
                if has_subtitle_marker:
                    logger.info(f"   - Contains SUBTITLE# markers")
                if has_para_marker:
                    logger.info(f"   - Contains PARA# markers")
                if has_hash_markers:
                    logger.info(f"   - Contains ## markers")
            else:
                logger.info(f"✅ {html_file.name}: No issues found")
                
        except Exception as e:
            logger.error(f"❌ Error reading {html_file}: {e}")
    
    if files_with_issues > 0:
        logger.info(f"📊 Found {files_with_issues} files with issues (preview of first 5 files)")
    else:
        logger.info("✅ No issues found in preview files")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        logger.info("🔍 Running in preview mode...")
        show_cleaning_preview()
    else:
        logger.info("🚀 Running full cleaning process...")
        clean_all_articles() 