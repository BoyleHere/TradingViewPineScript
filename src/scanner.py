import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from colorama import Fore, Style, init
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .data_provider import DataProvider
from .fvg_detector import FVGDetector
from .alert_manager import AlertManager
from .table_display import TableDisplay

# Initialize colorama for colored output
init()

class FVGScanner:
    """Enhanced scanner with real-time optimizations"""
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        self.data_provider = DataProvider(symbols)
        self.data_provider.cache_timeout = config.get('cache_timeout', 30)
        self.data_provider.fast_update_mode = config.get('enable_fast_updates', True)
        
        self.fvg_detector = FVGDetector(threshold=config.get('fvg_threshold', 0.001))
        self.alert_manager = AlertManager(config)
        self.table_display = TableDisplay(config)
        self.logger = logging.getLogger(__name__)
        
        self.scan_results = {}
        self.is_running = False
        self.scan_count = 0
        self.last_scan_time = None
        self.performance_metrics = {
            'avg_scan_time': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'alerts_sent': 0
        }
        self.scan_thread = None
        self.scan_count = 0
        
        # Track previous scan results to detect new signals
        self.previous_results = {}
        
    def scan_single_symbol(self, symbol: str) -> Dict[str, Any]:
        """Scan a single symbol across multiple timeframes"""
        symbol_results = {
            'symbol': symbol,
            'timeframes': {},
            'timestamp': datetime.now()
        }
        
        # Get data for both timeframes
        timeframe_data = self.data_provider.get_multi_timeframe_data(symbol)
        
        for timeframe, data in timeframe_data.items():
            if data is not None and not data.empty:
                analysis = self.fvg_detector.analyze_symbol(symbol, data)
                symbol_results['timeframes'][timeframe] = analysis
            else:
                symbol_results['timeframes'][timeframe] = {
                    'symbol': symbol,
                    'fvgs': [],
                    'ifvgs': [],
                    'active_fvgs': [],
                    'recent_fvg': None,
                    'recent_ifvg': None,
                    'fvg_count': 0,
                    'ifvg_count': 0,
                    'active_fvg_count': 0,
                    'analysis_timestamp': datetime.now(),
                    'current_price': None
                }
        
        return symbol_results
    
    def scan_all_symbols(self) -> Dict[str, Any]:
        """Scan all symbols and return comprehensive results"""
        scan_start_time = datetime.now()
        self.scan_count += 1
        
        scan_results = {
            'scan_number': self.scan_count,
            'timestamp': scan_start_time,
            'symbols': {}
        }
        
        self.logger.info(f"Starting scan #{self.scan_count} of {len(self.symbols)} symbols")
        
        # Update data cache
        self.data_provider.update_cache()
        
        # Scan each symbol
        successful_scans = 0
        for symbol in self.symbols:
            try:
                symbol_results = self.scan_single_symbol(symbol)
                scan_results['symbols'][symbol] = symbol_results
                successful_scans += 1
                
                # Check for new signals and send alerts
                self._check_and_send_alerts(symbol_results)
                
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {str(e)}")
                
        scan_duration = (datetime.now() - scan_start_time).total_seconds()
        
        scan_results['scan_duration'] = scan_duration
        scan_results['successful_scans'] = successful_scans
        scan_results['failed_scans'] = len(self.symbols) - successful_scans
        
        self.scan_results = scan_results
        
        self.logger.info(f"Scan #{self.scan_count} completed in {scan_duration:.2f}s - "
                        f"Success: {successful_scans}/{len(self.symbols)}")
        
        return scan_results
    
    def _check_and_send_alerts(self, symbol_results: Dict[str, Any]):
        """Check for new signals and send alerts"""
        symbol = symbol_results['symbol']
        
        # Get previous results for comparison
        previous_symbol_results = self.previous_results.get(symbol, {})
        
        for timeframe, analysis in symbol_results['timeframes'].items():
            # Check for new FVG
            if analysis['recent_fvg']:
                fvg = analysis['recent_fvg']
                
                # Check if this is a new FVG
                is_new_fvg = True
                if (timeframe in previous_symbol_results.get('timeframes', {}) and
                    previous_symbol_results['timeframes'][timeframe]['recent_fvg']):
                    
                    prev_fvg = previous_symbol_results['timeframes'][timeframe]['recent_fvg']
                    if prev_fvg['timestamp'] == fvg['timestamp']:
                        is_new_fvg = False
                
                if is_new_fvg:
                    self.alert_manager.send_fvg_alert(symbol, timeframe, fvg)
            
            # Check for new iFVG
            if analysis['recent_ifvg']:
                ifvg = analysis['recent_ifvg']
                
                # Check if this is a new iFVG
                is_new_ifvg = True
                if (timeframe in previous_symbol_results.get('timeframes', {}) and
                    previous_symbol_results['timeframes'][timeframe]['recent_ifvg']):
                    
                    prev_ifvg = previous_symbol_results['timeframes'][timeframe]['recent_ifvg']
                    if prev_ifvg['timestamp'] == ifvg['timestamp']:
                        is_new_ifvg = False
                
                if is_new_ifvg:
                    self.alert_manager.send_ifvg_alert(symbol, timeframe, ifvg)
        
        # Update previous results
        self.previous_results[symbol] = symbol_results
    
    def start_continuous_scan(self, interval: int = 60):
        """Start continuous scanning with specified interval"""
        if self.is_running:
            self.logger.warning("Scanner is already running")
            return
            
        self.is_running = True
        self.scan_thread = threading.Thread(target=self._scan_loop, args=(interval,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        self.logger.info(f"Started continuous scanning with {interval}s interval")
        print(f"{Fore.GREEN}✓ Scanner started - Running every {interval} seconds{Style.RESET_ALL}")
    
    def stop_continuous_scan(self):
        """Stop continuous scanning"""
        if not self.is_running:
            self.logger.warning("Scanner is not running")
            return
            
        self.is_running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
            
        self.logger.info("Stopped continuous scanning")
        print(f"{Fore.RED}✗ Scanner stopped{Style.RESET_ALL}")
    
    def _scan_loop(self, interval: int):
        """Main scanning loop"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Perform scan
                results = self.scan_all_symbols()
                
                # Display results if enabled
                if self.config.get('display_table', True):
                    self.table_display.display_results(results)
                
                # Calculate sleep time
                elapsed_time = time.time() - start_time
                sleep_time = max(0, interval - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"Error in scan loop: {str(e)}")
                time.sleep(interval)
    
    def get_summary_table(self) -> pd.DataFrame:
        """Generate a summary table of current scan results"""
        if not self.scan_results:
            return pd.DataFrame()
        
        rows = []
        for symbol, data in self.scan_results['symbols'].items():
            row = {'Symbol': symbol}
            
            # Process each timeframe
            for timeframe in ['5m', '15m']:
                if timeframe in data['timeframes']:
                    analysis = data['timeframes'][timeframe]
                    
                    # Current price
                    if analysis['current_price']:
                        row['Price'] = f"${analysis['current_price']:.2f}"
                    else:
                        row['Price'] = "N/A"
                    
                    # FVG status
                    if analysis['recent_fvg']:
                        fvg_direction = analysis['recent_fvg']['direction']
                        fvg_percentage = analysis['recent_fvg']['gap_percentage']
                        fvg_status = f"{fvg_direction[:4]} ({fvg_percentage:.1f}%)"
                    else:
                        fvg_status = "None"
                    
                    # iFVG status
                    if analysis['recent_ifvg']:
                        ifvg_direction = analysis['recent_ifvg']['direction']
                        ifvg_percentage = analysis['recent_ifvg']['fill_percentage']
                        ifvg_status = f"{ifvg_direction[:4]} ({ifvg_percentage:.1f}%)"
                    else:
                        ifvg_status = "None"
                    
                    # Active FVGs
                    active_count = analysis['active_fvg_count']
                    
                    row[f'FVG_{timeframe}'] = fvg_status
                    row[f'iFVG_{timeframe}'] = ifvg_status
                    row[f'Active_{timeframe}'] = active_count
                    
                else:
                    row['Price'] = "N/A"
                    row[f'FVG_{timeframe}'] = "No Data"
                    row[f'iFVG_{timeframe}'] = "No Data"
                    row[f'Active_{timeframe}'] = 0
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def get_detailed_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific symbol"""
        if not self.scan_results or symbol not in self.scan_results['symbols']:
            return None
        
        return self.scan_results['symbols'][symbol]
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get scanning statistics"""
        if not self.scan_results:
            return {}
        
        total_symbols = len(self.scan_results['symbols'])
        symbols_with_fvg = 0
        symbols_with_ifvg = 0
        total_fvgs = 0
        total_ifvgs = 0
        total_active_fvgs = 0
        
        for symbol_data in self.scan_results['symbols'].values():
            symbol_has_fvg = False
            symbol_has_ifvg = False
            
            for timeframe_data in symbol_data['timeframes'].values():
                if timeframe_data['recent_fvg']:
                    symbol_has_fvg = True
                    total_fvgs += 1
                
                if timeframe_data['recent_ifvg']:
                    symbol_has_ifvg = True
                    total_ifvgs += 1
                
                total_active_fvgs += timeframe_data['active_fvg_count']
            
            if symbol_has_fvg:
                symbols_with_fvg += 1
            if symbol_has_ifvg:
                symbols_with_ifvg += 1
        
        return {
            'scan_number': self.scan_results['scan_number'],
            'scan_timestamp': self.scan_results['timestamp'],
            'scan_duration': self.scan_results.get('scan_duration', 0),
            'total_symbols': total_symbols,
            'successful_scans': self.scan_results.get('successful_scans', 0),
            'failed_scans': self.scan_results.get('failed_scans', 0),
            'symbols_with_fvg': symbols_with_fvg,
            'symbols_with_ifvg': symbols_with_ifvg,
            'total_fvgs': total_fvgs,
            'total_ifvgs': total_ifvgs,
            'total_active_fvgs': total_active_fvgs
        }
    
    def export_results(self, filename: str = None) -> str:
        """Export scan results to CSV"""
        if not self.scan_results:
            raise ValueError("No scan results to export")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fvg_scan_results_{timestamp}.csv"
        
        summary_table = self.get_summary_table()
        summary_table.to_csv(filename, index=False)
        
        self.logger.info(f"Results exported to {filename}")
        return filename
