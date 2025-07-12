
import json
import shutil
import os
from datetime import datetime
import re
import subprocess
import sys 
from scripts.logger import log_stage, setup_logging
logger = setup_logging()

from scripts.llm_processor import convert_tagged_text_to_html




def copy_static_files(output_dir):
    """Copy static files (logo, x icon) to output directory"""
    try:
        static_dir = "static"
        if os.path.exists(static_dir):
            # Copy logo.png
            logo_src = os.path.join(static_dir, "logo.png")
            logo_dst = os.path.join(output_dir, "logo.png")
            if os.path.exists(logo_src):
                shutil.copy2(logo_src, logo_dst)
                logger.info(f"✅ Copied logo.png to {output_dir}")
            
            # Copy x.png
            x_src = os.path.join(static_dir, "x.png")
            x_dst = os.path.join(output_dir, "x.png")
            if os.path.exists(x_src):
                shutil.copy2(x_src, x_dst)
                logger.info(f"✅ Copied x.png to {output_dir}")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not copy static files: {e}")




def auto_fix_article_html(ticker):
    """מתקן אוטומטית את עיצוב המאמר לפני עדכון הריפוזיטורי"""
    current_date = datetime.now().strftime("%Y%m%d")
    html_path = f"articles/{ticker}_{current_date}.html"
    txt_path = f"txt/{ticker}_processed_{current_date}.txt"
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            processed = f.read()
        html_content = convert_tagged_text_to_html(processed)
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        # החלף את התוכן בתוך <div class="article-content-text">...</div>
        new_html = re.sub(
            r'(<div class="article-content-text">)[\s\S]*?(</div>)',
            f'\\1\n{html_content}\n\\2',
            html
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_html)
    except Exception as e:
        logger.error(f"❌ Auto-fix failed for {ticker}: {e}")

@log_stage("JS_INJECT")
def run_js_cleaner_on_file(ticker):
    """הפעל את הניטור האוטומטי על קובץ HTML חדש לפני commit"""
    current_date = datetime.now().strftime("%Y%m%d")
    html_path = f"articles/{ticker}_{current_date}.html"
    
    try:
        logger.info(f"🧹 Running JavaScript cleaner on {ticker}...")
        
        # הפעל את הסקריפט ישירות על הקובץ
        result = subprocess.run([
            sys.executable, "inject_js_cleaner.py", 
            "--file", html_path, 
            "--no-backup"  # אל תיצור גיבוי נוסף
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ JavaScript cleaner completed for {ticker}")
            return True
        else:
            logger.warning(f"⚠️ JavaScript cleaner warning for {ticker}: {result.stderr}")
            return True  # נמשיך גם אם יש אזהרה
    except Exception as e:
        logger.error(f"❌ Error running JavaScript cleaner for {ticker}: {e}")
        return False

def check_and_clear_unavailable_tickers():
    """בדוק אם זה יום חדש ונקה את רשימת הטיקרים הלא זמינים"""
    today = datetime.now().strftime('%Y%m%d')
    last_clear_file = 'processed_tickers/last_clear_date.txt'
    
    try:
        # בדוק מתי הייתה הניקוי האחרון
        if os.path.exists(last_clear_file):
            with open(last_clear_file, 'r') as f:
                last_clear_date = f.read().strip()
            
            # אם זה אותו יום, אל תעשה כלום
            if last_clear_date == today:
                return
        
        # זה יום חדש - נקה את הרשימה
        unavailable_file = 'processed_tickers/unavailable_tickers.json'
        if os.path.exists(unavailable_file):
            # גבה את הקובץ הנוכחי
            backup_path = f'processed_tickers/unavailable_tickers_backup_{today}.json'
            with open(unavailable_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            if current_data:  # רק אם יש נתונים לגבות
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=2)
                logger.info(f"📋 גיבוי נשמר: {backup_path}")
                logger.info(f"📊 מספר טיקרים בגיבוי: {len(current_data)}")
        
        # צור קובץ ריק חדש
        with open(unavailable_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        # שמור את התאריך הנוכחי
        with open(last_clear_file, 'w') as f:
            f.write(today)
        
        logger.info("🧹 רשימת הטיקרים הלא זמינים נוקתה אוטומטית ליום החדש")
        logger.info("🔄 כעת ניתן לסרוק מחדש את כל הטיקרים")
        
    except Exception as e:
        logger.error(f"❌ שגיאה בניקוי אוטומטי: {e}")
