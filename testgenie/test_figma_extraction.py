"""Test script to check Figma link extraction from Jira"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jira_integration import JiraIntegration
from groomroom.core_no_scoring import GroomRoomNoScoring

def test_figma_extraction():
    print("\n=== Testing Figma Link Extraction ===\n")
    
    # Initialize Jira
    jira = JiraIntegration()
    
    # Fetch ticket
    ticket_number = "ODCD-34544"
    print(f"Fetching ticket {ticket_number}...")
    ticket_data = jira.fetch_ticket(ticket_number)
    
    if not ticket_data:
        print("❌ Failed to fetch ticket")
        return
    
    print("✅ Ticket fetched successfully\n")
    
    # Check description field
    desc = ticket_data.get('fields', {}).get('description')
    print(f"Description type: {type(desc)}")
    print(f"Description preview: {str(desc)[:200]}...\n")
    
    # Check for Figma links in description
    if isinstance(desc, dict):
        print("Description is ADF format (dict)")
        print(f"ADF keys: {desc.keys()}")
        print(f"ADF content sample: {json.dumps(desc, indent=2)[:500]}...\n")
    
    # Check Acceptance Criteria field
    ac_field = ticket_data.get('fields', {}).get('customfield_13383')
    print(f"\n=== Acceptance Criteria Field ===")
    print(f"AC field type: {type(ac_field)}")
    if ac_field:
        print(f"AC field preview: {str(ac_field)[:500]}...")
        if isinstance(ac_field, dict):
            print(f"\nAC ADF sample: {json.dumps(ac_field, indent=2)[:1000]}...")
    else:
        print("AC field is None or empty")
    
    # Dump ALL fields to find Figma references
    print(f"\n=== Searching ALL Fields for Figma ===")
    fields_data = ticket_data.get('fields', {})
    for field_key, field_value in fields_data.items():
        if field_value:
            field_str = str(field_value).lower()
            if 'figma' in field_str or 'animation should match' in field_str:
                print(f"\n✅ Found 'figma' or 'animation' in field: {field_key}")
                print(f"   Type: {type(field_value)}")
                print(f"   Preview: {str(field_value)[:300]}...")
    
    # Check renderedFields (HTML-rendered version)
    print(f"\n=== Checking renderedFields for Figma Links ===")
    rendered_fields = ticket_data.get('renderedFields', {})
    for field_key, field_value in rendered_fields.items():
        if field_value and isinstance(field_value, str):
            if 'figma' in field_value.lower():
                print(f"\n✅ Found 'figma' in RENDERED field: {field_key}")
                print(f"   Full HTML content:")
                print(field_value)
                print("\n   Extracting Figma links from HTML...")
                # Extract using the jira _html_to_text method
                text, links = jira._html_to_text(field_value)
                print(f"   Links found: {links}")
    
    # Initialize GroomRoom
    groomroom = GroomRoomNoScoring()
    
    # Parse content
    parsed_data = groomroom.parse_jira_content(ticket_data)
    
    # Check extracted links
    print(f"\n=== Extracted Figma Links ===")
    print(f"Total links found: {len(parsed_data['design_links'])}")
    
    for idx, link in enumerate(parsed_data['design_links']):
        print(f"\nLink {idx + 1}:")
        print(f"  URL: {link.url}")
        print(f"  Anchor Text: {link.anchor_text}")
        print(f"  File Key: {link.file_key}")
    
    if not parsed_data['design_links']:
        print("\n❌ No Figma links extracted!")
        print("\nLet's try manual ADF extraction...")
        
        # Try extracting directly from description
        if desc:
            links = groomroom.extract_figma_from_adf_structure(desc)
            print(f"Manual ADF extraction from description: {len(links)} links")
            for link in links:
                print(f"  - {link.url} ({link.anchor_text})")
        
        # Try extracting from AC field
        if ac_field:
            links = groomroom.extract_figma_from_adf_structure(ac_field)
            print(f"\nManual ADF extraction from AC field: {len(links)} links")
            for link in links:
                print(f"  - {link.url} ({link.anchor_text})")
        
        # Try extracting from Test Scenarios field (customfield_13286)
        test_scenarios_field = ticket_data.get('fields', {}).get('customfield_13286')
        if test_scenarios_field:
            print(f"\n=== Test Scenarios Field (customfield_13286) ===")
            print(f"Full content: {json.dumps(test_scenarios_field, indent=2)[:2000]}...")
            links = groomroom.extract_figma_from_adf_structure(test_scenarios_field)
            print(f"\nManual ADF extraction from Test Scenarios: {len(links)} links")
            for link in links:
                print(f"  ✅ {link.url} (anchor: '{link.anchor_text}')")

if __name__ == "__main__":
    test_figma_extraction()

