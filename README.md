# FVG Scanner - Fair Value Gap Detection System

A comprehensive Python-based scanner for detecting Fair Value Gaps (FVGs) and Inversion Fair Value Gaps (iFVGs) across multiple symbols and timeframes, designed as a powerful alternative to Pine Script for TradingView analysis.

## 🎯 Features

### Core Functionality
- **Multi-Symbol Scanning**: Monitor up to 20 symbols simultaneously
- **Multi-Timeframe Support**: Analyze 5-minute and 15-minute timeframes
- **Real-time Detection**: Detect FVGs and iFVGs as they form
- **Advanced Pattern Recognition**: Sophisticated algorithms for accurate gap detection
- **Active Gap Tracking**: Monitor unfilled gaps across all symbols

### Alert System
- **Multiple Alert Channels**: Console, sound, and Telegram notifications
- **Smart Alert Management**: Cooldown periods to prevent spam
- **Detailed Alert Information**: Complete gap details with percentages and prices
- **Alert History**: Track all alerts with statistics

### User Interface
- **Real-time Table Display**: Live updating results in formatted tables
- **Color-coded Results**: Visual distinction between bullish/bearish signals
- **Detailed Symbol Analysis**: In-depth breakdown for individual symbols
- **Export Functionality**: Save results to CSV and generate reports

### Technical Features
- **Robust Data Handling**: Automatic data validation and error recovery
- **Performance Optimized**: Efficient scanning with minimal resource usage
- **Configurable Parameters**: Customizable thresholds and intervals
- **Comprehensive Logging**: Full audit trail for debugging and analysis

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- Windows/Linux/macOS support
- Internet connection for data fetching

### Python Dependencies
```
yfinance==0.2.18      # Market data fetching
pandas==2.0.3         # Data manipulation
numpy==1.24.3         # Numerical computations
colorama==0.4.6       # Colored terminal output
tabulate==0.9.0       # Table formatting
```

### Optional Dependencies
```
python-telegram-bot==20.3  # Telegram notifications
matplotlib==3.7.1         # Charts and visualization
```

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
# Create virtual environment
python -m venv fvg-env

# Activate virtual environment
# Windows:
fvg-env\Scripts\activate
# Linux/Mac:
source fvg-env/bin/activate
```

### 2. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Create default configuration
python main.py --create-config

# Edit config.ini with your preferences
```

### 4. Run Scanner
```bash
# Single scan
python main.py --single-scan

# Continuous scanning
python main.py

# Test alerts
python main.py --test-alerts
```

## ⚙️ Configuration

### Basic Configuration (config.ini)
```ini
[SYMBOLS]
symbols = AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX,AMD,INTC

[TIMEFRAMES]
timeframe_1 = 5m
timeframe_2 = 15m

[ALERTS]
enable_console_alerts = true
enable_sound_alerts = true
enable_telegram_alerts = false

[SCANNER]
scan_interval = 60
fvg_threshold = 0.001
display_table = true
```

### Telegram Setup (Optional)
1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Get your bot token and chat ID
3. Update config.ini:
```ini
[ALERTS]
telegram_bot_token = YOUR_BOT_TOKEN
telegram_chat_id = YOUR_CHAT_ID
enable_telegram_alerts = true
```

## 🔧 Usage Examples

### Command Line Options
```bash
# Basic usage
python main.py                                    # Continuous scanning
python main.py --single-scan                      # Single scan only
python main.py --symbols "AAPL,MSFT,GOOGL"      # Custom symbols
python main.py --interval 30                      # 30-second intervals
python main.py --test-alerts                      # Test alert system
python main.py --export                           # Export results to CSV
python main.py --no-display                       # Disable table display
```

### Programmatic Usage
```python
from src.scanner import FVGScanner
from src.utils import load_config

# Load configuration
config = load_config('config.ini')

# Initialize scanner
symbols = ['AAPL', 'MSFT', 'GOOGL']
scanner = FVGScanner(symbols, config)

# Single scan
results = scanner.scan_all_symbols()

# Continuous scanning
scanner.start_continuous_scan(interval=60)
```

## 📊 Understanding the Results

### FVG Detection
- **Bullish FVG**: Gap between previous candle's high and current candle's low
- **Bearish FVG**: Gap between previous candle's low and current candle's high
- **Threshold**: Minimum gap size (default: 0.1%) to filter noise

### iFVG Detection
- **Inversion FVG**: Occurs when price fills a previous FVG and then reverses
- **Bullish iFVG**: Price fills bearish FVG and reverses upward
- **Bearish iFVG**: Price fills bullish FVG and reverses downward

### Results Table
```
Symbol  │ Price   │ FVG 5m      │ FVG 15m     │ iFVG 5m     │ iFVG 15m    │ Active
AAPL    │ $150.25 │ Bull 0.8%   │ None        │ None        │ Bear 1.2%   │ 2
MSFT    │ $280.50 │ None        │ Bear 0.5%   │ Bull 0.9%   │ None        │ 1
```

### Alert Format
```
🔥 FVG Alert! 🟢
Symbol: AAPL
Timeframe: 5m
Direction: Bullish
Gap Size: 1.2500
Gap %: 0.83%
Time: 2024-01-15 10:35:00
```

## 🔬 Technical Details

### FVG Detection Algorithm
1. **Gap Identification**: Compare candle relationships over 3-period window
2. **Threshold Filtering**: Apply minimum gap size filter
3. **Direction Classification**: Determine bullish/bearish nature
4. **Percentage Calculation**: Calculate gap size as percentage of price

### iFVG Detection Process
1. **Gap Monitoring**: Track all detected FVGs
2. **Fill Detection**: Monitor for price returning to gap zone
3. **Reversal Confirmation**: Verify price reversal after fill
4. **Classification**: Determine inversion direction

### Data Management
- **Real-time Updates**: Fetch latest market data every scan
- **Data Validation**: Automatic error checking and cleanup
- **Caching System**: Efficient data storage and retrieval
- **Error Recovery**: Graceful handling of network/data issues

## 🛠️ Advanced Features

### Custom Symbol Lists
```python
# Override symbols programmatically
scanner = FVGScanner(['AAPL', 'MSFT', 'GOOGL'], config)

# Or via command line
python main.py --symbols "AAPL,MSFT,GOOGL,AMZN,TSLA"
```

### Export and Reporting
```python
# Export results to CSV
filename = scanner.export_results()

# Generate summary report
report = scanner.table_display.create_summary_report(results)
```

### Performance Monitoring
```python
# Get scan statistics
stats = scanner.get_scan_statistics()
print(f"Scan duration: {stats['scan_duration']:.2f}s")
print(f"Success rate: {stats['successful_scans']}/{stats['total_symbols']}")
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_fvg_detector.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

### Test Examples
```bash
# Test FVG detection
python tests/test_fvg_detector.py

# Test scanner functionality
python examples/basic_usage.py
```

## 📈 Performance Optimization

### Scan Interval Recommendations
- **High Frequency**: 30-60 seconds for active trading
- **Standard**: 60-120 seconds for general monitoring
- **Low Frequency**: 300+ seconds for long-term analysis

### Resource Management
- **Memory Usage**: ~50-100MB for 20 symbols
- **CPU Usage**: Low impact during scans
- **Network**: Minimal data usage with caching

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. No Data Received**
```bash
# Check internet connection and symbol validity
python main.py --symbols "AAPL" --single-scan
```

**3. Telegram Alerts Not Working**
```bash
# Verify bot token and chat ID
python main.py --test-alerts
```

**4. High CPU Usage**
```bash
# Increase scan interval
python main.py --interval 120
```

### Debug Mode
```bash
# Enable debug logging
python main.py --log-level DEBUG
```

## 📋 Roadmap

### Planned Features
- [ ] Web dashboard interface
- [ ] Email alert support
- [ ] Advanced pattern recognition
- [ ] Historical backtesting
- [ ] Portfolio-level analysis
- [ ] API integration
- [ ] Mobile app support

### Current Limitations
- Real-time data depends on yfinance availability
- Limited to supported Yahoo Finance symbols
- No intraday historical data beyond current session

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd fvg-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add comprehensive docstrings
- Include unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

For support, questions, or feature requests:
- Create an issue on GitHub
- Check the examples directory for usage patterns
- Review the test files for implementation details

## 🎯 Conclusion

The FVG Scanner provides a comprehensive solution for Fair Value Gap detection, offering the functionality of Pine Script with the flexibility and power of Python. Whether you're a day trader looking for real-time alerts or an analyst conducting market research, this scanner delivers the tools you need for effective gap analysis.

The combination of multi-symbol scanning, real-time alerts, and detailed analysis makes it an invaluable tool for technical analysis and trading strategy development.

---

**Happy Trading! 📈**
