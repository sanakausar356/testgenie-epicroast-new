#!/usr/bin/env python3
"""
Deploy TestGenie Backend to Vercel
"""

import os
import subprocess
import sys
from pathlib import Path
import json

def run_command(command, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {command}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Success: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        result = subprocess.run(
            ["vercel", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not found")
        return False

def install_vercel_cli():
    """Install Vercel CLI"""
    print("Installing Vercel CLI...")
    if run_command("npm install -g vercel"):
        print("✅ Vercel CLI installed successfully")
        return True
    else:
        print("❌ Failed to install Vercel CLI")
        return False

def create_vercel_config():
    """Create Vercel configuration for Python backend"""
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "app.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "app.py"
            }
        ]
    }
    
    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ Created vercel.json configuration")

def deploy_backend():
    """Deploy backend to Vercel"""
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    print("🚀 Deploying backend to Vercel...")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Create Vercel configuration
    create_vercel_config()
    
    # Deploy to Vercel
    if run_command("vercel --prod --yes"):
        print("✅ Backend deployed successfully to Vercel")
        return True
    else:
        print("❌ Failed to deploy backend to Vercel")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting TestGenie Backend Deployment to Vercel")
    
    # Check/install Vercel CLI
    if not check_vercel_cli():
        if not install_vercel_cli():
            print("❌ Failed to install Vercel CLI")
            return False
    
    # Deploy backend
    if deploy_backend():
        print("✅ Backend deployment completed successfully")
        print("🌐 Your backend is now live on Vercel!")
        return True
    else:
        print("❌ Backend deployment failed")
        return False

if __name__ == "__main__":
    main()
