#!/usr/bin/env python3
"""
Manual Railway deployment script
"""

import os
import subprocess
import sys
from pathlib import Path

def check_railway_cli():
    """Check if Railway CLI is available"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is available")
            return True
        else:
            print("❌ Railway CLI is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI is not installed")
        return False

def install_railway_cli():
    """Try to install Railway CLI"""
    print("🔧 Attempting to install Railway CLI...")
    try:
        # Try npm install
        result = subprocess.run(['npm', 'install', '-g', '@railway/cli'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI installed successfully")
            return True
        else:
            print(f"❌ npm install failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ npm is not available")
        return False

def deploy_to_railway():
    """Deploy to Railway"""
    try:
        print("🚀 Deploying to Railway...")
        
        # Navigate to backend directory
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return False
        
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Try to deploy
        result = subprocess.run(['railway', 'up', '--detach'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Deployment initiated successfully!")
            print("Check Railway dashboard for deployment status")
            return True
        else:
            print("❌ Deployment failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False

def main():
    """Main deployment process"""
    print("=== Manual Railway Deployment ===")
    
    # Check if Railway CLI is available
    if not check_railway_cli():
        print("\n🔧 Railway CLI not found. Attempting to install...")
        if not install_railway_cli():
            print("\n❌ Could not install Railway CLI automatically")
            print("Please install manually:")
            print("1. Install Node.js: https://nodejs.org/")
            print("2. Run: npm install -g @railway/cli")
            print("3. Run: railway login")
            print("4. Run this script again")
            return False
    
    # Try to deploy
    if deploy_to_railway():
        print("\n🎉 Deployment process completed!")
        print("Check your Railway dashboard for deployment status")
        return True
    else:
        print("\n❌ Deployment failed")
        print("Please try manual deployment through Railway dashboard:")
        print("1. Go to https://railway.app/dashboard")
        print("2. Find your project")
        print("3. Click 'Redeploy' or 'Deploy'")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
