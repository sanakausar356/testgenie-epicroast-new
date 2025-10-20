"""
Test the GroomRoom API directly
"""

import requests
import json

def test_groomroom_api():
    """Test the GroomRoom API with a real Jira ticket"""
    
    url = "https://backend-production-83c6.up.railway.app/api/groomroom"
    
    payload = {
        "ticket_number": "ODCD-34544",
        "level": "actionable"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing GroomRoom API")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        print("📡 Making API request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("✅ Success! Response:")
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
            except:
                print("Raw response:")
                print(response.text)
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_groomroom_api()
