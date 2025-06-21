# תרשים זרימה של האפליקציה

קובץ זה מכיל את התרשים המלא של ה-flow של האפליקציה marketBit.

## איך ליצור תמונה מהתרשים

### אפשרות 1: Mermaid Live Editor (הכי קל)
1. לך ל: https://mermaid.live/
2. העתק את התוכן מקובץ `flow_diagram.mmd`
3. הדבק בעורך
4. לחץ על "Download PNG" או "Download SVG"

### אפשרות 2: GitHub
1. העלה את הקובץ `flow_diagram.mmd` ל-GitHub
2. GitHub יציג את התרשים אוטומטית
3. לחץ קליק ימני -> "Save image as..."

### אפשרות 3: VS Code עם הרחבה
1. התקן את ההרחבה "Mermaid Preview"
2. פתח את הקובץ `flow_diagram.mmd`
3. לחץ על "Open Preview"

### אפשרות 4: Command Line (עם Node.js)
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i flow_diagram.mmd -o flow_diagram.png
```

## תיאור התרשים

התרשים מראה את הזרימה המלאה של האפליקציה:

1. **התחלה** - הפעלת main.py
2. **טעינת נתונים** - קריאת CSV וטעינת רשימת טיקרים
3. **סקרייפינג** - חילוץ טקסט מהאתר
4. **עיבוד LLM** - עיבוד עם מודל הבינה המלאכותית
5. **בניית HTML** - יצירת כתבה מעוצבת
6. **שמירת קבצים** - שמירת התוצאות
7. **מטא-דאטה** - עדכון מידע על הכתבה
8. **Git operations** - commit ו-push

## צבעים בתרשים

- 🔵 **כחול בהיר** - התחלה וניהול תהליך
- 🟢 **ירוק** - סיום מוצלח
- 🟡 **צהוב** - עיבוד LLM
- 🟣 **סגול** - עיצוב HTML
- 🟢 **ירוק בהיר** - Git operations
- 🟡 **צהוב בהיר** - ניקוי מטא-דאטה

## קבצים מעורבים

- **main.py** - ניהול התהליך הראשי
- **llm_processor.py** - עיבוד LLM וניקוי טקסט
- **html_template.py** - בניית HTML מעוצב
- **clean_metadata.py** - ניקוי מטא-דאטה (אופציונלי) 