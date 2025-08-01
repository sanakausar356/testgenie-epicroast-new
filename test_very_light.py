#!/usr/bin/env python3
"""
Test script to verify Very Light roast level functionality
"""

from epicroast.core import EpicRoast

def test_very_light_level():
    """Test the Very Light roast level"""
    
    # Test ticket content
    test_ticket = """
    Add "refund" endpoint to the API
    
    Description:
    We need to add a refund endpoint to handle customer refunds.
    
    Acceptance Criteria:
    - Endpoint should accept refund requests
    - Should return success/failure status
    """
    
    print("Testing Very Light roast level...")
    print("=" * 50)
    
    try:
        # Initialize Epic Roast
        epicroast = EpicRoast()
        
        # Test Very Light level
        print("Generating Very Light analysis...")
        very_light_result = epicroast.generate_roast(test_ticket, theme="default", level="very_light")
        
        print("\n✅ Very Light Result:")
        print("-" * 30)
        print(very_light_result)
        
        # Check for humor keywords
        humor_keywords = ['haha', 'lol', 'roast', 'burn', 'savage', 'destroy', 'legendary', 'epic', 'fire']
        found_humor = [word for word in humor_keywords if word.lower() in very_light_result.lower()]
        
        if found_humor:
            print(f"\n❌ WARNING: Found humor keywords in Very Light: {found_humor}")
        else:
            print("\n✅ SUCCESS: No humor keywords found in Very Light analysis")
        
        # Check for professional analysis keywords
        analysis_keywords = ['gap', 'missing', 'undefined', 'criteria', 'requirement', 'specify']
        found_analysis = [word for word in analysis_keywords if word.lower() in very_light_result.lower()]
        
        if found_analysis:
            print(f"✅ SUCCESS: Found analysis keywords: {found_analysis}")
        else:
            print("⚠️ WARNING: Few analysis keywords found")
        
        # Test comparison with Light level
        print("\n" + "=" * 50)
        print("Generating Light level for comparison...")
        light_result = epicroast.generate_roast(test_ticket, theme="default", level="light")
        
        print("\n✅ Light Result (first 200 chars):")
        print("-" * 30)
        print(light_result[:200] + "...")
        
        # Compare humor content
        light_humor = [word for word in humor_keywords if word.lower() in light_result.lower()]
        print(f"\nLight level humor keywords: {light_humor}")
        
        print("\n" + "=" * 50)
        print("✅ Very Light level test completed!")
        
    except Exception as e:
        print(f"❌ Error testing Very Light level: {e}")

if __name__ == "__main__":
    test_very_light_level() 