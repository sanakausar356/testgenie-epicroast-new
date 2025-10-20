"""
Test the frontend API call to see what's happening
"""

import requests
import json

def test_frontend_api_call():
    """Test the exact API call the frontend is making"""
    
    # This is the exact call the frontend makes
    url = "https://backend-production-83c6.up.railway.app/api/groomroom"
    
    payload = {
        "ticket_number": "ODCD-34544",
        "level": "actionable",
        "timestamp": 1737273600000  # Add timestamp like frontend does
    }
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    print("🧪 Testing Frontend API Call")
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
                
                # Check if it's the formatted output
                groom_content = data.get('data', {}).get('groom', '')
                if groom_content and not groom_content.startswith('{'):
                    print("\n" + "="*50)
                    print("📋 FORMATTED GROOM ANALYSIS:")
                    print("="*50)
                    print(groom_content)
                else:
                    print("\n❌ Still getting raw data instead of formatted output")
                    
            except Exception as e:
                print(f"Error parsing JSON: {e}")
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
    test_frontend_api_call()
