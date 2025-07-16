@echo off
echo ===============================================
echo FVG Scanner GUI - Quick Launch
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "fvg-env" (
    echo Creating virtual environment...
    python -m venv fvg-env
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call fvg-env\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Launch GUI
echo.
echo Starting FVG Scanner GUI...
echo.
python gui_app.py

pause
