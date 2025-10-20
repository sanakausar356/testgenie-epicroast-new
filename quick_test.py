"""
Quick test of the GroomRoom API
"""

import requests
import json

def quick_test():
    url = "https://backend-production-83c6.up.railway.app/api/groomroom"
    payload = {"ticket_number": "ODCD-34544", "level": "actionable"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ API Working!")
            print(f"Success: {data.get('success')}")
            if data.get('success'):
                groom = data.get('data', {}).get('groom', '')
                print(f"Groom content length: {len(groom)}")
                if groom and len(groom) > 100:
                    print("✅ Formatted output working!")
                else:
                    print("❌ Still getting raw data")
            else:
                print(f"Error: {data.get('error')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    quick_test()
