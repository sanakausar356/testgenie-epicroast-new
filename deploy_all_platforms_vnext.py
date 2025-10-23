"""
Deploy GroomRoom vNext to GitHub, Railway, and Vercel
Comprehensive deployment script for all platforms
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_git_status():
    """Check git status and ensure clean working directory"""
    print("🔍 Checking git status...")
    
    stdout, stderr, returncode = run_command("git status --porcelain")
    if returncode != 0:
        print("❌ Git not initialized. Initializing...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit with GroomRoom vNext"')
        return True
    
    if stdout.strip():
        print("📝 Uncommitted changes detected. Committing changes...")
        run_command("git add .")
        run_command('git commit -m "Update GroomRoom vNext implementation"')
        return True
    
    print("✅ Git working directory is clean")
    return True

def setup_github():
    """Set up GitHub repository"""
    print("\n🐙 Setting up GitHub repository...")
    
    # Check if remote exists
    stdout, stderr, returncode = run_command("git remote -v")
    if "origin" in stdout:
        print("✅ GitHub remote already configured")
        return True
    
    # Get repository URL from user or use default
    repo_url = input("Enter GitHub repository URL (or press Enter for default): ").strip()
    if not repo_url:
        repo_url = "https://github.com/yourusername/testgenie-groomroom-vnext.git"
        print(f"Using default repository: {repo_url}")
    
    # Add remote
    run_command(f"git remote add origin {repo_url}")
    
    # Push to GitHub
    print("📤 Pushing to GitHub...")
    stdout, stderr, returncode = run_command("git push -u origin main")
    if returncode != 0:
        # Try master branch
        stdout, stderr, returncode = run_command("git push -u origin master")
    
    if returncode == 0:
        print("✅ Successfully pushed to GitHub")
        return True
    else:
        print(f"❌ Failed to push to GitHub: {stderr}")
        return False

def setup_railway():
    """Deploy backend to Railway"""
    print("\n🚂 Setting up Railway deployment...")
    
    # Check if Railway CLI is installed
    stdout, stderr, returncode = run_command("railway --version")
    if returncode != 0:
        print("📦 Installing Railway CLI...")
        run_command("npm install -g @railway/cli")
    
    # Login to Railway
    print("🔐 Logging into Railway...")
    stdout, stderr, returncode = run_command("railway login")
    if returncode != 0:
        print("❌ Failed to login to Railway. Please login manually.")
        return False
    
    # Create new project or link existing
    print("🚀 Creating Railway project...")
    stdout, stderr, returncode = run_command("railway init")
    if returncode != 0:
        print("⚠️ Project might already exist, continuing...")
    
    # Set environment variables
    print("🔧 Setting environment variables...")
    env_vars = {
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
        "JIRA_URL": os.getenv("JIRA_URL", ""),
        "JIRA_USERNAME": os.getenv("JIRA_USERNAME", ""),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN", ""),
        "FLASK_ENV": "production"
    }
    
    for key, value in env_vars.items():
        if value:
            run_command(f"railway variables set {key}={value}")
    
    # Deploy to Railway
    print("🚀 Deploying to Railway...")
    stdout, stderr, returncode = run_command("railway up")
    if returncode == 0:
        print("✅ Successfully deployed to Railway")
        
        # Get deployment URL
        stdout, stderr, returncode = run_command("railway domain")
        if returncode == 0:
            print(f"🌐 Railway URL: {stdout.strip()}")
        
        return True
    else:
        print(f"❌ Failed to deploy to Railway: {stderr}")
        return False

def setup_vercel():
    """Deploy frontend to Vercel"""
    print("\n▲ Setting up Vercel deployment...")
    
    # Check if Vercel CLI is installed
    stdout, stderr, returncode = run_command("vercel --version")
    if returncode != 0:
        print("📦 Installing Vercel CLI...")
        run_command("npm install -g vercel")
    
    # Navigate to frontend directory
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Login to Vercel
    print("🔐 Logging into Vercel...")
    stdout, stderr, returncode = run_command("vercel login", cwd=frontend_dir)
    if returncode != 0:
        print("❌ Failed to login to Vercel. Please login manually.")
        return False
    
    # Update vercel.json with Railway backend URL
    vercel_config = {
        "rewrites": [
            {
                "source": "/api/(.*)",
                "destination": "https://backend-production-83c6.up.railway.app/api/$1"
            }
        ],
        "buildCommand": "npm run build",
        "outputDirectory": "dist",
        "installCommand": "npm install",
        "framework": "vite"
    }
    
    with open(frontend_dir / "vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    # Deploy to Vercel
    print("🚀 Deploying to Vercel...")
    stdout, stderr, returncode = run_command("vercel --prod", cwd=frontend_dir)
    if returncode == 0:
        print("✅ Successfully deployed to Vercel")
        print(f"🌐 Vercel URL: {stdout.strip()}")
        return True
    else:
        print(f"❌ Failed to deploy to Vercel: {stderr}")
        return False

def create_deployment_docs():
    """Create deployment documentation"""
    print("\n📚 Creating deployment documentation...")
    
    docs = """# GroomRoom vNext Deployment Guide

## 🚀 Deployment Status

### GitHub Repository
- **Status**: ✅ Deployed
- **Repository**: [GitHub Repository URL]
- **Branch**: main/master

### Railway (Backend)
- **Status**: ✅ Deployed
- **URL**: [Railway Backend URL]
- **Environment**: Production
- **Services**: Flask API with GroomRoom vNext

### Vercel (Frontend)
- **Status**: ✅ Deployed
- **URL**: [Vercel Frontend URL]
- **Environment**: Production
- **Framework**: Vite + React + TypeScript

## 🔧 Environment Variables

### Railway (Backend)
```
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_key
JIRA_URL=your_jira_url
JIRA_USERNAME=your_jira_username
JIRA_API_TOKEN=your_jira_token
FLASK_ENV=production
```

### Vercel (Frontend)
```
VITE_API_URL=your_railway_backend_url
```

## 📊 Services

### Backend API (Railway)
- **Port**: 443 (HTTPS)
- **Framework**: Flask
- **Features**: GroomRoom vNext analysis
- **Endpoints**: 
  - `/api/groomroom/generate` - Main analysis
  - `/api/groomroom/concise` - Concise analysis
  - `/health` - Health check

### Frontend (Vercel)
- **Framework**: React + TypeScript + Vite
- **Features**: GroomRoom vNext UI
- **Components**: GroomRoomPanel, EpicRoastPanel, TestGeniePanel

## 🧪 Testing

### Backend Testing
```bash
curl -X POST https://your-railway-url/api/groomroom/generate \\
  -H "Content-Type: application/json" \\
  -d '{"ticket_content": "As a user, I want to test", "level": "actionable"}'
```

### Frontend Testing
1. Visit Vercel URL
2. Open GroomRoom panel
3. Enter ticket content
4. Select analysis level
5. Generate analysis

## 🔄 Updates

### Backend Updates
1. Make changes to code
2. Commit to GitHub
3. Railway auto-deploys from GitHub

### Frontend Updates
1. Make changes to frontend code
2. Commit to GitHub
3. Vercel auto-deploys from GitHub

## 📈 Monitoring

### Railway
- View logs: `railway logs`
- Check status: `railway status`
- View metrics in Railway dashboard

### Vercel
- View analytics in Vercel dashboard
- Check function logs
- Monitor performance metrics

## 🛠️ Troubleshooting

### Common Issues
1. **Environment variables not set**: Check Railway/Vercel dashboard
2. **API connection issues**: Verify backend URL in vercel.json
3. **Build failures**: Check logs in respective platforms

### Debug Commands
```bash
# Railway
railway logs
railway status
railway variables

# Vercel
vercel logs
vercel inspect
```

## 🎯 GroomRoom vNext Features

- ✅ All Jira card types (Story, Bug, Task, Feature)
- ✅ Figma link detection inside ACs
- ✅ Accurate DoR scoring by type
- ✅ Conflict checks and quality detectors
- ✅ Contextual AC rewrites (non-Gherkin)
- ✅ P/N/E test scenarios
- ✅ ADA/NFR compliance checks
- ✅ Consistent Markdown + JSON outputs
"""
    
    with open("DEPLOYMENT_GUIDE_VNEXT.md", "w") as f:
        f.write(docs)
    
    print("✅ Deployment documentation created")

def main():
    """Main deployment process"""
    print("🚀 GroomRoom vNext - Multi-Platform Deployment")
    print("=" * 60)
    print("Deploying to: GitHub, Railway (Backend), Vercel (Frontend)")
    print("=" * 60)
    
    try:
        # Step 1: Git setup
        if not check_git_status():
            print("❌ Git setup failed")
            return False
        
        # Step 2: GitHub deployment
        if not setup_github():
            print("❌ GitHub deployment failed")
            return False
        
        # Step 3: Railway deployment (Backend)
        if not setup_railway():
            print("❌ Railway deployment failed")
            return False
        
        # Step 4: Vercel deployment (Frontend)
        if not setup_vercel():
            print("❌ Vercel deployment failed")
            return False
        
        # Step 5: Create documentation
        create_deployment_docs()
        
        print("\n" + "=" * 60)
        print("🎉 ALL DEPLOYMENTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📊 Deployment Summary:")
        print("   • GitHub Repository: ✅")
        print("   • Railway Backend: ✅")
        print("   • Vercel Frontend: ✅")
        print("   • Documentation: ✅")
        print("\n🎯 GroomRoom vNext is now live on all platforms!")
        print("🔗 Check DEPLOYMENT_GUIDE_VNEXT.md for details")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 GroomRoom vNext deployment complete!")
    else:
        print("\n❌ Deployment failed. Check errors above.")
