import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from colorama import Fore, Style, init
import os
import time

# Initialize colorama for colored output
init()

class TableDisplay:
    """Enhanced table display with real-time indicators"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.display_enabled = config.get('display_table', True)
        self.max_table_width = 120
        self.last_display_time = time.time()
        self.refresh_rate = config.get('display_refresh_rate', 1.0)  # Max 1 update per second
        
    def display_results(self, scan_results: Dict[str, Any]):
        """Display scan results with real-time throttling"""
        if not self.display_enabled:
            return
        
        # Throttle display updates to avoid flickering
        current_time = time.time()
        if current_time - self.last_display_time < self.refresh_rate:
            return
        
        self.last_display_time = current_time
        
        # Clear screen (Windows/Unix compatible)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display real-time header
        self._display_realtime_header(scan_results)
        
        # Display main results table
        self._display_main_table(scan_results)
        
        # Display enhanced statistics
        self._display_enhanced_statistics(scan_results)
        
    def _display_realtime_header(self, scan_results: Dict[str, Any]):
        """Display enhanced header with real-time indicators"""
        timestamp = scan_results['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        scan_number = scan_results.get('scan_number', 'N/A')
        duration = scan_results.get('scan_duration', 0)
        
        # Real-time indicators
        data_freshness = self._get_data_freshness(scan_results)
        update_frequency = scan_results.get('update_frequency', 'N/A')
        
        print(f"{Fore.CYAN}{'='*self.max_table_width}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 REAL-TIME FVG SCANNER #{scan_number}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*self.max_table_width}{Style.RESET_ALL}")
        print(f"🕐 Scan Time: {timestamp}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📈 Symbols: {len(scan_results['symbols'])}")
        print(f"🔄 Update Freq: {update_frequency}")
        print(f"📡 Data Freshness: {data_freshness}")
        print(f"🚀 Status: {Fore.GREEN}LIVE SCANNING{Style.RESET_ALL}")
        print("")
    
    def _display_main_table(self, scan_results: Dict[str, Any]):
        """Display enhanced main results table with real-time indicators"""
        if not scan_results['symbols']:
            print(f"{Fore.YELLOW}No symbol data available{Style.RESET_ALL}")
            return
        
        # Create table data with real-time indicators
        table_data = []
        headers = ['Symbol', 'Price', 'Change', 'FVG 5m', 'FVG 15m', 'iFVG 5m', 'iFVG 15m', 'Active', 'Fresh']
        
        for symbol, data in scan_results['symbols'].items():
            row = [symbol]
            
            # Get current price and change
            current_price = None
            price_change = None
            for tf_data in data['timeframes'].values():
                if tf_data.get('current_price'):
                    current_price = tf_data['current_price']
                    price_change = tf_data.get('price_change', 0)
                    break
            
            # Price with color coding
            if current_price:
                price_str = f"${current_price:.2f}"
                row.append(price_str)
                
                # Price change indicator
                if price_change > 0:
                    change_str = f"{Fore.GREEN}+{price_change:.2f}%{Style.RESET_ALL}"
                elif price_change < 0:
                    change_str = f"{Fore.RED}{price_change:.2f}%{Style.RESET_ALL}"
                else:
                    change_str = f"{Fore.LIGHTBLACK_EX}0.00%{Style.RESET_ALL}"
                row.append(change_str)
            else:
                row.append("N/A")
                row.append("N/A")
            
            # Process timeframes with enhanced indicators
            for timeframe in ['5m', '15m']:
                if timeframe in data['timeframes']:
                    analysis = data['timeframes'][timeframe]
                    
                    # FVG status with strength indicator
                    if analysis['recent_fvg']:
                        fvg_direction = analysis['recent_fvg']['direction']
                        fvg_percentage = analysis['recent_fvg']['gap_percentage']
                        
                        # Strength indicator
                        if fvg_percentage > 0.5:
                            strength = "🔥"
                        elif fvg_percentage > 0.3:
                            strength = "⚡"
                        else:
                            strength = "💫"
                        
                        fvg_status = f"{strength} {fvg_direction[:4]} {fvg_percentage:.1f}%"
                        
                        # Color coding with intensity
                        if fvg_direction == 'Bullish':
                            fvg_status = f"{Fore.GREEN}{fvg_status}{Style.RESET_ALL}"
                        else:
                            fvg_status = f"{Fore.RED}{fvg_status}{Style.RESET_ALL}"
                    else:
                        fvg_status = f"{Fore.LIGHTBLACK_EX}None{Style.RESET_ALL}"
                    
                    row.append(fvg_status)
                else:
                    row.append(f"{Fore.LIGHTBLACK_EX}No Data{Style.RESET_ALL}")
            
            # iFVG for both timeframes
            for timeframe in ['5m', '15m']:
                if timeframe in data['timeframes']:
                    analysis = data['timeframes'][timeframe]
                    
                    # iFVG status
                    if analysis['recent_ifvg']:
                        ifvg_direction = analysis['recent_ifvg']['direction']
                        ifvg_percentage = analysis['recent_ifvg']['fill_percentage']
                        ifvg_status = f"🔄 {ifvg_direction[:4]} {ifvg_percentage:.1f}%"
                        
                        # Color coding
                        if ifvg_direction == 'Bullish':
                            ifvg_status = f"{Fore.CYAN}{ifvg_status}{Style.RESET_ALL}"
                        else:
                            ifvg_status = f"{Fore.MAGENTA}{ifvg_status}{Style.RESET_ALL}"
                    else:
                        ifvg_status = f"{Fore.LIGHTBLACK_EX}None{Style.RESET_ALL}"
                    
                    row.append(ifvg_status)
                else:
                    row.append(f"{Fore.LIGHTBLACK_EX}No Data{Style.RESET_ALL}")
            
            # Active FVGs count
            total_active = sum(
                tf_data.get('active_fvg_count', 0) 
                for tf_data in data['timeframes'].values()
            )
            row.append(str(total_active))
            
            # Data freshness indicator
            freshness = data.get('data_freshness', 'Unknown')
            if 'ago' in freshness:
                if 's ago' in freshness:
                    fresh_indicator = f"{Fore.GREEN}🟢{Style.RESET_ALL}"
                elif 'm ago' in freshness and int(freshness.split('m')[0]) < 5:
                    fresh_indicator = f"{Fore.YELLOW}🟡{Style.RESET_ALL}"
                else:
                    fresh_indicator = f"{Fore.RED}🔴{Style.RESET_ALL}"
            else:
                fresh_indicator = f"{Fore.LIGHTBLACK_EX}❓{Style.RESET_ALL}"
            
            row.append(fresh_indicator)
            table_data.append(row)
        
        # Display table
        self._print_table(headers, table_data)
        
    def _display_statistics(self, scan_results: Dict[str, Any]):
        """Display scan statistics"""
        stats = self._calculate_statistics(scan_results)
        
        print(f"\n{Fore.YELLOW}📊 SCAN STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
        
        print(f"✅ Successful Scans: {stats['successful_scans']}/{stats['total_symbols']}")
        print(f"🔥 Symbols with FVG: {stats['symbols_with_fvg']}")
        print(f"🔄 Symbols with iFVG: {stats['symbols_with_ifvg']}")
        print(f"📈 Total Active FVGs: {stats['total_active_fvgs']}")
        
        if stats['failed_scans'] > 0:
            print(f"{Fore.RED}❌ Failed Scans: {stats['failed_scans']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}🚀 Next scan in progress...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*self.max_table_width}{Style.RESET_ALL}")
    
    def _calculate_statistics(self, scan_results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate scan statistics"""
        total_symbols = len(scan_results['symbols'])
        successful_scans = scan_results.get('successful_scans', 0)
        failed_scans = scan_results.get('failed_scans', 0)
        
        symbols_with_fvg = 0
        symbols_with_ifvg = 0
        total_active_fvgs = 0
        
        for symbol_data in scan_results['symbols'].values():
            symbol_has_fvg = False
            symbol_has_ifvg = False
            
            for timeframe_data in symbol_data['timeframes'].values():
                if timeframe_data.get('recent_fvg'):
                    symbol_has_fvg = True
                
                if timeframe_data.get('recent_ifvg'):
                    symbol_has_ifvg = True
                
                total_active_fvgs += timeframe_data.get('active_fvg_count', 0)
            
            if symbol_has_fvg:
                symbols_with_fvg += 1
            if symbol_has_ifvg:
                symbols_with_ifvg += 1
        
        return {
            'total_symbols': total_symbols,
            'successful_scans': successful_scans,
            'failed_scans': failed_scans,
            'symbols_with_fvg': symbols_with_fvg,
            'symbols_with_ifvg': symbols_with_ifvg,
            'total_active_fvgs': total_active_fvgs
        }
    
    def _print_table(self, headers: List[str], data: List[List[str]]):
        """Print formatted table"""
        # Calculate column widths
        widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in data:
                # Strip color codes for width calculation
                clean_cell = self._strip_color_codes(str(row[i]))
                max_width = max(max_width, len(clean_cell))
            widths.append(min(max_width, 15))  # Max width of 15 per column
        
        # Print header
        header_row = "│ " + " │ ".join(
            header.ljust(width) for header, width in zip(headers, widths)
        ) + " │"
        
        separator = "├" + "┼".join("─" * (width + 2) for width in widths) + "┤"
        top_border = "┌" + "┬".join("─" * (width + 2) for width in widths) + "┐"
        bottom_border = "└" + "┴".join("─" * (width + 2) for width in widths) + "┘"
        
        print(top_border)
        print(header_row)
        print(separator)
        
        # Print data rows
        for row in data:
            formatted_row = "│ " + " │ ".join(
                str(cell).ljust(width + len(str(cell)) - len(self._strip_color_codes(str(cell))))
                for cell, width in zip(row, widths)
            ) + " │"
            print(formatted_row)
        
        print(bottom_border)
    
    def _strip_color_codes(self, text: str) -> str:
        """Remove ANSI color codes from text for length calculation"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def display_symbol_details(self, symbol: str, symbol_data: Dict[str, Any]):
        """Display detailed information for a specific symbol"""
        print(f"\n{Fore.CYAN}📊 DETAILED ANALYSIS: {symbol}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        for timeframe, analysis in symbol_data['timeframes'].items():
            print(f"\n{Fore.YELLOW}⏰ {timeframe.upper()} TIMEFRAME{Style.RESET_ALL}")
            print(f"Current Price: ${analysis.get('current_price', 'N/A'):.2f}")
            print(f"Total FVGs: {analysis['fvg_count']}")
            print(f"Total iFVGs: {analysis['ifvg_count']}")
            print(f"Active FVGs: {analysis['active_fvg_count']}")
            
            if analysis['recent_fvg']:
                fvg = analysis['recent_fvg']
                direction_color = Fore.GREEN if fvg['direction'] == 'Bullish' else Fore.RED
                print(f"{direction_color}🔥 Latest FVG: {fvg['direction']} "
                      f"({fvg['gap_percentage']:.2f}%){Style.RESET_ALL}")
                print(f"   Gap: {fvg['gap_start']:.2f} → {fvg['gap_end']:.2f}")
                print(f"   Time: {fvg['timestamp']}")
            
            if analysis['recent_ifvg']:
                ifvg = analysis['recent_ifvg']
                direction_color = Fore.CYAN if ifvg['direction'] == 'Bullish' else Fore.MAGENTA
                print(f"{direction_color}🔄 Latest iFVG: {ifvg['direction']} "
                      f"({ifvg['fill_percentage']:.2f}%){Style.RESET_ALL}")
                print(f"   Fill Price: {ifvg['fill_price']:.2f}")
                print(f"   Time: {ifvg['timestamp']}")
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def create_summary_report(self, scan_results: Dict[str, Any]) -> str:
        """Create a text summary report"""
        timestamp = scan_results['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        stats = self._calculate_statistics(scan_results)
        
        report = f"""
FVG SCANNER SUMMARY REPORT
==========================
Scan Time: {timestamp}
Duration: {scan_results.get('scan_duration', 0):.2f}s
Scan #: {scan_results.get('scan_number', 'N/A')}

STATISTICS:
-----------
Total Symbols: {stats['total_symbols']}
Successful Scans: {stats['successful_scans']}
Failed Scans: {stats['failed_scans']}
Symbols with FVG: {stats['symbols_with_fvg']}
Symbols with iFVG: {stats['symbols_with_ifvg']}
Total Active FVGs: {stats['total_active_fvgs']}

ACTIVE SIGNALS:
--------------
"""
        
        # Add active signals
        for symbol, data in scan_results['symbols'].items():
            has_signals = False
            signal_text = f"{symbol}:\n"
            
            for timeframe, analysis in data['timeframes'].items():
                if analysis['recent_fvg']:
                    fvg = analysis['recent_fvg']
                    signal_text += f"  {timeframe} FVG: {fvg['direction']} ({fvg['gap_percentage']:.1f}%)\n"
                    has_signals = True
                
                if analysis['recent_ifvg']:
                    ifvg = analysis['recent_ifvg']
                    signal_text += f"  {timeframe} iFVG: {ifvg['direction']} ({ifvg['fill_percentage']:.1f}%)\n"
                    has_signals = True
            
            if has_signals:
                report += signal_text + "\n"
        
        return report
    
    def _get_data_freshness(self, scan_results: Dict[str, Any]) -> str:
        """Calculate overall data freshness"""
        if not scan_results['symbols']:
            return "No data"
        
        freshness_values = []
        for symbol_data in scan_results['symbols'].values():
            freshness = symbol_data.get('data_freshness', 'Unknown')
            if 'ago' in freshness:
                if 's ago' in freshness:
                    freshness_values.append(1)  # Fresh
                elif 'm ago' in freshness:
                    freshness_values.append(2)  # Moderate
                else:
                    freshness_values.append(3)  # Stale
            else:
                freshness_values.append(4)  # Unknown
        
        if not freshness_values:
            return "Unknown"
        
        avg_freshness = sum(freshness_values) / len(freshness_values)
        if avg_freshness <= 1.5:
            return f"{Fore.GREEN}Fresh{Style.RESET_ALL}"
        elif avg_freshness <= 2.5:
            return f"{Fore.YELLOW}Moderate{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}Stale{Style.RESET_ALL}"
    
    def _display_enhanced_statistics(self, scan_results: Dict[str, Any]):
        """Display enhanced scan statistics with real-time metrics"""
        stats = self._calculate_statistics(scan_results)
        
        print(f"\n{Fore.YELLOW}📊 REAL-TIME STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
        
        print(f"✅ Successful Scans: {stats['successful_scans']}/{stats['total_symbols']}")
        print(f"🔥 Symbols with FVG: {stats['symbols_with_fvg']}")
        print(f"🔄 Symbols with iFVG: {stats['symbols_with_ifvg']}")
        print(f"📈 Total Active FVGs: {stats['total_active_fvgs']}")
        
        # Real-time performance metrics
        avg_scan_time = scan_results.get('avg_scan_time', 0)
        scan_frequency = scan_results.get('scan_frequency', 'Unknown')
        
        if avg_scan_time > 0:
            print(f"⚡ Avg Scan Time: {avg_scan_time:.2f}s")
        if scan_frequency != 'Unknown':
            print(f"🔄 Scan Frequency: {scan_frequency}")
        
        if stats['failed_scans'] > 0:
            print(f"{Fore.RED}❌ Failed Scans: {stats['failed_scans']}{Style.RESET_ALL}")
        
        # Real-time status
        next_scan_in = scan_results.get('next_scan_in', 0)
        if next_scan_in > 0:
            print(f"\n{Fore.GREEN}🚀 Next scan in {next_scan_in:.0f}s...{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}🚀 Live scanning active...{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*self.max_table_width}{Style.RESET_ALL}")
        
    def _display_statistics(self, scan_results: Dict[str, Any]):
        """Display scan statistics - Legacy method"""
        return self._display_enhanced_statistics(scan_results)
