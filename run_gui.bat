@echo off
echo ===============================================
echo FVG Scanner - Desktop Application
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "fvg-env" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to create the environment
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call fvg-env\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

REM Launch GUI application
echo Starting FVG Scanner GUI...
echo.
python launch_gui.py

REM Check if GUI launched successfully
if errorlevel 1 (
    echo.
    echo ERROR: GUI failed to start
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo FVG Scanner GUI closed successfully
pause
