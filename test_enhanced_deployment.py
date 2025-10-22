#!/usr/bin/env python3
"""
Test script to verify enhanced GroomRoom deployment
"""

import requests
import json
import time

def test_railway_backend():
    """Test Railway backend deployment"""
    print("🚀 Testing Railway Backend Deployment")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get('https://backend-production-83c6.up.railway.app/health', timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
        else:
            print("   ❌ Health endpoint failed")
            return False
        
        # Test enhanced GroomRoom API
        print("\n2. Testing enhanced GroomRoom API...")
        test_data = {
            "ticket_content": "As a customer, I want to apply discount codes during checkout so that I can save money on my purchase",
            "level": "actionable",
            "figma_link": "https://figma.com/example"
        }
        
        response = requests.post(
            'https://backend-production-83c6.up.railway.app/api/groomroom/generate',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                groom_content = result.get('data', {}).get('groom', '')
                print("   ✅ Enhanced GroomRoom API working")
                print(f"   📊 Response length: {len(groom_content)} characters")
                
                # Check for enhanced features
                enhanced_features = [
                    "⚡ Actionable Groom Report",
                    "📋 Definition of Ready",
                    "🧭 Framework Scores",
                    "🧩 User Story Review",
                    "✅ Acceptance Criteria",
                    "🧪 Test Scenarios",
                    "🧱 Technical / ADA",
                    "💡 Role-Tagged Recommendations"
                ]
                
                found_features = []
                for feature in enhanced_features:
                    if feature in groom_content:
                        found_features.append(feature)
                
                print(f"   🎯 Enhanced features found: {len(found_features)}/{len(enhanced_features)}")
                for feature in found_features:
                    print(f"      ✅ {feature}")
                
                missing_features = [f for f in enhanced_features if f not in found_features]
                if missing_features:
                    print("   ⚠️ Missing features:")
                    for feature in missing_features:
                        print(f"      ❌ {feature}")
                
                return len(found_features) >= 6  # At least 6 features should be present
            else:
                print(f"   ❌ API returned error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Railway backend: {e}")
        return False

def test_vercel_frontend():
    """Test Vercel frontend deployment"""
    print("\n🌐 Testing Vercel Frontend Deployment")
    print("=" * 50)
    
    try:
        # Test main frontend URL
        print("1. Testing frontend availability...")
        response = requests.get('https://summervibe-testgenie-epicroast-2xrvnwxnk-newell-dt.vercel.app', timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            return True
        else:
            print("   ❌ Frontend not accessible")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Vercel frontend: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🧪 Enhanced GroomRoom Deployment Test")
    print("=" * 60)
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test Railway backend
    railway_success = test_railway_backend()
    
    # Test Vercel frontend
    vercel_success = test_vercel_frontend()
    
    # Summary
    print("\n📊 Deployment Test Summary")
    print("=" * 50)
    print(f"Railway Backend: {'✅ SUCCESS' if railway_success else '❌ FAILED'}")
    print(f"Vercel Frontend: {'✅ SUCCESS' if vercel_success else '❌ FAILED'}")
    
    if railway_success and vercel_success:
        print("\n🎉 All deployments successful!")
        print("✅ Enhanced GroomRoom 04-mini style is live and working!")
        return True
    else:
        print("\n⚠️ Some deployments need attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
