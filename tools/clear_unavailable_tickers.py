#!/usr/bin/env python3
"""
סקריפט לניקוי רשימת הטיקרים הלא זמינים
מאפשר סריקה חוזרת של טיקרים שלא היו זמינים בימים קודמים
"""

import json
import os
from datetime import datetime

def clear_unavailable_tickers():
    """מנקה את קובץ unavailable_tickers.json"""
    file_path = 'processed_tickers/unavailable_tickers.json'
    
    try:
        # בדוק אם הקובץ קיים
        if os.path.exists(file_path):
            # גבה את הקובץ הנוכחי
            backup_path = f'processed_tickers/unavailable_tickers_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # שמור גיבוי
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            
            print(f"📋 גיבוי נשמר: {backup_path}")
            print(f"📊 מספר טיקרים בגיבוי: {len(current_data)}")
        
        # צור קובץ ריק חדש
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        print("✅ רשימת הטיקרים הלא זמינים נוקתה בהצלחה!")
        print("🔄 כעת ניתן לסרוק מחדש את כל הטיקרים")
        
    except Exception as e:
        print(f"❌ שגיאה בניקוי הקובץ: {e}")

def show_current_status():
    """מציג את הסטטוס הנוכחי של unavailable_tickers.json"""
    file_path = 'processed_tickers/unavailable_tickers.json'
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"📊 מספר טיקרים לא זמינים כרגע: {len(data)}")
            if data:
                print("📋 דוגמאות לטיקרים לא זמינים:")
                for ticker in data[:10]:  # הצג רק 10 ראשונים
                    print(f"   - {ticker}")
                if len(data) > 10:
                    print(f"   ... ועוד {len(data) - 10} טיקרים")
        else:
            print("📊 הקובץ לא קיים - אין טיקרים לא זמינים")
    except Exception as e:
        print(f"❌ שגיאה בקריאת הקובץ: {e}")

if __name__ == "__main__":
    print("🧹 ניקוי רשימת הטיקרים הלא זמינים")
    print("=" * 50)
    
    # הצג סטטוס נוכחי
    show_current_status()
    print()
    
    # שאל את המשתמש אם להמשיך
    response = input("האם לנקות את הרשימה? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'כן']:
        clear_unavailable_tickers()
    else:
        print("❌ הפעולה בוטלה") 