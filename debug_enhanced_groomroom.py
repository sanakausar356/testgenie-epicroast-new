#!/usr/bin/env python3
"""
Debug script for enhanced GroomRoom implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_groomroom_locally():
    """Test the enhanced GroomRoom locally to debug issues"""
    print("🔍 Debugging Enhanced GroomRoom Implementation")
    print("=" * 60)
    
    try:
        from groomroom.core import GroomRoom
        
        # Initialize GroomRoom
        print("1. Initializing GroomRoom...")
        groomroom = GroomRoom()
        print("   ✅ GroomRoom initialized")
        
        # Test ticket data
        test_ticket = {
            'key': 'TEST-123',
            'summary': 'As a customer, I want to apply discount codes during checkout so that I can save money on my purchase',
            'description': 'This feature allows customers to apply discount codes during the checkout process. The system should validate the code, apply the discount, and update the total price accordingly.',
            'acceptance_criteria': [
                'User can enter a discount code in the checkout form',
                'System validates the discount code',
                'Discount is applied to the total price',
                'User sees updated price with discount applied'
            ],
            'issuetype': {'name': 'Story'},
            'status': {'name': 'To Do'},
            'priority': {'name': 'Medium'},
            'assignee': None,
            'reporter': {'displayName': 'Product Owner'},
            'created': '2024-01-15T10:00:00.000+0000',
            'updated': '2024-01-15T10:00:00.000+0000',
            'project': {'name': 'E-commerce Platform'},
            'labels': ['enhancement', 'checkout'],
            'components': [{'name': 'Frontend'}, {'name': 'Backend'}]
        }
        
        print("\n2. Testing enhanced analyze_ticket method...")
        result = groomroom.analyze_ticket(test_ticket, mode="actionable")
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            return False
        
        print("   ✅ Analysis completed")
        
        # Check enhanced output
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
            
            # Show first 500 characters of output
            print(f"\n   📄 Output preview:")
            print(f"   {enhanced_output[:500]}...")
            
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

def test_individual_methods():
    """Test individual enhanced methods"""
    print("\n3. Testing individual enhanced methods...")
    
    try:
        from groomroom.core import GroomRoom
        groomroom = GroomRoom()
        
        # Test enhanced methods exist
        enhanced_methods = [
            'audit_acceptance_criteria_enhanced',
            'generate_comprehensive_test_scenarios', 
            'analyze_frameworks_enhanced',
            'calculate_readiness_enhanced',
            '_generate_role_tagged_recommendations',
            'generate_enhanced_output',
            'apply_length_guardrails'
        ]
        
        for method in enhanced_methods:
            if hasattr(groomroom, method):
                print(f"   ✅ {method} exists")
            else:
                print(f"   ❌ {method} missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing methods: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Enhanced GroomRoom Debug Test")
    print("=" * 60)
    
    # Test individual methods
    methods_ok = test_individual_methods()
    
    # Test full analysis
    analysis_ok = test_enhanced_groomroom_locally()
    
    print(f"\n📊 Debug Results:")
    print(f"Methods available: {'✅' if methods_ok else '❌'}")
    print(f"Analysis working: {'✅' if analysis_ok else '❌'}")
    
    if methods_ok and analysis_ok:
        print("\n🎉 Enhanced GroomRoom is working locally!")
    else:
        print("\n⚠️ Issues found with enhanced GroomRoom implementation")
