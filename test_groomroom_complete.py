#!/usr/bin/env python3
"""
Complete test for GroomRoom functionality
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_groomroom_core():
    """Test GroomRoom core functionality"""
    print("=== Testing GroomRoom Core ===")
    
    try:
        from groomroom.core import GroomRoom
        print("✅ GroomRoom import successful")
        
        # Test initialization
        groomroom = GroomRoom()
        print("✅ GroomRoom initialization successful")
        
        # Test methods exist
        required_methods = [
            'generate_groom_analysis',
            'generate_groom_analysis_enhanced', 
            'generate_updated_groom_analysis',
            'generate_concise_groom_analysis',
            'get_groom_level_prompt'
        ]
        
        for method in required_methods:
            if hasattr(groomroom, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        # Test level prompts
        levels = ['updated', 'strict', 'light', 'default', 'insight', 'deep_dive', 'actionable', 'summary']
        for level in levels:
            try:
                prompt = groomroom.get_groom_level_prompt(level)
                if prompt and len(prompt) > 50:
                    print(f"✅ Level '{level}' prompt generated ({len(prompt)} chars)")
                else:
                    print(f"❌ Level '{level}' prompt too short or empty")
            except Exception as e:
                print(f"❌ Level '{level}' prompt failed: {e}")
        
        # Test fallback analysis (should work without Azure OpenAI)
        sample_ticket = "As a user, I want to reset my password so that I can access my account"
        fallback_analysis = groomroom._generate_fallback_analysis(sample_ticket)
        if fallback_analysis and len(fallback_analysis) > 100:
            print("✅ Fallback analysis working")
        else:
            print("❌ Fallback analysis failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ GroomRoom core test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api():
    """Test backend API functionality"""
    print("\n=== Testing Backend API ===")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app import app
        print("✅ Backend API import successful")
        
        # Test with Flask test client
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                data = response.get_json()
                print("✅ Health endpoint working")
                print(f"   Services status: {data.get('services', {})}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
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
                    print(f"   Response length: {len(data.get('data', {}).get('groom', ''))}")
                else:
                    print(f"❌ GroomRoom API returned error: {data.get('error')}")
                    return False
            else:
                print(f"❌ GroomRoom API failed: {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_integration():
    """Test frontend integration"""
    print("\n=== Testing Frontend Integration ===")
    
    try:
        # Check if frontend files exist
        frontend_files = [
            'frontend/src/components/GroomRoomPanel.tsx',
            'frontend/src/services/api.ts',
            'frontend/package.json'
        ]
        
        for file_path in frontend_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        # Check if GroomRoomPanel has required props
        groomroom_panel = Path('frontend/src/components/GroomRoomPanel.tsx').read_text()
        required_props = ['sharedTicketNumber', 'setSharedTicketNumber', 'setIsLoading']
        
        for prop in required_props:
            if prop in groomroom_panel:
                print(f"✅ GroomRoomPanel has {prop} prop")
            else:
                print(f"❌ GroomRoomPanel missing {prop} prop")
                return False
        
        # Check if API service has generateGroom function
        api_service = Path('frontend/src/services/api.ts').read_text()
        if 'generateGroom' in api_service:
            print("✅ API service has generateGroom function")
        else:
            print("❌ API service missing generateGroom function")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== GroomRoom Complete Test Suite ===")
    
    # Run tests
    core_ok = test_groomroom_core()
    backend_ok = test_backend_api()
    frontend_ok = test_frontend_integration()
    
    print("\n=== Test Results Summary ===")
    print(f"GroomRoom Core: {'✅ PASS' if core_ok else '❌ FAIL'}")
    print(f"Backend API: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Integration: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if core_ok and backend_ok and frontend_ok:
        print("\n🎉 All tests passed! GroomRoom implementation is complete and ready.")
        print("\nNext steps:")
        print("1. Set up Azure OpenAI environment variables for full functionality")
        print("2. Deploy to production")
        print("3. Test with real Jira tickets")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return core_ok and backend_ok and frontend_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
