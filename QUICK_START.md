# 🚀 Quick Start Guide - MarketBit Refactored

## מבנה חדש מוכן לשימוש!

### 📁 מבנה התיקיות החדש

```
src/
├── core/              # Core functionality
├── config/            # Configuration
├── data/              # Data scraping
├── services/          # Business services
└── processing/        # Processing pipeline
```

## 🎯 איך להשתמש

### אפשרות 1: קוד ישן (עובד כמו תמיד)
```bash
python main.py AAPL              # טיקר אחד
python main.py                   # כל הטיקרים
```

### אפשרות 2: קוד חדש (מסודר)
```bash
python src/main.py AAPL         # טיקר אחד
python src/main.py              # כל הטיקרים
```

### אפשרות 3: ישירות מהקוד
```python
# Single ticker
from src.processing.pipeline import TickerProcessingPipeline
from tools.ticker_data import ticker_manager

pipeline = TickerProcessingPipeline()
ticker_info = ticker_manager.get_ticker_info("AAPL")
result = pipeline.process_ticker("AAPL", ticker_info)

if result.is_ok():
    print(f"✅ Article: {result.data['html_filepath']}")

# Batch processing
from src.processing.batch_processor import BatchProcessor

batch = BatchProcessor()
batch.process_all_available_tickers()
```

## ✨ השירותים החדשים

### 1. TickerProcessingPipeline
עיבוד מלא של טיקר בודד - scraping, entity analysis, LLM, HTML

### 2. BatchProcessor
עיבוד אצווה של כל הטיקרים הזמינים

### 3. MarketBeatScraper
Scraping מסודר עם Result types

### 4. LLMService
שירות LLM עם error handling

### 5. EntityAnalysisService
ניתוח ישויות מסודר

### 6. ArticleProcessorService
עיבוד מאמרים

## 🔄 Backward Compatibility

**הכל עובד!** הקוד הישן:
- ✅ `main.py` - עובד
- ✅ `scripts/process_manager.py` - עובד
- ✅ `scripts/scrap_marketBeat_keypoints.py` - עובד
- ✅ כל ה-`tools/` - עובד

## 📋 דוגמאות

### Scraping בלבד
```python
from src.data.scrapers.marketbeat import MarketBeatScraper

scraper = MarketBeatScraper()
result = scraper.scrape("AAPL")
if result.is_ok():
    print(result.data)
```

### LLM בלבד
```python
from src.services.llm_service import LLMService

llm = LLMService()
result = llm.generate("Write about AAPL")
if result.is_ok():
    print(result.data)
```

### Entity Analysis בלבד
```python
from src.services.entity_service import EntityAnalysisService

entity = EntityAnalysisService()
result = entity.analyze_and_save(text, "AAPL")
```

## ⚙️ Configuration

כל ההגדרות ב-`src/config/settings.py` או ב-`.env`:

```python
from src.config.settings import get_settings

settings = get_settings()
print(settings.llm_endpoint)
print(settings.llm_model)
```

## 🎉 הכל מוכן!

**הקוד החדש מסודר, מאורגן, עם שמות ברורים, ובעיקר - עובד!**

---
**תאריך**: 29/10/2024  
**סטטוס**: ✅ הושלם בהצלחה

