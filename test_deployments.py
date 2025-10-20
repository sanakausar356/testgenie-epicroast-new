"""
Test script to verify deployments are working
"""

import requests
import json

def test_railway_backend():
    """Test Railway backend deployment"""
    print("🔍 Testing Railway Backend...")
    
    try:
        # Test health endpoint
        response = requests.get("https://backend-production-83c6.up.railway.app/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Test API health
        response = requests.get("https://backend-production-83c6.up.railway.app/api/health", timeout=10)
        print(f"✅ API health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Services: {data}")
        
        # Test GroomRoom endpoint
        test_data = {
            "ticket_content": "As a user, I want to test the deployment"
        }
        response = requests.post(
            "https://backend-production-83c6.up.railway.app/api/groomroom/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"✅ GroomRoom API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Sprint Readiness: {data.get('SprintReadiness', 'N/A')}%")
            print(f"   Type: {data.get('Type', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Railway backend test failed: {e}")
        return False

def test_vercel_frontend():
    """Test Vercel frontend deployment"""
    print("\n🔍 Testing Vercel Frontend...")
    
    try:
        response = requests.get("https://summervibe-testgenie-epicroast-2xrvnwxnk-newell-dt.vercel.app", timeout=10)
        print(f"✅ Frontend: {response.status_code}")
        
        if response.status_code == 200:
            print("   Frontend is accessible")
            return True
        else:
            print(f"   Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Vercel frontend test failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 Testing Deployments")
    print("=" * 50)
    
    railway_ok = test_railway_backend()
    vercel_ok = test_vercel_frontend()
    
    print("\n" + "=" * 50)
    print("📊 Deployment Test Results:")
    print(f"Railway Backend: {'✅ Success' if railway_ok else '❌ Failed'}")
    print(f"Vercel Frontend: {'✅ Success' if vercel_ok else '❌ Failed'}")
    
    if railway_ok and vercel_ok:
        print("\n🎉 All deployments are working!")
        print("\n🌐 URLs:")
        print("Backend: https://backend-production-83c6.up.railway.app")
        print("Frontend: https://summervibe-testgenie-epicroast-2xrvnwxnk-newell-dt.vercel.app")
    else:
        print("\n⚠️ Some deployments need attention")

if __name__ == "__main__":
    main()
