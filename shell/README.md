# Shell Scripts

This directory contains shell scripts and automation tools for the MarketBit project.

## Files

### run_auto_commit.sh
Bash script to start automatic monitoring of the articles directory.

**Usage:**
```bash
# From project root
./shell/run_auto_commit.sh

# Or from shell directory
cd shell
./run_auto_commit.sh
```

**What it does:**
- Starts automatic monitoring of the `articles/` directory
- Detects new HTML files and automatically commits them to git
- Pushes changes to GitHub repository
- Runs continuously until stopped with Ctrl+C

### auto_commit.py
Python script for automatic file monitoring and git operations.

**Features:**
- Uses `watchdog` library to monitor file system changes
- Automatically detects new HTML files in articles directory
- Performs git add, commit, and push operations
- Includes logging and error handling
- Prevents duplicate processing

**Dependencies:**
- `watchdog` library (install with: `pip install watchdog`)
- Git repository must be initialized
- Proper git credentials configured

## Installation

Make sure you have the required dependencies:
```bash
pip install watchdog
```

## Usage

1. **Start monitoring:**
   ```bash
   ./shell/run_auto_commit.sh
   ```

2. **The script will:**
   - Monitor the `articles/` directory for new HTML files
   - Automatically commit new articles to git
   - Push changes to GitHub
   - Log all activities to `auto_commit.log`

3. **Stop monitoring:**
   - Press `Ctrl+C` to stop the monitoring

## Logs

The script creates a log file `auto_commit.log` in the project root with detailed information about all operations.

## Notes

- The script runs from the project root directory
- It monitors the `articles/` directory for new HTML files
- Each new file triggers an automatic git commit and push
- The script includes a 5-second delay to ensure files are fully written 