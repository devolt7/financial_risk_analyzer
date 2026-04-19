#!/bin/bash

# Financial Risk Analyzer - Setup Script
# This script sets up the development environment

echo "================================"
echo "Financial Risk Analyzer Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python installation..."
python_version=$(python3 --version 2>&1)
echo "✓ $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To run the application:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Start server: python app.py"
echo "  3. Open browser: http://localhost:5000"
echo ""
