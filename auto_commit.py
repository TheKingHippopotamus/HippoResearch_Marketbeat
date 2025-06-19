#!/usr/bin/env python3
"""
סקריפט לניטור אוטומטי של קבצי HTML חדשים ועדכון הריפוזיטורי
"""

import os
import time
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_commit.log'),
        logging.StreamHandler()
    ]
)

class HTMLFileHandler(FileSystemEventHandler):
    def __init__(self, articles_dir, repo_dir):
        self.articles_dir = articles_dir
        self.repo_dir = repo_dir
        self.last_processed = set()
        self.processing = False
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        if str(event.src_path).endswith('.html'):
            self.handle_new_html(event.src_path)
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if str(event.src_path).endswith('.html'):
            self.handle_new_html(event.src_path)
    
    def handle_new_html(self, file_path):
        """מטפל בקובץ HTML חדש"""
        if self.processing:
            logging.info(f"כבר מעבד קובץ אחר, דילוג על: {file_path}")
            return
            
        filename = os.path.basename(file_path)
        if filename in self.last_processed:
            return
            
        logging.info(f"זוהה קובץ HTML חדש: {filename}")
        
        # המתנה של 5 שניות
        logging.info("ממתין 5 שניות לפני עדכון הריפוזיטורי...")
        time.sleep(5)
        
        try:
            self.processing = True
            self.update_repository(filename)
            self.last_processed.add(filename)
            logging.info(f"הריפוזיטורי עודכן בהצלחה עבור: {filename}")
        except Exception as e:
            logging.error(f"שגיאה בעדכון הריפוזיטורי: {e}")
        finally:
            self.processing = False
    
    def update_repository(self, filename):
        """מעדכן את הריפוזיטורי עם הקובץ החדש"""
        try:
            # מעבר לתיקיית הפרויקט
            os.chdir(self.repo_dir)
            
            # בדיקה אם יש שינויים
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                logging.info("אין שינויים חדשים לעדכן")
                return
            
            # הוספת כל השינויים
            logging.info("מוסיף קבצים ל-git...")
            subprocess.run(['git', 'add', '.'], check=True)
            
            # יצירת commit
            commit_message = f"הוספת כתבה חדשה: {filename} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            logging.info(f"יוצר commit: {commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # push ל-GitHub
            logging.info("דוחף ל-GitHub...")
            subprocess.run(['git', 'push'], check=True)
            
            logging.info("הריפוזיטורי עודכן בהצלחה!")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"שגיאה בפקודת git: {e}")
            raise
        except Exception as e:
            logging.error(f"שגיאה כללית: {e}")
            raise

def main():
    # הגדרת נתיבים
    current_dir = os.path.dirname(os.path.abspath(__file__))
    articles_dir = os.path.join(current_dir, 'articles')
    repo_dir = current_dir
    
    # בדיקה שהתיקיות קיימות
    if not os.path.exists(articles_dir):
        logging.error(f"תיקיית articles לא נמצאה: {articles_dir}")
        return
    
    if not os.path.exists(os.path.join(repo_dir, '.git')):
        logging.error(f"תיקיית git לא נמצאה: {repo_dir}")
        return
    
    logging.info(f"מתחיל ניטור תיקיית articles: {articles_dir}")
    logging.info(f"תיקיית פרויקט: {repo_dir}")
    
    # יצירת event handler
    event_handler = HTMLFileHandler(articles_dir, repo_dir)
    
    # יצירת observer
    observer = Observer()
    observer.schedule(event_handler, articles_dir, recursive=False)
    
    try:
        # התחלת הניטור
        observer.start()
        logging.info("הניטור התחיל. לחץ Ctrl+C לעצירה...")
        
        # המתנה אינסופית
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("מקבל אות עצירה...")
        observer.stop()
    
    observer.join()
    logging.info("הניטור הופסק")

if __name__ == "__main__":
    main() 