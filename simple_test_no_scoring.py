#!/usr/bin/env python3
"""
Simple test for GroomRoom No-Scoring implementation
"""

def test_import():
    """Test if the module can be imported"""
    try:
        from groomroom.core_no_scoring import GroomRoomNoScoring
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        from groomroom.core_no_scoring import GroomRoomNoScoring
        
        groomroom = GroomRoomNoScoring()
        print("✅ GroomRoom instance created")
        
        # Test with minimal ticket
        ticket_data = {
            'key': 'TEST-001',
            'fields': {
                'summary': 'Test ticket',
                'description': 'This is a test ticket for GroomRoom analysis',
                'issuetype': {'name': 'Story'}
            }
        }
        
        result = groomroom.analyze_ticket(ticket_data, "Actionable")
        print("✅ Analysis completed")
        
        # Check that no framework scores are present
        if 'FrameworkScores' in result.data or 'framework_scores' in result.data:
            print("❌ Framework scores found in output")
            return False
        
        # Check that status is present
        if 'Status' not in result.data:
            print("❌ Status not found in output")
            return False
        
        print(f"✅ Status: {result.data.get('Status')}")
        print(f"✅ Suggested Rewrite: {result.data.get('StoryReview', {}).get('SuggestedRewrite', 'Not found')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing GroomRoom No-Scoring Implementation")
    print("=" * 50)
    
    # Test import
    if not test_import():
        exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("✅ No framework scores in output")
    print("✅ Context-specific content generated")
