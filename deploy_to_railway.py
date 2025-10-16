#!/usr/bin/env python3
"""
Deploy backend to Railway
"""

import os
import subprocess
import sys
from pathlib import Path

def deploy_to_railway():
    """Deploy the backend to Railway"""
    print("🚀 Deploying backend to Railway...")
    
    try:
        # Check if Railway CLI is installed
        try:
            subprocess.run(["railway", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 Installing Railway CLI...")
            # Install Railway CLI
            if os.name == 'nt':  # Windows
                subprocess.run(["powershell", "-Command", "iwr -useb https://railway.app/install.ps1 | iex"], check=True)
            else:  # Unix-like
                subprocess.run(["curl", "-fsSL", "https://railway.app/install.sh"], check=True)
        
        # Login to Railway (this will open browser)
        print("🔐 Logging into Railway...")
        print("Please complete the login in your browser...")
        subprocess.run(["railway", "login"], check=True)
        
        # Link to existing project or create new one
        print("🔗 Linking to Railway project...")
        try:
            subprocess.run(["railway", "link"], check=True)
        except subprocess.CalledProcessError:
            print("Creating new Railway project...")
            subprocess.run(["railway", "init"], check=True)
        
        # Deploy to Railway
        print("🚀 Deploying to Railway...")
        result = subprocess.run(["railway", "up"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend deployed to Railway successfully!")
            print(f"Output: {result.stdout}")
            
            # Get the deployment URL
            url_result = subprocess.run(["railway", "domain"], capture_output=True, text=True)
            if url_result.returncode == 0:
                print(f"🌐 Your backend is available at: {url_result.stdout.strip()}")
            
            return True
        else:
            print(f"❌ Railway deployment failed: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during deployment: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = deploy_to_railway()
    if success:
        print("\n🎉 Backend deployment completed!")
        print("Your backend should now be available at the Railway URL")
    else:
        print("\n❌ Backend deployment failed")
        sys.exit(1)
