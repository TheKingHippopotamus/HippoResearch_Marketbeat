#!/usr/bin/env python3
"""
Text Quality Checker for Hebrew Financial Writing
בודק איכות טקסט לכתיבה כלכלית עברית
"""

import re
from typing import Dict, List, Tuple, Optional
from tools.hebrew_vocabulary import get_vocabulary_manager

class TextQualityChecker:
    """בודק איכות טקסט עברי כלכלי"""
    
    def __init__(self):
        self.vocab_manager = get_vocabulary_manager()
        
    def check_text_quality(self, text: str) -> Dict:
        """בודק את איכות הטקסט ומחזיר דוח מפורט"""
        results = {
            'overall_score': 0,
            'issues': [],
            'suggestions': [],
            'grammar_errors': [],
            'style_issues': [],
            'vocabulary_score': 0,
            'flow_score': 0,
            'professionalism_score': 0
        }
        
        # בדיקת שגיאות דקדוק
        grammar_errors = self._check_grammar(text)
        results['grammar_errors'] = grammar_errors
        
        # בדיקת בעיות סגנון
        style_issues = self._check_style(text)
        results['style_issues'] = style_issues
        
        # בדיקת אוצר מילים
        vocab_score = self._check_vocabulary(text)
        results['vocabulary_score'] = vocab_score
        
        # בדיקת זרימה
        flow_score = self._check_flow(text)
        results['flow_score'] = flow_score
        
        # בדיקת מקצועיות
        professionalism_score = self._check_professionalism(text)
        results['professionalism_score'] = professionalism_score
        
        # חישוב ציון כללי
        results['overall_score'] = self._calculate_overall_score(results)
        
        # יצירת הצעות לשיפור
        results['suggestions'] = self._generate_suggestions(results)
        
        return results
    
    def _check_grammar(self, text: str) -> List[str]:
        """בודק שגיאות דקדוק נפוצות"""
        errors = []
        
        # בדיקת רבים/יחיד
        if re.search(r'המשקיעים\s+יכול\b', text):
            errors.append("שגיאת רבים/יחיד: 'המשקיעים יכול' → 'המשקיעים יכולים'")
        
        if re.search(r'האנליסטים\s+הציג\b', text):
            errors.append("שגיאת רבים/יחיד: 'האנליסטים הציג' → 'האנליסטים הציגו'")
        
        if re.search(r'החברות\s+מתמודד\b', text):
            errors.append("שגיאת רבים/יחיד: 'החברות מתמודד' → 'החברות מתמודדות'")
        
        # בדיקת ביטויים שגויים
        if re.search(r'שוק המניות של\s+', text):
            errors.append("ביטוי שגוי: 'שוק המניות של' → 'מניית'")
        
        # בדיקת משפטים לא שלמים
        if re.search(r'\w+\s+ל,\s*', text):
            errors.append("משפט לא שלם: משפט שמסתיים ב-'ל,'")
        
        # בדיקת סימני פיסוק
        if re.search(r',\s*,', text):
            errors.append("סימני פיסוק: פסיקים כפולים")
        
        if re.search(r'\.\s*\.', text):
            errors.append("סימני פיסוק: נקודות כפולות")
        
        return errors
    
    def _check_style(self, text: str) -> List[str]:
        """בודק בעיות סגנון"""
        issues = []
        
        # בדיקת מילות קישור
        connection_words = ['יתר על כן', 'לעומת זאת', 'בנוסף', 'לפיכך', 'מצד אחד', 'מצד שני']
        found_connections = sum(1 for word in connection_words if word in text)
        
        if found_connections < 2:
            issues.append("חסרות מילות קישור: מומלץ להשתמש ביותר מילות קישור לזרימה טובה יותר")
        
        # בדיקת אורך משפטים
        sentences = re.split(r'[.!?]', text)
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        
        if len(long_sentences) > 2:
            issues.append("משפטים ארוכים מדי: מומלץ לפצל משפטים ארוכים")
        
        # בדיקת חזרות
        words = text.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 3:  # רק מילים ארוכות
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = [word for word, count in word_counts.items() if count > 3]
        if repeated_words:
            issues.append(f"מילים חוזרות: {', '.join(repeated_words[:3])}")
        
        return issues
    
    def _check_vocabulary(self, text: str) -> float:
        """בודק את איכות אוצר המילים"""
        score = 0
        total_words = len(text.split())
        
        if total_words == 0:
            return 0
        
        # בדיקת שימוש במילים מקצועיות
        professional_words = [
            'רווח', 'הפסד', 'צמיחה', 'ירידה', 'תנודתיות', 'משקיע', 'אנליסט',
            'חברה', 'מניה', 'שוק', 'ביצועים', 'תחזית', 'הערכה'
        ]
        
        found_professional = sum(1 for word in professional_words if word in text)
        score += (found_professional / len(professional_words)) * 40
        
        # בדיקת שימוש במילות קישור מקצועיות
        connection_words = ['יתר על כן', 'לעומת זאת', 'בנוסף', 'לפיכך']
        found_connections = sum(1 for word in connection_words if word in text)
        score += (found_connections / len(connection_words)) * 30
        
        # בדיקת הימנעות ממילים לא מקצועיות
        informal_words = ['אבל', 'גם', 'פשוט', 'באמת', 'ממש']
        found_informal = sum(1 for word in informal_words if word in text)
        score -= (found_informal / len(informal_words)) * 30
        
        return max(0, min(100, score))
    
    def _check_flow(self, text: str) -> float:
        """בודק את זרימת הטקסט"""
        score = 0
        
        # בדיקת מעברים טבעיים
        transitions = ['יתר על כן', 'לעומת זאת', 'בנוסף', 'לפיכך', 'מצד אחד', 'מצד שני']
        found_transitions = sum(1 for transition in transitions if transition in text)
        score += (found_transitions / len(transitions)) * 40
        
        # בדיקת אורך פסקאות
        paragraphs = text.split('\n\n')
        good_paragraphs = sum(1 for p in paragraphs if 2 <= len(p.split()) <= 8)
        if paragraphs:
            score += (good_paragraphs / len(paragraphs)) * 30
        
        # בדיקת מבנה לוגי
        if '#TITLE#' in text and '#SUBTITLE#' in text and '#PARA#' in text:
            score += 30
        
        return min(100, score)
    
    def _check_professionalism(self, text: str) -> float:
        """בודק את רמת המקצועיות"""
        score = 0
        
        # בדיקת שימוש בגוף שלישי
        first_person = ['אני', 'אנחנו', 'אני', 'אנחנו']
        second_person = ['אתה', 'אתם', 'את', 'אתן']
        
        first_person_count = sum(1 for word in first_person if word in text)
        second_person_count = sum(1 for word in second_person if word in text)
        
        if first_person_count == 0 and second_person_count == 0:
            score += 40  # שימוש נכון בגוף שלישי
        
        # בדיקת מילים מקצועיות
        professional_terms = [
            'ניתוח', 'תחזית', 'הערכה', 'ביצועים', 'תוצאות', 'אסטרטגיה',
            'שוק', 'משקיע', 'אנליסט', 'חברה', 'רווח', 'הפסד'
        ]
        
        found_terms = sum(1 for term in professional_terms if term in text)
        score += (found_terms / len(professional_terms)) * 30
        
        # בדיקת הימנעות ממילים לא מקצועיות
        informal_terms = ['ממש', 'באמת', 'פשוט', 'כזה', 'כאלה']
        found_informal = sum(1 for term in informal_terms if term in text)
        score -= (found_informal / len(informal_terms)) * 30
        
        return max(0, min(100, score))
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """מחשב ציון כללי"""
        weights = {
            'vocabulary_score': 0.25,
            'flow_score': 0.25,
            'professionalism_score': 0.25,
            'grammar_errors': 0.15,
            'style_issues': 0.10
        }
        
        score = 0
        
        # ציונים חיוביים
        score += results['vocabulary_score'] * weights['vocabulary_score']
        score += results['flow_score'] * weights['flow_score']
        score += results['professionalism_score'] * weights['professionalism_score']
        
        # הפחתות על שגיאות
        grammar_penalty = len(results['grammar_errors']) * 5
        style_penalty = len(results['style_issues']) * 3
        
        score -= min(grammar_penalty, 20)  # מקסימום הפחתה של 20 נקודות
        score -= min(style_penalty, 15)    # מקסימום הפחתה של 15 נקודות
        
        return max(0, min(100, score))
    
    def _generate_suggestions(self, results: Dict) -> List[str]:
        """מייצר הצעות לשיפור"""
        suggestions = []
        
        # הצעות על בסיס שגיאות דקדוק
        for error in results['grammar_errors']:
            suggestions.append(f"תיקון דקדוק: {error}")
        
        # הצעות על בסיס בעיות סגנון
        for issue in results['style_issues']:
            suggestions.append(f"שיפור סגנון: {issue}")
        
        # הצעות על בסיס ציונים נמוכים
        if results['vocabulary_score'] < 60:
            suggestions.append("הרחבת אוצר מילים: השתמש במילים מקצועיות יותר")
        
        if results['flow_score'] < 60:
            suggestions.append("שיפור זרימה: הוסף מילות קישור ומעברים טבעיים")
        
        if results['professionalism_score'] < 60:
            suggestions.append("הגברת מקצועיות: השתמש בגוף שלישי והימנע ממילים לא פורמליות")
        
        # הצעות כלליות
        if results['overall_score'] < 70:
            suggestions.append("בדוק את המבנה הכללי של הטקסט")
            suggestions.append("וודא שכל המשפטים שלמים ומדויקים")
        
        return suggestions
    
    def get_improved_text(self, text: str) -> str:
        """מחזיר גרסה משופרת של הטקסט"""
        improved_text = text
        
        # תיקון שגיאות דקדוק
        improved_text = re.sub(r'המשקיעים\s+יכול\b', 'המשקיעים יכולים', improved_text)
        improved_text = re.sub(r'האנליסטים\s+הציג\b', 'האנליסטים הציגו', improved_text)
        improved_text = re.sub(r'החברות\s+מתמודד\b', 'החברות מתמודדות', improved_text)
        
        # תיקון ביטויים שגויים
        improved_text = re.sub(r'שוק המניות של\s+', 'מניית ', improved_text)
        
        # תיקון סימני פיסוק
        improved_text = re.sub(r',\s*,', ',', improved_text)
        improved_text = re.sub(r'\.\s*\.', '.', improved_text)
        
        return improved_text
    
    def generate_quality_report(self, text: str) -> str:
        """מייצר דוח איכות מפורט"""
        results = self.check_text_quality(text)
        
        report = f"""
📊 דוח איכות טקסט

🎯 ציון כללי: {results['overall_score']:.1f}/100

📈 ציונים מפורטים:
• אוצר מילים: {results['vocabulary_score']:.1f}/100
• זרימה: {results['flow_score']:.1f}/100
• מקצועיות: {results['professionalism_score']:.1f}/100

❌ שגיאות דקדוק ({len(results['grammar_errors'])}):
"""
        
        for error in results['grammar_errors']:
            report += f"  • {error}\n"
        
        if results['style_issues']:
            report += f"\n⚠️ בעיות סגנון ({len(results['style_issues'])}):\n"
            for issue in results['style_issues']:
                report += f"  • {issue}\n"
        
        if results['suggestions']:
            report += f"\n💡 הצעות לשיפור:\n"
            for suggestion in results['suggestions']:
                report += f"  • {suggestion}\n"
        
        return report

# Global instance
quality_checker = TextQualityChecker()

def get_quality_checker() -> TextQualityChecker:
    """מחזיר את בודק האיכות הגלובלי"""
    return quality_checker

def check_text_quality(text: str) -> Dict:
    """פונקציה נוחה לבדיקת איכות טקסט"""
    return quality_checker.check_text_quality(text)

def get_improved_text(text: str) -> str:
    """פונקציה נוחה לשיפור טקסט"""
    return quality_checker.get_improved_text(text)

def generate_quality_report(text: str) -> str:
    """פונקציה נוחה ליצירת דוח איכות"""
    return quality_checker.generate_quality_report(text)

if __name__ == "__main__":
    # דוגמה לשימוש
    sample_text = """
    #TITLE# ניתוח מניית Apple
    
    #SUBTITLE# ביצועים מעורבים ברבעון האחרון
    
    #PARA# מניית Apple חווה תנודתיות בשוק, עם ביצועים מעורבים ברבעון האחרון. המשקיעים יכול לראות הזדמנויות, אבל האנליסטים הציג חששות לגבי הצמיחה העתידית.
    
    #PARA# שוק המניות של Apple הגיב בחיוביות לחדשות האחרונות, אולם האתגרים נותרו משמעותיים.
    """
    
    print("דוגמה לבדיקת איכות טקסט:")
    print(generate_quality_report(sample_text))
    
    print("\nטקסט משופר:")
    print(get_improved_text(sample_text)) 