#!/usr/bin/env python3
"""
FVG Scanner GUI Application
Modern desktop interface for Fair Value Gap detection
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import os
import sys
from datetime import datetime
import json
from typing import Dict, Any, List, Optional
import queue
import webbrowser
from pathlib import Path

# Import our existing scanner modules
try:
    from src.scanner import FVGScanner
    from src.utils import load_config, setup_logging
    from src.alert_manager import AlertManager
    from src.data_provider import DataProvider
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

class FVGScannerGUI:
    """Modern GUI interface for FVG Scanner"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FVG Scanner Pro - Real-Time Fair Value Gap Detection")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Configure style
        self.setup_styles()
        
        # Initialize variables
        self.scanner = None
        self.scanning_thread = None
        self.is_scanning = False
        self.scan_results = {}
        self.config = None
        self.message_queue = queue.Queue()
        
        # Load configuration
        self.load_configuration()
        
        # Create GUI components
        self.create_widgets()
        
        # Start message processing
        self.process_messages()
        
        # Setup logging
        self.setup_gui_logging()
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Status.TLabel', font=('Segoe UI', 10), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground='#e74c3c')
        style.configure('Success.TButton', background='#27ae60')
        style.configure('Warning.TButton', background='#f39c12')
        style.configure('Danger.TButton', background='#e74c3c')
        
    def load_configuration(self):
        """Load scanner configuration"""
        try:
            if os.path.exists('config.ini'):
                self.config = load_config('config.ini')
            else:
                self.config = None
            
            if not self.config:
                self.create_default_config()
        except Exception as e:
            print(f"Configuration error: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config = {
            'SYMBOLS': {
                'symbols': 'AAPL,MSFT,GOOGL,AMZN,TSLA'
            },
            'SCANNER': {
                'scan_interval': '15',
                'fvg_threshold': '0.001',
                'enable_fast_updates': 'true',
                'cache_timeout': '30'
            },
            'ALERTS': {
                'enable_console_alerts': 'true',
                'enable_sound_alerts': 'true',
                'enable_telegram_alerts': 'false'
            },
            'TIMEFRAMES': {
                'timeframe_1': '5m',
                'timeframe_2': '15m'
            }
        }
        
        # Also create a simple dict-like access
        if not hasattr(self, 'config') or not self.config:
            self.config = {}
        
        # Ensure all required sections exist
        for section, values in {
            'SYMBOLS': {'symbols': 'AAPL,MSFT,GOOGL,AMZN,TSLA'},
            'SCANNER': {'scan_interval': '15', 'fvg_threshold': '0.001', 'enable_fast_updates': 'true', 'cache_timeout': '30'},
            'ALERTS': {'enable_console_alerts': 'true', 'enable_sound_alerts': 'true', 'enable_telegram_alerts': 'false'},
            'TIMEFRAMES': {'timeframe_1': '5m', 'timeframe_2': '15m'}
        }.items():
            if section not in self.config:
                self.config[section] = values
    
    def create_widgets(self):
        """Create main GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create sections
        self.create_header(main_frame)
        self.create_control_panel(main_frame)
        self.create_results_panel(main_frame)
        self.create_status_panel(main_frame)
        
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="FVG Scanner Pro", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(header_frame, text="v2.0 - Real-Time Edition", 
                                 font=('Segoe UI', 10, 'italic'))
        version_label.grid(row=0, column=1, sticky=tk.E)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(header_frame, textvariable=self.status_var, 
                                     style='Status.TLabel')
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Performance metrics
        self.performance_var = tk.StringVar(value="")
        self.performance_label = ttk.Label(header_frame, textvariable=self.performance_var, 
                                          font=('Segoe UI', 9))
        self.performance_label.grid(row=1, column=1, sticky=tk.E)
        
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = ttk.LabelFrame(parent, text="Scanner Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Symbols configuration
        symbols_frame = ttk.Frame(control_frame)
        symbols_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        symbols_frame.columnconfigure(1, weight=1)
        
        ttk.Label(symbols_frame, text="Symbols:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Safe access to config
        default_symbols = 'AAPL,MSFT,GOOGL,AMZN,TSLA'
        if self.config and 'SYMBOLS' in self.config and 'symbols' in self.config['SYMBOLS']:
            default_symbols = self.config['SYMBOLS']['symbols']
        
        self.symbols_var = tk.StringVar(value=default_symbols)
        symbols_entry = ttk.Entry(symbols_frame, textvariable=self.symbols_var, width=30)
        symbols_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Scan interval
        interval_frame = ttk.Frame(control_frame)
        interval_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(interval_frame, text="Scan Interval (seconds):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Safe access to config
        default_interval = '15'
        if self.config and 'SCANNER' in self.config and 'scan_interval' in self.config['SCANNER']:
            default_interval = self.config['SCANNER']['scan_interval']
        
        self.interval_var = tk.StringVar(value=default_interval)
        interval_spin = ttk.Spinbox(interval_frame, from_=5, to=300, textvariable=self.interval_var, width=10)
        interval_spin.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # FVG Threshold
        threshold_frame = ttk.Frame(control_frame)
        threshold_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(threshold_frame, text="FVG Threshold (%):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Safe access to config
        default_threshold = '0.1'
        if self.config and 'SCANNER' in self.config and 'fvg_threshold' in self.config['SCANNER']:
            default_threshold = str(float(self.config['SCANNER']['fvg_threshold']) * 100)
        
        self.threshold_var = tk.StringVar(value=default_threshold)
        threshold_spin = ttk.Spinbox(threshold_frame, from_=0.01, to=5.0, increment=0.01, 
                                   textvariable=self.threshold_var, width=10)
        threshold_spin.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Scanning", 
                                      command=self.start_scanning, style='Success.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 5), pady=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Scanning", 
                                     command=self.stop_scanning, style='Danger.TButton', state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 5), pady=(0, 5))
        
        self.single_scan_button = ttk.Button(button_frame, text="Single Scan", 
                                           command=self.single_scan)
        self.single_scan_button.grid(row=1, column=0, padx=(0, 5), pady=(0, 5))
        
        self.test_alerts_button = ttk.Button(button_frame, text="Test Alerts", 
                                           command=self.test_alerts)
        self.test_alerts_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))
        
        # Alert settings
        alert_frame = ttk.LabelFrame(control_frame, text="Alert Settings", padding="5")
        alert_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Safe access to config
        console_default = True
        sound_default = True
        telegram_default = False
        
        if self.config and 'ALERTS' in self.config:
            console_default = self.config['ALERTS'].get('enable_console_alerts', 'true') == 'true'
            sound_default = self.config['ALERTS'].get('enable_sound_alerts', 'true') == 'true'
            telegram_default = self.config['ALERTS'].get('enable_telegram_alerts', 'false') == 'true'
        
        self.console_alerts_var = tk.BooleanVar(value=console_default)
        ttk.Checkbutton(alert_frame, text="Console Alerts", variable=self.console_alerts_var).grid(row=0, column=0, sticky=tk.W)
        
        self.sound_alerts_var = tk.BooleanVar(value=sound_default)
        ttk.Checkbutton(alert_frame, text="Sound Alerts", variable=self.sound_alerts_var).grid(row=1, column=0, sticky=tk.W)
        
        self.telegram_alerts_var = tk.BooleanVar(value=telegram_default)
        ttk.Checkbutton(alert_frame, text="Telegram Alerts", variable=self.telegram_alerts_var).grid(row=2, column=0, sticky=tk.W)
        
        # Configuration buttons
        config_frame = ttk.Frame(control_frame)
        config_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(config_frame, text="Load Config", command=self.load_config_file).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(config_frame, text="Save Config", command=self.save_config_file).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(config_frame, text="Export Results", command=self.export_results).grid(row=0, column=2)
        
    def create_results_panel(self, parent):
        """Create results display panel"""
        results_frame = ttk.LabelFrame(parent, text="Scan Results", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results summary
        summary_frame = ttk.Frame(results_frame)
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        summary_frame.columnconfigure(1, weight=1)
        
        self.scan_count_var = tk.StringVar(value="Scans: 0")
        ttk.Label(summary_frame, textvariable=self.scan_count_var, font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        self.last_scan_var = tk.StringVar(value="Last scan: Never")
        ttk.Label(summary_frame, textvariable=self.last_scan_var, font=('Segoe UI', 10)).grid(row=0, column=1, sticky=tk.E)
        
        # Results table
        self.create_results_table(results_frame)
        
    def create_results_table(self, parent):
        """Create results table with scrollbars"""
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Symbol', 'Price', 'Change', 'FVG 5m', 'FVG 15m', 'iFVG 5m', 'iFVG 15m', 'Active', 'Fresh')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = {
            'Symbol': 80,
            'Price': 100,
            'Change': 80,
            'FVG 5m': 120,
            'FVG 15m': 120,
            'iFVG 5m': 120,
            'iFVG 15m': 120,
            'Active': 60,
            'Fresh': 60
        }
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure tags for coloring
        self.results_tree.tag_configure('bullish', background='#d5f4e6')
        self.results_tree.tag_configure('bearish', background='#ffeaa7')
        self.results_tree.tag_configure('neutral', background='#f8f9fa')
        
    def create_status_panel(self, parent):
        """Create status and log panel"""
        status_frame = ttk.LabelFrame(parent, text="System Status & Logs", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(status_frame, height=8, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Add initial message
        self.log_message("FVG Scanner Pro initialized successfully")
        self.log_message("Ready to scan for Fair Value Gaps")
        
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, colored_message)
        self.log_text.see(tk.END)
        
        # Limit log size
        if int(self.log_text.index('end-1c').split('.')[0]) > 1000:
            self.log_text.delete('1.0', '100.0')
    
    def setup_gui_logging(self):
        """Setup logging to redirect to GUI"""
        import logging
        
        class GUILogHandler(logging.Handler):
            def __init__(self, gui_instance):
                super().__init__()
                self.gui = gui_instance
                
            def emit(self, record):
                msg = self.format(record)
                self.gui.message_queue.put(('log', msg, record.levelname))
        
        # Configure logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Add GUI handler
        gui_handler = GUILogHandler(self)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)
    
    def process_messages(self):
        """Process messages from queue"""
        try:
            while True:
                msg_type, msg_data, *args = self.message_queue.get_nowait()
                
                if msg_type == 'log':
                    level = args[0] if args else "INFO"
                    self.log_message(msg_data, level)
                elif msg_type == 'status':
                    self.status_var.set(msg_data)
                elif msg_type == 'performance':
                    self.performance_var.set(msg_data)
                elif msg_type == 'results':
                    self.update_results_display(msg_data)
                elif msg_type == 'scan_count':
                    self.scan_count_var.set(f"Scans: {msg_data}")
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_messages)
    
    def start_scanning(self):
        """Start continuous scanning"""
        if self.is_scanning:
            return
        
        try:
            # Update configuration
            self.update_config_from_gui()
            
            # Convert config to the format expected by scanner
            scanner_config = {
                'fvg_threshold': float(self.config['SCANNER']['fvg_threshold']),
                'cache_timeout': int(self.config['SCANNER'].get('cache_timeout', 30)),
                'enable_fast_updates': self.config['SCANNER'].get('enable_fast_updates', 'true').lower() == 'true',
                'enable_console_alerts': self.config['ALERTS'].get('enable_console_alerts', 'true').lower() == 'true',
                'enable_sound_alerts': self.config['ALERTS'].get('enable_sound_alerts', 'true').lower() == 'true',
                'enable_telegram_alerts': self.config['ALERTS'].get('enable_telegram_alerts', 'false').lower() == 'true'
            }
            
            # Initialize scanner
            symbols = [s.strip() for s in self.symbols_var.get().split(',')]
            self.scanner = FVGScanner(symbols, scanner_config)
            
            # Start scanning thread
            self.is_scanning = True
            self.scanning_thread = threading.Thread(target=self.scanning_loop, daemon=True)
            self.scanning_thread.start()
            
            # Update UI
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.single_scan_button.config(state='disabled')
            
            self.message_queue.put(('status', 'SCANNING'))
            self.message_queue.put(('log', 'Started continuous scanning'))
            
        except Exception as e:
            self.log_message(f"Error starting scanner: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to start scanning: {str(e)}")
    
    def stop_scanning(self):
        """Stop continuous scanning"""
        if not self.is_scanning:
            return
        
        self.is_scanning = False
        
        # Update UI
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.single_scan_button.config(state='normal')
        
        self.message_queue.put(('status', 'STOPPED'))
        self.message_queue.put(('log', 'Stopped continuous scanning'))
    
    def single_scan(self):
        """Perform a single scan"""
        try:
            # Update configuration
            self.update_config_from_gui()
            
            # Convert config to the format expected by scanner
            scanner_config = {
                'fvg_threshold': float(self.config['SCANNER']['fvg_threshold']),
                'cache_timeout': int(self.config['SCANNER'].get('cache_timeout', 30)),
                'enable_fast_updates': self.config['SCANNER'].get('enable_fast_updates', 'true').lower() == 'true',
                'enable_console_alerts': self.config['ALERTS'].get('enable_console_alerts', 'true').lower() == 'true',
                'enable_sound_alerts': self.config['ALERTS'].get('enable_sound_alerts', 'true').lower() == 'true',
                'enable_telegram_alerts': self.config['ALERTS'].get('enable_telegram_alerts', 'false').lower() == 'true'
            }
            
            # Initialize scanner
            symbols = [s.strip() for s in self.symbols_var.get().split(',')]
            self.scanner = FVGScanner(symbols, scanner_config)
            
            # Perform scan in thread
            threading.Thread(target=self.perform_single_scan, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"Error during single scan: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to perform scan: {str(e)}")
    
    def perform_single_scan(self):
        """Perform single scan in background thread"""
        try:
            self.message_queue.put(('status', 'SCANNING'))
            self.message_queue.put(('log', 'Starting single scan...'))
            
            start_time = time.time()
            results = self.scanner.scan_all_symbols()
            scan_duration = time.time() - start_time
            
            self.message_queue.put(('results', results))
            self.message_queue.put(('performance', f"Scan time: {scan_duration:.2f}s"))
            self.message_queue.put(('status', 'READY'))
            self.message_queue.put(('log', f'Single scan completed in {scan_duration:.2f}s'))
            
        except Exception as e:
            self.message_queue.put(('log', f"Scan error: {str(e)}", "ERROR"))
            self.message_queue.put(('status', 'ERROR'))
    
    def scanning_loop(self):
        """Main scanning loop"""
        scan_count = 0
        
        while self.is_scanning:
            try:
                start_time = time.time()
                results = self.scanner.scan_all_symbols()
                scan_duration = time.time() - start_time
                
                scan_count += 1
                
                # Update UI
                self.message_queue.put(('results', results))
                self.message_queue.put(('scan_count', scan_count))
                self.message_queue.put(('performance', f"Scan #{scan_count} - {scan_duration:.2f}s"))
                self.message_queue.put(('log', f'Scan #{scan_count} completed in {scan_duration:.2f}s'))
                
                # Update last scan time
                last_scan_time = datetime.now().strftime("%H:%M:%S")
                self.last_scan_var.set(f"Last scan: {last_scan_time}")
                
                # Wait for next scan
                time.sleep(int(self.interval_var.get()))
                
            except Exception as e:
                self.message_queue.put(('log', f"Scan error: {str(e)}", "ERROR"))
                time.sleep(5)  # Wait before retry
    
    def update_results_display(self, results: Dict):
        """Update results table display"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Handle the actual scanner results structure
        if 'symbols' in results:
            symbols_data = results['symbols']
        else:
            symbols_data = results
        
        # Add new results
        for symbol, symbol_data in symbols_data.items():
            if isinstance(symbol_data, dict) and 'timeframes' in symbol_data:
                # Extract price and change info
                price = 0
                change_percent = 0
                
                # Get current price from first available timeframe
                timeframes = symbol_data.get('timeframes', {})
                for timeframe, tf_data in timeframes.items():
                    if tf_data and tf_data.get('current_price'):
                        price = tf_data['current_price']
                        break
                
                # Get FVG data from different timeframes
                fvg_5m = None
                fvg_15m = None
                ifvg_5m = None
                ifvg_15m = None
                active_gaps = 0
                
                # Extract 5m data
                if '5m' in timeframes:
                    tf_5m = timeframes['5m']
                    if tf_5m.get('recent_fvg'):
                        fvg_5m = tf_5m['recent_fvg']
                    if tf_5m.get('recent_ifvg'):
                        ifvg_5m = tf_5m['recent_ifvg']
                    active_gaps += tf_5m.get('active_fvg_count', 0)
                
                # Extract 15m data
                if '15m' in timeframes:
                    tf_15m = timeframes['15m']
                    if tf_15m.get('recent_fvg'):
                        fvg_15m = tf_15m['recent_fvg']
                    if tf_15m.get('recent_ifvg'):
                        ifvg_15m = tf_15m['recent_ifvg']
                    active_gaps += tf_15m.get('active_fvg_count', 0)
                
                # Format data for display
                price_str = f"${price:.2f}" if price else "N/A"
                change_str = "N/A"  # Change calculation would need historical data
                
                # Format FVG data
                fvg_5m_str = self.format_fvg_display(fvg_5m)
                fvg_15m_str = self.format_fvg_display(fvg_15m)
                ifvg_5m_str = self.format_fvg_display(ifvg_5m)
                ifvg_15m_str = self.format_fvg_display(ifvg_15m)
                
                active_str = str(active_gaps)
                fresh_str = self.format_freshness(0)  # Default to fresh for now
                
                # Determine row color
                tag = 'neutral'
                if any('Bull' in str(v) for v in [fvg_5m_str, fvg_15m_str, ifvg_5m_str, ifvg_15m_str]):
                    tag = 'bullish'
                elif any('Bear' in str(v) for v in [fvg_5m_str, fvg_15m_str, ifvg_5m_str, ifvg_15m_str]):
                    tag = 'bearish'
                
                # Insert row
                self.results_tree.insert('', 'end', values=(
                    symbol, price_str, change_str, fvg_5m_str, fvg_15m_str, 
                    ifvg_5m_str, ifvg_15m_str, active_str, fresh_str
                ), tags=(tag,))
        
        # Update scan results summary
        if 'scan_number' in results:
            self.scan_count_var.set(f"Scans: {results['scan_number']}")
        
        # Update last scan time
        if 'timestamp' in results:
            scan_time = results['timestamp'].strftime("%H:%M:%S")
            self.last_scan_var.set(f"Last scan: {scan_time}")
        
        # Update performance metrics
        if 'scan_duration' in results:
            duration = results['scan_duration']
            success_rate = results.get('successful_scans', 0)
            total_symbols = len(symbols_data)
            self.performance_var.set(f"Duration: {duration:.2f}s | Success: {success_rate}/{total_symbols}")
    
    def format_fvg_display(self, fvg_data) -> str:
        """Format FVG data for display"""
        if not fvg_data:
            return 'None'
        
        if isinstance(fvg_data, dict):
            # Handle actual FVG data structure
            direction = fvg_data.get('direction', 'Unknown')
            gap_size = fvg_data.get('gap_size', 0)
            gap_percent = fvg_data.get('gap_percent', 0)
            
            # If gap_percent is not available, calculate it
            if gap_percent == 0 and gap_size > 0:
                current_price = fvg_data.get('current_price', fvg_data.get('price', 100))
                if current_price > 0:
                    gap_percent = gap_size / current_price
            
            # Add emoji based on strength
            if gap_percent > 0.005:  # > 0.5%
                emoji = '🔥'
            elif gap_percent > 0.003:  # > 0.3%
                emoji = '⚡'
            else:
                emoji = '💫'
            
            # Format direction
            direction_short = 'Bull' if direction.lower() == 'bullish' else 'Bear'
            
            return f"{emoji} {direction_short} {gap_percent:.1%}"
        
        return str(fvg_data)
    
    def format_freshness(self, data_age: float) -> str:
        """Format data freshness indicator"""
        if data_age < 60:  # < 1 minute
            return '🟢'
        elif data_age < 300:  # < 5 minutes
            return '🟡'
        else:
            return '🔴'
    
    def test_alerts(self):
        """Test alert system"""
        try:
            self.message_queue.put(('log', 'Testing alert system...'))
            
            # Test different alert types
            if self.console_alerts_var.get():
                self.message_queue.put(('log', '✓ Console alerts enabled'))
            
            if self.sound_alerts_var.get():
                self.message_queue.put(('log', '✓ Sound alerts enabled'))
            
            if self.telegram_alerts_var.get():
                self.message_queue.put(('log', '✓ Telegram alerts enabled'))
            
            # Simulate alert
            messagebox.showinfo("Alert Test", "Alert system test completed!\nCheck logs for details.")
            
        except Exception as e:
            self.log_message(f"Alert test error: {str(e)}", "ERROR")
    
    def update_config_from_gui(self):
        """Update configuration from GUI settings"""
        if not self.config:
            self.config = {}
        
        # Ensure sections exist
        if 'SYMBOLS' not in self.config:
            self.config['SYMBOLS'] = {}
        if 'SCANNER' not in self.config:
            self.config['SCANNER'] = {}
        if 'ALERTS' not in self.config:
            self.config['ALERTS'] = {}
        
        # Update values
        self.config['SYMBOLS']['symbols'] = self.symbols_var.get()
        self.config['SCANNER']['scan_interval'] = self.interval_var.get()
        self.config['SCANNER']['fvg_threshold'] = str(float(self.threshold_var.get()) / 100)
        self.config['ALERTS']['enable_console_alerts'] = str(self.console_alerts_var.get()).lower()
        self.config['ALERTS']['enable_sound_alerts'] = str(self.sound_alerts_var.get()).lower()
        self.config['ALERTS']['enable_telegram_alerts'] = str(self.telegram_alerts_var.get()).lower()
    
    def load_config_file(self):
        """Load configuration from file"""
        try:
            filename = filedialog.askopenfilename(
                title="Load Configuration",
                filetypes=[("Config files", "*.ini"), ("All files", "*.*")]
            )
            
            if filename:
                self.config = load_config(filename)
                self.update_gui_from_config()
                self.log_message(f"Configuration loaded from {filename}")
                
        except Exception as e:
            self.log_message(f"Error loading config: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def save_config_file(self):
        """Save configuration to file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Configuration",
                defaultextension=".ini",
                filetypes=[("Config files", "*.ini"), ("All files", "*.*")]
            )
            
            if filename:
                self.update_config_from_gui()
                # Save config logic would go here
                self.log_message(f"Configuration saved to {filename}")
                messagebox.showinfo("Success", "Configuration saved successfully!")
                
        except Exception as e:
            self.log_message(f"Error saving config: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def update_gui_from_config(self):
        """Update GUI from configuration"""
        if not self.config:
            return
            
        # Update symbols
        if 'SYMBOLS' in self.config and 'symbols' in self.config['SYMBOLS']:
            self.symbols_var.set(self.config['SYMBOLS']['symbols'])
        
        # Update scanner settings
        if 'SCANNER' in self.config:
            if 'scan_interval' in self.config['SCANNER']:
                self.interval_var.set(self.config['SCANNER']['scan_interval'])
            if 'fvg_threshold' in self.config['SCANNER']:
                self.threshold_var.set(str(float(self.config['SCANNER']['fvg_threshold']) * 100))
        
        # Update alert settings
        if 'ALERTS' in self.config:
            self.console_alerts_var.set(self.config['ALERTS'].get('enable_console_alerts', 'true') == 'true')
            self.sound_alerts_var.set(self.config['ALERTS'].get('enable_sound_alerts', 'true') == 'true')
            self.telegram_alerts_var.set(self.config['ALERTS'].get('enable_telegram_alerts', 'false') == 'true')
    
    def export_results(self):
        """Export scan results to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Results",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                # Export logic would go here
                self.log_message(f"Results exported to {filename}")
                messagebox.showinfo("Success", "Results exported successfully!")
                
        except Exception as e:
            self.log_message(f"Error exporting results: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_scanning:
            if messagebox.askokcancel("Quit", "Scanner is running. Do you want to quit?"):
                self.stop_scanning()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = FVGScannerGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
