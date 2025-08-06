#!/usr/bin/env python3
"""
Debug script to test field extraction and detection issues
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_field_extraction():
    """Test field extraction with sample content"""
    print("🔍 Testing Field Extraction Logic...")
    
    groomroom = GroomRoom()
    
    # Sample content that should have user stories and Figma links
    test_content = """
Summary: Redesign PWA sign-up modal with loyalty opt-in
Description: As a returning customer, I want to see a redesigned sign-up modal with loyalty opt-in, so that I can easily join the rewards program during registration. This story scopes the redesign of the PWA sign-up modal for the MMT (Marmot) brand.

Acceptance Criteria:
- Match Figma designs: https://www.figma.com/file/abc123/signup-modal
- Update profile account component
- Update sign-up component
- Remove previous rewards screen

Test Scenarios:
- Cross-browser testing (Safari, Chrome)
- Cross-device testing (desktop, tablet, mobile)
- Email opt-in toggle functionality
- Session expiry handling

Status: Ready For Dev
Priority: Medium
"""
    
    print("\n📋 Test Content:")
    print("=" * 60)
    print(test_content)
    print("=" * 60)
    
    # Test field extraction
    print("\n🔍 Field Extraction Results:")
    print("-" * 40)
    
    description = groomroom._extract_field_section(test_content, 'description')
    print(f"Description extracted: {len(description)} chars")
    print(f"Description content: '{description[:100]}...'")
    
    ac = groomroom._extract_field_section(test_content, 'acceptance criteria')
    print(f"Acceptance Criteria extracted: {len(ac)} chars")
    print(f"AC content: '{ac[:100]}...'")
    
    test_scenarios = groomroom._extract_field_section(test_content, 'test scenarios')
    print(f"Test Scenarios extracted: {len(test_scenarios)} chars")
    print(f"Test Scenarios content: '{test_scenarios[:100]}...'")
    
    # Test user story detection
    print("\n🔍 User Story Detection:")
    print("-" * 40)
    
    has_story = groomroom.has_user_story(description, ac)
    print(f"has_user_story() result: {has_story}")
    
    enhanced_result = groomroom.detect_user_story_enhanced(test_content)
    print(f"detect_user_story_enhanced() result: {enhanced_result['user_story_found']}")
    print(f"Location: {enhanced_result['location']}")
    print(f"Debug info: {enhanced_result['debug_info']}")
    
    # Test Figma link detection
    print("\n🔍 Figma Link Detection:")
    print("-" * 40)
    
    figma_link = groomroom.find_figma_link(description, ac)
    print(f"find_figma_link() result: {figma_link}")
    
    enhanced_figma = groomroom.detect_figma_links_enhanced(test_content)
    print(f"detect_figma_links_enhanced() result: {enhanced_figma['figma_link_found']}")
    print(f"Links found: {enhanced_figma['links']}")
    print(f"Debug info: {enhanced_figma['debug_info']}")
    
    # Test analysis context
    print("\n🔍 Analysis Context:")
    print("-" * 40)
    
    context = groomroom.create_analysis_context(test_content)
    print(f"User story found: {context['user_story_found']}")
    print(f"Figma link found: {context['figma_link_found']}")
    print(f"Figma link: {context['figma_link']}")
    
    # Test framework analysis
    print("\n🔍 Framework Analysis:")
    print("-" * 40)
    
    framework_analysis = groomroom.analyze_frameworks(test_content, context['user_story_found'])
    user_story_framework = framework_analysis.get('user_story_template', {})
    print(f"User Story Template coverage: {user_story_framework.get('coverage_percentage', 0):.1f}%")
    print(f"Missing elements: {user_story_framework.get('missing_elements', [])}")
    
    # Test DOR analysis
    print("\n🔍 DOR Analysis:")
    print("-" * 40)
    
    dor_analysis = groomroom.analyze_dor_requirements(test_content, context['user_story_found'])
    user_story_dor = dor_analysis.get('user_story', {})
    print(f"User Story coverage: {user_story_dor.get('coverage_percentage', 0):.1f}%")
    print(f"Missing elements: {user_story_dor.get('missing_elements', [])}")

def test_with_actual_content():
    """Test with content similar to what the user is seeing"""
    print("\n🧪 Testing with Actual Content Pattern...")
    
    groomroom = GroomRoom()
    
    # Content that matches the pattern from the user's analysis output
    actual_content = """
Summary: This story scopes the redesign of the PWA sign-up modal for the MMT (Marmot) brand, introducing a loyalty opt-in section and updating the left-side content based on SFRA controller data (accountmodal-register and accountmodal-login). The work is currently marked Ready For Dev but requires further refinement to meet Definition of Ready standards.

Description: This story scopes the redesign of the PWA sign-up modal for the MMT (Marmot) brand, introducing a loyalty opt-in section and updating the left-side content based on SFRA controller data (accountmodal-register and accountmodal-login). The work is currently marked Ready For Dev but requires further refinement to meet Definition of Ready standards.

Acceptance Criteria:
- Match Figma designs: https://www.figma.com/file/abc123/signup-modal
- Update profile account component
- Update sign-up component
- Remove previous rewards screen

Test Scenarios:
- Cross-browser testing (Safari, Chrome)
- Cross-device testing (desktop, tablet, mobile)
- Email opt-in toggle functionality
- Session expiry handling

Status: Ready For Dev
Priority: Medium
"""
    
    print("\n📋 Actual Content Pattern:")
    print("=" * 60)
    print(actual_content)
    print("=" * 60)
    
    # Test field extraction
    print("\n🔍 Field Extraction Results:")
    print("-" * 40)
    
    description = groomroom._extract_field_section(actual_content, 'description')
    print(f"Description extracted: {len(description)} chars")
    print(f"Description content: '{description[:100]}...'")
    
    ac = groomroom._extract_field_section(actual_content, 'acceptance criteria')
    print(f"Acceptance Criteria extracted: {len(ac)} chars")
    print(f"AC content: '{ac[:100]}...'")
    
    # Test user story detection
    print("\n🔍 User Story Detection:")
    print("-" * 40)
    
    has_story = groomroom.has_user_story(description, ac)
    print(f"has_user_story() result: {has_story}")
    
    enhanced_result = groomroom.detect_user_story_enhanced(actual_content)
    print(f"detect_user_story_enhanced() result: {enhanced_result['user_story_found']}")
    print(f"Location: {enhanced_result['location']}")
    print(f"Debug info: {enhanced_result['debug_info']}")
    
    # Test Figma link detection
    print("\n🔍 Figma Link Detection:")
    print("-" * 40)
    
    figma_link = groomroom.find_figma_link(description, ac)
    print(f"find_figma_link() result: {figma_link}")
    
    enhanced_figma = groomroom.detect_figma_links_enhanced(actual_content)
    print(f"detect_figma_links_enhanced() result: {enhanced_figma['figma_link_found']}")
    print(f"Links found: {enhanced_figma['links']}")
    print(f"Debug info: {enhanced_figma['debug_info']}")
    
    # Test analysis context
    print("\n🔍 Analysis Context:")
    print("-" * 40)
    
    context = groomroom.create_analysis_context(actual_content)
    print(f"User story found: {context['user_story_found']}")
    print(f"Figma link found: {context['figma_link_found']}")
    print(f"Figma link: {context['figma_link']}")

if __name__ == "__main__":
    print("🚀 Starting Field Extraction Debug...")
    
    # Test with sample content
    test_field_extraction()
    
    # Test with actual content pattern
    test_with_actual_content()
    
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY:")
    print("This will help identify why user stories and Figma links")
    print("aren't being detected in the actual analysis output.") 