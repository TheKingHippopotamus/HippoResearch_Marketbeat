#!/usr/bin/env python3
"""
A script to inject a JavaScript cleaner into all HTML files in a directory.
The script hides unwanted markers like #TITLE:, PARA:, ##, etc., without altering the HTML structure.
Now includes automatic monitoring for new HTML files.
"""

import os
import glob
from bs4 import BeautifulSoup, Tag, NavigableString
import argparse
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import re
from bs4.element import NavigableString
import functools

# ANSI color codes for log highlighting
class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\033[90m'
    WHITE = '\033[97m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'

# Helper for colored log messages
def color_log(msg, color):
    return f"{color}{msg}{LogColors.ENDC}"

# Upgrade logging format
class ColorFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if record.levelno >= logging.ERROR:
            return color_log(msg, LogColors.FAIL)
        elif record.levelno == logging.WARNING:
            return color_log(msg, LogColors.WARNING)
        elif record.levelno == logging.INFO:
            if any(x in msg for x in ["[STAGE]", "[DONE]", "[SUCCESS]", "[INJECT]", "[SOCIAL]", "[STRUCTURE]"]):
                return color_log(msg, LogColors.OKCYAN)
            elif "[CLEANER]" in msg:
                return color_log(msg, LogColors.OKBLUE)
            else:
                return msg
        return msg

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler('js_cleaner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
for handler in logging.getLogger().handlers:
    handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'))
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
            if file_path.endswith((".bak", ".backup")):
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

@log_stage("STRUCTURE")
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

@log_stage("CLEANER")
def inject_script_into_file(file_path, backup=True):
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

    # Remove all old cleaner scripts
    for script in soup.find_all('script'):
        script_id = script.get('id') if isinstance(script, Tag) else None
        is_cleaner_id = isinstance(script_id, str) and 'cleaner' in script_id
        script_string = getattr(script, 'string', None)
        is_cleaner_content = script_string and ('jsCleanerApplied' in script_string or 'text-cleaner' in script_string)
        if is_cleaner_id or is_cleaner_content:
            script.decompose()

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
    body.append(script_tag)

    # 1. Add CSS if not present
    head = soup.find('head')
    if head and SOCIAL_CSS_BLOCK.strip() not in str(head):
        css_soup = BeautifulSoup(SOCIAL_CSS_BLOCK, 'html.parser')
        for style_tag in css_soup.find_all('style'):
            if isinstance(head, Tag):
                head.append(style_tag)

    # 2. Always inject the share button and script using the dynamic ticker and filename
    filename = os.path.basename(file_path)
    match = re.match(r"([A-Z0-9]+)_", filename)
    ticker = match.group(1) if match else ""
    ensure_share_button_and_script(soup, ticker, filename)

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    logger.info(f"  -> Successfully injected script.")
    return True

@log_stage("PROCESS_ALL")
def process_all_articles(articles_dir, backup=True):
    """Processes all HTML files in the specified directory."""
    html_files = glob.glob(os.path.join(articles_dir, "*.html"))
    # Filter out backup files that we might have created
    html_files = [f for f in html_files if not f.endswith((".bak", ".backup"))]

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

@log_stage("MONITOR")
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

def clean_single_article(filename):
    from bs4 import BeautifulSoup, Tag
    marker_words = [
        'ראשונה', 'שניה', 'שנייה', 'שלישית', 'רביעית', 'חמישית', 'שישית', 'אחרונה'
    ]
    marker_regex = re.compile(rf"^\s*({'|'.join(marker_words)})\s*:?\s*$")
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    # Remove <h3> that are only marker words
    for h3 in soup.find_all('h3'):
        if isinstance(h3, Tag):
            text = h3.get_text(strip=True)
            if marker_regex.match(text):
                h3.decompose()
    # Remove marker words anywhere in text of p/h1/h2/h3/h4/li/span
    text_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'span'])
    marker_anywhere = re.compile(rf"(\s*({'|'.join(marker_words)})\s*:?\s*)")
    for tag in text_tags:
        if isinstance(tag, Tag):
            text = tag.get_text()
            new_text = marker_anywhere.sub(' ', text)
            # Only replace tag.string if tag has no children (is NavigableString)
            if tag.string and len(tag.contents) == 1:
                tag.string.replace_with(NavigableString(new_text.strip()))
            else:
                # If tag has children, replace all text nodes
                for node in tag.find_all(text=True, recursive=False):
                    if isinstance(node, NavigableString):
                        cleaned = marker_anywhere.sub(' ', str(node))
                        node.replace_with(NavigableString(cleaned.strip()))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(soup))

def ensure_share_button_and_script(soup, ticker, filename):
    from bs4 import Tag
    # Always ensure social-section exists
    header_content = soup.find('div', class_='header-content')
    social_section = soup.find('div', class_='social-section')
    if not social_section and header_content:
        # Create social-section if missing
        social_section = soup.new_tag('div', attrs={'class': 'social-section'})
        # Try to insert after logo-section if exists, else at end
        logo_section = header_content.find('div', class_='logo-section')
        if logo_section:
            logo_section.insert_after(social_section)
        else:
            header_content.append(social_section)
    if social_section:
        # Remove all existing share buttons to avoid duplicates
        for btn in social_section.find_all('button', class_='x-share-btn-custom'):
            btn.decompose()
        # Add share button at the end
        btn = soup.new_tag('button', attrs={'class': 'x-share-btn-custom', 'type': 'button'})
        x_icon = soup.new_tag('span', attrs={'class': 'x-icon'})
        x_img = soup.new_tag('img', src='x.png', alt='X')
        x_icon.append(x_img)
        btn.append(x_icon)
        btn.append(' שתף ב־X')
        social_section.append(btn)
    # Remove all old share scripts
    for script in soup.find_all('script'):
        if script.string and 'x-share-btn-custom' in script.string:
            script.decompose()
    # Add the share script at the end of body, with dynamic share_url
    share_url = f'https://twitter.com/intent/tweet?text=%D7%9E%D7%97%D7%A7%D7%A8%20%D7%97%D7%93%D7%A9%20%D7%A9%D7%9C%20Hippopotamus%20Research%20%24{ticker}%0Ahttps%3A%2F%2Fthekinghippopotamus.github.io%2FHippoResearch_Marketbeat%2Farticles%2F{filename}'
    share_script = soup.new_tag('script')
    share_script.string = f'''
document.addEventListener('DOMContentLoaded', function() {{
  document.querySelectorAll('.x-share-btn-custom').forEach(function(btn) {{
    btn.addEventListener('click', function(e) {{
      e.preventDefault();
      e.stopPropagation();
      var popup = document.createElement('div');
      popup.className = 'share-popup-message';
      popup.textContent = 'השיתוף מחכה לך בדף השני :)';
      document.body.appendChild(popup);
      setTimeout(function() {{
        popup.remove();
        window.open('https://thekinghippopotamus.github.io/HippoResearch_Marketbeat/', '_blank', 'noopener');
        window.open('{share_url}', '_self', 'noopener');
      }}, 3000);
      return false;
    }});
  }});
}});
'''
    soup.body.append(share_script)

# Add a decorator to log function entry/exit for major steps
def log_stage(stage):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            filename = None
            if 'file_path' in kwargs:
                filename = kwargs['file_path']
            elif args:
                if isinstance(args[0], str):
                    filename = args[0]
            logger.info(f"[STAGE] {stage} START {'['+filename+']' if filename else ''}")
            result = func(*args, **kwargs)
            logger.info(f"[STAGE] {stage} END {'['+filename+']' if filename else ''}")
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    main() 