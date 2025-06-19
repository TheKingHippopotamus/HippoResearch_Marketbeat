# 📰 Hippopotamus Research — מערכת כתבות כלכליות אוטומטית

מערכת אוטומטית ליצירת, עיבוד ופרסום כתבות כלכליות מבוססות בינה מלאכותית, עם תמיכה מלאה ב-GitHub Pages, ניהול טיקרים, אוטומציה מלאה, עיצוב מודרני, וממשק חיפוש.

---

## 📢 Follow 
- [Twitter/X של Hippopotamus Research](https://x.com/LmlyhNyr)

---

## 📁 מבנה הפרויקט
```
marketBit/
├── articles/                # כתבות HTML בלבד
├── assets/
│   └── images/              # לוגו, אייקונים
├── data/                    # קבצי נתונים: JSON, טקסט מקור/מעובד
│   ├── articles_metadata.json
│   ├── tickers.json
│   ├── unavailable_tickers.json
│   ├── processed_YYYYMMDD.json
│   └── [TICKER]_original.txt / [TICKER]_processed.txt
├── scripts/                 # כל הסקריפטים (Python, shell)
│   ├── main.py
│   ├── llm_processor.py
│   ├── html_template.py
│   ├── llm_prompt.py
│   ├── auto_commit.py
│   ├── run_processing.sh
│   └── run_auto_commit.sh
├── install_scripts/         # סקריפטי התקנה אוטומטיים
│   ├── install.sh
│   └── install.ps1
├── index.html               # דף הבית הראשי
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ התקנה והפעלה

### א. התקנה אוטומטית (מומלץ)
- **macOS/Linux:**
  ```bash
  cd install_scripts
  bash install.sh
  ```
- **Windows:**
  ```powershell
  cd install_scripts
  powershell -ExecutionPolicy Bypass -File install.ps1
  ```
- הסקריפט יטפל בכל התלויות: Python, pip, Ollama, aya-expanse:8b, venv, requirements.

### ב. התקנה ידנית (למתקדמים)
1. התקן Python 3.8+, pip, ו-virtualenv
2. התקן Ollama לפי [הוראות האתר](https://ollama.com/download)
3. משוך את המודל:
   ```bash
   ollama pull aya-expanse:8b
   ```
4. צור סביבה וירטואלית:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # ב-Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. ודא ש-Ollama רץ:
   ```bash
   ollama serve
   ```
6. הרץ את המערכת כרגיל (ראה בהמשך)

---

## 🤖 שימוש ב-Ollama והמודל aya-expanse:8b
- עיבוד הטקסטים מתבצע באמצעות [Ollama](https://ollama.com/) שרץ לוקלית על המחשב שלך.
- המערכת משתמשת במודל **aya-expanse:8b** (ראה scripts/llm_processor.py).
- יש להפעיל את Ollama לפני הרצת המערכת:
  ```bash
  ollama serve
  ```
- הסקריפט יתחבר ל-Ollama בכתובת http://localhost:11434 וישלח את הטקסט לעיבוד.
- אם Ollama לא רץ, תופעל לוגיקת fallback פנימית.

---

## 🚀 תכונות עיקריות
- **סקרייפינג אוטומטי** של חדשות ממקורות מקצועיים (MarketBeat, Finviz, Briefing.com, Zacks ועוד)
- **עיבוד טקסט עם LLM** (מודל aya-expanse:8b)
- **שמירת כתבות מעוצבות** ב-HTML בתיקיית `articles/`
- **ניהול מטא-דאטה** ב-`data/articles_metadata.json`
- **אינדקס סטטי** עם חיפוש, סינון, גלילה אופקית, כרטיסים רספונסיביים
- **ניהול טיקרים חכם**: tickers.json, לוג יומי, unavailable, מניעת כפילויות
- **אוטומציה מלאה**: shell scripts, auto_commit, git integration
- **עיצוב מקצועי**: RTL, Newsletter, דיסקליימר, תמיכה במובייל

---

## 📊 ניהול טיקרים
- **tickers.json**: רשימת הטיקרים לעיבוד (מבנה: { "tickers": [ ... ] })
- **unavailable_tickers.json**: טיקרים שלא ניתן לעבד (נוצר אוטומטית)
- **processed_YYYYMMDD.json**: לוג טיקרים שעובדו היום (נוצר אוטומטית)
- **אין כפילויות**: כל טיקר יעובד פעם אחת ביום בלבד

---

## 📝 עיבוד כתבות
- **מקור**: סקרייפינג חדשות ממקורות מגוונים
- **עיבוד**: LLM (aya-expanse:8b) מסכם, מנתח ומייצר טקסט מקצועי
- **קבצי טקסט**: נשמרים ב-`data/` כ-[TICKER]_original.txt ו-[TICKER]_processed.txt
- **HTML**: כתבה מעוצבת נשמרת ב-`articles/`
- **מטא-דאטה**: כל כתבה מתועדת ב-`data/articles_metadata.json`

---

## 🎨 עיצוב וממשק
- **RTL מלא** ותמיכה בעברית
- **כרטיסי כתבות רספונסיביים** עם גלילה אופקית במובייל
- **חיפוש וסינון** לפי טיקר
- **Newsletter** מובנה (iframe)
- **דיסקליימר מקצועי** (כולל אזהרת שגיאות AI)
- **עיצוב אחיד** בין דפי כתבה לאינדקס
- **הדגשת כותרות פסקה** (subtle highlight)

---

## 🌐 פרסום ב-GitHub Pages
1. העלה את כל התיקיות והקבצים ל-repository
2. ודא ש-`index.html` בשורש
3. הגדר את GitHub Pages ל-root של ה-main branch
4. כל commit דוחף כתבות חדשות לאתר

---

## 🔧 התאמות ושדרוגים
- ניתן להוסיף/להסיר טיקרים ב-`data/tickers.json`
- ניתן להרחיב את הסקריפטים ב-`scripts/`
- כל נתיב לקובץ עודכן למבנה החדש — יש לעדכן כל קוד חיצוני בהתאם

---

## 🚨 פתרון בעיות
- **שגיאות סקרייפינג**: טיקר יתווסף אוטומטית ל-unavailable
- **בעיות Git**: ודא הרשאות, branch, ו-remote
- **בעיות LLM**: ודא זמינות מודל
- **הרצת סקריפטים**: ודא שאתה ב-scripts/

---

## 🛡️ רישיון

**עברית:**
כל הזכויות שמורות © 2024 Hippopotamus Research - Nir Elmaliah
הקוד, התוכן, והעיצוב בפרויקט זה הם קנייניים ואינם קוד פתוח. אין להעתיק, להפיץ, לשנות, להשתמש, או למסחר את הקוד או כל חלק ממנו, ללא אישור מפורש ובכתב מהיוצר. הפרה של תנאים אלו עלולה להוביל להליכים משפטיים.

**English:**
All rights reserved © 2024 Hippopotamus Research - Nir Elmaliah
The code, content, and design in this project are proprietary and not open source. You may not copy, distribute, modify, use, or commercialize any part of this code or content without explicit written permission from the author. Violation of these terms may result in legal action.

לפרטים מלאים ראה קובץ [LICENSE](LICENSE)

---

**הערה מקצועית**: המערכת מיועדת למחקר/למידה בלבד. ייתכנו טעויות ניסוח/תרגום/עובדות עקב שימוש ב-AI. יש להצליב מידע עם מקורות נוספים. אין לראות בניתוחים המלצה לפעולה. 