#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Tests the configuration before deployment
"""

import os
import sys
import subprocess
import importlib.util

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_python_import(module_name, description):
    """Check if a Python module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            print(f"✅ {description}: {module_name}")
            return True
        else:
            print(f"❌ {description}: {module_name} - NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ {description}: {module_name} - ERROR: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking Environment Variables:")
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY', 
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    optional_vars = [
        'OPENAI_API_KEY',
        'JIRA_SERVER_URL',
        'JIRA_EMAIL',
        'JIRA_API_TOKEN',
        'PORT'
    ]
    
    all_good = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ Required: {var}")
        else:
            print(f"❌ Required: {var} - NOT SET")
            all_good = False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ Optional: {var}")
        else:
            print(f"⚠️  Optional: {var} - NOT SET")
    
    return all_good

def test_backend_import():
    """Test if backend can be imported"""
    print("\n🔍 Testing Backend Import:")
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Try to import the app
        from app import app
        print("✅ Backend app imported successfully")
        
        # Test if app is a Flask app
        if hasattr(app, 'route'):
            print("✅ Flask app object is valid")
            return True
        else:
            print("❌ App object is not a valid Flask app")
            return False
            
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def test_requirements():
    """Test if all requirements can be imported"""
    print("\n🔍 Testing Requirements:")
    
    requirements = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('dotenv', 'python-dotenv'),
        ('requests', 'requests'),
        ('openai', 'openai'),
        ('gunicorn', 'gunicorn')
    ]
    
    all_good = True
    
    for module, name in requirements:
        if check_python_import(module, name):
            continue
        else:
            all_good = False
    
    return all_good

def main():
    """Main verification function"""
    print("🚀 Railway Deployment Verification")
    print("=" * 50)
    
    # Check file structure
    print("\n🔍 Checking File Structure:")
    files_to_check = [
        ('railway.toml', 'Railway configuration'),
        ('nixpacks.toml', 'Nixpacks configuration'),
        ('Procfile', 'Procfile'),
        ('requirements.txt', 'Root requirements.txt'),
        ('backend/requirements.txt', 'Backend requirements.txt'),
        ('backend/app.py', 'Backend Flask app'),
        ('runtime.txt', 'Python runtime specification')
    ]
    
    file_checks = []
    for filepath, description in files_to_check:
        file_checks.append(check_file_exists(filepath, description))
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Test requirements
    req_ok = test_requirements()
    
    # Test backend import
    backend_ok = test_backend_import()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if all(file_checks) and req_ok and backend_ok:
        print("✅ All checks passed! Ready for Railway deployment.")
        if not env_ok:
            print("⚠️  Warning: Some required environment variables are not set.")
            print("   Make sure to set them in Railway dashboard before deployment.")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)