import spacy
import os
from pathlib import Path
from collections import defaultdict, Counter
import json
import sys
from typing import Dict, List, Tuple, Any, Optional
import re
from datetime import datetime
import logging
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class EntityAnalysisConfig:
    """Configuration for entity analysis"""
    model_name: str = "en_core_web_trf"
    min_importance_score: int = 2
    max_important_sentences: int = 10
    max_key_phrases: int = 20
    financial_keywords: Optional[List[str]] = None
    industry_keywords: Optional[Dict[str, List[str]]] = None
    sentiment_threshold: float = 0.01
    
    def __post_init__(self):
        if self.financial_keywords is None:
            self.financial_keywords = [
                'earnings', 'revenue', 'profit', 'loss', 'growth', 'decline', 'stock', 'share', 
                'market', 'trading', 'investment', 'quarter', 'annual', 'fiscal', 'dividend',
                'acquisition', 'merger', 'ipo', 'bankruptcy', 'restructuring', 'layoff',
                'expansion', 'contraction', 'forecast', 'guidance', 'analyst', 'rating'
            ]
        
        if self.industry_keywords is None:
            self.industry_keywords = {
                'tech': ['software', 'hardware', 'ai', 'machine learning', 'cloud', 'cybersecurity', 'mobile', 'app'],
                'finance': ['banking', 'insurance', 'credit', 'loan', 'mortgage', 'investment', 'trading'],
                'healthcare': ['pharmaceutical', 'medical', 'biotech', 'healthcare', 'drug', 'treatment', 'clinical'],
                'energy': ['oil', 'gas', 'renewable', 'solar', 'wind', 'nuclear', 'electricity'],
                'retail': ['e-commerce', 'retail', 'consumer', 'shopping', 'online', 'brick-and-mortar'],
                'automotive': ['car', 'vehicle', 'automotive', 'electric vehicle', 'autonomous', 'tesla'],
                'media': ['entertainment', 'streaming', 'content', 'advertising', 'social media', 'gaming']
            }

class EntityAnalyzer:
    """Entity analyzer for financial articles - integrated with project workflow"""
    
    def __init__(self, config: Optional[EntityAnalysisConfig] = None):
        self.config = config if config is not None else EntityAnalysisConfig()
        self.nlp = self._load_model()
        self.industry_classifier = self._create_industry_classifier()
        
    def _load_model(self):
        """Load spaCy model with error handling"""
        try:
            nlp = spacy.load(self.config.model_name)
            logger.info(f"✅ Loaded spaCy model: {self.config.model_name}")
            return nlp
        except OSError:
            logger.error(f"Error: spaCy model '{self.config.model_name}' not found.")
            logger.info(f"Please install it using: python -m spacy download {self.config.model_name}")
            return None
    
    def _create_industry_classifier(self):
        """Create industry classification patterns"""
        return {
            industry: re.compile(r'\b(' + '|'.join(keywords) + r')\b', re.IGNORECASE)
            for industry, keywords in (self.config.industry_keywords or {}).items()
        }
    
    def analyze_text(self, text: str, ticker: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text and return comprehensive entity analysis"""
        if not self.nlp:
            logger.error("❌ spaCy model not loaded, skipping entity analysis")
            return {}
            
        try:
            doc = self.nlp(text)
            
            # Extract all analysis components
            analysis = {
                'ticker': ticker,
                'entities': self._extract_entities(doc),
                'relationships': self._extract_relationships(doc),
                'key_phrases': self._extract_key_phrases(doc),
                'important_sentences': self._extract_important_sentences(doc),
                'entity_statistics': self._analyze_entity_statistics(doc),
                'financial_analysis': self._extract_financial_analysis(doc),
                'temporal_analysis': self._extract_temporal_analysis(doc),
                'sentiment_analysis': self._analyze_sentiment(doc),
                'industry_analysis': self._classify_industry(doc),
                'market_analysis': self._analyze_market_context(doc),
                'competitor_analysis': self._extract_competitor_info(doc),
                'risk_analysis': self._analyze_risks(doc),
                'opportunity_analysis': self._analyze_opportunities(doc),
                'processing_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'model_used': self.config.model_name,
                    'text_length': len(text)
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error during entity analysis: {e}")
            return {}
    
    def _extract_entities(self, doc) -> List[Dict]:
        """Extract entities with enhanced information"""
        entities = []
        for ent in doc.ents:
            entity_info = {
                'text': ent.text.strip(),
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'sentence': ent.sent.text.strip(),
                'context': self._get_entity_context(ent),
                'is_company': self._is_company_entity(ent),
                'is_person': ent.label_ == 'PERSON',
                'is_location': ent.label_ in ['GPE', 'LOC'],
                'is_financial': ent.label_ in ['MONEY', 'PERCENT']
            }
            entities.append(entity_info)
        return entities
    
    def _get_entity_context(self, ent) -> str:
        """Get context around entity"""
        start = max(0, ent.start_char - 50)
        end = min(len(ent.doc.text), ent.end_char + 50)
        return ent.doc.text[start:end].strip()
    
    def _is_company_entity(self, ent) -> bool:
        """Check if entity is likely a company"""
        company_indicators = ['inc', 'corp', 'ltd', 'llc', 'co', 'company', 'group', 'holdings']
        return (ent.label_ == 'ORG' or 
                any(indicator in ent.text.lower() for indicator in company_indicators))
    
    def _extract_relationships(self, doc) -> List[Dict]:
        """Extract entity relationships with enhanced patterns"""
        relationships = []
        
        # Subject-Verb-Object relationships
        for token in doc:
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                subject = token.text
                verb = token.head.text
                obj = None
                
                for child in token.head.children:
                    if child.dep_ in ["dobj", "pobj"]:
                        obj = child.text
                        break
                
                if obj:
                    relationships.append({
                        'type': 'SVO',
                        'subject': subject,
                        'verb': verb,
                        'object': obj,
                        'sentence': token.sent.text.strip(),
                        'importance': self._calculate_relationship_importance(token.sent)
                    })
        
        # Entity co-occurrences
        for sent in doc.sents:
            entities_in_sent = [token for token in sent if token.ent_type_]
            for i, ent1 in enumerate(entities_in_sent):
                for ent2 in entities_in_sent[i+1:]:
                    relationships.append({
                        'type': 'co-occurrence',
                        'entity1': ent1.text,
                        'entity1_type': ent1.ent_type_,
                        'entity2': ent2.text,
                        'entity2_type': ent2.ent_type_,
                        'sentence': sent.text.strip(),
                        'distance': abs(ent1.i - ent2.i)
                    })
        
        return relationships
    
    def _calculate_relationship_importance(self, sent) -> int:
        """Calculate importance of a sentence based on financial keywords"""
        financial_words = sum(1 for token in sent if token.text.lower() in self.config.financial_keywords)
        entity_count = len([token for token in sent if token.ent_type_])
        return financial_words + entity_count
    
    def _extract_key_phrases(self, doc) -> List[Dict]:
        """Extract key phrases with categorization"""
        key_phrases = []
        
        # Noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                key_phrases.append({
                    'text': chunk.text.strip(),
                    'type': 'noun_chunk',
                    'category': self._categorize_phrase(chunk.text)
                })
        
        # Financial patterns
        patterns = [
            (r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|trillion))?', 'money'),
            (r'\d+(?:\.\d+)?\s*(?:percent|%)', 'percentage'),
            (r'\b(?:Q[1-4]\s+\d{4})\b', 'quarter'),
            (r'\b(?:FY\d{4}|fiscal\s+year)\b', 'fiscal_year'),
            (r'\b(?:earnings|revenue|profit|loss|growth|decline)\b', 'financial_metric'),
            (r'\b(?:stock|share|market|trading|investment)\b', 'market_term')
        ]
        
        for pattern, category in patterns:
            matches = re.finditer(pattern, doc.text, re.IGNORECASE)
            for match in matches:
                key_phrases.append({
                    'text': match.group(),
                    'type': 'pattern',
                    'category': category
                })
        
        return key_phrases
    
    def _categorize_phrase(self, phrase: str) -> str:
        """Categorize a phrase based on content"""
        phrase_lower = phrase.lower()
        
        if any(word in phrase_lower for word in ['earnings', 'revenue', 'profit', 'loss']):
            return 'financial_metric'
        elif any(word in phrase_lower for word in ['stock', 'share', 'market']):
            return 'market_term'
        elif any(word in phrase_lower for word in ['growth', 'decline', 'increase', 'decrease']):
            return 'trend'
        elif any(word in phrase_lower for word in ['quarter', 'year', 'month']):
            return 'temporal'
        else:
            return 'general'
    
    def _extract_important_sentences(self, doc) -> List[Dict]:
        """Extract important sentences with enhanced scoring"""
        important_sentences = []
        
        for sent in doc.sents:
            # Calculate various importance factors
            entity_count = len([token for token in sent if token.ent_type_])
            financial_keyword_count = sum(1 for token in sent if token.text.lower() in self.config.financial_keywords)
            money_count = len([ent for ent in sent.ents if ent.label_ == 'MONEY'])
            company_count = len([ent for ent in sent.ents if ent.label_ == 'ORG'])
            
            # Calculate composite importance score
            importance_score = (
                entity_count * 2 +
                financial_keyword_count * 3 +
                money_count * 5 +
                company_count * 4
            )
            
            if importance_score >= self.config.min_importance_score:
                important_sentences.append({
                    'text': sent.text.strip(),
                    'importance_score': importance_score,
                    'entity_count': entity_count,
                    'financial_keyword_count': financial_keyword_count,
                    'money_count': money_count,
                    'company_count': company_count,
                    'sentiment': self._get_sentence_sentiment(sent)
                })
        
        # Sort by importance and return top sentences
        important_sentences.sort(key=lambda x: x['importance_score'], reverse=True)
        return important_sentences[:self.config.max_important_sentences]
    
    def _get_sentence_sentiment(self, sent) -> str:
        """Get sentiment for a single sentence"""
        positive_words = ['growth', 'profit', 'increase', 'positive', 'strong', 'success', 'gain', 'rise']
        negative_words = ['loss', 'decline', 'decrease', 'negative', 'weak', 'failure', 'drop', 'fall']
        
        pos_count = sum(1 for token in sent if token.text.lower() in positive_words)
        neg_count = sum(1 for token in sent if token.text.lower() in negative_words)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_entity_statistics(self, doc) -> Dict:
        """Analyze entity statistics with enhanced metrics"""
        entities = [ent for ent in doc.ents]
        
        if not entities:
            return {}
        
        # Basic counts
        type_counts = Counter(ent.label_ for ent in entities)
        text_counts = Counter(ent.text for ent in entities)
        
        # Enhanced statistics
        company_entities = [ent for ent in entities if self._is_company_entity(ent)]
        person_entities = [ent for ent in entities if ent.label_ == 'PERSON']
        financial_entities = [ent for ent in entities if ent.label_ in ['MONEY', 'PERCENT']]
        
        return {
            'total_entities': len(entities),
            'unique_entities': len(set(ent.text for ent in entities)),
            'type_counts': dict(type_counts),
            'type_distribution': {label: count/len(entities) for label, count in type_counts.items()},
            'most_common_entities': text_counts.most_common(10),
            'entity_types_found': list(type_counts.keys()),
            'company_entities': len(company_entities),
            'person_entities': len(person_entities),
            'financial_entities': len(financial_entities),
            'entity_density': len(entities) / len([token for token in doc if token.is_alpha])
        }
    
    def _extract_financial_analysis(self, doc) -> Dict:
        """Extract comprehensive financial analysis"""
        financial_data = {
            'money_amounts': [],
            'percentages': [],
            'companies': [],
            'people': [],
            'dates': [],
            'financial_terms': [],
            'financial_metrics': [],
            'market_indicators': []
        }
        
        # Extract by entity type
        for ent in doc.ents:
            if ent.label_ == 'MONEY':
                financial_data['money_amounts'].append(ent.text)
            elif ent.label_ == 'PERCENT':
                financial_data['percentages'].append(ent.text)
            elif ent.label_ == 'ORG':
                financial_data['companies'].append(ent.text)
            elif ent.label_ == 'PERSON':
                financial_data['people'].append(ent.text)
            elif ent.label_ == 'DATE':
                financial_data['dates'].append(ent.text)
        
        # Extract financial terms and metrics
        financial_terms = re.findall(r'\b(?:earnings|revenue|profit|loss|growth|decline|stock|share|market|trading|investment|quarter|annual|fiscal)\b', doc.text, re.IGNORECASE)
        financial_data['financial_terms'] = list(set(financial_terms))
        
        # Extract market indicators
        market_indicators = re.findall(r'\b(?:bull|bear|rally|crash|volatility|volume|price|target|rating|upgrade|downgrade)\b', doc.text, re.IGNORECASE)
        financial_data['market_indicators'] = list(set(market_indicators))
        
        return financial_data
    
    def _extract_temporal_analysis(self, doc) -> Dict:
        """Extract temporal information and patterns"""
        temporal_data = {
            'dates': [],
            'time_expressions': [],
            'temporal_relationships': [],
            'quarters': [],
            'years': [],
            'time_periods': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                temporal_data['dates'].append(ent.text)
                # Extract quarters and years
                if 'Q' in ent.text:
                    temporal_data['quarters'].append(ent.text)
                if re.search(r'\b(20\d{2}|19\d{2})\b', ent.text):
                    temporal_data['years'].append(ent.text)
            elif ent.label_ == 'TIME':
                temporal_data['time_expressions'].append(ent.text)
        
        # Find temporal patterns
        temporal_patterns = re.findall(r'\b(?:yesterday|today|tomorrow|last|next|previous|upcoming|recent|future|past|annual|quarterly|monthly)\b', doc.text, re.IGNORECASE)
        temporal_data['temporal_relationships'] = list(set(temporal_patterns))
        
        return temporal_data
    
    def _analyze_sentiment(self, doc) -> Dict:
        """Enhanced sentiment analysis"""
        positive_words = ['growth', 'profit', 'increase', 'positive', 'strong', 'success', 'gain', 'rise', 'up', 'good', 'excellent', 'bullish', 'rally']
        negative_words = ['loss', 'decline', 'decrease', 'negative', 'weak', 'failure', 'drop', 'down', 'bad', 'poor', 'fall', 'bearish', 'crash']
        
        positive_count = sum(1 for token in doc if token.text.lower() in positive_words)
        negative_count = sum(1 for token in doc if token.text.lower() in negative_words)
        
        total_words = len([token for token in doc if token.is_alpha])
        
        if total_words > 0:
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
            sentiment_score = positive_ratio - negative_ratio
        else:
            sentiment_score = 0
        
        # Enhanced sentiment classification
        if sentiment_score > self.config.sentiment_threshold:
            sentiment_label = 'positive'
        elif sentiment_score < -self.config.sentiment_threshold:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'positive_words': positive_count,
            'negative_words': negative_count,
            'positive_ratio': positive_ratio if total_words > 0 else 0,
            'negative_ratio': negative_ratio if total_words > 0 else 0,
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'sentiment_strength': abs(sentiment_score),
            'confidence': min(abs(sentiment_score) * 10, 1.0)  # Confidence based on strength
        }
    
    def _classify_industry(self, doc) -> Dict:
        """Classify the industry based on content"""
        text = doc.text.lower()
        industry_scores = {}
        
        for industry, pattern in self.industry_classifier.items():
            matches = pattern.findall(text)
            industry_scores[industry] = len(matches)
        
        # Find dominant industry
        if industry_scores:
            dominant_industry = max(industry_scores.items(), key=lambda x: x[1])
            return {
                'dominant_industry': dominant_industry[0] if dominant_industry[1] > 0 else 'general',
                'industry_scores': industry_scores,
                'confidence': dominant_industry[1] / max(sum(industry_scores.values()), 1)
            }
        
        return {'dominant_industry': 'general', 'industry_scores': {}, 'confidence': 0}
    
    def _analyze_market_context(self, doc) -> Dict:
        """Analyze market context and trends"""
        text = doc.text.lower()
        
        # Market sentiment indicators
        bullish_indicators = ['bullish', 'rally', 'surge', 'jump', 'soar', 'climb', 'gain']
        bearish_indicators = ['bearish', 'crash', 'plunge', 'drop', 'fall', 'decline', 'loss']
        
        bullish_count = sum(1 for indicator in bullish_indicators if indicator in text)
        bearish_count = sum(1 for indicator in bearish_indicators if indicator in text)
        
        # Market conditions
        market_conditions = {
            'volatility': 'high' if 'volatility' in text or 'volatile' in text else 'normal',
            'volume': 'high' if 'high volume' in text or 'heavy trading' in text else 'normal',
            'trend': 'bullish' if bullish_count > bearish_count else 'bearish' if bearish_count > bullish_count else 'neutral'
        }
        
        return {
            'market_sentiment': 'bullish' if bullish_count > bearish_count else 'bearish' if bearish_count > bullish_count else 'neutral',
            'bullish_indicators': bullish_count,
            'bearish_indicators': bearish_count,
            'market_conditions': market_conditions,
            'trading_activity': 'high' if any(term in text for term in ['heavy trading', 'high volume', 'active trading']) else 'normal'
        }
    
    def _extract_competitor_info(self, doc) -> Dict:
        """Extract competitor information"""
        companies = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        
        # Look for competitive language
        competitive_terms = ['competitor', 'rival', 'competition', 'market share', 'outperform', 'underperform']
        competitive_context = []
        
        for sent in doc.sents:
            if any(term in sent.text.lower() for term in competitive_terms):
                competitive_context.append(sent.text.strip())
        
        return {
            'companies_mentioned': companies,
            'competitive_context': competitive_context,
            'competitor_count': len(companies),
            'has_competitive_language': len(competitive_context) > 0
        }
    
    def _analyze_risks(self, doc) -> Dict:
        """Analyze risk factors mentioned"""
        risk_keywords = ['risk', 'threat', 'danger', 'concern', 'warning', 'caution', 'uncertainty', 'volatility']
        risk_sentences = []
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in risk_keywords):
                risk_sentences.append(sent.text.strip())
        
        return {
            'risk_sentences': risk_sentences,
            'risk_count': len(risk_sentences),
            'risk_level': 'high' if len(risk_sentences) > 3 else 'medium' if len(risk_sentences) > 1 else 'low'
        }
    
    def _analyze_opportunities(self, doc) -> Dict:
        """Analyze opportunity factors mentioned"""
        opportunity_keywords = ['opportunity', 'potential', 'growth', 'expansion', 'innovation', 'breakthrough', 'advantage']
        opportunity_sentences = []
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in opportunity_keywords):
                opportunity_sentences.append(sent.text.strip())
        
        return {
            'opportunity_sentences': opportunity_sentences,
            'opportunity_count': len(opportunity_sentences),
            'opportunity_level': 'high' if len(opportunity_sentences) > 3 else 'medium' if len(opportunity_sentences) > 1 else 'low'
        }

    def generate_entity_context_for_llm(self, analysis: Dict) -> str:
        """Generate context string for LLM with entity information"""
        if not analysis:
            return ""
        
        context_parts = []
        
        # Entity statistics
        stats = analysis.get('entity_statistics', {})
        if stats:
            context_parts.append(f"📊 ENTITY ANALYSIS:")
            context_parts.append(f"• Total entities found: {stats.get('total_entities', 0)}")
            context_parts.append(f"• Companies mentioned: {stats.get('company_entities', 0)}")
            context_parts.append(f"• People mentioned: {stats.get('person_entities', 0)}")
            context_parts.append(f"• Financial entities: {stats.get('financial_entities', 0)}")
        
        # Financial analysis
        financial = analysis.get('financial_analysis', {})
        if financial:
            context_parts.append(f"\n💰 FINANCIAL DATA:")
            if financial.get('money_amounts'):
                context_parts.append(f"• Money amounts: {', '.join(financial['money_amounts'][:3])}")
            if financial.get('percentages'):
                context_parts.append(f"• Percentages: {', '.join(financial['percentages'][:3])}")
            if financial.get('companies'):
                context_parts.append(f"• Companies: {', '.join(financial['companies'][:5])}")
        
        # Industry analysis
        industry = analysis.get('industry_analysis', {})
        if industry:
            context_parts.append(f"\n🏭 INDUSTRY:")
            context_parts.append(f"• Dominant industry: {industry.get('dominant_industry', 'Unknown')}")
            context_parts.append(f"• Confidence: {industry.get('confidence', 0):.2f}")
        
        # Market analysis
        market = analysis.get('market_analysis', {})
        if market:
            context_parts.append(f"\n📈 MARKET CONTEXT:")
            context_parts.append(f"• Market sentiment: {market.get('market_sentiment', 'Unknown')}")
            context_parts.append(f"• Trading activity: {market.get('trading_activity', 'Unknown')}")
        
        # Sentiment analysis
        sentiment = analysis.get('sentiment_analysis', {})
        if sentiment:
            context_parts.append(f"\n😊 SENTIMENT:")
            context_parts.append(f"• Overall sentiment: {sentiment.get('sentiment_label', 'Unknown')}")
            context_parts.append(f"• Sentiment score: {sentiment.get('sentiment_score', 0):.3f}")
        
        # Risk and opportunities
        risks = analysis.get('risk_analysis', {})
        opportunities = analysis.get('opportunity_analysis', {})
        if risks or opportunities:
            context_parts.append(f"\n⚖️ RISK & OPPORTUNITY:")
            context_parts.append(f"• Risk level: {risks.get('risk_level', 'Unknown')} ({risks.get('risk_count', 0)} mentions)")
            context_parts.append(f"• Opportunity level: {opportunities.get('opportunity_level', 'Unknown')} ({opportunities.get('opportunity_count', 0)} mentions)")
        
        # Important entities to preserve
        entities = analysis.get('entities', [])
        if entities:
            # Group entities by type
            companies = [e['text'] for e in entities if e.get('is_company')]
            people = [e['text'] for e in entities if e.get('is_person')]
            money = [e['text'] for e in entities if e.get('is_financial')]
            
            context_parts.append(f"\n🏷️ KEY ENTITIES TO PRESERVE:")
            if companies:
                context_parts.append(f"• Companies: {', '.join(companies[:5])}")
            if people:
                context_parts.append(f"• People: {', '.join(people[:3])}")
            if money:
                context_parts.append(f"• Financial amounts: {', '.join(money[:3])}")
        
        return "\n".join(context_parts)

# Global instance for reuse
_entity_analyzer = None

def get_entity_analyzer() -> EntityAnalyzer:
    """Get or create global entity analyzer instance"""
    global _entity_analyzer
    if _entity_analyzer is None:
        _entity_analyzer = EntityAnalyzer()
    return _entity_analyzer

def analyze_text_for_llm(text: str, ticker: Optional[str] = None) -> str:
    """Analyze text and return context string for LLM"""
    analyzer = get_entity_analyzer()
    analysis = analyzer.analyze_text(text, ticker)
    return analyzer.generate_entity_context_for_llm(analysis)

def save_entity_analysis(analysis: Dict, ticker: str, output_dir: str = "analysis_results"):
    """Save entity analysis to JSON file"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{ticker}_entity_analysis_{current_date}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Entity analysis saved for {ticker} → {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Error saving entity analysis for {ticker}: {e}")
        return None 