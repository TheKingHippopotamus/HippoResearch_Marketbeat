import os
import re
from pathlib import Path

NEWSLETTER_HTML = '''<div class="newsletter-section" style="margin:12px auto 20px auto;max-width:260px;padding:0;background:none;border:none;box-shadow:none;border-radius:0;position:relative;z-index:2;">
    <h3 style="font-weight:400;opacity:0.5;font-size:0.85em;margin-bottom:2px;margin-top:0;color:var(--accent-color);">הצטרפו לרשימת התפוצה שלנו</h3>
    <iframe class="newsletter-iframe" scrolling="no" style="height:110px;width:100%;border:none;background:none;box-shadow:none;border-radius:0;" src="https://buttondown.com/nirstam?as_embed=true"></iframe>
</div>\n'''

NEWSLETTER_IFRAME_REGEX = re.compile(r'<iframe[^>]*src="https://buttondown.com/nirstam\?as_embed=true"[^>]*></iframe>', re.IGNORECASE)
NEWSLETTER_SECTION_REGEX = re.compile(r'<div class="newsletter-section"[\s\S]*?</div>\s*', re.IGNORECASE)


def update_or_insert_newsletter(html):
    # בדוק אם יש div newsletter-section בתוכן (ולא רק ב-CSS)
    if re.search(r'<div\s+class=["\"]newsletter-section["\"]', html, re.IGNORECASE):
        # עדכן את כל ה-newsletter-section לגרסה החדשה
        html, n = NEWSLETTER_SECTION_REGEX.subn(NEWSLETTER_HTML, html, count=1)
        return html, (n > 0)
    else:
        # הוסף לראש ה-content
        html, n = re.subn(r'(<div class="content">)', r'\1\n' + NEWSLETTER_HTML, html, count=1)
        return html, (n > 0)

def process_all_articles():
    articles_dir = Path("articles")
    html_files = list(articles_dir.glob("*.html"))
    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        new_html, changed = update_or_insert_newsletter(html)
        if changed:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"✅ Newsletter updated/added in {html_file.name}")
        else:
            print(f"ℹ️ No change needed for {html_file.name}")

if __name__ == "__main__":
    print("🔄 Adding or updating newsletter-section in all articles...")
    process_all_articles()
    print("✨ Done!") 