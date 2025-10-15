#!/usr/bin/env python3
"""
Complete deployment script for GroomRoom functionality
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("=== Environment Check ===")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if required files exist
    required_files = [
        'groomroom/core.py',
        'groomroom/cli.py',
        'backend/app.py',
        'frontend/src/components/GroomRoomPanel.tsx',
        'frontend/src/services/api.ts'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def test_groomroom_functionality():
    """Test GroomRoom functionality"""
    print("\n=== GroomRoom Functionality Test ===")
    
    try:
        # Test core functionality
        from groomroom.core import GroomRoom
        groomroom = GroomRoom()
        
        # Test fallback analysis (works without Azure OpenAI)
        sample_ticket = "As a user, I want to reset my password so that I can access my account"
        analysis = groomroom._generate_fallback_analysis(sample_ticket)
        
        if analysis and len(analysis) > 100:
            print("✅ GroomRoom core functionality working")
            return True
        else:
            print("❌ GroomRoom core functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ GroomRoom test failed: {e}")
        return False

def test_backend_api():
    """Test backend API"""
    print("\n=== Backend API Test ===")
    
    try:
        sys.path.append('backend')
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Backend API health check working")
                
                # Test GroomRoom endpoint
                test_data = {
                    'ticket_content': 'As a user, I want to reset my password so that I can access my account',
                    'level': 'updated'
                }
                
                response = client.post('/api/groomroom/generate', 
                                     json=test_data,
                                     content_type='application/json')
                
                if response.status_code == 200:
                    data = response.get_json()
                    if data.get('success'):
                        print("✅ GroomRoom API endpoint working")
                        return True
                    else:
                        print(f"❌ GroomRoom API error: {data.get('error')}")
                        return False
                else:
                    print(f"❌ GroomRoom API failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Backend API health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False

def build_frontend():
    """Build frontend for production"""
    print("\n=== Frontend Build ===")
    
    try:
        frontend_dir = Path('frontend')
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Install dependencies
        print("Installing frontend dependencies...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr}")
            return False
        
        # Build frontend
        print("Building frontend...")
        result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm build failed: {result.stderr}")
            return False
        
        print("✅ Frontend build successful")
        return True
        
    except Exception as e:
        print(f"❌ Frontend build failed: {e}")
        return False
    finally:
        # Change back to root directory
        os.chdir('..')

def create_deployment_summary():
    """Create deployment summary"""
    print("\n=== Deployment Summary ===")
    
    summary = {
        'groomroom_implementation': {
            'core_functionality': '✅ Complete',
            'api_endpoints': '✅ Complete',
            'frontend_integration': '✅ Complete',
            'fallback_mode': '✅ Working (no Azure OpenAI required)',
            'level_support': '✅ 8 levels supported (updated, strict, light, default, insight, deep_dive, actionable, summary)'
        },
        'deployment_status': {
            'backend_ready': '✅ Ready for deployment',
            'frontend_ready': '✅ Ready for deployment',
            'environment_required': 'Azure OpenAI credentials for full functionality'
        },
        'next_steps': [
            'Set up Azure OpenAI environment variables',
            'Deploy backend to Railway/Vercel',
            'Deploy frontend to Vercel',
            'Test with real Jira tickets',
            'Configure Jira integration (optional)'
        ]
    }
    
    # Save summary to file
    with open('GROOMROOM_DEPLOYMENT_SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Deployment summary created: GROOMROOM_DEPLOYMENT_SUMMARY.json")
    
    # Print summary
    print("\n📋 GroomRoom Implementation Summary:")
    print("=" * 50)
    print("✅ Core functionality: Complete")
    print("✅ API endpoints: Complete") 
    print("✅ Frontend integration: Complete")
    print("✅ Fallback mode: Working")
    print("✅ Level support: 8 levels")
    print("\n🚀 Ready for deployment!")
    print("\n📝 Next steps:")
    for step in summary['next_steps']:
        print(f"   • {step}")

def main():
    """Main deployment process"""
    print("=== GroomRoom Complete Deployment ===")
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        return False
    
    # Test functionality
    if not test_groomroom_functionality():
        print("❌ GroomRoom functionality test failed")
        return False
    
    if not test_backend_api():
        print("❌ Backend API test failed")
        return False
    
    # Build frontend
    if not build_frontend():
        print("❌ Frontend build failed")
        return False
    
    # Create deployment summary
    create_deployment_summary()
    
    print("\n🎉 GroomRoom implementation is complete and ready for deployment!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
