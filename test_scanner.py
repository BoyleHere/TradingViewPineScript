#!/usr/bin/env python3
"""
Test script to verify FVG Scanner data structure
"""

import sys
sys.path.append('.')

from src.scanner import FVGScanner
from src.utils import load_config
import json

def test_scanner_structure():
    """Test the scanner data structure"""
    # Load config
    config = {
        'fvg_threshold': 0.001,
        'cache_timeout': 30,
        'enable_fast_updates': True,
        'enable_console_alerts': False,
        'enable_sound_alerts': False,
        'enable_telegram_alerts': False
    }
    
    # Create scanner
    symbols = ['AAPL', 'MSFT']
    scanner = FVGScanner(symbols, config)
    
    print("Testing scanner with symbols:", symbols)
    print("=" * 50)
    
    # Perform scan
    results = scanner.scan_all_symbols()
    
    print("Results structure:")
    print("Top level keys:", list(results.keys()))
    print()
    
    if 'symbols' in results:
        print("Symbols data:")
        for symbol, data in results['symbols'].items():
            print(f"\n{symbol}:")
            print(f"  Data type: {type(data)}")
            print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            if isinstance(data, dict) and 'timeframes' in data:
                print(f"  Timeframes: {list(data['timeframes'].keys())}")
                
                for tf, tf_data in data['timeframes'].items():
                    print(f"    {tf}: {list(tf_data.keys()) if isinstance(tf_data, dict) else 'N/A'}")
                    
                    if isinstance(tf_data, dict):
                        print(f"      Current price: {tf_data.get('current_price')}")
                        print(f"      Recent FVG: {tf_data.get('recent_fvg') is not None}")
                        print(f"      Recent iFVG: {tf_data.get('recent_ifvg') is not None}")
                        print(f"      Active FVG count: {tf_data.get('active_fvg_count', 0)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_scanner_structure()
