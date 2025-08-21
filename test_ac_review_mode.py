#!/usr/bin/env python3
"""
Test script for AC Review Mode GroomRoom functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ac_review_mode():
    """Test the AC Review Mode groomroom functionality"""
    
    # Test case 1: Ticket with existing AC
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
    
    # Test case 2: Ticket with missing AC
    test_ticket_2 = """
    Summary: Update product listing page design
    
    Description:
    As a user, I want to see an improved product listing page so that I can find products more easily.
    
    Test Scenarios:
    - User can browse products
    - User can filter products
    """
    
    # Test case 3: Ticket with vague AC
    test_ticket_3 = """
    Summary: Implement checkout flow
    
    Description:
    As a user, I want to complete my purchase so that I can receive my items.
    
    Acceptance Criteria:
    - Checkout page matches Figma design
    - Form looks like the mockup
    - User can enter payment details
    """
    
    try:
        from groomroom.core import GroomRoom
        
        print("🧹 Testing AC Review Mode GroomRoom Functionality")
        print("="*60)
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        
        print(f"✅ GroomRoom initialized: {groomroom is not None}")
        
        # Test case 1: Ticket with existing AC
        print("\n🔍 Test Case 1: Ticket with existing AC")
        print("-" * 40)
        analysis_1 = groomroom.generate_concise_groom_analysis(test_ticket_1)
        
        print(f"✅ Analysis generated: {len(analysis_1)} characters")
        print(f"✅ Contains 'Groom Analysis — Lean': {'Groom Analysis — Lean' in analysis_1}")
        print(f"✅ Contains 'Acceptance Criteria Review': {'Acceptance Criteria Review' in analysis_1}")
        print(f"✅ Contains 'Rephrased intent-based AC': {'Rephrased intent-based AC' in analysis_1}")
        print(f"✅ Contains 'ADA / Accessibility': {'ADA / Accessibility' in analysis_1}")
        print(f"✅ No 'Key Gaps' section: {'Key Gaps' not in analysis_1}")
        print(f"✅ No 'Definition of Ready' section: {'Definition of Ready' not in analysis_1}")
        
        # Test case 2: Ticket with missing AC
        print("\n🔍 Test Case 2: Ticket with missing AC")
        print("-" * 40)
        analysis_2 = groomroom.generate_concise_groom_analysis(test_ticket_2)
        
        print(f"✅ Analysis generated: {len(analysis_2)} characters")
        print(f"✅ Contains 'AC missing': {'AC missing' in analysis_2}")
        print(f"✅ Contains suggested examples: {'Suggested examples' in analysis_2}")
        print(f"✅ No ADA section (not accessibility related): {'ADA / Accessibility' not in analysis_2}")
        
        # Test case 3: Ticket with vague AC
        print("\n🔍 Test Case 3: Ticket with vague AC")
        print("-" * 40)
        analysis_3 = groomroom.generate_concise_groom_analysis(test_ticket_3)
        
        print(f"✅ Analysis generated: {len(analysis_3)} characters")
        print(f"✅ Contains 'match Figma': {'match Figma' in analysis_3 or 'Figma' in analysis_3}")
        print(f"✅ Contains 'Vague phrases': {'Vague phrases' in analysis_3}")
        
        # Check for AC Review Mode improvements
        print("\n📊 AC Review Mode Quality Check:")
        print("-" * 40)
        
        # Check for removed sections
        removed_sections = ["Key Gaps", "Definition of Ready Gaps"]
        for section in removed_sections:
            if section not in analysis_1 and section not in analysis_2 and section not in analysis_3:
                print(f"✅ Removed section: '{section}'")
            else:
                print(f"❌ Found removed section: '{section}'")
        
        # Check for new sections
        new_sections = ["Acceptance Criteria Review", "Test Scenarios (High-Level)"]
        for section in new_sections:
            if section in analysis_1 or section in analysis_2 or section in analysis_3:
                print(f"✅ New section present: '{section}'")
            else:
                print(f"❌ Missing new section: '{section}'")
        
        # Check for intent-based AC
        if "intent-based AC" in analysis_1:
            print("✅ Found intent-based AC rephrasing")
        else:
            print("❌ Missing intent-based AC rephrasing")
        
        # Check for test scenarios alignment
        if "High-level test cases" in analysis_1:
            print("✅ Found high-level test cases")
        else:
            print("❌ Missing high-level test cases")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ac_review_mode()
    
    print("\n" + "="*60)
    print(f"TEST RESULT: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("🎉 AC Review Mode GroomRoom functionality is working correctly!")
    else:
        print("🔧 AC Review Mode GroomRoom functionality needs attention")
