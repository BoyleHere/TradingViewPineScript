import logging
import configparser
from typing import Dict, Any, List
import os

def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration"""
    log_level = config.get('log_level', 'INFO')
    log_file = config.get('log_file', 'fvg_scanner.log')
    enable_file_logging = config.get('enable_file_logging', True)
    
    handlers = [logging.StreamHandler()]
    
    if enable_file_logging:
        # Use UTF-8 encoding for log file to handle emojis
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Reduce noise from yfinance
    logging.getLogger('yfinance').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def load_config(config_file: str = "config.ini") -> Dict[str, Any]:
    """Load configuration from file"""
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found")
    
    config.read(config_file)
    
    # Parse configuration
    parsed_config = {
        'symbols': config.get('SYMBOLS', 'symbols').split(','),
        'timeframe_1': config.get('TIMEFRAMES', 'timeframe_1'),
        'timeframe_2': config.get('TIMEFRAMES', 'timeframe_2'),
        'telegram_bot_token': config.get('ALERTS', 'telegram_bot_token'),
        'telegram_chat_id': config.get('ALERTS', 'telegram_chat_id'),
        'enable_console_alerts': config.getboolean('ALERTS', 'enable_console_alerts'),
        'enable_telegram_alerts': config.getboolean('ALERTS', 'enable_telegram_alerts'),
        'enable_sound_alerts': config.getboolean('ALERTS', 'enable_sound_alerts'),
        'scan_interval': config.getint('SCANNER', 'scan_interval'),
        'max_lookback_periods': config.getint('SCANNER', 'max_lookback_periods'),
        'fvg_threshold': config.getfloat('SCANNER', 'fvg_threshold'),
        'enable_continuous_scan': config.getboolean('SCANNER', 'enable_continuous_scan'),
        'display_table': config.getboolean('SCANNER', 'display_table'),
        'log_level': config.get('LOGGING', 'log_level'),
        'log_file': config.get('LOGGING', 'log_file'),
        'enable_file_logging': config.getboolean('LOGGING', 'enable_file_logging')
    }
    
    # Clean up symbols (remove whitespace)
    parsed_config['symbols'] = [s.strip().upper() for s in parsed_config['symbols']]
    
    return parsed_config

def validate_symbols(symbols: List[str]) -> List[str]:
    """Validate and clean symbol list"""
    valid_symbols = []
    for symbol in symbols:
        # Basic validation - ensure it's not empty and contains only valid characters
        cleaned = symbol.strip().upper()
        if cleaned and all(c.isalnum() or c in '.-' for c in cleaned):
            if len(cleaned) <= 10:  # Reasonable symbol length limit
                valid_symbols.append(cleaned)
    
    return valid_symbols

def format_currency(value: float) -> str:
    """Format currency values"""
    return f"${value:.2f}"

def format_percentage(value: float) -> str:
    """Format percentage values"""
    return f"{value:.2f}%"

def format_timeframe(timeframe: str) -> str:
    """Format timeframe display"""
    return timeframe.upper()

def create_default_config(config_file: str = "config.ini"):
    """Create a default configuration file"""
    default_config = """[SYMBOLS]
symbols = AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX,AMD,INTC,CRM,ORCL,ADBE,PYPL,DIS,WMT,V,MA,JNJ,PG

[TIMEFRAMES]
timeframe_1 = 5m
timeframe_2 = 15m

[ALERTS]
telegram_bot_token = YOUR_BOT_TOKEN_HERE
telegram_chat_id = YOUR_CHAT_ID_HERE
enable_console_alerts = true
enable_telegram_alerts = false
enable_sound_alerts = true

[SCANNER]
scan_interval = 60
max_lookback_periods = 100
fvg_threshold = 0.001
enable_continuous_scan = true
display_table = true

[LOGGING]
log_level = INFO
log_file = fvg_scanner.log
enable_file_logging = true
"""
    
    with open(config_file, 'w') as f:
        f.write(default_config)
    
    print(f"Default configuration created at {config_file}")
    print("Please edit the configuration file before running the scanner.")

def get_project_info() -> Dict[str, str]:
    """Get project information"""
    return {
        'name': 'FVG Scanner',
        'version': '1.0.0',
        'description': 'A comprehensive TradingView Fair Value Gap scanner in Python',
        'author': 'Trading Analytics Team',
        'license': 'MIT'
    }

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ███████╗██╗   ██╗ ██████╗     ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗  ║
║  ██╔════╝██║   ██║██╔════╝     ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗ ║
║  █████╗  ██║   ██║██║  ███╗    ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝ ║
║  ██╔══╝  ██║   ██║██║   ██║    ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗ ║
║  ██║     ╚██████╔╝╚██████╔╝    ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║ ║
║  ╚═╝      ╚═════╝  ╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                   Fair Value Gap & Inversion FVG Scanner                    ║
║                         Real-time Multi-Symbol Analysis                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'yfinance',
        'pandas',
        'numpy',
        'colorama'
    ]
    
    optional_packages = [
        'telegram'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        print("Please install with: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("Telegram alerts will be disabled")
    
    return True

def setup_environment():
    """Setup the application environment"""
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    return True
