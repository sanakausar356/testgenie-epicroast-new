"""Test with versionedRepresentations to get FULL description"""
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
url = f"{jira_url}/rest/api/3/issue/{ticket}?fields=description&expand=renderedFields,versionedRepresentations"

auth_string = f"{jira_username}:{jira_api_token}"
import base64
auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

headers = {
    'Authorization': auth_header,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print(f"\n{'='*80}")
print(f"FETCHING WITH versionedRepresentations")
print(f"{'='*80}\n")

try:
    response = requests.get(url, headers=headers, proxies={'http': None, 'https': None}, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check versionedRepresentations
        versioned = data.get('versionedRepresentations', {})
        print(f"\nversionedRepresentations keys: {list(versioned.keys())}")
        
        # Check raw description
        desc_raw = data.get('fields', {}).get('description', {})
        print(f"\n{'='*80}")
        print("RAW DESCRIPTION ADF (Full JSON):")
        print(f"{'='*80}\n")
        desc_json = json.dumps(desc_raw, indent=2)
        print(desc_json[:5000])  # First 5000 chars
        
        # Count content nodes
        content_nodes = desc_raw.get('content', [])
        print(f"\n{'='*80}")
        print(f"CONTENT NODES: {len(content_nodes)} total")
        print(f"{'='*80}\n")
        for i, node in enumerate(content_nodes):
            node_type = node.get('type', 'unknown')
            print(f"Node {i+1}: {node_type}")
            if node_type == 'paragraph' and 'content' in node:
                text_parts = [c.get('text', '') for c in node['content'] if c.get('type') == 'text']
                text = ' '.join(text_parts)[:100]
                print(f"  Text preview: {text}")
            elif node_type == 'heading' and 'content' in node:
                text_parts = [c.get('text', '') for c in node['content'] if c.get('type') == 'text']
                text = ' '.join(text_parts)
                print(f"  Heading text: {text}")
        
except Exception as e:
    print(f"ERROR: {e}")

