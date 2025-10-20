"""
Check Vercel deployment status
"""

import requests
import json

def check_vercel_deployment():
    """Check if Vercel deployment is working"""
    print("🔍 Checking Vercel Deployment...")
    
    vercel_url = "https://summervibe-testgenie-epicroast-2xrvnwxnk-newell-dt.vercel.app"
    
    try:
        # Test the main page
        response = requests.get(vercel_url, timeout=10)
        print(f"✅ Main page: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            
            # Check if it's serving the React app
            if "testgenie" in response.text.lower() or "react" in response.text.lower():
                print("   ✅ React app is loading")
            else:
                print("   ⚠️ React app might not be loading properly")
                
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out - deployment might be building")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - deployment might have failed")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_vercel_api_proxy():
    """Check if API proxy is working"""
    print("\n🔍 Checking API Proxy...")
    
    vercel_url = "https://summervibe-testgenie-epicroast-2xrvnwxnk-newell-dt.vercel.app"
    
    try:
        # Test API proxy
        response = requests.get(f"{vercel_url}/api/health", timeout=10)
        print(f"✅ API proxy: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend connection working: {data}")
            return True
        else:
            print(f"   ❌ API proxy failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API proxy error: {e}")
        return False

def main():
    """Check Vercel deployment status"""
    print("🚀 Vercel Deployment Status Check")
    print("=" * 50)
    
    frontend_ok = check_vercel_deployment()
    api_ok = check_vercel_api_proxy()
    
    print("\n" + "=" * 50)
    print("📊 Vercel Status:")
    print(f"Frontend: {'✅ Working' if frontend_ok else '❌ Failed'}")
    print(f"API Proxy: {'✅ Working' if api_ok else '❌ Failed'}")
    
    if frontend_ok and api_ok:
        print("\n🎉 Vercel deployment is working correctly!")
    elif frontend_ok:
        print("\n⚠️ Frontend works but API proxy has issues")
    else:
        print("\n❌ Vercel deployment has issues")
        print("\nTroubleshooting steps:")
        print("1. Check Vercel dashboard for build logs")
        print("2. Verify build configuration")
        print("3. Check for any build errors")
        print("4. Try redeploying")

if __name__ == "__main__":
    main()
