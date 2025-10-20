"""
Test the GroomRoom API with sample content instead of Jira ticket
"""

import requests
import json

def test_groomroom_api_with_content():
    """Test the GroomRoom API with sample ticket content"""
    
    url = "https://backend-production-83c6.up.railway.app/api/groomroom"
    
    # Sample ticket content
    sample_content = """
    As a customer, I want to apply discount codes at checkout so that I can save money on my purchases.
    
    Acceptance Criteria:
    - User can enter discount code in checkout form
    - System validates the code against active promotions
    - Discount is applied to the total order amount
    - User sees confirmation of applied discount
    
    Test Scenarios:
    - Valid code applies correct discount
    - Invalid code shows error message
    - Expired code shows appropriate message
    """
    
    payload = {
        "ticket_content": sample_content,
        "level": "actionable"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing GroomRoom API with Sample Content")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Level: {payload['level']}")
    print(f"Content: {sample_content[:100]}...")
    print()
    
    try:
        print("📡 Making API request...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ Success! Response:")
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
                
                # Extract the groom analysis
                groom_content = data.get('data', {}).get('groom', '')
                print("\n" + "="*60)
                print("📋 GROOM ANALYSIS OUTPUT:")
                print("="*60)
                print(groom_content)
                
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
    test_groomroom_api_with_content()
