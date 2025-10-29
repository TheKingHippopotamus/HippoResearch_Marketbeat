"""
MarketBeat scraper implementation
מימוש scraper ל-MarketBeat
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.data.scrapers.base import BaseScraper
from src.core.types import Result
from src.core.exceptions import ScrapingError
from src.config.settings import get_settings
from src.core.utils import get_current_date, ensure_directory_exists
import os
import logging

logger = logging.getLogger(__name__)


class MarketBeatScraper(BaseScraper):
    """
    Scraper for MarketBeat website
    Scraper לאתר MarketBeat
    """
    
    def __init__(self):
        """Initialize the scraper with settings"""
        self.settings = get_settings()
        self._driver = None
    
    def _start_driver(self):
        """Start Selenium WebDriver"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return webdriver.Chrome(options=options)
    
    def _close_popup_if_present(self, driver):
        """Close popup if it appears"""
        try:
            time.sleep(self.settings.popup_wait_time)
            popup = driver.find_element(By.CSS_SELECTOR, "div.bg-white")
            driver.execute_script("""
                arguments[0].style.display = 'none';
                arguments[0].remove();
            """, popup)
            logger.info("🧹 Closed popup")
        except Exception:
            logger.info("✅ No popup found or already closed.")
    
    def _find_and_extract_summary(self, driver, ticker: str) -> str:
        """
        Find and extract the AI summary block
        מוצא ומחלץ את בלוק הסיכום של AI
        """
        try:
            wait = WebDriverWait(driver, self.settings.selenium_timeout)
            
            # Look for the AI summary block
            summary_selectors = [
                "div.border.rounded.p-3.font-small.mb-3.bg-light-blue.ai-summary",
                "div.ai-summary",
                "div.bg-light-blue.ai-summary",
                "div[class*='ai-summary']"
            ]
            
            for selector in summary_selectors:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Found AI summary block using selector: {selector}")
                    return element.text
                except Exception:
                    continue
            
            # Try finding by content pattern
            try:
                elements = driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'ai-summary') or contains(@class, 'bg-light-blue')]"
                )
                for element in elements:
                    if "AI Generated" in element.text or "Posted" in element.text:
                        logger.info("✅ Found AI summary block by content pattern")
                        return element.text
            except Exception:
                pass
            
            logger.error(f"❌ Could not find AI summary block for {ticker}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding summary block: {e}")
            return None
    
    def scrape(self, ticker: str) -> Result[str]:
        """
        Scrape text from MarketBeat for given ticker
        גורפ טקסט מ-MarketBeat עבור טיקר נתון
        
        Args:
            ticker: Ticker symbol (e.g., "AAPL")
        
        Returns:
            Result with scraped text or error message
        """
        url = self.settings.marketbeat_url_template.format(ticker=ticker)
        driver = None
        
        try:
            logger.info(f"🌐 Opening URL for {ticker}...")
            driver = self._start_driver()
            driver.get(url)
            time.sleep(1)
            
            # Close popup if present
            self._close_popup_if_present(driver)
            
            # Find and extract summary
            summary_text = self._find_and_extract_summary(driver, ticker)
            
            if not summary_text:
                return Result.err(f"No matching summary block found for {ticker}")
            
            logger.info(f"📄 Scraped text length: {len(summary_text)} characters")
            return Result.ok(summary_text)
            
        except Exception as e:
            error_msg = f"Error during scraping for {ticker}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
        
        finally:
            if driver:
                driver.quit()
                logger.info("🌐 Browser closed")
    
    def scrape_and_save(self, ticker: str, output_dir: str = "txt") -> Result[tuple[str, str]]:
        """
        Scrape text and save to file (for backward compatibility)
        גורפ טקסט ושומר לקובץ (לתאימות אחורה)
        
        Args:
            ticker: Ticker symbol
            output_dir: Directory to save the file
        
        Returns:
            Result with (text, filename) tuple or error
        """
        # Scrape
        scrape_result = self.scrape(ticker)
        if scrape_result.is_err():
            return scrape_result
        
        # Save to file
        try:
            ensure_directory_exists(output_dir)
            current_date = get_current_date()
            filename = f"{ticker}_original_{current_date}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(scrape_result.data)
            
            logger.info(f"✅ Original text for {ticker} saved → {filepath}")
            return Result.ok((scrape_result.data, filename))
            
        except Exception as e:
            error_msg = f"Error saving scraped text: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)

