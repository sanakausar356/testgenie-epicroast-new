"""Get FULL rendered description for ODCD-34668"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from jira_integration import JiraIntegration

ticket = "ODCD-34668"
jira = JiraIntegration()
ticket_data = jira.fetch_ticket(ticket)

if ticket_data:
    rendered_desc = ticket_data.get('renderedFields', {}).get('description', '')
    
    print("\n" + "="*80)
    print("FULL RENDERED DESCRIPTION (ALL CONTENT):")
    print("="*80)
    print(rendered_desc)
    
    # Strip HTML and check
    import re
    text = re.sub(r'<[^>]+>', ' ', rendered_desc)
    text = re.sub(r'\s+', ' ', text).strip()
    
    print("\n" + "="*80)
    print("STRIPPED TEXT (First 1000 chars):")
    print("="*80)
    print(text[:1000])
    
    if 'User Story' in text:
        idx = text.index('User Story')
        print("\n✅ 'User Story' FOUND at position:", idx)
        print(f"\nContext (300 chars):\n{text[idx:idx+300]}")
    else:
        print("\n❌ 'User Story' NOT found")

