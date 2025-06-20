import os
import re
from bs4 import BeautifulSoup

ARTICLES_DIR = 'articles'

# תנאים לזיהוי כותרת משנה
def is_subheading(text):
    text = text.strip()
    if len(text) <= 40:
        return True
    if text.endswith((':', '?', '!', '：', '؟', '！')):
        return True
    return False

def fix_headings_in_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    changed = False
    # מצא את div של התוכן
    content_div = soup.find('div', class_='article-content-text')
    if not content_div:
        return False
    # מצא את כל הפסקאות הישירות
    paragraphs = content_div.find_all('p', recursive=False)
    if not paragraphs:
        return False
    # הפסקה הראשונה תהפוך ל-h1
    first = paragraphs[0]
    h1 = soup.new_tag('h1')
    h1.string = first.get_text(strip=True)
    first.replace_with(h1)
    changed = True
    # כל פסקה קצרה או שמסתיימת בנקודתיים/סימן שאלה/קריאה תהפוך ל-h2
    for p in content_div.find_all('p', recursive=False):
        txt = p.get_text(strip=True)
        if is_subheading(txt):
            h2 = soup.new_tag('h2')
            h2.string = txt
            p.replace_with(h2)
            changed = True
    if changed:
        # שמור גיבוי
        os.rename(filepath, filepath + '.bak')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    return changed

def main():
    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.html')]
    print(f'נמצאו {len(files)} קבצים לתיקון...')
    fixed = 0
    for fname in files:
        path = os.path.join(ARTICLES_DIR, fname)
        if fix_headings_in_html_file(path):
            print(f'✅ תוקן: {fname}')
            fixed += 1
    print(f'בוצע תיקון ל-{fixed} קבצים.')

if __name__ == '__main__':
    main() 