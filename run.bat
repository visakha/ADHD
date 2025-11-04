@echo off
REM ADHD Productivity Trio - Run Script (Windows)

echo Starting ADHD Productivity Trio...

if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python productivity_trio.py
