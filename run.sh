#!/bin/bash
# ADHD Productivity Trio - Run Script (Linux/macOS)

echo "Starting ADHD Productivity Trio..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./install.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Run app
python productivity_trio.py
