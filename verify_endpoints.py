"""
Verification script to test both API endpoints
"""

import requests
import json

def test_both_endpoints():
    """Test both /api/groomroom and /api/groomroom/generate endpoints"""
    
    base_url = "https://backend-production-83c6.up.railway.app"
    payload = {
        "ticket_number": "ODCD-34544",
        "level": "actionable"
    }
    headers = {"Content-Type": "application/json"}
    
    print("🧪 Testing Both API Endpoints")
    print("=" * 50)
    
    # Test primary endpoint
    print("1️⃣ Testing /api/groomroom")
    try:
        response = requests.post(f"{base_url}/api/groomroom", json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success')}")
            if data.get('success'):
                groom = data.get('data', {}).get('groom', '')
                print(f"   📋 Groom content length: {len(groom)}")
                if len(groom) > 100:
                    print("   ✅ Formatted output working!")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    
    # Test legacy endpoint
    print("2️⃣ Testing /api/groomroom/generate")
    try:
        response = requests.post(f"{base_url}/api/groomroom/generate", json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success')}")
            if data.get('success'):
                groom = data.get('data', {}).get('groom', '')
                print(f"   📋 Groom content length: {len(groom)}")
                if len(groom) > 100:
                    print("   ✅ Formatted output working!")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    print("🎯 Both endpoints should return 200 OK with formatted output!")

if __name__ == "__main__":
    test_both_endpoints()
