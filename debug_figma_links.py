"""Debug script to check Figma link extraction from Jira"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from jira_integration import JiraIntegration

# Initialize Jira
jira = JiraIntegration()

# Fetch ticket
ticket_id = 'ODCD-34544'
print(f"\n=== Fetching {ticket_id} ===\n")

try:
    ticket_data = jira.fetch_ticket(ticket_id)
    
    # Check renderedFields for HTML version
    rendered = ticket_data.get('renderedFields', {})
    if rendered:
        print("=== Checking renderedFields (HTML) ===")
        for key, value in rendered.items():
            if value and 'figma' in str(value).lower():
                print(f"\n✅ Found 'figma' in renderedFields.{key}:")
                val_str = str(value)
                idx = val_str.lower().find('figma')
                print(f"Context: ...{val_str[max(0,idx-100):min(len(val_str),idx+200)]}...\n")
    
    # Print description
    desc = ticket_data.get('fields', {}).get('description', '')
    print(f"Description (first 500 chars):\n{str(desc)[:500]}\n")
    
    # Search for figma in description
    desc_str = str(desc).lower()
    if 'figma' in desc_str:
        print("✅ 'figma' found in description!\n")
        # Find context around figma
        idx = desc_str.find('figma')
        print(f"Context: ...{str(desc)[max(0,idx-50):min(len(str(desc)),idx+100)]}...\n")
    else:
        print("❌ 'figma' NOT found in description\n")
    
    # Check all custom fields
    print("=== Checking Custom Fields ===")
    fields = ticket_data.get('fields', {})
    for key, value in fields.items():
        if key.startswith('customfield'):
            val_str = str(value).lower()
            if 'figma' in val_str:
                print(f"\n✅ Found 'figma' in {key}:")
                print(f"Value: {str(value)[:200]}")
    
    # Check acceptance criteria
    ac = fields.get('customfield_13281', '') or fields.get('customfield_13383', '')
    if ac:
        ac_str = str(ac).lower()
        if 'figma' in ac_str:
            print(f"\n✅ Found 'figma' in Acceptance Criteria:")
            idx = ac_str.find('figma')
            print(f"Context: ...{str(ac)[max(0,idx-50):min(len(str(ac)),idx+100)]}...")
    
    # Check test scenarios in detail
    test_scenarios = fields.get('customfield_13286', '')
    if test_scenarios:
        print(f"\n=== Test Scenarios Field (customfield_13286) ===")
        print(f"Full content:\n{str(test_scenarios)[:1000]}")
        
        # Look for URL patterns in ADF
        import json
        if isinstance(test_scenarios, dict) and test_scenarios.get('type') == 'doc':
            print("\n=== Searching ADF for URLs ===")
            # Recursively search for URLs in ADF
            def find_urls_in_adf(node, depth=0):
                if isinstance(node, dict):
                    if node.get('type') == 'text' and node.get('marks'):
                        for mark in node.get('marks', []):
                            if mark.get('type') == 'link':
                                url = mark.get('attrs', {}).get('href', '')
                                if 'figma' in url.lower():
                                    print(f"{'  '*depth}✅ FIGMA LINK FOUND: {url}")
                                    print(f"{'  '*depth}   Text: {node.get('text', '')}")
                    for key, value in node.items():
                        find_urls_in_adf(value, depth+1)
                elif isinstance(node, list):
                    for item in node:
                        find_urls_in_adf(item, depth+1)
            
            find_urls_in_adf(test_scenarios)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

