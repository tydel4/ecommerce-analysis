#!/usr/bin/env python3
"""
E-Commerce Analytics Dashboard - Startup Script
Simple script to run the web application
"""

import subprocess
import sys
import os
import webbrowser
import time

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'pandas', 'plotly', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ Dependencies installed successfully!")
    else:
        print("✅ All dependencies are installed!")

def run_app():
    """Run the Streamlit web application"""
    print("🚀 Starting E-Commerce Analytics Dashboard...")
    print("="*50)
    
    # Check if streamlit_app.py exists
    if not os.path.exists('streamlit_app.py'):
        print("❌ Error: streamlit_app.py not found!")
        print("Make sure you're in the correct directory.")
        return
    
    # Check dependencies
    check_dependencies()
    
    print("\n📊 Launching dashboard...")
    print("🌐 The app will open in your browser automatically")
    print("🔗 Manual URL: http://localhost:8501")
    print("\n💡 Tips:")
    print("   • Use Ctrl+C to stop the server")
    print("   • The dashboard will auto-reload when you make changes")
    print("   • Check the sidebar for navigation options")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8501')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error running dashboard: {e}")
        print("Try running: streamlit run streamlit_app.py")

if __name__ == "__main__":
    run_app() 