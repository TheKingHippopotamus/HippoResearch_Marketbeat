#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def clean_llm_text(text):
    """Clean LLM output from JSON artifacts, HTML tags, and formatting issues"""
    if not text:
        return text
    
    # Remove JSON structure artifacts
    text = re.sub(r'^\s*\{\s*', '', text)
    text = re.sub(r'\s*\}\s*$', '', text)
    text = re.sub(r'^\s*"text":\s*"', '', text)
    text = re.sub(r'^\s*"":\s*"', '', text)
    text = re.sub(r'"\s*,\s*"tags":\s*\[\s*\]\s*$', '', text)
    text = re.sub(r'"\s*$', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown symbols
    text = re.sub(r'^#+\s*', '', text)  # Remove markdown headers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markdown
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic markdown
    
    # Clean up newlines and whitespace
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
    text = re.sub(r' +', ' ', text)  # Normalize spaces
    
    return text.strip()

def test_clean_llm():
    """Test the clean_llm_text function with various formatting artifacts"""
    
    # Test case 1: HTML tags and markdown
    test_input = """<h1>אקסון מוביל: צמיחה, דיבידנדים והזדמנויות במגזר האנרגיה ## רקע חיובי למניה ופוטנציאל לעתיד מניית אקסון מוביל (XOM) חווה עלייה לאחרונה, ומושכת את תשומת לבם של משקיעים רבים.</h1>"""
    
    expected_output = """אקסון מוביל: צמיחה, דיבידנדים והזדמנויות במגזר האנרגיה רקע חיובי למניה ופוטנציאל לעתיד מניית אקסון מוביל (XOM) חווה עלייה לאחרונה, ומושכת את תשומת לבם של משקיעים רבים."""
    
    result = clean_llm_text(test_input)
    
    print("🧪 Testing clean_llm_text function...")
    print(f"📄 Input: {test_input}")
    print(f"📄 Expected: {expected_output}")
    print(f"📄 Result: {result}")
    
    if result == expected_output:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
    
    # Test case 2: JSON artifacts
    test_input2 = '{"text": "מניית אפל עלתה היום"}'
    result2 = clean_llm_text(test_input2)
    print(f"\n📄 JSON test: {test_input2} → {result2}")
    
    # Test case 3: Bold markdown
    test_input3 = "**מבוא:** מניית טסלה חווה עליות"
    result3 = clean_llm_text(test_input3)
    print(f"📄 Bold test: {test_input3} → {result3}")
    
    return result

if __name__ == "__main__":
    test_clean_llm() 