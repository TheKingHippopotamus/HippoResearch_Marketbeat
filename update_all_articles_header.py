import os
import re
import shutil

ARTICLES_DIR = 'articles'
TEMPLATE_FILE = 'article_template.html'

# טען את ה-header וה-CSS מהתבנית
with open(TEMPLATE_FILE, encoding='utf-8') as f:
    template = f.read()

# חילוץ ה-header (כולל <style> ו-social-section)
header_match = re.search(r'(<div class="header">[\s\S]+?<div class="social-section">[\s\S]+?</div>\s*</div>\s*</div>)', template)
if not header_match:
    raise Exception('לא נמצא header בתבנית!')
header_html = header_match.group(1)

# חילוץ ה-CSS (כל ה-<style> עד סיום ה-header)
css_match = re.findall(r'<style>([\s\S]+?)</style>', template)
css = '\n'.join(css_match)

# חילוץ סקריפט השיתוף (אם יש)
share_script_match = re.search(r'(<script[^>]*>[^<]*document\.addEventListener\([\s\S]+?x-share-btn-custom[\s\S]+?</script>)', template)
share_script = share_script_match.group(1) if share_script_match else ''

def update_article(file_path):
    base = os.path.basename(file_path)
    if base.endswith('.bak'):
        return
    # חילוץ ticker+date מהשם
    m = re.match(r'([A-Z]+)_([0-9]{8})\.html$', base)
    if not m:
        return
    ticker, date = m.group(1), m.group(2)
    # גיבוי
    bak_path = file_path + '.bak'
    if not os.path.exists(bak_path):
        shutil.copy2(file_path, bak_path)
    # טען תוכן
    with open(file_path, encoding='utf-8') as f:
        html = f.read()
    # עדכן header (החלף את כל ה-header הישן)
    html = re.sub(r'(<div class="header">[\s\S]+?<div class="social-section">[\s\S]+?</div>\s*</div>\s*</div>)',
                  header_html.replace('GIS', ticker), html, count=1)
    # עדכן קישור שיתוף דינמי
    share_url = f'https://thekinghippopotamus.github.io/HippoResearch_Marketbeat/articles/{base}'
    html = re.sub(r'(https://twitter.com/intent/tweet\?text=[^\"]+)',
                  f'https://twitter.com/intent/tweet?text=מחקר חדש של Hippopotamus Research ${ticker}%0A{share_url}', html)
    # ודא שה-CSS וה-script מעודכנים (הסר ישנים, הוסף חדשים)
    html = re.sub(r'<style>[\s\S]+?</style>', '', html, count=0)
    html = re.sub(r'<script[^>]*>[^<]*document\.addEventListener\([\s\S]+?x-share-btn-custom[\s\S]+?</script>', '', html, count=0)
    # הוסף CSS ו-script חדשים אחרי </title>
    html = re.sub(r'(</title>)', r'\1\n<style>\n' + css + '\n</style>\n' + share_script + '\n', html, count=1)
    # שמור
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    for fname in os.listdir(ARTICLES_DIR):
        if fname.endswith('.html') and not fname.endswith('.bak'):
            update_article(os.path.join(ARTICLES_DIR, fname))
    print('העדכון הושלם!') 