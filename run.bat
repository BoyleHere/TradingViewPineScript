@echo off
echo ==========================================
echo FVG Scanner - Quick Run
echo ==========================================

echo Activating virtual environment...
call fvg-env\Scripts\activate.bat

echo.
echo Choose an option:
echo [1] Run continuous scanner
echo [2] Run single scan
echo [3] Test alerts
echo [4] Run with custom symbols
echo [5] Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting continuous scanner...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo Running single scan...
    python main.py --single-scan
) else if "%choice%"=="3" (
    echo.
    echo Testing alerts...
    python main.py --test-alerts
) else if "%choice%"=="4" (
    echo.
    set /p symbols="Enter symbols (e.g., AAPL,MSFT,GOOGL): "
    echo Running scanner with symbols: %symbols%
    python main.py --symbols "%symbols%"
) else if "%choice%"=="5" (
    echo Exiting...
    exit
) else (
    echo Invalid choice. Please run the script again.
)

echo.
pause
