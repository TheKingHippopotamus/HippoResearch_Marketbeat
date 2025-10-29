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
import requests

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
                # Basic financial metrics
                'earnings', 'revenue', 'profit', 'loss', 'income', 'expense', 'margin', 'ebitda', 'ebit',
                'growth', 'decline', 'increase', 'decrease', 'performance', 'results', 'quarterly', 'annual',
                
                # Market and trading terms
                'stock', 'share', 'market', 'trading', 'investment', 'portfolio', 'position', 'long', 'short',
                'options', 'futures', 'derivatives', 'volume', 'liquidity', 'volatility', 'momentum', 'trend',
                'bull', 'bear', 'rally', 'crash', 'correction', 'bubble', 'rally', 'downturn', 'uptick', 'downtick',
                
                # Corporate actions
                'acquisition', 'merger', 'ipo', 'secondary', 'buyback', 'split', 'reverse split', 'dividend',
                'bankruptcy', 'restructuring', 'layoff', 'hiring', 'expansion', 'contraction', 'consolidation',
                'spin-off', 'divestiture', 'joint venture', 'partnership', 'alliance',
                
                # Financial planning and guidance
                'forecast', 'guidance', 'outlook', 'projection', 'estimate', 'target', 'expectation', 'prediction',
                'budget', 'planning', 'strategy', 'initiative', 'roadmap', 'milestone',
                
                # Analyst and ratings
                'analyst', 'rating', 'upgrade', 'downgrade', 'initiate', 'maintain', 'price target', 'recommendation',
                'buy', 'sell', 'hold', 'outperform', 'underperform', 'market perform', 'sector perform',
                
                # Risk and compliance
                'risk', 'compliance', 'regulation', 'regulatory', 'audit', 'investigation', 'lawsuit', 'litigation',
                'settlement', 'fine', 'penalty', 'violation', 'breach', 'security', 'cybersecurity',
                
                # Technology and innovation
                'innovation', 'technology', 'digital', 'automation', 'ai', 'machine learning', 'blockchain',
                'cloud', 'saas', 'platform', 'software', 'hardware', 'infrastructure', 'data', 'analytics',
                
                # Market sectors and industries
                'sector', 'industry', 'vertical', 'horizontal', 'niche', 'market share', 'competition', 'competitive',
                'monopoly', 'oligopoly', 'barrier to entry', 'moat', 'competitive advantage',
                
                # Economic indicators
                'inflation', 'deflation', 'interest rate', 'fed', 'central bank', 'monetary policy', 'fiscal policy',
                'gdp', 'unemployment', 'consumer confidence', 'pmi', 'manufacturing', 'services',
                
                # Currency and international
                'currency', 'forex', 'exchange rate', 'international', 'global', 'domestic', 'export', 'import',
                'tariff', 'trade war', 'sanctions', 'embargo', 'geopolitical', 'political',
                
                # Debt and financing
                'debt', 'credit', 'loan', 'bond', 'yield', 'interest', 'leverage', 'liquidity', 'solvency',
                'refinancing', 'restructuring', 'default', 'credit rating', 'moody', 's&p', 'fitch',
                
                # Real estate and assets
                'real estate', 'property', 'asset', 'valuation', 'appraisal', 'depreciation', 'amortization',
                'capital expenditure', 'capex', 'opex', 'operating expense', 'maintenance',
                
                # Supply chain and operations
                'supply chain', 'logistics', 'inventory', 'warehouse', 'distribution', 'manufacturing', 'production',
                'capacity', 'utilization', 'efficiency', 'productivity', 'optimization', 'streamlining',
                
                # Customer and sales
                'customer', 'client', 'sales', 'revenue', 'subscription', 'recurring', 'churn', 'retention',
                'acquisition cost', 'lifetime value', 'conversion', 'pipeline', 'funnel', 'lead',
                
                # Environmental and social
                'esg', 'environmental', 'social', 'governance', 'sustainability', 'carbon', 'renewable', 'green',
                'diversity', 'inclusion', 'corporate responsibility', 'philanthropy', 'charity'
            ]
        
        if self.industry_keywords is None:
            self.industry_keywords = {
                # Technology
                'tech': ['software', 'hardware', 'ai', 'machine learning', 'cloud', 'cybersecurity', 'mobile', 'app', 
                        'blockchain', 'crypto', 'web3', 'metaverse', 'vr', 'ar', 'iot', '5g', 'semiconductor', 'chip'],
                
                # Financial Services
                'finance': ['banking', 'insurance', 'credit', 'loan', 'mortgage', 'investment', 'trading', 'fintech',
                           'payment', 'digital wallet', 'cryptocurrency', 'defi', 'nft', 'robo-advisor', 'wealth management'],
                
                # Healthcare & Biotech
                'healthcare': ['pharmaceutical', 'medical', 'biotech', 'healthcare', 'drug', 'treatment', 'clinical',
                              'vaccine', 'gene therapy', 'immunotherapy', 'telemedicine', 'digital health', 'medtech',
                              'diagnostic', 'therapeutic', 'oncology', 'cardiology', 'neurology'],
                
                # Energy & Utilities
                'energy': ['oil', 'gas', 'renewable', 'solar', 'wind', 'nuclear', 'electricity', 'utilities',
                          'clean energy', 'battery', 'hydrogen', 'carbon capture', 'energy storage', 'grid'],
                
                # Retail & Consumer
                'retail': ['e-commerce', 'retail', 'consumer', 'shopping', 'online', 'brick-and-mortar', 'fashion',
                          'luxury', 'fast fashion', 'department store', 'supermarket', 'convenience store'],
                
                # Automotive & Transportation
                'automotive': ['car', 'vehicle', 'automotive', 'electric vehicle', 'autonomous', 'tesla', 'ev',
                              'hybrid', 'fuel cell', 'charging station', 'ride sharing', 'logistics', 'delivery'],
                
                # Media & Entertainment
                'media': ['entertainment', 'streaming', 'content', 'advertising', 'social media', 'gaming',
                         'esports', 'podcast', 'news', 'publishing', 'music', 'film', 'tv', 'broadcasting'],
                
                # Industrial & Manufacturing
                'industrial': ['manufacturing', 'industrial', 'aerospace', 'defense', 'construction', 'materials',
                              'steel', 'aluminum', 'chemicals', 'machinery', 'equipment', 'automation', 'robotics'],
                
                # Real Estate
                'real_estate': ['real estate', 'property', 'commercial', 'residential', 'office', 'retail space',
                               'warehouse', 'hotel', 'hospitality', 'reit', 'development', 'construction'],
                
                # Telecommunications
                'telecom': ['telecommunications', 'wireless', 'broadband', 'fiber', 'satellite', 'internet service',
                           'mobile network', '5g', '6g', 'network infrastructure', 'data center'],
                
                # Food & Beverage
                'food_beverage': ['food', 'beverage', 'restaurant', 'fast food', 'casual dining', 'alcohol', 'wine',
                                 'beer', 'spirits', 'agriculture', 'farming', 'organic', 'plant-based'],
                
                # Travel & Tourism
                'travel': ['travel', 'tourism', 'airline', 'hotel', 'cruise', 'vacation', 'booking', 'airbnb',
                          'expedia', 'booking.com', 'leisure', 'business travel'],
                
                # Education & Training
                'education': ['education', 'edtech', 'online learning', 'university', 'college', 'school',
                             'training', 'certification', 'skill development', 'lms', 'mooc'],
                
                # Legal & Professional Services
                'professional': ['legal', 'law', 'consulting', 'accounting', 'audit', 'professional services',
                                'advisory', 'management consulting', 'strategy', 'hr', 'recruitment'],
                
                # Mining & Materials
                'mining': ['mining', 'gold', 'silver', 'copper', 'lithium', 'rare earth', 'metals', 'minerals',
                          'extraction', 'exploration', 'commodities', 'natural resources'],
                
                # Aerospace & Defense
                'aerospace': ['aerospace', 'defense', 'military', 'satellite', 'space', 'rocket', 'aircraft',
                             'drone', 'missile', 'weapons', 'government contract', 'defense contractor'],
                
                # Environmental & Clean Tech
                'environmental': ['environmental', 'clean tech', 'waste management', 'recycling', 'water treatment',
                                 'air quality', 'pollution control', 'sustainability', 'carbon reduction'],
                
                # Cannabis & Alternative Medicine
                'cannabis': ['cannabis', 'marijuana', 'cbd', 'thc', 'hemp', 'medical cannabis', 'recreational',
                            'dispensary', 'cultivation', 'extraction', 'edibles', 'vaping']
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
        """
        Generate entity context for LLM with feedback integration
        """
        # Load feedback rules for enhanced context
        try:
            from .feedback_processor import get_feedback_processor
            processor = get_feedback_processor()
            feedback_summary = processor.generate_rule_summary()
        except Exception as e:
            feedback_summary = "# No feedback rules available\n"
        """Generate enhanced context string for LLM with detailed spaCy analysis"""
        if not analysis:
            return ""
        
        context_parts = []
        
        # Enhanced entity statistics with spaCy insights
        stats = analysis.get('entity_statistics', {})
        if stats:
            context_parts.append(f"📊 SPAÇY ENTITY ANALYSIS:")
            context_parts.append(f"• Total entities found: {stats.get('total_entities', 0)}")
            context_parts.append(f"• Companies (ORG): {stats.get('company_entities', 0)}")
            context_parts.append(f"• People (PERSON): {stats.get('person_entities', 0)}")
            context_parts.append(f"• Financial amounts (MONEY): {stats.get('financial_entities', 0)}")
            context_parts.append(f"• Locations (GPE/LOC): {stats.get('location_entities', 0)}")
            context_parts.append(f"• Dates (DATE): {stats.get('date_entities', 0)}")
            context_parts.append(f"• Percentages (PERCENT): {stats.get('percent_entities', 0)}")
        
        # Detailed entity relationships from spaCy
        relationships = analysis.get('relationships', [])
        if relationships:
            context_parts.append(f"\n🔗 SPAÇY RELATIONSHIPS:")
            # Group by relationship type
            svo_relations = [r for r in relationships if r.get('type') == 'SVO']
            co_occurrences = [r for r in relationships if r.get('type') == 'co-occurrence']
            
            if svo_relations:
                context_parts.append(f"• Subject-Verb-Object patterns: {len(svo_relations)}")
                # Show top 3 most important relationships
                important_svo = sorted(svo_relations, key=lambda x: x.get('importance', 0), reverse=True)[:3]
                for rel in important_svo:
                    context_parts.append(f"  - {rel.get('subject', '')} → {rel.get('verb', '')} → {rel.get('object', '')}")
            
            if co_occurrences:
                context_parts.append(f"• Entity co-occurrences: {len(co_occurrences)}")
                # Show important co-occurrences
                important_co = sorted(co_occurrences, key=lambda x: x.get('distance', 0))[:3]
                for rel in important_co:
                    context_parts.append(f"  - {rel.get('entity1', '')} ({rel.get('entity1_type', '')}) ↔ {rel.get('entity2', '')} ({rel.get('entity2_type', '')})")
        
        # Key phrases extracted by spaCy
        key_phrases = analysis.get('key_phrases', [])
        if key_phrases:
            context_parts.append(f"\n🔑 SPAÇY KEY PHRASES:")
            # Group by category
            categories = {}
            for phrase in key_phrases:
                cat = phrase.get('category', 'general')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(phrase.get('text', ''))
            
            for cat, phrases in categories.items():
                if phrases:
                    context_parts.append(f"• {cat.replace('_', ' ').title()}: {', '.join(phrases[:5])}")
        
        # Important sentences with spaCy scoring
        important_sentences = analysis.get('important_sentences', [])
        if important_sentences:
            context_parts.append(f"\n📝 SPAÇY IMPORTANT SENTENCES:")
            context_parts.append(f"• Top {len(important_sentences)} sentences by spaCy importance scoring")
            for i, sent in enumerate(important_sentences[:3], 1):
                score = sent.get('importance_score', 0)
                entities = sent.get('entity_count', 0)
                financial = sent.get('financial_keyword_count', 0)
                context_parts.append(f"  {i}. Score: {score} (entities: {entities}, financial: {financial})")
                context_parts.append(f"     \"{sent.get('text', '')[:100]}...\"")
        
        # Financial analysis with spaCy insights
        financial = analysis.get('financial_analysis', {})
        if financial:
            context_parts.append(f"\n💰 SPAÇY FINANCIAL DATA:")
            if financial.get('money_amounts'):
                context_parts.append(f"• Money amounts (spaCy MONEY entities): {', '.join(financial['money_amounts'][:5])}")
            if financial.get('percentages'):
                context_parts.append(f"• Percentages (spaCy PERCENT entities): {', '.join(financial['percentages'][:5])}")
            if financial.get('companies'):
                unique_companies = list(dict.fromkeys(financial['companies'][:8]))
                context_parts.append(f"• Companies (spaCy ORG entities): {', '.join(unique_companies)}")
            if financial.get('people'):
                context_parts.append(f"• People (spaCy PERSON entities): {', '.join(financial['people'][:3])}")
        
        # Industry analysis with spaCy keyword matching
        industry = analysis.get('industry_analysis', {})
        if industry:
            context_parts.append(f"\n🏭 SPAÇY INDUSTRY CLASSIFICATION:")
            context_parts.append(f"• Dominant industry: {industry.get('dominant_industry', 'Unknown')}")
            context_parts.append(f"• Confidence: {industry.get('confidence', 0):.2f}")
            if industry.get('industry_keywords_found'):
                context_parts.append(f"• Industry keywords found: {', '.join(industry['industry_keywords_found'][:5])}")
        
        # Market analysis with spaCy patterns
        market = analysis.get('market_analysis', {})
        if market:
            context_parts.append(f"\n📈 SPAÇY MARKET CONTEXT:")
            context_parts.append(f"• Market sentiment: {market.get('market_sentiment', 'Unknown')}")
            context_parts.append(f"• Trading activity: {market.get('trading_activity', 'Unknown')}")
            if market.get('market_conditions'):
                conditions = market['market_conditions']
                context_parts.append(f"• Market conditions: {conditions.get('trend', 'Unknown')}")
                if conditions.get('volatility_indicators'):
                    context_parts.append(f"• Volatility indicators: {', '.join(conditions['volatility_indicators'][:3])}")
        
        # Enhanced sentiment analysis with spaCy
        sentiment = analysis.get('sentiment_analysis', {})
        if sentiment:
            context_parts.append(f"\n😊 SPAÇY SENTIMENT ANALYSIS:")
            context_parts.append(f"• Overall sentiment: {sentiment.get('sentiment_label', 'Unknown')}")
            context_parts.append(f"• Sentiment score: {sentiment.get('sentiment_score', 0):.3f}")
            context_parts.append(f"• Positive ratio: {sentiment.get('positive_ratio', 0):.3f}")
            context_parts.append(f"• Negative ratio: {sentiment.get('negative_ratio', 0):.3f}")
            if sentiment.get('sentiment_keywords'):
                context_parts.append(f"• Sentiment keywords: {', '.join(sentiment['sentiment_keywords'][:5])}")
        
        # Risk and opportunities with spaCy patterns
        risks = analysis.get('risk_analysis', {})
        opportunities = analysis.get('opportunity_analysis', {})
        if risks or opportunities:
            context_parts.append(f"\n⚖️ SPAÇY RISK & OPPORTUNITY:")
            context_parts.append(f"• Risk level: {risks.get('risk_level', 'Unknown')} ({risks.get('risk_count', 0)} mentions)")
            context_parts.append(f"• Opportunity level: {opportunities.get('opportunity_level', 'Unknown')} ({opportunities.get('opportunity_count', 0)} mentions)")
            
            if risks.get('risk_sentences'):
                context_parts.append(f"• Key risk sentence: \"{risks['risk_sentences'][0][:100]}...\"")
            if opportunities.get('opportunity_sentences'):
                context_parts.append(f"• Key opportunity sentence: \"{opportunities['opportunity_sentences'][0][:100]}...\"")
        
        # Competitor analysis with spaCy entity relationships
        competitor = analysis.get('competitor_analysis', {})
        if competitor:
            context_parts.append(f"\n🏆 SPAÇY COMPETITION ANALYSIS:")
            context_parts.append(f"• Companies mentioned: {competitor.get('competitor_count', 0)}")
            context_parts.append(f"• Has competitive language: {competitor.get('has_competitive_language', False)}")
            if competitor.get('competitive_relationships'):
                context_parts.append(f"• Competitive relationships: {len(competitor['competitive_relationships'])} found")
        
        # Temporal analysis with spaCy DATE entities
        temporal = analysis.get('temporal_analysis', {})
        if temporal:
            context_parts.append(f"\n📅 SPAÇY TEMPORAL ANALYSIS:")
            if temporal.get('dates'):
                context_parts.append(f"• Dates mentioned: {', '.join(temporal['dates'][:3])}")
            if temporal.get('time_periods'):
                context_parts.append(f"• Time periods: {', '.join(temporal['time_periods'][:3])}")
            if temporal.get('temporal_indicators'):
                context_parts.append(f"• Temporal indicators: {', '.join(temporal['temporal_indicators'][:3])}")
        
        # Critical entities to preserve (from spaCy entities)
        entities = analysis.get('entities', [])
        if entities:
            # Group entities by spaCy label and remove duplicates
            companies = list(dict.fromkeys([e['text'] for e in entities if e.get('label') == 'ORG']))
            people = list(dict.fromkeys([e['text'] for e in entities if e.get('label') == 'PERSON']))
            money = list(dict.fromkeys([e['text'] for e in entities if e.get('label') == 'MONEY']))
            locations = list(dict.fromkeys([e['text'] for e in entities if e.get('label') in ['GPE', 'LOC']]))
            dates = list(dict.fromkeys([e['text'] for e in entities if e.get('label') == 'DATE']))
            percentages = list(dict.fromkeys([e['text'] for e in entities if e.get('label') == 'PERCENT']))
            
            context_parts.append(f"\n🏷️ SPAÇY ENTITIES TO PRESERVE:")
            if companies:
                context_parts.append(f"• Companies (ORG): {', '.join(companies[:8])}")
            if people:
                context_parts.append(f"• People (PERSON): {', '.join(people[:3])}")
            if money:
                context_parts.append(f"• Money amounts (MONEY): {', '.join(money[:3])}")
            if locations:
                context_parts.append(f"• Locations (GPE/LOC): {', '.join(locations[:3])}")
            if dates:
                context_parts.append(f"• Dates (DATE): {', '.join(dates[:3])}")
            if percentages:
                context_parts.append(f"• Percentages (PERCENT): {', '.join(percentages[:3])}")
        
        # Add spaCy processing metadata
        metadata = analysis.get('processing_metadata', {})
        if metadata:
            context_parts.append(f"\n🔧 SPAÇY PROCESSING INFO:")
            context_parts.append(f"• Model used: {metadata.get('model_used', 'Unknown')}")
            context_parts.append(f"• Text length: {metadata.get('text_length', 0)} characters")
            context_parts.append(f"• Processing timestamp: {metadata.get('timestamp', 'Unknown')}")
        
        return "\n".join(context_parts)

    def generate_compact_entity_context_for_llm(self, analysis: Dict) -> str:
        """
        Generate compact entity context for LLM (max 1000 chars) with only essential information
        """
        if not analysis:
            return ""
        
        context_parts = []
        
        # Check if this is the new compact format
        if 'companies' in analysis and 'sentiment' in analysis:
            # New compact format
            if analysis.get('companies'):
                context_parts.append(f"🏢 Companies: {', '.join(analysis['companies'][:3])}")
            if analysis.get('people'):
                context_parts.append(f"👥 People: {', '.join(analysis['people'][:2])}")
            
            # Enhanced sentiment
            sentiment = analysis.get('sentiment', {})
            if isinstance(sentiment, dict):
                overall = sentiment.get('overall', 'neutral')
                pos_count = sentiment.get('positive_count', 0)
                neg_count = sentiment.get('negative_count', 0)
                context_parts.append(f"📊 Sentiment: {overall} (pos:{pos_count}, neg:{neg_count})")
            else:
                context_parts.append(f"📊 Sentiment: {sentiment}")
            
            if analysis.get('industry'):
                context_parts.append(f"🏭 Industry: {analysis['industry']}")
            
            # Important dates
            if analysis.get('important_dates'):
                context_parts.append(f"📅 Key dates: {', '.join(analysis['important_dates'][:3])}")
            
            # Financial keywords
            if analysis.get('financial_keywords'):
                context_parts.append(f"💰 Financial terms: {', '.join(analysis['financial_keywords'][:5])}")
            
            # Key relationships
            if analysis.get('key_relationships'):
                context_parts.append("🔗 Key relationships:")
                for rel in analysis['key_relationships'][:2]:
                    context_parts.append(f"  - {rel.get('subject', '')} → {rel.get('verb', '')} → {rel.get('object', '')}")
            
            # Business context
            if analysis.get('business_context'):
                context_parts.append("💼 Business context:")
                for ctx in analysis['business_context'][:2]:
                    context_parts.append(f"  - {ctx.get('text', '')[:60]}...")
            
            if analysis.get('money_amounts'):
                context_parts.append(f"💰 Key amounts: {', '.join(analysis['money_amounts'][:3])}")
            
            if analysis.get('key_points'):
                context_parts.append("📝 Key points:")
                for i, point in enumerate(analysis['key_points'][:3], 1):
                    text = point.get('text', '')[:100]
                    sentiment = point.get('sentiment', 'neutral')
                    if text:
                        context_parts.append(f"  {i}. [{sentiment}] {text}...")
        else:
            # Old full format - extract essential info
            # Key entities (top 5 most important)
            entities = analysis.get('entities', [])
            if entities:
                # Get unique company names and key entities
                companies = []
                people = []
                for ent in entities:
                    if ent.get('is_company') and ent.get('text') not in companies:
                        companies.append(ent.get('text'))
                    elif ent.get('label') == 'PERSON' and ent.get('text') not in people:
                        people.append(ent.get('text'))
                
                if companies:
                    context_parts.append(f"🏢 Companies: {', '.join(companies[:3])}")
                if people:
                    context_parts.append(f"👥 People: {', '.join(people[:2])}")
            
            # Sentiment summary
            sentiment = analysis.get('sentiment_analysis', {})
            if sentiment:
                overall = sentiment.get('sentiment_label', 'neutral')
                context_parts.append(f"📊 Sentiment: {overall}")
            
            # Industry classification
            industry = analysis.get('industry_analysis', {})
            if industry:
                dominant = industry.get('dominant_industry', 'Unknown')
                context_parts.append(f"🏭 Industry: {dominant}")
            
            # Key financial data (if any)
            financial = analysis.get('financial_analysis', {})
            if financial:
                money = financial.get('money_amounts', [])
                if money:
                    context_parts.append(f"💰 Key amounts: {', '.join(money[:2])}")
            
            # Important sentences (top 2)
            important_sentences = analysis.get('important_sentences', [])
            if important_sentences:
                context_parts.append("📝 Key points:")
                for i, sent in enumerate(important_sentences[:2], 1):
                    text = sent.get('text', '')[:80]
                    if text:
                        context_parts.append(f"  {i}. {text}...")
        
        result = "\n".join(context_parts)
        
        # Ensure we don't exceed 1000 characters
        if len(result) > 1000:
            result = result[:997] + "..."
        
        return result

def mark_entities(text, entities):
    for ent in sorted(entities, key=len, reverse=True):
        text = re.sub(rf'\b{re.escape(ent)}\b', f'[[{ent}]]', text)
    return text

def restore_marked_entities(text, entities):
    for ent in sorted(entities, key=len, reverse=True):
        text = re.sub(rf'\[\[.*?{re.escape(ent)}.*?\]\]', ent, text)
    return text

def translate_key_points_to_hebrew(key_points, entities):
    """תרגם key points לעברית מקצועית עם שמירה על ישויות באנגלית"""
    key_points_he = []
    entity_list = ', '.join(sorted(set(entities)))
    for kp in key_points:
        text = kp.get('text', '')
        marked = mark_entities(text, entities)
        prompt = f"""
תרגם את המשפט הבא לעברית מקצועית, שמור על שמות חברות, סימולים, תרופות, אנשים ומונחים מקצועיים באנגלית (למשל: {entity_list}). אל תתרגם מונחים מקצועיים. שמור על הקשר תחבירי נכון (עבר/הווה/עתיד, יחיד/רבים, שם עצם/פועל). אם יש מילה בסוגריים מרובעים [[...]], אל תיגע בה.

משפט: {marked}
"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "aya-expanse:8b",
                    "prompt": prompt,
                    "options": {"num_predict": 256, "temperature": 0.4, "top_p": 0.9},
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            heb = response.json()["response"] if "response" in response.json() else response.text
            heb = restore_marked_entities(heb, entities)
            key_points_he.append(heb.strip())
        except Exception as e:
            key_points_he.append(f"[שגיאה בתרגום: {e}]")
    return key_points_he

def generate_model_guidance_from_spacy(analysis: Dict) -> str:
    """Generate specific guidance for the model based on spaCy analysis"""
    if not analysis:
        return ""
    
    guidance_parts = []
    
    # Get key insights from spaCy analysis
    entities = analysis.get('entities', [])
    relationships = analysis.get('relationships', [])
    important_sentences = analysis.get('important_sentences', [])
    financial = analysis.get('financial_analysis', {})
    sentiment = analysis.get('sentiment_analysis', {})
    
    guidance_parts.append("🤖 MODEL GUIDANCE FROM SPAÇY ANALYSIS:")
    
    # Entity preservation guidance
    if entities:
        guidance_parts.append("\n📋 ENTITY PRESERVATION GUIDANCE:")
        companies = [e['text'] for e in entities if e.get('label') == 'ORG']
        people = [e['text'] for e in entities if e.get('label') == 'PERSON']
        money = [e['text'] for e in entities if e.get('label') == 'MONEY']
        
        if companies:
            guidance_parts.append(f"• CRITICAL: Preserve these company names exactly: {', '.join(companies[:5])}")
            guidance_parts.append("• DO NOT translate company names to Hebrew - keep them in English")
        
        if people:
            guidance_parts.append(f"• Preserve these person names: {', '.join(people[:3])}")
        
        if money:
            guidance_parts.append(f"• Preserve these financial amounts exactly: {', '.join(money[:3])}")
    
    # Relationship guidance
    if relationships:
        guidance_parts.append("\n🔗 RELATIONSHIP GUIDANCE:")
        svo_relations = [r for r in relationships if r.get('type') == 'SVO']
        if svo_relations:
            guidance_parts.append(f"• Found {len(svo_relations)} subject-verb-object relationships")
            guidance_parts.append("• Use these relationships to understand the narrative structure")
            guidance_parts.append("• Maintain the logical flow between entities in your writing")
    
    # Sentence importance guidance
    if important_sentences:
        guidance_parts.append("\n📝 SENTENCE IMPORTANCE GUIDANCE:")
        top_sentences = important_sentences[:3]
        guidance_parts.append(f"• spaCy identified {len(important_sentences)} highly important sentences")
        guidance_parts.append("• These sentences contain key financial information and entities")
        guidance_parts.append("• Ensure these key points are prominently featured in your article")
        
        for i, sent in enumerate(top_sentences, 1):
            score = sent.get('importance_score', 0)
            guidance_parts.append(f"• Sentence {i} (score: {score}): \"{sent.get('text', '')[:80]}...\"")
    
    # Financial context guidance
    if financial:
        guidance_parts.append("\n💰 FINANCIAL CONTEXT GUIDANCE:")
        if financial.get('money_amounts'):
            guidance_parts.append("• Multiple financial amounts detected - ensure accurate reporting")
            guidance_parts.append("• Use these amounts to provide concrete financial context")
        
        if financial.get('percentages'):
            guidance_parts.append("• Percentage changes detected - emphasize trends and growth/decline")
        
        if financial.get('companies'):
            guidance_parts.append("• Multiple companies mentioned - consider competitive dynamics")
    
    # Sentiment guidance
    if sentiment:
        guidance_parts.append("\n😊 SENTIMENT GUIDANCE:")
        sentiment_label = sentiment.get('sentiment_label', 'Unknown')
        sentiment_score = sentiment.get('sentiment_score', 0)
        
        if sentiment_label == 'positive':
            guidance_parts.append("• Overall positive sentiment detected - emphasize opportunities and growth")
        elif sentiment_label == 'negative':
            guidance_parts.append("• Overall negative sentiment detected - address risks and challenges")
        else:
            guidance_parts.append("• Mixed or neutral sentiment - provide balanced analysis")
        
        guidance_parts.append(f"• Sentiment score: {sentiment_score:.3f} - use this to calibrate your tone")
    
    # Writing style guidance based on content
    guidance_parts.append("\n✍️ WRITING STYLE GUIDANCE:")
    
    # Count entity types to guide writing style
    entity_counts = {}
    for entity in entities:
        label = entity.get('label', 'OTHER')
        entity_counts[label] = entity_counts.get(label, 0) + 1
    
    if entity_counts.get('ORG', 0) > 3:
        guidance_parts.append("• Multiple companies involved - focus on industry dynamics and competitive landscape")
    
    if entity_counts.get('MONEY', 0) > 2:
        guidance_parts.append("• Significant financial data present - provide detailed financial analysis")
    
    if entity_counts.get('PERSON', 0) > 1:
        guidance_parts.append("• Key personnel mentioned - consider leadership and management implications")
    
    if entity_counts.get('DATE', 0) > 1:
        guidance_parts.append("• Multiple dates/timelines - structure article chronologically")
    
    # Content structure guidance
    guidance_parts.append("\n📊 CONTENT STRUCTURE GUIDANCE:")
    
    if important_sentences:
        guidance_parts.append("• Lead with the most important sentence identified by spaCy")
        guidance_parts.append("• Use spaCy's importance scoring to prioritize information")
    
    if relationships:
        guidance_parts.append("• Use identified relationships to create logical flow between paragraphs")
    
    if financial.get('money_amounts') or financial.get('percentages'):
        guidance_parts.append("• Include specific financial metrics and their implications")
    
    # Language and tone guidance
    guidance_parts.append("\n🗣️ LANGUAGE GUIDANCE:")
    guidance_parts.append("• Write in professional Hebrew financial style")
    guidance_parts.append("• Use connecting words for smooth transitions")
    guidance_parts.append("• Maintain third-person voice throughout")
    guidance_parts.append("• DO NOT translate company names to Hebrew")
    guidance_parts.append("• Preserve all numerical data exactly as provided")
    
    return "\n".join(guidance_parts)

def generate_spacy_collaboration_instructions() -> str:
    """Generate instructions for the model on how to collaborate with spaCy analysis"""
    return """
🤝 SPAÇY-MODEL COLLABORATION INSTRUCTIONS:

You are working in collaboration with spaCy, a powerful NLP library that has analyzed the text and provided you with detailed insights. Here's how to work together effectively:

📊 UNDERSTANDING SPAÇY'S ROLE:
• spaCy has already analyzed the text and identified entities, relationships, and patterns
• spaCy provides you with structured data about what it found
• Your role is to use this analysis to write a comprehensive, professional article
• You should trust spaCy's entity identification and relationship analysis

🔍 HOW TO USE SPAÇY'S ANALYSIS:
1. **Entity Preservation**: Use the entities spaCy identified (companies, people, money amounts)
2. **Relationship Understanding**: Use spaCy's relationship analysis to understand connections
3. **Importance Scoring**: Prioritize information based on spaCy's importance scores
4. **Sentiment Guidance**: Use spaCy's sentiment analysis to guide your tone
5. **Financial Context**: Use spaCy's financial data extraction for accurate reporting

📝 YOUR RESPONSIBILITIES:
• Write the actual article content in professional Hebrew
• Use spaCy's insights to structure your narrative
• Preserve all entities and data that spaCy identified
• Create flowing, logical connections between ideas
• Maintain professional financial writing style

🎯 COLLABORATION WORKFLOW:
1. Review spaCy's entity analysis and guidance
2. Use spaCy's importance scoring to prioritize information
3. Follow spaCy's relationship patterns in your narrative
4. Preserve all identified entities exactly as spaCy found them
5. Write your article using spaCy's insights as a foundation

⚠️ CRITICAL RULES:
• DO NOT translate company names - spaCy identified them as ORG entities
• Preserve all financial amounts exactly - spaCy identified them as MONEY entities
• Use spaCy's sentiment analysis to guide your tone
• Trust spaCy's entity identification and relationship analysis
• Write in professional Hebrew while using spaCy's English entity data

This is a true collaboration - spaCy provides the analysis, you provide the writing expertise!
"""

# Global instance for reuse
_entity_analyzer = None

def get_entity_analyzer() -> EntityAnalyzer:
    """Get or create global entity analyzer instance"""
    global _entity_analyzer
    if _entity_analyzer is None:
        _entity_analyzer = EntityAnalyzer()
    return _entity_analyzer

def analyze_text_for_llm(text: str, ticker: Optional[str] = None) -> str:
    """Analyze text and return enhanced context string for LLM"""
    analyzer = get_entity_analyzer()
    analysis = analyzer.analyze_text(text, ticker)
    collaboration_instructions = generate_spacy_collaboration_instructions()
    context = analyzer.generate_compact_entity_context_for_llm(analysis)
    guidance = generate_model_guidance_from_spacy(analysis)
    return f"{collaboration_instructions}\n\n{context}\n\n{guidance}"

def save_entity_analysis(analysis: Dict, ticker: str, output_dir: str = "entityAnalyzer_DB"):
    """Save compact entity analysis to JSON file (uses compact version by default)"""
    return save_compact_entity_analysis(analysis, ticker, output_dir)

def load_existing_entity_analysis(ticker: str, output_dir: str = "entityAnalyzer_DB") -> Optional[Dict]:
    """Load existing entity analysis from JSON file"""
    try:
        # Look for the most recent file for this ticker
        import glob
        pattern = os.path.join(output_dir, f"{ticker}_entity_analysis_*.json")
        files = glob.glob(pattern)
        
        if not files:
            logger.warning(f"No existing entity analysis found for {ticker}")
            return None
        
        # Get the most recent file
        latest_file = max(files, key=os.path.getctime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        logger.info(f"✅ Loaded existing entity analysis for {ticker} from {latest_file}")
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Error loading existing entity analysis for {ticker}: {e}")
        return None

def analyze_text_for_llm_with_cache(text: str, ticker: Optional[str] = None, output_dir: str = "entityAnalyzer_DB") -> str:
    """Analyze text and return enhanced context string for LLM, using cached analysis if available"""
    if not ticker:
        # Fall back to real-time analysis if no ticker provided
        logger.info("No ticker provided, performing real-time analysis")
        return analyze_text_for_llm(text, ticker)
    
    # Try to load existing analysis first
    logger.info(f"🔍 Looking for cached entity analysis for {ticker}...")
    existing_analysis = load_existing_entity_analysis(ticker, output_dir)
    
    if existing_analysis:
        # Use existing analysis
        logger.info(f"✅ Using cached entity analysis for {ticker}")
        analyzer = get_entity_analyzer()
        collaboration_instructions = generate_spacy_collaboration_instructions()
        context = analyzer.generate_compact_entity_context_for_llm(existing_analysis)
        guidance = generate_model_guidance_from_spacy(existing_analysis)
        return f"{collaboration_instructions}\n\n{context}\n\n{guidance}"
    else:
        # Fall back to real-time analysis
        logger.info(f"⚠️ No cached analysis found for {ticker}, performing real-time analysis")
        return analyze_text_for_llm(text, ticker) 

def list_available_entity_analyses(output_dir: str = "entityAnalyzer_DB") -> List[str]:
    """List all available entity analysis files"""
    try:
        import glob
        pattern = os.path.join(output_dir, "*_entity_analysis_*.json")
        files = glob.glob(pattern)
        
        # Extract ticker names from filenames
        tickers = []
        for file in files:
            filename = os.path.basename(file)
            # Extract ticker from filename like "DASH_entity_analysis_20250713.json"
            parts = filename.split('_')
            if len(parts) >= 2:
                ticker = parts[0]
                tickers.append(ticker)
        
        # Remove duplicates and sort
        unique_tickers = sorted(list(set(tickers)))
        
        logger.info(f"📁 Found {len(unique_tickers)} unique tickers with entity analysis: {', '.join(unique_tickers)}")
        return unique_tickers
        
    except Exception as e:
        logger.error(f"❌ Error listing entity analyses: {e}")
        return [] 

def has_entity_analysis(ticker: str, output_dir: str = "entityAnalyzer_DB") -> bool:
    """Check if entity analysis exists for a specific ticker"""
    try:
        import glob
        pattern = os.path.join(output_dir, f"{ticker}_entity_analysis_*.json")
        files = glob.glob(pattern)
        return len(files) > 0
    except Exception as e:
        logger.error(f"❌ Error checking entity analysis for {ticker}: {e}")
        return False 

def get_entity_analysis_stats(output_dir: str = "entityAnalyzer_DB") -> Dict[str, Any]:
    """Get statistics about entity analysis files"""
    try:
        import glob
        from datetime import datetime
        
        pattern = os.path.join(output_dir, "*_entity_analysis_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return {"total_files": 0, "unique_tickers": 0, "latest_date": None, "oldest_date": None}
        
        # Extract dates and tickers
        dates = []
        tickers = set()
        
        for file in files:
            filename = os.path.basename(file)
            parts = filename.split('_')
            if len(parts) >= 4:
                ticker = parts[0]
                date_str = parts[3].replace('.json', '')
                tickers.add(ticker)
                try:
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    dates.append(date_obj)
                except ValueError:
                    continue
        
        if dates:
            latest_date = max(dates)
            oldest_date = min(dates)
        else:
            latest_date = None
            oldest_date = None
        
        stats = {
            "total_files": len(files),
            "unique_tickers": len(tickers),
            "latest_date": latest_date.strftime('%Y-%m-%d') if latest_date else None,
            "oldest_date": oldest_date.strftime('%Y-%m-%d') if oldest_date else None,
            "date_range_days": (latest_date - oldest_date).days if latest_date and oldest_date else 0
        }
        
        logger.info(f"📊 Entity Analysis Stats: {stats['total_files']} files, {stats['unique_tickers']} tickers")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting entity analysis stats: {e}")
        return {"error": str(e)} 

def save_compact_entity_analysis(analysis: Dict, ticker: str, output_dir: str = "entityAnalyzer_DB"):
    """Save compact entity analysis with only essential information for LLM processing, including key_points_he"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{ticker}_entity_analysis_{current_date}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Extract only essential information
        compact_analysis = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "companies": [],
            "people": [],
            "sentiment": {
                "overall": "neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            },
            "industry": "Unknown",
            "key_points": [],
            "money_amounts": [],
            "important_dates": [],
            "financial_keywords": [],
            "key_relationships": [],
            "business_context": []
        }
        
        # Extract companies
        entities = analysis.get('entities', [])
        for ent in entities:
            if ent.get('is_company') and ent.get('text') not in compact_analysis['companies']:
                compact_analysis['companies'].append(ent.get('text'))
            elif ent.get('label') == 'PERSON' and ent.get('text') not in compact_analysis['people']:
                compact_analysis['people'].append(ent.get('text'))
            elif ent.get('label') == 'DATE' and ent.get('text') not in compact_analysis['important_dates']:
                compact_analysis['important_dates'].append(ent.get('text'))
        
        # Extract detailed sentiment
        sentiment = analysis.get('sentiment_analysis', {})
        if sentiment:
            compact_analysis['sentiment']['overall'] = sentiment.get('sentiment_label', 'neutral')
            compact_analysis['sentiment']['positive_count'] = sentiment.get('positive_count', 0)
            compact_analysis['sentiment']['negative_count'] = sentiment.get('negative_count', 0)
            compact_analysis['sentiment']['neutral_count'] = sentiment.get('neutral_count', 0)
        
        # Extract industry
        industry = analysis.get('industry_analysis', {})
        if industry:
            compact_analysis['industry'] = industry.get('dominant_industry', 'Unknown')
        
        # Extract key points (top 5 sentences)
        important_sentences = analysis.get('important_sentences', [])
        for sent in important_sentences[:5]:
            compact_analysis['key_points'].append({
                "text": sent.get('text', '')[:300],
                "importance_score": sent.get('importance_score', 0),
                "sentiment": sent.get('sentiment', 'neutral')
            })
        # תרגום key points לעברית מקצועית
        all_entities = compact_analysis['companies'] + compact_analysis['people']
        key_points_he = translate_key_points_to_hebrew(compact_analysis['key_points'], all_entities)
        compact_analysis['key_points_he'] = key_points_he
        
        # Extract money amounts
        financial = analysis.get('financial_analysis', {})
        if financial:
            compact_analysis['money_amounts'] = financial.get('money_amounts', [])[:10]
            compact_analysis['financial_keywords'] = financial.get('financial_keywords_found', [])[:15]
        
        # Extract key relationships (top 5)
        relationships = analysis.get('relationships', [])
        for rel in relationships[:5]:
            if rel.get('type') == 'SVO':
                compact_analysis['key_relationships'].append({
                    "subject": rel.get('subject', ''),
                    "verb": rel.get('verb', ''),
                    "object": rel.get('object', ''),
                    "importance": rel.get('importance', 0)
                })
        
        # Extract business context from key phrases
        key_phrases = analysis.get('key_phrases', [])
        for phrase in key_phrases[:10]:
            if phrase.get('category') in ['financial', 'business', 'market']:
                compact_analysis['business_context'].append({
                    "text": phrase.get('text', ''),
                    "category": phrase.get('category', ''),
                    "importance": phrase.get('importance_score', 0)
                })
        
        # Create a clean version for compact_analysis field (without the field itself to avoid recursion)
        compact_for_llm = {
            "ticker": compact_analysis["ticker"],
            "companies": compact_analysis["companies"],
            "people": compact_analysis["people"],
            "sentiment": compact_analysis["sentiment"],
            "industry": compact_analysis["industry"],
            "key_points": compact_analysis["key_points"],
            "money_amounts": compact_analysis["money_amounts"],
            "important_dates": compact_analysis["important_dates"],
            "financial_keywords": compact_analysis["financial_keywords"],
            "key_relationships": compact_analysis["key_relationships"],
            "business_context": compact_analysis["business_context"]
        }
        
        # Add compact_analysis field for LLM processing
        compact_analysis['compact_analysis'] = json.dumps(compact_for_llm, ensure_ascii=False)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(compact_analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Compact entity analysis saved for {ticker} → {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Error saving compact entity analysis for {ticker}: {e}")
        return None

def demonstrate_spacy_model_collaboration(text: str, ticker: str = "DEMO") -> str:
    """Demonstrate how spaCy and the model work together"""
    analyzer = get_entity_analyzer()
    
    print("🔍 SPAÇY-MODEL COLLABORATION DEMONSTRATION")
    print("=" * 50)
    
    # Step 1: spaCy Analysis
    print("\n📊 STEP 1: SPAÇY ANALYSIS")
    print("-" * 30)
    analysis = analyzer.analyze_text(text, ticker)
    
    entities = analysis.get('entities', [])
    relationships = analysis.get('relationships', [])
    important_sentences = analysis.get('important_sentences', [])
    
    print(f"• spaCy found {len(entities)} entities")
    print(f"• spaCy identified {len(relationships)} relationships")
    print(f"• spaCy scored {len(important_sentences)} important sentences")
    
    # Show key entities
    companies = [e['text'] for e in entities if e.get('label') == 'ORG']
    people = [e['text'] for e in entities if e.get('label') == 'PERSON']
    money = [e['text'] for e in entities if e.get('label') == 'MONEY']
    
    if companies:
        print(f"• Companies (ORG): {', '.join(companies)}")
    if people:
        print(f"• People (PERSON): {', '.join(people)}")
    if money:
        print(f"• Money amounts (MONEY): {', '.join(money)}")
    
    # Step 2: Model Guidance
    print("\n🤖 STEP 2: MODEL GUIDANCE")
    print("-" * 30)
    guidance = generate_model_guidance_from_spacy(analysis)
    print(guidance)
    
    # Step 3: Collaboration Instructions
    print("\n🤝 STEP 3: COLLABORATION INSTRUCTIONS")
    print("-" * 30)
    collaboration = generate_spacy_collaboration_instructions()
    print(collaboration)
    
    # Step 4: Final Context
    print("\n📝 STEP 4: FINAL CONTEXT FOR MODEL")
    print("-" * 30)
    context = analyzer.generate_entity_context_for_llm(analysis)
    print(context)
    
    print("\n✅ COLLABORATION DEMONSTRATION COMPLETE")
    print("The model now has all the information it needs to write a professional article!")
    
    return f"Demonstration completed for {ticker} with {len(entities)} entities found" 