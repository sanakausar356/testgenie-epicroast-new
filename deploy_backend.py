#!/usr/bin/env python3
"""
Deploy TestGenie Backend to Railway
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

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(
            ["railway", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("Installing Railway CLI...")
    if run_command("npm install -g @railway/cli"):
        print("✅ Railway CLI installed successfully")
        return True
    else:
        print("❌ Failed to install Railway CLI")
        return False

def deploy_backend():
    """Deploy backend to Railway"""
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    print("🚀 Deploying backend to Railway...")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check if railway.toml exists, if not create it
    railway_toml = Path("railway.toml")
    if not railway_toml.exists():
        print("Creating railway.toml configuration...")
        railway_config = """[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
"""
        with open(railway_toml, "w") as f:
            f.write(railway_config)
        print("✅ Created railway.toml")
    
    # Deploy to Railway
    if run_command("railway up --detach"):
        print("✅ Backend deployed successfully to Railway")
        return True
    else:
        print("❌ Failed to deploy backend to Railway")
        return False

def get_railway_url():
    """Get the Railway deployment URL"""
    try:
        result = subprocess.run(
            ["railway", "status"],
            capture_output=True,
            text=True,
            cwd="backend"
        )
        if result.returncode == 0:
            print("Railway status:")
            print(result.stdout)
            return True
        else:
            print("❌ Could not get Railway status")
            return False
    except Exception as e:
        print(f"❌ Error getting Railway status: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting TestGenie Backend Deployment")
    
    # Check if Railway CLI is installed
    if not check_railway_cli():
        if not install_railway_cli():
            print("❌ Cannot proceed without Railway CLI")
            sys.exit(1)
    
    # Deploy backend
    if deploy_backend():
        print("🎉 Backend deployment completed successfully!")
        print("\nNext steps:")
        print("1. Your backend is now deployed on Railway")
        print("2. Get the deployment URL with: railway status")
        print("3. Update the API URL in frontend/vercel.json")
        print("4. Set environment variables in Railway dashboard")
        
        # Try to get the Railway URL
        get_railway_url()
    else:
        print("❌ Backend deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
