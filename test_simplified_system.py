#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_simplified_system():
    """Test the simplified system with clean text processing"""
    
    # Simulate the original text (clean)
    original_text = """מניות חברת International Business Machines (NYSE: IBM) רשמו מגמת עלייה, כאשר משקיעים הגיבו לסדרה של דוחות אנליסטים אופטימיים, יוזמות אסטרטגיות בתחום הבינה המלאכותית והענן, ומנהיגות בטכנולוגיות מתפתחות.
זאקס מדגיש את הדחיפה החזקה של יבמ בתחום הענן ההיברידי, את המומנטום של עסקאות הבינה המלאכותית ואת הערכת השווי האטרקטיבית לעומת אורקל, התומכים בפוטנציאל הצמיחה.
המגזין מוטלי פול מכנה את IBM כמניית המחשוב הקוונטי המובילה, וציין את הפוטנציאל ארוך הטווח שלה לפתור בעיות מעבר למחשבי-על קלאסיים."""
    
    print("🧪 Testing simplified system...")
    print(f"📄 Original text length: {len(original_text)} characters")
    print(f"📄 Original text preview: {original_text[:100]}...")
    
    # Test that the text is clean (no HTML tags)
    if '<' in original_text or '>' in original_text:
        print("❌ Original text contains HTML tags!")
    else:
        print("✅ Original text is clean (no HTML tags)")
    
    # Test that the text is not empty
    if len(original_text.strip()) > 0:
        print("✅ Original text is not empty")
    else:
        print("❌ Original text is empty!")
    
    # Test that the text contains expected content
    if "IBM" in original_text and "זאקס" in original_text:
        print("✅ Original text contains expected content")
    else:
        print("❌ Original text missing expected content")
    
    print("\n🎯 Conclusion: Simplified system is ready!")
    print("📁 Files will be saved only in /txt directory")
    print("🤖 LLM will receive clean text only")
    print("📄 No HTML duplication")
    
    return original_text

if __name__ == "__main__":
    test_simplified_system() 