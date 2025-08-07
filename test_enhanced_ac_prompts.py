#!/usr/bin/env python3
"""
Test Enhanced Acceptance Criteria Prompts with Given/When/Then Format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_enhanced_ac_prompts():
    """Test the enhanced Acceptance Criteria prompts with Given/When/Then format"""
    print("🧪 Testing Enhanced Acceptance Criteria Prompts with Given/When/Then Format")
    print("=" * 80)
    
    # Initialize GroomRoom
    groomroom = GroomRoom()
    
    # Test content with user story and vague AC
    test_content = """
    Summary: User Login Enhancement
    
    User Story:
    As a customer, I want to be able to log in with my email and password so that I can access my account and view my orders.
    
    Acceptance Criteria:
    - User can log in with email and password
    - match Figma design
    - works properly
    - looks good on mobile
    """
    
    print("📋 Test Content:")
    print(test_content)
    print("-" * 80)
    
    # Test enhanced AC analysis
    print("🔍 Testing Enhanced AC Analysis...")
    enhanced_ac_analysis = groomroom.analyze_enhanced_acceptance_criteria(test_content)
    
    print(f"✅ AC Present: {enhanced_ac_analysis.get('ac_present', False)}")
    print(f"✅ Overall Quality: {enhanced_ac_analysis.get('overall_quality', 'unknown')}")
    
    # Test vague AC detection
    vague_ac = enhanced_ac_analysis.get('vague_ac_detected', [])
    print(f"✅ Vague AC Detected: {len(vague_ac)} items")
    
    for i, vague_item in enumerate(vague_ac, 1):
        print(f"\n  {i}. Original: {vague_item.get('issue', 'Unknown')}")
        suggestion = vague_item.get('suggestion', '')
        if 'Given/When/Then:' in suggestion:
            print(f"     ✅ Contains Given/When/Then format")
            gwt_part = suggestion.split('Given/When/Then:')[1].strip()
            print(f"     Given/When/Then: {gwt_part}")
    
    # Test user story gaps
    user_story_gaps = enhanced_ac_analysis.get('user_story_gaps', [])
    print(f"\n✅ User Story Gaps: {len(user_story_gaps)} items")
    
    for i, gap in enumerate(user_story_gaps, 1):
        print(f"\n  {i}. Component: {gap.get('component', 'Unknown')}")
        print(f"     Given/When/Then: {gap.get('suggestion', 'No suggestion')}")
    
    # Test missing criteria
    missing_criteria = enhanced_ac_analysis.get('missing_criteria', [])
    print(f"\n✅ Missing Criteria: {len(missing_criteria)} items")
    
    for i, criteria in enumerate(missing_criteria, 1):
        print(f"\n  {i}. Type: {criteria.get('type', 'Unknown')}")
        print(f"     Given/When/Then: {criteria.get('suggestion', 'No suggestion')}")
    
    # Test enhanced AC summary
    print("\n" + "=" * 80)
    print("📝 Enhanced AC Summary:")
    print("-" * 80)
    
    summary = groomroom._create_enhanced_acceptance_criteria_summary(enhanced_ac_analysis)
    print(summary)
    
    print("\n" + "=" * 80)
    print("✅ Enhanced Acceptance Criteria Prompts Test Complete!")
    
    # Verify key enhancements
    success = True
    
    # Check if Given/When/Then format is present in suggestions
    has_gwt_format = any('Given/When/Then:' in item.get('suggestion', '') for item in vague_ac)
    if has_gwt_format:
        print("✅ Given/When/Then format detected in vague AC suggestions")
    else:
        print("❌ Given/When/Then format not found in vague AC suggestions")
        success = False
    
    # Check if user story gaps are detected
    if user_story_gaps:
        print("✅ User story gaps analysis working")
    else:
        print("⚠️ No user story gaps detected (may be expected)")
    
    # Check if missing criteria are detected
    if missing_criteria:
        print("✅ Missing criteria analysis working")
    else:
        print("⚠️ No missing criteria detected (may be expected)")
    
    return success

def test_prompt_instructions():
    """Test that the enhanced prompt instructions are included"""
    print("\n🧪 Testing Enhanced Prompt Instructions")
    print("=" * 80)
    
    groomroom = GroomRoom()
    
    # Get comprehensive instructions
    instructions = groomroom.get_comprehensive_jira_analysis_instructions()
    
    # Check for enhanced AC analysis instructions
    if 'ENHANCED ACCEPTANCE CRITERIA ANALYSIS:' in instructions:
        print("✅ Enhanced AC Analysis instructions found")
    else:
        print("❌ Enhanced AC Analysis instructions not found")
        return False
    
    if 'Given/When/Then' in instructions:
        print("✅ Given/When/Then format mentioned in instructions")
    else:
        print("❌ Given/When/Then format not mentioned in instructions")
        return False
    
    if 'compare the user story to its acceptance criteria' in instructions.lower():
        print("✅ User story comparison mentioned in instructions")
    else:
        print("❌ User story comparison not mentioned in instructions")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Enhanced Acceptance Criteria Prompts Tests")
    print("=" * 80)
    
    test1_success = test_enhanced_ac_prompts()
    test2_success = test_prompt_instructions()
    
    print("\n" + "=" * 80)
    print("📊 Test Results Summary:")
    print(f"✅ Enhanced AC Prompts Test: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Prompt Instructions Test: {'PASS' if test2_success else 'FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! Enhanced Acceptance Criteria prompts are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("=" * 80) 