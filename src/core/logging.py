"""
Advanced logging system with daily rotation and structured logging
מערכת לוגים מתקדמת עם רוטציה יומית ולוגים מובנים
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

from src.config.settings import get_settings


class DailyFileHandler(logging.FileHandler):
    """
    File handler that creates daily log files
    File handler שיוצר קבצי לוג יומיים
    """
    
    def __init__(self, log_dir: str, base_filename: str = "marketbit"):
        """
        Initialize daily file handler
        
        Args:
            log_dir: Directory for log files
            base_filename: Base name for log files
        """
        self.log_dir = log_dir
        self.base_filename = base_filename
        self.current_date = None
        self.log_file_path = None
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize with today's log file
        self._update_log_file()
        
        super().__init__(self.log_file_path, encoding='utf-8', mode='a')
    
    def _update_log_file(self):
        """Update log file path based on current date"""
        today = datetime.now().strftime("%Y%m%d")
        if self.current_date != today:
            self.current_date = today
            self.log_file_path = os.path.join(
                self.log_dir,
                f"{self.base_filename}_{today}.log"
            )
            # If file already exists, update it
            if self.current_date and os.path.exists(self.log_file_path):
                return
            # Close old handler if exists
            if self.baseFilename:
                self.close()
            # Open new file
            if self.current_date:
                self.baseFilename = self.log_file_path
    
    def emit(self, record):
        """Emit a record, updating file if date changed"""
        # Check if date changed
        today = datetime.now().strftime("%Y%m%d")
        if self.current_date != today:
            self._update_log_file()
        super().emit(record)


def setup_logging(
    log_level: int = logging.INFO,
    use_console: bool = True,
    use_file: bool = True,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Setup advanced logging system
    הגדרת מערכת לוגים מתקדמת
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        use_console: Enable console logging
        use_file: Enable file logging
        log_dir: Directory for log files (defaults to settings)
    
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    
    # Get root logger
    logger = logging.getLogger('marketbit')
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Format
    detailed_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
    simple_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    formatter_detailed = logging.Formatter(detailed_format, datefmt='%Y-%m-%d %H:%M:%S')
    formatter_simple = logging.Formatter(simple_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Console handler (simple format)
    if use_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter_simple)
        logger.addHandler(console_handler)
    
    # File handler (detailed format with daily rotation)
    if use_file:
        log_directory = log_dir or settings.logs_dir
        file_handler = DailyFileHandler(log_directory, "marketbit")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter_detailed)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance for a module
    מקבל instance של logger למודול
    
    Args:
        name: Optional module name
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'marketbit.{name}')
    return logging.getLogger('marketbit')


