#!/usr/bin/env python3
"""
Test the local fixes for enhanced GroomRoom
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_local_fixes():
    """Test the fixes locally"""
    print("🔍 Testing Local Fixes for Enhanced GroomRoom")
    print("=" * 60)
    
    try:
        from groomroom.core import GroomRoom
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        
        # Test ticket data
        test_ticket = {
            'key': 'TEST-123',
            'summary': 'As a customer, I want to apply discount codes during checkout so that I can save money on my purchase',
            'description': 'This feature allows customers to apply discount codes during the checkout process.',
            'acceptance_criteria': [
                'User can enter a discount code',
                'System validates the code',
                'Discount is applied to total price'
            ],
            'issuetype': {'name': 'Story'},
            'status': {'name': 'To Do'},
            'priority': {'name': 'Medium'},
            'assignee': None,
            'reporter': {'displayName': 'Product Owner'},
            'created': '2024-01-15T10:00:00.000+0000',
            'updated': '2024-01-15T10:00:00.000+0000',
            'project': {'name': 'E-commerce Platform'},
            'labels': ['enhancement'],
            'components': [{'name': 'Frontend'}]
        }
        
        print("1. Testing enhanced analyze_ticket method...")
        result = groomroom.analyze_ticket(test_ticket, mode="actionable")
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            return False
        
        print("   ✅ Analysis completed")
        
        # Check if enhanced output exists
        if "enhanced_output" in result:
            enhanced_output = result["enhanced_output"]
            print(f"   📊 Enhanced output length: {len(enhanced_output)} characters")
            
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
                if feature in enhanced_output:
                    found_features.append(feature)
            
            print(f"   🎯 Enhanced features found: {len(found_features)}/{len(enhanced_features)}")
            for feature in found_features:
                print(f"      ✅ {feature}")
            
            missing_features = [f for f in enhanced_features if f not in found_features]
            if missing_features:
                print("   ⚠️ Missing features:")
                for feature in missing_features:
                    print(f"      ❌ {feature}")
            
            # Show first 300 characters of output
            print(f"\n   📄 Output preview:")
            print(f"   {enhanced_output[:300]}...")
            
            return len(found_features) >= 6
        else:
            print("   ❌ No enhanced_output found in result")
            print(f"   📊 Available keys: {list(result.keys())}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_local_fixes()
    if success:
        print("\n🎉 Local fixes are working!")
    else:
        print("\n⚠️ Issues still exist with local implementation")
