# FVG Scanner Setup Script for PowerShell
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "FVG Scanner - Virtual Environment Setup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
python -m venv fvg-env

Write-Host ""
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& ".\fvg-env\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Step 5: Creating configuration file..." -ForegroundColor Yellow
python main.py --create-config

Write-Host ""
Write-Host "Step 6: Testing installation..." -ForegroundColor Yellow
python main.py --test-alerts

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the scanner:" -ForegroundColor White
Write-Host "  1. Activate environment: .\fvg-env\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  2. Run scanner: python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "For more options, run: python main.py --help" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
