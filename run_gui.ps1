# FVG Scanner GUI Launcher (PowerShell)
# Launch the desktop application with proper error handling

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "FVG Scanner - Desktop Application" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "fvg-env")) {
    Write-Host "ERROR: Virtual environment 'fvg-env' not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first to create the environment" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
try {
    & ".\fvg-env\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "Virtual environment activation failed"
    }
} catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in virtual environment" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Launch GUI application
Write-Host "Starting FVG Scanner GUI..." -ForegroundColor Green
Write-Host ""

try {
    python launch_gui.py
    if ($LASTEXITCODE -ne 0) {
        throw "GUI application failed to start"
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: GUI failed to start" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "FVG Scanner GUI closed successfully" -ForegroundColor Green
Read-Host "Press Enter to exit"
