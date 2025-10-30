"""
Post-processing utilities for HTML articles
Utilities לעיבוד לאחר יצירת מאמרי HTML
"""
import os
import re
import subprocess
import sys
import logging
from typing import Optional

from src.config.settings import get_settings
from src.core.utils import get_current_date
from src.core.text_processing import convert_tagged_text_to_html

logger = logging.getLogger(__name__)


class PostProcessor:
    """
    Post-processing for HTML articles
    עיבוד לאחר יצירת מאמרי HTML
    """
    
    def __init__(self):
        """Initialize post processor"""
        self.settings = get_settings()
    
    def auto_fix_article_html(self, ticker: str) -> bool:
        """
        Auto-fix article HTML formatting
        מתקן אוטומטית את עיצוב HTML של המאמר
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            True if successful
        """
        try:
            current_date = get_current_date()
            html_path = os.path.join(self.settings.articles_dir, f"{ticker}_{current_date}.html")
            txt_path = os.path.join(self.settings.txt_dir, f"{ticker}_processed_{current_date}.txt")
            
            if not os.path.exists(txt_path):
                logger.warning(f"⚠️ Processed text file not found: {txt_path}")
                return False
            
            if not os.path.exists(html_path):
                logger.warning(f"⚠️ HTML file not found: {html_path}")
                return False
            
            # Read processed text
            with open(txt_path, 'r', encoding='utf-8') as f:
                processed_text = f.read()
            
            # Convert to HTML
            html_content = convert_tagged_text_to_html(processed_text)
            
            # Read existing HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            # Replace content in article-content-text div
            new_html = re.sub(
                r'(<div class="article-content-text">)[\s\S]*?(</div>)',
                f'\\1\n{html_content}\n\\2',
                html
            )
            
            # Write back
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            
            logger.info(f"✅ Auto-fixed HTML for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Auto-fix failed for {ticker}: {e}")
            return False
    
    def run_js_cleaner(self, ticker: str) -> bool:
        """
        Run JavaScript cleaner on HTML file
        מריץ JavaScript cleaner על קובץ HTML
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            True if successful
        """
        try:
            current_date = get_current_date()
            html_path = os.path.join(self.settings.articles_dir, f"{ticker}_{current_date}.html")
            
            if not os.path.exists(html_path):
                logger.warning(f"⚠️ HTML file not found: {html_path}")
                return False
            
            # Check if inject_js_cleaner.py exists (in tools - backward compat check)
            cleaner_script = "tools/inject_js_cleaner.py"
            if not os.path.exists(cleaner_script):
                logger.warning(f"⚠️ JS cleaner script not found: {cleaner_script}")
                # Continue without JS cleaner - not critical
                return True
            
            logger.info(f"🧹 Running JavaScript cleaner on {ticker}...")
            
            result = subprocess.run(
                [
                    sys.executable,
                    cleaner_script,
                    "--file", html_path,
                    "--no-backup"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ JavaScript cleaner completed for {ticker}")
                return True
            else:
                logger.warning(f"⚠️ JavaScript cleaner warning: {result.stderr}")
                return True  # Non-critical, continue
            
        except subprocess.TimeoutExpired:
            logger.warning(f"⚠️ JS cleaner timed out for {ticker}")
            return True  # Non-critical
        except Exception as e:
            logger.warning(f"⚠️ Error running JS cleaner: {e}")
            return True  # Non-critical, continue


# Global instance
_post_processor: Optional[PostProcessor] = None


def get_post_processor() -> PostProcessor:
    """
    Get global post processor instance (singleton)
    מקבל instance גלובלי של post processor (singleton)
    
    Returns:
        PostProcessor instance
    """
    global _post_processor
    if _post_processor is None:
        _post_processor = PostProcessor()
    return _post_processor


