#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_success() {
  echo -e "${GREEN}$1${NC}"
}
function print_error() {
  echo -e "${RED}$1${NC}"
}
function print_info() {
  echo -e "${YELLOW}$1${NC}"
}

print_info "[0/6] Checking for Python3..."
if ! command -v python3 &> /dev/null; then
  print_error "Python3 is not installed. Please install Python 3.8+ and try again."
  exit 1
fi
if ! python3 -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)"; then
  print_error "Python version must be 3.8 or higher."
  exit 1
fi
print_success "Python3 found."

if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
  print_error "pip is not installed. Please install pip for Python3."
  exit 1
fi
print_success "pip found."
sleep 1

print_info "[1/6] Detecting OS..."
OS="$(uname -s)"
if [[ "$OS" == "Darwin" ]]; then
  print_success "Detected macOS."
  if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed. Please install Homebrew first: https://brew.sh/"
    exit 1
  fi
elif [[ "$OS" == "Linux" ]]; then
  print_success "Detected Linux."
  if ! command -v curl &> /dev/null; then
    print_error "curl is not installed. Please install curl (e.g. sudo apt install curl) and try again."
    exit 1
  fi
else
  print_error "Unsupported OS: $OS. Please use install.ps1 for Windows."
  exit 1
fi
sleep 2

print_info "[2/6] Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
  print_info "Ollama not found. Installing..."
  if [[ "$OS" == "Darwin" ]]; then
    brew install ollama || { print_error "Failed to install Ollama."; exit 1; }
  else
    curl -fsSL https://ollama.com/install.sh | sh || { print_error "Failed to install Ollama."; exit 1; }
  fi
else
  print_success "Ollama is already installed."
fi
sleep 2

print_info "[3/6] Pulling aya-expanse:8b model..."
if ollama list | grep -q "aya-expanse"; then
  print_success "Model aya-expanse:8b already present."
else
  ollama pull aya-expanse:8b || { print_error "Failed to pull aya-expanse:8b."; exit 1; }
fi
sleep 2

print_info "[4/6] Creating Python virtual environment..."
if [ -d "venv" ]; then
  print_success "Virtual environment already exists."
else
  python3 -m venv venv || { print_error "Failed to create virtual environment."; exit 1; }
fi
sleep 2

print_info "[5/6] Installing Python requirements..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || { print_error "Failed to install requirements."; deactivate; exit 1; }
deactivate
sleep 2

print_success "[6/6] Setup complete!"
echo -e "\n${GREEN}You can now run the system with:${NC}"
echo -e "${YELLOW}cd scripts && ./run_processing.sh${NC}\n" 