import pandas as pd
import subprocess
import json as pyjson
import re

# קריאת מיפוי טיקרים לסקטורים
sector_map_df = pd.read_csv("/Users/kinghippo/Documents/rssFeed/marketBit/data/flat-ui__data-Thu Jun 19 2025.csv")
sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))

# פרומפט מעודכן לפי דרישות המשתמש – שכתוב בלבד, ללא פרשנות
def generate_prompt(original_text: str, ticker_info=None):
    company = ticker_info.get("Security") if ticker_info else ""
    sector_name = ticker_info.get("GICS Sector") if ticker_info else ""

    prompt = f"""
אתה כותב כתבה מקצועית עבור גוף מחקר עצמאי בשם "Hippopotamus Research".

🎯 מטרתך:
ליצור כתבה ארוכה, מסוגננת ומעניינת המכסה את כל נקודות המפתח שנמסרו, עם מבנה מקצועי ועיצוב HTML נכון.

📌 מה שקיבלת:
רשימת נקודות מפתח (key points) על חברה כלשהי, כל משפט הוא נקודת עניין נפרדת.

📌 מה עליך לעשות:
1. **כתוב כתבה ארוכה ומקיפה** - המכסה את כל נקודות המפתח ללא יוצא מן הכלל
2. **שמור על כל הנתונים** - מספרים, תאריכים, שמות, ציטוטים ומחירי יעד חייבים להישאר בדיוק כפי שהם
3. **צור מבנה מקצועי עם HTML** - כותרת ראשית עם <h1>, כותרות משנה עם <h2>, פסקאות עם <p>, ואיות ברמה גבוהה
4. **סגנון כתיבה מעניין** - כתוב בצורה שמושכת עניין וזורמת, עם חיבורים לוגיים בין הפסקאות
5. **מקוריות** - אל תחזור על כותרות או משפטים זהים, שמור על גיוון וחדשנות

⚠️ כללים חשובים:
- אסור לשנות אף נתון מספרי או מידע חשוב
- אסור לפספס אף נקודת מפתח - כל פיסת מידע חייבת להופיע בכתבה
- אסור להוסיף מידע חדש שלא היה במקור
- אסור לבצע ניתוח או תחזיות משלך
- הכתבה חייבת להיות נאמנה למידע המקורי אך מסוגננת בכתיבה

✍️ מבנה הכתבה עם HTML:
- <h1>כותרת ראשית מעניינת</h1>
- <h2>כותרת משנה ראשונה</h2>
- <p>פסקה ראשונה עם תוכן...</p>
- <h2>כותרת משנה שנייה</h2>
- <p>פסקה שנייה עם תוכן...</p>
- וכן הלאה...

🔎 חברה: {company}
📂 סקטור: {sector_name}

**נקודות המפתח המקוריות:**
===
{original_text}
===

⚠️ חשוב מאוד: החזר כתבה מעוצבת עם תגי HTML נכונים (<h1>, <h2>, <p>), ללא JSON, תגים, או markdown (#).
"""
    return prompt

# הפעלת מודל Ollama עם prompt מעודכן
def process_with_gemma(original_text, ticker_info=None):
    """
    Process the original text with the LLM (aya-expanse:8b) using ONLY rephrasing and restructuring rules.
    Returns the processed text as a string.
    """
    prompt = generate_prompt(original_text, ticker_info)

    if ticker_info:
        prompt += "\n---\nמידע נוסף על החברה:\n"
        for k, v in ticker_info.items():
            prompt += f"{k}: {v}\n"

    prompt += "\n---\nהחזר כתבה מעוצבת עם תגי HTML נכונים (<h1>, <h2>, <p>), ללא JSON או תגים."

    try:
        result = subprocess.run(
            ["ollama", "run", "aya-expanse:8b"],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        output = result.stdout.decode("utf-8").strip()

        # ניקוי הפלט מכל סוגי JSON ותגים
        cleaned_output = clean_llm_text(output)
        
        # הסרת תגים ועובדות אם עדיין קיימים
        cleaned_output = remove_json_artifacts(cleaned_output)
        
        # המרת markdown ל-HTML אם נדרש
        cleaned_output = convert_markdown_to_html(cleaned_output)
        
        return cleaned_output

    except Exception as e:
        print(f"❌ Error running ollama: {e}")
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

def convert_markdown_to_html(text):
    """Convert markdown formatting to proper HTML tags"""
    if not text:
        return text
    
    # ניקוי בסיסי
    text = text.strip()
    
    # הסרת תגים כפולים או לא תקינים
    text = re.sub(r'<h1>\s*<h1>', '<h1>', text)
    text = re.sub(r'</h1>\s*</h1>', '</h1>', text)
    text = re.sub(r'<p>\s*<h1>', '<h1>', text)
    text = re.sub(r'</h1>\s*</p>', '</h1>', text)
    
    # המרת כותרות markdown ל-HTML
    text = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    
    # המרת פסקאות
    lines = text.split('\n')
    processed_lines = []
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        if not line:
            # שורה ריקה - סיים את הפסקה הנוכחית
            if current_paragraph:
                processed_lines.append(f'<p>{" ".join(current_paragraph)}</p>')
                current_paragraph = []
            continue
            
        # אם השורה מתחילה עם תג HTML (כותרת), סיים פסקה קיימת והתחל חדשה
        if re.match(r'^<[^>]+>', line):
            if current_paragraph:
                processed_lines.append(f'<p>{" ".join(current_paragraph)}</p>')
                current_paragraph = []
            processed_lines.append(line)
        else:
            # הוסף לשורה הנוכחית
            current_paragraph.append(line)
    
    # הוסף פסקה אחרונה אם יש
    if current_paragraph:
        processed_lines.append(f'<p>{" ".join(current_paragraph)}</p>')
    
    result = '\n'.join(processed_lines)
    
    # ניקוי נוסף של תגים כפולים - תיקון ה-regex
    result = re.sub(r'<p>\s*<h([1-6])>', r'<h\1>', result)
    result = re.sub(r'</h([1-6])>\s*</p>', r'</h\1>', result)
    
    return result

def clean_llm_text(text):
    """Clean LLM output from JSON artifacts and formatting issues"""
    if not text:
        return text
    text = re.sub(r'^\s*\{\s*', '', text)
    text = re.sub(r'\s*\}\s*$', '', text)
    text = re.sub(r'^\s*"text":\s*"', '', text)
    text = re.sub(r'^\s*"":\s*"', '', text)
    text = re.sub(r'"\s*,\s*"tags":\s*\[\s*\]\s*$', '', text)
    text = re.sub(r'"\s*$', '', text)
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
