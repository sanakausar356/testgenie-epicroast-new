#!/usr/bin/env python3
"""
Test full API response to see if content is truncated
"""

import requests
import json

def test_full_response():
    """Test the full API response"""
    print("🔍 Testing full API response...")
    
    url = "https://backend-production-83c6.up.railway.app/api/groomroom/generate"
    
    test_data = {
        "ticket_content": "ODCD-12345: As a user, I want to be able to click a button, so that I can submit a form. This should work across all browsers and devices. Acceptance Criteria: 1. Button should be visible 2. Button should be clickable 3. Form should submit when clicked 4. Should work on mobile and desktop",
        "level": "updated"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            json_response = response.json()
            
            if json_response.get('success'):
                groom_content = json_response.get('data', {}).get('groom', '')
                print(f"\n✅ Success!")
                print(f"Groom content length: {len(groom_content)} characters")
                print(f"Level: {json_response.get('data', {}).get('level', 'N/A')}")
                print(f"Ticket number: {json_response.get('data', {}).get('ticket_number', 'N/A')}")
                
                print(f"\n📋 Full Groom Analysis:")
                print("=" * 80)
                print(groom_content)
                print("=" * 80)
                
                # Check if it looks truncated
                if len(groom_content) < 100:
                    print("\n⚠️  WARNING: Groom content seems very short, might be truncated")
                elif "..." in groom_content[-50:]:
                    print("\n⚠️  WARNING: Groom content might be truncated (ends with ...)")
                else:
                    print("\n✅ Groom content appears complete")
                    
            else:
                print(f"\n❌ API returned error: {json_response.get('error', 'Unknown error')}")
        else:
            print(f"\n❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

if __name__ == "__main__":
    test_full_response()
