# 🦛 MarketBit Research - Automated Market Analysis System

A comprehensive automated system for scraping, processing, and generating market research articles using AI-powered content generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser (for web scraping)
- Ollama with `aya-expanse:8b` model installed
- Git repository initialized

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd marketBit

# Install dependencies
pip install -r requirements.txt

# Install Ollama model
ollama pull aya-expanse:8b
```

## 📋 Main System Interface

The `main.py` file provides a unified interface for all system operations:

### Interactive Mode (Recommended for beginners)
```bash
python main.py --interactive
```
This starts an easy-to-use menu system where you can:
- Process individual tickers
- Process all available tickers
- Check system status
- Run maintenance tasks

### Command Line Options

#### Process Individual Ticker
```bash
python main.py --ticker AAPL
# or
python main.py -t AAPL
```

#### Process All Available Tickers
```bash
python main.py --all
# or
python main.py -a
```

#### System Status
```bash
python main.py --status
# or
python main.py -s
```

#### System Maintenance
```bash
python main.py --maintenance
# or
python main.py -m
```

#### Migrate Existing Articles
```bash
python main.py --migrate
```

#### Commit Changes for Specific Ticker
```bash
python main.py --commit AAPL
# or
python main.py -c AAPL
```

## 🏗️ System Architecture

### Core Modules

#### 1. **Process Manager** (`scripts/process_manager.py`)
- Orchestrates the entire ticker processing pipeline
- Handles batch processing and single ticker processing
- Manages processing state and tracking

#### 2. **Web Scraper** (`scripts/scrap_marketBeat_keypoints.py`)
- Scrapes market data from MarketBeat
- Extracts AI-generated summaries and key points
- Handles browser automation with Selenium

#### 3. **LLM Processor** (`scripts/llm_processor.py`)
- Processes raw market data with AI (aya-expanse:8b)
- Generates structured articles with Hebrew content
- Converts tagged text to HTML format

#### 4. **UI/UX Manager** (`scripts/ui_ux_manager.py`)
- Handles article formatting and styling
- Manages JavaScript injection for content cleaning
- Provides automatic HTML structure fixes

#### 5. **File Manager** (`scripts/filemanager.py`)
- Manages file operations and metadata
- Handles CSV data loading and processing
- Provides safe filename creation

#### 6. **JSON Manager** (`scripts/json_manager.py`)
- Manages processing state tracking
- Handles unavailable tickers list
- Tracks daily processing progress

#### 7. **Git Automation** (`scripts/github_automation.py`)
- Automates Git commits and pushes
- Handles repository synchronization
- Manages deployment workflow

#### 8. **Logger** (`scripts/logger.py`)
- Provides comprehensive logging system
- Includes stage tracking and colored output
- Supports both file and console logging

## 📊 System Features

### Automated Processing Pipeline
1. **Data Scraping**: Automatically scrapes market data from MarketBeat
2. **AI Processing**: Uses LLM to generate structured articles
3. **Content Formatting**: Applies consistent styling and structure
4. **Quality Assurance**: Runs automatic content cleaning
5. **Git Integration**: Commits and pushes changes automatically

### Intelligent State Management
- Tracks processed tickers to avoid duplicates
- Maintains unavailable tickers list
- Daily reset of processing state
- Automatic backup and recovery

### Content Quality Features
- Automatic HTML structure fixing
- JavaScript-based content cleaning
- Social media integration
- Responsive design support

## 📁 Directory Structure

```
marketBit/
├── main.py                 # Main system interface
├── articles/               # Generated HTML articles
├── txt/                    # Raw and processed text files
├── data/                   # CSV data and metadata
├── processed_tickers/      # Processing state tracking
├── static/                 # Static assets (logos, icons)
├── scripts/                # Core system modules
├── tools/                  # Utility scripts
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### CSV Data Format
The system expects a CSV file at `data/flat-ui__data-Thu Jun 19 2025.csv` with columns:
- `Tickers`: Stock symbol
- `Security`: Company name
- `GICS Sector`: Industry sector
- `GICS Sub-Industry`: Sub-industry classification

### Environment Setup
1. Ensure Chrome browser is installed
2. Install Ollama and the required model
3. Initialize Git repository
4. Set up proper file permissions

## 🚨 Troubleshooting

### Common Issues

#### "Chrome driver not found"
- Ensure Chrome browser is installed
- Check Chrome version compatibility

#### "Ollama model not found"
```bash
ollama pull aya-expanse:8b
```

#### "Git repository not initialized"
```bash
git init
git remote add origin <your-repo-url>
```

#### "Permission denied"
```bash
chmod +x main.py
chmod +x scripts/*.py
```

### Log Files
- Check `js_cleaner.log` for JavaScript injection issues
- System logs are written to console and files
- Use `--status` to check system health

## 🔄 Workflow Examples

### Daily Processing
```bash
# Check system status
python main.py --status

# Run maintenance
python main.py --maintenance

# Process all available tickers
python main.py --all
```

### Single Ticker Development
```bash
# Process specific ticker
python main.py --ticker AAPL

# Commit changes
python main.py --commit AAPL
```

### Interactive Development
```bash
# Start interactive mode
python main.py --interactive
```

## 📈 Performance Tips

1. **Batch Processing**: Use `--all` for efficient bulk processing
2. **Maintenance**: Run `--maintenance` regularly to keep system healthy
3. **Monitoring**: Use `--status` to track processing progress
4. **Backup**: System automatically creates backups before major operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Use `--status` to diagnose system issues
4. Create an issue with detailed error information

---

**🦛 MarketBit Research** - Making market analysis accessible and automated.


