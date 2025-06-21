import os
import re
from pathlib import Path

def convert_tagged_text_to_html(text):
    if not text:
        return text
    text = re.sub(r'#+\s*SUBTITLE#', '#SUBTITLE#', text)
    text = re.sub(r'#+\s*TITLE#', '#TITLE#', text)
    text = re.sub(r'#+\s*PARA#', '#PARA#', text)
    parts = re.split(r'(#TITLE#|#SUBTITLE#|#PARA#)', text)
    html_lines = []
    current_tag = None
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part in ['#TITLE#', '#SUBTITLE#', '#PARA#']:
            current_tag = part
        else:
            if current_tag == '#TITLE#':
                html_lines.append(f"<h1>{part}</h1>")
            elif current_tag == '#SUBTITLE#':
                html_lines.append(f"<h2>{part}</h2>")
            elif current_tag == '#PARA#':
                html_lines.append(f"<p>{part}</p>")
            else:
                html_lines.append(part)
    return '\n'.join(html_lines)

def clean_html_content(html_content):
    if not html_content:
        return html_content
    cleaned = convert_tagged_text_to_html(html_content)
    cleaned = re.sub(r'##\s*', '', cleaned)
    cleaned = re.sub(r'#+\s*', '', cleaned)
    cleaned = re.sub(r'<p>\s*</p>', '', cleaned)
    cleaned = re.sub(r'<h\d>\s*</h\d>', '', cleaned)
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    return cleaned.strip()

def extract_head_section(template_path):
    """Extract the <head>...</head> section from the template file."""
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    match = re.search(r'<head[\s\S]*?</head>', html, re.IGNORECASE)
    if match:
        return match.group(0)
    else:
        raise ValueError('No <head> section found in template.')

def replace_head_in_html(html_content, new_head):
    """Replace or insert the <head>...</head> section in html_content with new_head."""
    # Remove existing <head>...</head>
    if re.search(r'<head[\s\S]*?</head>', html_content, re.IGNORECASE):
        html_content = re.sub(r'<head[\s\S]*?</head>', new_head, html_content, count=1, flags=re.IGNORECASE)
    else:
        # Insert after <!DOCTYPE html> or <html ...>
        if '<html' in html_content:
            html_content = re.sub(r'(<html[^>]*>)', r'\1\n' + new_head, html_content, count=1, flags=re.IGNORECASE)
        else:
            html_content = new_head + '\n' + html_content
    return html_content

def extract_newsletter_section(template_path):
    """Extract the newsletter-section HTML from the template file (עדין במיוחד)."""
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    # שלוף את הניוזלטר כולל ה-h3 המעודכן
    match = re.search(r'(<div class="newsletter-section"[\s\S]*?</div>\s*)', html)
    if match:
        return match.group(1)
    else:
        raise ValueError('No newsletter-section found in template.')

def insert_newsletter_section(html_content, newsletter_html):
    """Insert the newsletter section right after <div class="container"> if not already present."""
    if 'newsletter-section' in html_content:
        return html_content  # Already present
    return re.sub(r'(<div class="container">)', r'\1\n' + newsletter_html, html_content, count=1)

def restore_and_clean_articles():
    articles_dir = Path("articles")
    html_files = list(articles_dir.glob("*.html"))
    template_path = Path("arcive/test_V_new_style.html")
    new_head = extract_head_section(template_path)
    newsletter_html = extract_newsletter_section(template_path)
    for html_file in html_files:
        backup_file = html_file.with_suffix(html_file.suffix + ".backup")
        if backup_file.exists():
            with open(backup_file, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = clean_html_content(content)
        else:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = clean_html_content(content)
        cleaned_with_head = replace_head_in_html(cleaned, new_head)
        cleaned_with_newsletter = insert_newsletter_section(cleaned_with_head, newsletter_html)
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(cleaned_with_newsletter)
        print(f"✅ Restored, cleaned, styled, and added newsletter: {html_file.name}")

if __name__ == "__main__":
    print("🧹 Restoring, cleaning, and styling all articles in 'articles/'...")
    restore_and_clean_articles()
    print("✨ All articles processed!") 