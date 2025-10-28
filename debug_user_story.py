import sys; sys.path.insert(0, '.'); import os; os.environ['NO_COLOR'] = '1'
from jira_integration import JiraIntegration
from groomroom.core_no_scoring import GroomRoomNoScoring

j = JiraIntegration()
t = j.fetch_ticket('ODCD-34544')
g = GroomRoomNoScoring()
parsed = g.parse_jira_content(t)

with open('user_story_debug.txt', 'w', encoding='utf-8') as f:
    f.write(f"=== USER STORY DEBUG ===\n\n")
    f.write(f"parsed_data['fields']['user_story']:\n{parsed['fields'].get('user_story', 'EMPTY')}\n\n")
    
    # Check all custom fields
    fields = t.get('fields', {})
    f.write("=== ALL FIELDS WITH 'STORY' OR 'USER' IN NAME ===\n")
    for key, value in fields.items():
        if value and ('story' in str(key).lower() or 'user' in str(key).lower()):
            content = g._extract_text_from_field(value) if hasattr(g, '_extract_text_from_field') else str(value)
            f.write(f"{key}: {content[:200]}\n\n")
    
    # Check description
    desc = g._extract_text_from_field(fields.get('description', ''))
    f.write(f"=== DESCRIPTION (first 500 chars) ===\n{desc[:500]}\n\n")
    
    # Check if "As a user" exists anywhere
    if 'as a user' in desc.lower():
        f.write("✅ FOUND 'As a user' in description!\n")
        start = desc.lower().find('as a user')
        f.write(f"Snippet: {desc[start:start+200]}\n")

print("Check user_story_debug.txt")

