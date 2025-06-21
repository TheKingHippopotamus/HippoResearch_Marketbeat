# Scripts Directory

This directory contains utility scripts for the MarketBit project.

## Files

### clean_metadata.py
A utility script to clean and maintain the articles metadata file.

**Usage:**
```bash
# Clean metadata file
python scripts/clean_metadata.py

# Test mode (dry run)
python scripts/clean_metadata.py --test
```

**Features:**
- Cleans summary text using LLM text cleaning functions
- Removes HTML artifacts and formatting issues
- Maintains data integrity in articles_metadata.json

### llm_processor.py
Core LLM processing module for text generation and HTML conversion.

**Key Functions:**
- `process_with_gemma()` - Main LLM processing function using aya-expanse:8b
- `convert_tagged_text_to_html()` - Converts tagged text (#TITLE#, #SUBTITLE#, #PARA#) to HTML
- `clean_llm_text()` - Cleans LLM output from JSON artifacts and formatting issues
- `generate_prompt()` - Generates prompts for the LLM with company and sector context

**Features:**
- Hebrew text processing with professional article generation
- Structured HTML output with proper headings and paragraphs
- Integration with company metadata from CSV files
- Robust error handling and text cleaning

**Dependencies:**
- Requires Ollama with aya-expanse:8b model
- Uses pandas for CSV data processing
- Integrates with main project data files

### html_template.py
HTML template generation module for creating styled article content.

**Key Functions:**
- `create_html_content()` - Creates formatted HTML content with company logos and styling
- `get_company_logo_url()` - Generates company logo URLs using Clearbit API
- `create_safe_filename()` - Creates safe filenames from ticker symbols
- `get_current_timestamp()` / `get_current_date()` - Date/time utilities

**Features:**
- Professional HTML styling with CSS variables
- Company logo integration using Clearbit API
- Responsive design with mobile optimization
- Hebrew RTL text support
- Ticker badge generation with company branding

**Dependencies:**
- Integrates with llm_processor for text conversion
- Uses company metadata from CSV files
- Generates logos via Clearbit API

## Import Usage

These scripts are designed to be imported from the main project:

```python
# From main.py or other root-level files
from scripts.llm_processor import process_with_gemma, convert_tagged_text_to_html
from scripts.html_template import create_html_content
from scripts.clean_metadata import clean_summary_text

# From within scripts directory
from llm_processor import process_with_gemma
from html_template import create_html_content
from clean_metadata import clean_summary_text
```

## Path Management

All scripts include proper path management to work from both the root directory and the scripts directory:

```python
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## Data Integration

Scripts automatically integrate with project data:
- CSV files in `../data/` directory
- JSON metadata files in root directory
- Static assets and templates

## Module Dependencies

```
html_template.py
├── llm_processor.py (convert_tagged_text_to_html)
└── CSV data (company metadata)

llm_processor.py
├── CSV data (sector mapping)
└── Ollama (aya-expanse:8b)

clean_metadata.py
└── llm_processor.py (clean_llm_text)
```

## הערות חשובות:

1. **הסביבה הוירטואלית חייבת להיות מופעלת** לפני הרצת הסקריפט
2. הסקריפט משתמש בנתיבים יחסיים כדי למצוא את הקבצים הנדרשים
3. הסקריפט מייבא את `llm_processor.py` מהתיקייה הראשית
4. הקובץ `articles_metadata.json` חייב להיות קיים בתיקייה הראשית

## קבצים נדרשים:
- `../llm_processor.py` - מכיל את הפונקציה `clean_llm_text`
- `../articles_metadata.json` - קובץ המטא-דאטה לניקוי 