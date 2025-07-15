#!/usr/bin/env python3
"""
Quick launch script for FVG Scanner
"""
import subprocess
import sys
import os

def main():
    """Quick launch with common options"""
    print("FVG Scanner Quick Launch")
    print("=" * 40)
    print("1. Run single scan (AAPL, MSFT, GOOGL, TSLA)")
    print("2. Run continuous scanner")
    print("3. Test alerts")
    print("4. Custom symbols")
    print("5. Exit")
    print()
    
    choice = input("Choose option (1-5): ").strip()
    
    if choice == "1":
        cmd = ["main.py", "--single-scan", "--symbols", "AAPL,MSFT,GOOGL,TSLA"]
    elif choice == "2":
        cmd = ["main.py"]
    elif choice == "3":
        cmd = ["main.py", "--test-alerts"]
    elif choice == "4":
        symbols = input("Enter symbols (comma-separated): ").strip()
        cmd = ["main.py", "--single-scan", "--symbols", symbols]
    elif choice == "5":
        print("Exiting...")
        return
    else:
        print("Invalid choice!")
        return
    
    try:
        # Use sys.executable to ensure we use the current Python interpreter
        cmd = [sys.executable] + cmd
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running scanner: {e}")
    except KeyboardInterrupt:
        print("\nScan interrupted by user")

if __name__ == "__main__":
    main()
