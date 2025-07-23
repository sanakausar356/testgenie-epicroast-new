#!/usr/bin/env python3
"""
Debug Jira API Response
"""

import os
import base64
import json
import requests
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

def debug_jira_api():
    """Debug Jira API response"""
    
    console.print("[bold blue]🔍 Debugging Jira API Response[/bold blue]")
    
    # Get credentials
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, jira_username, jira_api_token]):
        console.print("[red]Missing Jira credentials[/red]")
        return
    
    # Setup auth
    base_url = jira_url.rstrip('/')
    auth_string = f"{jira_username}:{jira_api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    auth_header = f"Basic {auth_b64}"
    
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    # Test ticket
    ticket_number = input("Enter ticket number to test (e.g., ODCD-33741): ").strip()
    if not ticket_number:
        console.print("[yellow]No ticket number provided[/yellow]")
        return
    
    endpoint = f"/rest/api/3/issue/{ticket_number.upper()}"
    url = f"{base_url}{endpoint}"
    
    console.print(f"\n[bold]Testing URL:[/bold] {url}")
    console.print(f"[bold]Headers:[/bold] Authorization: Basic ***")
    
    try:
        response = requests.get(url, headers=headers)
        
        console.print(f"\n[bold]Response Status:[/bold] {response.status_code}")
        console.print(f"[bold]Response Headers:[/bold] {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                console.print(f"\n[green]✅ JSON parsed successfully[/green]")
                console.print(f"[bold]Ticket Key:[/bold] {data.get('key', 'N/A')}")
                console.print(f"[bold]Has Fields:[/bold] {'fields' in data}")
                
                if 'fields' in data:
                    fields = data['fields']
                    console.print(f"[bold]Summary:[/bold] {fields.get('summary', 'N/A')}")
                    console.print(f"[bold]Status:[/bold] {fields.get('status', {}).get('name', 'N/A')}")
                    console.print(f"[bold]Type:[/bold] {fields.get('issuetype', {}).get('name', 'N/A')}")
                
            except json.JSONDecodeError as e:
                console.print(f"\n[red]❌ JSON decode error: {e}[/red]")
                console.print(f"[yellow]Response content (first 500 chars):[/yellow]")
                console.print(response.text[:500])
                
        else:
            console.print(f"\n[red]❌ HTTP Error: {response.status_code}[/red]")
            console.print(f"[yellow]Response content:[/yellow]")
            console.print(response.text)
            
    except Exception as e:
        console.print(f"\n[red]❌ Request failed: {e}[/red]")

if __name__ == "__main__":
    debug_jira_api() 