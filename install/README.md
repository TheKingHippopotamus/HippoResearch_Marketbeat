# Install Scripts

This directory contains installation scripts for setting up the MarketBit project on different operating systems.

## Files

- **install.sh**  
  Bash script for macOS and Linux. Checks for Python 3.8+, pip, Homebrew/curl, installs Ollama and the aya-expanse:8b model, creates a virtual environment, and installs Python dependencies.

- **install.ps1**  
  PowerShell script for Windows. Checks for Python 3.8+, pip, installs Ollama and the aya-expanse:8b model, creates a virtual environment, and installs Python dependencies.

## Usage

### macOS / Linux
```bash
bash install.sh
```

### Windows
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

## What these scripts do
- Ensure all system dependencies are present
- Install Ollama and required LLM model
- Set up a Python virtual environment
- Install all Python requirements

**After running the script, you can start the system as described in the main README.** 