#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime

def run_command(command):
    """Run a command and return success status"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            return True
        else:
            print(f"❌ Failed: {command}")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Simple deployment by committing and pushing changes"""
    print("🚀 Simple Deployment - Commit and Push Changes")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository")
        return False
    
    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Step 1: Add all changes
    if not run_command("git add ."):
        return False
    
    # Step 2: Commit changes
    commit_msg = f"fix: enhance User Story and Acceptance Criteria detection - {timestamp}"
    if not run_command(f'git commit -m "{commit_msg}"'):
        return False
    
    # Step 3: Push changes
    if not run_command("git push"):
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Deployment Summary")
    print("=" * 50)
    print("✅ Changes committed and pushed successfully")
    print("✅ Railway will automatically deploy the backend")
    print("✅ Vercel will automatically deploy the frontend")
    print("\n🔗 Live URLs:")
    print("   Backend: https://craven-worm-production.up.railway.app")
    print("   Frontend: https://summervibe-testgenie-epicroast-gcx3ip6sa-newell-dt.vercel.app")
    print("\n📋 Fixes Deployed:")
    print("   • Enhanced User Story detection")
    print("   • Enhanced Acceptance Criteria detection")
    print("   • Support for both field formats")
    print("   • Improved analysis quality")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 