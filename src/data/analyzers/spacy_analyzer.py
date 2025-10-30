"""
Advanced spaCy-based entity analyzer
ניתוח ישויות מתקדם מבוסס spaCy
"""
import spacy
import logging
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class SpaCyEntityAnalyzer:
    """
    Advanced entity analyzer using spaCy
    ניתוח ישויות מתקדם באמצעות spaCy
    """
    
    def __init__(self, model_name: str = "en_core_web_trf"):
        """
        Initialize spaCy analyzer
        
        Args:
            model_name: spaCy model name to use
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load spaCy model"""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"✅ Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.error(f"❌ spaCy model '{self.model_name}' not found.")
            logger.info(f"Install it using: python -m spacy download {self.model_name}")
            self.nlp = None
        except Exception as e:
            logger.error(f"❌ Error loading spaCy model: {e}")
            self.nlp = None
    
    def analyze(self, text: str, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive entity analysis
        מבצע ניתוח ישויות מקיף
        
        Args:
            text: Text to analyze
            ticker: Optional ticker symbol for context
        
        Returns:
            Complete analysis dictionary
        """
        if not self.nlp:
            logger.error("❌ spaCy model not loaded")
            return self._empty_analysis()
        
        try:
            doc = self.nlp(text)
            
            analysis = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'entities': self._extract_entities(doc),
                'sentiment_analysis': self._analyze_sentiment(doc, text),
                'financial_data': self._extract_financial_data(text),
                'relationships': self._extract_relationships(doc),
                'important_sentences': self._extract_important_sentences(doc, text, ticker),
                'industry_keywords': self._detect_industry(doc),
                'processing_metadata': {
                    'model_used': self.model_name,
                    'text_length': len(text),
                    'sentence_count': len(list(doc.sents)),
                    'token_count': len(doc)
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")
            return self._empty_analysis()
    
    def _extract_entities(self, doc) -> List[Dict[str, Any]]:
        """Extract all entities with details"""
        entities = []
        seen = set()
        
        for ent in doc.ents:
            entity_text = ent.text.strip()
            if not entity_text or entity_text in seen:
                continue
            seen.add(entity_text)
            
            # Determine if it's a company
            is_company = (
                ent.label_ == 'ORG' or
                (ent.label_ == 'PERSON' and len(ent.text.split()) == 1) or
                any(char.isupper() for char in entity_text[:3])
            )
            
            entities.append({
                'text': entity_text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'is_company': is_company,
                'length': len(entity_text)
            })
        
        return entities
    
    def _analyze_sentiment(self, doc, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using advanced keyword detection
        מנתח סנטימנט באמצעות זיהוי מילות מפתח מתקדם
        """
        text_lower = text.lower()
        
        # Positive indicators
        positive_patterns = [
            r'\b(?:strong|boost|surge|gain|rise|upgrade|positive|bullish|outperform|exceed|beat|growth|success|high|increase|raise|improve|optimistic)\b',
            r'\b(?:price target|raised|upgraded|recommend|buy|outperform|beat expectations)\b'
        ]
        
        # Negative indicators
        negative_patterns = [
            r'\b(?:decline|fall|drop|loss|risk|uncertainty|concern|worry|negative|bearish|downgrade|miss|below|decrease|cut|reduce|pessimistic)\b',
            r'\b(?:court ordered|legal risk|regulatory|fined|penalty|lawsuit)\b'
        ]
        
        positive_count = sum(len(re.findall(pattern, text_lower)) for pattern in positive_patterns)
        negative_count = sum(len(re.findall(pattern, text_lower)) for pattern in negative_patterns)
        
        # Determine overall sentiment
        if positive_count > negative_count * 1.5:
            sentiment_label = 'positive'
        elif negative_count > positive_count * 1.5:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'sentiment_label': sentiment_label,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': 0,
            'confidence': min(abs(positive_count - negative_count) / max(positive_count + negative_count, 1), 1.0)
        }
    
    def _extract_financial_data(self, text: str) -> Dict[str, List[str]]:
        """Extract financial data: money, dates, percentages"""
        # Money amounts
        money_patterns = [
            r'\$[\d.,]+\s*(?:billion|million|trillion|B|M|T|bn|mn|k)?',
            r'\$[\d.,]+',
            r'€[\d.,]+\s*(?:billion|million|trillion|B|M|T|bn|mn)?',
            r'€[\d.,]+',
            r'\d+\.?\d*\s*(?:billion|million|trillion)\s*(?:dollars|USD|€)?'
        ]
        money_amounts = []
        for pattern in money_patterns:
            money_amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Dates
        date_patterns = [
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:\s+\d{4})?',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\b(?:Q[1-4]|quarter)\s+\d{4}',
            r'\bfiscal\s+(?:Q[1-4]|year|quarter)',
            r'\b(?:this|next|last)\s+(?:week|month|quarter|year)'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Percentages
        percentages = re.findall(r'[\d.,]+\s*%', text)
        
        # Financial keywords
        financial_keywords = [
            'revenue', 'earnings', 'profit', 'loss', 'margin', 'ebitda',
            'price target', 'market cap', 'valuation', 'P/E', 'EPS',
            'dividend', 'guidance', 'forecast', 'analyst', 'upgrade', 'downgrade'
        ]
        found_keywords = [kw for kw in financial_keywords if kw.lower() in text.lower()]
        
        return {
            'money_amounts': sorted(list(set(money_amounts)), key=len, reverse=True),
            'important_dates': sorted(list(set(dates))),
            'percentages': sorted(list(set(percentages))),
            'financial_keywords': found_keywords
        }
    
    def _extract_relationships(self, doc) -> List[Dict[str, Any]]:
        """Extract subject-verb-object relationships"""
        relationships = []
        
        for sent in doc.sents:
            # Simple SVO extraction
            subjects = [token for token in sent if token.dep_ == 'nsubj']
            verbs = [token for token in sent if token.pos_ == 'VERB']
            objects = [token for token in sent if token.dep_ == 'dobj']
            
            if subjects and verbs:
                rel = {
                    'subject': subjects[0].text,
                    'verb': verbs[0].text,
                    'object': objects[0].text if objects else '',
                    'sentence': sent.text[:200],
                    'importance': len(sent.text)  # Simple importance metric
                }
                relationships.append(rel)
        
        # Sort by importance
        relationships.sort(key=lambda x: x['importance'], reverse=True)
        return relationships[:10]  # Top 10
    
    def _extract_important_sentences(
        self, 
        doc, 
        text: str, 
        ticker: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract and score important sentences"""
        sentences = []
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if len(sent_text) < 20:  # Skip very short sentences
                continue
            
            score = 0
            
            # Tick mentions
            if ticker and ticker.upper() in sent_text.upper():
                score += 50
            
            # Money mentions
            if re.search(r'[\$€]\d+', sent_text):
                score += 30
            
            # Numbers
            if re.search(r'\d+', sent_text):
                score += 10
            
            # Financial keywords
            financial_terms = ['revenue', 'earnings', 'analyst', 'upgrade', 'price target']
            score += sum(10 for term in financial_terms if term in sent_text.lower())
            
            # Length factor
            if 50 <= len(sent_text) <= 300:
                score += 20
            
            sentences.append({
                'text': sent_text[:500],  # Limit length
                'importance_score': score,
                'sentiment': 'neutral'  # Will be enhanced later
            })
        
        # Sort by importance
        sentences.sort(key=lambda x: x['importance_score'], reverse=True)
        return sentences
    
    def _detect_industry(self, doc) -> str:
        """Detect industry from text"""
        industry_keywords = {
            'tech': ['technology', 'software', 'hardware', 'device', 'app', 'cloud', 'digital'],
            'finance': ['bank', 'financial', 'investment', 'trading', 'market', 'stock'],
            'healthcare': ['pharmaceutical', 'medical', 'health', 'drug', 'treatment'],
            'energy': ['oil', 'gas', 'energy', 'petroleum', 'electric', 'power'],
            'consumer': ['retail', 'consumer', 'product', 'brand', 'store']
        }
        
        text_lower = ' '.join([token.text.lower() for token in doc])
        
        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        
        return 'unknown'
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'ticker': None,
            'timestamp': datetime.now().isoformat(),
            'entities': [],
            'sentiment_analysis': {
                'sentiment_label': 'neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'confidence': 0.0
            },
            'financial_data': {
                'money_amounts': [],
                'important_dates': [],
                'percentages': [],
                'financial_keywords': []
            },
            'relationships': [],
            'important_sentences': [],
            'industry_keywords': 'unknown',
            'processing_metadata': {
                'model_used': self.model_name,
                'text_length': 0,
                'sentence_count': 0,
                'token_count': 0
            }
        }


# Global instance
_spacy_analyzer: Optional[SpaCyEntityAnalyzer] = None


def get_spacy_analyzer(model_name: str = "en_core_web_trf") -> SpaCyEntityAnalyzer:
    """
    Get global spaCy analyzer instance (singleton)
    מקבל instance גלובלי של analyzer (singleton)
    
    Args:
        model_name: spaCy model name
    
    Returns:
        SpaCyEntityAnalyzer instance
    """
    global _spacy_analyzer
    if _spacy_analyzer is None:
        _spacy_analyzer = SpaCyEntityAnalyzer(model_name)
    return _spacy_analyzer


