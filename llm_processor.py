import pandas as pd
import subprocess
import json as pyjson

# קריאת מיפוי טיקרים לסקטורים
sector_map_df = pd.read_csv("/Users/kinghippo/Documents/rssFeed/marketBit/data/flat-ui__data-Thu Jun 19 2025.csv")
sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))

# פונקציה ליצירת הפרומפט המותאם
def generate_prompt(original_text: str, ticker: str, ticker_info=None):
    company = ticker_info.get("Security") if ticker_info else ""
    sector_name = ticker_info.get("GICS Sector") if ticker_info else ""

    prompt = f"""
אתה כותב דוח מוסדי עבור גוף מחקר פיננסי עצמאי בשם "Hippopotamus Research".

סקטור: **{sector_name}**, חברה: **{company}**.

**דרישות הדוח:**
- כתוב דוח מקצועי, מעמיק, עשיר, נרטיבי, ומובנה (בין 500 ל-700 מילים לפחות, או יותר אם הטקסט המקורי ארוך במיוחד).
- פתח כל נקודה, הוסף ניתוח, דוגמאות, הקשרים, מגמות, השוואות, מסקנות.
- סדר את הדוח: כותרת, תקציר, סעיפים (גורמים, ניתוח שוק, השוואה, סיכונים/הזדמנויות, "הנהלה", "מינוי בכיר", "הצהרת מנכ״ל/בכיר", "עסקת פנים", "תחזית הנהלה", "התפטרות/פיטורין",
        "אנליסטים", "תחזית מחיר יעד", "סיקור חדש", "שדרוג/הורדת דירוג", "קונצנזוס שוק", "פירמת השקעות",
        "משקיעים מוסדיים", "שותפות אסטרטגית", "מיזוג/רכישה", "הרחבת פעילות", "הנפקה/גיוס הון", "השקעה חדשה",
        "משפטי", "קנס", "תביעה ייצוגית", "פיקוח רגולטורי", "רגולציה אירופית", "חקירה ממשלתית", "תחרות הוגנת / הגבלים עסקיים",
        "AI", "חדשנות טכנולוגית", "מפת דרכים", "שבבים", "EUV", "בינה גנרטיבית", "שיתוף פעולה טכנולוגי", "פלטפורמות/תוכנה",
        "סנטימנט שוק", "תחזיות שוק", "ריבית / פד", "תנודתיות", "מקרו-כלכלה", "צפי אינפלציה", "שערי מטבע", "רוח גבית / רוח נגדית",
        "ממשל", "חקיקה / סנאט", "תמריצים פדרליים", "רגולציה סביבתית", "מדיניות מס", "וועדות ציבוריות",
        "אסון טבע", "מזג אוויר קיצוני", "פגיעה תפעולית", "אירועי ביטחון", "אירוע חריג",
        "פעילות שטח", "תחזוקה", "תקלות", "ביצועים תפעוליים" ), מסקנה.
- אל תסתפק בשכתוב – הוסף ערך, תובנות, עומק, קשר בין פסקאות, סיפוריות, עניין, מתח, או ביקורת נוקבת כשצריך.
- היה נועז: אם יש מקום לקטול מניה – עשה זאת בנימוק. אם יש סיפור מעניין – הדגש אותו. אל תחשוש להפעיל שיקול דעת.
- השתמש בכל המידע מהטקסט המקורי, אך אל תעתיק.
- כתוב עברית רהוטה, ברורה, עם מבנה מקצועי.
- ענה בפורמט JSON: {{"text": "...", "tags": [...]}}.
- importent !! -  תשתמש בכל הנתונים שאתה מקבל , אל תמציא נתונים חדשים אבל כן תפתח את הדימיון אצל הקוראים שלך עם כתיבה מרתקת ובוחנת .  אבל הנתונים חייבים להיות אמיתיים מדוייקים וכמובן עדכניים !!!!

**הטקסט המקורי:**
===
{original_text}
===
"""
    return prompt

def process_with_gemma(original_text, ticker, ticker_info=None):
    """
    Process the original text with the LLM (aya-expanse:8b) using Ollama, including extra ticker info for richer context.
    Returns a dict: {"text": ..., "tags": [...]}
    """
    # בנה פרומפט עשיר עם המידע הנוסף
    prompt = generate_prompt(original_text, ticker)
    if ticker_info:
        prompt += f"\n---\nמידע נוסף על החברה:\n"
        for k, v in ticker_info.items():
            prompt += f"{k}: {v}\n"
    prompt += "\n---\nענה בפורמט JSON: {\"text\": ..., \"tags\": [...]}\n"

    # קריאה ל-ollama (דוגמה בסיסית, אפשר להחליף/להרחיב)
    try:
        result = subprocess.run(
            ["ollama", "run", "aya-expanse:8b"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=120
        )
        output = result.stdout.decode("utf-8").strip()
        # נסה לחלץ JSON מהפלט
        try:
            first_brace = output.find('{')
            last_brace = output.rfind('}')
            if first_brace != -1 and last_brace != -1:
                json_str = output[first_brace:last_brace+1]
                return pyjson.loads(json_str)
        except Exception:
            pass
        # ניקוי markdown אם קיים
        if output.startswith('```json'):
            output = output[7:]
        if output.startswith('```'):
            output = output[3:]
        if output.endswith('```'):
            output = output[:-3]
        return {"text": output.strip(), "tags": []}
    except Exception as e:
        print(f"❌ Error running ollama: {e}")
        # fallback בסיסי
        return {"text": "שגיאה בעיבוד LLM: " + str(e), "tags": []}
