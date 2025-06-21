import json
import re
import os
import sys
from datetime import datetime

# הוספת הנתיב הראשי למערכת כדי שנוכל לקרוא את קובץ ה-CSV
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.llm_processor import clean_llm_text

def clean_summary_text(text):
    """Clean summary text by removing JSON artifacts and formatting issues"""
    # Use the unified cleaning function from llm_processor
    return clean_llm_text(text)

def clean_metadata_file():
    """Clean the metadata JSON file"""
    try:
        # שימוש בנתיב יחסי לתיקייה הראשית
        metadata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'articles_metadata.json')
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned_count = 0
        for article in data:
            if 'summary' in article and article['summary']:
                original_summary = article['summary']
                cleaned_summary = clean_summary_text(original_summary)
                if cleaned_summary != original_summary:
                    article['summary'] = cleaned_summary
                    cleaned_count += 1
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleaned {cleaned_count} summaries in metadata file")
        
    except Exception as e:
        print(f"❌ Error cleaning metadata: {e}")

if __name__ == "__main__":
    print("🧹 Starting cleanup process...")
    
    # Clean metadata file
    clean_metadata_file()
    
    print("✨ Cleanup completed!") 