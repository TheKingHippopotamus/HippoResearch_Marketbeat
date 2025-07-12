
from datetime import datetime
import json


def load_unavailable_tickers():
    """Load unavailable tickers from JSON file"""
    try:
        with open('processed_tickers/unavailable_tickers.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_unavailable_tickers(tickers):
    """Save unavailable tickers to JSON file"""
    with open('processed_tickers/unavailable_tickers.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(tickers)), f, ensure_ascii=False, indent=2)

def load_today_processed():
    """Load tickers processed today from JSON file"""
    today = datetime.now().strftime('%Y%m%d')
    fname = f'processed_tickers/processed_{today}.json'
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_today_processed(tickers):
    """Save today's processed tickers to JSON file"""
    today = datetime.now().strftime('%Y%m%d')
    fname = f'processed_tickers/processed_{today}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(tickers)), f, ensure_ascii=False, indent=2)
