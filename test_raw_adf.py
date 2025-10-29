"""Check RAW ADF for full content including User Story"""
import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from jira_integration import JiraIntegration
from groomroom.core_no_scoring import GroomRoomNoScoring

ticket = "ODCD-34668"
jira = JiraIntegration()
ticket_data = jira.fetch_ticket(ticket)

if ticket_data:
    fields = ticket_data.get('fields', {})
    description_adf = fields.get('description', {})
    
    print("\n" + "="*80)
    print("RAW ADF STRUCTURE:")
    print("="*80)
    print(json.dumps(description_adf, indent=2)[:3000])
    
    # Extract text from ADF
    groom = GroomRoomNoScoring()
    extracted_text = groom._extract_from_adf(description_adf)
    
    print("\n" + "="*80)
    print("EXTRACTED TEXT FROM ADF (ALL CONTENT):")
    print("="*80)
    print(extracted_text[:2000])
    
    if 'User Story' in extracted_text:
        idx = extracted_text.index('User Story')
        print(f"\n✅ 'User Story' FOUND at position {idx}")
        print(f"\nContext (500 chars):\n{extracted_text[idx:idx+500]}")
    else:
        print("\n❌ 'User Story' NOT found in ADF extraction")

