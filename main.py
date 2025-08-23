#!/usr/bin/env python3
"""
Graduation Scanner - Main Entry Point
An intelligent QR/Barcode Scanner for Graduation Ceremonies
Using InsightFace buffalo_l model for face recognition
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import GraduationScannerApp


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'cv2',
        'numpy',
        'insightface',
        'qrcode',
        'pyzbar',
        'PIL',
        'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'tkinter':
                __import__('tkinter')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Error: Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main application entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Graduation Scanner - Face Recognition System for Ceremonies'
    )
    
    parser.add_argument(
        '--mode',
        choices=['low_cpu', 'balanced', 'high_performance'],
        default='balanced',
        help='Performance mode (default: balanced)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    args = parser.parse_args()
    
    # Show version if requested
    if args.version:
        from config import Config
        print(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        return
    
    # Enable debug mode if requested
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Debug mode enabled")
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("Dependencies OK")
    
    # Start application
    try:
        print(f"Starting Graduation Scanner in {args.mode} mode...")
        app = GraduationScannerApp(performance_mode=args.mode)
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"\nApplication error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()