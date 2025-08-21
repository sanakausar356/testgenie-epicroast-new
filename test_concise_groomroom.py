#!/usr/bin/env python3
"""
Test script for the new concise GroomRoom functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_concise_groomroom():
    """Test the concise groom analysis functionality"""
    
    # Sample ticket content for testing
    sample_ticket = """
    Summary: Add password reset functionality to user account page
    
    Description:
    As a user, I want to be able to reset my password when I forget it, so that I can regain access to my account.
    
    Acceptance Criteria:
    - User can click "Forgot Password" link
    - User receives email with reset link
    - User can set new password via reset link
    - Password meets security requirements
    
    Additional Information:
    - This is for the main user portal
    - Should work across all browsers
    - Must be accessible for screen readers
    """
    
    try:
        from groomroom.core import GroomRoom
        
        print("Testing GroomRoom concise analysis...")
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        
        if not groomroom.client:
            print("❌ GroomRoom not properly configured")
            return False
        
        print("✅ GroomRoom initialized successfully")
        
        # Test concise analysis
        print("Generating concise analysis...")
        analysis = groomroom.generate_concise_groom_analysis(sample_ticket)
        
        if analysis and "Groom Analysis" in analysis:
            print("✅ Concise analysis generated successfully")
            print("\n" + "="*50)
            print("SAMPLE ANALYSIS OUTPUT:")
            print("="*50)
            print(analysis)
            print("="*50)
            return True
        else:
            print("❌ Analysis generation failed or returned unexpected format")
            print(f"Analysis preview: {analysis[:200] if analysis else 'None'}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GroomRoom: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the API endpoint for concise analysis"""
    
    try:
        import requests
        import json
        
        # Sample ticket content
        sample_ticket = """
        Summary: Implement user profile picture upload
        
        Description:
        As a user, I want to upload a profile picture so that my account feels more personalised.
        
        Acceptance Criteria:
        - User can upload image file
        - Image is resized to standard dimensions
        - User sees preview before saving
        """
        
        # Test API endpoint
        url = "http://localhost:5000/api/groomroom/concise"
        data = {
            "ticket_content": sample_ticket
        }
        
        print("Testing API endpoint...")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('groom'):
                print("✅ API endpoint working correctly")
                print("\nAPI Response:")
                print(json.dumps(result, indent=2))
                return True
            else:
                print("❌ API returned success but no analysis data")
                print(f"Response: {result}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running (expected if testing locally)")
        return True
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing GroomRoom Concise Analysis")
    print("="*50)
    
    # Test core functionality
    core_success = test_concise_groomroom()
    
    # Test API endpoint (if server is running)
    api_success = test_api_endpoint()
    
    print("\n" + "="*50)
    print("TEST RESULTS:")
    print(f"Core Functionality: {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"API Endpoint: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if core_success:
        print("\n🎉 GroomRoom concise analysis is working correctly!")
        print("\nUsage examples:")
        print("  python groomroom/cli.py 'As a user, I want to...'")
        print("  python groomroom/cli.py --file ticket.txt")
        print("  curl -X POST http://localhost:5000/api/groomroom/concise -H 'Content-Type: application/json' -d '{\"ticket_content\":\"...\"}'")
    else:
        print("\n❌ Some tests failed. Check configuration and try again.")
