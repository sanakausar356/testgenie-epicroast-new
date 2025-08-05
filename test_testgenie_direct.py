#!/usr/bin/env python3
"""
Direct test of TestGenie functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_testgenie_direct():
    """Test TestGenie directly without web server"""
    print("🧙‍♂️ Testing TestGenie Directly")
    print("=" * 50)
    
    try:
        from testgenie.core import TestGenie
        
        print("📝 Creating TestGenie instance...")
        testgenie = TestGenie()
        print("✅ TestGenie created successfully")
        
        # Sample acceptance criteria
        sample_criteria = """
        As a user, I want to reset my password via email link so that I can regain access to my account.
        
        Acceptance Criteria:
        - User enters email address on password reset page
        - System validates email format and existence
        - System sends password reset link via email
        - User clicks link and is taken to password reset form
        - User enters new password and confirmation
        - System validates password strength and confirmation match
        - System updates password and logs user in
        """
        
        print("📝 Generating test scenarios...")
        result = testgenie.generate_test_scenarios(sample_criteria, ['positive', 'negative', 'edge'])
        
        if result:
            print("✅ Test scenarios generated successfully!")
            print(f"📊 Result length: {len(result)} characters")
            print("📊 First 300 characters:")
            print(f"   {result[:300]}...")
            
            # Check for expected sections
            expected_sections = ['Test Scenarios', 'Edge Cases', 'Cross Browser']
            for section in expected_sections:
                if section in result:
                    print(f"   ✅ Contains '{section}' section")
                else:
                    print(f"   ❌ Missing '{section}' section")
            
            return True
        else:
            print("❌ No result returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_import():
    """Test if backend can be imported"""
    print("\n🔍 Testing backend import...")
    
    try:
        from backend.app import app, testgenie
        print("✅ Backend app imported successfully")
        
        if testgenie:
            print("✅ TestGenie available in backend")
            return True
        else:
            print("❌ TestGenie not available in backend")
            return False
            
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 TestGenie Direct Test")
    print("=" * 40)
    
    # Test direct functionality
    direct_success = test_testgenie_direct()
    
    # Test backend import
    backend_success = test_backend_import()
    
    if direct_success and backend_success:
        print("\n✅ All tests passed! TestGenie is working correctly.")
        print("📝 The issue might be with the web server or API endpoint.")
    else:
        print("\n❌ Some tests failed!") 