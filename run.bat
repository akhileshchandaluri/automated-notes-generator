@echo off
REM Quick run script for Automated PDF Notes Generator (Windows)

echo ============================================================
echo   Automated PDF Notes Generator
echo ============================================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [!] Dependencies not found!
    echo [!] Please run: python setup.py
    echo [!] Or: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Starting Streamlit app...
echo.
echo Browser will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
