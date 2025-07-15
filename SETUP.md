# Virtual Environment Setup Guide

This guide will help you set up a virtual environment for the FVG Scanner project.

## Why Use a Virtual Environment?

Virtual environments provide isolated Python environments for your projects, preventing dependency conflicts and ensuring consistent behavior across different systems.

## Setup Instructions

### 1. Create Virtual Environment

#### Windows (PowerShell)
```powershell
# Navigate to project directory
cd "d:\Users\Prashast\Desktop\Freelance\TradingViewPineScript"

# Create virtual environment
python -m venv fvg-env

# Activate virtual environment
.\fvg-env\Scripts\Activate.ps1
```

#### Windows (Command Prompt)
```cmd
# Navigate to project directory
cd "d:\Users\Prashast\Desktop\Freelance\TradingViewPineScript"

# Create virtual environment
python -m venv fvg-env

# Activate virtual environment
fvg-env\Scripts\activate.bat
```

#### Linux/macOS
```bash
# Navigate to project directory
cd /path/to/TradingViewPineScript

# Create virtual environment
python3 -m venv fvg-env

# Activate virtual environment
source fvg-env/bin/activate
```

### 2. Install Dependencies

After activating the virtual environment, install the required packages:

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 3. Verify Installation

Check if all packages are installed correctly:

```bash
# List installed packages
pip list

# Check specific packages
python -c "import yfinance; print('yfinance installed successfully')"
python -c "import pandas; print('pandas installed successfully')"
python -c "import numpy; print('numpy installed successfully')"
```

### 4. Create Configuration

Create the default configuration file:

```bash
# Create config file
python main.py --create-config

# Edit the config file to customize settings
```

### 5. Test the Scanner

Run a quick test to ensure everything works:

```bash
# Test basic functionality
python main.py --test-alerts

# Run a single scan
python main.py --single-scan --symbols "AAPL,MSFT"
```

## Virtual Environment Management

### Activating the Environment

Every time you want to work with the scanner, activate the virtual environment:

#### Windows
```powershell
# PowerShell
.\fvg-env\Scripts\Activate.ps1

# Command Prompt
fvg-env\Scripts\activate.bat
```

#### Linux/macOS
```bash
source fvg-env/bin/activate
```

### Deactivating the Environment

To exit the virtual environment:

```bash
deactivate
```

### Updating Dependencies

To update packages to their latest versions:

```bash
# Update specific package
pip install --upgrade yfinance

# Update all packages
pip list --outdated
pip install --upgrade package_name
```

## Common Issues and Solutions

### Issue 1: PowerShell Execution Policy

If you get an execution policy error on Windows:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Python Not Found

If Python is not found:

1. Ensure Python is installed
2. Check if Python is in your PATH
3. Try using `python3` instead of `python`

### Issue 3: pip Not Found

If pip is not available:

```bash
# Install pip
python -m ensurepip --upgrade

# Or download get-pip.py and run
python get-pip.py
```

### Issue 4: Package Installation Fails

If package installation fails:

```bash
# Clear pip cache
pip cache purge

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# Install packages one by one
pip install yfinance
pip install pandas
pip install numpy
```

## Development Environment

For development work, you might want additional tools:

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Format code
black src/

# Run linting
flake8 src/

# Run type checking
mypy src/
```

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./fvg-env/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true
}
```

### PyCharm

1. Go to File → Settings → Project → Python Interpreter
2. Click the gear icon → Add
3. Select "Existing environment"
4. Choose `fvg-env/Scripts/python.exe` (Windows) or `fvg-env/bin/python` (Linux/macOS)

## Automation Script

Create a batch file (Windows) or shell script (Linux/macOS) to automate the setup:

### Windows (setup.bat)
```batch
@echo off
echo Setting up FVG Scanner...

python -m venv fvg-env
call fvg-env\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

python main.py --create-config

echo Setup complete!
echo To run the scanner:
echo   1. Activate environment: fvg-env\Scripts\activate.bat
echo   2. Run scanner: python main.py
pause
```

### Linux/macOS (setup.sh)
```bash
#!/bin/bash
echo "Setting up FVG Scanner..."

python3 -m venv fvg-env
source fvg-env/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python main.py --create-config

echo "Setup complete!"
echo "To run the scanner:"
echo "  1. Activate environment: source fvg-env/bin/activate"
echo "  2. Run scanner: python main.py"
```

## Best Practices

1. **Always activate the virtual environment** before working on the project
2. **Keep requirements.txt updated** when adding new dependencies
3. **Use specific version numbers** in requirements.txt for reproducibility
4. **Don't commit the virtual environment** to version control
5. **Document environment setup** in your project README

## Troubleshooting Commands

```bash
# Check Python version
python --version

# Check virtual environment status
which python  # Linux/macOS
where python   # Windows

# Check installed packages
pip list

# Check package versions
pip show yfinance

# Reinstall all packages
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

This setup ensures you have a clean, isolated environment for running the FVG Scanner without any conflicts with other Python projects on your system.
