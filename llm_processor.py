import pandas as pd
import subprocess
import json as pyjson
import re
import os

# קריאת מיפוי טיקרים לסקטורים - עם טיפול במקרה שהקובץ לא קיים
sector_map = {}
csv_path = "/Users/kinghippo/Documents/rssFeed/marketBit/data/flat-ui__data-Thu Jun 19 2025.csv"
if os.path.exists(csv_path):
    try:
        sector_map_df = pd.read_csv(csv_path)
        sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))
    except Exception as e:
        print(f"⚠️ Warning: Could not load sector mapping: {e}")
else:
    print("⚠️ Warning: CSV file not found, sector mapping will be empty")

# פרומפט מעודכן לפי דרישות המשתמש – שכתוב בלבד, ללא פרשנות
def generate_prompt(original_text: str, ticker_info=None):
    company = ticker_info.get("Security") if ticker_info else ""
    sector_name = ticker_info.get("GICS Sector") if ticker_info else ""

    prompt = f"""
אתה כותב כתבה מקצועית ומרתקת עבור גוף מחקר עצמאי בשם "Hippopotamus Research".

🎯 מטרתך:
ליצור כתבה ארוכה, מסוגננת ומעניינת המכסה את כל נקודות המפתח שנמסרו, עם סגנון כתיבה סיפורי ומרתק.

📌 מה שקיבלת:
רשימת נקודות מפתח (key points) על חברה כלשהי, כל משפט הוא נקודת עניין נפרדת.

📌 מה עליך לעשות:
1. **כתוב כתבה ארוכה ומקיפה** - המכסה את כל נקודות המפתח ללא יוצא מן הכלל
2. **שמור על כל הנתונים** - מספרים, תאריכים, שמות, ציטוטים ומחירי יעד חייבים להישאר בדיוק כפי שהם
3. **צור מבנה מקצועי עם סימון ברור** - השתמש במבנה הבא:
   - כותרת ראשית: התחל את השורה ב-#TITLE#
   - כותרת משנה: התחל את השורה ב-#SUBTITLE#
   - פסקה רגילה: התחל את השורה ב-#PARA#
4. **סגנון כתיבה סיפורי ומרתק** - כתוב בצורה שמושכת עניין, עם:
   - כותרות מעניינות ומעוררות סקרנות
   - שאלות רטוריות שמעוררות מחשבה
   - חיבורים לוגיים וזורמים בין הפסקאות
   - תיאורים חיים ומרתקים
   - שימוש במטאפורות ומשחקי מילים מתאימים
5. **מקוריות** - אל תחזור על כותרות או משפטים זהים, שמור על גיוון וחדשנות

🎭 סגנון הכתיבה הרצוי:
- **כותרות מעניינות**: "המירוץ למרחב הסייבר", "המשחק הגדול של השווקים"
- **שאלות רטוריות**: "האם זהו רץ סוס מנצח או אשליה קצרת טווח?"
- **תיאורים חיים**: "המניה הגיעה לשיאים חדשים, עם שיאי 52 שבועות ושיאי כל הזמנים"
- **חיבורים זורמים**: "בעוד שהעולם מתמודד עם...", "מאחורי החגיגה הזאת..."
- **מטאפורות מתאימות**: "המתחים הגיאופוליטיים משמשים כדלק נוסף"

⚠️ כללים חשובים:
- אסור לשנות אף נתון מספרי או מידע חשוב
- אסור לפספס אף נקודת מפתח - כל פיסת מידע חייבת להופיע בכתבה
- אסור להוסיף מידע חדש שלא היה במקור
- אסור לבצע ניתוח או תחזיות משלך
- הכתבה חייבת להיות נאמנה למידע המקורי אך מסוגננת בכתיבה

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

def convert_tagged_text_to_html(text):
    """המרת טקסט מסומן (#TITLE#, #SUBTITLE#, #PARA#) ל-HTML תקני"""
    html_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#TITLE#"):
            html_lines.append(f"<h1>{line[len('#TITLE#'):].strip()}</h1>")
        elif line.startswith("#SUBTITLE#"):
            html_lines.append(f"<h2>{line[len('#SUBTITLE#'):].strip()}</h2>")
        elif line.startswith("#PARA#"):
            html_lines.append(f"<p>{line[len('#PARA#'):].strip()}</p>")
        else:
            html_lines.append(f"<p>{line}</p>")
    return '\n'.join(html_lines)

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

    prompt += "\n---\nהחזר טקסט בלבד, כל שורה מתחילה באחד מהבאים: #TITLE#, #SUBTITLE#, #PARA#. אין להחזיר תגי HTML, markdown, JSON או תגים אחרים."

    try:
        result = subprocess.run(
            ["ollama", "run", "aya-expanse:8b"],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        output = result.stdout.decode("utf-8").strip()
        print(f"🔍 DEBUG: Raw LLM output (first 200 chars): {output[:200]}...")
        # ניקוי הפלט מכל סוגי JSON ותגים
        cleaned_output = clean_llm_text(output)
        print(f"🔍 DEBUG: After clean_llm_text (first 200 chars): {cleaned_output[:200]}...")
        # הסרת תגים ועובדות אם עדיין קיימים
        cleaned_output = remove_json_artifacts(cleaned_output)
        print(f"🔍 DEBUG: After remove_json_artifacts (first 200 chars): {cleaned_output[:200]}...")
        # המרה מהפורמט המסומן ל-HTML
        cleaned_output = convert_tagged_text_to_html(cleaned_output)
        print(f"🔍 DEBUG: After convert_tagged_text_to_html (first 200 chars): {cleaned_output[:200]}...")
        print(f"🔍 DEBUG: Final output contains '<h': {'<h' in cleaned_output}")
        print(f"🔍 DEBUG: Final output contains '<p': {'<p' in cleaned_output}")
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
