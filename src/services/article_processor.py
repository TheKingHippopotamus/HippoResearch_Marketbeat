"""
Article processing service - handles LLM-based article generation
שירות עיבוד מאמרים - מטפל ביצירת מאמרים מבוססי LLM
"""
import os
import json
import logging
from typing import Optional, Dict, Any

from src.services.llm_service import LLMService
from src.services.entity_service import EntityAnalysisService
from src.config.settings import get_settings
from src.core.types import Result
from src.core.utils import get_current_date, create_safe_filename

logger = logging.getLogger(__name__)


class ArticleProcessorService:
    """
    Service for processing and generating articles
    שירות לעיבוד ויצירת מאמרים
    """
    
    def __init__(self):
        """Initialize article processor"""
        self.settings = get_settings()
        self.llm_service = LLMService()
        self.entity_service = EntityAnalysisService()
    
    def process_with_contextual_prompt(
        self,
        text_block: str,
        ticker_info: Dict[str, Any],
        metadata_path: Optional[str] = None,
        max_tokens: Optional[int] = None,
        original_text: Optional[str] = None
    ) -> Result[str]:
        """
        Process text with contextual prompt (replaces old process_with_contextual_prompt)
        מעבד טקסט עם contextual prompt (מחליף את הפונקציה הישנה)
        
        Args:
            text_block: Original text to process
            ticker_info: Ticker information dictionary
            metadata_path: Path to entity analysis metadata
            max_tokens: Maximum tokens for generation
            original_text: Original text for context
        
        Returns:
            Result with processed article text
        """
        try:
            # Load entity analysis if available
            entity_analysis = ""
            if metadata_path and os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        entity_data = json.load(f)
                        if 'compact_analysis' in entity_data:
                            compact_data = json.loads(entity_data['compact_analysis'])
                            entity_analysis = self._format_entity_analysis(compact_data)
                except Exception as e:
                    logger.warning(f"Could not load entity analysis: {e}")
            
            # Load vocabulary
            vocabulary = self._load_hebrew_vocabulary()
            
            # Generate Hebrew article
            article_result = self._generate_hebrew_article(
                ticker_info.get('ticker', ''),
                entity_analysis,
                vocabulary,
                original_text=original_text or text_block
            )
            
            if article_result.is_err():
                return article_result
            
            # Improve the article
            improved_result = self._improve_hebrew_article(
                article_result.data,
                ticker_info,
                vocabulary,
                max_tokens=max_tokens
            )
            
            return improved_result
            
        except Exception as e:
            error_msg = f"Error in article processing: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
    
    def _format_entity_analysis(self, compact_data: Dict[str, Any]) -> str:
        """Format entity analysis data for prompt"""
        parts = []
        
        if compact_data.get('companies'):
            parts.append(f"**חברות מוזכרות:** {', '.join(compact_data['companies'][:5])}")
        if compact_data.get('people'):
            parts.append(f"**אנשים מוזכרים:** {', '.join(compact_data['people'][:3])}")
        if compact_data.get('industry'):
            parts.append(f"**תחום:** {compact_data['industry']}")
        if compact_data.get('sentiment', {}).get('overall'):
            parts.append(f"**רגש כללי:** {compact_data['sentiment']['overall']}")
        
        if compact_data.get('key_points'):
            parts.append("**נקודות מפתח:**")
            for point in compact_data['key_points'][:3]:
                parts.append(f"• {point.get('text', '')[:200]}...")
        
        if compact_data.get('money_amounts'):
            parts.append(f"**סכומי כסף:** {', '.join(compact_data['money_amounts'][:5])}")
        if compact_data.get('important_dates'):
            parts.append(f"**תאריכים חשובים:** {', '.join(compact_data['important_dates'][:3])}")
        
        return "\n".join(parts)
    
    def _load_hebrew_vocabulary(self) -> str:
        """Load Hebrew vocabulary for prompts"""
        try:
            vocab_path = self.settings.hebrew_vocabulary_file
            if os.path.exists(vocab_path):
                with open(vocab_path, encoding='utf-8') as f:
                    vocab = json.load(f)
                financial_terms = vocab.get('financial_terms', {})
                terms = [f"{eng} → {heb}" for eng, heb in list(financial_terms.items())[:25]]
                return "\n".join(terms)
            return ""
        except Exception as e:
            logger.warning(f"Could not load vocabulary: {e}")
            return ""
    
    def _generate_hebrew_article(
        self,
        ticker: str,
        entity_analysis: str,
        vocabulary: str,
        original_text: str
    ) -> Result[str]:
        """Generate Hebrew article using LLM"""
        # Extract entities
        entities = self._extract_entities(original_text)
        entity_list = ', '.join(sorted(set(entities)))
        
        # Mark entities in text
        marked_text = self._mark_entities(original_text, entities)
        
        prompt = f"""אתה מומחה לכתיבת כתבות פיננסיות בעברית. כתוב כתבה מקצועית ומעניינת על {ticker}.

**חשוב מאוד - הוראות לכתיבה:**
- אל תתרגם שמות של חברות, תרופות, אנשים, סימולים, מונחים מקצועיים – השאר אותם באנגלית כפי שמופיעים בטקסט המקורי.
- להלן רשימת ישויות שיש לשמר באנגלית: {entity_list}
- בנה פתיחה מעניינת בהתבסס על המידע הספציפי שתקבל
- כתוב בשפה מקצועית אך נגישה

**מידע לניתוח:**
{entity_analysis}

**מילון מונחים רלוונטיים:**
{vocabulary}

**טקסט מקורי מסומן:**
{marked_text}

כתוב כתבה מקצועית ומעניינת בעברית:"""
        
        result = self.llm_service.generate(
            prompt,
            num_predict=1024,
            temperature=self.settings.llm_temperature,
            top_p=self.settings.llm_top_p
        )
        
        if result.is_ok():
            # Restore entities
            text = self._restore_entities(result.data, entities)
            return Result.ok(text)
        
        return result
    
    def _improve_hebrew_article(
        self,
        article_text: str,
        ticker_info: Dict[str, Any],
        vocabulary_examples: str,
        max_tokens: Optional[int] = None
    ) -> Result[str]:
        """Improve Hebrew article with grammar and style corrections"""
        prompt = f"""ערוך את המאמר הבא כך שיהיה תקני, מקצועי, ברור, ועם דקדוק נכון בעברית.

**הוראות עריכה:**
1. בדוק דקדוק עברי נכון
2. תרגם מונחים פיננסיים לעברית מדויקת
3. ודא שכל הנתונים המדויקים נשמרים
4. שפר ניסוחים לעברית טבעית
5. הוסף או תיקן הדגשות (**טקסט**) למילות מפתח

**מאמר לעריכה:**
{article_text}"""
        
        return self.llm_service.generate(
            prompt,
            num_predict=max_tokens or self.settings.max_tokens_default
        )
    
    def _extract_entities(self, text: str) -> list:
        """Extract entity names from text"""
        import re
        pattern = re.compile(r'\b([A-Z][A-Za-z0-9&.()\-]+)\b')
        return list(pattern.findall(text))
    
    def _mark_entities(self, text: str, entities: list) -> str:
        """Mark entities in text with [[...]]"""
        import re
        for ent in sorted(entities, key=len, reverse=True):
            text = re.sub(rf'\b{re.escape(ent)}\b', f'[[{ent}]]', text)
        return text
    
    def _restore_entities(self, text: str, entities: list) -> str:
        """Restore marked entities to original form"""
        import re
        for ent in sorted(entities, key=len, reverse=True):
            text = re.sub(rf'\[\[.*?{re.escape(ent)}.*?\]\]', ent, text)
        return text

