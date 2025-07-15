# Virtual Environment Setup and Run Commands

## Quick Setup (Windows PowerShell)

```powershell
# Navigate to project directory
cd "d:\Users\Prashast\Desktop\Freelance\TradingViewPineScript"

# Create virtual environment
python -m venv fvg-env

# Activate virtual environment
.\fvg-env\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create configuration file
python main.py --create-config

# Test the scanner
python main.py --test-alerts
```

## Running the Scanner

### After Setup (Always activate environment first)

```powershell
# Activate virtual environment
.\fvg-env\Scripts\Activate.ps1

# Run continuous scanner
python main.py

# Run single scan
python main.py --single-scan

# Run with custom symbols
python main.py --symbols "AAPL,MSFT,GOOGL,TSLA"

# Run with custom interval
python main.py --interval 30
```

## Key Commands

### Configuration
```bash
# Create default config
python main.py --create-config

# Edit config file
notepad config.ini  # Windows
```

### Scanner Operations
```bash
# Continuous scanning (default)
python main.py

# Single scan only
python main.py --single-scan

# Test alerts
python main.py --test-alerts

# Export results
python main.py --single-scan --export
```

### Customization
```bash
# Custom symbols
python main.py --symbols "AAPL,MSFT,GOOGL"

# Custom scan interval (seconds)
python main.py --interval 60

# Disable table display
python main.py --no-display

# Debug mode
python main.py --log-level DEBUG
```

## Configuration (config.ini)

Key settings to modify:

```ini
[SYMBOLS]
symbols = AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX,AMD,INTC

[SCANNER]
scan_interval = 60
fvg_threshold = 0.001

[ALERTS]
enable_console_alerts = true
enable_sound_alerts = true
enable_telegram_alerts = false
```

## Telegram Setup (Optional)

1. Create bot with @BotFather on Telegram
2. Get bot token and chat ID
3. Update config.ini:
```ini
[ALERTS]
telegram_bot_token = YOUR_BOT_TOKEN
telegram_chat_id = YOUR_CHAT_ID
enable_telegram_alerts = true
```

## Troubleshooting

### If packages are missing:
```bash
pip install -r requirements.txt
```

### If Python not found:
```bash
python --version
# or try
python3 --version
```

### If virtual environment issues:
```bash
# Deactivate and recreate
deactivate
rmdir /s fvg-env
python -m venv fvg-env
```

## Example Usage

1. **Basic scan of tech stocks:**
```bash
python main.py --symbols "AAPL,MSFT,GOOGL,AMZN,TSLA" --single-scan
```

2. **Continuous monitoring with alerts:**
```bash
python main.py --interval 30
```

3. **Export results to CSV:**
```bash
python main.py --single-scan --export
```

The scanner will display a real-time table showing FVG and iFVG signals for each symbol and timeframe, with color-coded alerts for new patterns detected.
