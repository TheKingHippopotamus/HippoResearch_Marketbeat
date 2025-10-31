import re
#
def clean_processed_text(text):
    """
    מנקה את הטקסט המעובד מסימונים מיותרים ותגים לא נכונים
    ומתקן שגיאות עברית נפוצות
    """
    if not text:
        return text
    
    # הסרת סימונים פנימיים של המערכת
    text = re.sub(r'TITLE#\s*', '', text)
    text = re.sub(r'SUBTITLE#\s*', '', text)
    text = re.sub(r'PARA#\s*', '', text)
    
    # הסרת סימונים מיותרים
    text = re.sub(r'##\s*', '', text)
    text = re.sub(r'#+\s*', '', text)
    
    # הסרת כותרות לא נכונות
    text = re.sub(r'^כותרת:\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^פסקאות גוף:\s*', '', text, flags=re.MULTILINE)
    
    # ניקוי תגי HTML לא נכונים
    text = re.sub(r'<p>\s*</p>', '', text)  # תגי p ריקים
    text = re.sub(r'<h\d>\s*</h\d>', '', text)  # תגי h ריקים
    
    # # תיקון שגיאות עברית נפוצות
    # text = re.sub(r'שוק המניות של\s+', 'מניית ', text)  # תיקון "שוק המניות של"
    # text = re.sub(r'המשקיעים יכול\b', 'המשקיעים יכולים', text)  # תיקון רבים/יחיד
    # text = re.sub(r'תנודתיות ל,\s*', 'תנודתיות בשוק, ', text)  # תיקון משפטים לא שלמים
    
    # הסרת שורות ריקות מיותרות
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # ניקוי רווחים מיותרים בתחילת ובסוף
    text = text.strip()
    return text

def clean_llm_text(text):
    """Clean LLM output from JSON artifacts, HTML tags, markdown symbols, and formatting issues"""
    if not text:
        return text
    # Remove JSON structure artifacts
    text = re.sub(r'^\s*\{\s*', '', text)
    text = re.sub(r'\s*\}\s*$', '', text)
    text = re.sub(r'^\s*"text":\s*"', '', text)
    text = re.sub(r'^\s*"":\s*"', '', text)
    text = re.sub(r'"\s*,\s*"tags":\s*\[\s*\]\s*$', '', text)
    text = re.sub(r'"\s*$', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markdown symbols
    text = re.sub(r'^#+\s*', '', text)  # Remove markdown headers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markdown
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic markdown
    # Clean up newlines and whitespace
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
    text = re.sub(r' +', ' ', text)  # Normalize spaces
    
    # Fix Hebrew grammar errors
    text = fix_hebrew_grammar_errors(text)
    
    return text.strip()

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

def convert_tagged_text_to_html(text):
    """
    המרת טקסט מסומן (כולל סימוני markdown, כותרות ופסקאות בעברית) ל-HTML תקני, תוך הסרה מוחלטת של תוויות מיותרות.
    """
    if not text:
        return text
    lines = text.split('\n')
    processed_lines = []
    label_pattern = re.compile(r'^(#*)\s*(פסקה( משנה| אחרונה)?(:|\s*:)?..*)$', re.UNICODE)
    main_title_pattern = re.compile(r'^כותרת ראשית:\s*(.*)$')
    subtitle_pattern = re.compile(r'^כותרת משנה:\s*(.*)$')
    subpara_pattern = re.compile(r'^פסקה משנה:\s*(.*)$')
    lastpara_pattern = re.compile(r'^פסקה אחרונה:\s*(.*)$')
    title_hash_pattern = re.compile(r'^TITLE#\s*(.*)$')
    subtitle_hash_pattern = re.compile(r'^(##\s*)?SUBTITLE#\s*(.*)$')
    subtitle_hash_alt_pattern = re.compile(r'^##\s*#([^#]+)$')
    subtitle_double_hash_pattern = re.compile(r'^##\s*##\s*(.*)$')
    subtitle_hash_with_hash_pattern = re.compile(r'^##\s*#SUBTITLE#\s*(.*)$')
    para_hash_with_hash_pattern = re.compile(r'^##\s*#PARA#\s*(.*)$')
    para_hash_pattern = re.compile(r'^#PARA#\s*(.*)$')
    para_hash_triple_pattern = re.compile(r'^###\s*PARA#\s*(.*)$')
    # hebrew_para_pattern = re.compile(r'^#\s*פסקה\s+(ראשונה|שנייה|שלישית|רביעית|חמישית|שישית|שביעית|שמינית|תשיעית|עשירית):\s*(.*)$')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if label_pattern.match(line):
            continue
        m = main_title_pattern.match(line)
        if m:
            title = m.group(1).strip()
            if title:
                processed_lines.append(f'<h1>{title}</h1>')
            continue
        m = subtitle_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        m = subpara_pattern.match(line)
        if m:
            subpara = m.group(1).strip()
            if subpara:
                processed_lines.append(f'<h3>{subpara}</h3>')
            continue
        m = lastpara_pattern.match(line)
        if m:
            lastpara = m.group(1).strip()
            if lastpara:
                processed_lines.append(f'<h3>{lastpara}</h3>')
            continue
        m = title_hash_pattern.match(line)
        if m:
            title = m.group(1).strip()
            if title:
                processed_lines.append(f'<h1>{title}</h1>')
            continue
        m = subtitle_hash_pattern.match(line)
        if m:
            subtitle = m.group(2).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        m = subtitle_hash_alt_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        m = subtitle_double_hash_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        m = subtitle_hash_with_hash_pattern.match(line)
        if m:
            subtitle = m.group(1).strip()
            if subtitle:
                processed_lines.append(f'<h2>{subtitle}</h2>')
            continue
        m = para_hash_with_hash_pattern.match(line)
        if m:
            para_text = m.group(1).strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        m = para_hash_pattern.match(line)
        if m:
            para_text = m.group(1).strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        # m = hebrew_para_pattern.match(line)
        # if m:
        #     para_text = m.group(2).strip()
        #     if para_text:
        #         processed_lines.append(f'<p>{para_text}</p>')
        #     continue
        if line.startswith('### ') and not line.startswith('### PARA#') and not line.startswith('### SUBTITLE#'):
            para_text = line[4:].strip()
            if para_text:
                processed_lines.append(f'<p>{para_text}</p>')
            continue
        if line.startswith('### '):
            processed_lines.append(f'<h3>{line[4:]}</h3>')
            continue
        if line.startswith('## '):
            processed_lines.append(f'<h2>{line[3:]}</h2>')
            continue
        if line.startswith('# '):
            processed_lines.append(f'<h1>{line[2:]}</h1>')
            continue
        processed_lines.append(f'<p>{line}</p>')
    return '\n'.join(processed_lines)

def parse_marketbeat_structure(text):
    """
    מנתח את מבנה הטקסט של MarketBeat וממיר אותו לפורמט מתאים ל-LLM
    """
    if not text:
        return text
    lines = text.split('\n')
    processed_lines = []
    if lines and lines[0].strip():
        company_line = lines[0].strip()
        processed_lines.append(f"#TITLE# {company_line}")
    current_sentiment = None
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('Positive Sentiment:'):
            current_sentiment = 'positive'
            processed_lines.append(f"#SUBTITLE# נקודות חיוביות")
            continue
        elif line.startswith('Neutral Sentiment:'):
            current_sentiment = 'neutral'
            processed_lines.append(f"#SUBTITLE# נקודות נייטרליות")
            continue
        elif line.startswith('Negative Sentiment:'):
            current_sentiment = 'negative'
            processed_lines.append(f"#SUBTITLE# נקודות שליליות")
            continue
        elif line.startswith('Posted') or line.startswith('AI Generated'):
            continue
        elif line and current_sentiment:
            processed_lines.append(f"#PARA# {line}")
    return '\n'.join(processed_lines) 

def fix_hebrew_grammar_errors(text):
    """
    מתקן שגיאות דקדוק עברית נפוצות בטקסט
    """
    if not text:
        return text
    
    # # תיקון שגיאות רבים/יחיד
    # text = re.sub(r'המשקיעים יכול\b', 'המשקיעים יכולים', text)
    # text = re.sub(r'האנליסטים הציג\b', 'האנליסטים הציגו', text)
    # text = re.sub(r'החברות מתמודד\b', 'החברות מתמודדות', text)
    
    # # תיקון ביטויים שגויים
    # text = re.sub(r'שוק המניות של\s+', 'מניית ', text)
    # text = re.sub(r'המניה של\s+', 'מניית ', text)
    
    # # תיקון משפטים לא שלמים
    # text = re.sub(r'תנודתיות ל,\s*', 'תנודתיות בשוק, ', text)
    # text = re.sub(r'ביצועים ל,\s*', 'ביצועים מעורבים, ', text)
    
    # # תיקון מילות קישור
    # text = re.sub(r'\bאבל\b', 'אולם', text)  # יותר מקצועי
    # text = re.sub(r'\bגם\b', 'בנוסף', text)  # יותר מקצועי
    
    # # תיקון סימני פיסוק
    # text = re.sub(r',\s*,', ',', text)  # הסרת פסיקים כפולים
    # text = re.sub(r'\.\s*\.', '.', text)  # הסרת נקודות כפולות
    
    # return text 