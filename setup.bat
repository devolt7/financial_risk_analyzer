@echo off
REM Financial Risk Analyzer - Setup Script for Windows

echo.
echo ================================
echo Financial Risk Analyzer Setup
echo ================================
echo.

REM Check Python version
echo Checking Python installation...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip > nul
echo Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo Dependencies installed
echo.

echo ================================
echo Setup Complete!
echo ================================
echo.
echo To run the application:
echo   1. Activate environment: venv\Scripts\activate.bat
echo   2. Start server: python app.py
echo   3. Open browser: http://localhost:5000
echo.
pause
