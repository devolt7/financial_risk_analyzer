#!/bin/bash

# Financial Risk Analyzer - Run Script (Windows-compatible batch file equivalent)

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -q -r requirements.txt

# Run the Flask app
echo "================================"
echo "Starting Financial Risk Analyzer"
echo "================================"
echo ""
echo "🌐 Server: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
