# Feedback System Integration

## סקירה כללית

מערכת המשוב המשולבת משפרת את איכות התרגום על ידי שילוב כללי איכות מפורטים עם המודל הקיים. המערכת כוללת:

1. **Feedback Processor** - מעבד את כללי המשוב מ-JSON
2. **Thinking Prompts** - יוצר הנחיות חשיבה מובנות
3. **Quality Checks** - בודק איכות התרגום
4. **Entity Analysis Integration** - משלב ניתוח ישויות עם כללי המשוב

## מבנה הקבצים

```
tools/
├── feedback_processor.py    # מעבד כללי משוב
├── feedback_demo.py         # דוגמה לשימוש
├── llm_processor.py         # מעודכן עם שילוב משוב
├── entity_analyzer.py       # מעודכן עם שילוב משוב
└── config.py               # הגדרות משוב חדשות

feedback_clean.json         # כללי המשוב
FEEDBACK_INTEGRATION.md     # קובץ זה
```

## שימוש בסיסי

### 1. טעינת מעבד המשוב

```python
from tools.feedback_processor import get_feedback_processor

processor = get_feedback_processor()
rules = processor.get_all_rules()
print(f"נטענו {len(rules)} כללי משוב")
```

### 2. יצירת Thinking Prompt

```python
text = "Apple (AAPL) reported strong earnings..."
thinking_prompt = processor.generate_thinking_prompt(text, "AAPL")
print(thinking_prompt)
```

### 3. עיבוד עם בדיקת איכות

```python
from tools.llm_processor import process_with_quality_check

result = process_with_quality_check(
    text_block=text,
    ticker_symbol="AAPL"
)

print(f"תרגום ראשוני: {result['initial_translation']}")
print(f"בדיקת איכות: {result['quality_check_prompt']}")
```

## כללי המשוב

### קטגוריות

1. **Translation** - תרגום שמות חברות וטיקרים
2. **Factual** - דיוק עובדתי ומקורות
3. **Stylistic** - סגנון וניסוח
4. **General** - כללים כלליים

### דוגמאות לכללים

#### תרגום שמות חברות
```json
{
  "error_type": "Entity Translation - Company Name",
  "rule": "Do not translate company names like 'Abbott Laboratories' into Hebrew",
  "bad_example": "Abbott Laboratories (ABT) צריכה להופיע באנגלית בלבד",
  "good_example": "Abbott Laboratories (ABT) מופיעה באנגלית בלבד"
}
```

#### דיוק עובדתי
```json
{
  "error_type": "Factual Addition Without Source",
  "rule": "Avoid inventing strategic acquisitions",
  "bad_example": "הרכישה האחרונה שזכתה לתשומת לב",
  "good_example": "שמועה לרכישה אפשרית של PTC"
}
```

## שילוב עם Entity Analyzer

המערכת משלבת את ניתוח הישויות עם כללי המשוב:

```python
from tools.entity_analyzer import analyze_text_for_llm_with_cache

# ניתוח ישויות עם משוב משולב
entity_context = analyze_text_for_llm_with_cache(text, "MSFT")
```

## הגדרות

בקובץ `config.py`:

```python
FEEDBACK_SETTINGS = {
    "enable_thinking_prompt": True,    # האם לכלול thinking prompt
    "enable_quality_check": True,      # האם לבדוק איכות
    "feedback_file_path": "feedback_clean.json",
    "auto_correct": False,             # תיקון אוטומטי
    "manual_review": True,             # סקירה ידנית
}
```

## הרצת הדוגמה

```bash
cd tools
python feedback_demo.py
```

## יתרונות השילוב

### 1. איכות משופרת
- כללי משוב מובנים מונעים שגיאות נפוצות
- Thinking prompts מכוונים את המודל
- בדיקות איכות תופסות בעיות

### 2. עקביות
- כללים אחידים לכל התרגומים
- סגנון עקבי בין מאמרים
- שמירה על דיוק עובדתי

### 3. יכולת למידה
- הוספת כללים חדשים בקלות
- עדכון כללים קיימים
- מעקב אחר שיפורים

### 4. שקיפות
- כל הכללים גלויים וניתנים לסקירה
- דוגמאות טובות ורעות
- הסברים מפורטים

## הוספת כללים חדשים

1. ערוך את `feedback_clean.json`
2. הוסף כלל חדש:

```json
{
  "error_type": "New Error Type",
  "rule": "Description of the rule",
  "bad_example": "Example of bad translation",
  "good_example": "Example of good translation",
  "comment": "Additional explanation"
}
```

3. המודל יטען את הכלל החדש אוטומטית

## מעקב אחר ביצועים

המערכת מספקת לוגים מפורטים:

```
🧠 Generated thinking prompt with feedback rules for AAPL
🔍 Applied quality check for AAPL
✅ Entity analysis context generated for AAPL
```

## סיכום

מערכת המשוב המשולבת מספקת:

- **איכות גבוהה יותר** - כללים מובנים מונעים שגיאות
- **עקביות** - סגנון אחיד בין כל המאמרים  
- **שקיפות** - כל הכללים גלויים וניתנים לסקירה
- **גמישות** - הוספת כללים חדשים בקלות
- **יכולת למידה** - שיפור מתמיד של המערכת

המערכת מוכנה לשימוש מיידי ומשפרת משמעותית את איכות התרגום הפיננסי. 