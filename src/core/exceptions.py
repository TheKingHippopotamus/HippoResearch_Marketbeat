"""
Custom exceptions for MarketBit system
Exceptions מותאמים למערכת MarketBit
"""


class MarketBitError(Exception):
    """Base exception for all MarketBit errors"""
    pass


class ScrapingError(MarketBitError):
    """Error occurred during web scraping"""
    pass


class LLMProcessingError(MarketBitError):
    """Error occurred during LLM processing"""
    pass


class EntityAnalysisError(MarketBitError):
    """Error occurred during entity analysis"""
    pass


class ProcessingError(MarketBitError):
    """General processing error"""
    pass


class ConfigurationError(MarketBitError):
    """Configuration error - missing or invalid settings"""
    pass


class FileOperationError(MarketBitError):
    """Error during file operations"""
    pass


class GitOperationError(MarketBitError):
    """Error during Git operations"""
    pass

