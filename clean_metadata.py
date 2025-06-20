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

def clean_html_content(html_content):
    """Clean HTML content by removing JSON artifacts from all <p>...</p> blocks"""
    # Pattern to find JSON-like content inside <p>...</p>
    def clean_p_tag(match):
        p_content = match.group(1)
        # Try to extract the text part from JSON if present
        json_match = re.search(r'\{\s*"text":\s*"(.*?)"(?:,\s*"tags":\s*\[.*?\])?\s*\}', p_content, re.DOTALL)
        if json_match:
            clean_text = json_match.group(1)
        else:
            clean_text = p_content
        # Clean up any remaining artifacts
        clean_text = clean_summary_text(clean_text)
        return f'<p>{clean_text}</p>'
    # Replace all <p>...</p> blocks
    cleaned_html = re.sub(r'<p>(.*?)</p>', clean_p_tag, html_content, flags=re.DOTALL)
    return cleaned_html

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

def clean_html_files():
    """Clean all HTML files in the articles directory"""
    articles_dir = 'articles'
    if not os.path.exists(articles_dir):
        print(f"❌ Articles directory not found: {articles_dir}")
        return
    
    html_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]
    cleaned_count = 0
    
    for html_file in html_files:
        file_path = os.path.join(articles_dir, html_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean the content
            cleaned_content = clean_html_content(content)
            
            # Only write if content changed
            if cleaned_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                cleaned_count += 1
                print(f"✅ Cleaned: {html_file}")
            
        except Exception as e:
            print(f"❌ Error cleaning {html_file}: {e}")
    
    print(f"🎉 Cleaned {cleaned_count} HTML files out of {len(html_files)} total files")

if __name__ == "__main__":
    print("🧹 Starting cleanup process...")
    
    # Clean metadata file
    clean_metadata_file()
    
    # Clean HTML files
    clean_html_files()
    
    print("✨ Cleanup completed!") 