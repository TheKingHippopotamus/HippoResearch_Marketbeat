import os
import re
from pathlib import Path

def extract_title_from_html(html):
    match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else None

def replace_title_in_html(html, new_title):
    if re.search(r'<title>.*?</title>', html, re.IGNORECASE | re.DOTALL):
        return re.sub(r'(<title>)(.*?)(</title>)', f'\\1{new_title}\\3', html, count=1, flags=re.IGNORECASE | re.DOTALL)
    else:
        # No <title> tag, insert after <head>
        return re.sub(r'(<head[^>]*>)', r'\1\n<title>' + new_title + '</title>', html, count=1, flags=re.IGNORECASE)

def restore_titles_from_backup():
    articles_dir = Path("articles")
    html_files = list(articles_dir.glob("*.html"))
    for html_file in html_files:
        backup_file = html_file.with_suffix(html_file.suffix + ".backup")
        if not backup_file.exists():
            print(f"❌ No backup for {html_file.name}, skipping.")
            continue
        with open(backup_file, "r", encoding="utf-8") as f:
            backup_html = f.read()
        orig_title = extract_title_from_html(backup_html)
        if not orig_title:
            print(f"❌ No <title> found in backup for {html_file.name}, skipping.")
            continue
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        new_html = replace_title_in_html(html, orig_title)
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"✅ Restored title for {html_file.name}: {orig_title}")

if __name__ == "__main__":
    print("🔄 Restoring original <title> tags from backups...")
    restore_titles_from_backup()
    print("✨ Done!") 