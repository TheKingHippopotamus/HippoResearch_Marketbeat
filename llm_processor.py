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
3. **צור מבנה מקצועי עם HTML** - כותרת ראשית עם <h1>, כותרות משנה עם <h2>, פסקאות עם <p>
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

✍️ מבנה הכתבה עם HTML:
- <h1>כותרת ראשית מעניינת ומעוררת סקרנות</h1>
- <h2>כותרת משנה ראשונה - מרתקת</h2>
- <p>פסקה ראשונה עם תוכן מעניין וזורם...</p>
- <h2>כותרת משנה שנייה - מעוררת מחשבה</h2>
- <p>פסקה שנייה עם תוכן מרתק...</p>
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
        
        print(f"🔍 DEBUG: Raw LLM output (first 200 chars): {output[:200]}...")
        print(f"🔍 DEBUG: Raw LLM output contains '##': {'##' in output}")
        print(f"🔍 DEBUG: Raw LLM output contains '<h': {'<h' in output}")

        # ניקוי הפלט מכל סוגי JSON ותגים
        cleaned_output = clean_llm_text(output)
        print(f"🔍 DEBUG: After clean_llm_text (first 200 chars): {cleaned_output[:200]}...")
        
        # הסרת תגים ועובדות אם עדיין קיימים
        cleaned_output = remove_json_artifacts(cleaned_output)
        print(f"🔍 DEBUG: After remove_json_artifacts (first 200 chars): {cleaned_output[:200]}...")
        
        # המרת markdown ל-HTML אם נדרש
        cleaned_output = convert_markdown_to_html(cleaned_output)
        print(f"🔍 DEBUG: After convert_markdown_to_html (first 200 chars): {cleaned_output[:200]}...")
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

def convert_markdown_to_html(text):
    """Convert markdown formatting to proper HTML tags with short paragraphs and <br> for readability, including links and images. לא ייווצרו תגי <h1> כפולים ולא divים מיותרים."""
    if not text:
        return text
    text = text.strip()

    # טיפול מיוחד ב-## שמופיעים בתוך הטקסט (לא בתחילת שורה)
    if '##' in text:
        parts = text.split('##')
        if len(parts) > 1:
            result_parts = []
            # החלק הראשון - כותרת ראשית (הסרת # אם יש)
            if parts[0].strip():
                title = parts[0].strip()
                if title.startswith('# '):
                    title = title[2:].strip()
                elif title.startswith('#'):
                    title = title[1:].strip()
                # הסר תגי h1 מיותרים
                title = re.sub(r'<h1>(.*?)</h1>', r'\1', title)
                result_parts.append(f'<h1>{title}</h1>')
            for i, part in enumerate(parts[1:], 1):
                part = part.strip()
                if part:
                    lines = part.split('\n', 1)
                    if len(lines) > 1:
                        subtitle = lines[0].strip()
                        content = lines[1].strip()
                        # הסר תגי h2 מיותרים
                        subtitle = re.sub(r'<h2>(.*?)</h2>', r'\1', subtitle)
                        result_parts.append(f'<h2>{subtitle}</h2>')
                        if content:
                            result_parts.append(content)
                    else:
                        subtitle = re.sub(r'<h2>(.*?)</h2>', r'\1', part)
                        result_parts.append(f'<h2>{subtitle}</h2>')
            text = '\n'.join(result_parts)

    # כותרות markdown רגילות
    text = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)

    # bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

    # לינקים: [טקסט](url) => <a href="url" target="_blank">טקסט</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    # תמונות: ![alt](url) => <img src="url" alt="alt">
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)

    # הסר עטיפות כפולות של כותרות (למשל <h1><h1>...</h1></h1>)
    text = re.sub(r'<h1>\s*<h1>(.*?)</h1>\s*</h1>', r'<h1>\1</h1>', text, flags=re.DOTALL)
    text = re.sub(r'<h2>\s*<h2>(.*?)</h2>\s*</h2>', r'<h2>\1</h2>', text, flags=re.DOTALL)
    text = re.sub(r'<h3>\s*<h3>(.*?)</h3>\s*</h3>', r'<h3>\1</h3>', text, flags=re.DOTALL)

    # פיצול לשורות וטיפול נפרד בכותרות ופסקאות
    lines = text.split('\n')
    result_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # אם זו כותרת HTML, הוסף אותה כמו שהיא
        if re.match(r'<h[1-4]>.*</h[1-4]>', line):
            result_lines.append(line)
        else:
            # אם זו פסקה רגילה, עטוף ב-<p>
            result_lines.append(f'<p>{line}</p>')
    # חיבור עם <br> בין אלמנטים
    html = '<br>\n'.join(result_lines)
    # ניקוי נוסף - הסרת <p> ריקים
    html = re.sub(r'<p>\s*</p>', '', html)
    return html

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
