"""
Article HTML generation service
שירות ליצירת HTML של מאמרים
"""
import os
import re
import logging
from typing import Dict, Any, Optional

from src.config.settings import get_settings
from src.core.types import Result
from src.core.utils import get_current_date, create_safe_filename, get_current_timestamp, ensure_directory_exists

logger = logging.getLogger(__name__)


class ArticleHTMLGenerator:
    """
    Service for generating HTML articles
    שירות ליצירת מאמרי HTML
    """
    
    def __init__(self):
        """Initialize HTML generator"""
        self.settings = get_settings()
    
    def generate_html_article(
        self,
        ticker: str,
        processed_text: str,
        ticker_info: Optional[Dict[str, Any]] = None
    ) -> Result[str]:
        """
        Generate HTML article from processed text
        יוצר מאמר HTML מטקסט מעובד
        
        Args:
            ticker: Ticker symbol
            processed_text: Processed article text
            ticker_info: Optional ticker metadata
        
        Returns:
            Result with HTML file path or error
        """
        try:
            ensure_directory_exists(self.settings.articles_dir)
            
            # Create filename
            safe_ticker = create_safe_filename(ticker)
            current_date = get_current_date()
            html_filename = f"{safe_ticker}_{current_date}.html"
            html_filepath = os.path.join(self.settings.articles_dir, html_filename)
            
            # Format content
            formatted_content = self._convert_to_html(processed_text)
            
            # Build HTML
            html_content = self._build_html(
                ticker=ticker,
                content=formatted_content,
                ticker_info=ticker_info or {}
            )
            
            # Save file
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ HTML article saved for {ticker} → {html_filepath}")
            return Result.ok(html_filepath)
            
        except Exception as e:
            error_msg = f"Failed to generate HTML article: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
    
    def _convert_to_html(self, text: str) -> str:
        """Convert processed text to HTML format"""
        from src.core.text_processing import convert_tagged_text_to_html
        return convert_tagged_text_to_html(text)
    
    def _build_html(
        self,
        ticker: str,
        content: str,
        ticker_info: Dict[str, Any]
    ) -> str:
        """Build full HTML document"""
        # Load template
        template_path = os.path.join(self.settings.templates_dir, "article_template.html")
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                # Replace placeholders
                company_name = ticker_info.get('Security') or ticker
                title = f"{company_name} ({ticker}) - מחקר כלכלי מתקדם | Hippopotamus Research"
                timestamp = get_current_timestamp()
                
                html = template.replace("{{TITLE}}", title)
                html = html.replace("{{TICKER}}", ticker)
                html = html.replace("{{ARTICLE_BODY}}", content)
                html = html.replace("{{TIMESTAMP}}", timestamp)
                
                return html
            except Exception as e:
                logger.warning(f"⚠️ Could not load template: {e}, using default")
        
        # Fallback: default HTML
        return self._default_html_template(ticker, content, ticker_info)
    
    def _default_html_template(
        self,
        ticker: str,
        content: str,
        ticker_info: Dict[str, Any]
    ) -> str:
        """Default HTML template if template file not found"""
        company_name = ticker_info.get('Security') or ticker
        title = f"{company_name} ({ticker}) - מחקר כלכלי מתקדם"
        
        return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <article>
        <h1>{title}</h1>
        <div class="article-content">
            {content}
        </div>
        <footer>
            <p>נוצר ב: {get_current_timestamp()}</p>
        </footer>
    </article>
</body>
</html>"""

