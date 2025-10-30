import requests
import ollama

API_URL = "https://thekinghippopotamus.github.io/HippoResearch_Marketbeat/data/articles_metadata.json"

def fetch_articles():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()

def show_last_articles(articles, limit=10):
    recent = articles[:limit]
    for idx, a in enumerate(recent):
        print(f"{idx+1}. {a['ticker']} – {a['title'][:50]}... ({a['timestamp']})")
    return recent

def analyze_sentiment(text):
    prompt = f"""
    הנך מנתח סנטימנט פיננסי.
    טקסט: "{text}"
    החזר מספר בלבד:
    -1 = שלילי, 0 = ניטרלי, +1 = חיובי
    """

    res = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return float(res["message"]["content"].strip())
    except:
        return 0.0

def interactive_mode():
    articles = fetch_articles()

    print("\n🔥 הנה 10 הכתבות האחרונות במערכת שלך:")
    recent = show_last_articles(articles)

    choice = int(input("\nבחר מספר לניתוח: ")) - 1
    if choice < 0 or choice >= len(recent):
        print("בחירה לא תקינה")
        return

    selected = recent[choice]
    text = selected["title"] + "\n" + selected["summary"]
    print("\n🔍 מבצע ניתוח סנטימנט:")
    score = analyze_sentiment(text)

    print("\n📊 תוצאות:")
    print(f"סקירה על: {selected['ticker']}")
    print(f"סנטימנט: {score}")
    print("\n📰 תקציר:")
    print(selected["summary"])

if __name__ == "__main__":
    interactive_mode()
