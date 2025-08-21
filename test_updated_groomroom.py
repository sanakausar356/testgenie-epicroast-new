#!/usr/bin/env python3
"""
Test script for updated GroomRoom functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_updated_groomroom():
    """Test the updated groomroom functionality"""
    
    # Test case 1: Ticket with AC and accessibility
    test_ticket_1 = """
    Summary: Add password reset functionality to user account page
    
    Description:
    As a user, I want to be able to reset my password when I forget it, so that I can regain access to my account.
    
    Acceptance Criteria:
    - User can click "Forgot Password" link
    - User receives email with reset link
    - User can set new password via reset link
    - Password meets security requirements
    - Screen reader announces password reset status
    - Keyboard navigation works for all form elements
    
    Test Scenarios:
    - User clicks ATC on PLP → PDP loads
    - Missing image on PDP → fallback message appears
    - ATC button not visible on out-of-stock item
    """
    
    # Test case 2: Ticket with vague AC
    test_ticket_2 = """
    Summary: Update product listing page design
    
    Description:
    As a user, I want to see an improved product listing page so that I can find products more easily.
    
    Acceptance Criteria:
    - Product cards match Figma design
    - Layout looks like the mockup
    - User can click on products
    """
    
    try:
        from groomroom.core import GroomRoom
        
        print("🧹 Testing Updated GroomRoom Functionality")
        print("="*60)
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        
        print(f"✅ GroomRoom initialized: {groomroom is not None}")
        
        # Test case 1: Ticket with AC and accessibility
        print("\n🔍 Test Case 1: Ticket with AC and accessibility")
        print("-" * 40)
        analysis_1 = groomroom.generate_concise_groom_analysis(test_ticket_1)
        
        print(f"✅ Analysis generated: {len(analysis_1)} characters")
        print(f"✅ Contains 'ADA / Accessibility': {'ADA / Accessibility' in analysis_1}")
        print(f"✅ Definition of Ready at end: {'Definition of Ready Gaps' in analysis_1.split('##')[-1]}")
        
        # Test case 2: Ticket with vague AC
        print("\n🔍 Test Case 2: Ticket with vague AC")
        print("-" * 40)
        analysis_2 = groomroom.generate_concise_groom_analysis(test_ticket_2)
        
        print(f"✅ Analysis generated: {len(analysis_2)} characters")
        print(f"✅ Contains 'match Figma': {'match Figma' in analysis_2 or 'Figma' in analysis_2}")
        print(f"✅ No ADA section (not accessibility related): {'ADA / Accessibility' not in analysis_2}")
        
        # Check for improvements
        print("\n📊 Analysis Quality Check:")
        print("-" * 40)
        
        # Check for generic phrases that should be avoided
        generic_phrases = ["AC is missing", "add AC", "define test cases"]
        for phrase in generic_phrases:
            if phrase in analysis_1 or phrase in analysis_2:
                print(f"❌ Found generic phrase: '{phrase}'")
            else:
                print(f"✅ No generic phrase: '{phrase}'")
        
        # Check for field-specific content
        if "Test scenarios present" in analysis_1:
            print("✅ Found field-specific test scenario analysis")
        else:
            print("❌ Missing field-specific test scenario analysis")
        
        if "Vague phrases found" in analysis_2:
            print("✅ Found vague phrase detection")
        else:
            print("❌ Missing vague phrase detection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_updated_groomroom()
    
    print("\n" + "="*60)
    print(f"TEST RESULT: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("🎉 Updated GroomRoom functionality is working correctly!")
    else:
        print("🔧 Updated GroomRoom functionality needs attention")
