#!/usr/bin/env python3
"""
Setup script for TestGenie project
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print setup banner"""
    print("=" * 50)
    print("🎯 TestGenie Project Setup")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    print(f"Python version: {platform.python_version()}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print("✅ Python version is compatible")
    return True

def install_dependencies():
    """Install project dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    try:
        result = subprocess.run([sys.executable, "test_installation.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Installation test passed")
            return True
        else:
            print("❌ Installation test failed")
            print("Error output:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run installation test: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Installation test failed. Please check your .env file configuration.")
        print("Make sure you have copied env.example to .env and filled in your Azure OpenAI credentials.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nYou can now run TestGenie using:")
    print("- python testgenie.py")
    print("- python -m testgenie.cli")
    print("- testgenie (if installed with pip install -e .)")

if __name__ == "__main__":
    main() 