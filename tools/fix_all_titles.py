#!/usr/bin/env python3
"""
סקריפט לעדכון כותרות המאמרים בפורמט: Ticker: Security | GICS Sector | GICS Sub-Industry
כולל קיצור כותרות ארוכות ל-70 תווים.
"""

import json
import os
import csv

MAX_TITLE_LEN = 70

# Load CSV data for Security names
csv_data = {}
try:
    with open('data/flat-ui__data', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_data[row['Tickers'].strip()] = row
except:
    print("⚠️ לא ניתן לטעון קובץ CSV - יושתמש רק בטיקר")

def extract_from_tags(tags):
    """Extract sector and sub-industry from tags"""
    sector = ""
    sub_industry = ""
    for tag in tags:
        if tag.startswith("סקטור: "):
            sector = tag.replace("סקטור: ", "").strip()
        elif tag.startswith("תעשייה: "):
            sub_industry = tag.replace("תעשייה: ", "").strip()
    return sector, sub_industry

def build_title(article):
    ticker = article.get('ticker', '').strip()
    if not ticker:
        return ""
    
    # Get Security name from CSV
    security = ""
    if ticker in csv_data:
        security = csv_data[ticker].get('Security', '').strip()
    
    # Get sector and sub-industry from tags
    tags = article.get('tags', [])
    sector, sub_industry = extract_from_tags(tags)
    
    # Build title
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
    metadata_file = "data/articles_metadata.json"
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
            if new_title and article.get('title', '') != new_title:
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