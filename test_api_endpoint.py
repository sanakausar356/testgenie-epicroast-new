#!/usr/bin/env python3
"""
Test the TestGenie API endpoint directly
"""

import requests
import json

def test_testgenie_api():
    """Test the TestGenie API endpoint"""
    print("🧙‍♂️ Testing TestGenie API Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "acceptance_criteria": """
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
    }
    
    try:
        # Test the API endpoint
        print("📡 Making API call to /api/testgenie/generate...")
        response = requests.post(
            'http://localhost:5000/api/testgenie/generate',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📊 Response structure: {list(result.keys())}")
            
            if result.get('success'):
                data = result.get('data', {})
                scenarios = data.get('scenarios', '')
                
                if scenarios:
                    print("✅ Test scenarios received!")
                    print(f"📊 Scenarios length: {len(scenarios)} characters")
                    print("📊 First 200 characters:")
                    print(f"   {scenarios[:200]}...")
                    
                    # Check for expected sections
                    expected_sections = ['Test Scenarios', 'Edge Cases', 'Cross Browser']
                    for section in expected_sections:
                        if section in scenarios:
                            print(f"   ✅ Contains '{section}' section")
                        else:
                            print(f"   ❌ Missing '{section}' section")
                else:
                    print("❌ No scenarios in response data")
                    print(f"📊 Data content: {data}")
            else:
                print("❌ API returned success=false")
                print(f"📊 Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📊 Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   Make sure the backend server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🔍 Testing health endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health endpoint working")
            print(f"📊 Services status: {result.get('services', {})}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to health endpoint")
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

if __name__ == '__main__':
    test_health_endpoint()
    test_testgenie_api() 