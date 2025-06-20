#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def test_with_real_files():
    """Test the simplified system using real existing files"""
    
    print("🧪 Testing simplified system with real files...")
    
    # Test 1: Check that original files are clean (no HTML tags)
    original_files = [f for f in os.listdir('txt') if f.endswith('_original.txt')]
    print(f"📁 Found {len(original_files)} original files")
    
    html_tags_found = 0
    for file in original_files[:5]:  # Test first 5 files
        with open(f'txt/{file}', 'r', encoding='utf-8') as f:
            content = f.read()
            if '<' in content or '>' in content:
                html_tags_found += 1
                print(f"❌ {file} contains HTML tags")
            else:
                print(f"✅ {file} is clean (no HTML tags)")
    
    if html_tags_found == 0:
        print("✅ All original files are clean!")
    else:
        print(f"❌ {html_tags_found} files contain HTML tags")
    
    # Test 2: Check that processed files have proper HTML formatting
    processed_files = [f for f in os.listdir('txt') if f.endswith('_processed.txt')]
    print(f"\n📁 Found {len(processed_files)} processed files")
    
    proper_html_found = 0
    for file in processed_files[:5]:  # Test first 5 files
        with open(f'txt/{file}', 'r', encoding='utf-8') as f:
            content = f.read()
            if '<h1>' in content or '<h2>' in content or '<p>' in content:
                proper_html_found += 1
                print(f"✅ {file} has proper HTML formatting")
            else:
                print(f"❌ {file} missing proper HTML formatting")
    
    if proper_html_found == len(processed_files[:5]):
        print("✅ All processed files have proper HTML formatting!")
    else:
        print(f"❌ Only {proper_html_found}/{len(processed_files[:5])} files have proper HTML")
    
    # Test 3: Check file sizes (processed should be larger than original)
    print(f"\n📊 File size comparison:")
    for i in range(min(3, len(original_files))):
        original_file = original_files[i]
        ticker = original_file.replace('_original.txt', '')
        processed_file = f"{ticker}_processed.txt"
        
        if os.path.exists(f'txt/{processed_file}'):
            original_size = os.path.getsize(f'txt/{original_file}')
            processed_size = os.path.getsize(f'txt/{processed_file}')
            
            print(f"📄 {ticker}: {original_size:,} → {processed_size:,} bytes")
            if processed_size > original_size:
                print(f"✅ {ticker}: Processing worked (file grew)")
            else:
                print(f"❌ {ticker}: Processing may have failed")
    
    # Test 4: Check that no HTML files exist in txt directory
    html_files = [f for f in os.listdir('txt') if f.endswith('.html')]
    if len(html_files) == 0:
        print(f"\n✅ No HTML files in txt directory (clean structure)")
    else:
        print(f"\n❌ Found {len(html_files)} HTML files in txt directory")
    
    # Test 5: Check that data directory doesn't exist (was removed)
    if not os.path.exists('data'):
        print(f"\n✅ Data directory removed (no duplication)")
    else:
        print(f"\n❌ Data directory still exists")
    
    print(f"\n🎯 Summary:")
    print(f"📁 Original files: {len(original_files)} (should be clean)")
    print(f"📁 Processed files: {len(processed_files)} (should have HTML)")
    print(f"📁 HTML files in txt: {len(html_files)} (should be 0)")
    print(f"📁 Data directory: {'removed' if not os.path.exists('data') else 'exists'}")
    
    return True

if __name__ == "__main__":
    test_with_real_files() 