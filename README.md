# MarketBit (HippoResearch – MarketBeat Pipeline)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-green.svg)]()

MarketBit is an automated market-research pipeline that collects, processes, and analyzes equity-related information and generates publication-ready research articles (HTML). It is designed for scalable batch processing across large ticker universes and emphasizes reproducible outputs, structured metadata, and AI-assisted text analytics.

> Security note: this repository is public for GitHub Pages / demo purposes. Sensitive files, secrets, and private datasets were removed or replaced with examples.

---

## Table of Contents

- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [High-Level Architecture](#high-level-architecture)
- [Project Layout](#project-layout)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Outputs](#outputs)
- [Testing](#testing)
- [Operational Notes](#operational-notes)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

---

## Overview

MarketBit automates the end-to-end workflow of equity research content creation:

1. Collect source content for a ticker  
2. Clean and normalize raw text  
3. Run NLP / entity extraction and sentiment analysis  
4. Generate an investment-style narrative using an LLM (configurable)  
5. Render a modern, responsive HTML article  
6. Persist outputs + metadata, track processing state, and optionally automate Git updates  

The system is built as a pragmatic, production-oriented pipeline: clear logging, failure handling, daily processing state, and reusable utilities.

---

## Key Capabilities

### Data Collection
- Automated web collection from MarketBeat (pipeline-oriented scraping module)
- Batch processing for large ticker sets (e.g., S&P 500-scale universes)
- Automated source management and availability tracking

### AI / NLP Processing
- spaCy-based NLP pipeline
- Financial entity recognition (companies, instruments, key terms)
- Sentiment analysis and structured output storage
- Automated categorization / classification hooks

### Research & Comparative Analysis
- Trend and narrative extraction from source text
- Risk/opportunity framing
- Peer/industry comparison hooks (extendable)
- Time-aware processing (date-stamped outputs and metadata)

### Content Generation
- Research-style article generation (Hebrew-focused in current templates; extendable to EN)
- Modern HTML templates and responsive layout
- SEO-friendly structure and reusable templates

### Automation & Ops
- Batch processing and daily processing ledgers
- Git automation support (optional)
- Structured logging and archived run history

---

## High-Level Architecture

```
Collection → Cleaning → NLP/Entity Analysis → LLM Generation → HTML Rendering → Optimization → Storage/Versioning
```

Core components:
- `scripts/` orchestrates processing and automation
- `tools/` provides reusable utilities (NLP, templating, config, logging)
- `data/`, `articles/`, and state folders store results and run ledgers

---

## Project Layout

```
marketBit/
├── main.py
├── requirements.txt
├── index.html
├── LICENSE
│
├── tools/
│   ├── config.py
│   ├── entity_analyzer.py
│   ├── logger.py
│   ├── llm_processor.py
│   ├── html_template.py
│   ├── text_processing.py
│   ├── ticker_data.py
│   └── inject_js_cleaner.py
│
├── scripts/
│   ├── process_manager.py
│   ├── scrap_marketBeat_keypoints.py
│   ├── ui_ux_manager.py
│   ├── filemanager.py
│   ├── github_automation.py
│   └── json_manager.py
│
├── data/
│   ├── articles_metadata.json
│   └── flat-ui__data.csv
│
├── articles/
│   └── [TICKER]_[DATE].html
│
├── txt/
│   ├── [TICKER]_cleaned_[DATE].txt
│   └── [TICKER]_original_[DATE].txt
│
├── entityAnalyzer_DB/
│   └── [TICKER]_entity_analysis_[DATE].json
│
├── processed_tickers/
│   ├── processed_[DATE].json
│   ├── unavailable_tickers.json
│   └── last_clear_date.txt
│
├── templates/
│   └── article_template.html
│
├── static/
│   ├── logo.png
│   └── x.png
│
└── unit-test/
    ├── entity_extractor.py
    ├── test_token_control.py
    ├── test_professional_prompt.py
    └── run_single_ticker.py
```

---

## Installation

### Requirements
- Python 3.8+
- Git
- A supported browser + driver if Selenium is enabled (environment-dependent)

### Setup

```bash
git clone https://github.com/TheKingHippopotamus/HippoResearch_Marketbeat.git
cd HippoResearch_Marketbeat

python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

pip install -r requirements.txt

# Optional: spaCy model used by entity analysis
python -m spacy download en_core_web_trf
```

---

## Configuration

1. Copy the example config:
   ```bash
   cp tools/config.example.py tools/config.py
   ```

2. Update `tools/config.py`:
   - LLM model settings (provider/model name, temperature, etc.)
   - Paths (if you moved folders)
   - Any runtime flags (verbose logging, scraping mode, etc.)

Example:
```python
LLM_MODEL_SETTINGS = {
    "model_name": "your-model-name-here",
    "temperature": 0.7,
    "top_p": 0.9,
}
```

---

## Usage

### Run the full universe
```bash
python main.py
```

### Run a single ticker
```bash
python main.py AAPL
```

### Run with verbose logs
```bash
python main.py MSFT --verbose
```

### Maintenance utilities
```bash
python scripts/filemanager.py --cleanup
python scripts/filemanager.py --backup
python scripts/filemanager.py --restore
```

---

## Outputs

- **Generated articles:** `articles/[TICKER]_[DATE].html`
- **Raw and cleaned text:** `txt/`
- **Entity/NLP results:** `entityAnalyzer_DB/`
- **Processing ledgers:** `processed_tickers/`
- **Metadata index:** `data/articles_metadata.json`

---

## Testing

Basic unit and pipeline tests live under `unit-test/`.

Examples:
```bash
python unit-test/run_single_ticker.py
python unit-test/test_professional_prompt.py
```

---

## Operational Notes

- **Source availability:** some tickers may not have accessible source content; these are tracked in `processed_tickers/unavailable_tickers.json`.
- **Reproducibility:** outputs are date-stamped and tracked via ledgers to avoid re-processing.
- **Compliance:** if you enable automated collection from third-party sites, ensure your usage complies with the relevant Terms of Service and applicable laws, and apply rate-limiting and respectful crawling patterns.

---

## License

**All rights reserved © 2024 Hippopotamus Research – Nir Elmaliah**

This project is proprietary and not open source. You may not copy, distribute, modify, use, or commercialize any part of the code, content, or design without explicit written permission from the author.

See [LICENSE](LICENSE) for details.

---

## Contact

Creator: **Nir Elmaliah**  
Organization: **Hippopotamus Research**

---

## Acknowledgments

- MarketBeat (data source referenced by the pipeline)
- spaCy (NLP toolkit)
- Selenium (browser automation)
- The Python ecosystem
