#!/usr/bin/env python3
"""
סקריפט לעדכון כותרות המאמרים בפורמט: Ticker: Security | GICS Sector | GICS Sub-Industry
כולל קיצור כותרות ארוכות ל-70 תווים.
"""

import json
import os

MAX_TITLE_LEN = 70


def build_title(article):
    parts = []
    ticker = article.get('ticker', '').strip()
    if ticker:
        parts.append(ticker)
    security = article.get('Security', '').strip()
    sector = article.get('GICS Sector', '').strip()
    sub_industry = article.get('GICS Sub-Industry', '').strip()
    details = [s for s in [security, sector, sub_industry] if s]
    if details:
        title = f"{ticker}: " + " | ".join(details)
    else:
        title = ticker
    # קיצור אם צריך
    if len(title) > MAX_TITLE_LEN:
        title = title[:MAX_TITLE_LEN-1] + '…'
    return title

def fix_titles_to_metadata():
    metadata_file = os.path.join("..", "data", "articles_metadata.json")
    if not os.path.exists(metadata_file):
        print("❌ קובץ המטא-דאטה לא נמצא!")
        return
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"📊 נמצאו {len(metadata)} מאמרים לטיפול")
        fixed_count = 0
        for article in metadata:
            new_title = build_title(article)
            if article.get('title', '') != new_title:
                print(f"✅ {article.get('title','')} → {new_title}")
                article['title'] = new_title
                fixed_count += 1
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 סיום! עודכנו {fixed_count} כותרות מתוך {len(metadata)} מאמרים")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == "__main__":
    fix_titles_to_metadata() 