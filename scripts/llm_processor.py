import pandas as pd
import subprocess
import json as pyjson
import re
import os
import sys
import logging

# Setup logging
logger = logging.getLogger(__name__)

# הוספת הנתיב הראשי למערכת כדי שנוכל לקרוא את קובץ ה-CSV
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# קריאת מיפוי טיקרים לסקטורים - עם טיפול במקרה שהקובץ לא קיים
sector_map = {}
csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "flat-ui__data-Thu Jun 19 2025.csv")
if os.path.exists(csv_path):
    try:
        sector_map_df = pd.read_csv(csv_path)
        sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not load sector mapping: {e}")
else:
    logger.warning("⚠️ Warning: CSV file not found, sector mapping will be empty")

# פרומפט מעודכן לפי דרישות המשתמש – שכתוב בלבד, ללא פרשנות
def generate_prompt(original_text: str, ticker_info=None):
    company = ticker_info.get("Security") if ticker_info else ""
    sector_name = ticker_info.get("GICS Sector") if ticker_info else ""

    prompt = f"""
אתה כותב כתבה מקצועית ומרתקת עבור גוף מחקר עצמאי בשם "Hippopotamus Research".

🎯 מטרתך:
ליצור כתבה ארוכה, מסוגננת ומעניינת המכסה את כל נקודות המפתח שנמסרו - לעולם אל תדלג או תשמיט מידע מהמידע שקיבלת ! אתה חייב להשתמש בכולו ! , עם סגנון כתיבה סיפורי ומרתק.

📌 מה שקיבלת:
רשימת נקודות מפתח (key points) על חברה כלשהי, כל משפט הוא נקודת עניין נפרדת.

📌 מה עליך לעשות:
1. **כתוב כתבה ארוכה ומקיפה** - המכסה את כל נקודות המפתח ללא יוצא מן הכלל
2. **שמור על כל הנתונים** - מספרים, תאריכים, שמות, ציטוטים ומחירי יעד חייבים להישאר בדיוק כפי שהם
3. **צור מבנה מקצועי עם סימון ברור** - השתמש במבנה הבא:
   - כותרת ראשית: התחל את השורה ב-#TITLE#
   - כותרת משנה: התחל את השורה ב-#SUBTITLE#
   - פסקה רגילה: התחל את השורה ב-#PARA#
4. **סגנון כתיבה יצירתי, מגוון ומפתיע** - כל כתבה חייבת להיות בסגנון שונה, מקורי, וחדשני. אל תחזור על כותרות, ביטויים, או מבנה מהכתבות הקודמות. השתמש במגוון רחב של סגנונות, מטאפורות, שאלות רטוריות, ודימויים. הפתע את הקורא בכל כתבה מחדש. אל תשתמש בדוגמאות מהוראות אלו – המצא בעצמך!
5. **מקוריות** - אל תחזור על כותרות או משפטים זהים, שמור על גיוון וחדשנות

⚠️ כללים חשובים:
- אסור לשנות אף נתון מספרי או מידע חשוב
- אסור לפספס אף נקודת מפתח - כל פיסת מידע חייבת להופיע בכתבה
- אסור להוסיף מידע חדש שלא היה במקור
- אסור לבצע ניתוח או תחזיות משלך
- הכתבה חייבת להיות נאמנה למידע המקורי אך מסוגננת בכתיבה

🔤 הנחיה חשובה:
כל שם של מוסד, אתר, חברה, גוף מחקר, כלי תקשורת (למשל: CNBC, Bloomberg, Palantir, Visa, Microsoft, Google, Reuters, MarketBeat) – יש לכתוב באנגלית בלבד, גם אם שאר הכתבה בעברית. אין לתרגם או לתעתק שמות אלו לעברית.

✍️ מבנה הכתבה:
- שורה ראשונה: #TITLE# כותרת ראשית מעניינת
- שורה שנייה: #SUBTITLE# כותרת משנה ראשונה
- שורה שלישית: #PARA# פסקה ראשונה
- וכן הלאה...

🔎 חברה: {company}
📂 סקטור: {sector_name}

**נקודות המפתח המקוריות:**
===
{original_text}
===

⚠️ חשוב מאוד: החזר טקסט בלבד, כל שורה מתחילה באחד מהבאים: #TITLE#, #SUBTITLE#, #PARA#. אין להחזיר תגי HTML, markdown, JSON או תגים אחרים.
"""
    return prompt

def clean_processed_text(text):
    """
    מנקה את הטקסט המעובד מסימונים מיותרים ותגים לא נכונים
    """
    if not text:
        return text
    
    # הסרת סימונים פנימיים של המערכת
    text = re.sub(r'TITLE#\s*', '', text)
    text = re.sub(r'SUBTITLE#\s*', '', text)
    text = re.sub(r'PARA#\s*', '', text)
    
    # הסרת סימונים מיותרים
    text = re.sub(r'##\s*', '', text)
    text = re.sub(r'#+\s*', '', text)
    
    # ניקוי תגי HTML לא נכונים
    text = re.sub(r'<p>\s*</p>', '', text)  # תגי p ריקים
    text = re.sub(r'<h\d>\s*</h\d>', '', text)  # תגי h ריקים
    
    # הסרת שורות ריקות מיותרות
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # ניקוי רווחים מיותרים בתחילת ובסוף
    text = text.strip()
    
    return text

def convert_tagged_text_to_html(text):
    """
    המרת טקסט מסומן (כולל סימוני markdown, כותרות ופסקאות בעברית) ל-HTML תקני, תוך הסרה מוחלטת של תוויות מיותרות.
    """
    if not text:
        return text
    
    lines = text.split('\n')
    processed_lines = []
    
    # דפוס לזיהוי שורות תווית מיותרות (עם או בלי #)
    label_pattern = re.compile(r'^(#*)\s*(פסקה( משנה| אחרונה)?(:|\s*:)?.*)$', re.UNICODE)
    # דפוס לזיהוי "כותרת ראשית: ..."
    main_title_pattern = re.compile(r'^כותרת ראשית:\s*(.*)$')
    # דפוס לזיהוי "כותרת משנה: ..."
    subtitle_pattern = re.compile(r'^כותרת משנה:\s*(.*)$')
    # דפוס לזיהוי "פסקה משנה: ..."
    subpara_pattern = re.compile(r'^פסקה משנה:\s*(.*)$')
    # דפוס לזיהוי "פסקה אחרונה: ..."
    lastpara_pattern = re.compile(r'^פסקה אחרונה:\s*(.*)$')
    # דפוס לזיהוי TITLE# ...
    title_hash_pattern = re.compile(r'^TITLE#\s*(.*)$')
    # דפוס לזיהוי SUBTITLE# (עם או בלי ##)
    subtitle_hash_pattern = re.compile(r'^(##\s*)?SUBTITLE#\s*(.*)$')
    # דפוס לזיהוי ## #pattern (like PFE uses)
    subtitle_hash_alt_pattern = re.compile(r'^##\s*#([^#]+)$')
    # דפוס לזיהוי ## ## pattern (like INCY uses)
    subtitle_double_hash_pattern = re.compile(r'^##\s*##\s*(.*)$')
    # דפוס לזיהוי #PARA# ...
    para_hash_pattern = re.compile(r'^#PARA#\s*(.*)$')
    # דפוס לזיהוי ### PARA# ...
    para_hash_triple_pattern = re.compile(r'^###\s*PARA#\s*(.*)$')
    # דפוס לזיהוי # פסקה ראשונה:, # פסקה שנייה: וכו'
    hebrew_para_pattern = re.compile(r'^#\s*פסקה\s+(ראשונה|שנייה|שלישית|רביעית|חמישית|שישית|שביעית|שמינית|תשיעית|עשירית):\s*(.*)$')

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # דלג על שורות שהן רק תווית פסקה ("פסקה ראשונה:", "פסקה שנייה:" וכו')
        if label_pattern.match(line):
            continue
        # כותרת ראשית
        m = main_title_pattern.match(line)
        if m:
            title = m.group(1).strip()
            if title:
                processed_lines.append(f'<h1>{title}</h1>')
            continue
        # כותרת משנה
        m = subtitle_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        # פסקה משנה
        m = subpara_pattern.match(line)
        if m:
            subpara = m.group(1).strip()
            if subpara:
                processed_lines.append(f'<h3>{subpara}</h3>')
            continue
        # פסקה אחרונה
        m = lastpara_pattern.match(line)
        if m:
            lastpara = m.group(1).strip()
            if lastpara:
                processed_lines.append(f'<h3>{lastpara}</h3>')
            continue
        # TITLE# pattern
        m = title_hash_pattern.match(line)
        if m:
            title = m.group(1).strip()
            if title:
                processed_lines.append(f'<h1>{title}</h1>')
            continue
        # SUBTITLE# pattern
        m = subtitle_hash_pattern.match(line)
        if m:
            subtitle = m.group(2).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        # ## #pattern (like PFE uses)
        m = subtitle_hash_alt_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        # ## ## pattern (like INCY uses)
        m = subtitle_double_hash_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        # #PARA# pattern
        m = para_hash_pattern.match(line)
        if m:
            para_text = m.group(1).strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        # ### PARA# pattern
        m = para_hash_triple_pattern.match(line)
        if m:
            para_text = m.group(1).strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        # Hebrew paragraph pattern (# פסקה ראשונה:, etc.)
        m = hebrew_para_pattern.match(line)
        if m:
            para_text = m.group(2).strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        # ### pattern for paragraphs (like ORCL uses)
        if line.startswith('### ') and not line.startswith('### PARA#') and not line.startswith('### SUBTITLE#'):
            para_text = line[4:].strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        # markdown
        if line.startswith('### '):
            processed_lines.append(f'<h3>{line[4:]}</h3>')
            continue
        if line.startswith('## '):
            processed_lines.append(f'<h2>{line[3:]}</h2>')
            continue
        if line.startswith('# '):
            processed_lines.append(f'<h1>{line[2:]}</h1>')
            continue
        # כל שאר השורות - פסקה רגילה
        processed_lines.append(f'<p>{line}</p>')
    
    return '\n'.join(processed_lines)

# הפעלת מודל Ollama עם prompt מעודכן
def process_with_gemma(original_text, ticker_info=None):
    """
    Process the original text with the LLM (aya-expanse:8b) using ONLY rephrasing and restructuring rules.
    Returns the processed text as a string with markers (#TITLE#, #SUBTITLE#, #PARA#).
    """
    prompt = generate_prompt(original_text, ticker_info)

    if ticker_info:
        prompt += "\n---\nמידע נוסף על החברה:\n"
        for k, v in ticker_info.items():
            prompt += f"{k}: {v}\n"

    prompt += "\n---\nהחזר טקסט בלבד, כל שורה מתחילה באחד מהבאים: #TITLE#, #SUBTITLE#, #PARA#. אין להחזיר תגי HTML, markdown, JSON או תגים אחרים."

    try:
        result = subprocess.run(
            ["ollama", "run", "aya-expanse:8b"],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        output = result.stdout.decode("utf-8").strip()
        logger.debug(f"🔍 DEBUG: Raw LLM output (first 200 chars): {output[:200]}...")
        
        # ניקוי הפלט מכל סוגי JSON ותגים
        cleaned_output = clean_llm_text(output)
        logger.debug(f"🔍 DEBUG: After clean_llm_text (first 200 chars): {cleaned_output[:200]}...")
        
        # הסרת תגים ועובדות אם עדיין קיימים
        cleaned_output = remove_json_artifacts(cleaned_output)
        logger.debug(f"🔍 DEBUG: After remove_json_artifacts (first 200 chars): {cleaned_output[:200]}...")
        
        # החזרת הטקסט הגולמי עם הסימונים - לא HTML!
        return cleaned_output
        
    except Exception as e:
        logger.error(f"❌ Error running ollama: {e}")
        return clean_llm_text("שגיאה בעיבוד LLM: " + str(e))

def remove_json_artifacts(text):
    """Remove JSON artifacts, tags, and facts from the text"""
    if not text:
        return text
    
    # הסרת JSON מלא
    text = re.sub(r'^\s*\{.*?"text":\s*"', '', text, flags=re.DOTALL)
    text = re.sub(r'",\s*"tags":\s*\[.*?\]\s*,\s*"facts":\s*\[.*?\]\s*\}\s*$', '', text, flags=re.DOTALL)
    text = re.sub(r'",\s*"tags":\s*\[.*?\]\s*\}\s*$', '', text, flags=re.DOTALL)
    text = re.sub(r'",\s*"facts":\s*\[.*?\]\s*\}\s*$', '', text, flags=re.DOTALL)
    text = re.sub(r'"\s*\}\s*$', '', text)
    
    # הסרת תגים ועובדות בודדים
    text = re.sub(r',\s*"tags":\s*\[.*?\]', '', text, flags=re.DOTALL)
    text = re.sub(r',\s*"facts":\s*\[.*?\]', '', text, flags=re.DOTALL)
    
    # הסרת markdown
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # ניקוי נוסף
    text = re.sub(r'^\s*"', '', text)
    text = re.sub(r'"\s*$', '', text)
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\\"', '"', text)
    
    return text.strip()

def clean_llm_text(text):
    """Clean LLM output from JSON artifacts, HTML tags, markdown symbols, and formatting issues"""
    if not text:
        return text
    
    # Remove JSON structure artifacts
    text = re.sub(r'^\s*\{\s*', '', text)
    text = re.sub(r'\s*\}\s*$', '', text)
    text = re.sub(r'^\s*"text":\s*"', '', text)
    text = re.sub(r'^\s*"":\s*"', '', text)
    text = re.sub(r'"\s*,\s*"tags":\s*\[\s*\]\s*$', '', text)
    text = re.sub(r'"\s*$', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown symbols
    text = re.sub(r'^#+\s*', '', text)  # Remove markdown headers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markdown
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic markdown
    
    # Clean up newlines and whitespace
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
    text = re.sub(r' +', ' ', text)  # Normalize spaces
    
    return text.strip() 