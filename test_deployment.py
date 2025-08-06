#!/usr/bin/env python3

import os
import sys

def test_environment():
    """Test the deployment environment"""
    print("🔍 Testing Deployment Environment")
    print("=" * 40)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check if .git exists
    if os.path.exists('.git'):
        print("✅ Git repository found")
    else:
        print("❌ Git repository not found")
    
    # Check if key files exist
    key_files = [
        'groomroom/core.py',
        'main.py',
        'railway.toml',
        'requirements.txt'
    ]
    
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if we can import the fixed modules
    try:
        from groomroom.core import GroomRoom
        print("✅ GroomRoom module imports successfully")
    except Exception as e:
        print(f"❌ GroomRoom module import failed: {e}")
    
    print("\n" + "=" * 40)
    print("Environment test completed")

if __name__ == "__main__":
    test_environment() 