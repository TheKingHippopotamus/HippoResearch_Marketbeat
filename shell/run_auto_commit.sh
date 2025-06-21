#!/bin/bash

# סקריפט הרצה לניטור אוטומטי
echo "מתחיל ניטור אוטומטי של תיקיית articles..."
echo "הסקריפט יזהה קבצי HTML חדשים ויעדכן את הריפוזיטורי אוטומטית"
echo "לעצירה לחץ Ctrl+C"
echo ""

# הפעלת הסקריפט
python3 shell/auto_commit.py 