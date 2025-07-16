#!/usr/bin/env python3
"""
FVG Scanner GUI Launcher
Simple launcher for the desktop application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    return True

def check_virtual_environment():
    """Check if virtual environment exists and is activated"""
    venv_path = Path("fvg-env")
    
    if not venv_path.exists():
        print("Virtual environment 'fvg-env' not found!")
        print("Please run setup.bat or setup.ps1 first")
        return False
    
    # Check if we're in the virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Virtual environment not activated!")
        print("Please activate with: fvg-env\\Scripts\\activate")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'tkinter',
        'yfinance',
        'pandas',
        'numpy',
        'colorama',
        'tabulate'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Please install with: pip install -r requirements.txt")
        return False
    
    return True

def launch_gui():
    """Launch the GUI application"""
    try:
        print("Starting FVG Scanner GUI...")
        
        # Import and run the GUI
        from gui_app import FVGScannerGUI
        
        app = FVGScannerGUI()
        app.run()
        
    except Exception as e:
        print(f"Error launching GUI: {str(e)}")
        input("Press Enter to exit...")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("FVG Scanner - Desktop Application Launcher")
    print("=" * 60)
    
    # Check system requirements
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    if not check_virtual_environment():
        input("Press Enter to exit...")
        return
    
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Launch GUI
    launch_gui()

if __name__ == "__main__":
    main()
