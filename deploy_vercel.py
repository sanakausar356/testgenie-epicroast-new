"""
Deploy to Vercel
"""

import subprocess
import os
from pathlib import Path

def deploy_to_vercel():
    """Deploy frontend to Vercel"""
    print("▲ Deploying to Vercel...")
    
    try:
        # Check if Vercel CLI is installed
        try:
            subprocess.run(["vercel", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Installing Vercel CLI...")
            subprocess.run(["npm", "install", "-g", "vercel"], check=True)
        
        # Navigate to frontend directory
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        # Login to Vercel
        print("🔐 Logging into Vercel...")
        subprocess.run(["vercel", "login"], cwd=frontend_dir, check=True)
        
        # Deploy
        print("🚀 Deploying to Vercel...")
        result = subprocess.run(["vercel", "--prod"], cwd=frontend_dir, capture_output=True, text=True, check=True)
        
        print(f"✅ Successfully deployed to Vercel")
        print(f"🌐 URL: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Vercel deployment failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    deploy_to_vercel()