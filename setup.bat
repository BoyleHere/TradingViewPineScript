@echo off
echo ==========================================
echo FVG Scanner - Virtual Environment Setup
echo ==========================================

echo.
echo Step 1: Creating virtual environment...
python -m venv fvg-env

echo.
echo Step 2: Activating virtual environment...
call fvg-env\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 5: Creating configuration file...
python main.py --create-config

echo.
echo Step 6: Testing installation...
python main.py --test-alerts

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To run the scanner:
echo   1. Activate environment: fvg-env\Scripts\activate.bat
echo   2. Run scanner: python main.py
echo.
echo For more options, run: python main.py --help
echo.
pause
