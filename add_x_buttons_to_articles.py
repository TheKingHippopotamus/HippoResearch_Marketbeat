import os
import re
from bs4 import BeautifulSoup, Tag

ARTICLES_DIR = 'articles'
DOMAIN = 'https://thekinghippopotamus.github.io/HippoResearch_Marketbeat/articles/'
FOLLOW_URL = 'https://twitter.com/your_twitter_handle'
X_ICON_SRC = 'x.png'

CSS_BLOCK = '''
    <style>
    .x-share-btn-custom {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 22px;
      background: linear-gradient(90deg, #14171a 0%, #1da1f2 100%);
      color: #fff;
      border-radius: 30px;
      text-decoration: none;
      font-weight: 700;
      font-size: 1em;
      box-shadow: 0 4px 16px rgba(29,161,242,0.10);
      transition: background 0.3s, transform 0.2s, box-shadow 0.2s;
      border: none;
      outline: none;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }
    .x-share-btn-custom:hover {
      background: linear-gradient(90deg, #1da1f2 0%, #14171a 100%);
      transform: translateY(-2px) scale(1.04);
      box-shadow: 0 8px 24px rgba(29,161,242,0.18);
    }
    .x-share-btn-custom .x-icon {
      width: 24px;
      height: 24px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.3s;
    }
    .x-share-btn-custom:hover .x-icon {
      background: #1da1f2;
    }
    .x-share-btn-custom .x-icon img {
      width: 16px;
      height: 16px;
      display: block;
    }
    .follow-btn {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 22px;
      background: linear-gradient(90deg, #7b2ff2 0%, #1da1f2 100%);
      color: #fff;
      border-radius: 30px;
      text-decoration: none;
      font-weight: 700;
      font-size: 1em;
      box-shadow: 0 4px 16px rgba(123,47,242,0.10);
      transition: background 0.3s, transform 0.2s, box-shadow 0.2s;
      border: none;
      outline: none;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }
    .follow-btn:hover {
      background: linear-gradient(90deg, #1da1f2 0%, #7b2ff2 100%);
      transform: translateY(-2px) scale(1.04);
      box-shadow: 0 8px 24px rgba(123,47,242,0.18);
    }
    .follow-btn .x-icon {
      width: 24px;
      height: 24px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.3s;
    }
    .follow-btn:hover .x-icon {
      background: #7b2ff2;
    }
    .follow-btn .x-icon img {
      width: 16px;
      height: 16px;
      display: block;
    }
    </style>
'''

SOCIAL_JS_TEMPLATE = '''<script>
document.addEventListener('DOMContentLoaded', function() {{
  document.querySelectorAll('.x-share-btn-custom').forEach(function(btn) {{
    btn.addEventListener('click', function(e) {{
      e.preventDefault();
      e.stopPropagation();
      window.open('index.html', '_blank');
      window.open('{share_url}', '_self', 'noopener');
      return false;
    }});
  }});
}});
</script>'''

SOCIAL_SECTION_TEMPLATE = '''<div class="social-section">
  <div class="ticker-badge">{ticker}</div>
  <a href="{follow_url}" rel="noopener" target="_blank" class="follow-btn">
    <span class="x-icon">
      <img src="{x_icon_src}" alt="X">
    </span>
    עקבו אחרינו
  </a>
  <button type="button" class="x-share-btn-custom">
    <span class="x-icon">
      <img src="{x_icon_src}" alt="X">
    </span>
    שתף ב־X
  </button>
</div>'''

def url_encode(text):
    from urllib.parse import quote
    return quote(text, safe='')

def build_share_url(ticker, filename):
    text = f"מחקר חדש של Hippopotamus Research (${ticker})\n{DOMAIN}{filename}"
    return f"https://twitter.com/intent/tweet?text={url_encode(text)}"

def update_article(file_path):
    filename = os.path.basename(file_path)
    match = re.match(r"([A-Z0-9]+)_", filename)
    if not match:
        print(f"Skipping {filename}: could not detect ticker.")
        return
    ticker = match.group(1)
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Add CSS if not present
    head = soup.find('head')
    if head and CSS_BLOCK.strip() not in str(head):
        css_soup = BeautifulSoup(CSS_BLOCK, 'html.parser')
        style_tags = css_soup.find_all('style')
        if style_tags and isinstance(head, Tag):
            for style_tag in style_tags:
                head.append(style_tag)

    # Build social section
    share_url = build_share_url(ticker, filename)
    social_html = SOCIAL_SECTION_TEMPLATE.format(
        ticker=ticker,
        follow_url=FOLLOW_URL,
        share_url=share_url,
        x_icon_src=X_ICON_SRC
    )
    social_soup = BeautifulSoup(social_html, 'html.parser')

    # Find and replace social-section in header
    header = soup.find('div', class_='header-content')
    if isinstance(header, Tag):
        old_social = header.find('div', class_='social-section') if isinstance(header, Tag) else None
        if old_social:
            old_social.replace_with(social_soup)
        else:
            # Insert after logo-section
            logo_section = header.find('div', class_='logo-section') if isinstance(header, Tag) else None
            if logo_section:
                logo_section.insert_after(social_soup)

    # Insert the JS block after the social-section (if not already present)
    js_html = SOCIAL_JS_TEMPLATE.format(share_url=share_url)
    js_soup = BeautifulSoup(js_html, 'html.parser')
    # Remove any old script with this logic
    for script in soup.find_all('script'):
        script_content = getattr(script, 'string', None)
        if script_content and 'x-share-btn-custom' in script_content and 'window.open' in script_content:
            script.decompose()
    # Insert after social-section
    social_section = header.find('div', class_='social-section') if isinstance(header, Tag) else None
    if social_section:
        social_section.insert_after(js_soup)

    # Remove old share/follow buttons outside header if exist (both <a> and <button> for share)
    for btn in soup.find_all(['a', 'button'], class_=['x-share-btn-custom', 'follow-btn']):
        parent_social = btn.find_parent('div', class_='social-section') if isinstance(btn, Tag) else None
        if not parent_social:
            btn.decompose()

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Updated {filename}")

def main():
    for fname in os.listdir(ARTICLES_DIR):
        if fname.endswith('.html'):
            update_article(os.path.join(ARTICLES_DIR, fname))

if __name__ == '__main__':
    main() 