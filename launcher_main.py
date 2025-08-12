#!/usr/bin/env python3
"""
Minecraft Server Manager Launcher (Python equivalent of launch.bat)
================================================================

This script provides the same functionality as launch.bat but in Python,
making it easier to create a standalone executable.
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path


def check_python():
    """Check if Python is available"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 6:
            print(f"✓ Python {version.major}.{version.minor}.{version.micro} is available")
            return True
        else:
            print(f"✗ Python {version.major}.{version.minor} is too old. Need Python 3.6+")
            return False
    except Exception as e:
        print(f"✗ Error checking Python: {e}")
        return False


def check_php():
    """Check if PHP is available"""
    try:
        result = subprocess.run(["php", "-v"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PHP is available")
            return True
        else:
            print("✗ PHP is not available")
            return False
    except FileNotFoundError:
        print("✗ PHP is not installed or not in PATH")
        return False


def launch_gui():
    """Launch the desktop GUI"""
    try:
        print("Launching Desktop GUI...")
        subprocess.run([sys.executable, "mc_server_manager_gui.py"])
    except Exception as e:
        print(f"Error launching GUI: {e}")
        input("Press Enter to continue...")


def launch_python_web():
    """Launch Python web interface"""
    try:
        print("Launching Python Web Interface...")
        # Start web server in background
        process = subprocess.Popen([sys.executable, "web_gui.py"])
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        webbrowser.open("http://localhost:5000")
        
        print("Web interface is running. Close this window to stop the server.")
        input("Press Enter to stop the web server...")
        
        # Terminate the web server
        process.terminate()
        
    except Exception as e:
        print(f"Error launching Python web interface: {e}")
        input("Press Enter to continue...")


def launch_php_web():
    """Launch PHP web interface"""
    if not check_php():
        print("Please install PHP 7.4 or higher")
        input("Press Enter to continue...")
        return
    
    try:
        print("Launching PHP Web Interface...")
        # Start PHP server in background
        process = subprocess.Popen(["php", "-S", "localhost:8000"])
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        webbrowser.open("http://localhost:8000/index.php")
        
        print("PHP web interface is running. Close this window to stop the server.")
        input("Press Enter to stop the PHP server...")
        
        # Terminate the PHP server
        process.terminate()
        
    except Exception as e:
        print(f"Error launching PHP web interface: {e}")
        input("Press Enter to continue...")


def main():
    """Main launcher function"""
    print("Minecraft Server Manager Launcher")
    print("=" * 40)
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Direct launch modes
    if "--gui" in args:
        launch_gui()
        return
    elif "--python" in args or "--web" in args:
        launch_python_web()
        return
    elif "--php" in args:
        launch_php_web()
        return
    
    # Check Python availability
    if not check_python():
        input("Press Enter to exit...")
        return
    
    # Interactive mode - show menu
    while True:
        print("\nChoose launch mode:")
        print("1. Desktop GUI (Recommended)")
        print("2. Python Web Interface")
        print("3. PHP Web Interface")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            launch_gui()
            break
        elif choice == "2":
            launch_python_web()
            break
        elif choice == "3":
            launch_php_web()
            break
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("Press Enter to exit...")
