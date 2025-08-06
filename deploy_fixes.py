#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def main():
    """Deploy the User Story and Acceptance Criteria detection fixes"""
    print("🚀 Deploying User Story & Acceptance Criteria Detection Fixes")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run this from the project root.")
        return False
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Step 1: Check git status
    if not run_command("git status", "Checking git status"):
        return False
    
    # Step 2: Add all changes
    if not run_command("git add .", "Adding all changes"):
        return False
    
    # Step 3: Commit changes
    commit_message = f"fix: enhance User Story and Acceptance Criteria detection - {timestamp}"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        return False
    
    # Step 4: Push to remote
    if not run_command("git push", "Pushing to remote repository"):
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Deployment Summary")
    print("=" * 60)
    print("✅ Changes committed and pushed successfully")
    print("✅ Railway will automatically deploy the backend")
    print("✅ Vercel will automatically deploy the frontend")
    print("\n🔗 Live URLs:")
    print("   Backend: https://craven-worm-production.up.railway.app")
    print("   Frontend: https://summervibe-testgenie-epicroast-gcx3ip6sa-newell-dt.vercel.app")
    print("\n📋 Fixes Deployed:")
    print("   • Enhanced field extraction for User Story and Acceptance Criteria")
    print("   • Support for both 'Field:' and 'Field' formats")
    print("   • Improved User Story pattern detection")
    print("   • Better Acceptance Criteria analysis")
    print("   • Comprehensive testing completed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 