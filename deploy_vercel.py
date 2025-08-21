#!/usr/bin/env python3
"""
Deploy TestGenie to Vercel
"""

import os
import subprocess
import sys
from pathlib import Path

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

def deploy_frontend():
    """Deploy frontend to Vercel"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print("🚀 Deploying frontend to Vercel...")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Install dependencies
    if not run_command("npm install"):
        print("❌ Failed to install frontend dependencies")
        return False
    
    # Build the project
    if not run_command("npm run build"):
        print("❌ Failed to build frontend")
        return False
    
    # Deploy to Vercel
    if run_command("vercel --prod --yes"):
        print("✅ Frontend deployed successfully to Vercel")
        return True
    else:
        print("❌ Failed to deploy frontend to Vercel")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting TestGenie Vercel Deployment")
    
    # Check if Vercel CLI is installed
    if not check_vercel_cli():
        if not install_vercel_cli():
            print("❌ Cannot proceed without Vercel CLI")
            sys.exit(1)
    
    # Deploy frontend
    if deploy_frontend():
        print("🎉 Deployment completed successfully!")
        print("\nNext steps:")
        print("1. Your frontend is now deployed on Vercel")
        print("2. The backend should be deployed separately (Railway/Render/Heroku)")
        print("3. Update the API URL in vercel.json if needed")
    else:
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 