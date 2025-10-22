"""
Debug GroomRoom analysis to understand why it returns 0% readiness
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def debug_groomroom_analysis():
    """Debug the GroomRoom analysis step by step"""
    
    print("🔍 Debugging GroomRoom Analysis")
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
        
        # Test the analysis
        print("\n2. Running analysis...")
        result = groomroom.analyze_ticket(sample_content, mode="actionable")
        
        print("\n3. Analysis Result:")
        print(f"Type: {result.get('Type', 'Unknown')}")
        print(f"SprintReadiness: {result.get('SprintReadiness', 0)}")
        print(f"TicketKey: {result.get('TicketKey', 'Unknown')}")
        
        # Check if it's already formatted
        print(f"Mode: {result.get('mode', 'Not formatted')}")
        print(f"Display format: {result.get('display_format', 'Not formatted')}")
        
        # Test the API formatting function
        print("\n4. Testing API formatting...")
        from app import _format_actionable_for_display
        formatted_output = _format_actionable_for_display(result)
        print("Formatted output:")
        print(formatted_output)
        
        # Check the issue data extraction
        print("\n4. Debugging issue data extraction...")
        jira_issue = {
            'key': 'PASTED-CONTENT',
            'fields': {
                'summary': 'Pasted Content Analysis',
                'description': sample_content,
                'issuetype': {'name': 'Unknown'},
                'status': {'name': 'Unknown'},
                'priority': {'name': 'None'},
                'assignee': None,
                'reporter': None,
                'created': '',
                'updated': '',
                'project': {'name': 'Unknown'},
                'labels': [],
                'components': []
            }
        }
        
        issue_data = groomroom.extract_jira_fields(jira_issue)
        print(f"Issue data keys: {list(issue_data.keys())}")
        print(f"Description length: {len(issue_data.get('description', ''))}")
        print(f"Acceptance criteria count: {len(issue_data.get('acceptance_criteria', []))}")
        print(f"Test scenarios count: {len(issue_data.get('test_scenarios', []))}")
        
        # Check DoR analysis
        print("\n5. Debugging DoR analysis...")
        dor_analysis = groomroom.analyze_dor_requirements(issue_data)
        print(f"DoR coverage: {dor_analysis.get('coverage_percentage', 0)}%")
        print(f"Missing elements: {dor_analysis.get('missing_elements', [])}")
        print(f"Present elements: {dor_analysis.get('present_elements', [])}")
        
        # Check story analysis
        print("\n6. Debugging story analysis...")
        story_analysis = groomroom.analyze_story(issue_data)
        print(f"Story analysis keys: {list(story_analysis.keys())}")
        print(f"Has clear structure: {story_analysis.get('has_clear_structure', False)}")
        print(f"Story quality score: {story_analysis.get('story_quality_score', 0)}")
        
        # Check card type detection
        print("\n7. Debugging card type detection...")
        card_type_analysis = groomroom.detect_card_type(issue_data)
        print(f"Card type: {card_type_analysis.get('type_name', 'Unknown')}")
        print(f"Confidence: {card_type_analysis.get('confidence', 0)}")
        
        print("\n8. Full result structure:")
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"  {key}: {type(value)} with {len(value)} items")
            else:
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_groomroom_analysis()
