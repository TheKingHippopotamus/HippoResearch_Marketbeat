import pandas as pd
import subprocess
import json as pyjson

# קריאת מיפוי טיקרים לסקטורים
sector_map_df = pd.read_csv("/Users/kinghippo/Documents/rssFeed/marketBit/data/flat-ui__data-Thu Jun 19 2025.csv")
sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))

# פרומפט מעודכן לפי דרישות המשתמש – שכתוב בלבד, ללא פרשנות
def generate_prompt(original_text: str, ticker_info=None):
    company = ticker_info.get("Security") if ticker_info else ""
    sector_name = ticker_info.get("GICS Sector") if ticker_info else ""

    prompt = f"""
אתה כותב כתבה עבור גוף מחקר עצמאי בשם "Hippopotamus Research".

🎯 מטרתך:
להנגיש את המידע שנמסר בצורה ברורה, מדויקת, נרטיבית וזורמת – מבלי לשנות אף פרט עובדתי.

📌 מה שקיבלת:
רשימת נקודות עיקריות (key points) על חברה כלשהי, מתוך מקורות חדשותיים מהימנים.

📌 מה עליך לעשות:
- להפוך את הנקודות האלו לכתבה מקצועית ונעימה לקריאה, עם חיבור לוגי בין הפסקאות.
- שמור על **כל הנתונים** בדיוק כפי שהם – כולל מספרים, שמות, ציטוטים, תאריכים ומחירי יעד.
- מותר לך לערוך רק את **אופן ההצגה**: לנסח מחדש, להוסיף משפטי קישור, ליצור רצף נרטיבי, ולבנות פסקאות.
- אל תוסיף שום מידע חדש.
- אל תבצע ניתוח, תחזיות, או הערכות משלך.
- אל תשמיט אף נקודה שהוזכרה בטקסט המקורי.

✍️ כתוב בסגנון של כתבה כלכלית מקצועית ונגישה לציבור.


🔎 חברה: {company}
📂 סקטור: {sector_name}

**הטקסט המקורי (Key Points):**
===
{original_text}
===
"""
    return prompt

# הפעלת מודל Ollama עם prompt מעודכן
def process_with_gemma(original_text, ticker_info=None):
    """
    Process the original text with the LLM (aya-expanse:8b) using Ollama, using ONLY rephrasing and restructuring rules.
    Returns the processed text as a string.
    """
    prompt = generate_prompt(original_text, ticker_info)

    if ticker_info:
        prompt += "\n---\nמידע נוסף על החברה:\n"
        for k, v in ticker_info.items():
            prompt += f"{k}: {v}\n"

    prompt += "\n---\nענה בפורמט JSON: {\"text\": ..., \"tags\": [...]}\n"

    try:
        result = subprocess.run(
            ["ollama", "run", "aya-expanse:8b"],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        output = result.stdout.decode("utf-8").strip()

        # ניסיון לחילוץ JSON מתוך הפלט
        try:
            first_brace = output.find('{')
            last_brace = output.rfind('}')
            if first_brace != -1 and last_brace != -1:
                json_str = output[first_brace:last_brace+1]
                parsed_json = pyjson.loads(json_str)
                # החזר רק את הטקסט, לא את ה-JSON המלא
                return parsed_json.get("text", output.strip())
        except Exception:
            pass

        # ניקוי תווי markdown אם קיימים
        if output.startswith('```json'):
            output = output[7:]
        if output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]

        return output.strip()

    except Exception as e:
        print(f"❌ Error running ollama: {e}")
        return "שגיאה בעיבוד LLM: " + str(e)
