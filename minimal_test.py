#!/usr/bin/env python3
"""
Minimal test for enhanced GroomRoom
"""

def test_enhanced_features():
    """Test the enhanced GroomRoom features"""
    print("🧪 Testing Enhanced GroomRoom Features")
    print("=" * 50)
    
    try:
        # Test import
        from groomroom.core import GroomRoom
        print("✅ Import successful")
        
        # Test initialization
        groomroom = GroomRoom()
        print("✅ Initialization successful")
        
        # Test enhanced methods exist
        enhanced_methods = [
            'audit_acceptance_criteria_enhanced',
            'generate_comprehensive_test_scenarios', 
            'analyze_frameworks_enhanced',
            'calculate_readiness_enhanced',
            '_generate_role_tagged_recommendations',
            'generate_enhanced_output',
            'analyze_batch_tickets',
            'apply_length_guardrails'
        ]
        
        for method in enhanced_methods:
            if hasattr(groomroom, method):
                print(f"✅ {method} exists")
            else:
                print(f"❌ {method} missing")
                return False
        
        print("\n🎉 All enhanced features are present!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_features()
    if success:
        print("\n✅ Enhanced GroomRoom is ready!")
    else:
        print("\n❌ Enhanced GroomRoom has issues")
        exit(1)