#!/usr/bin/env python3
"""
Quick Demo Deployment Script for TestGenie & EpicRoast
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"]).decode().strip()
        print(f"✅ Python: {python_version}")
    except:
        print("❌ Python not found. Please install Python 3.13+")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"]).decode().strip()
        print(f"✅ Node.js: {node_version}")
    except:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False
    
    # Check npm
    try:
        npm_version = subprocess.check_output(["npm", "--version"]).decode().strip()
        print(f"✅ npm: {npm_version}")
    except:
        print("❌ npm not found. Please install npm")
        return False
    
    return True

def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API credentials")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install Python dependencies
    try:
        print("Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    
    # Install Node.js dependencies
    try:
        print("Installing Node.js dependencies...")
        frontend_dir = Path("frontend")
        if frontend_dir.exists():
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Node.js dependencies installed")
        else:
            print("❌ Frontend directory not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    
    return True

def verify_setup():
    """Verify the setup is working"""
    print("\n🔍 Verifying setup...")
    
    # Check if .env has required variables
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'AZURE_OPENAI_ENDPOINT' in content and 'AZURE_OPENAI_API_KEY' in content:
                print("✅ Environment variables configured")
            else:
                print("⚠️  Please configure Azure OpenAI credentials in .env file")
    
    # Check if frontend and backend directories exist
    if Path("frontend").exists() and Path("backend").exists():
        print("✅ Project structure verified")
    else:
        print("❌ Project structure incomplete")
        return False
    
    return True

def start_application():
    """Start the application"""
    print("\n🚀 Starting TestGenie & EpicRoast...")
    print("This will start both the Flask backend and React frontend.")
    print("Press Ctrl+C to stop the application.")
    print()
    
    try:
        subprocess.run([sys.executable, "start_web_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main deployment function"""
    print("🎯 TestGenie & EpicRoast - Quick Demo Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install required software.")
        return
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        return
    
    # Verify setup
    if not verify_setup():
        print("\n❌ Setup verification failed.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your Azure OpenAI credentials")
    print("2. (Optional) Add Jira credentials for ticket integration")
    print("3. Run this script again to start the application")
    print("4. Open http://localhost:3000 in your browser")
    
    # Ask if user wants to start the application
    response = input("\n🚀 Start the application now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        start_application()
    else:
        print("\n💡 To start later, run: python start_web_app.py")

if __name__ == "__main__":
    main() 