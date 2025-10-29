import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FeedbackRule:
    """Represents a single feedback rule for quality improvement"""
    error_type: str
    rule: str
    bad_example: str
    good_example: str
    comment: str
    category: str = "general"  # general, translation, factual, stylistic

class FeedbackProcessor:
    """Processes and applies feedback rules to improve translation quality"""
    
    def __init__(self, feedback_path: str = "feedback_clean.json"):
        self.feedback_path = feedback_path
        self.rules = self._load_feedback_rules()
        self.categorized_rules = self._categorize_rules()
    
    def _load_feedback_rules(self) -> List[FeedbackRule]:
        """Load feedback rules from JSON file"""
        try:
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rules = []
            for item in data:
                rule = FeedbackRule(
                    error_type=item.get('error_type', ''),
                    rule=item.get('rule', ''),
                    bad_example=item.get('bad_example', ''),
                    good_example=item.get('good_example', ''),
                    comment=item.get('comment', ''),
                    category=self._determine_category(item.get('error_type', ''))
                )
                rules.append(rule)
            
            return rules
        except Exception as e:
            print(f"Error loading feedback rules: {e}")
            return []
    
    def _determine_category(self, error_type: str) -> str:
        """Determine the category of a feedback rule based on error type"""
        error_type_lower = error_type.lower()
        
        if any(keyword in error_type_lower for keyword in ['translation', 'entity', 'company name']):
            return 'translation'
        elif any(keyword in error_type_lower for keyword in ['factual', 'source', 'invent', 'misinterpretation']):
            return 'factual'
        elif any(keyword in error_type_lower for keyword in ['stylistic', 'redundancy', 'overgeneralization']):
            return 'stylistic'
        else:
            return 'general'
    
    def _categorize_rules(self) -> Dict[str, List[FeedbackRule]]:
        """Categorize rules by type for easier access"""
        categorized = {
            'translation': [],
            'factual': [],
            'stylistic': [],
            'general': []
        }
        
        for rule in self.rules:
            categorized[rule.category].append(rule)
        
        return categorized
    
    def generate_thinking_prompt(self, text: str, ticker: Optional[str] = None) -> str:
        """Generate a thinking prompt that incorporates feedback rules"""
        
        thinking_prompt = f"""אתה מתרגם טקסט פיננסי לעברית. לפני שתתחיל לתרגם, חשוב על הכללים הבאים:

## כללי איכות קריטיים:

### 1. שמות חברות וטיקרים:
- אל תתרגם שמות חברות לאנגלית (למשל: Abbott Laboratories נשאר באנגלית)
- השתמש בטיקר רק בהצגה הראשונה, אחר כך השתמש ב"החברה"
- הבהר הבדלים בין אנשים לחברות בעלות אותו שם

### 2. דיוק עובדתי:
- אל תמציא עובדות שלא מוזכרות במקור
- ציין במדויק תחזיות EPS, גם אם השינוי קטן
- שמור על טון מדויק - אל תעצים סנטימנט מעבר למקור

### 3. סגנון וניסוח:
- הימנע מניסוחים מיותרים ("בהירות ותקשורת ברורה" → "שקיפות")
- אל תטען לנוכחות גלובלית אם רק צפון אמריקה מוזכרת
- השתמש במגוון מקורות (Yahoo, MarketBeat, Zacks)

### 4. הפרדת סנטימנט:
- הפרד בין תוכן חיובי, שלילי ונייטרלי
- שמור על דיוק במחירים ותחזיות
- ציין גם שינויים שליליים גם אם הסנטימנט הכללי חיובי

## טקסט לעיבוד:
{text}

## הוראות חשיבה:
1. זהה את כל השמות והטיקרים שצריכים להישאר באנגלית
2. בדוק אילו עובדות פיננסיות מוזכרות במדויק
3. זהה את הסנטימנט הכללי והשינויים בו
4. תכנן איך להפריד בין חלקים חיוביים ושליליים
5. וודא שכל המספרים והתחזיות מדויקים

אחרי שתחשוב על הנקודות האלה, תתחיל לתרגם תוך שמירה על כל הכללים."""

        return thinking_prompt
    
    def generate_quality_check_prompt(self, translated_text: str, original_text: str) -> str:
        """Generate a prompt to check the quality of translated text"""
        
        check_prompt = f"""בדוק את התרגום הבא לפי כללי האיכות:

## טקסט מקורי:
{original_text[:500]}...

## טקסט מתורגם:
{translated_text}

## בדיקות איכות:

### 1. שמות חברות:
- [ ] כל שמות החברות נשארו באנגלית
- [ ] טיקרים מופיעים רק בהצגה הראשונה
- [ ] אין בלבול בין אנשים לחברות

### 2. דיוק עובדתי:
- [ ] אין עובדות שהומצאו
- [ ] כל המספרים והתחזיות מדויקים
- [ ] הסנטימנט תואם למקור

### 3. סגנון:
- [ ] אין ניסוחים מיותרים
- [ ] אין הכללות מוגזמות
- [ ] מגוון מקורות מוזכרים

### 4. מבנה:
- [ ] הפרדה ברורה בין סנטימנטים
- [ ] זרימה טבעית בעברית
- [ ] שמירה על משמעות המקור

אם יש בעיות, תקן אותן ותן גרסה משופרת."""

        return check_prompt
    
    def get_rules_by_category(self, category: str) -> List[FeedbackRule]:
        """Get rules by category"""
        return self.categorized_rules.get(category, [])
    
    def get_all_rules(self) -> List[FeedbackRule]:
        """Get all feedback rules"""
        return self.rules
    
    def generate_rule_summary(self) -> str:
        """Generate a summary of all rules for quick reference"""
        summary = "## סיכום כללי איכות:\n\n"
        
        for category, rules in self.categorized_rules.items():
            if rules:
                summary += f"### {category.upper()}:\n"
                for rule in rules:
                    summary += f"- {rule.rule}\n"
                summary += "\n"
        
        return summary

def get_feedback_processor() -> FeedbackProcessor:
    """Get a singleton instance of FeedbackProcessor"""
    if not hasattr(get_feedback_processor, '_instance'):
        get_feedback_processor._instance = FeedbackProcessor()
    return get_feedback_processor._instance

def integrate_feedback_with_prompt(base_prompt: str, text: str, ticker: Optional[str] = None) -> str:
    """Integrate feedback rules with existing prompt"""
    processor = get_feedback_processor()
    thinking_prompt = processor.generate_thinking_prompt(text, ticker)
    
    enhanced_prompt = f"""{thinking_prompt}

{base_prompt}"""
    
    return enhanced_prompt

def apply_quality_check(translated_text: str, original_text: str) -> str:
    """Apply quality check to translated text"""
    processor = get_feedback_processor()
    check_prompt = processor.generate_quality_check_prompt(translated_text, original_text)
    return check_prompt 