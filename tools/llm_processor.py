import os
from tools.logger import setup_logging
from tools.config import get_max_tokens, LLM_MODEL_SETTINGS, LLM_OUTPUT_SETTINGS
from tools.text_processing import fix_hebrew_grammar_errors, convert_tagged_text_to_html
from tools.entity_analyzer import analyze_text_for_llm_with_cache
import re
import requests
import json

logger = setup_logging()

HEBREW_VOCAB_PATH = os.path.join(os.path.dirname(__file__), '../data/hebrew_vocabulary.json')

def load_hebrew_vocabulary(context_text=None, max_terms=25, max_length=1000):
    """Load only relevant Hebrew vocabulary terms for prompt enrichment."""
    try:
        with open(HEBREW_VOCAB_PATH, encoding='utf-8') as f:
            vocab = json.load(f)
        financial_terms = vocab.get('financial_terms', {})
        found = []
        if context_text:
            for eng, heb in financial_terms.items():
                if eng in context_text:
                    found.append(f"{eng} → {heb}")
                if len(found) >= max_terms:
                    break
        # If not enough found, add some common terms
        if len(found) < 5:
            for eng, heb in list(financial_terms.items())[:max_terms-len(found)]:
                if f"{eng} → {heb}" not in found:
                    found.append(f"{eng} → {heb}")
        snippet = "\n".join(found)
        if len(snippet) > max_length:
            snippet = snippet[:max_length-3] + "..."
        return snippet
    except Exception as e:
        return ""


def parse_sentiment_blocks(text):
    """
    מחלק טקסט לבלוקים לפי סנטימנט (חיובי, נייטרלי, שלילי)
    מחזיר dict: {'positive': [...], 'neutral': [...], 'negative': [...]}
    """
    blocks = {'positive': [], 'neutral': [], 'negative': []}
    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('Positive Sentiment:'):
            current = 'positive'
            continue
        elif line.startswith('Neutral Sentiment:'):
            current = 'neutral'
            continue
        elif line.startswith('Negative Sentiment:'):
            current = 'negative'
            continue
        elif line.startswith('Posted') or line.startswith('AI Generated') or not line:
            continue
        if current:
            blocks[current].append(line)
    return blocks

def extract_entities(text):
    """
    
    מזהה ישויות באנגלית (פשוט: מילים גדולות/סימני מסחר/סימול) לשימור בתרגום
    """
    # דוגמה פשוטה: כל מילה באותיות גדולות או עם נקודה/סוגריים
    pattern = re.compile(r'\b([A-Z][A-Za-z0-9&.()\-]+)\b')
    return set(pattern.findall(text))

def hebrewize(text, entities=None):
    """
    ממיר טקסט לאנגלית בשפה עברית (פשוט: תרגום מילים בסיסי, שמירה על ישויות באנגלית)
    """
    if not text:
        return ''
    # שמור על ישויות באנגלית
    if entities:
        for ent in entities:
            text = re.sub(rf'\b{re.escape(ent)}\b', f'[[{ent}]]', text)
    # תרגום בסיסי (פייק): החלף מילים נפוצות
    replacements = {
        'shares': 'מניה',
        'stock': 'מניה',
        'price': 'מחיר',
        'growth': 'צמיחה',
        'decline': 'ירידה',
        'increase': 'עלייה',
        'decrease': 'ירידה',
        'investor': 'משקיע',
        'investors': 'משקיעים',
        'company': 'חברה',
        'earnings': 'רווחים',
        'loss': 'הפסד',
        'positive': 'חיובי',
        'negative': 'שלילי',
        'neutral': 'נייטרלי',
        'report': 'דוח',
        'target': 'יעד',
        'forecast': 'תחזית',
        'analyst': 'אנליסט',
        'analysts': 'אנליסטים',
        'agreement': 'הסכם',
        'deal': 'עסקה',
        'pipeline': 'צנרת',
        'AI': 'בינה מלאכותית',
        'innovation': 'חדשנות',
        'risk': 'סיכון',
        'opportunity': 'הזדמנות',
        'market': 'שוק',
        'revenue': 'הכנסה',
        'profit': 'רווח',
        'losses': 'הפסדים',
        'buy': 'קנייה',
        'sell': 'מכירה',
        'hold': 'החזקה',
        'rating': 'דירוג',
        'outlook': 'תחזית',
        'trend': 'מגמה',
        'bullish': 'שורי',
        'bearish': 'דובי',
        'dividend': 'דיבידנד',
        'partnership': 'שיתוף פעולה',
        'acquisition': 'רכישה',
        'merger': 'מיזוג',
        'lawsuit': 'תביעה',
        'legal': 'משפטי',
        'court': 'בית משפט',
        'CEO': 'מנכ"ל',
        'CFO': 'סמנכ"ל כספים',
        'Q2': 'רבעון שני',
        'Q3': 'רבעון שלישי',
        'Q4': 'רבעון רביעי',
        'Q1': 'רבעון ראשון',
    }
    for en, he in replacements.items():
        text = re.sub(rf'\b{en}\b', he, text, flags=re.IGNORECASE)
    # החזר את הישויות המקוריות
    if entities:
        for ent in entities:
            text = text.replace(f'[[{ent}]]', ent)
    # סימון RTL
    text = f'<span dir="rtl">{text}</span>'
    return fix_hebrew_grammar_errors(text)

def build_hebrew_article(title, sentiment_blocks, entities=None, as_html=True):
    """
    בונה HTML של מאמר בעברית עם שלושה בלוקים, או טקסט בלבד (אם as_html=False)
    """
    sentiment_titles = {
        'positive': 'נקודות חיוביות',
        'neutral': 'נקודות נייטרליות',
        'negative': 'נקודות שליליות',
    }
    if as_html:
        html = [f'<h1 dir="rtl" style="text-align:right">{title}</h1>']
        for key in ['positive', 'neutral', 'negative']:
            if sentiment_blocks[key]:
                html.append(f'<h2 dir="rtl" style="text-align:right">{sentiment_titles[key]}</h2>')
                html.append('<ul dir="rtl" style="text-align:right">')
                for sent in sentiment_blocks[key]:
                    heb = hebrewize(sent, entities)
                    html.append(f'<li>{heb}</li>')
                html.append('</ul>')
        return '\n'.join(html)
    else:
        # טקסט בלבד
        lines = [title]
        for key in ['positive', 'neutral', 'negative']:
            if sentiment_blocks[key]:
                lines.append(f'--- {sentiment_titles[key]} ---')
                for sent in sentiment_blocks[key]:
                    heb = hebrewize(sent, entities)
                    lines.append(f'- {heb}')
        return '\n'.join(lines)

def wrap_full_html(body_html, title="MarketBit מאמר בעברית"): 
    """
    עוטף את גוף המאמר ב-html מלא כולל head, RTL, meta וכו'.
    """
    return f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body {{ direction: rtl; text-align: right; font-family: Arial, sans-serif; }}</style>
</head>
<body>
{body_html}
</body>
</html>'''

def process_article_file(filepath, output_html_path=None, ticker=None, as_html=True):
    """
    קורא קובץ original, מפיק בלוקים, ממיר לעברית, בונה HTML מלא או טקסט בלבד, שומר/מחזיר פלט.
    :param filepath: נתיב לקובץ original
    :param output_html_path: נתיב לשמירת HTML (לא חובה)
    :param ticker: סימול (לא חובה)
    :param as_html: האם להחזיר HTML מלא (True) או טקסט בלבד (False)
    :return: מחרוזת HTML או טקסט
    """
    if not os.path.exists(filepath):
        logger.error(f"❌ File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    if not text.strip():
        logger.error(f"❌ File is empty: {filepath}")
        raise ValueError(f"File is empty: {filepath}")
    logger.info(f"🔍 Processing file: {filepath}")
    # הפקת ישויות (אפשרי)
    entities_context = None
    if ticker:
        try:
            entities_context = analyze_text_for_llm_with_cache(text, ticker)
        except Exception as e:
            logger.warning(f"Entity analysis failed: {e}")
    # כותרת ראשית
    first_line = text.split('\n', 1)[0].strip()
    entities = extract_entities(text)
    title = hebrewize(first_line, entities)
    # חלוקה לבלוקים
    sentiment_blocks = parse_sentiment_blocks(text)
    # בניית גוף המאמר
    body = build_hebrew_article(title, sentiment_blocks, entities, as_html=as_html)
    if as_html:
        html = wrap_full_html(body, title=first_line)
        html = convert_tagged_text_to_html(html)
        if output_html_path:
            with open(output_html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"✅ Saved HTML article to {output_html_path}")
        return html
    else:
        if output_html_path:
            with open(output_html_path, 'w', encoding='utf-8') as f:
                f.write(body)
            logger.info(f"✅ Saved text article to {output_html_path}")
        return body

def format_llm_output(text):
    """Convert markdown emphasis (**text**) to HTML <strong> tags and add line breaks."""
    import re
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Add line breaks for better readability
    text = text.replace('. ', '.<br>')
    text = text.replace('! ', '!<br>')
    text = text.replace('? ', '?<br>')
    return text


def parse_ollama_response(response):
    """Safely parse Ollama response, supporting NDJSON or multiple JSON objects."""
    try:
        # Try standard JSON
        raw_text = response.json().get('response', '')
    except Exception:
        # Try NDJSON (newline-delimited JSON)
        lines = response.text.strip().splitlines()
        for line in lines:
            try:
                obj = json.loads(line)
                if 'response' in obj:
                    raw_text = obj['response']
                    break
            except Exception:
                continue
        else:
            # Fallback: return raw text
            raw_text = response.text
    
    # Format the output
    return format_llm_output(raw_text)

def mark_entities(text, entities):
    """סמן ישויות בטקסט ב-[[...]] כדי שהמודל לא יתרגם אותן"""
    for ent in sorted(entities, key=len, reverse=True):
        text = re.sub(rf'\b{re.escape(ent)}\b', f'[[{ent}]]', text)
    return text

def restore_marked_entities(text, entities):
    """החזר כל ישות שסומנה ב-[[...]] למקור באנגלית, גם אם המודל שינה אותה"""
    for ent in sorted(entities, key=len, reverse=True):
        # תחזיר כל מופע של [[...]] ל-ent המקורי
        text = re.sub(rf'\[\[.*?{re.escape(ent)}.*?\]\]', ent, text)
    return text

def generate_hebrew_article(ticker, entity_analysis, vocabulary, original_text=None, key_points=None):
    """Generate Hebrew article from entity analysis, with entity protection and relevant vocabulary"""
    try:
        # Extract entities from original text
        entities = list(extract_entities(original_text)) if original_text else []
        entity_list = ', '.join(sorted(set(entities)))
        # Mark entities in the text for the LLM
        marked_text = mark_entities(original_text, entities) if original_text else ''
        # בנה snippet של מילון רלוונטי
        context_for_vocab = original_text or (" ".join([kp['text'] for kp in key_points]) if key_points else '')
        relevant_vocab = load_hebrew_vocabulary(context_text=context_for_vocab)
        # Create prompt with specific instructions to avoid repetitive openings and protect entities
        prompt = f"""אתה מומחה לכתיבת כתבות פיננסיות בעברית. כתוב כתבה מקצועית ומעניינת על {ticker}.

**חשוב מאוד - הוראות לכתיבה:**
- אל תתרגם שמות של חברות, תרופות, אנשים, סימולים, מונחים מקצועיים – השאר אותם באנגלית כפי שמופיעים בטקסט המקורי.
- אם מופיעה מילה בסוגריים מרובעים [[...]], אל תיגע בה.
- להלן רשימת ישויות שיש לשמר באנגלית: {entity_list}
- כאשר אתה מתרגם מונח מקצועי, בדוק במילון המצורף ובחר את התרגום המתאים ביותר. אל תמציא תרגומים – השתמש רק במה שמופיע במילון כשאפשר.
- בנה פתיחה מעניינת בהתבסס על המידע הספציפי שתקבל
- התחל עם המידע הכי מעניין או חשוב מהנתונים: סטטיסטיקה מרשימה, אירוע חשוב, תחזית מעניינת, או ניתוח מפתיע
- כתוב בשפה מקצועית אך נגישה
- השתמש במונחים פיננסיים עבריים מתאימים

**מידע לניתוח:**
{entity_analysis}

**מילון מונחים רלוונטיים:**
{relevant_vocab}

**טקסט מקורי מסומן:**
{marked_text}

**מבנה הכתבה:**
1. כותרת ראשית מעניינת
2. פתיחה מעניינת המבוססת על המידע הספציפי (לא משעממת!)
3. ניתוח הגורמים החיוביים
4. ניתוח הגורמים השליליים  
5. ניתוח הגורמים הנייטרליים
6. סיכום ותחזית

**הוראות לפתיחה:**
- קרא את כל המידע וזהה את הנתון הכי מעניין או חשוב
- התחל עם אותו נתון: אחוז שינוי, תחזית אנליסט, אירוע חשוב, או סטטיסטיקה מרשימה
- אל תפתח עם משפטים כלליים - התחל עם משהו ספציפי ומעניין

כתוב כתבה מקצועית ומעניינת בעברית:"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": LLM_MODEL_SETTINGS['model_name'],
                "prompt": prompt,
                "options": {
                    "num_predict": LLM_OUTPUT_SETTINGS.get("default_max_tokens", 5000),  # Use config value
                    "temperature": LLM_MODEL_SETTINGS.get('temperature', 0.7),
                    "top_p": LLM_MODEL_SETTINGS.get('top_p', 0.9),
                },
                "stream": False
            },
            timeout=300,  # Increased from 120 to 300 seconds
        )
        response.raise_for_status()
        article = parse_ollama_response(response)
        # Restore entities in the output
        article = restore_marked_entities(article, entities)
        return article
    except Exception as e:
        logger.error(f"Error generating Hebrew article: {e}")
        raise


def improve_hebrew_article(article_text, ticker_info, vocabulary_examples=None, max_tokens=None):
    """
    שלב 2: עריכה, תיקון דקדוק, תחביר, הקשר, תרגום, תוך שימוש בדוגמאות מהמילון במידת הצורך
    """
    prompt = f"""ערוך את המאמר הבא כך שיהיה תקני, מקצועי, ברור, ועם דקדוק נכון בעברית.

**הוראות עריכה:**
1. בדוק דקדוק עברי נכון (התאמה בין נושא לפועל, זכר/נקבה, יחיד/רבים)
2. תרגם מונחים פיננסיים לעברית מדויקת ומקצועית
3. ודא שכל הנתונים המדויקים (אחוזים, מספרים, תאריכים) נשמרים
4. שפר ניסוחים לעברית טבעית וזורמת
5. בדוק התאמה לוגית בין משפטים
6. הוסף או תיקן הדגשות (**טקסט**) למילות מפתח
7. ודא שימוש נכון בסימני פיסוק עבריים

**דוגמאות לשיפור:**
- "אופטימיות בשווקים" → "חוזק השווקים"
- "מכסי סחר מועילים" → "מכסים מועילים"  
- "החמצת הזדמנויות" → "המתנה להזדמנויות"
- "הרחבת נוכחות" → "הרחבת הנוכחות"

**מילון עזרה (אם זמין):**
{vocabulary_examples if vocabulary_examples else "אין מילון זמין"}

**מאמר לעריכה:**
{article_text}"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": LLM_MODEL_SETTINGS['model_name'],
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens or LLM_OUTPUT_SETTINGS.get("default_max_tokens", 5000),  # Use config value
                "temperature": LLM_MODEL_SETTINGS.get('temperature', 0.7),
                "top_p": LLM_MODEL_SETTINGS.get('top_p', 0.9),
            },
            "stream": False
        },
        timeout=300,  # Increased from 120 to 300 seconds
    )
    response.raise_for_status()
    return parse_ollama_response(response)


def process_with_contextual_prompt(text_block, ticker_info, metadata_path=None, max_tokens=None, original_text=None):
    """
    שלב 1: יצירת מאמר מקצועי בעברית (LLM)
    שלב 2: עריכה, תיקון דקדוק, תחביר, הקשר, תרגום, תוך שימוש בדוגמאות מהמילון
    """
    # Load entity analysis if available
    entity_analysis = ""
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                entity_data = json.load(f)
                if 'compact_analysis' in entity_data:
                    # Parse the compact_analysis JSON string
                    compact_data = json.loads(entity_data['compact_analysis'])
                    # Format it nicely for the LLM
                    entity_analysis = f"""
**ניתוח ישויות עבור {compact_data.get('ticker', '')}:**

**חברות מוזכרות:** {', '.join(compact_data.get('companies', [])[:5])}
**אנשים מוזכרים:** {', '.join(compact_data.get('people', [])[:3])}
**תחום:** {compact_data.get('industry', 'לא ידוע')}
**רגש כללי:** {compact_data.get('sentiment', {}).get('overall', 'נייטרלי')}

**נקודות מפתח:**
{chr(10).join([f"• {point.get('text', '')[:200]}..." for point in compact_data.get('key_points', [])[:3]])}

**סכומי כסף:** {', '.join(compact_data.get('money_amounts', [])[:5])}
**תאריכים חשובים:** {', '.join(compact_data.get('important_dates', [])[:3])}
**מילות מפתח פיננסיות:** {', '.join(compact_data.get('financial_keywords', [])[:5])}
"""
                else:
                    entity_analysis = str(entity_data)
        except Exception as e:
            logger.warning(f"Could not load entity analysis: {e}")
            entity_analysis = ""
    
    # Load vocabulary
    vocabulary = load_hebrew_vocabulary()
    
    # Generate Hebrew article (pass original_text for entity protection)
    hebrew_article = generate_hebrew_article(ticker_info.get('ticker'), entity_analysis, vocabulary, original_text=original_text)
    
    # Improve the article
    improved_article = improve_hebrew_article(hebrew_article, ticker_info, vocabulary_examples=vocabulary, max_tokens=max_tokens)
    return improved_article

# דוגמה לשימוש
if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Process MarketBit original txt to Hebrew HTML article.')
    parser.add_argument('input', help='Path to original txt file')
    parser.add_argument('--output', help='Output HTML/text file path', default=None)
    parser.add_argument('--ticker', help='Ticker symbol (optional)', default=None)
    parser.add_argument('--text', action='store_true', help='Output plain text instead of HTML')
    args = parser.parse_args()
    try:
        result = process_article_file(args.input, args.output, args.ticker, as_html=not args.text)
        print(result[:1000] + ('...\n[truncated]' if len(result) > 1000 else ''))
    except Exception as e:
        logger.error(f"❌ {e}")
        print(f"Error: {e}")