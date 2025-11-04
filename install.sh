#!/bin/bash
# ADHD Productivity Trio - Quick Install Script (Linux/macOS)

echo "================================================"
echo "ADHD Productivity Trio - Installation"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Found Python: $PYTHON_VERSION"
    
    # Check if version is 3.12+
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 12 ]); then
        echo "⚠️  Warning: Python 3.12+ recommended, you have $PYTHON_VERSION"
        echo "   App may work but not guaranteed."
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.12+ from https://python.org"
    exit 1
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================================"
echo "✅ Installation Complete!"
echo "================================================"
echo ""
echo "To run the app:"
echo "  1. source venv/bin/activate"
echo "  2. python productivity_trio.py"
echo ""
echo "Or run: ./run.sh"
echo ""
echo "Don't forget to:"
echo "  - Get your Claude API key from https://console.anthropic.com"
echo "  - Add it in Settings when you first open the app"
echo ""
echo "Happy building! 🚀"
