import requests
import json

def process_with_gemma(original_text, ticker):
    """
    Process text with Ollama using aya-expanse:8b model
    """
    
    prompt = f"""אתה כותב מטעם גוף מחקר פיננסי עצמאי בשם "Hippopotamus Research".

המטרה: לנתח תנועת מניה יומית באופן סיבתי, מקצועי ואמין.  
הכתיבה אינה שיווקית, אינה רגשית ואינה כללית – אלא אנליטית, מדויקת, ומבוססת תצפיות.  
כל תנועה מוסברת בקפדנות דרך מפת ניתוח הכוללת: הצהרות הנהלה, מוסדות, דיבידנד, רגולציה, מגמות סקטוריאליות, משפטים, שיח ציבורי, ומידע פנים.

מקורות המידע: MarketBeat, Seeking Alpha, Yahoo Finance, Benzinga, TipRanks

🔸 **כתיבה בסגנון מוסדי בכיר** – כאילו אתה מנהל מחלקת מחקר בגוף השקעות ענק.  
🔸 **סגנון**: רהוט, מחולק לפסקאות, חכם, חד, נקי מבאזזים.  
🔸 **קשר פנימי**: כל פסקה מחוברת רעיונית לפסקה שאחריה, כך שהקריאה זורמת ולא אוסף של נקודות.

**כל פסקה צריכה:**
- לעסוק בקטגוריה אחת מרכזית (לדוגמה: הנהלה, מוסדות, רגולציה, ציבור).
- להכיל משפטי עומק ולא רק תיאור.
- להמיר מידע יבש לנרטיב אינפורמטיבי מעניין.
- לא להמציא עובדות – רק להסביר לעומק את הנתונים שנמסרו.

**סיום הדוח:**  
לסכם את המצב תוך ציון איזון בין כוחות חיוביים (כגון תזרים, צמיחה, מוסדות) לכוחות מאזנים או שליליים (משפטים, סביבה, רגולציה), ולציין שנדרש המשך מעקב.

נתח את המידע הבא עבור {ticker}:

{original_text}"""
    
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
            chunk_count = 0
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            full_response += data['response']
                            chunk_count += 1
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            print(f"📝 Received {chunk_count} chunks from Ollama")
            print(f"📝 Response length: {len(full_response)} characters")
            print(f"📝 Original length: {len(original_text)} characters")
            
            # Check if the response is different from original
            if full_response.strip() == original_text.strip():
                print("⚠️ Model returned original text - using fallback")
                return fallback_processing(original_text, ticker)
            
            # Check if response is too short (might be incomplete)
            if len(full_response) < len(original_text) * 0.5:
                print("⚠️ Response too short - using fallback")
                return fallback_processing(original_text, ticker)
            
            # Check if response contains the original text (might be just echoing)
            if original_text in full_response:
                print("⚠️ Response contains original text - using fallback")
                return fallback_processing(original_text, ticker)
            
            print("✅ Successfully processed with Ollama")
            return full_response
            
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
    Fallback processing if Ollama is not available
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
            if line.startswith("גורמים עיקריים"):
                processed_lines.append("## גורמים עיקריים")
            elif line.startswith("פייפר") or line.startswith("רות'") or line.startswith("קליטה"):
                processed_lines.append(f"• {line}")
            else:
                processed_lines.append(line)
    
    # Add institutional conclusion
    processed_lines.append("")
    processed_lines.append("## סיכום וניתוח")
    processed_lines.append("")
    processed_lines.append("הדוח הנוכחי מציג ניתוח סיבתי של תנועות המניה. נדרש המשך מעקב אחר התפתחויות עתידיות.")
    
    result = '\n'.join(processed_lines)
    print(f"📝 Fallback processing complete: {len(result)} characters")
    return result
