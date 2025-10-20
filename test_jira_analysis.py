#!/usr/bin/env python3
"""
Test Jira ticket analysis with GroomRoom
"""

import requests
import json

def test_jira_analysis():
    """Test GroomRoom analysis with a Jira ticket"""
    print("🧪 Testing Jira ticket analysis...")
    
    url = "https://backend-production-83c6.up.railway.app/api/groomroom/generate"
    
    # Test with a sample Jira ticket
    test_data = {
        "ticket_content": "ODCD-12345: As a user, I want to be able to click a button, so that I can submit a form. This should work across all browsers and devices.",
        "level": "updated"
    }
    
    try:
        print(f"📤 Sending request to: {url}")
        print(f"📋 Test data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📏 Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS - Full Response:")
            print("=" * 80)
            print(response.text)
            print("=" * 80)
            
            # Try to parse as JSON
            try:
                json_response = response.json()
                print(f"\n📋 JSON Keys: {list(json_response.keys()) if isinstance(json_response, dict) else 'Not a dict'}")
            except:
                print("\n⚠️  Response is not valid JSON")
        else:
            print(f"\n❌ ERROR - Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

if __name__ == "__main__":
    test_jira_analysis()
