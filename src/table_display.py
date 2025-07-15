import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from colorama import Fore, Style, init
import os

# Initialize colorama for colored output
init()

class TableDisplay:
    """Handles formatting and display of scan results in table format"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.display_enabled = config.get('display_table', True)
        self.max_table_width = 120
        
    def display_results(self, scan_results: Dict[str, Any]):
        """Display scan results in a formatted table"""
        if not self.display_enabled:
            return
        
        # Clear screen (Windows)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display header
        self._display_header(scan_results)
        
        # Display main results table
        self._display_main_table(scan_results)
        
        # Display statistics
        self._display_statistics(scan_results)
        
    def _display_header(self, scan_results: Dict[str, Any]):
        """Display header information"""
        timestamp = scan_results['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        scan_number = scan_results.get('scan_number', 'N/A')
        duration = scan_results.get('scan_duration', 0)
        
        print(f"{Fore.CYAN}{'='*self.max_table_width}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 FVG SCANNER RESULTS #{scan_number}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*self.max_table_width}{Style.RESET_ALL}")
        print(f"🕐 Scan Time: {timestamp}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📈 Symbols: {len(scan_results['symbols'])}")
        print("")
    
    def _display_main_table(self, scan_results: Dict[str, Any]):
        """Display main results table"""
        if not scan_results['symbols']:
            print(f"{Fore.YELLOW}No symbol data available{Style.RESET_ALL}")
            return
        
        # Create table data
        table_data = []
        headers = ['Symbol', 'Price', 'FVG 5m', 'FVG 15m', 'iFVG 5m', 'iFVG 15m', 'Active']
        
        for symbol, data in scan_results['symbols'].items():
            row = [symbol]
            
            # Get current price (from any available timeframe)
            current_price = None
            for tf_data in data['timeframes'].values():
                if tf_data.get('current_price'):
                    current_price = tf_data['current_price']
                    break
            
            row.append(f"${current_price:.2f}" if current_price else "N/A")
            
            # Process timeframes
            for timeframe in ['5m', '15m']:
                if timeframe in data['timeframes']:
                    analysis = data['timeframes'][timeframe]
                    
                    # FVG status
                    if analysis['recent_fvg']:
                        fvg_direction = analysis['recent_fvg']['direction']
                        fvg_percentage = analysis['recent_fvg']['gap_percentage']
                        fvg_status = f"{fvg_direction[:4]} {fvg_percentage:.1f}%"
                        
                        # Color coding
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
                        ifvg_status = f"{ifvg_direction[:4]} {ifvg_percentage:.1f}%"
                        
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
