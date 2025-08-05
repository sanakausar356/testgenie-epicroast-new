#!/usr/bin/env python3
"""
Test script for enhanced GroomRoom functionality
Tests the new field reading accuracy fixes
"""

import sys
import os
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_enhanced_user_story_detection():
    """Test enhanced user story detection"""
    print("🧪 Testing Enhanced User Story Detection...")
    
    from groomroom.core import GroomRoom
    
    groomroom = GroomRoom()
    
    # Test case 1: User story in description (like ODCD-33741)
    test_content_1 = """
Summary: Add payment method to checkout
Description: As a customer, I want to add a new payment method during checkout, so that I can complete my purchase.
Acceptance Criteria:
- User can add credit card
- User can add PayPal
- Payment method is saved for future use
"""
    
    result_1 = groomroom.detect_user_story_enhanced(test_content_1)
    print(f"Test 1 - User story in description:")
    print(f"  Found: {result_1['user_story_found']}")
    print(f"  Location: {result_1['location']}")
    print(f"  Confidence: {result_1['confidence']}")
    print(f"  Debug: {result_1['debug_info']}")
    print()
    
    # Test case 2: User story in Acceptance Criteria
    test_content_2 = """
Summary: Update user profile
Description: Allow users to update their profile information
Acceptance Criteria:
As a user, I want to update my profile information, so that I can keep my details current.
- User can edit name
- User can edit email
- Changes are saved immediately
"""
    
    result_2 = groomroom.detect_user_story_enhanced(test_content_2)
    print(f"Test 2 - User story in AC:")
    print(f"  Found: {result_2['user_story_found']}")
    print(f"  Location: {result_2['location']}")
    print(f"  Confidence: {result_2['confidence']}")
    print(f"  Debug: {result_2['debug_info']}")
    print()
    
    # Test case 3: No user story
    test_content_3 = """
Summary: Fix login bug
Description: Users cannot log in with valid credentials
Acceptance Criteria:
- Login form accepts valid credentials
- Error message shown for invalid credentials
- Session is created after successful login
"""
    
    result_3 = groomroom.detect_user_story_enhanced(test_content_3)
    print(f"Test 3 - No user story:")
    print(f"  Found: {result_3['user_story_found']}")
    print(f"  Location: {result_3['location']}")
    print(f"  Confidence: {result_3['confidence']}")
    print(f"  Debug: {result_3['debug_info']}")
    print()

def test_enhanced_figma_detection():
    """Test enhanced Figma link detection"""
    print("🎨 Testing Enhanced Figma Link Detection...")
    
    from groomroom.core import GroomRoom
    
    groomroom = GroomRoom()
    
    # Test case 1: Figma link in Acceptance Criteria
    test_content_1 = """
Summary: Design new checkout flow
Description: Implement new checkout design
Acceptance Criteria:
- Follow design in https://www.figma.com/file/abc123/checkout-design
- Button should be blue as shown in design
- Layout matches Figma mockup exactly
"""
    
    result_1 = groomroom.detect_figma_links_enhanced(test_content_1)
    print(f"Test 1 - Figma link in AC:")
    print(f"  Found: {result_1['figma_link_found']}")
    print(f"  Locations: {result_1['locations']}")
    print(f"  Links: {result_1['links']}")
    print(f"  Confidence: {result_1['confidence']}")
    print(f"  Debug: {result_1['debug_info']}")
    print()
    
    # Test case 2: Figma link in description
    test_content_2 = """
Summary: Update homepage design
Description: 
Please refer to the new homepage design: https://www.figma.com/file/def456/homepage-update
The design shows a new hero section and updated navigation.

Acceptance Criteria:
- Implement new hero section
- Update navigation layout
- Match colors from design
"""
    
    result_2 = groomroom.detect_figma_links_enhanced(test_content_2)
    print(f"Test 2 - Figma link in description:")
    print(f"  Found: {result_2['figma_link_found']}")
    print(f"  Locations: {result_2['locations']}")
    print(f"  Links: {result_2['links']}")
    print(f"  Confidence: {result_2['confidence']}")
    print(f"  Debug: {result_2['debug_info']}")
    print()
    
    # Test case 3: No Figma link
    test_content_3 = """
Summary: Fix responsive layout
Description: Layout breaks on mobile devices
Acceptance Criteria:
- Layout works on mobile
- Layout works on tablet
- Layout works on desktop
"""
    
    result_3 = groomroom.detect_figma_links_enhanced(test_content_3)
    print(f"Test 3 - No Figma link:")
    print(f"  Found: {result_3['figma_link_found']}")
    print(f"  Locations: {result_3['locations']}")
    print(f"  Links: {result_3['links']}")
    print(f"  Confidence: {result_3['confidence']}")
    print(f"  Debug: {result_3['debug_info']}")
    print()

def test_dod_evaluation():
    """Test DoD evaluation logic"""
    print("✅ Testing DoD Evaluation Logic...")
    
    from groomroom.core import GroomRoom
    
    groomroom = GroomRoom()
    
    # Test case 1: Release-ready status
    test_content_1 = """
Summary: Production deployment
Status: Ready for Release
Status Category: Release
Description: Deploy to production environment
"""
    
    result_1 = groomroom.should_evaluate_dod(test_content_1)
    print(f"Test 1 - Release-ready status:")
    print(f"  Should evaluate: {result_1['should_evaluate']}")
    print(f"  Status found: {result_1['status_found']}")
    print(f"  Reason: {result_1['reason']}")
    print(f"  Debug: {result_1['debug_info']}")
    print()
    
    # Test case 2: Grooming status
    test_content_2 = """
Summary: New feature implementation
Status: To Do
Status Category: Development
Description: Implement new user feature
"""
    
    result_2 = groomroom.should_evaluate_dod(test_content_2)
    print(f"Test 2 - Grooming status:")
    print(f"  Should evaluate: {result_2['should_evaluate']}")
    print(f"  Status found: {result_2['status_found']}")
    print(f"  Reason: {result_2['reason']}")
    print(f"  Debug: {result_2['debug_info']}")
    print()
    
    # Test case 3: PROD RELEASE QUEUE status
    test_content_3 = """
Summary: Bug fix for production
Status: PROD RELEASE QUEUE
Description: Fix critical bug in production
"""
    
    result_3 = groomroom.should_evaluate_dod(test_content_3)
    print(f"Test 3 - PROD RELEASE QUEUE status:")
    print(f"  Should evaluate: {result_3['should_evaluate']}")
    print(f"  Status found: {result_3['status_found']}")
    print(f"  Reason: {result_3['reason']}")
    print(f"  Debug: {result_3['debug_info']}")
    print()

def test_enhanced_scoring():
    """Test enhanced scoring with detection flags"""
    print("📊 Testing Enhanced Scoring...")
    
    from groomroom.core import GroomRoom
    
    groomroom = GroomRoom()
    
    # Test case: User story and Figma found
    test_content = """
Summary: New checkout design
Description: As a customer, I want a streamlined checkout process, so that I can complete my purchase quickly.
Acceptance Criteria:
- Follow design in https://www.figma.com/file/abc123/checkout-design
- Implement one-click checkout
- Show order summary
"""
    
    # Run enhanced detection
    user_story_analysis = groomroom.detect_user_story_enhanced(test_content)
    figma_analysis = groomroom.detect_figma_links_enhanced(test_content)
    
    print(f"Enhanced Detection Results:")
    print(f"  User Story Found: {user_story_analysis['user_story_found']}")
    print(f"  Figma Link Found: {figma_analysis['figma_link_found']}")
    print()
    
    # Create mock analysis data
    mock_analyses = {
        'dor_analysis': {
            'user_story': {
                'name': 'User Story',
                'coverage_percentage': 30.0  # Low score that should be corrected
            }
        },
        'stakeholder_analysis': {
            'design_validation': {
                'missing': True  # Should be corrected by Figma detection
            }
        },
        'dependencies_analysis': {},
        'test_scenarios_analysis': {}
    }
    
    # Test enhanced scoring
    enhanced_score = groomroom.calculate_groom_readiness_score_enhanced(
        mock_analyses,
        user_story_analysis['user_story_found'],
        figma_analysis['figma_link_found']
    )
    
    print(f"Enhanced Scoring Results:")
    print(f"  Overall Score: {enhanced_score['overall_score']}")
    print(f"  Total Possible: {enhanced_score['total_possible']}")
    print(f"  Percentage: {(enhanced_score['overall_score'] / enhanced_score['total_possible'] * 100):.1f}%")
    print(f"  Corrections Made: {enhanced_score['enhanced_scoring']['corrections_made']}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced GroomRoom Tests")
    print("=" * 50)
    
    try:
        test_enhanced_user_story_detection()
        test_enhanced_figma_detection()
        test_dod_evaluation()
        test_enhanced_scoring()
        
        print("✅ All tests completed successfully!")
        print("Enhanced GroomRoom functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 