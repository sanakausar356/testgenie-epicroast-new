#!/usr/bin/env python3
"""
Debug API response format
"""

import requests
import json

def debug_api_response():
    """Debug the exact API response format"""
    print("🔍 Debugging API response format...")
    
    url = "https://backend-production-83c6.up.railway.app/api/groomroom/generate"
    
    test_data = {
        "ticket_content": "ODCD-12345: As a user, I want to be able to click a button, so that I can submit a form",
        "level": "updated"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print("\n📋 JSON Response Structure:")
                print(json.dumps(json_response, indent=2))
                
                # Check if it has the expected structure
                if isinstance(json_response, dict):
                    print(f"\n🔑 Top-level keys: {list(json_response.keys())}")
                    
                    if 'data' in json_response:
                        print(f"📊 Data keys: {list(json_response['data'].keys()) if isinstance(json_response['data'], dict) else 'Data is not a dict'}")
                    
                    if 'groom' in json_response:
                        print(f"🧹 Groom content length: {len(str(json_response['groom']))}")
                        print(f"🧹 Groom preview: {str(json_response['groom'])[:200]}...")
                        
            except json.JSONDecodeError:
                print("\n⚠️  Response is not valid JSON")
                print("Raw response:")
                print(response.text[:500])
        else:
            print(f"\n❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

if __name__ == "__main__":
    debug_api_response()
