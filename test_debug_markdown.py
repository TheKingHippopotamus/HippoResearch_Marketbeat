#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from llm_processor import convert_markdown_to_html

# הטקסט הבעייתי שציינת
test_text = """דובר קורפוריישן: הרחבה אסטרטגית, דיבידנדים חזקים והכרה בשוק ## רקע על החברה דובר קורפוריישן (NYSE: DOV), חברת ענק בתעשיית היערכות התעשייתית, ממשיכה להפתיע את השווקים עם צעדים אסטרטגיים חדשניים. לאחר עלייה במניית החברה, אנו בוחנים את ההתפתחויות האחרונות שמעצבות מחדש את פרופיל החברה ואת מעמדה בשוק. ## רכישה אסטרטגית של ipp Pump Products GmbH החברה הצהירה על רכישת ipp Pump Products GmbH, צעד שמדגיש את הכוונה שלה להרחיב את נוכחותה בתחום המשאבות ההיגייניות. שילוב העסק בתוך קבוצת פתרונות המשאבות של דובר יאפשר סינרגיות חזקות, תוך הרחבת התיק הקיים של החברה. ## התמקדות בגיוס דיבידנדים דו"ח השקעות אחרון מזכיר את דובר קורפוריישן בין "אריסטוקרטים" מובילים בתחום גיוס הדיבידנד. הכרה זו בשוק מדגישה את היציבות והביצועים ארוכי הטווח של החברה בתשלומי דיבידנדים, מה שהופך אותה ליעד אטרקטיבי למשקיעים המחפשים הכנסה קבועה. ## השפעה על השוק והמשקיעים העלייה במניית דובר לאחר ההודעה מראה את האופטימיות של השוק לגבי הכיוון העתידי של החברה. הרכישה האסטרטגית מבטיחה לא רק גיוון במוצרים, אלא גם נוכחות חזקה יותר בשוק המשאבות ההיגייניות. זהו צעד אסטרטגי שמחזק את דובר כחקן מרכזי בתעשייה. ## סיכום עם הרחבת תיק המוצרים שלה והמשכיות ברקורד התשלומים שלה, דובר קורפוריישן ממצבת את עצמה כמובילה בתחומה. השקעה זו אינה רק אסטרטגית עבור החברה, אלא גם מבטיחה ביטחון למשקיעים המחפשים יציבות וצמיחה ארוכות טווח. עם זאת, השוק ימשיך לעקוב אחר ההתפתחויות הבאות כדי להעריך את ההשפעה המלאה של הרכישה על הביצועים הפיננסיים של דובר."""

print("=== בדיקת המרת Markdown ל-HTML ===")
print(f"📄 טקסט מקורי (200 תווים ראשונים): {test_text[:200]}...")
print(f"🔍 מכיל '##': {'##' in test_text}")

# המרה
converted = convert_markdown_to_html(test_text)

print(f"\n📄 טקסט מומר (200 תווים ראשונים): {converted[:200]}...")
print(f"🔍 מכיל '<h': {'<h' in converted}")
print(f"🔍 מכיל '<p': {'<p' in converted}")

print(f"\n📄 טקסט מומר מלא:")
print(converted)

# בדיקה נוספת - נסה לפרק את הטקסט לפי ##
print(f"\n=== בדיקה נוספת - פירוק לפי ## ===")
parts = test_text.split('##')
for i, part in enumerate(parts):
    print(f"חלק {i}: {part[:100]}...") 