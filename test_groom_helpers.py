#!/usr/bin/env python3
"""
Test file for GroomRoom helper methods
Tests the centralized helper methods for user story, Figma link, and DoD detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_user_story_detection():
    """Test user story detection with various formats"""
    groomroom = GroomRoom()
    
    test_cases = [
        # Standard format
        ("As a user, I want to see the redesigned sign up modal and be automatically opted into loyalty when I create an account, so that there is no confusion about the loyalty experience.", "", True),
        # No user story
        ("This is a regular description without user story format.", "", False),
        # User story in acceptance criteria
        ("", "As a customer, I want to sign up easily, so that I can start shopping.", True),
        # Mixed content
        ("Regular description", "As a shopper, I want to create an account, so that I can save my preferences.", True),
    ]
    
    print("🧪 Testing User Story Detection")
    for description, ac, expected in test_cases:
        result = groomroom.has_user_story(description, ac)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"   {status} - Expected: {expected}, Got: {result}")
        if result != expected:
            print(f"      Description: '{description[:50]}...'")
            print(f"      AC: '{ac[:50]}...'")

def test_figma_detection():
    """Test Figma link detection with various formats"""
    groomroom = GroomRoom()
    
    test_cases = [
        # Direct Figma URL
        ("Check the design at https://www.figma.com/file/abc123", True),
        # Figma mention without URL
        ("UX should match Figma", True),
        # Figma in acceptance criteria
        ("", "UX should match Figma (Figma word is hyperlinked)", True),
        # No Figma reference
        ("This has no Figma reference", False),
        # Figma in description
        ("The design is in Figma", True),
    ]
    
    print("\n🎨 Testing Figma Detection")
    for field1, expected in test_cases:
        result = groomroom.find_figma_link(field1)
        found = bool(result)
        status = "✅ PASS" if found == expected else "❌ FAIL"
        print(f"   {status} - Expected: {expected}, Got: {found}")
        if found != expected:
            print(f"      Content: '{field1[:50]}...'")
            print(f"      Result: {result}")

def test_dod_gate():
    """Test DoD evaluation with various statuses"""
    groomroom = GroomRoom()
    
    test_cases = [
        ("PROD RELEASE QUEUE", True),
        ("Ready for Release", True),
        ("UAT Complete", True),
        ("In Production", True),
        ("To Do", False),
        ("In Progress", False),
        ("Ready For Dev", False),
        ("", False),
    ]
    
    print("\n📋 Testing DoD Gate")
    for status, expected in test_cases:
        result = groomroom.should_include_dod(status)
        status_icon = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"   {status_icon} - Status: '{status}' -> Expected: {expected}, Got: {result}")

def test_analysis_context():
    """Test the create_analysis_context method"""
    groomroom = GroomRoom()
    
    # Test content with user story, Figma reference, and non-release status
    test_content = """
Description

Prior to starting dev work on this ticket, need data from SFRA controllers for left side of modal: accountmodal-register and accountmodal-login

User Story

As a user, I want to see the redesigned sign up modal and be automatically opted into loyalty when I create an account, so that there is no confusion about the loyalty experience.

Acceptance Criteria

UX should match Figma (Figma word is hyperlinked)

Apply Marmot styling and colors - Marmot style guide (this is hyperlinked)

Status

Ready For Dev
"""
    
    print("\n🔍 Testing Analysis Context")
    context = groomroom.create_analysis_context(test_content)
    
    # Test user story detection
    expected_user_story = True
    actual_user_story = context['user_story_found']
    status = "✅ PASS" if actual_user_story == expected_user_story else "❌ FAIL"
    print(f"   {status} - User story should be found: Expected: {expected_user_story}, Got: {actual_user_story}")
    
    # Test Figma detection
    expected_figma = True
    actual_figma = context['figma_link_found']
    status = "✅ PASS" if actual_figma == expected_figma else "❌ FAIL"
    print(f"   {status} - Figma should be found: Expected: {expected_figma}, Got: {actual_figma}")
    print(f"      Figma link: {context['figma_link']}")
    
    # Test DoD inclusion
    expected_dod = False
    actual_dod = context['include_dod']
    status = "✅ PASS" if actual_dod == expected_dod else "❌ FAIL"
    print(f"   {status} - DoD should be included for release status: Expected: {expected_dod}, Got: {actual_dod}")
    
    # Test status extraction
    expected_status = "Ready For Dev"
    actual_status = context['status']
    status = "✅ PASS" if actual_status == expected_status else "❌ FAIL"
    print(f"   {status} - Status should be extracted: Expected: '{expected_status}', Got: '{actual_status}'")

def test_real_jira_ticket():
    """Test with the actual Jira ticket content provided by the user"""
    groomroom = GroomRoom()
    
    # The actual Jira ticket content from the user
    real_ticket_content = """
Description

Prior to starting dev work on this ticket, need data from SFRA controllers for left side of modal: accountmodal-register and accountmodal-login

User Story

As a user, I want to see the redesigned sign up modal and be automatically opted into loyalty when I create an account, so that there is no confusion about the loyalty experience.

Acceptance Criteria

UX should match Figma (Figma word is hyperlinked)

Apply Marmot styling and colors - Marmot style guide (this is hyperlinked)

Account benefits content asset (left on desktop/tablet modal, top on mobile modal)

T&Cs content asset should reflect in the storefront from SFRA

Email opt-in is controlled by site pref from SFRA

SMS opt-in phone number field

Error states

Loyalty should be opted in automatically upon account creation

Modal closes upon successful user registration

Modal closes if user clicks outside of the modal

Facebook sign up should be removed from the modal as it's no longer going to be an option for users to sign up via FB

Modal should adjust in height dependent on any error messages and the space those messages take

If new account modal is disabled, the existing flow should be present

For PWA sites, additional logic need to be added to show login pop up when user lands on homepage with /?modal=login parameters. 
Can check below URL for reference: https://test.foodsaver.com/?modal=login

Status

Ready For Dev
"""
    
    print("\n🎯 Testing Real Jira Ticket")
    context = groomroom.create_analysis_context(real_ticket_content)
    
    # Test user story detection
    expected_user_story = True
    actual_user_story = context['user_story_found']
    status = "✅ PASS" if actual_user_story == expected_user_story else "❌ FAIL"
    print(f"   {status} - User story should be found: Expected: {expected_user_story}, Got: {actual_user_story}")
    
    # Test Figma detection
    expected_figma = True
    actual_figma = context['figma_link_found']
    status = "✅ PASS" if actual_figma == expected_figma else "❌ FAIL"
    print(f"   {status} - Figma should be found: Expected: {expected_figma}, Got: {actual_figma}")
    print(f"      Figma link: {context['figma_link']}")
    
    # Test DoD inclusion
    expected_dod = False
    actual_dod = context['include_dod']
    status = "✅ PASS" if actual_dod == expected_dod else "❌ FAIL"
    print(f"   {status} - DoD should be included for release status: Expected: {expected_dod}, Got: {actual_dod}")
    
    # Test status extraction
    expected_status = "Ready For Dev"
    actual_status = context['status']
    status = "✅ PASS" if actual_status == expected_status else "❌ FAIL"
    print(f"   {status} - Status should be extracted: Expected: '{expected_status}', Got: '{actual_status}'")

def main():
    """Run all tests"""
    print("🧪 GroomRoom Helper Methods Test Suite")
    print("=" * 50)
    
    try:
        test_user_story_detection()
        test_figma_detection()
        test_dod_gate()
        test_analysis_context()
        test_real_jira_ticket()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 