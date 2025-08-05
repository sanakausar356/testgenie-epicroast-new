#!/usr/bin/env python3
"""
Test script to verify the enhanced grooming analysis fixes
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_user_story_detection_fix():
    """Test that user story detection works correctly and doesn't generate false negatives"""
    print("🧪 Testing User Story Detection Fix...")
    
    groomroom = GroomRoom()
    
    # Test case 1: User story in description
    test_content_1 = """
Summary: New checkout design
Description: As a customer, I want a streamlined checkout process, so that I can complete my purchase quickly.
Acceptance Criteria:
- Follow design in https://www.figma.com/file/abc123/checkout-design
- Implement one-click checkout
- Show order summary
"""
    
    # Test case 2: User story in acceptance criteria
    test_content_2 = """
Summary: Update user profile
Description: Update the user profile page with new fields
Acceptance Criteria:
- As a user, I want to update my profile information, so that I can keep my details current
- Add new fields for phone and address
- Validate input data
"""
    
    # Test case 3: No user story (should detect as missing)
    test_content_3 = """
Summary: Fix login bug
Description: The login page is not working properly
Acceptance Criteria:
- Fix the login button
- Test with different browsers
- Update error messages
"""
    
    test_cases = [
        ("User story in description", test_content_1),
        ("User story in AC", test_content_2),
        ("No user story", test_content_3)
    ]
    
    for test_name, content in test_cases:
        print(f"\n📋 Testing: {test_name}")
        
        # Run enhanced detection
        user_story_analysis = groomroom.detect_user_story_enhanced(content)
        print(f"  Enhanced Detection: {user_story_analysis['user_story_found']}")
        print(f"  Location: {user_story_analysis['location']}")
        
        # Run DOR analysis with enhanced detection
        dor_analysis = groomroom.analyze_dor_requirements(content, user_story_analysis['user_story_found'])
        user_story_dor = dor_analysis.get('user_story', {})
        print(f"  DOR Coverage: {user_story_dor.get('coverage_percentage', 0):.1f}%")
        print(f"  Missing Elements: {user_story_dor.get('missing_elements', [])}")

def test_figma_link_detection_fix():
    """Test that Figma link detection works correctly and doesn't generate false negatives"""
    print("\n🎨 Testing Figma Link Detection Fix...")
    
    groomroom = GroomRoom()
    
    # Test case 1: Figma link in AC
    test_content_1 = """
Summary: New checkout design
Description: Update the checkout page
Acceptance Criteria:
- Follow design in https://www.figma.com/file/abc123/checkout-design
- Implement one-click checkout
- Show order summary
"""
    
    # Test case 2: Figma link in description
    test_content_2 = """
Summary: Update user profile
Description: Update the user profile page with new fields. Design reference: https://www.figma.com/file/def456/profile-update
Acceptance Criteria:
- Add new fields for phone and address
- Validate input data
"""
    
    # Test case 3: No Figma link
    test_content_3 = """
Summary: Fix login bug
Description: The login page is not working properly
Acceptance Criteria:
- Fix the login button
- Test with different browsers
- Update error messages
"""
    
    test_cases = [
        ("Figma link in AC", test_content_1),
        ("Figma link in description", test_content_2),
        ("No Figma link", test_content_3)
    ]
    
    for test_name, content in test_cases:
        print(f"\n📋 Testing: {test_name}")
        
        # Run enhanced detection
        figma_analysis = groomroom.detect_figma_links_enhanced(content)
        print(f"  Enhanced Detection: {figma_analysis['figma_link_found']}")
        print(f"  Locations: {figma_analysis['locations']}")
        
        # Run stakeholder analysis with enhanced detection
        stakeholder_analysis = groomroom.analyze_stakeholder_validation(content, figma_analysis['figma_link_found'])
        design_validation = stakeholder_analysis.get('design_validation', {})
        print(f"  Design Validation Missing: {design_validation.get('missing', True)}")
        print(f"  Design Validation Found: {design_validation.get('found', False)}")

def test_dod_evaluation_fix():
    """Test that DoD evaluation is only performed for release-ready tickets"""
    print("\n✅ Testing DoD Evaluation Fix...")
    
    groomroom = GroomRoom()
    
    # Test case 1: Release-ready status
    test_content_1 = """
Summary: New checkout design
Status: PROD RELEASE QUEUE
Description: Update the checkout page
Acceptance Criteria:
- Follow design in https://www.figma.com/file/abc123/checkout-design
- Implement one-click checkout
"""
    
    # Test case 2: Grooming status
    test_content_2 = """
Summary: Update user profile
Status: Backlog
Description: Update the user profile page with new fields
Acceptance Criteria:
- Add new fields for phone and address
- Validate input data
"""
    
    # Test case 3: Development status
    test_content_3 = """
Summary: Fix login bug
Status: In Development
Description: The login page is not working properly
Acceptance Criteria:
- Fix the login button
- Test with different browsers
"""
    
    test_cases = [
        ("Release-ready status", test_content_1),
        ("Grooming status", test_content_2),
        ("Development status", test_content_3)
    ]
    
    for test_name, content in test_cases:
        print(f"\n📋 Testing: {test_name}")
        
        # Run DoD evaluation
        dod_evaluation = groomroom.should_evaluate_dod(content)
        print(f"  Should Evaluate DoD: {dod_evaluation['should_evaluate']}")
        print(f"  Reason: {dod_evaluation['reason']}")
        
        # Run DoD analysis only if should evaluate
        if dod_evaluation['should_evaluate']:
            dod_analysis = groomroom.analyze_dod_alignment(content)
            print(f"  DoD Analysis: {len(dod_analysis)} items found")
        else:
            print(f"  DoD Analysis: Skipped (not release-ready)")

def test_duplicate_warnings_fix():
    """Test that duplicate warnings are prevented"""
    print("\n🔄 Testing Duplicate Warnings Fix...")
    
    groomroom = GroomRoom()
    
    # Test case with both user story and Figma link present
    test_content = """
Summary: New checkout design
Description: As a customer, I want a streamlined checkout process, so that I can complete my purchase quickly.
Acceptance Criteria:
- Follow design in https://www.figma.com/file/abc123/checkout-design
- Implement one-click checkout
- Show order summary
Status: PROD RELEASE QUEUE
"""
    
    print("📋 Testing: User story and Figma link present")
    
    # Run enhanced detection
    user_story_analysis = groomroom.detect_user_story_enhanced(test_content)
    figma_analysis = groomroom.detect_figma_links_enhanced(test_content)
    dod_evaluation = groomroom.should_evaluate_dod(test_content)
    
    print(f"  User Story Found: {user_story_analysis['user_story_found']}")
    print(f"  Figma Link Found: {figma_analysis['figma_link_found']}")
    print(f"  DoD Evaluation: {dod_evaluation['should_evaluate']}")
    
    # Run all analyses with enhanced detection
    dor_analysis = groomroom.analyze_dor_requirements(test_content, user_story_analysis['user_story_found'])
    stakeholder_analysis = groomroom.analyze_stakeholder_validation(test_content, figma_analysis['figma_link_found'])
    enhanced_ac_analysis = groomroom.analyze_enhanced_acceptance_criteria(test_content, figma_analysis['figma_link_found'])
    
    # Check for duplicate warnings
    user_story_dor = dor_analysis.get('user_story', {})
    design_validation = stakeholder_analysis.get('design_validation', {})
    
    print(f"  DOR User Story Missing: {len(user_story_dor.get('missing_elements', []))}")
    print(f"  Stakeholder Design Missing: {design_validation.get('missing', True)}")
    print(f"  AC Figma Links: {len(enhanced_ac_analysis.get('figma_links', []))}")
    
    # Verify no false negatives
    if user_story_analysis['user_story_found'] and user_story_dor.get('missing_elements'):
        print("  ❌ ERROR: User story found but still marked as missing in DOR")
    else:
        print("  ✅ User story detection working correctly")
    
    if figma_analysis['figma_link_found'] and design_validation.get('missing', True):
        print("  ❌ ERROR: Figma link found but still marked as missing in stakeholder validation")
    else:
        print("  ✅ Figma link detection working correctly")

def main():
    """Run all tests"""
    print("🔧 Testing Enhanced Grooming Analysis Fixes")
    print("=" * 50)
    
    test_user_story_detection_fix()
    test_figma_link_detection_fix()
    test_dod_evaluation_fix()
    test_duplicate_warnings_fix()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 