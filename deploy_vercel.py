#!/usr/bin/env python3
"""
Vercel Deployment Script for Enhanced Groom Room Agent
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Vercel Deployment for Enhanced Groom Room Agent")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check if frontend directory exists
    frontend_dir = os.path.join(current_dir, "frontend")
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found")
        return
    
    print("✅ Frontend directory found")
    
    # Check Vercel CLI
    print("\n🔍 Checking Vercel CLI...")
    vercel_version = run_command("vercel --version")
    if vercel_version:
        print(f"✅ Vercel CLI version: {vercel_version}")
    else:
        print("❌ Vercel CLI not found or not working")
        return
    
    # Check current Vercel project
    print("\n🔍 Checking Vercel project status...")
    vercel_status = run_command("vercel ls")
    if vercel_status:
        print("✅ Vercel project status:")
        print(vercel_status)
    else:
        print("❌ Could not get Vercel project status")
    
    # Build frontend
    print("\n🔨 Building frontend...")
    build_result = run_command("npm run build", cwd=frontend_dir)
    if build_result:
        print("✅ Frontend build successful")
    else:
        print("❌ Frontend build failed")
        return
    
    # Deploy to Vercel
    print("\n🚀 Deploying to Vercel...")
    deploy_result = run_command("vercel --prod", cwd=frontend_dir)
    if deploy_result:
        print("✅ Deployment successful!")
        print("Deployment output:")
        print(deploy_result)
    else:
        print("❌ Deployment failed")
    
    print("\n🎉 Deployment process completed!")

if __name__ == "__main__":
    main() 