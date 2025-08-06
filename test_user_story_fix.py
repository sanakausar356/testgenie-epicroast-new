#!/usr/bin/env python3
"""
Test script to verify the user story detection fix
Tests the new centralized user story detection helper method
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
    
    # Test case: User story in description (like ODCD-33741)
    test_content = """
Summary: Add payment method to checkout
Description: As a customer, I want to add a new payment method during checkout, so that I can complete my purchase.
Acceptance Criteria:
- User can add credit card
- User can add PayPal
- Payment method is saved for future use
"""
    
    print("\n📋 Test Case: User Story in Description")
    print("=" * 50)
    
    # Test the new centralized helper method
    description = "As a customer, I want to add a new payment method during checkout, so that I can complete my purchase."
    ac = "User can add credit card\nUser can add PayPal\nPayment method is saved for future use"
    
    result = groomroom.has_user_story(description, ac)
    print(f"✅ has_user_story() result: {result}")
    
    # Test the enhanced detection method
    enhanced_result = groomroom.detect_user_story_enhanced(test_content)
    print(f"✅ detect_user_story_enhanced() result: {enhanced_result['user_story_found']}")
    print(f"   Location: {enhanced_result['location']}")
    print(f"   Confidence: {enhanced_result['confidence']}")
    print(f"   Debug info: {enhanced_result['debug_info']}")
    
    # Test the analysis context creation
    context = groomroom.create_analysis_context(test_content)
    print(f"✅ create_analysis_context() user_story_found: {context['user_story_found']}")
    
    # Test framework analysis with user story flag
    framework_analysis = groomroom.analyze_frameworks(test_content, context['user_story_found'])
    user_story_framework = framework_analysis.get('user_story_template', {})
    print(f"✅ Framework Analysis - User Story Template:")
    print(f"   Coverage: {user_story_framework.get('coverage_percentage', 0):.1f}%")
    print(f"   Missing elements: {user_story_framework.get('missing_elements', [])}")
    
    # Test DOR analysis with user story flag
    dor_analysis = groomroom.analyze_dor_requirements(test_content, context['user_story_found'])
    user_story_dor = dor_analysis.get('user_story', {})
    print(f"✅ DOR Analysis - User Story:")
    print(f"   Coverage: {user_story_dor.get('coverage_percentage', 0):.1f}%")
    print(f"   Missing elements: {user_story_dor.get('missing_elements', [])}")
    
    # Test sprint readiness analysis with user story flag
    sprint_analysis = groomroom.analyze_sprint_readiness(test_content, context['user_story_found'])
    print(f"✅ Sprint Readiness Analysis:")
    print(f"   Missing for sprint: {sprint_analysis.get('missing_for_sprint', [])}")
    print(f"   Recommendations: {sprint_analysis.get('recommendations', [])}")
    
    # Test framework summary creation
    framework_summary = groomroom._create_framework_summary(framework_analysis, context['user_story_found'])
    print(f"✅ Framework Summary:")
    print(framework_summary)
    
    # Test DOR summary creation
    dor_summary = groomroom._create_dor_summary(dor_analysis, context['user_story_found'])
    print(f"✅ DOR Summary:")
    print(dor_summary)
    
    # Test sprint readiness summary creation
    sprint_summary = groomroom._create_sprint_readiness_summary(sprint_analysis)
    print(f"✅ Sprint Readiness Summary:")
    print(sprint_summary)
    
    print("\n" + "=" * 50)
    print("🎯 Expected Results:")
    print("- User story should be detected as FOUND")
    print("- Framework coverage should be 100% (not 0%)")
    print("- DOR coverage should be 100% (not missing)")
    print("- Sprint readiness should NOT mention 'User story is missing'")
    print("- All summaries should NOT mention missing user story")
    
    # Verify the results
    success = True
    if not result:
        print("❌ has_user_story() failed to detect user story")
        success = False
    
    if not enhanced_result['user_story_found']:
        print("❌ detect_user_story_enhanced() failed to detect user story")
        success = False
    
    if not context['user_story_found']:
        print("❌ create_analysis_context() failed to detect user story")
        success = False
    
    if user_story_framework.get('coverage_percentage', 0) < 100:
        print("❌ Framework analysis still shows missing user story")
        success = False
    
    if user_story_dor.get('coverage_percentage', 0) < 100:
        print("❌ DOR analysis still shows missing user story")
        success = False
    
    if 'User story is missing' in sprint_analysis.get('missing_for_sprint', []):
        print("❌ Sprint readiness still mentions missing user story")
        success = False
    
    if success:
        print("\n✅ ALL TESTS PASSED! User story detection fix is working correctly.")
    else:
        print("\n❌ Some tests failed. User story detection fix needs more work.")
    
    return success

def test_various_user_story_formats():
    """Test various user story formats to ensure the helper method catches them all"""
    print("\n🧪 Testing Various User Story Formats...")
    
    groomroom = GroomRoom()
    
    test_cases = [
        # Standard format
        ("As a user, I want to see the redesigned sign up modal and be automatically opted into loyalty when I create an account, so that there is no confusion about the loyalty experience.", True),
        # No comma after "As a"
        ("As a customer I want to add a payment method so that I can complete my purchase.", True),
        # "so I can" variation
        ("As a shopper, I want to create an account, so I can save my preferences.", True),
        # "I want to" variation
        ("As a user, I want to update my profile, so that I can keep my details current.", True),
        # Combined variations
        ("As a customer I want to add a payment method so I can complete my purchase.", True),
        # Without ending period
        ("As a user, I want to see my order history, so that I can track my purchases", True),
        # No user story
        ("This is a regular description without user story format.", False),
        # Empty content
        ("", False),
    ]
    
    print("📋 Testing has_user_story() with various formats:")
    print("=" * 60)
    
    all_passed = True
    for i, (content, expected) in enumerate(test_cases, 1):
        result = groomroom.has_user_story(content)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{i:2d}. {status} - Expected: {expected}, Got: {result}")
        if result != expected:
            print(f"      Content: '{content[:50]}...'")
            all_passed = False
    
    if all_passed:
        print("\n✅ ALL FORMAT TESTS PASSED! The helper method correctly detects all user story variations.")
    else:
        print("\n❌ Some format tests failed. The helper method needs improvement.")
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting User Story Detection Fix Tests...")
    
    # Test the main fix
    main_test_passed = test_user_story_detection_fix()
    
    # Test various formats
    format_test_passed = test_various_user_story_formats()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"Main Fix Test: {'✅ PASSED' if main_test_passed else '❌ FAILED'}")
    print(f"Format Tests: {'✅ PASSED' if format_test_passed else '❌ FAILED'}")
    
    if main_test_passed and format_test_passed:
        print("\n🎉 ALL TESTS PASSED! The user story detection fix is working correctly.")
        print("The GroomRoom analysis should now correctly detect user stories and suppress")
        print("false negative messages about missing user stories.")
    else:
        print("\n⚠️ Some tests failed. Please review the implementation.") 