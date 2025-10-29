"""Test ALL possible ways to get description"""
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

# Try API v2 (might have more complete data)
url_v2 = f"{jira_url}/rest/api/2/issue/{ticket}?fields=description&expand=renderedFields"

auth_string = f"{jira_username}:{jira_api_token}"
import base64
auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

headers = {
    'Authorization': auth_header,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print(f"\n{'='*80}")
print(f"TRYING API V2 (might have full content)")
print(f"{'='*80}\n")

try:
    response = requests.get(url_v2, headers=headers, proxies={'http': None, 'https': None}, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Get raw description
        desc = data.get('fields', {}).get('description')
        
        print(f"\n{'='*80}")
        print(f"DESCRIPTION TYPE: {type(desc)}")
        print(f"{'='*80}\n")
        
        if isinstance(desc, str):
            print(f"String description (first 2000 chars):")
            print(desc[:2000])
            if 'User Story' in desc:
                idx = desc.index('User Story')
                print(f"\n✅ 'User Story' FOUND at position {idx}")
                print(f"\nContext:\n{desc[idx:idx+500]}")
        elif isinstance(desc, dict):
            print(f"ADF description:")
            print(json.dumps(desc, indent=2)[:3000])
            content = desc.get('content', [])
            print(f"\nContent nodes: {len(content)}")
            for i, node in enumerate(content):
                print(f"  {i+1}. {node.get('type', 'unknown')}")
        else:
            print(f"Description: {desc}")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

