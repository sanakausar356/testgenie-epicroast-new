#!/usr/bin/env python3
"""
Deploy Enhanced GroomRoom to all platforms
"""

import os
import subprocess
import sys
import time
from datetime import datetime

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=False
        )
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def deploy_to_github():
    """Deploy code to GitHub"""
    print("\n🚀 Deploying to GitHub")
    print("=" * 50)
    
    # Check git status
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        print(f"❌ Failed to check git status: {stderr}")
        return False
    
    if stdout.strip():
        print("📝 Changes detected, committing...")
        
        # Add all changes
        success, stdout, stderr = run_command("git add .")
        if not success:
            print(f"❌ Failed to add changes: {stderr}")
            return False
        
        # Commit changes
        commit_message = f"feat: enhanced GroomRoom with Markdown + JSON output - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
        if not success:
            print(f"❌ Failed to commit changes: {stderr}")
            return False
        
        print("✅ Changes committed")
    else:
        print("✅ No changes to commit")
    
    # Push to remote
    print("📤 Pushing to remote repository...")
    success, stdout, stderr = run_command("git push")
    if not success:
        print(f"❌ Failed to push to remote: {stderr}")
        return False
    
    print("✅ Successfully pushed to GitHub")
    return True

def deploy_to_railway():
    """Deploy backend to Railway"""
    print("\n🚂 Deploying Backend to Railway")
    print("=" * 50)
    
    # Check if Railway CLI is available
    success, stdout, stderr = run_command("railway --version")
    if not success:
        print("❌ Railway CLI not found. Please install it first:")
        print("npm install -g @railway/cli")
        return False
    
    # Check if logged in
    success, stdout, stderr = run_command("railway whoami")
    if not success:
        print("❌ Not logged into Railway. Please run 'railway login' first.")
        return False
    
    print("✅ Railway CLI authenticated")
    
    # Deploy to Railway
    print("🚀 Deploying to Railway...")
    success, stdout, stderr = run_command("railway up")
    if not success:
        print(f"❌ Railway deployment failed: {stderr}")
        return False
    
    print("✅ Successfully deployed to Railway")
    
    # Get deployment URL
    success, stdout, stderr = run_command("railway domain")
    if success and stdout.strip():
        print(f"🌐 Railway URL: {stdout.strip()}")
    
    return True

def deploy_to_vercel():
    """Deploy frontend to Vercel"""
    print("\n⚡ Deploying Frontend to Vercel")
    print("=" * 50)
    
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory '{frontend_dir}' not found")
        return False
    
    # Check if Vercel CLI is available
    success, stdout, stderr = run_command("vercel --version")
    if not success:
        print("❌ Vercel CLI not found. Please install it first:")
        print("npm install -g vercel")
        return False
    
    # Check if logged in
    success, stdout, stderr = run_command("vercel whoami")
    if not success:
        print("❌ Not logged into Vercel. Please run 'vercel login' first.")
        return False
    
    print("✅ Vercel CLI authenticated")
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Dependencies installed")
    
    # Build frontend
    print("🔨 Building frontend...")
    success, stdout, stderr = run_command("npm run build", cwd=frontend_dir)
    if not success:
        print(f"❌ Frontend build failed: {stderr}")
        return False
    
    print("✅ Frontend built successfully")
    
    # Deploy to Vercel
    print("🚀 Deploying to Vercel...")
    success, stdout, stderr = run_command("vercel --prod", cwd=frontend_dir)
    if not success:
        print(f"❌ Vercel deployment failed: {stderr}")
        return False
    
    print("✅ Successfully deployed to Vercel")
    
    # Get deployment URL
    success, stdout, stderr = run_command("vercel ls", cwd=frontend_dir)
    if success and stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'Production' in line and 'https://' in line:
                url = line.split()[-1]
                print(f"🌐 Vercel URL: {url}")
                break
    
    return True

def main():
    """Main deployment function"""
    print("🚀 Enhanced GroomRoom Deployment")
    print("Deploying to GitHub, Railway, and Vercel")
    print("=" * 60)
    
    # Track deployment results
    results = {}
    
    # Deploy to GitHub
    print("\n1. Deploying to GitHub...")
    results['github'] = deploy_to_github()
    
    # Deploy to Railway
    print("\n2. Deploying to Railway...")
    results['railway'] = deploy_to_railway()
    
    # Deploy to Vercel
    print("\n3. Deploying to Vercel...")
    results['vercel'] = deploy_to_vercel()
    
    # Summary
    print("\n📊 Deployment Summary")
    print("=" * 30)
    
    for platform, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{platform.title()}: {status}")
    
    # Final message
    if all(results.values()):
        print("\n🎉 All deployments completed successfully!")
        print("\nEnhanced GroomRoom is now live with:")
        print("- Rich Markdown reports")
        print("- JSON data tabs")
        print("- Improved UI readability")
        print("- UK spelling throughout")
        print("- Comprehensive analysis framework")
    else:
        failed_platforms = [platform for platform, success in results.items() if not success]
        print(f"\n⚠️ Some deployments failed: {', '.join(failed_platforms)}")
        print("Please check the error messages above and retry.")

if __name__ == "__main__":
    main()
