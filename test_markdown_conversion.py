#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from llm_processor import convert_markdown_to_html

def test_markdown_conversion():
    """Test the markdown to HTML conversion function"""
    
    # Test case with markdown content
    markdown_text = """# ניתוח תנועת המניה של Marvell Technology, Inc. (MRVL)

## סיכום המצב הנוכחי

מניות Marvell Technology (MRVL) חוו עלייה משמעותית בזכות מגוון גורמים חיוביים שהציתו את עניין המשקיעים. החברה מציגה ביצועים פיננסיים חזקים, חדשנות מוצר בתחומי בינה מלאכותית (AI) ומרכזי נתונים, וכן תחזיות אופטימיות מצד אנליסטים רבים.

## גורמים בולטים: הנהלה, מוסדות ואנליסטים

**הנהלה ומוצרים חדשניים:** Marvell הציגה לאחרונה מוצרים פורצי דרך בתעשיית השבבים, כולל את שבב ה-AI הראשון בעולם ב-2 ננומטר ושבבי כוח משולבים.

**תמיכה מוסדית ואנליסטית:** מספר אנליסטים מובילים הגבירו את מחירי היעד שלהם עבור MRVL, כולל Bank of America, B. Riley, Rosenblatt, Benchmark, Needham, Zacks Research ועוד."""
    
    print("🧪 Testing markdown to HTML conversion...")
    print(f"📄 Input length: {len(markdown_text)} characters")
    print(f"📄 Input preview: {markdown_text[:100]}...")
    
    # Convert markdown to HTML
    html_result = convert_markdown_to_html(markdown_text)
    
    print(f"\n📄 Output length: {len(html_result)} characters")
    print(f"📄 Output preview: {html_result[:200]}...")
    
    # Check for HTML tags
    has_h1 = '<h1>' in html_result
    has_h2 = '<h2>' in html_result
    has_p = '<p>' in html_result
    has_strong = '<strong>' in html_result
    
    print(f"\n✅ HTML tags found:")
    print(f"   <h1>: {has_h1}")
    print(f"   <h2>: {has_h2}")
    print(f"   <p>: {has_p}")
    print(f"   <strong>: {has_strong}")
    
    # Check for markdown symbols (should be removed)
    has_markdown = '#' in html_result or '**' in html_result
    
    if has_markdown:
        print(f"❌ Markdown symbols still present!")
    else:
        print(f"✅ Markdown symbols removed!")
    
    # Overall assessment
    if has_h1 and has_h2 and has_p and not has_markdown:
        print(f"\n🎉 Conversion successful!")
        return True
    else:
        print(f"\n❌ Conversion failed!")
        return False

if __name__ == "__main__":
    test_markdown_conversion() 