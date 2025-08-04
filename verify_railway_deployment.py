#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Run this locally to verify your setup before deploying to Railway
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version should be 3.11+")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'dotenv',
        'requests',
        'openai',
        'rich',
        'prompt_toolkit'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All dependencies are available")
        return True

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    # Load from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  .env file not found")
    
    # Check for required variables (OpenAI or Azure OpenAI)
    required_vars = []
    optional_vars = ['JIRA_SERVER_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
    
    # Check for either OpenAI or Azure OpenAI configuration
    openai_key = os.getenv('OPENAI_API_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    if openai_key:
        print(f"✅ OPENAI_API_KEY")
    elif azure_endpoint and azure_key:
        print(f"✅ AZURE_OPENAI_ENDPOINT")
        print(f"✅ AZURE_OPENAI_API_KEY")
    else:
        print(f"❌ OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT+AZURE_OPENAI_API_KEY - Missing")
        required_vars.append('OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT+AZURE_OPENAI_API_KEY')
    
    missing_required = []
    for var in required_vars:
        missing_required.append(var)
    
    print("\nOptional variables:")
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} - Not set (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required variables: {', '.join(missing_required)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_file_structure():
    """Check if all required files exist"""
    print("\n🔍 Checking file structure...")
    
    required_files = [
        'main.py',
        'backend/app.py',
        'requirements.txt',
        'backend/requirements.txt',
        'railway.toml',
        'Procfile'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_imports():
    """Test if the main application can be imported"""
    print("\n🔍 Testing imports...")
    
    try:
        # Test backend import
        sys.path.append('.')
        from backend.app import app
        print("✅ Backend app imported successfully")
        
        # Test core modules
        from testgenie.core import TestGenie
        print("✅ TestGenie core imported successfully")
        
        from epicroast.core import EpicRoast
        print("✅ EpicRoast core imported successfully")
        
        from groomroom.core import GroomRoom
        print("✅ GroomRoom core imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_flask_app():
    """Test if Flask app can start"""
    print("\n🔍 Testing Flask app...")
    
    try:
        from backend.app import app
        
        # Test if app has required routes
        routes = ['/', '/health', '/api/health']
        for route in routes:
            with app.test_client() as client:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✅ Route {route} works")
                else:
                    print(f"❌ Route {route} returned {response.status_code}")
                    return False
        
        print("✅ Flask app test passed")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🚀 Railway Deployment Verification")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_environment_variables,
        check_file_structure,
        test_imports,
        test_flask_app
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Verification Results")
    print("=" * 50)
    
    if all(results):
        print("🎉 All checks passed! Your setup is ready for Railway deployment.")
        print("\nNext steps:")
        print("1. Commit your changes to git")
        print("2. Push to your Railway-connected repository")
        print("3. Check Railway dashboard for deployment status")
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Create .env file with required variables")
        print("- Check file paths and permissions")

if __name__ == "__main__":
    main() 