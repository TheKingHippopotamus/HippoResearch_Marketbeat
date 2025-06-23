#!/usr/bin/env python3
"""
סקריפט לתיקון כל הכותרות עם סימן שאלה
"""

import json
import os

def fix_all_article_titles():
    """תקן את כל הכותרות עם סימן שאלה"""
    
    # נתיב לקובץ המטא-דאטה
    metadata_file = os.path.join("data", "articles_metadata.json")
    
    if not os.path.exists(metadata_file):
        print("❌ קובץ המטא-דאטה לא נמצא!")
        return
    
    try:
        # טען את המטא-דאטה
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"📊 נמצאו {len(metadata)} מאמרים לטיפול")
        
        # ספור כמה כותרות תוקנו
        fixed_count = 0
        
        # עבור על כל המאמרים
        for article in metadata:
            if 'title' in article:
                original_title = article['title']
                new_title = original_title
                
                # תיקון 1: הסר רווחים מיותרים אחרי "סיקור יומי"
                if "סיקור יומי " in new_title:
                    new_title = new_title.replace("סיקור יומי ", "סיקור יומי")
                
                # תיקון 2: הסר סימן שאלה אחרי "סיקור יומי"
                if "סיקור יומי ?" in new_title:
                    new_title = new_title.replace("סיקור יומי ?", "סיקור יומי")
                
                # תיקון 3: הסר רווחים מיותרים לפני סימן שאלה
                if "סיקור יומי  ?" in new_title:
                    new_title = new_title.replace("סיקור יומי  ?", "סיקור יומי")
                
                # תיקון 4: הסר סימן שאלה אחרי "סיקור יומי" (ללא רווח)
                if "סיקור יומי?" in new_title:
                    new_title = new_title.replace("סיקור יומי?", "סיקור יומי")
                
                # אם השתנה משהו, עדכן את הכותרת
                if new_title != original_title:
                    article['title'] = new_title
                    fixed_count += 1
                    print(f"✅ תוקן: {original_title} → {new_title}")
        
        # שמור את המטא-דאטה המתוקנת
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 סיום! תוקנו {fixed_count} כותרות מתוך {len(metadata)} מאמרים")
        
        # בדיקה נוספת
        print("\n🔍 בדיקה נוספת - חיפוש כותרות עם סימן שאלה:")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata_check = json.load(f)
        
        remaining_issues = 0
        for article in metadata_check:
            if 'title' in article and '?' in article['title']:
                print(f"⚠️  עדיין יש בעיה: {article['title']}")
                remaining_issues += 1
        
        if remaining_issues == 0:
            print("✅ כל הכותרות נקיות!")
        else:
            print(f"⚠️  נשארו {remaining_issues} כותרות עם בעיות")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == "__main__":
    fix_all_article_titles() 