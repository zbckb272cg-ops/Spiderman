#!/usr/bin/env python3
"""
🕷️ Spider App - Telegram Auto Message System Starter
Run this file to start the application
"""

import os
import sys
import subprocess
import platform
import webbrowser
import time

def main():
    print("=" * 60)
    print("🕷️  SPIDER APP - Telegram Auto Message System")
    print("=" * 60)
    print()
    
    # Check if required files exist
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Make sure you're running this script from the Spider App directory.")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required!")
        sys.exit(1)
    
    print("✓ Environment check passed")
    print()
    
    # Install requirements
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
        print("✓ Dependencies installed")
    except Exception as e:
        print(f"⚠️  Warning: Could not install dependencies: {e}")
        print("   Trying to continue anyway...")
    
    print()
    print("🚀 Starting Spider App...")
    print("-" * 60)
    print("📍 App will be available at: http://localhost:5000")
    print("-" * 60)
    print()
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
            print("✓ Browser opened automatically")
        except:
            print("⚠️  Could not open browser automatically")
            print("   Visit http://localhost:5000 manually")
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=False, host='localhost', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n\n⏹️  Spider App stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
