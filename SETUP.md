# 🔧 מדריך התקנה מפורט / Detailed Setup Guide

## ⚠️ **חשוב לדעת / Important Notice**

זהו ריפוזיטורי public לצורך GitHub Pages. הקוד המלא והנתונים הרגישים אינם כלולים כאן.

This is a public repository for GitHub Pages purposes. The complete code and sensitive data are not included here.

## 📋 **קבצים חסרים / Missing Files**

### קבצי נתונים / Data Files
- `data/flat-ui__data.csv` - בסיס נתוני טיקרים מ-S&P 500
- `processed_tickers/` - תיקיית מעקב עיבוד יומי
- `entityAnalyzer_DB/` - תיקיית ניתוח AI
- `txt/` - קבצי עיבוד טקסט
- `articles/` - מאמרים שנוצרו

### קבצי תצורה / Configuration Files
- `tools/config.py` - הגדרות LLM ומודלים
- `scripts/github_automation.py` - הגדרות אוטומציה Git

## 🚀 **הוראות התקנה מלאות / Complete Installation Instructions**

### שלב 1: הכנת סביבה / Environment Setup

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

# Install spaCy model
python -m spacy download en_core_web_trf
```

### שלב 2: הכנת קבצי תצורה / Configuration Setup

```bash
# Copy example configuration
cp tools/config.example.py tools/config.py

# Edit configuration with your settings
nano tools/config.py  # או עורך אחר
```

**תוכן נדרש ב-`tools/config.py`**:
```python
LLM_MODEL_SETTINGS = {
    "model_name": "your-actual-model-name",  # שם המודל האמיתי שלך
    "temperature": 0.7,
    "top_p": 0.9,
}
```

### שלב 3: הכנת נתונים / Data Preparation

#### יצירת בסיס נתוני טיקרים / Creating Ticker Database

צור קובץ `data/flat-ui__data.csv` עם המבנה הבא:
```csv
ticker,Security,GICS Sector,GICS Sub-Industry
AAPL,Apple Inc.,Information Technology,Technology Hardware Storage & Peripherals
MSFT,Microsoft Corporation,Information Technology,Systems Software
GOOGL,Alphabet Inc.,Communication Services,Interactive Media & Services
...
```

#### יצירת תיקיות נדרשות / Creating Required Directories

```bash
# Create required directories
mkdir -p processed_tickers
mkdir -p entityAnalyzer_DB
mkdir -p txt
mkdir -p articles
mkdir -p logs-tracker/archives

# Create initial tracking files
echo '{"processed": [], "date": "'$(date +%Y-%m-%d)'"}' > processed_tickers/processed_$(date +%Y%m%d).json
echo '[]' > processed_tickers/unavailable_tickers.json
echo $(date +%Y-%m-%d) > processed_tickers/last_clear_date.txt
```

### שלב 4: הגדרת אוטומציה Git / Git Automation Setup

צור קובץ `scripts/github_automation.py` עם הגדרות Git שלך:

```python
import subprocess
import os

def commit_and_push_changes(ticker):
    """Commit and push changes to GitHub"""
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit with ticker info
        commit_message = f"Update {ticker} analysis - {os.popen('date').read().strip()}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to remote
        subprocess.run(['git', 'push'], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        return False
```

### שלב 5: בדיקת התקנה / Installation Verification

```bash
# Test single ticker processing
python main.py AAPL

# Check if files are created
ls -la articles/
ls -la txt/
ls -la entityAnalyzer_DB/
```

## 🔍 **פתרון בעיות / Troubleshooting**

### שגיאות נפוצות / Common Errors

#### 1. **ModuleNotFoundError: No module named 'tools'**
```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. **spaCy model not found**
```bash
# Install spaCy model
python -m spacy download en_core_web_trf
```

#### 3. **Missing data files**
```bash
# Create sample data structure
python -c "
import json
import os

# Create sample ticker data
sample_data = [
    {'ticker': 'AAPL', 'Security': 'Apple Inc.', 'GICS Sector': 'Information Technology'},
    {'ticker': 'MSFT', 'Security': 'Microsoft Corporation', 'GICS Sector': 'Information Technology'}
]

# Save to CSV
with open('data/flat-ui__data.csv', 'w') as f:
    f.write('ticker,Security,GICS Sector\n')
    for item in sample_data:
        f.write(f'{item[\"ticker\"]},{item[\"Security\"]},{item[\"GICS Sector\"]}\n')

print('Sample data created successfully!')
"
```

## 📞 **תמיכה / Support**

לשאלות או בעיות, צור קשר עם Nir Elmaliah.

For questions or issues, contact Nir Elmaliah.

---

**הערה**: מדריך זה מיועד למשתמשים שמעוניינים להריץ את המערכת המלאה. הריפוזיטורי Public מכיל רק את המבנה והקוד הבסיסי.

**Note**: This guide is for users who want to run the complete system. The public repository contains only the structure and basic code. 