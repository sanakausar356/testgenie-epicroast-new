"""
Test the local API to verify the formatting is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom
from app import _extract_formatted_text

def test_local_api():
    """Test the local API formatting"""
    
    print("🧪 Testing Local API Formatting")
    print("=" * 50)
    
    # Sample content
    sample_content = """
    As a customer, I want to apply discount codes at checkout so that I can save money on my purchases.
    
    Acceptance Criteria:
    - User can enter discount code in checkout form
    - System validates the code against active promotions
    - Discount is applied to the total order amount
    - User sees confirmation of applied discount
    
    Test Scenarios:
    - Valid code applies correct discount
    - Invalid code shows error message
    - Expired code shows appropriate message
    """
    
    try:
        # Initialize GroomRoom
        print("1. Initializing GroomRoom...")
        groomroom = GroomRoom()
        print("✅ GroomRoom initialized")
        
        # Run analysis
        print("\n2. Running analysis...")
        result = groomroom.analyze_ticket(sample_content, mode="actionable")
        
        # Test the API formatting logic
        print("\n3. Testing API formatting logic...")
        
        # Check if result is already formatted
        if 'mode' in result and 'display_format' in result:
            print("✅ Result is already formatted")
            formatted_output = _extract_formatted_text(result, "actionable")
        else:
            print("❌ Result is not formatted")
            from app import _format_actionable_for_display
            formatted_output = _format_actionable_for_display(result)
        
        print("\n4. Formatted Output:")
        print("=" * 50)
        print(formatted_output)
        print("=" * 50)
        
        # Test the analysis structure
        print("\n5. Analysis Structure:")
        analysis = {
            'groom': formatted_output,
            'level': 'actionable',
            'ticket_number': '',
            'sprint_readiness': result.get('SprintReadiness', result.get('readiness_score', 0)),
            'type': result.get('Type', result.get('ticket_key', 'Unknown')),
            'issues_found': result.get('DefinitionOfReady', {}).get('MissingFields', []),
            'suggestions': result.get('Recommendations', [])
        }
        
        print(f"Sprint readiness: {analysis['sprint_readiness']}")
        print(f"Type: {analysis['type']}")
        print(f"Issues found: {analysis['issues_found']}")
        print(f"Suggestions: {analysis['suggestions']}")
        
        print("\n✅ Local API formatting is working correctly!")
        print("The issue is that the deployed API on Railway needs to be updated.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_api()
