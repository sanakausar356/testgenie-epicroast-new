"""Test fresh fetch with customfield_13287"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Force reimport
import importlib
if 'jira_integration' in sys.modules:
    del sys.modules['jira_integration']
if 'groomroom.core_no_scoring' in sys.modules:
    del sys.modules['groomroom.core_no_scoring']

from jira_integration import JiraIntegration
from groomroom.core_no_scoring import GroomRoomNoScoring

print("\n" + "="*80)
print("FRESH TEST WITH customfield_13287")
print("="*80 + "\n")

jira = JiraIntegration()
ticket_data = jira.fetch_ticket("ODCD-34668")

if ticket_data:
    fields = ticket_data.get('fields', {})
    
    print("Checking for customfield_13287...")
    cf_13287 = fields.get('customfield_13287')
    print(f"customfield_13287: {cf_13287}")
    
    if cf_13287:
        print("\n✅ customfield_13287 EXISTS in fetched data!")
        
        groom = GroomRoomNoScoring()
        extracted = groom._extract_text_from_field(cf_13287)
        print(f"\nExtracted text: {extracted}")
        
        # Now test extract_user_story
        parsed = groom.parse_jira_content(ticket_data)
        user_story = parsed['fields'].get('user_story', '')
        
        print(f"\n{'='*80}")
        print("USER STORY EXTRACTION RESULT:")
        print(f"{'='*80}")
        print(f"Length: {len(user_story)}")
        print(f"Content: {user_story}")
        
        if user_story:
            print("\n✅✅✅ USER STORY SUCCESSFULLY EXTRACTED!")
        else:
            print("\n❌ Still not extracted - checking why...")
            
            # Debug
            all_text = parsed.get('title', '') + ' ' + groom._extract_text_from_field(ticket_data.get('fields', {}).get('description'))
            manual_extract = groom.extract_user_story(fields, all_text)
            print(f"Manual extract result: {manual_extract}")
    else:
        print("\n❌ customfield_13287 NOT in fetched data")
        print("Fields requested might not include it")

