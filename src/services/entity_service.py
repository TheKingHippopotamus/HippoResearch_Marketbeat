"""
Advanced Entity Analysis Service with high-resolution sentiment analysis
שירות ניתוח ישויות מתקדם עם ניתוח סנטימנט ברזולוציה גבוהה
"""
import os
import json
import logging
import re
from typing import Optional, Dict, Any, Set, List
from datetime import datetime

from src.config.settings import get_settings
from src.core.types import Result
from src.core.exceptions import EntityAnalysisError
from src.core.utils import get_current_date, ensure_directory_exists
from src.data.analyzers.spacy_analyzer import get_spacy_analyzer
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class EntityAnalysisService:
    """
    Advanced entity analysis service with spaCy and high-resolution analysis
    שירות ניתוח ישויות מתקדם עם spaCy וניתוח ברזולוציה גבוהה
    """
    
    def __init__(self):
        """Initialize entity analysis service"""
        self.settings = get_settings()
        self.spacy_analyzer = get_spacy_analyzer()
        self.llm_service = LLMService()
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        ensure_directory_exists(self.settings.entity_analyzer_db)
    
    def analyze_text(self, text: str, ticker: Optional[str] = None) -> Result[Dict[str, Any]]:
        """
        Analyze text with high-resolution sentiment and comprehensive extraction
        מנתח טקסט עם סנטימנט ברזולוציה גבוהה וחילוץ מקיף
        
        Args:
            text: Text to analyze
            ticker: Optional ticker symbol for context
        
        Returns:
            Result with detailed analysis dictionary
        """
        try:
            if not text or len(text.strip()) == 0:
                return Result.err("Empty text provided")
            
            # Step 1: Base spaCy analysis
            base_analysis = self.spacy_analyzer.analyze(text, ticker)
            if not base_analysis:
                return Result.err("spaCy analysis failed")
            
            # Step 2: Enhance with high-resolution sentiment analysis
            enhanced_analysis = self._enhance_with_high_resolution_sentiment(
                base_analysis,
                text,
                ticker
            )
            
            # Step 3: Translate key points to Hebrew (optional, async could be added)
            enhanced_analysis = self._add_hebrew_translations(enhanced_analysis)
            
            return Result.ok(enhanced_analysis)
            
        except Exception as e:
            error_msg = f"Entity analysis failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
    
    def _enhance_with_high_resolution_sentiment(
        self,
        base_analysis: Dict[str, Any],
        text: str,
        ticker: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance analysis with sentence-level sentiment and detailed extraction
        משפר ניתוח עם סנטימנט ברמת משפט וחילוץ מפורט
        """
        # Split into fine-grained segments
        segments = self._split_into_segments(text)
        
        # Analyze each segment individually
        detailed_segments = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        all_entities = set()
        all_money = set(base_analysis.get('financial_data', {}).get('money_amounts', []))
        all_dates = set(base_analysis.get('financial_data', {}).get('important_dates', []))
        all_percentages = set(base_analysis.get('financial_data', {}).get('percentages', []))
        all_keywords = set(base_analysis.get('financial_data', {}).get('financial_keywords', []))
        
        # Extract base entities
        for ent in base_analysis.get('entities', []):
            if ent.get('is_company'):
                all_entities.add(ent.get('text'))
            elif ent.get('label') == 'PERSON':
                all_entities.add(ent.get('text'))
        
        for segment in segments:
            if not segment.strip() or len(segment.strip()) < 10:
                continue
            
            # Segment-level analysis
            segment_sentiment = self._analyze_segment_sentiment(segment)
            sentiment_counts[segment_sentiment] += 1
            
            # Extract segment-specific data
            segment_entities = self._extract_entities_from_segment(segment)
            all_entities.update(segment_entities)
            
            segment_money = self._extract_money_from_segment(segment)
            all_money.update(segment_money)
            
            segment_dates = self._extract_dates_from_segment(segment)
            all_dates.update(segment_dates)
            
            segment_percentages = self._extract_percentages_from_segment(segment)
            all_percentages.update(segment_percentages)
            
            segment_keywords = self._extract_financial_keywords(segment)
            all_keywords.update(segment_keywords)
            
            # Calculate importance
            importance = self._calculate_segment_importance(segment, ticker)
            
            detailed_segments.append({
                'text': segment.strip(),
                'sentiment': segment_sentiment,
                'importance_score': importance,
                'entities': segment_entities,
                'money_amounts': list(segment_money),
                'dates': list(segment_dates),
                'percentages': list(segment_percentages)
            })
        
        # Sort by importance
        detailed_segments.sort(key=lambda x: x['importance_score'], reverse=True)
        
        # Build enhanced key points (keep ALL segments - no filtering)
        enhanced_key_points = [
            {
                'text': seg['text'],
                'importance_score': seg['importance_score'],
                'sentiment': seg['sentiment'],
                'entities_in_segment': seg['entities'],
                'money_in_segment': seg['money_amounts'],
                'dates_in_segment': seg['dates']
            }
            for seg in detailed_segments
        ]
        
        # Recalculate overall sentiment
        total_segments = sum(sentiment_counts.values())
        if total_segments > 0:
            if sentiment_counts['positive'] > sentiment_counts['negative']:
                overall = 'positive'
            elif sentiment_counts['negative'] > sentiment_counts['positive']:
                overall = 'negative'
            else:
                overall = 'neutral'
        else:
            overall = base_analysis.get('sentiment_analysis', {}).get('sentiment_label', 'neutral')
        
        # Build enhanced analysis
        enhanced = base_analysis.copy()
        enhanced.update({
            'companies': sorted(list(all_entities)),
            'people': [],  # Will be populated from spaCy entities
            'sentiment': {
                'overall': overall,
                'positive_count': sentiment_counts['positive'],
                'negative_count': sentiment_counts['negative'],
                'neutral_count': sentiment_counts['neutral'],
                'total_segments': total_segments,
                'sentiment_breakdown': {
                    'positive_percentage': round(sentiment_counts['positive'] / total_segments * 100, 2) if total_segments > 0 else 0,
                    'negative_percentage': round(sentiment_counts['negative'] / total_segments * 100, 2) if total_segments > 0 else 0,
                    'neutral_percentage': round(sentiment_counts['neutral'] / total_segments * 100, 2) if total_segments > 0 else 0
                }
            },
            'key_points': enhanced_key_points,
            'money_amounts': sorted(list(all_money), key=len, reverse=True),
            'important_dates': sorted(list(all_dates)),
            'percentages': sorted(list(all_percentages)),
            'financial_keywords': sorted(list(all_keywords)),
            'total_segments_analyzed': len(detailed_segments),
            'analysis_resolution': 'high'
        })
        
        # Separate companies and people
        enhanced['people'] = [ent for ent in enhanced['companies'] 
                            if any(char.islower() for char in ent) and 
                            ent not in ['Apple', 'Fed', 'Robert']]
        enhanced['companies'] = [c for c in enhanced['companies'] if c not in enhanced['people']]
        
        return enhanced
    
    def _split_into_segments(self, text: str) -> List[str]:
        """Split text into fine-grained segments for analysis"""
        segments = []
        
        # Split by explicit sentiment markers first
        parts = re.split(r'(Positive Sentiment:|Negative Sentiment:|Neutral Sentiment:)', text)
        
        current_segment = ""
        for i, part in enumerate(parts):
            if part in ['Positive Sentiment:', 'Negative Sentiment:', 'Neutral Sentiment:']:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = part + " "
            elif part.strip():
                current_segment += part
                # Also split by sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', part)
                if len(sentences) > 1:
                    if current_segment:
                        segments.append(current_segment.strip())
                    segments.extend([s.strip() for s in sentences[1:] if s.strip()])
                    current_segment = ""
                else:
                    current_segment += " "
        
        if current_segment:
            segments.append(current_segment.strip())
        
        # If no explicit markers, split by sentences
        if not segments or all('Sentiment:' not in s for s in segments):
            sentences = re.split(r'(?<=[.!?])\s+|(?<=\n)\s*', text)
            segments = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return segments
    
    def _analyze_segment_sentiment(self, segment: str) -> str:
        """Analyze sentiment of a single segment"""
        segment_lower = segment.lower()
        
        # Explicit markers
        if 'positive sentiment:' in segment_lower or 'bullish' in segment_lower:
            return 'positive'
        if 'negative sentiment:' in segment_lower or 'bearish' in segment_lower:
            return 'negative'
        if 'neutral sentiment:' in segment_lower:
            return 'neutral'
        
        # Keyword-based analysis
        positive_keywords = [
            'strong', 'boost', 'upgrade', 'higher', 'raising', 'increases', 
            'outperform', 'upbeat', 'revived', 'crossed', 'milestone', 
            'confidence', 'top', 'growth', 'success', 'gain', 'beat', 'exceed'
        ]
        negative_keywords = [
            'ordered to pay', 'court ordered', 'legal risk', 'risk', 
            'sell-off', 'headwind', 'modest hit', 'uncertainty', 
            'decline', 'loss', 'fall', 'drop', 'miss', 'below', 'cut'
        ]
        
        positive_score = sum(1 for kw in positive_keywords if kw in segment_lower)
        negative_score = sum(1 for kw in negative_keywords if kw in segment_lower)
        
        if positive_score > negative_score and positive_score > 0:
            return 'positive'
        elif negative_score > positive_score and negative_score > 0:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_entities_from_segment(self, segment: str) -> List[str]:
        """Extract entities from a segment"""
        entities = []
        
        # Multi-word capitalized
        multi = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z.]+)+)\b', segment)
        entities.extend(multi)
        
        # All caps (tickers, acronyms)
        all_caps = re.findall(r'\b([A-Z]{2,})\b', segment)
        entities.extend(all_caps)
        
        # Single capitalized (exclude common words)
        single = re.findall(r'\b([A-Z][a-z]{3,})\b', segment)
        common = {'The', 'This', 'That', 'These', 'Those', 'They', 'There',
                 'Positive', 'Negative', 'Neutral', 'Sentiment', 'Apple'}
        entities.extend([w for w in single if w not in common])
        
        return list(set([e for e in entities if e and len(e) > 2]))
    
    def _extract_money_from_segment(self, segment: str) -> Set[str]:
        """Extract money amounts from segment"""
        patterns = [
            r'\$[\d.,]+\s*(?:billion|million|trillion|B|M|T|bn|mn)',
            r'\$[\d.,]+',
            r'€[\d.,]+\s*(?:billion|million|trillion|B|M|T|bn|mn)',
            r'€[\d.,]+',
            r'[\d.,]+\s*(?:billion|million|trillion)\s*(?:dollars|USD)'
        ]
        money = set()
        for pattern in patterns:
            money.update(re.findall(pattern, segment, re.IGNORECASE))
        return money
    
    def _extract_dates_from_segment(self, segment: str) -> Set[str]:
        """Extract dates from segment"""
        patterns = [
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\b(?:Q[1-4]|quarter)\s+\d{4}',
            r'\bfiscal\s+(?:Q[1-4]|year|quarter)'
        ]
        dates = set()
        for pattern in patterns:
            dates.update(re.findall(pattern, segment, re.IGNORECASE))
        return dates
    
    def _extract_percentages_from_segment(self, segment: str) -> Set[str]:
        """Extract percentages from segment"""
        percentages = set(re.findall(r'[\d.,]+\s*%', segment))
        return percentages
    
    def _extract_financial_keywords(self, segment: str) -> Set[str]:
        """Extract financial keywords from segment"""
        keywords = {
            'revenue', 'earnings', 'price target', 'market cap', 'upgrade', 'downgrade',
            'outperform', 'rating', 'analyst', 'valuation', 'trading', 'stock',
            'dividend', 'dividend yield', 'EPS', 'P/E', 'guidance', 'forecast'
        }
        segment_lower = segment.lower()
        return {kw for kw in keywords if kw in segment_lower}
    
    def _calculate_segment_importance(self, segment: str, ticker: Optional[str] = None) -> int:
        """Calculate importance score for segment"""
        score = 10  # Base score
        
        if ticker and ticker.upper() in segment.upper():
            score += 50
        
        if '$' in segment or '€' in segment or 'billion' in segment.lower():
            score += 30
        
        if re.search(r'\d+', segment):
            score += 20
        
        financial_terms = ['revenue', 'earnings', 'price target', 'analyst', 'upgrade']
        score += sum(10 for term in financial_terms if term in segment.lower())
        
        length = len(segment)
        if 50 <= length <= 500:
            score += 20
        
        return score
    
    def _add_hebrew_translations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add Hebrew translations for key points using LLM
        מוסיף תרגומים לעברית לנקודות מפתח באמצעות LLM
        """
        key_points = analysis.get('key_points', [])
        if not key_points:
            analysis['key_points_he'] = []
            return analysis
        
        entities = set(analysis.get('companies', []) + analysis.get('people', []))
        entity_list = ', '.join(sorted(list(entities)))[:500]  # Limit length
        
        hebrew_translations = []
        
        for kp in key_points[:10]:  # Limit to top 10 for performance
            text = kp.get('text', '')
            if not text:
                hebrew_translations.append("")
                continue
            
            # Mark entities
            marked_text = self._mark_entities_for_translation(text, entities)
            
            prompt = f"""תרגם את המשפט הבא לעברית מקצועית. שמור על שמות חברות, סימולים, אנשים ומונחים מקצועיים באנגלית (למשל: {entity_list}). 

משפט: {marked_text}"""
            
            try:
                result = self.llm_service.generate(
                    prompt,
                    max_tokens=300,
                    temperature=0.4
                )
                
                if result.is_ok():
                    translated = self._restore_marked_entities(result.data, entities)
                    hebrew_translations.append(translated.strip())
                else:
                    hebrew_translations.append("")
            except Exception as e:
                logger.warning(f"⚠️ Translation failed for segment: {e}")
                hebrew_translations.append("")
        
        analysis['key_points_he'] = hebrew_translations
        return analysis
    
    def _mark_entities_for_translation(self, text: str, entities: Set[str]) -> str:
        """Mark entities in text for translation protection"""
        marked = text
        for entity in sorted(entities, key=len, reverse=True):
            if len(entity) > 2:
                pattern = r'\b' + re.escape(entity) + r'\b'
                marked = re.sub(pattern, f'[[{entity}]]', marked, flags=re.IGNORECASE)
        return marked
    
    def _restore_marked_entities(self, text: str, entities: Set[str]) -> str:
        """Restore marked entities after translation"""
        restored = text
        for entity in entities:
            pattern = r'\[\[(' + re.escape(entity) + r')\]\]'
            restored = re.sub(pattern, entity, restored, flags=re.IGNORECASE)
        return restored
    
    def save_analysis(self, analysis: Dict[str, Any], ticker: str) -> Result[str]:
        """
        Save entity analysis to file with compact format
        שומר ניתוח ישויות לקובץ בפורמט compact
        """
        try:
            ensure_directory_exists(self.settings.entity_analyzer_db)
            current_date = get_current_date()
            filename = f"{ticker}_entity_analysis_{current_date}.json"
            filepath = os.path.join(self.settings.entity_analyzer_db, filename)
            
            # Build compact analysis for LLM processing
            compact = {
                'ticker': ticker,
                'timestamp': analysis.get('timestamp', datetime.now().isoformat()),
                'companies': analysis.get('companies', []),
                'people': analysis.get('people', []),
                'sentiment': analysis.get('sentiment', {}),
                'industry': analysis.get('industry_keywords', 'unknown'),
                'key_points': [
                    {
                        'text': kp.get('text', '')[:500],
                        'importance_score': kp.get('importance_score', 0),
                        'sentiment': kp.get('sentiment', 'neutral')
                    }
                    for kp in analysis.get('key_points', [])
                ],
                'money_amounts': analysis.get('money_amounts', []),
                'important_dates': analysis.get('important_dates', []),
                'financial_keywords': analysis.get('financial_keywords', []),
                'key_relationships': [
                    {
                        'subject': r.get('subject', ''),
                        'verb': r.get('verb', ''),
                        'object': r.get('object', ''),
                        'importance': r.get('importance', 0)
                    }
                    for r in analysis.get('relationships', [])[:5]
                ],
                'business_context': []
            }
            
            # Full analysis with Hebrew translations
            full_analysis = {
                'ticker': ticker,
                'timestamp': analysis.get('timestamp', datetime.now().isoformat()),
                'companies': analysis.get('companies', []),
                'people': analysis.get('people', []),
                'sentiment': analysis.get('sentiment', {}),
                'industry': analysis.get('industry_keywords', 'unknown'),
                'key_points': analysis.get('key_points', []),
                'money_amounts': analysis.get('money_amounts', []),
                'important_dates': analysis.get('important_dates', []),
                'financial_keywords': analysis.get('financial_keywords', []),
                'key_relationships': analysis.get('relationships', [])[:5],
                'business_context': [],
                'key_points_he': analysis.get('key_points_he', []),
                'compact_analysis': json.dumps(compact, ensure_ascii=False)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(full_analysis, f, indent=2, ensure_ascii=False)
            
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
        """
        analysis_result = self.analyze_text(text, ticker)
        if analysis_result.is_err():
            return analysis_result
        
        save_result = self.save_analysis(analysis_result.data, ticker)
        if save_result.is_err():
            logger.warning(f"⚠️ Analysis succeeded but save failed: {save_result.error}")
        
        return analysis_result
    
    def load_existing_analysis(self, ticker: str) -> Result[Dict[str, Any]]:
        """
        Load existing entity analysis for ticker
        טוען ניתוח ישויות קיים עבור ticker
        """
        try:
            current_date = get_current_date()
            filename = f"{ticker}_entity_analysis_{current_date}.json"
            filepath = os.path.join(self.settings.entity_analyzer_db, filename)
            
            if not os.path.exists(filepath):
                return Result.err(f"No analysis found for {ticker} on {current_date}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            return Result.ok(analysis)
            
        except Exception as e:
            error_msg = f"Failed to load analysis: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return Result.err(error_msg)
