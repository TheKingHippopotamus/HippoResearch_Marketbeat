"""
Text processing utilities for HTML conversion and formatting
Utilities לעיבוד טקסט להמרת HTML ועיצוב
"""
import re
from typing import List, Tuple


def convert_tagged_text_to_html(text: str) -> str:
    """
    Convert tagged text to HTML format
    ממיר טקסט מסומן לפורמט HTML
    
    Converts:
    - **text** to <strong>text</strong>
    - Line breaks to <br>
    - Paragraphs to <p> tags
    
    Args:
        text: Input text with markdown-like tags
    
    Returns:
        HTML formatted text
    """
    if not text:
        return ""
    
    # Convert markdown bold to HTML strong
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert multiple newlines to paragraphs
    paragraphs = text.split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        if not para.strip():
            continue
        
        # Replace single newlines with <br>
        para = para.replace('\n', '<br>')
        
        # Add paragraph tag
        html_paragraphs.append(f'<p>{para}</p>')
    
    return '\n'.join(html_paragraphs) if html_paragraphs else f'<p>{text.replace(chr(10), "<br>")}</p>'


def mark_entities_in_text(text: str, entities: List[str]) -> str:
    """
    Mark entities in text for protection during translation
    מסמן ישויות בטקסט להגנה בעת תרגום
    
    Args:
        text: Input text
        entities: List of entity names to mark
    
    Returns:
        Text with entities marked as [[ENTITY]]
    """
    if not entities:
        return text
    
    # Sort by length (longest first) to avoid partial matches
    sorted_entities = sorted(set(entities), key=len, reverse=True)
    
    marked_text = text
    for entity in sorted_entities:
        if not entity or len(entity) < 2:
            continue
        # Use word boundaries for exact matches
        pattern = r'\b' + re.escape(entity) + r'\b'
        marked_text = re.sub(pattern, f'[[{entity}]]', marked_text, flags=re.IGNORECASE)
    
    return marked_text


def restore_marked_entities(text: str, entities: List[str]) -> str:
    """
    Restore marked entities after translation
    משחזר ישויות מסומנות אחרי תרגום
    
    Args:
        text: Text with marked entities [[ENTITY]]
        entities: Original entity list
    
    Returns:
        Text with entities restored
    """
    if not entities:
        return text
    
    restored_text = text
    for entity in entities:
        if not entity:
            continue
        # Replace [[ENTITY]] with ENTITY
        pattern = r'\[\[(' + re.escape(entity) + r')\]\]'
        restored_text = re.sub(pattern, entity, restored_text, flags=re.IGNORECASE)
    
    return restored_text


def extract_entities_from_text(text: str) -> List[str]:
    """
    Extract potential entity names from text
    מחלץ שמות ישויות פוטנציאליות מטקסט
    
    Args:
        text: Input text
    
    Returns:
        List of potential entity names
    """
    entities = []
    
    # Pattern 1: Multi-word capitalized (e.g., "Apple Inc.", "Robert W. Baird")
    multi_word = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z.]+)+)\b', text)
    entities.extend(multi_word)
    
    # Pattern 2: All caps (tickers, acronyms)
    all_caps = re.findall(r'\b([A-Z]{2,})\b', text)
    entities.extend(all_caps)
    
    # Pattern 3: Single capitalized words (excluding common words)
    single_word = re.findall(r'\b([A-Z][a-z]{3,})\b', text)
    common_words = {'The', 'This', 'That', 'These', 'Those', 'They', 'There',
                   'Positive', 'Negative', 'Neutral', 'Sentiment', 'Sentiment:', 'Apple'}
    entities.extend([w for w in single_word if w not in common_words])
    
    # Remove duplicates and empty strings
    return sorted(list(set([e for e in entities if e and len(e) > 2])))


def format_financial_numbers(text: str) -> str:
    """
    Format financial numbers for better readability
    מעיצב מספרים פיננסיים לקריאה טובה יותר
    
    Args:
        text: Text with numbers
    
    Returns:
        Formatted text
    """
    # Format large numbers with commas
    text = re.sub(r'(\d{4,})', lambda m: f"{int(m.group(1)):,}", text)
    return text


