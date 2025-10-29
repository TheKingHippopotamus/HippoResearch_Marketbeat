# 🦛 MarketBit - Automated Market Research System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-green.svg)]()

## 📋 תוכן עניינים / Table of Contents

- [תיאור הפרויקט / Project Description](#תיאור-הפרויקט--project-description)
- [תכונות עיקריות / Key Features](#תכונות-עיקריות--key-features)
- [מבנה הפרויקט / Project Structure](#מבנה-הפרויקט--project-structure)
- [התקנה והפעלה / Installation & Setup](#התקנה-והפעלה--installation--setup)
- [שימוש / Usage](#שימוש--usage)
- [ארכיטקטורה / Architecture](#ארכיטקטורה--architecture)
- [טכנולוגיות / Technologies](#טכנולוגיות--technologies)
- [תרומה / Contributing](#תרומה--contributing)
- [רישיון / License](#רישיון--license)

---

## 🎯 תיאור הפרויקט / Project Description

**MarketBit** הוא מערכת אוטומטית לניתוח מחקרי שוק המבוססת על בינה מלאכותית. המערכת אוספת, מעבדת ומנתחת מידע פיננסי ממקורות שונים כדי ליצור דוחות מחקר מקצועיים על מניות.

**MarketBit** is an automated market research system powered by artificial intelligence. The system collects, processes, and analyzes financial information from various sources to generate professional research reports on stocks.

### 🎯 מטרות הפרויקט / Project Goals

- **איסוף אוטומטי** של מידע פיננסי ממקורות מהימנים
- **ניתוח מתקדם** באמצעות טכנולוגיות AI ו-NLP
- **יצירת תוכן** מקצועי ואיכותי בעברית
- **אוטומציה מלאה** של תהליך המחקר
- **ממשק משתמש** מודרני ונגיש

---

## ✨ תכונות עיקריות / Key Features

### 🔍 **איסוף נתונים חכם / Smart Data Collection**
- Web scraping אוטומטי מ-MarketBeat
- איסוף מידע על מאות מניות מ-S&P 500
- ניהול אוטומטי של מקורות נתונים

### 🤖 **עיבוד AI מתקדם / Advanced AI Processing**
- ניתוח טקסט מתקדם עם spaCy
- זיהוי ישויות פיננסיות (entities)
- ניתוח רגשות (sentiment analysis)
- סיווג תעשיות אוטומטי

### 📊 **ניתוח פיננסי / Financial Analysis**
- זיהוי מגמות שוק
- ניתוח סיכונים והזדמנויות
- השוואה בין מתחרים
- ניתוח הקשר זמני

### 🎨 **יצירת תוכן / Content Generation**
- יצירת מאמרים מקצועיים בעברית
- עיצוב HTML מודרני ורספונסיבי
- תבניות תוכן מותאמות אישית
- אופטימיזציה SEO

### 🔄 **אוטומציה מלאה / Full Automation**
- עיבוד אוטומטי של מניות
- ניהול גרסאות עם Git
- עדכון אוטומטי של מאגר הנתונים
- ניטור ביצועים

---

## 📁 מבנה הפרויקט / Project Structure

```
marketBit/
├── 📄 main.py                    # Entry point - נקודת הכניסה הראשית
├── 📄 requirements.txt           # Python dependencies - תלויות Python
├── 📄 index.html                # Main website - האתר הראשי
├── 📄 LICENSE                   # License file - קובץ רישיון
│
├── 🛠️ tools/                    # Core utilities - כלים מרכזיים
│   ├── config.py                # Configuration settings - הגדרות
│   ├── entity_analyzer.py       # AI text analysis - ניתוח טקסט AI
│   ├── logger.py                # Logging system - מערכת לוגים
│   ├── llm_processor.py         # LLM integration - אינטגרציה LLM
│   ├── html_template.py         # HTML generation - יצירת HTML
│   ├── text_processing.py       # Text processing - עיבוד טקסט
│   ├── ticker_data.py           # Ticker management - ניהול טיקרים
│   └── inject_js_cleaner.py     # JavaScript injection - הזרקת JavaScript
│
├── 📜 scripts/                  # Processing scripts - סקריפטים לעיבוד
│   ├── process_manager.py       # Main processing logic - לוגיקת עיבוד ראשית
│   ├── scrap_marketBeat_keypoints.py  # Web scraping - גריפת אתרים
│   ├── ui_ux_manager.py         # UI/UX management - ניהול ממשק
│   ├── filemanager.py           # File operations - פעולות קבצים
│   ├── github_automation.py     # Git automation - אוטומציה Git
│   └── json_manager.py          # JSON data management - ניהול נתוני JSON
│
├── 📊 data/                     # Data storage - אחסון נתונים
│   ├── articles_metadata.json   # Articles metadata - מטא-דאטה של מאמרים
│   └── flat-ui__data.csv        # Ticker database - בסיס נתוני טיקרים
│
├── 📰 articles/                 # Generated articles - מאמרים שנוצרו
│   └── [TICKER]_[DATE].html     # Individual articles - מאמרים בודדים
│
├── 📝 txt/                      # Text processing files - קבצי עיבוד טקסט
│   ├── [TICKER]_cleaned_[DATE].txt    # Cleaned text - טקסט מנוקה
│   └── [TICKER]_original_[DATE].txt   # Original text - טקסט מקורי
│
├── 🧠 entityAnalyzer_DB/        # AI analysis database - בסיס נתוני ניתוח AI
│   └── [TICKER]_entity_analysis_[DATE].json
│
├── 📋 processed_tickers/        # Processing tracking - מעקב עיבוד
│   ├── processed_[DATE].json    # Daily processed - מעובדים יומית
│   ├── unavailable_tickers.json # Unavailable tickers - טיקרים לא זמינים
│   └── last_clear_date.txt      # Last clear date - תאריך ניקוי אחרון
│
├── 🎨 templates/                # HTML templates - תבניות HTML
│   └── article_template.html    # Article template - תבנית מאמר
│
├── 🖼️ static/                   # Static assets - נכסים סטטיים
│   ├── logo.png                 # Logo - לוגו
│   └── x.png                    # X icon - אייקון X
│
├── 🧪 unit-test/                # Testing files - קבצי בדיקה
│   ├── entity_extractor.py      # Entity extraction tests - בדיקות זיהוי ישויות
│   ├── test_token_control.py    # Token control tests - בדיקות בקרת טוקנים
│   ├── test_professional_prompt.py  # Prompt testing - בדיקות הנחיות
│   └── run_single_ticker.py     # Single ticker testing - בדיקת טיקר בודד
│
├── 📚 logs-tracker/             # Log files - קבצי לוג
│   └── archives/                # Log archives - ארכיון לוגים
│
└── 🗄️ z-archives/               # Archive files - קבצי ארכיון
    └── [various backup files]   # Backup and archive files - קבצי גיבוי וארכיון
```

---

## 🚀 התקנה והפעלה / Installation & Setup

### ⚠️ **אזהרת אבטחה / Security Warning**

**זהו ריפוזיטורי public לצורך GitHub Pages. קבצים רגישים הוסרו או הוחלפו בדוגמאות.**

**This is a public repository for GitHub Pages purposes. Sensitive files have been removed or replaced with examples.**

### דרישות מערכת / System Requirements
- Python 3.8+
- Git
- Internet connection

### התקנה / Installation

```bash
# Clone the repository
git clone [repository-url]
cd marketBit

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy model (for entity analysis)
python -m spacy download en_core_web_trf
```

### הגדרות / Configuration

1. **העתק קובץ התצורה לדוגמה**:
   ```bash
   cp tools/config.example.py tools/config.py
   ```

2. **עדכן הגדרות ב-`tools/config.py`**:
   ```python
   LLM_MODEL_SETTINGS = {
       "model_name": "your-model-name-here",  # החלף עם המודל שלך
       "temperature": 0.7,
       "top_p": 0.9,
   }
   ```

3. **הוסף קבצי נתונים נדרשים**:
   - `data/flat-ui__data.csv` - בסיס נתוני טיקרים
   - `processed_tickers/` - תיקיית מעקב עיבוד
   - `entityAnalyzer_DB/` - תיקיית ניתוח AI

4. **הגדר נתיבי קבצים** במידת הצורך

---

## 💻 שימוש / Usage

### הפעלת המערכת / Running the System

```bash
# עיבוד כל הטיקרים הזמינים
python main.py

# עיבוד טיקר ספציפי
python main.py AAPL

# עיבוד טיקר ספציפי עם לוגים מפורטים
python main.py MSFT --verbose
```

### תהליך העיבוד / Processing Pipeline

1. **איסוף נתונים** - גריפת מידע מ-MarketBeat
2. **ניקוי טקסט** - הסרת תוכן מיותר
3. **ניתוח AI** - זיהוי ישויות וניתוח רגשות
4. **יצירת תוכן** - יצירת מאמר מקצועי
5. **עיצוב HTML** - עיצוב המאמר
6. **אופטימיזציה** - ניקוי JavaScript ואופטימיזציה
7. **שמירה** - שמירה למסד נתונים ו-Git

### ניהול קבצים / File Management

```bash
# ניקוי קבצים ישנים
python scripts/filemanager.py --cleanup

# גיבוי נתונים
python scripts/filemanager.py --backup

# שחזור מגיבוי
python scripts/filemanager.py --restore
```

---

## 🏗️ ארכיטקטורה / Architecture

### רכיבי המערכת / System Components

#### 🔧 **Core Tools (`tools/`)**
- **`entity_analyzer.py`**: ניתוח טקסט מתקדם עם spaCy
- **`llm_processor.py`**: אינטגרציה עם מודלי AI
- **`logger.py`**: מערכת לוגים מתקדמת
- **`config.py`**: ניהול הגדרות מרכזי

#### 📜 **Processing Scripts (`scripts/`)**
- **`process_manager.py`**: מנהל התהליך הראשי
- **`scrap_marketBeat_keypoints.py`**: גריפת נתונים
- **`ui_ux_manager.py`**: ניהול ממשק משתמש
- **`github_automation.py`**: אוטומציה Git

#### 📊 **Data Management**
- **`data/`**: אחסון נתונים מרכזי
- **`processed_tickers/`**: מעקב עיבוד
- **`entityAnalyzer_DB/`**: תוצאות ניתוח AI

### זרימת נתונים / Data Flow

```
Web Scraping → Text Cleaning → AI Analysis → Content Generation → HTML Creation → Optimization → Storage
```

---

## 🛠️ טכנולוגיות / Technologies

### **Backend Technologies**
- **Python 3.8+** - שפת התכנות הראשית
- **Selenium** - אוטומציה של דפדפן
- **BeautifulSoup4** - עיבוד HTML
- **spaCy** - עיבוד שפה טבעית
- **Requests** - בקשות HTTP

### **AI & ML**
- **spaCy NLP** - ניתוח טקסט מתקדם
- **Custom LLM Integration** - אינטגרציה עם מודלי AI
- **Entity Recognition** - זיהוי ישויות פיננסיות
- **Sentiment Analysis** - ניתוח רגשות

### **Frontend & Design**
- **HTML5/CSS3** - מבנה ועיצוב
- **JavaScript** - אינטראקטיביות
- **Responsive Design** - עיצוב רספונסיבי
- **Modern UI/UX** - ממשק משתמש מודרני

### **Data & Storage**
- **JSON** - אחסון נתונים מובנה
- **CSV** - נתוני טיקרים
- **Git** - ניהול גרסאות
- **File System** - אחסון קבצים

### **Automation & DevOps**
- **GitHub Automation** - אוטומציה Git
- **Logging System** - מערכת לוגים
- **Error Handling** - טיפול בשגיאות
- **Process Management** - ניהול תהליכים

---

## 🤝 תרומה / Contributing

### הנחיות לתרומה / Contribution Guidelines

1. **Fork** את הפרויקט
2. צור **branch** חדש (`git checkout -b feature/AmazingFeature`)
3. **Commit** את השינויים (`git commit -m 'Add some AmazingFeature'`)
4. **Push** ל-branch (`git push origin feature/AmazingFeature`)
5. פתח **Pull Request**

### סטנדרטי קוד / Code Standards

- השתמש ב-**Python PEP 8** style guide
- הוסף **docstrings** לכל פונקציות
- כתוב **unit tests** לפונקציות חדשות
- שמור על **backward compatibility**

### דיווח באגים / Bug Reports

אנא השתמש ב-Issues של GitHub לדיווח באגים או בקשות תכונות.

---

## 📄 רישיון / License

**כל הזכויות שמורות © 2024 Hippopotamus Research - Nir Elmaliah**

הקוד, התוכן, והעיצוב בפרויקט זה הם קנייניים ואינם קוד פתוח.
אין להעתיק, להפיץ, לשנות, להשתמש, או למסחר את הקוד או כל חלק ממנו, ללא אישור מפורש ובכתב מהיוצר.

**All rights reserved © 2024 Hippopotamus Research - Nir Elmaliah**

The code, content, and design in this project are proprietary and not open source.
You may not copy, distribute, modify, use, or commercialize any part of this code or content without explicit written permission from the author.

---

## 📞 יצירת קשר / Contact

- **יוצר / Creator**: Nir Elmaliah
- **ארגון / Organization**: Hippopotamus Research
- **שנה / Year**: 2024

---

## 🙏 תודות / Acknowledgments

- **MarketBeat** - מקור הנתונים הפיננסיים
- **spaCy** - כלי עיבוד השפה הטבעית
- **Selenium** - אוטומציה של דפדפן
- **קהילת Python** - כלים וספריות

---

<div align="center">

**🦛 MarketBit - מחקר שוק חכם ואוטומטי**  
**Smart & Automated Market Research**

</div> 






