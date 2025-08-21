#!/usr/bin/env python3
"""
Deploy TestGenie - Complete Deployment Script
Deploys both frontend (Vercel) and backend (Railway)
"""

import os
import subprocess
import sys
import time
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

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    # Check Python
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python: {result.stdout.strip()}")
        else:
            print("❌ Python not found")
            return False
    except FileNotFoundError:
        print("❌ Python not found")
        return False
    
    return True

def install_cli_tools():
    """Install required CLI tools"""
    print("📦 Installing CLI tools...")
    
    # Install Vercel CLI
    print("Installing Vercel CLI...")
    if not run_command("npm install -g vercel"):
        print("❌ Failed to install Vercel CLI")
        return False
    
    # Install Railway CLI
    print("Installing Railway CLI...")
    if not run_command("npm install -g @railway/cli"):
        print("❌ Failed to install Railway CLI")
        return False
    
    print("✅ All CLI tools installed successfully")
    return True

def deploy_backend():
    """Deploy backend to Railway"""
    print("🚀 Deploying backend to Railway...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Change to backend directory
    original_dir = os.getcwd()
    os.chdir(backend_dir)
    
    try:
        # Check if railway.toml exists
        if not Path("railway.toml").exists():
            print("Creating railway.toml...")
            railway_config = """[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
"""
            with open("railway.toml", "w") as f:
                f.write(railway_config)
        
        # Deploy to Railway
        if run_command("railway up --detach"):
            print("✅ Backend deployed successfully to Railway")
            
            # Wait a moment for deployment to complete
            time.sleep(5)
            
            # Get the Railway URL
            print("Getting Railway deployment URL...")
            status_result = run_command("railway status")
            if status_result:
                print("Railway deployment status:")
                print(status_result)
            
            return True
        else:
            print("❌ Failed to deploy backend to Railway")
            return False
    
    finally:
        # Return to original directory
        os.chdir(original_dir)

def deploy_frontend():
    """Deploy frontend to Vercel"""
    print("🚀 Deploying frontend to Vercel...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Change to frontend directory
    original_dir = os.getcwd()
    os.chdir(frontend_dir)
    
    try:
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
    
    finally:
        # Return to original directory
        os.chdir(original_dir)

def update_api_url():
    """Update the API URL in vercel.json with the new Railway URL"""
    print("🔧 Updating API URL in vercel.json...")
    
    # Get Railway URL
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
        try:
            status_result = run_command("railway status")
            if status_result:
                # Extract URL from status (this is a simplified approach)
                # In practice, you'd need to parse the output more carefully
                print("Please manually update the API URL in frontend/vercel.json")
                print("with your Railway deployment URL")
        finally:
            os.chdir("..")

def main():
    """Main deployment function"""
    print("🚀 Starting TestGenie Complete Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please install Node.js, npm, and Python")
        sys.exit(1)
    
    # Install CLI tools
    if not install_cli_tools():
        print("❌ Failed to install CLI tools")
        sys.exit(1)
    
    # Deploy backend first
    print("\n" + "=" * 50)
    if not deploy_backend():
        print("❌ Backend deployment failed")
        sys.exit(1)
    
    # Deploy frontend
    print("\n" + "=" * 50)
    if not deploy_frontend():
        print("❌ Frontend deployment failed")
        sys.exit(1)
    
    # Update API URL
    print("\n" + "=" * 50)
    update_api_url()
    
    print("\n🎉 Deployment completed successfully!")
    print("\nNext steps:")
    print("1. ✅ Backend deployed on Railway")
    print("2. ✅ Frontend deployed on Vercel")
    print("3. 🔧 Update API URL in frontend/vercel.json with your Railway URL")
    print("4. 🔧 Set environment variables in Railway dashboard:")
    print("   - AZURE_OPENAI_ENDPOINT")
    print("   - AZURE_OPENAI_API_KEY")
    print("   - AZURE_OPENAI_DEPLOYMENT_NAME")
    print("   - JIRA_SERVER_URL")
    print("   - JIRA_EMAIL")
    print("   - JIRA_API_TOKEN")
    print("\nYour application should now be live!")

if __name__ == "__main__":
    main()
