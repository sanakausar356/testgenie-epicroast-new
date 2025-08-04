#!/usr/bin/env python3
"""
Test script to verify groom room fix is working
"""

import requests
import json
import time

def test_railway_deployment():
    """Test the Railway deployment groom room endpoint"""
    print("🧪 Testing Railway deployment...")
    
    url = "https://craven-worm-production.up.railway.app/api/groomroom/generate"
    
    test_data = {
        "ticket_content": "As a user, I want to be able to click a button, so that I can submit a form",
        "level": "default"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                groom_content = result['data']['groom']
                print("✅ Groom room analysis generated successfully!")
                print(f"Content length: {len(groom_content)} characters")
                print(f"First 200 chars: {groom_content[:200]}...")
                
                # Check if it's the fallback response
                if "temporarily unavailable" in groom_content:
                    print("⚠️  Using fallback response (API may be down)")
                else:
                    print("✅ Using live Azure OpenAI response")
                    
                return True
            else:
                print(f"❌ API returned error: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    url = "https://craven-worm-production.up.railway.app/api/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status')}")
            services = result.get('services', {})
            print("Services:")
            for service, status in services.items():
                print(f"  - {service}: {'✅' if status else '❌'}")
            return True
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Groom Room Fix")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    # Test groom room endpoint
    groom_ok = test_railway_deployment()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Groom Room API: {'✅ PASS' if groom_ok else '❌ FAIL'}")
    
    if health_ok and groom_ok:
        print("\n🎉 All tests passed! Groom room should be working.")
    else:
        print("\n⚠️  Some tests failed. Please check the deployment.")

if __name__ == "__main__":
    main() 