# FVG Scanner - Desktop Application Setup Guide

## 🖥️ **GUI Application Overview**

The FVG Scanner now includes a modern desktop application with a user-friendly graphical interface. No more command-line complexity - just point, click, and scan!

### ✨ **GUI Features**

- **Modern Interface**: Clean, intuitive design with real-time updates
- **Live Results Table**: Color-coded FVG detection with strength indicators
- **Real-Time Monitoring**: Live price updates and data freshness indicators
- **Alert Management**: Visual and audio alerts with customizable settings
- **Configuration GUI**: Easy setup without editing config files
- **Performance Metrics**: Real-time scan statistics and performance monitoring
- **Export Functionality**: Save results to CSV files
- **Multi-Threading**: Non-blocking interface with background scanning

## 🚀 **Quick Start Guide**

### **Method 1: Run from Python (Recommended for Development)**

1. **Setup Environment**
   ```bash
   # Activate virtual environment
   fvg-env\Scripts\activate
   
   # Install GUI dependencies
   pip install -r requirements.txt
   ```

2. **Launch GUI**
   ```bash
   # Option 1: Use batch file (Windows)
   run_gui.bat
   
   # Option 2: Use PowerShell
   .\run_gui.ps1
   
   # Option 3: Direct Python
   python launch_gui.py
   ```

### **Method 2: Build Standalone Executable**

1. **Build Application**
   ```bash
   # Run build script
   build_exe.bat
   
   # Or manually with PyInstaller
   pyinstaller --onefile --windowed gui_app.py
   ```

2. **Run Executable**
   ```bash
   # Double-click the executable
   dist\FVG_Scanner_Pro.exe
   
   # Or run from command line
   .\dist\FVG_Scanner_Pro.exe
   ```

3. **Create Desktop Shortcuts**
   ```bash
   # Create desktop and start menu shortcuts
   python create_shortcuts.py
   ```

## 🎯 **GUI Interface Guide**

### **Main Window Layout**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FVG Scanner Pro                                                          v2.0    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Status: READY                                   Performance: Scan #1 - 8.11s    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────────────────────────────────────┐ │
│ │   Scanner Controls  │ │                Scan Results                         │ │
│ │                     │ │                                                     │ │
│ │ Symbols: [________] │ │  Symbol │ Price   │ FVG 5m  │ FVG 15m │ Active      │ │
│ │ Interval: [15s]     │ │  AAPL   │ $210.21 │ 🔥 Bull │ None    │ 16         │ │
│ │ Threshold: [0.1%]   │ │  MSFT   │ $505.68 │ None    │ ⚡ Bull │ 7          │ │
│ │                     │ │  GOOGL  │ $183.25 │ 💫 Bear │ 🔥 Bull │ 14         │ │
│ │ [Start] [Stop]      │ │                                                     │ │
│ │ [Single] [Test]     │ │                                                     │ │
│ │                     │ │                                                     │ │
│ │ Alert Settings:     │ │                                                     │ │
│ │ ☑ Console Alerts    │ │                                                     │ │
│ │ ☑ Sound Alerts      │ │                                                     │ │
│ │ ☐ Telegram Alerts   │ │                                                     │ │
│ │                     │ │                                                     │ │
│ │ [Load] [Save] [Export] │                                                   │ │
│ └─────────────────────┘ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              System Status & Logs                              │
│ [10:55:24] INFO: FVG Scanner Pro initialized successfully                       │
│ [10:55:25] INFO: Started continuous scanning                                   │
│ [10:55:33] INFO: Scan #1 completed in 8.11s                                   │
│ [10:55:41] INFO: Scan #2 completed in 7.95s                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **Control Panel Features**

#### **Scanner Configuration**
- **Symbols**: Comma-separated list of stock symbols (e.g., AAPL,MSFT,GOOGL)
- **Scan Interval**: Time between scans in seconds (5-300)
- **FVG Threshold**: Minimum gap size percentage (0.01-5.0%)

#### **Control Buttons**
- **Start Scanning**: Begin continuous real-time scanning
- **Stop Scanning**: Stop continuous scanning
- **Single Scan**: Perform one-time scan
- **Test Alerts**: Test alert system functionality

#### **Alert Settings**
- **Console Alerts**: Show alerts in log panel
- **Sound Alerts**: Play audio notifications
- **Telegram Alerts**: Send alerts to Telegram bot

#### **File Operations**
- **Load Config**: Load configuration from .ini file
- **Save Config**: Save current settings to .ini file
- **Export Results**: Export scan results to CSV

### **Results Display**

The results table shows real-time FVG detection with:

- **Color Coding**: 
  - 🟢 Green: Bullish patterns
  - 🟡 Yellow: Bearish patterns
  - ⚪ White: Neutral/no patterns

- **Strength Indicators**:
  - 🔥 Strong FVG (>0.5%)
  - ⚡ Medium FVG (0.3-0.5%)
  - 💫 Weak FVG (<0.3%)

- **Data Freshness**:
  - 🟢 Fresh (<1 min)
  - 🟡 Moderate (1-5 min)
  - 🔴 Stale (>5 min)

### **System Logs**

The bottom panel shows:
- Real-time status updates
- Scan completion times
- Error messages and warnings
- Performance metrics

## ⚙️ **Configuration Options**

### **Basic Settings**
```ini
[SYMBOLS]
symbols = AAPL,MSFT,GOOGL,AMZN,TSLA

[SCANNER]
scan_interval = 15
fvg_threshold = 0.001
enable_fast_updates = true

[ALERTS]
enable_console_alerts = true
enable_sound_alerts = true
enable_telegram_alerts = false
```

### **Advanced Settings**
```ini
[SCANNER]
cache_timeout = 30
concurrent_workers = 4
max_retries = 3

[DISPLAY]
show_performance_metrics = true
show_data_freshness = true
auto_scroll_logs = true
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. GUI Won't Start**
```bash
# Check Python version
python --version

# Verify virtual environment
fvg-env\Scripts\activate

# Check dependencies
pip list | findstr tkinter
```

#### **2. Import Errors**
```bash
# Reinstall requirements
pip install -r requirements.txt

# Check module availability
python -c "import tkinter; print('tkinter available')"
```

#### **3. Performance Issues**
- Reduce scan interval (increase seconds)
- Limit number of symbols
- Close other applications

#### **4. Alert Problems**
- Check alert settings in GUI
- Test alerts using "Test Alerts" button
- Verify Telegram bot configuration

### **Debug Mode**
```bash
# Run with debug logging
python gui_app.py --debug

# Check log files
type logs\fvg_scanner.log
```

## 🎨 **Customization**

### **Themes and Styling**
The GUI uses modern tkinter styling with:
- Professional color scheme
- Responsive layout
- High-DPI support
- Custom icons and indicators

### **Adding Custom Features**
```python
# Example: Add custom symbol lists
def add_custom_symbols(self):
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'CUSTOM']
    self.symbols_var.set(','.join(symbols))
```

## 📦 **Distribution**

### **Standalone Executable**
```bash
# Create single-file executable
pyinstaller --onefile --windowed gui_app.py

# Create installer (requires NSIS)
makensis installer.nsi
```

### **System Requirements**
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Network**: Internet connection for market data

## 🚀 **Advanced Features**

### **Performance Monitoring**
- Real-time scan duration tracking
- Success rate statistics
- Memory usage monitoring
- API call efficiency metrics

### **Data Export**
- CSV export with timestamps
- Summary reports
- Performance analytics
- Historical data logging

### **Alert System**
- Multiple notification channels
- Customizable alert rules
- Alert history tracking
- Cooldown periods

## 📝 **Usage Tips**

1. **Start with Default Settings**: Use the pre-configured symbols and intervals
2. **Monitor Performance**: Watch scan times and adjust interval accordingly
3. **Use Single Scan**: Test configuration before starting continuous scanning
4. **Save Configurations**: Create different setups for different trading sessions
5. **Check Logs**: Monitor the log panel for errors and performance info

## 🎯 **Next Steps**

After setting up the GUI:
1. Configure your preferred symbols
2. Set appropriate scan intervals
3. Test alert system
4. Start continuous scanning
5. Monitor results in real-time

The GUI application transforms the command-line FVG scanner into a professional desktop tool suitable for daily trading use!

---

**Happy Trading with FVG Scanner Pro! 📈**
