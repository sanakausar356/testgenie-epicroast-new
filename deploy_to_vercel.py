#!/usr/bin/env python3
"""
Deploy frontend to Vercel
"""

import os
import subprocess
import sys
from pathlib import Path

def deploy_to_vercel():
    """Deploy the frontend to Vercel"""
    print("🚀 Deploying frontend to Vercel...")
    
    # Change to frontend directory
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Build the project
        print("🔨 Building project...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        
        # Check if Vercel CLI is installed
        try:
            subprocess.run(["vercel", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 Installing Vercel CLI...")
            subprocess.run(["npm", "install", "-g", "vercel"], check=True)
        
        # Deploy to Vercel
        print("🚀 Deploying to Vercel...")
        result = subprocess.run(["vercel", "--prod", "--yes"], cwd=frontend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend deployed to Vercel successfully!")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Vercel deployment failed: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during deployment: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = deploy_to_vercel()
    if success:
        print("\n🎉 Frontend deployment completed!")
        print("Your frontend should now be available at the Vercel URL")
    else:
        print("\n❌ Frontend deployment failed")
        sys.exit(1)
