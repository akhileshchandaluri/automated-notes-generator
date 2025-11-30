#!/bin/bash
# Quick run script for Automated PDF Notes Generator (Linux/Mac)

echo "============================================================"
echo "  Automated PDF Notes Generator"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo ""
fi

# Check if dependencies are installed
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[!] Dependencies not found!"
    echo "[!] Please run: python setup.py"
    echo "[!] Or: pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "Starting Streamlit app..."
echo ""
echo "Browser will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
