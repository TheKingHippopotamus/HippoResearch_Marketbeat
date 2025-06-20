#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from llm_processor import process_with_gemma
from html_template import create_html_content

def test_real_article():
    """Test the new formatting with real V text"""
    
    # קריאת הטקסט המקורי
    with open('txt/V_original.txt', 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    print("📖 הטקסט המקורי:")
    print("=" * 50)
    print(original_text)
    print("\n" + "=" * 50)
    
    # מידע על החברה (כמו ב-CSV)
    ticker_info = {
        "Security": "Visa Inc.",
        "GICS Sector": "Financial Services",
        "GICS Sub-Industry": "Financial Services",
        "Headquarters Location": "San Francisco, California"
    }
    
    print("\n🔄 עיבוד עם הסגנון החדש...")
    
    # עיבוד הטקסט
    processed_text = process_with_gemma(original_text, ticker_info)
    
    print("\n📝 הטקסט המעובד:")
    print("=" * 50)
    print(processed_text)
    print("\n" + "=" * 50)
    
    # יצירת HTML סופי כמו בקבצים הקיימים
    print("\n🌐 יצירת HTML סופי...")
    
    html_content, ticker_badge = create_html_content("V", processed_text, ticker_info)
    
    # יצירת HTML מלא עם template
    full_html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visa Inc. (V) - מחקר כלכלי מתקדם | Hippopotamus Research</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --accent-color: #3498db;
            --highlight-color: #e74c3c;
            --gradient-accent: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --shadow-accent: 0 4px 15px rgba(52, 152, 219, 0.3);
            --text-color: #2c3e50;
            --bg-color: #f8f9fa;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        
        .header {{
            background: var(--gradient-accent);
            color: white;
            padding: 20px 0;
            text-align: center;
            box-shadow: var(--shadow-accent);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .article-header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .article-header h1 {{
            font-size: 2.2em;
            color: var(--accent-color);
            margin-bottom: 20px;
            font-weight: 700;
        }}
        
        .article-container {{
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .article-content-text {{
            font-size: 1.1em;
            line-height: 1.8;
        }}
        
        .article-content-text h1 {{
            font-size: 1.8em;
            font-weight: 700;
            color: var(--accent-color);
            margin: 20px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--highlight-color);
        }}
        
        .article-content-text h2 {{
            font-size: 1.4em;
            font-weight: 600;
            color: var(--accent-color);
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--highlight-color);
        }}
        
        .article-content-text h3 {{
            font-size: 1.2em;
            font-weight: 600;
            color: var(--accent-color);
            margin: 20px 0 10px 0;
        }}
        
        .article-content-text p {{
            font-size: 1.05em;
            line-height: 1.7;
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        .footer {{
            background: var(--primary-color);
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            margin-top: 30px;
        }}
        
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            color: #856404;
        }}
        
        .warning strong {{
            color: var(--highlight-color);
        }}
        
        .metadata {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid var(--accent-color);
        }}
        
        .metadata p {{
            margin: 5px 0;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Hippopotamus Research</h1>
        <p>מחקר כלכלי מתקדם</p>
        {ticker_badge}
    </div>
    
    <div class="container">
        <div class="article-header">
            <h1>Visa Inc. (V) - מחקר כלכלי מתקדם</h1>
        </div>
        
        {html_content}
        
        <div class="warning">
            <strong>⚠️ אזהרה:</strong> המידע הנ״ל מבוסס על מקורות מידע שונים ועלול להשתנות בכל עת. המידע המוזכר בכתבה זו מוגבל לצורך מחקר והנאה ואין לראות בכתוב המלצה להשקעה. יש להתייעץ עם יועץ פיננסי לפני קבלת החלטות השקעה.
        </div>
        
        <div class="metadata">
            <p><strong>Hippopotamus Research</strong></p>
            <p>נוצר ב: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>מקור: MarketBeat | עובד באמצעות LLM - aya-expanse:8b</p>
        </div>
    </div>
</body>
</html>"""
    
    # שמירת הקובץ
    output_file = "test_V_new_style.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ הקובץ נשמר: {output_file}")
    print(f"📁 גודל הקובץ: {os.path.getsize(output_file)} bytes")
    
    # הצגת דוגמה מהתוכן
    print("\n📄 דוגמה מהתוכן הסופי:")
    print("=" * 50)
    lines = processed_text.split('\n')[:10]
    for line in lines:
        if line.strip():
            print(line[:100] + "..." if len(line) > 100 else line)

if __name__ == "__main__":
    test_real_article() 