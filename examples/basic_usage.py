"""
Basic usage examples for the FVG Scanner
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils import setup_logging, load_config
from src.scanner import FVGScanner

def basic_single_scan():
    """Example of a basic single scan"""
    print("=== BASIC SINGLE SCAN EXAMPLE ===")
    
    # Setup
    config = load_config('config.ini')
    setup_logging(config)
    
    # Initialize scanner with a few symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    scanner = FVGScanner(symbols, config)
    
    # Run scan
    print(f"Scanning {len(symbols)} symbols: {', '.join(symbols)}")
    results = scanner.scan_all_symbols()
    
    # Display results
    summary_table = scanner.get_summary_table()
    if not summary_table.empty:
        print("\nFVG Scanner Results:")
        print("=" * 80)
        print(summary_table.to_string(index=False))
        print("=" * 80)
    else:
        print("No data available for summary")
    
    # Get detailed results for a specific symbol
    if 'AAPL' in results['symbols']:
        aapl_results = results['symbols']['AAPL']
        print(f"\nDetailed results for AAPL:")
        print(f"Scan timestamp: {aapl_results['timestamp']}")
        
        for timeframe, analysis in aapl_results['timeframes'].items():
            print(f"\n{timeframe} timeframe:")
            print(f"  Current price: ${analysis.get('current_price', 'N/A')}")
            print(f"  FVGs found: {analysis['fvg_count']}")
            print(f"  iFVGs found: {analysis['ifvg_count']}")
            print(f"  Active FVGs: {analysis['active_fvg_count']}")
            
            if analysis['recent_fvg']:
                fvg = analysis['recent_fvg']
                print(f"  Latest FVG: {fvg['direction']} - {fvg['gap_percentage']:.2f}%")
                print(f"              Gap: {fvg['gap_start']:.2f} → {fvg['gap_end']:.2f}")
                print(f"              Time: {fvg['timestamp']}")
            
            if analysis['recent_ifvg']:
                ifvg = analysis['recent_ifvg']
                print(f"  Latest iFVG: {ifvg['direction']} - {ifvg['fill_percentage']:.2f}%")
                print(f"               Fill price: {ifvg['fill_price']:.2f}")
                print(f"               Time: {ifvg['timestamp']}")

def continuous_scan_example():
    """Example of continuous scanning"""
    print("\n=== CONTINUOUS SCAN EXAMPLE ===")
    
    # Setup
    config = load_config('config.ini')
    setup_logging(config)
    
    # Initialize scanner
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    scanner = FVGScanner(symbols, config)
    
    print(f"Starting continuous scan for {len(symbols)} symbols")
    print("This will run for 2 minutes...")
    
    # Start continuous scanning
    scanner.start_continuous_scan(interval=30)  # 30 second interval
    
    # Let it run for a while
    import time
    time.sleep(120)  # Run for 2 minutes
    
    # Stop scanning
    scanner.stop_continuous_scan()
    
    # Show final results
    summary_table = scanner.get_summary_table()
    if not summary_table.empty:
        print("\nFinal Results:")
        print("=" * 60)
        print(summary_table.to_string(index=False))
        print("=" * 60)
    
    # Show statistics
    stats = scanner.get_scan_statistics()
    if stats:
        print(f"\nScan Statistics:")
        print(f"Total scans: {stats['scan_number']}")
        print(f"Last scan duration: {stats['scan_duration']:.2f}s")
        print(f"Symbols with FVG: {stats['symbols_with_fvg']}")
        print(f"Symbols with iFVG: {stats['symbols_with_ifvg']}")
        print(f"Total active FVGs: {stats['total_active_fvgs']}")

def test_alerts_example():
    """Example of testing the alert system"""
    print("\n=== ALERT TEST EXAMPLE ===")
    
    # Setup
    config = load_config('config.ini')
    setup_logging(config)
    
    # Initialize scanner
    symbols = ['AAPL']
    scanner = FVGScanner(symbols, config)
    
    # Test alerts
    print("Testing alert system...")
    scanner.alert_manager.test_alerts()
    
    # Show alert history
    alert_history = scanner.alert_manager.get_alert_history(limit=5)
    if alert_history:
        print(f"\nRecent alerts ({len(alert_history)}):")
        for alert in alert_history:
            print(f"  {alert['timestamp']}: {alert['data']['type']} - {alert['data']['symbol']}")

def symbol_analysis_example():
    """Example of detailed symbol analysis"""
    print("\n=== SYMBOL ANALYSIS EXAMPLE ===")
    
    # Setup
    config = load_config('config.ini')
    setup_logging(config)
    
    # Initialize scanner
    symbols = ['AAPL', 'TSLA']
    scanner = FVGScanner(symbols, config)
    
    # Run scan
    scanner.scan_all_symbols()
    
    # Analyze specific symbols
    for symbol in symbols:
        analysis = scanner.get_detailed_analysis(symbol)
        if analysis:
            print(f"\n--- {symbol} Analysis ---")
            scanner.table_display.display_symbol_details(symbol, analysis)

def export_example():
    """Example of exporting results"""
    print("\n=== EXPORT EXAMPLE ===")
    
    # Setup
    config = load_config('config.ini')
    setup_logging(config)
    
    # Initialize scanner
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    scanner = FVGScanner(symbols, config)
    
    # Run scan
    scanner.scan_all_symbols()
    
    # Export results
    try:
        filename = scanner.export_results()
        print(f"Results exported to: {filename}")
        
        # Also create a summary report
        report = scanner.table_display.create_summary_report(scanner.scan_results)
        report_filename = f"fvg_report_{scanner.scan_results['timestamp'].strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"Summary report saved to: {report_filename}")
        
    except Exception as e:
        print(f"Export failed: {str(e)}")

if __name__ == "__main__":
    # Change to the parent directory (TradingViewPineScript)
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    
    print("FVG Scanner Examples")
    print("=" * 50)
    
    try:
        # Run examples
        basic_single_scan()
        continuous_scan_example()
        test_alerts_example()
        symbol_analysis_example()
        export_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()
