#!/usr/bin/env python3
"""
Sanity check test file for GroomRoom helper methods
Tests the centralized helper methods: has_user_story, find_figma_link, should_include_dod
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_user_story_detection():
    """Test the has_user_story helper method"""
    print("🧪 Testing User Story Detection...")
    
    groomroom = GroomRoom()
    
    # Test cases
    test_cases = [
        {
            'description': "As a shopper, I want to sign up so that I can earn rewards.",
            'ac': "",
            'expected': True,
            'name': "User story in description"
        },
        {
            'description': "This is a regular description without user story format.",
            'ac': "As a user, I want to login so that I can access my account.",
            'expected': True,
            'name': "User story in acceptance criteria"
        },
        {
            'description': "As a customer, I want to browse products so I can find what I need.",
            'ac': "As a user, I want to login so that I can access my account.",
            'expected': True,
            'name': "User stories in both description and AC"
        },
        {
            'description': "This is a regular description without user story format.",
            'ac': "The system should allow users to login.",
            'expected': False,
            'name': "No user story format"
        },
        {
            'description': "As a user, I want to do something so that I can achieve a goal",
            'ac': "",
            'expected': True,
            'name': "User story without period"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = groomroom.has_user_story(test_case['description'], test_case['ac'])
        passed = result == test_case['expected']
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {i}. {test_case['name']}: {status}")
        if not passed:
            print(f"     Expected: {test_case['expected']}, Got: {result}")
            all_passed = False
    
    print(f"User Story Detection: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}\n")
    return all_passed

def test_figma_detection():
    """Test the find_figma_link helper method"""
    print("🎨 Testing Figma Link Detection...")
    
    groomroom = GroomRoom()
    
    # Test cases
    test_cases = [
        {
            'fields': ["Design can be found here: https://www.figma.com/file/abc123"],
            'expected': "https://www.figma.com/file/abc123",
            'name': "Figma link in single field"
        },
        {
            'fields': ["Description: Some text", "AC: Check design at https://www.figma.com/file/xyz789"],
            'expected': "https://www.figma.com/file/xyz789",
            'name': "Figma link in second field"
        },
        {
            'fields': ["No figma link here", "Just regular text"],
            'expected': None,
            'name': "No Figma link"
        },
        {
            'fields': ["https://www.figma.com/file/abc123", "https://www.figma.com/file/xyz789"],
            'expected': "https://www.figma.com/file/abc123",
            'name': "Multiple Figma links (should return first)"
        },
        {
            'fields': ["Check the design: https://www.figma.com/file/abc123/design-name"],
            'expected': "https://www.figma.com/file/abc123/design-name",
            'name': "Figma link with additional path"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = groomroom.find_figma_link(*test_case['fields'])
        passed = result == test_case['expected']
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {i}. {test_case['name']}: {status}")
        if not passed:
            print(f"     Expected: {test_case['expected']}, Got: {result}")
            all_passed = False
    
    print(f"Figma Link Detection: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}\n")
    return all_passed

def test_dod_gate():
    """Test the should_include_dod helper method"""
    print("🚀 Testing DoD Evaluation Gate...")
    
    groomroom = GroomRoom()
    
    # Test cases
    test_cases = [
        {
            'status': "PROD RELEASE QUEUE",
            'expected': True,
            'name': "Prod release queue status"
        },
        {
            'status': "Ready for Release",
            'expected': True,
            'name': "Ready for release status"
        },
        {
            'status': "UAT Complete",
            'expected': True,
            'name': "UAT complete status"
        },
        {
            'status': "In Production",
            'expected': True,
            'name': "In production status"
        },
        {
            'status': "To Do",
            'expected': False,
            'name': "Grooming status"
        },
        {
            'status': "In Progress",
            'expected': False,
            'name': "Development status"
        },
        {
            'status': "Ready for Review",
            'expected': False,
            'name': "Review status"
        },
        {
            'status': "",
            'expected': False,
            'name': "Empty status"
        },
        {
            'status': None,
            'expected': False,
            'name': "None status"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = groomroom.should_include_dod(test_case['status'])
        passed = result == test_case['expected']
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {i}. {test_case['name']}: {status}")
        if not passed:
            print(f"     Expected: {test_case['expected']}, Got: {result}")
            all_passed = False
    
    print(f"DoD Evaluation Gate: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}\n")
    return all_passed

def test_analysis_context():
    """Test the create_analysis_context helper method"""
    print("🔧 Testing Analysis Context Creation...")
    
    groomroom = GroomRoom()
    
    # Test ticket content with all elements - using format that _extract_field_section can parse
    test_content = """
Description: As a user, I want to login so that I can access my account.

Acceptance Criteria:
- User can enter credentials
- Design reference: https://www.figma.com/file/abc123
- System validates input

Status: PROD RELEASE QUEUE
"""
    
    # Extract fields using the helper method
    description_extracted = groomroom._extract_field_section(test_content, 'description')
    ac_extracted = groomroom._extract_field_section(test_content, 'acceptance criteria')
    status_extracted = groomroom._extract_field_section(test_content, 'status')
    
    context = groomroom.create_analysis_context(test_content)
    
    # Test assertions
    tests = [
        ('user_story_found', True, "User story should be found"),
        ('figma_link_found', True, "Figma link should be found"),
        ('include_dod', True, "DoD should be included for release status"),
        ('figma_link', "https://www.figma.com/file/abc123", "Figma link should be extracted"),
        ('status', "PROD RELEASE QUEUE", "Status should be extracted")
    ]
    
    all_passed = True
    for field, expected, description in tests:
        result = context.get(field)
        passed = result == expected
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {description}: {status}")
        if not passed:
            print(f"     Expected: {expected}, Got: {result}")
            all_passed = False
    
    print(f"Analysis Context: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}\n")
    return all_passed

def main():
    """Run all tests"""
    print("🧪 GroomRoom Helper Methods Sanity Check\n")
    print("=" * 50)
    
    tests = [
        test_user_story_detection,
        test_figma_detection,
        test_dod_gate,
        test_analysis_context
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Helper methods are working correctly.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED! Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main()) 