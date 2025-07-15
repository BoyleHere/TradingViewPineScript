#!/usr/bin/env python3
"""
TradingView FVG Scanner
A comprehensive scanner for Fair Value Gaps (FVGs) and Inversion Fair Value Gaps (iFVGs)
"""

import argparse
import sys
import signal
import time
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import (
    setup_logging, load_config, validate_symbols, 
    print_banner, setup_environment, create_default_config
)
from src.scanner import FVGScanner

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Received interrupt signal. Shutting down...")
    sys.exit(0)

def main():
    """Main application entry point"""
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description='TradingView FVG Scanner - Real-time Fair Value Gap Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Run continuous scanner
  python main.py --single-scan       # Run single scan
  python main.py --test-alerts       # Test alert system
  python main.py --symbols AAPL,MSFT # Override symbols
  python main.py --create-config     # Create default config file
        """
    )
    
    parser.add_argument('--config', default='config.ini', help='Configuration file path')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--single-scan', action='store_true', 
                       help='Run single scan instead of continuous')
    parser.add_argument('--test-alerts', action='store_true', 
                       help='Test alert system')
    parser.add_argument('--symbols', type=str, 
                       help='Comma-separated list of symbols to scan')
    parser.add_argument('--interval', type=int, default=None,
                       help='Scan interval in seconds (overrides config)')
    parser.add_argument('--create-config', action='store_true',
                       help='Create default configuration file')
    parser.add_argument('--export', action='store_true',
                       help='Export results to CSV after scan')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable table display')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Create default config if requested
    if args.create_config:
        create_default_config(args.config)
        return
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Please check dependencies.")
        sys.exit(1)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Override config with command line arguments
        if args.symbols:
            config['symbols'] = [s.strip().upper() for s in args.symbols.split(',')]
        
        if args.interval:
            config['scan_interval'] = args.interval
        
        if args.no_display:
            config['display_table'] = False
        
        # Setup logging
        setup_logging(config)
        
        # Validate symbols
        symbols = validate_symbols(config['symbols'])
        if not symbols:
            print("❌ Error: No valid symbols found in configuration")
            sys.exit(1)
        
        # Display configuration
        print(f"🔧 Configuration:")
        print(f"   📊 Symbols: {len(symbols)} ({', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''})")
        print(f"   ⏱️  Scan interval: {config['scan_interval']} seconds")
        print(f"   🎯 FVG threshold: {config['fvg_threshold']}")
        print(f"   🔊 Console alerts: {'✓' if config['enable_console_alerts'] else '✗'}")
        print(f"   📱 Telegram alerts: {'✓' if config['enable_telegram_alerts'] else '✗'}")
        print(f"   🔔 Sound alerts: {'✓' if config['enable_sound_alerts'] else '✗'}")
        print(f"   📋 Table display: {'✓' if config['display_table'] else '✗'}")
        
        # Initialize scanner
        scanner = FVGScanner(symbols, config)
        
        # Test alerts if requested
        if args.test_alerts:
            print("\n🧪 Testing alert system...")
            scanner.alert_manager.test_alerts()
            print("✅ Alert test completed!")
            return
        
        # Run scanner
        if args.single_scan:
            print("\n🚀 Running single scan...")
            results = scanner.scan_all_symbols()
            
            # Display results
            if config['display_table']:
                scanner.table_display.display_results(results)
            
            # Display summary
            summary_table = scanner.get_summary_table()
            if not summary_table.empty:
                print("\n📊 SCAN SUMMARY:")
                print("=" * 80)
                print(summary_table.to_string(index=False))
                print("=" * 80)
            else:
                print("❌ No data available for summary")
            
            # Export if requested
            if args.export:
                try:
                    filename = scanner.export_results()
                    print(f"📁 Results exported to: {filename}")
                except Exception as e:
                    print(f"❌ Export failed: {str(e)}")
                    
            # Display statistics
            stats = scanner.get_scan_statistics()
            if stats:
                print(f"\n📈 Statistics:")
                print(f"   Duration: {stats['scan_duration']:.2f}s")
                print(f"   Success Rate: {stats['successful_scans']}/{stats['total_symbols']}")
                print(f"   Symbols with FVG: {stats['symbols_with_fvg']}")
                print(f"   Symbols with iFVG: {stats['symbols_with_ifvg']}")
                print(f"   Total Active FVGs: {stats['total_active_fvgs']}")
            
        else:
            print("\n🚀 Starting continuous scanning...")
            print("📝 Press Ctrl+C to stop")
            print("=" * 80)
            
            scanner.start_continuous_scan(config['scan_interval'])
            
            # Keep the main thread alive and show periodic updates
            try:
                last_display_time = time.time()
                while True:
                    time.sleep(1)
                    
                    # Show periodic status updates
                    current_time = time.time()
                    if current_time - last_display_time >= 60:  # Every minute
                        stats = scanner.get_scan_statistics()
                        if stats:
                            print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] "
                                 f"Scan #{stats['scan_number']} - "
                                 f"Active FVGs: {stats['total_active_fvgs']}")
                        last_display_time = current_time
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping scanner...")
                scanner.stop_continuous_scan()
                print("✅ Scanner stopped successfully!")
                
                # Show final statistics
                stats = scanner.get_scan_statistics()
                if stats:
                    print(f"\n📊 Final Statistics:")
                    print(f"   Total Scans: {stats['scan_number']}")
                    print(f"   Last Scan Duration: {stats['scan_duration']:.2f}s")
                    print(f"   Success Rate: {stats['successful_scans']}/{stats['total_symbols']}")
                
                # Show alert history
                alert_stats = scanner.alert_manager.get_alert_stats()
                if alert_stats['total_alerts'] > 0:
                    print(f"\n🚨 Alert Summary:")
                    print(f"   Total Alerts: {alert_stats['total_alerts']}")
                    print(f"   FVG Alerts: {alert_stats['fvg_alerts']}")
                    print(f"   iFVG Alerts: {alert_stats['ifvg_alerts']}")
                    print(f"   Bullish Alerts: {alert_stats['bullish_alerts']}")
                    print(f"   Bearish Alerts: {alert_stats['bearish_alerts']}")
                
    except FileNotFoundError as e:
        print(f"❌ Configuration Error: {str(e)}")
        print("💡 Use --create-config to create a default configuration file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
