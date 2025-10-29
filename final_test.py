"""Final test with all fixes"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Fresh imports
for mod in list(sys.modules.keys()):
    if 'jira' in mod or 'groom' in mod:
        del sys.modules[mod]

from jira_integration import JiraIntegration
from groomroom.core_no_scoring import GroomRoomNoScoring

print("\n" + "="*80)
print("FINAL TEST - ODCD-34668")
print("="*80 + "\n")

jira = JiraIntegration()
ticket_data = jira.fetch_ticket("ODCD-34668")

if ticket_data:
    print("✅ Ticket fetched")
    
    # Check what we got
    fields = ticket_data.get('fields')
    rendered = ticket_data.get('renderedFields', {})
    
    print(f"fields type: {type(fields)}")
    print(f"renderedFields keys: {list(rendered.keys())[:10]}")
    
    # Now test GroomRoom parsing
    print("\n" + "="*80)
    print("TESTING GROOMROOM PARSING:")
    print("="*80 + "\n")
    
    groom = GroomRoomNoScoring()
    parsed = groom.parse_jira_content(ticket_data)
    
    user_story = parsed['fields'].get('user_story', '')
    
    print(f"User Story length: {len(user_story)}")
    print(f"User Story content:\n{user_story}\n")
    
    if user_story and len(user_story) > 20:
        print("="*80)
        print("✅✅✅ SUCCESS! USER STORY EXTRACTED!")
        print("="*80)
    else:
        print("="*80)
        print("❌ Still not extracted")
        print("="*80)

