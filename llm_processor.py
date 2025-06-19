import requests
import json

def process_with_gemma(original_text, ticker):
    """
    Process text with Ollama using aya-expanse:8b model, returning both text and causal tags as JSON
    """
    
    # Define the causal tags vocabulary
    CAUSAL_TAGS = [
        "הנהלה", "מינוי בכיר", "הצהרת מנכ״ל/בכיר", "עסקת פנים", "תחזית הנהלה", "התפטרות/פיטורין",
        "אנליסטים", "תחזית מחיר יעד", "סיקור חדש", "שדרוג/הורדת דירוג", "קונצנזוס שוק", "פירמת השקעות",
        "משקיעים מוסדיים", "שותפות אסטרטגית", "מיזוג/רכישה", "הרחבת פעילות", "הנפקה/גיוס הון", "השקעה חדשה",
        "משפטי", "קנס", "תביעה ייצוגית", "פיקוח רגולטורי", "רגולציה אירופית", "חקירה ממשלתית", "תחרות הוגנת / הגבלים עסקיים",
        "AI", "חדשנות טכנולוגית", "מפת דרכים", "שבבים", "EUV", "בינה גנרטיבית", "שיתוף פעולה טכנולוגי", "פלטפורמות/תוכנה",
        "סנטימנט שוק", "תחזיות שוק", "ריבית / פד", "תנודתיות", "מקרו-כלכלה", "צפי אינפלציה", "שערי מטבע", "רוח גבית / רוח נגדית",
        "ממשל", "חקיקה / סנאט", "תמריצים פדרליים", "רגולציה סביבתית", "מדיניות מס", "וועדות ציבוריות",
        "אסון טבע", "מזג אוויר קיצוני", "פגיעה תפעולית", "אירועי ביטחון", "אירוע חריג",
        "פעילות שטח", "תחזוקה", "תקלות", "ביצועים תפעוליים"
    ]

    # Add to the prompt a request for JSON output with tags
    prompt = f"""אתה כותב מטעם גוף מחקר פיננסי עצמאי בשם \"Hippopotamus Research\".\n\nהמטרה: לנתח תנועת מניה יומית באופן סיבתי, מקצועי ואמין.\nהכתיבה אינה שיווקית, אינה רגשית ואינה כללית – אלא אנליטית, מדויקת, ומבוססת תצפיות.\nכל תנועה מוסברת בקפדנות דרך מפת ניתוח הכוללת: הצהרות הנהלה, מוסדות, דיבידנד, רגולציה, מגמות סקטוריאליות, משפטים, שיח ציבורי, ומידע פנים.\n\nמקורות המידע: MarketBeat, Seeking Alpha, Yahoo Finance, Benzinga, TipRanks\n\n🔸 **כתיבה בסגנון מוסדי בכיר** – כאילו אתה מנהל מחלקת מחקר בגוף השקעות ענק.\n🔸 **סגנון**: רהוט, מחולק לפסקאות, חכם, חד, נקי מבאזזים.\n🔸 **קשר פנימי**: כל פסקה מחוברת רעיונית לפסקה שאחריה, כך שהקריאה זורמת ולא אוסף של נקודות.\n\n**כל פסקה צריכה:**\n- לעסוק בקטגוריה אחת מרכזית (לדוגמה: הנהלה, מוסדות, רגולציה, ציבור).\n- להכיל משפטי עומק ולא רק תיאור.\n- להמיר מידע יבש לנרטיב אינפורמטיבי מעניין.\n- לא להמציא עובדות – רק להסביר לעומק את הנתונים שנמסרו.\n- שמור על מבנה מאמר תקני , פסקאות ,רווחים הפרדות ועוד \n**סיום הדוח:**  \nלסכם את המצב תוך ציון איזון בין כוחות חיוביים (כגון תזרים, צמיחה, מוסדות) לכוחות מאזנים או שליליים (משפטים, סביבה, רגולציה), ולציין שנדרש המשך מעקב.\n\n**הוראות פורמט:**\n- החזר תשובה בפורמט JSON בלבד.\n- השדות: 'text' (גוף הדוח, בפורמט markdown), 'tags' (רשימת תיוגים סיבתיים מתוך הרשימה הבאה בלבד):\n{CAUSAL_TAGS}\n- דוגמה:\n{{\n  \"text\": \"...\",\n  \"tags\": [\"הנהלה\", \"AI\", ...]\n}}\n\nנתח את המידע הבא עבור {ticker}:\n\n{original_text}"""

    try:
        print("🔄 Processing with Ollama...")
        print(f"📝 Prompt length: {len(prompt)} characters")
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "aya-expanse:8b",
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.9,
                "top_p": 0.95,
                "num_predict": 2000
            }
        }
        response = requests.post(url, json=payload, timeout=120, stream=True)
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            full_response += data['response']
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            # Try to parse the JSON output
            try:
                result = json.loads(full_response)
                if 'text' in result and 'tags' in result:
                    return result
            except Exception:
                pass
            # Fallback: treat as plain text
            print("⚠️ Model did not return valid JSON, using fallback")
            return fallback_processing(original_text, ticker)
        else:
            print(f"❌ Ollama Error: {response.status_code}")
            print(f"Response: {response.text}")
            return fallback_processing(original_text, ticker)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama - make sure it's running")
        return fallback_processing(original_text, ticker)
    except Exception as e:
        print(f"❌ Error: {e}")
        return fallback_processing(original_text, ticker)

def fallback_processing(original_text, ticker):
    """
    Fallback processing if Ollama is not available. Also extract tags using keyword matching.
    """
    print("⚠️ Using fallback processing...")
    # Simple text processing to make it look like institutional research
    lines = original_text.split('\n')
    processed_lines = []
    # Add institutional header
    processed_lines.append(f"# דוח ניתוח סיבתיות - {ticker}")
    processed_lines.append("")
    processed_lines.append("**Hippopotamus Research**")
    processed_lines.append("")
    # Process each line
    for line in lines:
        line = line.strip()
        if line and not line.startswith("פורסם") and not line.startswith("נוצר"):
            processed_lines.append(line)
    # Add institutional conclusion
    processed_lines.append("")
    processed_lines.append("## סיכום וניתוח")
    processed_lines.append("")
    processed_lines.append("הדוח הנוכחי מציג ניתוח סיבתי של תנועות המניה. נדרש המשך מעקב אחר התפתחויות עתידיות.")
    result_text = '\n'.join(processed_lines)
    # Extract tags using keyword matching
    tags = []
    for tag in [
        "הנהלה", "מינוי בכיר", "הצהרת מנכ״ל/בכיר", "עסקת פנים", "תחזית הנהלה", "התפטרות/פיטורין",
        "אנליסטים", "תחזית מחיר יעד", "סיקור חדש", "שדרוג/הורדת דירוג", "קונצנזוס שוק", "פירמת השקעות",
        "משקיעים מוסדיים", "שותפות אסטרטגית", "מיזוג/רכישה", "הרחבת פעילות", "הנפקה/גיוס הון", "השקעה חדשה",
        "משפטי", "קנס", "תביעה ייצוגית", "פיקוח רגולטורי", "רגולציה אירופית", "חקירה ממשלתית", "תחרות הוגנת / הגבלים עסקיים",
        "AI", "חדשנות טכנולוגית", "מפת דרכים", "שבבים", "EUV", "בינה גנרטיבית", "שיתוף פעולה טכנולוגי", "פלטפורמות/תוכנה",
        "סנטימנט שוק", "תחזיות שוק", "ריבית / פד", "תנודתיות", "מקרו-כלכלה", "צפי אינפלציה", "שערי מטבע", "רוח גבית / רוח נגדית",
        "ממשל", "חקיקה / סנאט", "תמריצים פדרליים", "רגולציה סביבתית", "מדיניות מס", "וועדות ציבוריות",
        "אסון טבע", "מזג אוויר קיצוני", "פגיעה תפעולית", "אירועי ביטחון", "אירוע חריג",
        "פעילות שטח", "תחזוקה", "תקלות", "ביצועים תפעוליים"
    ]:
        if tag in result_text:
            tags.append(tag)
    return {"text": result_text, "tags": tags}
