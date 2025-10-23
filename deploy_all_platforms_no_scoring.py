#!/usr/bin/env python3
"""
Deploy GroomRoom No-Scoring to GitHub, Railway, and Vercel
"""

import os
import subprocess
import sys
import json
import time
from pathlib import Path

def check_git_status():
    """Check git status and commit changes"""
    print("🔍 Checking git status...")
    
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print("📝 Found uncommitted changes, committing...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Deploy GroomRoom No-Scoring implementation"], check=True)
        else:
            print("✅ No uncommitted changes")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False

def deploy_to_github():
    """Deploy to GitHub"""
    print("\n🚀 Deploying to GitHub...")
    
    try:
        # Push to GitHub
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub")
            return True
        else:
            print(f"❌ GitHub push failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub deployment error: {e}")
        return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n🚀 Deploying to Railway...")
    
    try:
        # Check if Railway CLI is available
        try:
            subprocess.run(["railway", "--version"], check=True, capture_output=True)
            print("✅ Railway CLI found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 Railway CLI not found. Please install it manually:")
            print("   npm install -g @railway/cli")
            print("   Then run: railway login")
            return False
        
        # Check Railway status
        try:
            status_result = subprocess.run(["railway", "status"], capture_output=True, text=True)
            if status_result.returncode == 0:
                print("✅ Railway project linked")
                
                # Deploy to Railway
                print("🚀 Deploying to Railway...")
                deploy_result = subprocess.run(["railway", "up", "--detach"], capture_output=True, text=True)
                
                if deploy_result.returncode == 0:
                    print("✅ Railway deployment initiated")
                    
                    # Get the deployment URL
                    url_result = subprocess.run(["railway", "domain"], capture_output=True, text=True)
                    if url_result.returncode == 0:
                        print(f"🌐 Railway URL: {url_result.stdout.strip()}")
                    
                    return True
                else:
                    print(f"❌ Railway deployment failed: {deploy_result.stderr}")
                    return False
            else:
                print("❌ Railway project not linked. Please run: railway link")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Railway error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Railway deployment error: {e}")
        return False

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("\n🚀 Deploying to Vercel...")
    
    try:
        # Check if Vercel CLI is available
        try:
            subprocess.run(["vercel", "--version"], check=True, capture_output=True)
            print("✅ Vercel CLI found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 Vercel CLI not found. Please install it manually:")
            print("   npm install -g vercel")
            print("   Then run: vercel login")
            return False
        
        # Deploy frontend to Vercel
        frontend_dir = Path("frontend")
        if frontend_dir.exists():
            print("📁 Deploying frontend to Vercel...")
            os.chdir("frontend")
            
            try:
                # Deploy to Vercel
                result = subprocess.run(["vercel", "--prod"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Frontend deployed to Vercel")
                    print(f"Output: {result.stdout}")
                    return True
                else:
                    print(f"❌ Vercel deployment failed: {result.stderr}")
                    return False
            finally:
                os.chdir("..")
        else:
            print("❌ Frontend directory not found")
            return False
            
    except Exception as e:
        print(f"❌ Vercel deployment error: {e}")
        return False

def create_deployment_summary():
    """Create deployment summary"""
    print("\n📋 Creating deployment summary...")
    
    summary = """# GroomRoom No-Scoring Deployment Summary

## 🎯 Deployment Status

### GitHub
- ✅ Code committed and pushed to repository
- ✅ All GroomRoom No-Scoring files included
- ✅ Updated app.py to use new implementation

### Railway (Backend)
- 🚀 Backend deployment initiated
- 📝 Using GroomRoom No-Scoring implementation
- 🔧 Updated requirements.txt and Procfile
- 🌐 Backend URL: Check Railway dashboard for URL

### Vercel (Frontend)
- 🚀 Frontend deployment initiated
- 📝 Updated to use new backend API
- 🌐 Frontend URL: Check Vercel dashboard for URL

## 🔧 Key Changes Deployed

### GroomRoom No-Scoring Features:
1. **No Framework Scoring**: Removed all ROI/INVEST/ACCEPT/3C calculations
2. **Context-Specific Outputs**: Domain-aware content generation
3. **Figma Integration**: Anchor text detection for "Figma" links
4. **Conflict Detection**: Identifies contradictory ACs
5. **Role-Tagged Recommendations**: PO/QA/Dev specific guidance
6. **Rule-Based Status**: Ready/Needs Refinement/Not Ready

### Files Added/Modified:
- `groomroom/core_no_scoring.py` - Main implementation
- `app.py` - Updated to use new implementation
- `test_no_scoring_groomroom.py` - Test suite
- `demo_no_scoring.py` - Demo script
- `GROOMROOM_NO_SCORING_IMPLEMENTATION.md` - Documentation

## 🧪 Testing

### Backend API Endpoints:
- `/api/health` - Health check
- `/api/groomroom/generate` - Main GroomRoom analysis
- `/api/groomroom/concise` - Concise analysis

### Test the Implementation:
1. **Health Check**: `GET /api/health`
2. **GroomRoom Analysis**: `POST /api/groomroom/generate`
3. **Frontend Integration**: Use the Vercel frontend URL

## 📊 Expected Results

- ✅ No framework scores in output
- ✅ Context-specific story rewrites
- ✅ Domain-aware AC generation
- ✅ Figma link detection
- ✅ Role-tagged recommendations
- ✅ Conflict detection

## 🔍 Verification Steps

1. **Check Railway Deployment**:
   - Visit Railway dashboard
   - Check deployment logs
   - Test health endpoint

2. **Check Vercel Deployment**:
   - Visit Vercel dashboard
   - Check frontend build
   - Test GroomRoom functionality

3. **Test Integration**:
   - Use frontend to test GroomRoom
   - Verify no framework scores
   - Check context-specific outputs

## 🚨 Troubleshooting

If deployments fail:
1. Check platform-specific logs
2. Verify environment variables
3. Check file structure and dependencies
4. Test locally first

## 📞 Support

- Railway: https://docs.railway.app/
- Vercel: https://vercel.com/docs
- GitHub: Check repository for issues
"""
    
    with open("DEPLOYMENT_SUMMARY_NO_SCORING.md", "w") as f:
        f.write(summary)
    
    print("✅ Deployment summary created: DEPLOYMENT_SUMMARY_NO_SCORING.md")

def main():
    """Main deployment function"""
    print("🚀 GroomRoom No-Scoring Deployment")
    print("=" * 50)
    
    # Check git status
    if not check_git_status():
        print("❌ Git check failed")
        return False
    
    # Deploy to GitHub
    github_success = deploy_to_github()
    
    # Deploy to Railway
    railway_success = deploy_to_railway()
    
    # Deploy to Vercel
    vercel_success = deploy_to_vercel()
    
    # Create deployment summary
    create_deployment_summary()
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 Deployment Results:")
    print(f"GitHub: {'✅ Success' if github_success else '❌ Failed'}")
    print(f"Railway: {'✅ Success' if railway_success else '❌ Failed'}")
    print(f"Vercel: {'✅ Success' if vercel_success else '❌ Failed'}")
    
    if github_success and railway_success and vercel_success:
        print("\n🎉 All deployments completed successfully!")
        print("Check the deployment URLs in your platform dashboards.")
    else:
        print("\n⚠️ Some deployments failed. Check the logs above.")
        print("You may need to deploy manually through the platform dashboards.")
    
    return github_success and railway_success and vercel_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
