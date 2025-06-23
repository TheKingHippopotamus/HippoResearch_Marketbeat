#!/usr/bin/env python3
"""
סקריפט להוספת תגים למטא-דאטה לפי GICS Sector ו-GICS Sub-Industry
"""

import json
import csv
import os
from collections import defaultdict

def load_csv_data():
    """טוען את נתוני ה-CSV עם הסקטורים והתעשיות"""
    csv_file = os.path.join("..", "data", "flat-ui__data-Thu Jun 19 2025.csv")
    ticker_data = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row['Tickers'].strip()
                sector = row['GICS Sector'].strip()
                sub_industry = row['GICS Sub-Industry'].strip()
                security = row['Security'].strip()
                
                ticker_data[ticker] = {
                    'sector': sector,
                    'sub_industry': sub_industry,
                    'security': security
                }
        print(f"✅ נטענו נתונים עבור {len(ticker_data)} טיקרים")
        return ticker_data
    except Exception as e:
        print(f"❌ שגיאה בטעינת CSV: {e}")
        return {}

def get_unique_sectors_and_industries(ticker_data):
    """מחזיר רשימה של כל הסקטורים והתעשיות הייחודיים"""
    sectors = set()
    industries = set()
    
    for data in ticker_data.values():
        if data['sector']:
            sectors.add(data['sector'])
        if data['sub_industry']:
            industries.add(data['sub_industry'])
    
    return sorted(list(sectors)), sorted(list(industries))

def add_tags_to_metadata():
    """מוסיף תגים למטא-דאטה לפי הסקטורים והתעשיות"""
    metadata_file = os.path.join("..", "data", "articles_metadata.json")
    
    # טעינת נתוני ה-CSV
    ticker_data = load_csv_data()
    if not ticker_data:
        return
    
    # קבלת רשימת הסקטורים והתעשיות
    sectors, industries = get_unique_sectors_and_industries(ticker_data)
    print(f"📊 נמצאו {len(sectors)} סקטורים ו-{len(industries)} תעשיות")
    
    # טעינת המטא-דאטה
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"📄 נטענו {len(metadata)} מאמרים מהמטא-דאטה")
    except Exception as e:
        print(f"❌ שגיאה בטעינת מטא-דאטה: {e}")
        return
    
    # הוספת תגים לכל מאמר
    updated_count = 0
    for article in metadata:
        ticker = article.get('ticker', '').strip()
        if ticker in ticker_data:
            data = ticker_data[ticker]
            
            # יצירת תגים
            tags = []
            
            # תג הסקטור
            if data['sector']:
                tags.append(f"סקטור: {data['sector']}")
            
            # תג התעשייה
            if data['sub_industry']:
                tags.append(f"תעשייה: {data['sub_industry']}")
            
            # תג הטיקר
            tags.append(f"טיקר: {ticker}")
            
            # עדכון המאמר
            if article.get('tags') != tags:
                article['tags'] = tags
                updated_count += 1
                print(f"✅ {ticker}: {', '.join(tags)}")
    
    # שמירת המטא-דאטה המעודכן
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 סיום! עודכנו {updated_count} מאמרים עם תגים")
        
        # הדפסת סטטיסטיקות
        print(f"\n📈 סטטיסטיקות:")
        print(f"   • סך הכל מאמרים: {len(metadata)}")
        print(f"   • מאמרים עם תגים: {updated_count}")
        print(f"   • סקטורים ייחודיים: {len(sectors)}")
        print(f"   • תעשיות ייחודיות: {len(industries)}")
        
    except Exception as e:
        print(f"❌ שגיאה בשמירת מטא-דאטה: {e}")

if __name__ == "__main__":
    add_tags_to_metadata() 