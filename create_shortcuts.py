"""
Desktop Shortcut Creator for FVG Scanner
Creates a desktop shortcut for easy access
"""

import os
import sys
from pathlib import Path
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    """Create desktop shortcut for FVG Scanner"""
    try:
        # Get current directory
        current_dir = Path.cwd()
        
        # Check if executable exists
        exe_path = current_dir / "dist" / "FVG_Scanner_Pro.exe"
        if not exe_path.exists():
            print("ERROR: FVG_Scanner_Pro.exe not found!")
            print("Please run build_exe.bat first to create the executable")
            return False
        
        # Get desktop path
        desktop = winshell.desktop()
        
        # Create shortcut
        shortcut_path = os.path.join(desktop, "FVG Scanner Pro.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(exe_path)
        shortcut.WorkingDirectory = str(current_dir)
        shortcut.Description = "FVG Scanner Pro - Real-Time Fair Value Gap Detection"
        
        # Set icon if available
        icon_path = current_dir / "assets" / "icon.ico"
        if icon_path.exists():
            shortcut.IconLocation = str(icon_path)
        
        shortcut.save()
        
        print(f"Desktop shortcut created successfully!")
        print(f"Shortcut location: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Error creating desktop shortcut: {str(e)}")
        print("You may need to install: pip install pywin32 winshell")
        return False

def create_start_menu_shortcut():
    """Create Start Menu shortcut"""
    try:
        # Get current directory
        current_dir = Path.cwd()
        
        # Check if executable exists
        exe_path = current_dir / "dist" / "FVG_Scanner_Pro.exe"
        if not exe_path.exists():
            return False
        
        # Get Start Menu programs folder
        start_menu = winshell.programs()
        
        # Create FVG Scanner folder
        fvg_folder = os.path.join(start_menu, "FVG Scanner")
        os.makedirs(fvg_folder, exist_ok=True)
        
        # Create shortcut
        shortcut_path = os.path.join(fvg_folder, "FVG Scanner Pro.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(exe_path)
        shortcut.WorkingDirectory = str(current_dir)
        shortcut.Description = "FVG Scanner Pro - Real-Time Fair Value Gap Detection"
        
        # Set icon if available
        icon_path = current_dir / "assets" / "icon.ico"
        if icon_path.exists():
            shortcut.IconLocation = str(icon_path)
        
        shortcut.save()
        
        print(f"Start Menu shortcut created successfully!")
        print(f"Shortcut location: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Error creating Start Menu shortcut: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("FVG Scanner - Desktop Shortcut Creator")
    print("=" * 60)
    print()
    
    # Create desktop shortcut
    print("Creating desktop shortcut...")
    if create_desktop_shortcut():
        print("✓ Desktop shortcut created")
    else:
        print("✗ Failed to create desktop shortcut")
    
    print()
    
    # Create Start Menu shortcut
    print("Creating Start Menu shortcut...")
    if create_start_menu_shortcut():
        print("✓ Start Menu shortcut created")
    else:
        print("✗ Failed to create Start Menu shortcut")
    
    print()
    print("Shortcut creation completed!")
    print()
    print("You can now access FVG Scanner from:")
    print("1. Desktop shortcut")
    print("2. Start Menu → FVG Scanner → FVG Scanner Pro")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
