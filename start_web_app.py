#!/usr/bin/env python3
"""
Startup script for TestGenie & EpicRoast Web App
Runs both Flask backend and React frontend
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Run the Flask backend"""
    print("🚀 Starting Flask backend...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return
    
    # Install backend dependencies
    print("📦 Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
    
    # Start Flask app
    print("🔥 Starting Flask server on http://localhost:5000")
    os.chdir(backend_dir)
    subprocess.run([sys.executable, "app.py"])

def run_frontend():
    """Run the React frontend"""
    print("🎨 Starting React frontend...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    os.chdir(frontend_dir)
    subprocess.run(["npm", "install"], check=True)
    
    # Start React dev server
    print("⚛️  Starting React dev server on http://localhost:3000")
    subprocess.run(["npm", "run", "dev"])

def main():
    print("🎯 TestGenie & EpicRoast Web App")
    print("=" * 50)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found!")
        print("   Please make sure you have configured your environment variables.")
        print("   Copy env.example to .env and fill in your credentials.")
        print()
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    run_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 