#!/usr/bin/env python3
"""
Simple test for GroomRoom functionality without Azure OpenAI
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_groomroom_imports():
    """Test if GroomRoom can be imported and basic methods exist"""
    try:
        from groomroom.core import GroomRoom
        print("✅ GroomRoom import successful")
        
        # Test initialization
        groomroom = GroomRoom()
        print("✅ GroomRoom initialization successful")
        
        # Check if required methods exist
        required_methods = [
            'generate_groom_analysis',
            'generate_groom_analysis_enhanced',
            'generate_updated_groom_analysis',
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
                if prompt and len(prompt) > 100:
                    print(f"✅ Level '{level}' prompt generated ({len(prompt)} chars)")
                else:
                    print(f"❌ Level '{level}' prompt too short or empty")
            except Exception as e:
                print(f"❌ Level '{level}' prompt failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ GroomRoom test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api():
    """Test if backend API can be imported"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app import app
        print("✅ Backend API import successful")
        
        # Check if GroomRoom endpoint exists
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Backend API root endpoint working")
                return True
            else:
                print(f"❌ Backend API root endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== GroomRoom Simple Tests ===")
    
    # Test imports and basic functionality
    groomroom_ok = test_groomroom_imports()
    
    # Test backend API
    backend_ok = test_backend_api()
    
    print("\n=== Test Results ===")
    print(f"GroomRoom Core: {'✅ PASS' if groomroom_ok else '❌ FAIL'}")
    print(f"Backend API: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if groomroom_ok and backend_ok:
        print("\n🎉 All basic tests passed! GroomRoom is ready for configuration.")
        print("\nNext steps:")
        print("1. Set up Azure OpenAI environment variables")
        print("2. Test with actual API calls")
        print("3. Deploy to production")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return groomroom_ok and backend_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
