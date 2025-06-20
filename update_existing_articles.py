#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from datetime import datetime
from llm_processor import convert_markdown_to_html

def update_existing_articles():
    """Update all existing articles with new markdown conversion and consistent formatting"""
    
    # Load metadata
    with open('articles_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    articles_dir = "articles"
    updated_count = 0
    
    print(f"🔄 Starting update of existing articles...")
    print(f"📁 Found {len(metadata)} articles to update")
    
    for entry in metadata:
        ticker = entry['ticker']
        filename = entry['filename']
        filepath = os.path.join(articles_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️ File not found: {filename}")
            continue
            
        try:
            # Read the existing HTML file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the article content from the HTML
            # Look for the article-content div
            article_match = re.search(r'<div class="article-content">(.*?)</div>', content, re.DOTALL)
            if not article_match:
                print(f"⚠️ Could not find article content in {filename}")
                continue
                
            article_content = article_match.group(1)
            
            # Clean the content - remove existing HTML tags
            clean_content = re.sub(r'<[^>]+>', '', article_content)
            clean_content = re.sub(r'&[^;]+;', '', clean_content)  # Remove HTML entities
            clean_content = clean_content.strip()
            
            # Apply the new markdown conversion
            converted_content = convert_markdown_to_html(clean_content)
            
            # Replace the article content in the HTML
            new_content = re.sub(
                r'(<div class="article-content">).*?(</div>)',
                r'\1\n' + converted_content + r'\n\2',
                content,
                flags=re.DOTALL
            )
            
            # Write the updated file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated {filename}")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Error updating {filename}: {e}")
            continue
    
    print(f"\n🎉 Update completed!")
    print(f"✅ Successfully updated {updated_count} articles")
    print(f"📊 Total articles processed: {len(metadata)}")

def update_metadata_format():
    """Update metadata format to be consistent"""
    
    with open('articles_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    updated_entries = []
    
    for entry in metadata:
        # Ensure consistent format
        updated_entry = {
            "ticker": entry.get("ticker", ""),
            "title": entry.get("title", ""),
            "filename": entry.get("filename", ""),
            "timestamp": entry.get("timestamp", ""),
            "summary": entry.get("summary", ""),
            "tags": entry.get("tags", [])
        }
        
        # Add additional fields if they exist
        for field in ["Security", "GICS Sector", "GICS Sub-Industry", "Headquarters Location"]:
            if field in entry:
                updated_entry[field] = entry[field]
        
        updated_entries.append(updated_entry)
    
    # Save updated metadata
    with open('articles_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(updated_entries, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated metadata format for {len(updated_entries)} entries")

if __name__ == "__main__":
    print("🚀 Starting comprehensive update of existing articles and metadata...")
    
    # Update articles
    update_existing_articles()
    
    # Update metadata format
    update_metadata_format()
    
    print("\n🎉 All updates completed successfully!") 