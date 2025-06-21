#!/usr/bin/env python3
"""
Script to update all HTML files with the new JavaScript cleaner that supports Hebrew markers.
This script removes the old scripts and injects the updated ones.
"""

import os
import glob
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# The updated JavaScript code with Hebrew support
JS_CODE = """
document.addEventListener("DOMContentLoaded", function() {
  // Check if the cleaner has already run to avoid multiple executions
  if (document.body.dataset.jsCleanerApplied) {
    return;
  }
  document.body.dataset.jsCleanerApplied = 'true';

  const elements = document.querySelectorAll('p, h1, h2, h3, h4, li, span');
  
  // Regex to find all variations of markers:
  // - Optional hashes (e.g., #TITLE, ## TITLE)
  // - The marker words in English (TITLE, SUBTITLE, PARA) with an optional colon
  // - The marker words in Hebrew (כותרת ראשית, כותרת משנה, פסקה) with an optional colon
  // - Any remaining hash symbols
  const regex = /(?:#+\\s*)?(?:TITLE|SUBTITLE|PARA|כותרת ראשית|כותרת משנה|פסקה):?|#+/gi;

  elements.forEach(el => {
    // We iterate through child nodes to only affect text nodes.
    // This prevents breaking any HTML elements inside the tags (like <a> or <strong>).
    Array.from(el.childNodes).forEach(node => {
      if (node.nodeType === Node.TEXT_NODE) { // Process only text nodes
        const originalText = node.textContent;
        const newText = originalText.replace(regex, '').trim();
        if (originalText !== newText) {
          node.textContent = newText;
        }
      }
    });
  });
});
"""

def update_file(file_path):
    """Update a single HTML file with the new JavaScript cleaner."""
    logger.info(f"Updating: {os.path.basename(file_path)}")
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove old script if it exists
        old_script = soup.find("script", id="dynamic-text-cleaner-script")
        if old_script:
            old_script.decompose()
            logger.info(f"  -> Removed old script")
        
        # Find body tag
        body = soup.find("body")
        if not body:
            logger.warning(f"  -> WARNING: No <body> tag found. Skipping.")
            return False
        
        # Create the new script tag
        script_tag = soup.new_tag("script", id="dynamic-text-cleaner-script")
        script_tag.string = JS_CODE
        
        # Append the script at the end of the body
        body.append(script_tag)
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        logger.info(f"  -> Successfully updated with new script")
        return True
        
    except Exception as e:
        logger.error(f"  -> ERROR updating {os.path.basename(file_path)}: {e}")
        return False

def main():
    """Update all HTML files in the articles directory."""
    articles_dir = 'articles'
    
    # Find all HTML files
    html_files = glob.glob(os.path.join(articles_dir, "*.html"))
    # Filter out backup files
    html_files = [f for f in html_files if not f.endswith('.bak') and not f.endswith('.backup')]
    
    if not html_files:
        logger.info(f"No HTML files found in '{articles_dir}'.")
        return
    
    logger.info(f"Found {len(html_files)} HTML files to update in '{articles_dir}'.")
    updated_count = 0
    failed_count = 0
    
    for file_path in html_files:
        if update_file(file_path):
            updated_count += 1
        else:
            failed_count += 1
    
    logger.info("\\n--- Update Complete ---")
    logger.info(f"Successfully updated: {updated_count} files")
    logger.info(f"Failed: {failed_count} files")

if __name__ == "__main__":
    main() 