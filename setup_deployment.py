#!/usr/bin/env python3
"""
Setup script for TestGenie & EpicRoast deployment
Helps configure the deployment environment
"""

import os
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt

console = Console()

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
        return result.stdout.strip(), result.stderr.strip(), 0
    except subprocess.CalledProcessError as e:
        return e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else "", e.returncode

def check_git_setup():
    """Check and setup Git configuration"""
    console.print(Panel.fit("🔧 Git Setup", style="blue"))
    
    # Check if git is installed
    stdout, stderr, returncode = run_command("git --version")
    if returncode != 0:
        console.print("❌ Git is not installed. Please install Git first.")
        return False
    
    console.print(f"✅ Git version: {stdout}")
    
    # Check git configuration
    stdout, stderr, returncode = run_command("git config --global user.name")
    if returncode != 0 or not stdout:
        name = Prompt.ask("Enter your Git username")
        run_command(f'git config --global user.name "{name}"')
    
    stdout, stderr, returncode = run_command("git config --global user.email")
    if returncode != 0 or not stdout:
        email = Prompt.ask("Enter your Git email")
        run_command(f'git config --global user.email "{email}"')
    
    console.print("✅ Git configuration complete")
    return True

def check_node_setup():
    """Check and setup Node.js"""
    console.print(Panel.fit("🔧 Node.js Setup", style="green"))
    
    # Check if node is installed
    stdout, stderr, returncode = run_command("node --version")
    if returncode != 0:
        console.print("❌ Node.js is not installed. Please install Node.js first.")
        return False
    
    console.print(f"✅ Node.js version: {stdout}")
    
    # Check if npm is installed
    stdout, stderr, returncode = run_command("npm --version")
    if returncode != 0:
        console.print("❌ npm is not installed. Please install npm first.")
        return False
    
    console.print(f"✅ npm version: {stdout}")
    return True

def setup_railway():
    """Setup Railway CLI"""
    console.print(Panel.fit("🚂 Railway Setup", style="yellow"))
    
    # Check if Railway CLI is installed
    stdout, stderr, returncode = run_command("railway --version")
    if returncode != 0:
        console.print("❌ Railway CLI is not installed.")
        if Confirm.ask("Install Railway CLI?", default=True):
            run_command("npm install -g @railway/cli")
        else:
            return False
    
    console.print(f"✅ Railway CLI version: {stdout}")
    
    # Check if logged in
    stdout, stderr, returncode = run_command("railway whoami")
    if returncode != 0:
        console.print("❌ Not logged into Railway.")
        if Confirm.ask("Login to Railway?", default=True):
            run_command("railway login")
        else:
            return False
    
    console.print("✅ Railway authentication complete")
    return True

def setup_vercel():
    """Setup Vercel CLI"""
    console.print(Panel.fit("⚡ Vercel Setup", style="purple"))
    
    # Check if Vercel CLI is installed
    stdout, stderr, returncode = run_command("vercel --version")
    if returncode != 0:
        console.print("❌ Vercel CLI is not installed.")
        if Confirm.ask("Install Vercel CLI?", default=True):
            run_command("npm install -g vercel")
        else:
            return False
    
    console.print(f"✅ Vercel CLI version: {stdout}")
    
    # Check if logged in
    stdout, stderr, returncode = run_command("vercel whoami")
    if returncode != 0:
        console.print("❌ Not logged into Vercel.")
        if Confirm.ask("Login to Vercel?", default=True):
            run_command("vercel login")
        else:
            return False
    
    console.print("✅ Vercel authentication complete")
    return True

def check_environment_variables():
    """Check and setup environment variables"""
    console.print(Panel.fit("🔑 Environment Variables", style="cyan"))
    
    env_file = ".env"
    if not os.path.exists(env_file):
        console.print("❌ .env file not found.")
        if Confirm.ask("Create .env file from example?", default=True):
            if os.path.exists("env.example"):
                with open("env.example", "r") as f:
                    example_content = f.read()
                with open(env_file, "w") as f:
                    f.write(example_content)
                console.print("✅ Created .env file from example")
                console.print("⚠️ Please edit .env file with your actual API keys")
            else:
                console.print("❌ env.example file not found")
        return False
    
    console.print("✅ .env file exists")
    
    # Check for required variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    with open(env_file, "r") as f:
        env_content = f.read()
    
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=" in env_content and f"{var}=your_" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        console.print(f"⚠️ Missing or unconfigured variables: {', '.join(missing_vars)}")
        console.print("Please edit .env file with your actual API keys")
        return False
    
    console.print("✅ Environment variables configured")
    return True

def check_project_structure():
    """Check project structure"""
    console.print(Panel.fit("📁 Project Structure", style="magenta"))
    
    required_files = [
        "main.py",
        "backend/app.py",
        "frontend/package.json",
        "requirements.txt",
        "railway.toml",
        "Procfile"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        console.print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    console.print("✅ Project structure is complete")
    return True

def main():
    """Main setup function"""
    console.print(Panel.fit("🔧 TestGenie & EpicRoast Deployment Setup", style="bold blue"))
    console.print("This script will help you set up the deployment environment")
    console.print()
    
    setup_results = {}
    
    # Check project structure
    setup_results['project_structure'] = check_project_structure()
    
    # Check Git setup
    setup_results['git'] = check_git_setup()
    
    # Check Node.js setup
    setup_results['node'] = check_node_setup()
    
    # Check environment variables
    setup_results['env_vars'] = check_environment_variables()
    
    # Setup Railway
    setup_results['railway'] = setup_railway()
    
    # Setup Vercel
    setup_results['vercel'] = setup_vercel()
    
    # Summary
    console.print(Panel.fit("📊 Setup Summary", style="bold green"))
    
    summary_table = Table()
    summary_table.add_column("Component", style="cyan")
    summary_table.add_column("Status", style="green")
    
    for component, success in setup_results.items():
        status = "✅ Ready" if success else "❌ Not Ready"
        summary_table.add_row(component.replace('_', ' ').title(), status)
    
    console.print(summary_table)
    
    # Final message
    if all(setup_results.values()):
        console.print(Panel.fit("🎉 Setup complete! You can now run 'python deploy_all_platforms.py'", style="bold green"))
    else:
        failed_components = [comp for comp, success in setup_results.items() if not success]
        console.print(Panel.fit(f"⚠️ Setup incomplete. Please fix: {', '.join(failed_components)}", style="bold yellow"))

if __name__ == "__main__":
    main() 