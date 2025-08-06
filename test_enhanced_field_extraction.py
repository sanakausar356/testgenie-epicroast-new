#!/usr/bin/env python3
"""
Test enhanced field extraction with various formats
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_enhanced_field_extraction():
    """Test the enhanced field extraction with various formats"""
    print("🧪 Testing Enhanced Field Extraction...")
    
    groomroom = GroomRoom()
    
    # Test different field formats
    test_cases = [
        {
            "name": "Standard colon format",
            "content": """
Summary: Test ticket
Description: As a user, I want to test the field extraction, so that I can verify it works.
Acceptance Criteria: Match Figma designs: https://www.figma.com/file/abc123/test
Status: To Do
"""
        },
        {
            "name": "Markdown format",
            "content": """
**Summary:** Test ticket
**Description:** As a user, I want to test the field extraction, so that I can verify it works.
**Acceptance Criteria:** Match Figma designs: https://www.figma.com/file/abc123/test
**Status:** To Do
"""
        },
        {
            "name": "Dash format",
            "content": """
Summary - Test ticket
Description - As a user, I want to test the field extraction, so that I can verify it works.
Acceptance Criteria - Match Figma designs: https://www.figma.com/file/abc123/test
Status - To Do
"""
        },
        {
            "name": "Standalone field names",
            "content": """
Summary
Test ticket

Description
As a user, I want to test the field extraction, so that I can verify it works.

Acceptance Criteria
Match Figma designs: https://www.figma.com/file/abc123/test

Status
To Do
"""
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("=" * 60)
        
        content = test_case['content']
        
        # Test field extraction
        description = groomroom._extract_field_section(content, 'description')
        ac = groomroom._extract_field_section(content, 'acceptance criteria')
        
        print(f"Description extracted: {len(description)} chars")
        print(f"Description: '{description[:100]}...'")
        print(f"Acceptance Criteria extracted: {len(ac)} chars")
        print(f"AC: '{ac[:100]}...'")
        
        # Test user story detection
        has_story = groomroom.has_user_story(description, ac)
        print(f"User story detected: {has_story}")
        
        # Test Figma link detection
        figma_link = groomroom.find_figma_link(description, ac)
        print(f"Figma link detected: {figma_link}")
        
        # Test analysis context
        context = groomroom.create_analysis_context(content)
        print(f"Context - User story: {context['user_story_found']}")
        print(f"Context - Figma link: {context['figma_link_found']}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("🚀 Testing Enhanced Field Extraction...")
    test_enhanced_field_extraction()
    print("\n✅ Enhanced field extraction test completed!") 