#!/usr/bin/env python3
"""
Test script for enhanced GroomRoom functionality
Tests the new Acceptance Criteria and Test Scenarios parsing capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_enhanced_acceptance_criteria():
    """Test enhanced Acceptance Criteria analysis"""
    print("🧪 Testing Enhanced Acceptance Criteria Analysis...")
    
    groom_room = GroomRoom()
    
    # Test case 1: Good AC with Figma link
    test_content_1 = """
    Summary: Add login modal to homepage
    
    Acceptance Criteria:
    - When a user clicks the login button, then the modal should appear with email and password fields
    - When a user enters valid credentials and clicks submit, then they should be logged in successfully
    - When a user enters invalid credentials, then an error message should be displayed
    - The modal should match the design in https://www.figma.com/file/abc123/Login-Modal-Frame-2
    
    Test Scenarios:
    - Positive: Valid login flow
    - Negative: Invalid credentials, network errors
    - RBT: High-risk authentication scenarios
    - Cross-browser: Test on Chrome, Safari, Firefox
    """
    
    ac_analysis = groom_room.analyze_enhanced_acceptance_criteria(test_content_1)
    
    print(f"✅ AC Present: {ac_analysis['ac_present']}")
    print(f"✅ Overall Quality: {ac_analysis['overall_quality']}")
    print(f"✅ Figma Links Found: {len(ac_analysis['figma_links'])}")
    print(f"✅ Test Scenarios in AC: {ac_analysis['test_scenarios_in_ac']}")
    
    # Test case 2: Vague AC
    test_content_2 = """
    Summary: Fix the bug
    
    Acceptance Criteria:
    - Should match Figma
    - Works like current version
    - Fixes the bug properly
    """
    
    ac_analysis_2 = groom_room.analyze_enhanced_acceptance_criteria(test_content_2)
    
    print(f"\n❌ Vague AC Detected: {len(ac_analysis_2['vague_ac_detected'])}")
    for vague in ac_analysis_2['vague_ac_detected']:
        print(f"  - {vague['issue']}")
    
    return True

def test_enhanced_test_scenarios():
    """Test enhanced Test Scenarios analysis"""
    print("\n🧪 Testing Enhanced Test Scenarios Analysis...")
    
    groom_room = GroomRoom()
    
    # Test case 1: Good test scenarios
    test_content_1 = """
    Summary: Add payment integration
    
    Test Scenarios:
    - Positive: User completes payment successfully with valid card
    - Negative: Payment fails with invalid card, network timeout
    - RBT: High-value transactions, data corruption scenarios
    - Cross-browser: Test payment flow on mobile and desktop browsers
    """
    
    ts_analysis = groom_room.analyze_enhanced_test_scenarios_v2(test_content_1)
    
    print(f"✅ Test Scenarios Field Present: {ts_analysis['test_scenarios_field_present']}")
    print(f"✅ Field Quality: {ts_analysis['field_quality']}")
    print(f"✅ Misuse Detected: {ts_analysis['misuse_detected']}")
    
    # Test case 2: Misused test scenarios field
    test_content_2 = """
    Summary: Update user profile
    
    Test Scenarios:
    TODO: Add test cases
    TBD: Need to determine scope
    """
    
    ts_analysis_2 = groom_room.analyze_enhanced_test_scenarios_v2(test_content_2)
    
    print(f"\n❌ Field Misuse Detected: {ts_analysis_2['misuse_detected']}")
    for misuse in ts_analysis_2['misuse_details']:
        print(f"  - {misuse}")
    
    return True

def test_figma_link_detection():
    """Test Figma link detection and analysis"""
    print("\n🎨 Testing Figma Link Detection...")
    
    groom_room = GroomRoom()
    
    # Test case 1: Figma link with context
    test_content_1 = """
    Acceptance Criteria:
    - When user clicks the button, then the modal should appear as shown in Frame #2 of https://www.figma.com/file/abc123/Design-System
    - The modal should have the same layout and animations as the Figma prototype
    """
    
    ac_analysis = groom_room.analyze_enhanced_acceptance_criteria(test_content_1)
    
    print(f"✅ Figma Links Found: {len(ac_analysis['figma_links'])}")
    for link in ac_analysis['figma_links']:
        print(f"  - URL: {link['url']}")
        print(f"  - Has Context: {link['has_context']}")
        print(f"  - Has Behavioral Expectation: {link['has_behavioral_expectation']}")
        print(f"  - Is Generic: {link['is_generic']}")
        print(f"  - Recommendation: {link['recommendation']}")
    
    # Test case 2: Generic Figma link
    test_content_2 = """
    Acceptance Criteria:
    - Should match https://www.figma.com/file/xyz789/Design
    """
    
    ac_analysis_2 = groom_room.analyze_enhanced_acceptance_criteria(test_content_2)
    
    print(f"\n❌ Generic Figma Link:")
    for link in ac_analysis_2['figma_links']:
        print(f"  - Is Generic: {link['is_generic']}")
        print(f"  - Recommendation: {link['recommendation']}")
    
    return True

def test_separation_logic():
    """Test separation logic between AC and Test Scenarios"""
    print("\n🔄 Testing Separation Logic...")
    
    groom_room = GroomRoom()
    
    # Test case: Test scenarios embedded in AC
    test_content = """
    Summary: Add search functionality
    
    Acceptance Criteria:
    - When user enters search term, then results should appear
    - When user clicks search button, then search should execute
    - Test scenario: Enter valid search term and verify results
    - Test scenario: Enter invalid search term and verify error handling
    - RBT: Test with large datasets
    """
    
    ac_analysis = groom_room.analyze_enhanced_acceptance_criteria(test_content)
    
    print(f"✅ Test Scenarios in AC Detected: {ac_analysis['test_scenarios_in_ac']}")
    if ac_analysis['test_scenarios_in_ac']:
        print("  - Recommendation: Move test scenarios to dedicated field")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced GroomRoom Tests...\n")
    
    try:
        test_enhanced_acceptance_criteria()
        test_enhanced_test_scenarios()
        test_figma_link_detection()
        test_separation_logic()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary of Enhanced Features:")
        print("- Enhanced Acceptance Criteria validation (intent, conditions, expected results, pass/fail logic)")
        print("- Vague AC detection with specific pattern matching")
        print("- Figma link detection and context analysis")
        print("- Enhanced Test Scenarios analysis with NLP patterns")
        print("- Field misuse detection for Test Scenarios")
        print("- Separation logic to detect test scenarios in AC")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 