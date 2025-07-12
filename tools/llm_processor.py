import subprocess
import json
import os
import sys
from tools.logger import setup_logging
from tools.text_processing import clean_llm_text, remove_json_artifacts
from tools.ticker_data import get_ticker_info
from tools.config import get_max_tokens, LLM_MODEL_SETTINGS

logger = setup_logging()

def load_previous_titles(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        titles = [d.get("title", "") for d in data if d.get("title")]
        subtitles = [d.get("subtitle", "") for d in data if d.get("subtitle")]
        return titles[-25:], subtitles[-25:]
    except Exception as e:
        logger.warning(f"⚠️ Failed loading metadata file: {e}")
        return [], []

def generate_contextual_prompt(text_block: str, ticker_info=None, metadata_path=None):
    company = ticker_info.get("Security") if ticker_info else ""
    sector = ticker_info.get("GICS Sector") if ticker_info else ""
    titles, subtitles = load_previous_titles(metadata_path) if metadata_path else ([], [])

    prev_titles_str = "\n".join(f"- {t}" for t in titles)
    prev_subtitles_str = "\n".join(f"- {s}" for s in subtitles)

    return f"""
<system>
# ROLE:
אתה אנאליסט פיננסי  שעובד בגוף שנקרא - "Hippopotamus Research". 
שתפקידו לפענח טקסטים מעובדים של חדשות כלכליות ולבצע עליהם ניתוח רב-שכבתי מדויק.
המשימה שלך היא לפעול בשלבים סדורים ומובנים. אל תדלג על שום שלב. ענה בסגנון אנליטי-מוסדי, ללא קיצורים וללא חזרות מיותרות
לבסוף אתה תצטרך לערוך את הניתוח שלך למחקר כלכלי עם סגנון כתיבה עיתונאי.

# OBJECTIVE:
- ליצור כתבות כלכליות מקצועיות המיועדות לקהל בוגר ומתמצא בשווקים הפיננסיים
- התוכן שתקבל הוא נקודות קצרות המתויגות לפי סנטימנט [חיובי, נייטרלי, שלילי] - תזהה את הסנטימנט ותעבד אותו בהתאם
- סגנון הכתיבה: איות נכון בעברית, תרגום מדויק עם הקשר פיננסי, יכולת העברת מסר מקצועי, הרחבת נקודות לכתבה מקיפה המעמיקה בהסברים כדי לשפר את ההבנה והחוויה לקורא המקצועי
- כל כתבה חייבת להביא ערך אנליטי ומקצועי לקורא 

# STRUCTURE:
- #TITLE#: כותרת ראשית מעניינת וייחודית
- #SUBTITLE#: כותרת משנה ראשונה
- #PARA#: פסקאות גוף מפורטות ומסופרות

# WRITING STYLE:
- **סגנון כתיבה כלכלי מקצועי** - מיועד לקהל בוגר ומתמצא בשווקים הפיננסיים
- **אל תחזור על כותרות, ביטויים, או מבנה** מהכתבות הקודמות
- **השתמש במטאפורות ואנלוגיות מתאימות** - כאלה שמתאימות לעולם הפיננסים והעסקים
- **הימנע מכתיבה ילדותית או לא מקצועית** - בחר מילים ומטאפורות בוגרות ומתאימות
- **סגנון אנליטי מקצועי** עם זווית עסקית מרתקת
- ספק ניתוח מקצועי של הנתונים הקיימים בלבד  : 
* ספק את הסנטימנט!  תכלול אותו בכתבה בצורה שמשתלבת עם הטקסט  במידת הצורך, פצל את הסנטימנט לשכבות (לדוגמה: "חיובי בטווח הקצר, שלילי לטווח הבינוני")
*  מינוי הנהלה, רכישה/מיזוג, המלצת אנליסט, תביעה/חקירה, מוצר/טכנולוגיה חדשה, רגולציה, מכירות או ביצועי מניה. - ניתוח מבנה תוכן
*  גילוי ניגוד פנימי או חוסר עקביות לדוגמא -  האם יש סתירה בין הנתונים? בין הסנטימנט לבין העובדות? בין המלצות אנליסטים לאירוע עצמו?
* . חילוץ ישויות ומידע מספרי ישיר (NER פיננסי) 
*  הבנת מגמה סמויה או מתפתחת
* הסק אם מתגבשת מגמה ארוכת-טווח (לטובה או לרעה), או אם מדובר באירועים מבודדים.
* זיהוי טריגרים אסטרטגיים - הדגש חדשות שיכולות להוות  , Catalyst חיובי או Risk שלילי.  הערך את פוטנציאל השפעתם לפי ניסוח הידיעה ועוצמת המידע.
* סיכום אסטרטגי והערכת סנטימנט כללית 

- IMPORTENT!!  **צור נרטיב פיננסי זורם** - המשלב נתונים עם תובנות מקצועיות
- שלב מטאפורות רלוונטיות מהעולם הפיננסי
- כתוב בגוף שלישי, עם עומק מחשבתי והקשרים מקצועיים


# CONTENT REQUIREMENTS:
- **כתוב כתבה ארוכה ומקיפה** - המכסה את כל נקודות המפתח ללא יוצא מן הכלל
- **שמור על כל הנתונים** - מספרים, תאריכים, שמות, ציטוטים ומחירי יעד חייבים להישאר בדיוק כפי שהם
- **צור מבנה מקצועי** - התחל עם הכותרת הראשית, אחר כך כותרת משנה, ואז פסקאות מפורטות
- **מקוריות** - אל תחזור על כותרות או משפטים זהים, שמור על גיוון וחדשנות

# CRITICAL RULES:
- אסור לשנות אף נתון מספרי או מידע חשוב
- אסור לפספס אף נקודת מפתח - כל פיסת מידע חייבת להופיע בכתבה
- אסור להוסיף מידע חדש שלא היה במקור
- הכתבה חייבת להיות נאמנה למידע המקורי אך מסוגננת בכתיבה

# LANGUAGE GUIDELINES:
- אל תתרגם את הטקסט אלא תכתוב אותו בעברית . תרגום טקסט לפעמים לא משתייך להקשר . 
- חובה עלייך לשים לב לזהות יישויות בטקסט  , ולא לתרגם אותם לעברית אלא להשאיר באנגלית . 
לדוגמא : שם החברה , שם המנייה , שם בית העסק ,  

# AVOID REPETITION:
## כותרות קודמות:
{prev_titles_str}

## תתי-כותרות קודמות:
{prev_subtitles_str}

# CONTEXT:
🔎 Company: {company}
📂 Sector: {sector}

# RAW DATA:
{text_block}

⚠️ חשוב מאוד: החזר טקסט בלבד, כל שורה מתחילה באחד מהבאים: #TITLE#, #SUBTITLE#, #PARA#. אין להחזיר תגי HTML, markdown, JSON או תגים אחרים.
</system>
"""

def process_with_contextual_prompt(text_block, ticker_info=None, metadata_path=None, max_tokens=None, article_type="default"):
    """
    Process text with LLM and control output length
    
    Args:
        text_block: The input text to process
        ticker_info: Ticker metadata information
        metadata_path: Path to metadata file for avoiding repetition
        max_tokens: Maximum number of tokens for output (if None, uses default from config)
        article_type: Type of article ("short", "default", "long") for token limit
    """
    # Use config default if max_tokens not specified
    if max_tokens is None:
        max_tokens = get_max_tokens(article_type)
    
    prompt = generate_contextual_prompt(text_block, ticker_info, metadata_path)
    
    # Add token limit instruction to prompt
    prompt += f"\n\n⚠️ הגבלת אורך: הכתבה חייבת להיות באורך של עד {max_tokens} מילים. אל תחרוג מהגבלה זו."
    
    try:
        result = subprocess.run(
            ["ollama", "run", LLM_MODEL_SETTINGS["model_name"]],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        output = result.stdout.decode("utf-8").strip()
        logger.debug(f"[LLM Output Sample]: {output[:200]}")

        cleaned = clean_llm_text(output)
        cleaned = remove_json_artifacts(cleaned)
        
        # Count words and truncate if necessary
        word_count = len(cleaned.split())
        if word_count > max_tokens:
            logger.warning(f"⚠️ Output truncated: {word_count} words > {max_tokens} limit")
            words = cleaned.split()[:max_tokens]
            cleaned = " ".join(words)
            # Try to end at a complete sentence
            last_period = cleaned.rfind('.')
            if last_period > len(cleaned) * 0.8:  # If period is in last 20% of text
                cleaned = cleaned[:last_period + 1]
        
        logger.info(f"📊 Output length: {len(cleaned.split())} words")
        return cleaned

    except Exception as e:
        logger.error(f"❌ Error running ollama: {e}")
        return f"שגיאה: {e}"

def process_with_length_control(text_block, ticker_info=None, metadata_path=None, target_length="default"):
    """
    Process text with specific length control
    
    Args:
        text_block: The input text to process
        ticker_info: Ticker metadata information
        metadata_path: Path to metadata file for avoiding repetition
        target_length: Target length ("short", "default", "long", or number of words)
    """
    if isinstance(target_length, str):
        max_tokens = get_max_tokens(target_length)
    else:
        max_tokens = target_length
    
    logger.info(f"🎯 Target length: {max_tokens} words")
    return process_with_contextual_prompt(
        text_block=text_block,
        ticker_info=ticker_info,
        metadata_path=metadata_path,
        max_tokens=max_tokens
    )
