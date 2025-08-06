#!/usr/bin/env python3
"""
Test script to verify the user story detection fix works for ODCD-33741
Simulates the exact scenario mentioned in the user's request
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_odcd_33741_scenario():
    """Test the exact scenario described in the user's request for ODCD-33741"""
    print("🧪 Testing ODCD-33741 User Story Detection Fix...")
    
    groomroom = GroomRoom()
    
    # Simulate the ODCD-33741 ticket content with user story in Description
    # This is the scenario where the user story is clearly present but was being flagged as missing
    test_content = """
Summary: Add payment method to checkout
Description: As a customer, I want to add a new payment method during checkout, so that I can complete my purchase.
Acceptance Criteria:
- User can add credit card
- User can add PayPal
- Payment method is saved for future use
- User receives confirmation email
Status: To Do
Priority: Medium
"""
    
    print("\n📋 Test Case: ODCD-33741 - User Story in Description")
    print("=" * 60)
    
    # Test the new centralized helper method
    description = "As a customer, I want to add a new payment method during checkout, so that I can complete my purchase."
    ac = "User can add credit card\nUser can add PayPal\nPayment method is saved for future use\nUser receives confirmation email"
    
    result = groomroom.has_user_story(description, ac)
    print(f"✅ has_user_story() result: {result}")
    
    # Test the analysis context creation
    context = groomroom.create_analysis_context(test_content)
    print(f"✅ create_analysis_context() user_story_found: {context['user_story_found']}")
    
    # Test all the analysis methods that were previously showing false negatives
    print("\n🔍 Testing Analysis Methods:")
    print("-" * 40)
    
    # 1. Framework Analysis
    framework_analysis = groomroom.analyze_frameworks(test_content, context['user_story_found'])
    user_story_framework = framework_analysis.get('user_story_template', {})
    print(f"1. Framework Analysis - User Story Template:")
    print(f"   Coverage: {user_story_framework.get('coverage_percentage', 0):.1f}%")
    print(f"   Missing elements: {user_story_framework.get('missing_elements', [])}")
    print(f"   Suggestions: {user_story_framework.get('suggestions', [])}")
    
    # 2. DOR Analysis
    dor_analysis = groomroom.analyze_dor_requirements(test_content, context['user_story_found'])
    user_story_dor = dor_analysis.get('user_story', {})
    print(f"\n2. DOR Analysis - User Story:")
    print(f"   Coverage: {user_story_dor.get('coverage_percentage', 0):.1f}%")
    print(f"   Missing elements: {user_story_dor.get('missing_elements', [])}")
    print(f"   Suggestions: {user_story_dor.get('suggestions', [])}")
    
    # 3. Sprint Readiness Analysis
    sprint_analysis = groomroom.analyze_sprint_readiness(test_content, context['user_story_found'])
    print(f"\n3. Sprint Readiness Analysis:")
    print(f"   Missing for sprint: {sprint_analysis.get('missing_for_sprint', [])}")
    print(f"   Recommendations: {sprint_analysis.get('recommendations', [])}")
    
    # 4. Visual Checklist
    all_analyses = {
        'dor_analysis': dor_analysis,
        'dependencies_analysis': {},
        'stakeholder_analysis': {},
        'test_scenarios_analysis': {}
    }
    visual_checklist = groomroom.create_visual_checklist(all_analyses, context['user_story_found'])
    print(f"\n4. Visual Checklist:")
    print(f"   Overall status: {visual_checklist['overall_status']}")
    print(f"   DOR section: {visual_checklist['sections'].get('dor', {}).get('status', 'unknown')}")
    
    # 5. Groom Readiness Score
    groom_score = groomroom.calculate_groom_readiness_score(all_analyses, context['user_story_found'])
    print(f"\n5. Groom Readiness Score:")
    print(f"   Overall score: {groom_score['overall_score']}/{groom_score['total_possible']}")
    print(f"   Critical gaps: {groom_score['critical_gaps']}")
    
    # Test summary creation methods
    print("\n📝 Testing Summary Creation Methods:")
    print("-" * 40)
    
    # Framework Summary
    framework_summary = groomroom._create_framework_summary(framework_analysis, context['user_story_found'])
    print(f"1. Framework Summary:")
    print(framework_summary)
    
    # DOR Summary
    dor_summary = groomroom._create_dor_summary(dor_analysis, context['user_story_found'])
    print(f"\n2. DOR Summary:")
    print(dor_summary)
    
    # Sprint Readiness Summary
    sprint_summary = groomroom._create_sprint_readiness_summary(sprint_analysis)
    print(f"\n3. Sprint Readiness Summary:")
    print(sprint_summary)
    
    # Checklist Summary
    checklist_summary = groomroom._create_checklist_summary(visual_checklist)
    print(f"\n4. Checklist Summary:")
    print(checklist_summary)
    
    print("\n" + "=" * 60)
    print("🎯 Expected Results (Based on User's Request):")
    print("❌ BEFORE FIX:")
    print("   - 'User Story Template Missing' in Key Findings")
    print("   - 'Define a Clear User Story' in Improvement Suggestions")
    print("   - 'User Story Template: 0%' in Framework Coverage")
    print("   - '[ ] User Story defined with business value' in the Checklist")
    print("   - 'User story is missing' in Sprint Readiness")
    print("\n✅ AFTER FIX:")
    print("   - User story should be detected as FOUND")
    print("   - Framework coverage should be 100% (not 0%)")
    print("   - DOR coverage should be 100% (not missing)")
    print("   - Sprint readiness should NOT mention 'User story is missing'")
    print("   - All summaries should NOT mention missing user story")
    
    # Verify the results
    success = True
    issues_found = []
    
    if not result:
        issues_found.append("❌ has_user_story() failed to detect user story")
        success = False
    
    if not context['user_story_found']:
        issues_found.append("❌ create_analysis_context() failed to detect user story")
        success = False
    
    if user_story_framework.get('coverage_percentage', 0) < 100:
        issues_found.append("❌ Framework analysis still shows missing user story")
        success = False
    
    if user_story_dor.get('coverage_percentage', 0) < 100:
        issues_found.append("❌ DOR analysis still shows missing user story")
        success = False
    
    if 'User story is missing' in sprint_analysis.get('missing_for_sprint', []):
        issues_found.append("❌ Sprint readiness still mentions missing user story")
        success = False
    
    if 'User Story Template' in user_story_framework.get('missing_elements', []):
        issues_found.append("❌ Framework analysis still lists 'User Story Template' as missing")
        success = False
    
    if 'User Story defined with business value' in user_story_dor.get('missing_elements', []):
        issues_found.append("❌ DOR analysis still lists 'User Story defined with business value' as missing")
        success = False
    
    if success:
        print("\n✅ ALL TESTS PASSED! The ODCD-33741 fix is working correctly.")
        print("The GroomRoom analysis now correctly detects user stories and suppresses")
        print("false negative messages about missing user stories across all sections.")
    else:
        print("\n❌ Some tests failed. Issues found:")
        for issue in issues_found:
            print(f"   {issue}")
        print("\nThe user story detection fix needs more work.")
    
    return success

def test_looser_variations():
    """Test the bonus requirement for looser variations of user story format"""
    print("\n🧪 Testing Looser User Story Variations (Bonus Requirement)...")
    
    groomroom = GroomRoom()
    
    test_cases = [
        # Standard variations
        ("As a [role] I want to [goal] so I can [benefit]", True),
        ("As a [persona], I want [action], so I can [value]", True),
        # Without exact punctuation
        ("As a user I want to login so that I can access my account", True),
        ("As a customer I want to checkout so I can buy products", True),
        # Different casing
        ("as a USER, I WANT to login, SO THAT I can access my account", True),
        ("AS A customer, i want to checkout, so i can buy products", True),
        # Mixed variations
        ("As a shopper I want to add items so I can purchase them", True),
        ("As a user, I want to update profile so that I can keep details current", True),
        # Edge cases
        ("As a user I want to do something so that I get value", True),
        ("As a customer I want to perform action so I can achieve goal", True),
        # Non-user stories
        ("This is not a user story", False),
        ("I want to do something", False),
        ("As a user I want something", False),  # Missing "so that" part
    ]
    
    print("📋 Testing has_user_story() with looser variations:")
    print("=" * 60)
    
    all_passed = True
    for i, (content, expected) in enumerate(test_cases, 1):
        result = groomroom.has_user_story(content)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{i:2d}. {status} - Expected: {expected}, Got: {result}")
        if result != expected:
            print(f"      Content: '{content}'")
            all_passed = False
    
    if all_passed:
        print("\n✅ ALL LOOSER VARIATION TESTS PASSED! The helper method correctly detects")
        print("various user story formats without requiring exact punctuation or casing.")
    else:
        print("\n❌ Some looser variation tests failed. The helper method needs improvement.")
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting ODCD-33741 User Story Detection Fix Tests...")
    
    # Test the main ODCD-33741 scenario
    main_test_passed = test_odcd_33741_scenario()
    
    # Test looser variations (bonus requirement)
    variation_test_passed = test_looser_variations()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"ODCD-33741 Fix Test: {'✅ PASSED' if main_test_passed else '❌ FAILED'}")
    print(f"Looser Variations Test: {'✅ PASSED' if variation_test_passed else '❌ FAILED'}")
    
    if main_test_passed and variation_test_passed:
        print("\n🎉 ALL TESTS PASSED! The user story detection fix is working correctly.")
        print("✅ The fix addresses all the issues mentioned in the user's request:")
        print("   - User story detection now works correctly")
        print("   - False negative messages are suppressed")
        print("   - Looser variations are supported")
        print("   - The fix is applied globally across all analysis modules")
    else:
        print("\n⚠️ Some tests failed. Please review the implementation.") 