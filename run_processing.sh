#!/bin/bash

# סקריפט הרצה לעיבוד טיקרים
echo "🚀 מתחיל עיבוד טיקרים מקובץ JSON..."
echo "המערכת תעבד כל טיקר בנפרד ותבצע commit אחרי כל אחד"
echo ""

# בדיקה שקובץ tickers.json קיים
if [ ! -f "tickers.json" ]; then
    echo "❌ קובץ tickers.json לא נמצא!"
    echo "אנא צור קובץ tickers.json עם רשימת הטיקרים"
    exit 1
fi

# הצגת הטיקרים שיעובדו
echo "📋 הטיקרים שיעובדו:"
python3 -c "
import json
with open('tickers.json', 'r') as f:
    data = json.load(f)
    tickers = data.get('tickers', [])
    for i, ticker in enumerate(tickers, 1):
        print(f'{i}. {ticker}')
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