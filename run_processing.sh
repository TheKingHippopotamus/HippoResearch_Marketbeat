#!/bin/bash

# סקריפט הרצה לעיבוד טיקרים
echo "🚀 מתחיל עיבוד טיקרים מקובץ CSV..."
echo "המערכת תעבד כל טיקר בנפרד ותבצע commit אחרי כל אחד"
echo ""

# בדיקה שקובץ CSV קיים
if [ ! -f "data/flat-ui__data-Thu Jun 19 2025.csv" ]; then
    echo "❌ קובץ CSV לא נמצא!"
    echo "אנא וודא שקובץ data/flat-ui__data-Thu Jun 19 2025.csv קיים"
    exit 1
fi

# הצגת הטיקרים שיעובדו
echo "📋 הטיקרים שיעובדו (מתוך קובץ CSV):"
python3 -c "
import csv
import os
csv_path = 'data/flat-ui__data-Thu Jun 19 2025.csv'
if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tickers = [row['Tickers'] for row in reader if row.get('Tickers', '').strip()]
        print(f'נמצאו {len(tickers)} טיקרים בקובץ CSV')
        print('דוגמאות לטיקרים:')
        for i, ticker in enumerate(tickers[:10], 1):
            print(f'{i}. {ticker}')
        if len(tickers) > 10:
            print(f'... ועוד {len(tickers) - 10} טיקרים')
else:
    print('❌ קובץ CSV לא נמצא')
"

echo ""
echo "התחל עיבוד? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "התחלת עיבוד..."
    python3 main.py
else
    echo "העיבוד בוטל"
fi 