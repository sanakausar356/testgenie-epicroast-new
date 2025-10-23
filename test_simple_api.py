#!/usr/bin/env python3
"""
Simple API test for GroomRoom
"""

import requests
import json

def test_groomroom_api():
    """Test the GroomRoom API"""
    url = "https://backend-production-83c6.up.railway.app/api/groomroom"
    
    # Simple test content
    test_content = """
    As a customer, I want to apply discount codes at checkout so that I can save money on my purchases.
    
    Acceptance Criteria:
    - User can enter discount code in checkout form
    - System validates the code against active promotions
    - Discount is applied to the total order amount
    - User sees confirmation of applied discount
    """
    
    payload = {
        "ticket_content": test_content,
        "level": "actionable"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing GroomRoom API")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"Level: {payload['level']}")
    print()
    
    try:
        print("📡 Making API request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ Success! Response received")
            try:
                data = response.json()
                print("Response structure:")
                print(f"- success: {data.get('success', 'N/A')}")
                if 'data' in data:
                    print(f"- data keys: {list(data['data'].keys())}")
                    if 'groom' in data['data']:
                        groom_content = data['data']['groom']
                        print(f"- groom content length: {len(groom_content)}")
                        print(f"- groom preview: {groom_content[:200]}...")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print("Raw response:")
                print(response.text[:500])
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text[:500])
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_groomroom_api()
