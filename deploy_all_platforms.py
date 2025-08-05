#!/usr/bin/env python3
"""
Comprehensive Deployment Script for TestGenie & EpicRoast
Deploys to Railway (Backend), GitHub (Code), and Vercel (Frontend)
"""

import os
import subprocess
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

console = Console()

def run_command(command, cwd=None, capture_output=True, check=True):
    """Run a command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd,
                capture_output=True, 
                text=True, 
                check=check
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        else:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd,
                check=check
            )
            return "", "", result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else "", e.returncode

def check_prerequisites():
    """Check if all required tools are installed"""
    console.print(Panel.fit("🔍 Checking Prerequisites", style="blue"))
    
    tools = {
        "git": "git --version",
        "node": "node --version",
        "npm": "npm --version",
        "railway": "railway --version",
        "vercel": "vercel --version"
    }
    
    missing_tools = []
    
    for tool, command in tools.items():
        stdout, stderr, returncode = run_command(command, check=False)
        if returncode == 0:
            console.print(f"✅ {tool}: {stdout}")
        else:
            console.print(f"❌ {tool}: Not found")
            missing_tools.append(tool)
    
    if missing_tools:
        console.print(f"\n❌ Missing tools: {', '.join(missing_tools)}")
        console.print("Please install the missing tools before proceeding.")
        return False
    
    return True

def deploy_to_github():
    """Deploy code to GitHub"""
    console.print(Panel.fit("🚀 Deploying to GitHub", style="green"))
    
    # Check git status
    stdout, stderr, returncode = run_command("git status --porcelain")
    if stdout:
        console.print("📝 Changes detected, committing...")
        
        # Add all changes
        stdout, stderr, returncode = run_command("git add .")
        if returncode != 0:
            console.print(f"❌ Failed to add changes: {stderr}")
            return False
        
        # Commit changes
        commit_message = f"feat: update deployment - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        stdout, stderr, returncode = run_command(f'git commit -m "{commit_message}"')
        if returncode != 0:
            console.print(f"❌ Failed to commit changes: {stderr}")
            return False
        
        console.print("✅ Changes committed")
    else:
        console.print("✅ No changes to commit")
    
    # Push to remote
    console.print("📤 Pushing to remote repository...")
    stdout, stderr, returncode = run_command("git push")
    if returncode != 0:
        console.print(f"❌ Failed to push to remote: {stderr}")
        return False
    
    console.print("✅ Successfully pushed to GitHub")
    return True

def deploy_to_railway():
    """Deploy backend to Railway"""
    console.print(Panel.fit("🚂 Deploying Backend to Railway", style="yellow"))
    
    # Check if Railway CLI is logged in
    stdout, stderr, returncode = run_command("railway whoami", check=False)
    if returncode != 0:
        console.print("❌ Not logged into Railway. Please run 'railway login' first.")
        return False
    
    console.print("✅ Railway CLI authenticated")
    
    # Check if project is linked
    stdout, stderr, returncode = run_command("railway status", check=False)
    if returncode != 0:
        console.print("🔗 Linking to Railway project...")
        stdout, stderr, returncode = run_command("railway link")
        if returncode != 0:
            console.print(f"❌ Failed to link Railway project: {stderr}")
            return False
    
    console.print("✅ Railway project linked")
    
    # Deploy to Railway
    console.print("🚀 Deploying to Railway...")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Deploying...", total=None)
        
        stdout, stderr, returncode = run_command("railway up", capture_output=False)
        
        if returncode != 0:
            console.print(f"❌ Railway deployment failed")
            return False
    
    console.print("✅ Successfully deployed to Railway")
    
    # Get deployment URL
    stdout, stderr, returncode = run_command("railway domain")
    if returncode == 0 and stdout:
        console.print(f"🌐 Railway URL: {stdout.strip()}")
    
    return True

def deploy_to_vercel():
    """Deploy frontend to Vercel"""
    console.print(Panel.fit("⚡ Deploying Frontend to Vercel", style="purple"))
    
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        console.print(f"❌ Frontend directory '{frontend_dir}' not found")
        return False
    
    # Check if Vercel CLI is logged in
    stdout, stderr, returncode = run_command("vercel whoami", check=False)
    if returncode != 0:
        console.print("❌ Not logged into Vercel. Please run 'vercel login' first.")
        return False
    
    console.print("✅ Vercel CLI authenticated")
    
    # Install frontend dependencies
    console.print("📦 Installing frontend dependencies...")
    stdout, stderr, returncode = run_command("npm install", cwd=frontend_dir)
    if returncode != 0:
        console.print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    console.print("✅ Dependencies installed")
    
    # Build frontend
    console.print("🔨 Building frontend...")
    stdout, stderr, returncode = run_command("npm run build", cwd=frontend_dir)
    if returncode != 0:
        console.print(f"❌ Frontend build failed: {stderr}")
        return False
    
    console.print("✅ Frontend built successfully")
    
    # Deploy to Vercel
    console.print("🚀 Deploying to Vercel...")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Deploying...", total=None)
        
        stdout, stderr, returncode = run_command("vercel --prod", cwd=frontend_dir, capture_output=False)
        
        if returncode != 0:
            console.print(f"❌ Vercel deployment failed")
            return False
    
    console.print("✅ Successfully deployed to Vercel")
    
    # Get deployment URL
    stdout, stderr, returncode = run_command("vercel ls", cwd=frontend_dir)
    if returncode == 0 and stdout:
        # Parse the output to find the production URL
        lines = stdout.split('\n')
        for line in lines:
            if 'Production' in line and 'https://' in line:
                url = line.split()[-1]
                console.print(f"🌐 Vercel URL: {url}")
                break
    
    return True

def verify_deployments():
    """Verify that deployments are working"""
    console.print(Panel.fit("🔍 Verifying Deployments", style="cyan"))
    
    # Get Railway URL
    stdout, stderr, returncode = run_command("railway domain")
    railway_url = stdout.strip() if returncode == 0 else None
    
    if railway_url:
        console.print(f"🔍 Checking Railway backend at {railway_url}")
        
        # Test health endpoint
        import requests
        try:
            response = requests.get(f"{railway_url}/health", timeout=10)
            if response.status_code == 200:
                console.print("✅ Railway backend is healthy")
            else:
                console.print(f"⚠️ Railway backend returned status {response.status_code}")
        except Exception as e:
            console.print(f"❌ Railway backend health check failed: {e}")
    
    # Get Vercel URL
    stdout, stderr, returncode = run_command("vercel ls", cwd="frontend")
    vercel_url = None
    if returncode == 0 and stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'Production' in line and 'https://' in line:
                vercel_url = line.split()[-1]
                break
    
    if vercel_url:
        console.print(f"🔍 Checking Vercel frontend at {vercel_url}")
        
        # Test frontend
        import requests
        try:
            response = requests.get(vercel_url, timeout=10)
            if response.status_code == 200:
                console.print("✅ Vercel frontend is accessible")
            else:
                console.print(f"⚠️ Vercel frontend returned status {response.status_code}")
        except Exception as e:
            console.print(f"❌ Vercel frontend check failed: {e}")

def main():
    """Main deployment function"""
    console.print(Panel.fit("🚀 TestGenie & EpicRoast Deployment", style="bold blue"))
    console.print("Deploying to Railway (Backend), GitHub (Code), and Vercel (Frontend)")
    console.print()
    
    # Check prerequisites
    if not check_prerequisites():
        return
    
    # Ask user which platforms to deploy to
    console.print("Select deployment targets:")
    deploy_github = Confirm.ask("Deploy to GitHub?", default=True)
    deploy_railway = Confirm.ask("Deploy to Railway (Backend)?", default=True)
    deploy_vercel = Confirm.ask("Deploy to Vercel (Frontend)?", default=True)
    
    if not any([deploy_github, deploy_railway, deploy_vercel]):
        console.print("❌ No deployment targets selected")
        return
    
    # Track deployment results
    results = {}
    
    # Deploy to GitHub
    if deploy_github:
        results['github'] = deploy_to_github()
    
    # Deploy to Railway
    if deploy_railway:
        results['railway'] = deploy_to_railway()
    
    # Deploy to Vercel
    if deploy_vercel:
        results['vercel'] = deploy_to_vercel()
    
    # Summary
    console.print(Panel.fit("📊 Deployment Summary", style="bold green"))
    
    summary_table = Table()
    summary_table.add_column("Platform", style="cyan")
    summary_table.add_column("Status", style="green")
    
    for platform, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        summary_table.add_row(platform.title(), status)
    
    console.print(summary_table)
    
    # Verify deployments if any were successful
    if any(results.values()):
        if Confirm.ask("Verify deployments?", default=True):
            verify_deployments()
    
    # Final message
    if all(results.values()):
        console.print(Panel.fit("🎉 All deployments completed successfully!", style="bold green"))
    else:
        failed_platforms = [platform for platform, success in results.items() if not success]
        console.print(Panel.fit(f"⚠️ Some deployments failed: {', '.join(failed_platforms)}", style="bold yellow"))

if __name__ == "__main__":
    main() 