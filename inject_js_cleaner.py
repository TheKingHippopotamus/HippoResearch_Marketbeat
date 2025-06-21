#!/usr/bin/env python3
"""
A script to inject a JavaScript cleaner into all HTML files in a directory.
The script hides unwanted markers like #TITLE:, PARA:, ##, etc., without altering the HTML structure.
Now includes automatic monitoring for new HTML files.
"""

import os
import glob
from bs4 import BeautifulSoup
import argparse
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('js_cleaner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# A unique ID for our script tag to prevent duplicate injections
JS_CLEANER_ID = "dynamic-text-cleaner-script"

# The JavaScript code to be injected
# This script runs after the DOM is loaded, finds all relevant text,
# and removes the specified markers.
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
  // - The marker words (TITLE, SUBTITLE, PARA) with an optional colon
  // - Any remaining hash symbols
  const regex = /(?:#+\\s*)?(?:TITLE|SUBTITLE|PARA):?|#+/gi;

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

class HTMLFileHandler(FileSystemEventHandler):
    """File system event handler for monitoring HTML files"""
    
    def __init__(self, articles_dir, backup=True):
        self.articles_dir = articles_dir
        self.backup = backup
        self.processed_files = set()
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and event.src_path.endswith('.html'):
            # Wait a moment for the file to be fully written
            time.sleep(1)
            file_path = event.src_path
            
            # Skip backup files
            if file_path.endswith('.bak') or file_path.endswith('.backup'):
                return
                
            # Skip if already processed
            if file_path in self.processed_files:
                return
                
            logger.info(f"🆕 New HTML file detected: {os.path.basename(file_path)}")
            try:
                if inject_script_into_file(file_path, self.backup):
                    self.processed_files.add(file_path)
                    logger.info(f"✅ Automatically processed: {os.path.basename(file_path)}")
                else:
                    logger.info(f"⏭️ Skipped (already processed): {os.path.basename(file_path)}")
            except Exception as e:
                logger.error(f"❌ Error processing new file {os.path.basename(file_path)}: {e}")

def inject_script_into_file(file_path, backup=True):
    """Injects the cleaning JavaScript into a single HTML file."""
    logger.info(f"Processing: {os.path.basename(file_path)}")

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create a backup if requested
    if backup:
        backup_path = file_path + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"  -> Backup created: {os.path.basename(backup_path)}")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # --- Prevent duplicate script injection ---
    if soup.find("script", id=JS_CLEANER_ID):
        logger.info(f"  -> Script already exists. Skipping injection.")
        return False

    body = soup.find("body")
    if not body:
        logger.warning(f"  -> WARNING: No <body> tag found. Skipping injection.")
        return False

    # Create the new script tag
    script_tag = soup.new_tag("script", id=JS_CLEANER_ID)
    script_tag.string = JS_CODE

    # Append the script at the end of the body
    body.append(script_tag)

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    logger.info(f"  -> Successfully injected script.")
    return True

def process_all_articles(articles_dir, backup=True):
    """Processes all HTML files in the specified directory."""
    html_files = glob.glob(os.path.join(articles_dir, "*.html"))
    # Filter out backup files that we might have created
    html_files = [f for f in html_files if not f.endswith('.bak') and not f.endswith('.backup')]

    if not html_files:
        logger.info(f"No HTML files found in '{articles_dir}'.")
        return

    logger.info(f"Found {len(html_files)} HTML files to process in '{articles_dir}'.")
    processed_count = 0
    skipped_count = 0
    failed_count = 0

    for file_path in html_files:
        try:
            if inject_script_into_file(file_path, backup):
                processed_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            logger.error(f"  -> ERROR processing {os.path.basename(file_path)}: {e}")
            failed_count += 1

    logger.info("\\n--- Processing Complete ---")
    logger.info(f"Successfully injected: {processed_count} files")
    logger.info(f"Skipped (already injected): {skipped_count} files")
    logger.info(f"Failed: {failed_count} files")

def start_monitoring(articles_dir, backup=True):
    """Start monitoring the articles directory for new HTML files"""
    logger.info(f"🔍 Starting automatic monitoring of '{articles_dir}' directory...")
    logger.info("📝 The script will automatically process new HTML files as they are created.")
    logger.info("⏹️ Press Ctrl+C to stop monitoring.")
    
    # Process existing files first
    logger.info("🔄 Processing existing HTML files...")
    process_all_articles(articles_dir, backup)
    
    # Set up file monitoring
    event_handler = HTMLFileHandler(articles_dir, backup)
    observer = Observer()
    observer.schedule(event_handler, articles_dir, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\\n⏹️ Stopping monitoring...")
        observer.stop()
    
    observer.join()
    logger.info("✅ Monitoring stopped.")

def main():
    parser = argparse.ArgumentParser(
        description="Injects a JavaScript cleaner into HTML articles with optional automatic monitoring.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--dir',
        default='articles',
        help="Directory containing HTML articles (default: 'articles')."
    )
    parser.add_argument(
        '--file',
        help="Process a single file instead of the entire directory."
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help="Disable creating backup files (.bak)."
    )
    parser.add_argument(
        '--monitor',
        action='store_true',
        help="Start automatic monitoring for new HTML files."
    )
    args = parser.parse_args()

    should_backup = not args.no_backup

    if args.file:
        if os.path.exists(args.file):
            inject_script_into_file(args.file, should_backup)
        else:
            logger.error(f"Error: File not found at '{args.file}'")
    elif args.monitor:
        if os.path.isdir(args.dir):
            start_monitoring(args.dir, should_backup)
        else:
            logger.error(f"Error: Directory not found at '{args.dir}'")
    else:
        if os.path.isdir(args.dir):
            process_all_articles(args.dir, should_backup)
        else:
            logger.error(f"Error: Directory not found at '{args.dir}'")

if __name__ == "__main__":
    main() 