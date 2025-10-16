#!/usr/bin/env python3
"""
Test script for enhanced GroomRoom functionality
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_groomroom():
    """Test the enhanced GroomRoom functionality"""
    print("=== Testing Enhanced GroomRoom ===")
    
    try:
        from groomroom.core import GroomRoom
        from jira_field_mapper import JiraFieldMapper
        
        print("✅ Imports successful")
        
        # Test GroomRoom initialization
        groomroom = GroomRoom()
        print("✅ GroomRoom initialized")
        
        # Test field mapper initialization
        if groomroom.field_mapper:
            print("✅ Field mapper initialized")
            mapping_info = groomroom.field_mapper.get_mapping_info()
            print(f"   Field mappings: {mapping_info['total_fields']} total, {mapping_info['custom_fields']} custom")
        else:
            print("⚠️  Field mapper not available (Jira integration may be disabled)")
        
        # Test enhanced analysis method exists
        if hasattr(groomroom, 'generate_groom_analysis_enhanced'):
            print("✅ Enhanced analysis method available")
        else:
            print("❌ Enhanced analysis method missing")
            return False
        
        # Test run_analysis method exists
        if hasattr(groomroom, 'run_analysis'):
            print("✅ Run analysis method available")
        else:
            print("❌ Run analysis method missing")
            return False
        
        # Test with sample ticket content
        sample_ticket = """
        As a user, I want to reset my password so that I can access my account.
        
        Acceptance Criteria:
        - User can request password reset via email
        - Reset link expires after 24 hours
        - User can set new password after clicking reset link
        
        Test Scenarios:
        - Valid email address should receive reset email
        - Invalid email should show error message
        - Expired reset link should not work
        """
        
        print("\n=== Testing Enhanced Analysis ===")
        result = groomroom.run_analysis(sample_ticket, level="light")
        
        if isinstance(result, dict):
            print("✅ Enhanced analysis returned structured data")
            print(f"   Keys: {list(result.keys())}")
            
            if 'ticket_summary' in result:
                print("✅ Ticket summary present")
            if 'definition_of_ready' in result:
                print("✅ DOR analysis present")
            if 'acceptance_criteria_review' in result:
                print("✅ AC review present")
            if 'test_analysis' in result:
                print("✅ Test analysis present")
            if 'sprint_readiness' in result:
                print("✅ Sprint readiness present")
            if 'next_actions' in result:
                print("✅ Next actions present")
                
            # Print a sample of the results
            if 'sprint_readiness' in result:
                readiness = result['sprint_readiness']
                print(f"   Sprint readiness: {readiness.get('status', 'Unknown')} ({readiness.get('score', 0):.1f}/100)")
            
            if 'definition_of_ready' in result:
                dor = result['definition_of_ready']
                print(f"   DOR coverage: {dor.get('coverage_percentage', 0):.1f}%")
                print(f"   Missing elements: {len(dor.get('missing_elements', []))}")
            
        else:
            print(f"⚠️  Analysis returned: {type(result)} - {str(result)[:100]}...")
        
        print("\n=== Testing Field Mapper ===")
        if groomroom.field_mapper:
            # Test common field lookups
            test_fields = ['Acceptance Criteria', 'Test Scenarios', 'Story Points', 'Agile Team']
            for field_name in test_fields:
                field_id = groomroom.field_mapper.get_field_id(field_name)
                if field_id:
                    print(f"✅ {field_name} -> {field_id}")
                else:
                    print(f"⚠️  {field_name} -> Not found (using fallback)")
        
        print("\n✅ Enhanced GroomRoom test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jira_field_mapper():
    """Test the JiraFieldMapper utility"""
    print("\n=== Testing JiraFieldMapper ===")
    
    try:
        from jira_field_mapper import JiraFieldMapper
        
        # Test standalone field mapper
        mapper = JiraFieldMapper()
        mapper.initialize()
        
        print("✅ Field mapper initialized")
        
        # Test field lookups
        test_fields = ['Acceptance Criteria', 'Test Scenarios', 'Story Points']
        for field_name in test_fields:
            field_id = mapper.get_field_id(field_name)
            print(f"   {field_name} -> {field_id or 'Not found'}")
        
        # Test mapping info
        info = mapper.get_mapping_info()
        print(f"   Total fields: {info['total_fields']}")
        print(f"   Custom fields: {info['custom_fields']}")
        print(f"   Cache exists: {info['cache_exists']}")
        
        print("✅ JiraFieldMapper test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ JiraFieldMapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Enhanced GroomRoom Tests...")
    
    success1 = test_enhanced_groomroom()
    success2 = test_jira_field_mapper()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Enhanced GroomRoom is ready for deployment.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)