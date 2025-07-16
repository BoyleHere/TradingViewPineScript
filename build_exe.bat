@echo off
echo ===============================================
echo FVG Scanner - Build Desktop Application
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "fvg-env" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call fvg-env\Scripts\activate.bat

REM Install PyInstaller if not present
echo Installing PyInstaller...
pip install pyinstaller

REM Create dist directory
if not exist "dist" mkdir dist

REM Build the executable
echo Building FVG Scanner executable...
echo This may take a few minutes...
echo.

pyinstaller --clean --onefile --windowed --name "FVG_Scanner_Pro" --add-data "config.ini;." --add-data "src;src" --icon "assets/icon.ico" gui_app.py

REM Check if build was successful
if exist "dist\FVG_Scanner_Pro.exe" (
    echo.
    echo ===============================================
    echo BUILD SUCCESSFUL!
    echo ===============================================
    echo.
    echo Executable created: dist\FVG_Scanner_Pro.exe
    echo.
    echo You can now run the application by double-clicking:
    echo dist\FVG_Scanner_Pro.exe
    echo.
    echo Or distribute this file to other computers
    echo without needing Python installed.
    echo.
) else (
    echo.
    echo ===============================================
    echo BUILD FAILED!
    echo ===============================================
    echo.
    echo Please check the error messages above
    echo.
)

pause
