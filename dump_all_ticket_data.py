"""Dump ALL fields from ODCD-34668 to find User Story"""
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

# Get ALL fields
url = f"{jira_url}/rest/api/3/issue/{ticket}"

auth_string = f"{jira_username}:{jira_api_token}"
import base64
auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

headers = {
    'Authorization': auth_header,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print(f"\n{'='*80}")
print(f"DUMPING ALL FIELDS FOR {ticket}")
print(f"{'='*80}\n")

try:
    response = requests.get(url, headers=headers, proxies={'http': None, 'https': None}, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        fields = data.get('fields', {})
        
        print(f"\nTotal fields: {len(fields)}")
        print(f"\n{'='*80}")
        print("SEARCHING FOR 'User Story' or 'As a user' CONTENT:")
        print(f"{'='*80}\n")
        
        found_count = 0
        for key, value in fields.items():
            if value:
                value_str = str(value).lower()
                if 'user story' in value_str or 'as a user' in value_str or 'paypal window to open immediately' in value_str:
                    found_count += 1
                    print(f"\n✅ FOUND in field: {key}")
                    print(f"Type: {type(value)}")
                    if isinstance(value, str):
                        print(f"Value (first 500 chars): {value[:500]}")
                    elif isinstance(value, dict):
                        print(f"Value (dict): {json.dumps(value, indent=2)[:500]}")
                    else:
                        print(f"Value: {value}")
                    print("-" * 80)
        
        if found_count == 0:
            print("\n❌ NO FIELD CONTAINS 'User Story' or 'As a user' or the PayPal text!")
            print("\nThis definitively proves the content is NOT in Jira's database.")
            print("It might be:")
            print("1. Cached in your browser")
            print("2. Draft/unsaved content")
            print("3. From a different ticket")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

