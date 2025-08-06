#!/usr/bin/env python3
"""
Test enhanced user story detection with various formats
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_enhanced_user_story_detection():
    """Test the enhanced user story detection with various formats"""
    print("🧪 Testing Enhanced User Story Detection...")
    
    groomroom = GroomRoom()
    
    # Test different user story formats
    test_cases = [
        {
            "name": "Standard format",
            "content": """
Summary: Test ticket
Description: As a customer, I want to add a payment method, so that I can complete my purchase.
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "Flexible format without punctuation",
            "content": """
Summary: Test ticket
Description: As a user I want to sign up so that I can access the platform
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "I want to format",
            "content": """
Summary: Test ticket
Description: As a shopper I want to add items to cart so I can purchase them
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "I need format",
            "content": """
Summary: Test ticket
Description: As a guest I need to create an account so that I can save my preferences
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "I would like format",
            "content": """
Summary: Test ticket
Description: As a returning customer I would like to see my order history so that I can track my purchases
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "In order to format",
            "content": """
Summary: Test ticket
Description: As a user I want to update my profile in order to keep my information current
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "Any I action format",
            "content": """
Summary: Test ticket
Description: As a customer I can view product details so that I can make informed decisions
Acceptance Criteria: Match Figma designs
Status: To Do
"""
        },
        {
            "name": "No user story (should fail)",
            "content": """
Summary: Test ticket
Description: This is a regular description without user story format
Acceptance Criteria: Match Figma designs
Status: To Do
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
        
        print(f"Description: '{description[:100]}...'")
        
        # Test user story detection
        has_story = groomroom.has_user_story(description, ac)
        print(f"has_user_story() result: {has_story}")
        
        enhanced_result = groomroom.detect_user_story_enhanced(content)
        print(f"detect_user_story_enhanced() result: {enhanced_result['user_story_found']}")
        print(f"Location: {enhanced_result['location']}")
        print(f"Pattern matched: {enhanced_result['pattern_matched']}")
        print(f"Debug info: {enhanced_result['debug_info']}")
        
        # Test analysis context
        context = groomroom.create_analysis_context(content)
        print(f"Context - User story: {context['user_story_found']}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("🚀 Testing Enhanced User Story Detection...")
    test_enhanced_user_story_detection()
    print("\n✅ Enhanced user story detection test completed!") 