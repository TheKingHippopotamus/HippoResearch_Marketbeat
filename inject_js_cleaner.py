#!/usr/bin/env python3
"""
A script to inject a JavaScript cleaner into all HTML files in a directory.
The script hides unwanted markers like #TITLE:, PARA:, ##, etc., without altering the HTML structure.
Now includes automatic monitoring for new HTML files.
"""

import os
import glob
from bs4 import BeautifulSoup, Tag
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
  
  // Regex to match marker words anywhere, with optional colon or space after
  const regex = /(?:#+\s*)?(TITLE|SUBTITLE|PARA|כותרת ראשית|כותרת משנה|פסקה|ראשונה|שניה|שנייה|שלישית|רביעית|חמישית|שישית|אחרונה)[:：]?\b/gi;

  elements.forEach(el => {
    // We iterate through child nodes to only affect text nodes.
    // This prevents breaking any HTML elements inside the tags (like <a> or <strong>).
    Array.from(el.childNodes).forEach(node => {
      if (node.nodeType === Node.TEXT_NODE) { // Process only text nodes
        const originalText = node.textContent;
        const newText = originalText.replace(regex, '').replace(/\s{2,}/g, ' ').trim();
        if (originalText !== newText) {
          node.textContent = newText;
        }
      }
    });
  });
});
"""

# --- Social Buttons Injection Templates ---
DOMAIN = 'https://thekinghippopotamus.github.io/HippoResearch_Marketbeat/articles/'
INDEX_URL = 'https://thekinghippopotamus.github.io/HippoResearch_Marketbeat/'
FOLLOW_URL = 'https://twitter.com/your_twitter_handle'
X_ICON_SRC = 'x.png'

SOCIAL_CSS_BLOCK = '''
    <style>
    .x-share-btn-custom {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 22px;
      background: linear-gradient(90deg, #14171a 0%, #1da1f2 100%);
      color: #fff;
      border-radius: 30px;
      text-decoration: none;
      font-weight: 700;
      font-size: 1em;
      box-shadow: 0 4px 16px rgba(29,161,242,0.10);
      transition: background 0.3s, transform 0.2s, box-shadow 0.2s;
      border: none;
      outline: none;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }
    .x-share-btn-custom:hover {
      background: linear-gradient(90deg, #1da1f2 0%, #14171a 100%);
      transform: translateY(-2px) scale(1.04);
      box-shadow: 0 8px 24px rgba(29,161,242,0.18);
    }
    .x-share-btn-custom .x-icon {
      width: 24px;
      height: 24px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.3s;
    }
    .x-share-btn-custom:hover .x-icon {
      background: #1da1f2;
    }
    .x-share-btn-custom .x-icon img {
      width: 16px;
      height: 16px;
      display: block;
    }
    .follow-btn {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 22px;
      background: linear-gradient(90deg, #7b2ff2 0%, #1da1f2 100%);
      color: #fff;
      border-radius: 30px;
      text-decoration: none;
      font-weight: 700;
      font-size: 1em;
      box-shadow: 0 4px 16px rgba(123,47,242,0.10);
      transition: background 0.3s, transform 0.2s, box-shadow 0.2s;
      border: none;
      outline: none;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }
    .follow-btn:hover {
      background: linear-gradient(90deg, #1da1f2 0%, #7b2ff2 100%);
      transform: translateY(-2px) scale(1.04);
      box-shadow: 0 8px 24px rgba(123,47,242,0.18);
    }
    .follow-btn .x-icon {
      width: 24px;
      height: 24px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.3s;
    }
    .follow-btn:hover .x-icon {
      background: #7b2ff2;
    }
    .follow-btn .x-icon img {
      width: 16px;
      height: 16px;
      display: block;
    }
    .share-popup-message {
      position: fixed;
      top: 30px;
      left: 50%;
      transform: translateX(-50%);
      background: #1da1f2;
      color: #fff;
      padding: 18px 32px;
      border-radius: 30px;
      font-size: 1.2em;
      font-weight: 700;
      box-shadow: 0 4px 24px rgba(29,161,242,0.18);
      z-index: 9999;
      opacity: 0.97;
      text-align: center;
      letter-spacing: 0.02em;
      animation: fadeInOut 3s;
    }
    @keyframes fadeInOut {
      0% { opacity: 0; transform: translateX(-50%) scale(0.95); }
      10% { opacity: 0.97; transform: translateX(-50%) scale(1.05); }
      90% { opacity: 0.97; transform: translateX(-50%) scale(1.05); }
      100% { opacity: 0; transform: translateX(-50%) scale(0.95); }
    }
    </style>
'''

SOCIAL_JS_TEMPLATE = '''<script>
document.addEventListener('DOMContentLoaded', function() {{
  document.querySelectorAll('.x-share-btn-custom').forEach(function(btn) {{
    btn.addEventListener('click', function(e) {{
      e.preventDefault();
      e.stopPropagation();
      // הצג פופ-אפ למשתמש
      var popup = document.createElement('div');
      popup.className = 'share-popup-message';
      popup.textContent = 'השיתוף מחכה לך בדף השני :)';
      document.body.appendChild(popup);
      setTimeout(function() {{
        popup.remove();
        window.open('{index_url}', '_blank', 'noopener');
        window.open('{share_url}', '_self', 'noopener');
      }}, 3000); // 3 שניות
      return false;
    }});
  }});
}});
</script>'''

SOCIAL_SECTION_TEMPLATE = '''<div class="social-section">
  <div class="ticker-badge">{ticker}</div>
  <a href="{follow_url}" rel="noopener" target="_blank" class="follow-btn">
    <span class="x-icon">
      <img src="{x_icon_src}" alt="X">
    </span>
    עקבו אחרינו
  </a>
  <button type="button" class="x-share-btn-custom">
    <span class="x-icon">
      <img src="{x_icon_src}" alt="X">
    </span>
    שתף ב־X
  </button>
</div>'''

def build_share_url(ticker, filename):
    from urllib.parse import quote
    text = f"מחקר חדש של Hippopotamus Research ${ticker}\n{DOMAIN}{filename}"
    return f"https://twitter.com/intent/tweet?text={{quote(text, safe='')}}"

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

def fix_html_structure(soup):
    """Fix HTML structure: h1->h2, h2->h3, paragraphs->p, remove all markers (English/Hebrew)."""
    fixed = False
    para_markers = ['PARA#', 'פסקה:', 'פסקה']
    title_markers = ['TITLE#', 'כותרת ראשית:', 'כותרת ראשית']
    subtitle_markers = ['SUBTITLE#', 'כותרת משנה:', 'כותרת משנה']
    ordinal_markers = ['ראשונה:', 'שניה:', 'שנייה:', 'שלישית:', 'רביעית:', 'חמישית:', 'שישית:', 'שישית', 'אחרונה:', 'אחרונה']

    # h1 -> h2
    h1_tags = soup.find_all('h1')
    for h1 in h1_tags:
        text_content = h1.get_text().strip()
        # Remove all markers
        for m in para_markers + title_markers + subtitle_markers + ordinal_markers:
            text_content = text_content.replace(m, '').strip()
        new_h2 = soup.new_tag('h2')
        new_h2.string = text_content
        h1.replace_with(new_h2)
        fixed = True
        logger.info(f"  -> Fixed: Converted h1 to h2 and cleaned markers")

    # h2 -> h3
    h2_tags = soup.find_all('h2')
    for h2 in h2_tags:
        text_content = h2.get_text().strip()
        for m in para_markers + title_markers + subtitle_markers + ordinal_markers:
            text_content = text_content.replace(m, '').strip()
        new_h3 = soup.new_tag('h3')
        new_h3.string = text_content
        h2.replace_with(new_h3)
        fixed = True
        logger.info(f"  -> Fixed: Converted h2 to h3 and cleaned markers")

    # p tags: clean markers
    p_tags = soup.find_all('p')
    for p in p_tags:
        text_content = p.get_text().strip()
        for m in para_markers + title_markers + subtitle_markers + ordinal_markers:
            text_content = text_content.replace(m, '').strip()
        p.string = text_content
        fixed = True
        logger.info(f"  -> Fixed: Cleaned markers in p tag")

    return fixed

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

    # Fix HTML structure first
    structure_fixed = fix_html_structure(soup)
    if structure_fixed:
        logger.info(f"  -> HTML structure fixed")

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

    # 1. Add CSS if not present
    head = soup.find('head')
    if head and SOCIAL_CSS_BLOCK.strip() not in str(head):
        css_soup = BeautifulSoup(SOCIAL_CSS_BLOCK, 'html.parser')
        for style_tag in css_soup.find_all('style'):
            if isinstance(head, Tag):
                head.append(style_tag)

    # 2. Add social section to header-content if not present
    filename = os.path.basename(file_path)
    import re
    match = re.match(r"([A-Z0-9]+)_", filename)
    if match:
        ticker = match.group(1)
        share_url = build_share_url(ticker, filename)
        social_html = SOCIAL_SECTION_TEMPLATE.format(
            ticker=ticker,
            follow_url=FOLLOW_URL,
            share_url=share_url,
            x_icon_src=X_ICON_SRC
        )
        social_soup = BeautifulSoup(social_html, 'html.parser')
        header = soup.find('div', class_='header-content')
        if header and isinstance(header, Tag):
            old_social = header.find('div', class_='social-section')
            if old_social:
                old_social.replace_with(social_soup)
            else:
                logo_section = header.find('div', class_='logo-section')
                if logo_section and isinstance(logo_section, Tag):
                    logo_section.insert_after(social_soup)

        # 3. Add JS for share button (remove old, insert new)
        js_html = SOCIAL_JS_TEMPLATE.format(share_url=share_url, index_url=INDEX_URL)
        js_soup = BeautifulSoup(js_html, 'html.parser')
        # Remove any old script with this logic
        for script in soup.find_all('script'):
            script_content = getattr(script, 'string', None)
            if script_content and 'x-share-btn-custom' in script_content and 'window.open' in script_content:
                script.decompose()
        # Insert after social-section
        social_section = header.find('div', class_='social-section') if header and isinstance(header, Tag) else None
        if social_section and isinstance(social_section, Tag):
            social_section.insert_after(js_soup)

        # Remove old share/follow buttons outside header if exist
        for btn in soup.find_all(['a', 'button']):
            if isinstance(btn, Tag) and btn.has_attr('class') and any(c in ['x-share-btn-custom', 'follow-btn'] for c in btn['class']):
                parent_social = btn.find_parent('div', class_='social-section')
                if not parent_social:
                    btn.decompose()

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