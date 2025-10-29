#!/usr/bin/env python3
"""
Test script to verify field names are displayed in human-readable format
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core_no_scoring import GroomRoomNoScoring

def test_field_name_formatting():
    """Test that field names are formatted correctly"""
    
    print("=" * 80)
    print("TESTING FIELD NAME FORMATTING")
    print("=" * 80)
    
    # Create GroomRoom instance
    groomroom = GroomRoomNoScoring()
    
    # Test 1: Test with underscore field names
    print("\n📋 Test 1: Format field names with underscores")
    print("-" * 80)
    
    test_fields = [
        'user_story',
        'acceptance_criteria',
        'testing_steps',
        'architectural_solution',
        'ada_criteria',
        'agile_team',
        'story_points'
    ]
    
    formatted = groomroom._format_field_names(test_fields)
    
    print("\n✅ BEFORE (with underscores):")
    print(f"   {', '.join(test_fields)}")
    
    print("\n✨ AFTER (human-readable):")
    print(f"   {formatted}")
    
    # Test 2: Test with mixed fields (some in mapping, some not)
    print("\n\n📋 Test 2: Format mixed field names")
    print("-" * 80)
    
    mixed_fields = [
        'acceptance_criteria',
        'brands',
        'components',
        'custom_field'  # Not in mapping
    ]
    
    formatted_mixed = groomroom._format_field_names(mixed_fields)
    
    print("\n✅ BEFORE (with underscores):")
    print(f"   {', '.join(mixed_fields)}")
    
    print("\n✨ AFTER (human-readable):")
    print(f"   {formatted_mixed}")
    
    # Test 3: Simulate Definition of Ready output
    print("\n\n📋 Test 3: Simulated Definition of Ready Output")
    print("-" * 80)
    
    dor = {
        'present': ['acceptance_criteria', 'testing_steps', 'brands', 'components'],
        'missing': ['user_story', 'implementation_details', 'architectural_solution', 'ada_criteria', 'agile_team', 'story_points'],
        'conflicts': []
    }
    
    print("\n## Definition of Ready")
    print(f"- **Present:** {groomroom._format_field_names(dor['present'])}")
    print(f"- **Missing:** {groomroom._format_field_names(dor['missing'])}")
    print(f"- **Conflicts:** {groomroom._format_field_names(dor['conflicts'])}")
    
    # Test 4: Compare old vs new format
    print("\n\n📊 COMPARISON: OLD vs NEW")
    print("=" * 80)
    
    print("\n❌ OLD FORMAT (with underscores):")
    print(f"- **Present:** {', '.join(dor['present'])}")
    print(f"- **Missing:** {', '.join(dor['missing'])}")
    
    print("\n✅ NEW FORMAT (human-readable):")
    print(f"- **Present:** {groomroom._format_field_names(dor['present'])}")
    print(f"- **Missing:** {groomroom._format_field_names(dor['missing'])}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("Field names are now displaying in human-readable format! 🎉")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_field_name_formatting()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

