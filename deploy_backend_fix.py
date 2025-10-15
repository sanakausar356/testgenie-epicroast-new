#!/usr/bin/env python3
"""
Backend deployment fix script for GroomRoom functionality
"""

import os
import subprocess
import sys
from pathlib import Path

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
        else:
            print("❌ Railway CLI is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI is not installed")
        print("Please install Railway CLI: npm install -g @railway/cli")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY', 
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your Railway project:")
        print("1. Go to Railway dashboard")
        print("2. Select your project")
        print("3. Go to Variables tab")
        print("4. Add the missing variables")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def deploy_backend():
    """Deploy the backend to Railway"""
    try:
        print("🚀 Deploying backend to Railway...")
        
        # Navigate to backend directory
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return False
        
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Deploy to Railway
        result = subprocess.run(['railway', 'deploy'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend deployed successfully!")
            print("Check Railway dashboard for deployment URL")
            return True
        else:
            print("❌ Backend deployment failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False

def test_backend_health():
    """Test the backend health endpoint"""
    try:
        import requests
        
        # Try to get the Railway URL
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the URL from railway status output
            lines = result.stdout.split('\n')
            url = None
            for line in lines:
                if 'https://' in line and 'railway.app' in line:
                    url = line.strip().split()[-1]
                    break
            
            if url:
                print(f"🔍 Testing backend at: {url}")
                response = requests.get(f"{url}/health", timeout=10)
                
                if response.status_code == 200:
                    print("✅ Backend is healthy!")
                    data = response.json()
                    print(f"Services status: {data.get('services', {})}")
                    return True
                else:
                    print(f"❌ Backend health check failed: {response.status_code}")
                    return False
            else:
                print("❌ Could not determine Railway URL")
                return False
        else:
            print("❌ Could not get Railway status")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def main():
    """Main deployment process"""
    print("=== Backend Deployment Fix ===")
    
    # Check prerequisites
    if not check_railway_cli():
        return False
    
    if not check_environment_variables():
        return False
    
    # Deploy backend
    if not deploy_backend():
        return False
    
    # Test deployment
    print("\n⏳ Waiting for deployment to complete...")
    import time
    time.sleep(30)  # Wait 30 seconds for deployment
    
    if test_backend_health():
        print("\n🎉 Backend deployment successful!")
        print("GroomRoom functionality should now work properly.")
        return True
    else:
        print("\n⚠️  Backend deployment may have issues.")
        print("Check Railway dashboard for more details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
