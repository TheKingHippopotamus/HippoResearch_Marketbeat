#!/bin/bash

# Script to run the JavaScript cleaner in monitoring mode
# This script will automatically process new HTML files as they are created

echo "🔍 Starting JavaScript cleaner in monitoring mode..."
echo "📝 The cleaner will automatically process new HTML files in the articles directory"
echo "⏹️ Press Ctrl+C to stop monitoring"
echo ""

# Run the Python script in monitoring mode
python3 inject_js_cleaner.py --monitor --dir articles 