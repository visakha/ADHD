@echo off
REM ADHD Productivity Trio - Quick Install Script (Windows)

echo ================================================
echo ADHD Productivity Trio - Installation
echo ================================================
echo.

echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    echo Please install Python 3.12+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo To run the app:
echo   1. venv\Scripts\activate.bat
echo   2. python productivity_trio.py
echo.
echo Or simply run: run.bat
echo.
echo Don't forget to:
echo   - Get your Claude API key from https://console.anthropic.com
echo   - Add it in Settings when you first open the app
echo.
echo Happy building! 🚀
echo.
pause
