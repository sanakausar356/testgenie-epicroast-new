"""Debug the actual API response"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

jira_url = os.getenv('JIRA_URL')
jira_username = os.getenv('JIRA_USERNAME')
jira_api_token = os.getenv('JIRA_API_TOKEN')

ticket = "ODCD-34668"

# Exact same call as in jira_integration.py
fields_to_request = "summary,description,status,priority,assignee,reporter,issuetype,project,labels,components,created,updated,comments,customfield_13287,customfield_13286,customfield_10117,customfield_13389,customfield_13383,customfield_13597,customfield_13298,customfield_13598,customfield_13649,customfield_13482"

url = f"{jira_url}/rest/api/3/issue/{ticket}?fields={fields_to_request}&expand=renderedFields,names,transitions,changelog,versionedRepresentations"

auth_string = f"{jira_username}:{jira_api_token}"
import base64
auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

headers = {
    'Authorization': auth_header,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print(f"\nFull URL: {url[:200]}...")
print(f"\nMaking request...")

try:
    response = requests.get(url, headers=headers, proxies={'http': None, 'https': None}, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\nTop-level keys: {list(data.keys())}")
        
        fields = data.get('fields')
        print(f"\nfields type: {type(fields)}")
        print(f"fields is None: {fields is None}")
        print(f"fields is empty dict: {fields == {}}")
        
        if fields:
            print(f"\nfields keys (first 20): {list(fields.keys())[:20]}")
            
            # Check for customfield_13287
            if 'customfield_13287' in fields:
                print(f"\n✅ customfield_13287 EXISTS!")
                print(f"Value: {fields['customfield_13287']}")
            else:
                print(f"\n❌ customfield_13287 NOT in fields")
                
                # Show which customfields ARE present
                custom_fields = [k for k in fields.keys() if k.startswith('customfield_132')]
                print(f"\nCustomfields starting with 'customfield_132': {custom_fields}")
        else:
            print(f"\n❌ No fields in response!")
            print(f"\nFull response:\n{json.dumps(data, indent=2)[:2000]}")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

