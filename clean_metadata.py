import json
import re
import os

def clean_summary_text(text):
    """Clean summary text by removing JSON artifacts and formatting issues"""
    if not text:
        return text
    
    # Remove JSON structure artifacts - more comprehensive cleaning
    text = re.sub(r'^\s*\{\s*"text":\s*"', '', text)
    text = re.sub(r'^\s*"text":\s*"', '', text)
    text = re.sub(r'^\s*\{\s*', '', text)
    text = re.sub(r'\s*\}\s*$', '', text)
    text = re.sub(r'^\s*"":\s*"', '', text)
    text = re.sub(r'"\s*,\s*"tags":\s*\[.*?\]\s*$', '', text)
    text = re.sub(r'"\s*,\s*"tags":\s*\[\s*\]\s*$', '', text)
    text = re.sub(r'"\s*$', '', text)
    
    # Remove markdown symbols
    text = re.sub(r'^#+\s*', '', text)  # Remove markdown headers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markdown
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic markdown
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)  # Remove all HTML tags
    
    # Remove newline characters and extra spaces
    text = re.sub(r'\\n', '\n', text)  # Convert \\n to actual newlines
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    return text

def clean_metadata_file():
    """Clean the metadata JSON file"""
    try:
        with open('articles_metadata.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned_count = 0
        for article in data:
            if 'summary' in article and article['summary']:
                original_summary = article['summary']
                cleaned_summary = clean_summary_text(original_summary)
                if cleaned_summary != original_summary:
                    article['summary'] = cleaned_summary
                    cleaned_count += 1
        
        with open('articles_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleaned {cleaned_count} summaries in metadata file")
        
    except Exception as e:
        print(f"❌ Error cleaning metadata: {e}")

if __name__ == "__main__":
    print("🧹 Starting cleanup process...")
    
    # Clean metadata file
    clean_metadata_file()
    
    print("✨ Cleanup completed!") 