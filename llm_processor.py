import pandas as pd
import subprocess
import json as pyjson

# קריאת מיפוי טיקרים לסקטורים
sector_map_df = pd.read_csv("/Users/kinghippo/Documents/rssFeed/marketBit/data/flat-ui__data-Thu Jun 19 2025.csv")
sector_map = dict(zip(sector_map_df['Tickers'], sector_map_df['GICS Sector']))

# הגדרת דמויות מחקר לפי סקטורים
PERSONAS = {
    "Technology": {
        "name": "המהנדס",
        "description": "מומחה טכנולוגיה וחדשנות, מתמקד בהנדסה, שבבים, AI ותוכנה.",
        "boost": "התמקד בממדים טכנולוגיים, חדשנות, פלטפורמות, מהפכות AI, ושיקולי תשתית."
    },
    "Health Care": {
        "name": "האנליסט הקליני",
        "description": "ביוטכנולוגיה, אישור FDA, סיכונים קליניים והשקעות הון רפואי.",
        "boost": "נתח את רגולציית הבריאות, ניסויים קליניים, תרופות פורצות דרך והשפעות מוסדיות."
    },
    "Financials": {
        "name": "המנתח הפיננסי",
        "description": "בנקאות, תיווך, ריבית, תשואות והערכת שווי.",
        "boost": "ספק ניתוח פיננסי עמוק של מנגנוני השוק, נזילות, רגולציה פיננסית ותמחור סיכונים."
    },
    "Energy": {
        "name": "המקרו-אנליסט",
        "description": "מומחה לתחום האנרגיה: נפט, גז, אנרגיה ירוקה, רגולציה סביבתית ותחזיות גלובליות.",
        "boost": "כלול ניתוח מגמות עולמיות באנרגיה, רגולציה, ביקוש-תפוקה וסיכונים גיאופוליטיים."
    },
    "Utilities": {
        "name": "הרגולטור",
        "description": "מתמקד באנרגיה ציבורית, חשמל, תשתיות, חקיקה והשפעות סביבתיות.",
        "boost": "סקר את מבנה הרגולציה, תמחור, שיקולי תשתית והשפעות של מזג אוויר או חקיקה."
    },
    "Consumer Staples": {
        "name": "המנתח ההתנהגותי",
        "description": "בוחן צריכה בסיסית, תחזיות רגישות מחירים, וביקושים מגזריים.",
        "boost": "הדגש את סנטימנט הצרכן, השפעות מאקרו, והתמודדות עם תנאי שוק מאתגרים."
    },
    "default": {
        "name": "האסטרטג הראשי",
        "description": "מוביל מחקר כוללני הבוחן שילובים של כוחות שוק, תחרות, רגולציה וציפיות.",
        "boost": "הבן את הקשר בין מוסדות, הנהלה, תחזיות מאקרו וסנטימנט למשקיעים ארוכי טווח."
    }
}

# פונקציה לקבלת דמות לפי טיקר
def get_persona_by_ticker(ticker: str):
    sector = sector_map.get(ticker.upper(), None)
    sector_key = sector if isinstance(sector, str) and sector else "default"
    persona = PERSONAS.get(sector_key, PERSONAS["default"])
    return persona, sector or "Unknown"

# פונקציה ליצירת הפרומפט המותאם
def generate_prompt(original_text: str, ticker: str):
    persona, sector = get_persona_by_ticker(ticker)

    prompt = f"""
אתה כותב מטעם גוף מחקר פיננסי עצמאי בשם "Hippopotamus Research".

תפקידך הוא **{persona["name"]}**, הפועל בתחום: **{sector}**
({persona["description"]})

המטרה: לנתח תנועת מניה יומית באופן סיבתי, מקצועי ואמין.  
🔹 הכתיבה אינה שיווקית, אינה רגשית ואינה כללית – אלא אנליטית, רהוטה, ומבוססת תצפיות.
🔹 כל תנועה מוסברת בקפדנות דרך מפת ניתוח הכוללת: הנהלה, מוסדות, דיבידנד, רגולציה, סקטור, משפטים, שיח ציבורי, מידע פנים ועוד.
🔹 אין להחסיר אף פרט מהמידע שניתן.
🔹 חובה לנסח מחדש, להוסיף עומק, קשר בין הפסקאות, ולבנות נרטיב אחיד ואינטליגנטי.

⬅️ **חיזוק ספציפי לתחום שלך:** {persona["boost"]}

❗ **אסור להעתיק את הטקסט המקורי, אך חובה להשתמש בו כולו.**
❗ **אין להוסיף פרטים שאינם קיימים.**

אנא נתח את המידע הבא עבור המניה: {ticker}
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
        output = result.stdout.decode("utf-8")
        # נסה לחלץ JSON מהפלט
        try:
            first_brace = output.find('{')
            last_brace = output.rfind('}')
            if first_brace != -1 and last_brace != -1:
                json_str = output[first_brace:last_brace+1]
                return pyjson.loads(json_str)
        except Exception:
            pass
        # אם לא הצליח, החזר טקסט גולמי
        return {"text": output.strip(), "tags": []}
    except Exception as e:
        print(f"❌ Error running ollama: {e}")
        # fallback בסיסי
        return {"text": "שגיאה בעיבוד LLM: " + str(e), "tags": []}
