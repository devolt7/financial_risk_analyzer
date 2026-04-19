@echo off
REM Financial Risk Analyzer - Run Script for Windows

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat

pip install -q -r requirements.txt

echo.
echo ================================
echo Starting Financial Risk Analyzer
echo ================================
echo.
echo Web Server: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
