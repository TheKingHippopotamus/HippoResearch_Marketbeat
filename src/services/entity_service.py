"""
Entity analysis service - wrapper around existing entity_analyzer
שירות ניתוח ישויות - wrapper מסביב ל-entity_analyzer הקיים
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.config.settings import get_settings
from src.core.types import Result
from src.core.exceptions import EntityAnalysisError
from src.core.utils import get_current_date, ensure_directory_exists

logger = logging.getLogger(__name__)


class EntityAnalysisService:
    """
    Service for entity analysis using spaCy
    שירות לניתוח ישויות באמצעות spaCy
    """
    
    def __init__(self):
        """Initialize entity analysis service"""
        self.settings = get_settings()
        self._analyzer = None
    
    def _get_analyzer(self):
        """Get or create entity analyzer instance (lazy loading)"""
        if self._analyzer is None:
            try:
                from tools.entity_analyzer import get_entity_analyzer
                self._analyzer = get_entity_analyzer()
            except ImportError:
                logger.warning("⚠️ Could not import entity_analyzer, entity analysis disabled")
                return None
        return self._analyzer
    
    def analyze_text(self, text: str, ticker: Optional[str] = None) -> Result[Dict[str, Any]]:
        """
        Analyze text and extract entities
        מנתח טקסט ומחלץ ישויות
        
        Args:
            text: Text to analyze
            ticker: Optional ticker symbol for context
        
        Returns:
            Result with analysis dictionary or error
        """
        try:
            analyzer = self._get_analyzer()
            if analyzer is None:
                return Result.err("Entity analyzer not available")
            
            analysis = analyzer.analyze_text(text, ticker)
            
            if not analysis:
                return Result.err("Empty analysis result")
            
            return Result.ok(analysis)
            
        except Exception as e:
            error_msg = f"Entity analysis failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
    
    def save_analysis(self, analysis: Dict[str, Any], ticker: str) -> Result[str]:
        """
        Save entity analysis to file
        שומר ניתוח ישויות לקובץ
        
        Args:
            analysis: Analysis dictionary
            ticker: Ticker symbol
        
        Returns:
            Result with file path or error
        """
        try:
            ensure_directory_exists(self.settings.entity_analyzer_db)
            current_date = get_current_date()
            filename = f"{ticker}_entity_analysis_{current_date}.json"
            filepath = os.path.join(self.settings.entity_analyzer_db, filename)
            
            # Use existing save function
            from tools.entity_analyzer import save_compact_entity_analysis
            save_compact_entity_analysis(analysis, ticker, self.settings.entity_analyzer_db)
            
            logger.info(f"✅ Entity analysis saved for {ticker} → {filepath}")
            return Result.ok(filepath)
            
        except Exception as e:
            error_msg = f"Failed to save entity analysis: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
    
    def analyze_and_save(self, text: str, ticker: str) -> Result[Dict[str, Any]]:
        """
        Analyze text and save results
        מנתח טקסט ושומר תוצאות
        
        Args:
            text: Text to analyze
            ticker: Ticker symbol
        
        Returns:
            Result with analysis dictionary
        """
        # Analyze
        analysis_result = self.analyze_text(text, ticker)
        if analysis_result.is_err():
            return analysis_result
        
        # Save
        save_result = self.save_analysis(analysis_result.data, ticker)
        if save_result.is_err():
            logger.warning(f"⚠️ Analysis succeeded but save failed: {save_result.error}")
            # Still return the analysis even if save failed
            return analysis_result
        
        return analysis_result
    
    def load_existing_analysis(self, ticker: str) -> Result[Dict[str, Any]]:
        """
        Load existing entity analysis for ticker
        טוען ניתוח ישויות קיים עבור ticker
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            Result with analysis dictionary or error
        """
        try:
            from tools.entity_analyzer import load_existing_entity_analysis
            analysis = load_existing_entity_analysis(ticker, self.settings.entity_analyzer_db)
            
            if analysis is None:
                return Result.err(f"No existing analysis found for {ticker}")
            
            return Result.ok(analysis)
            
        except Exception as e:
            error_msg = f"Failed to load existing analysis: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)

