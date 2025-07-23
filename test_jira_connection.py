#!/usr/bin/env python3
"""
Test Jira Connection Script
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

def test_jira_connection():
    """Test Jira connection and show available information"""
    
    console.print(Panel.fit(
        "[bold blue]🔗 Jira Connection Test[/bold blue]\n"
        "Testing your Jira integration setup...",
        title="Jira Test"
    ))
    
    # Check environment variables
    console.print("\n[bold]Checking environment variables:[/bold]")
    
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    
    if jira_url:
        console.print(f"✅ JIRA_URL: {jira_url}")
    else:
        console.print("❌ JIRA_URL: Not set")
    
    if jira_username:
        console.print(f"✅ JIRA_USERNAME: {jira_username}")
    else:
        console.print("❌ JIRA_USERNAME: Not set")
    
    if jira_api_token:
        console.print(f"✅ JIRA_API_TOKEN: {'*' * (len(jira_api_token) - 4) + jira_api_token[-4:]}")
    else:
        console.print("❌ JIRA_API_TOKEN: Not set")
    
    # Test connection
    console.print("\n[bold]Testing Jira connection:[/bold]")
    
    try:
        jira = JiraIntegration()
        
        if jira.is_available():
            console.print("✅ Jira connection successful!")
            
            # Test with a sample ticket (you can change this)
            console.print("\n[bold]Testing ticket fetch (optional):[/bold]")
            console.print("Enter a ticket number to test (e.g., PROJ-123) or press Enter to skip:")
            
            ticket_input = input("Ticket number: ").strip()
            
            if ticket_input:
                console.print(f"\n[blue]Fetching ticket {ticket_input}...[/blue]")
                ticket_info = jira.get_ticket_info(ticket_input)
                
                if ticket_info:
                    console.print(f"✅ Successfully fetched ticket {ticket_info['key']}")
                    console.print(f"Summary: {ticket_info['summary']}")
                    console.print(f"Status: {ticket_info['status']}")
                    console.print(f"Type: {ticket_info['issue_type']}")
                    console.print(f"Comments: {len(ticket_info['comments'])}")
                else:
                    console.print(f"❌ Could not fetch ticket {ticket_input}")
                    console.print("This might be normal if the ticket doesn't exist")
            else:
                console.print("Skipping ticket fetch test")
            
            console.print("\n🎉 Jira integration is working correctly!")
            console.print("You can now use TestGenie and Epic Roast with Jira tickets!")
            
        else:
            console.print("❌ Jira connection failed")
            console.print("Please check your credentials in the .env file")
            
    except Exception as e:
        console.print(f"❌ Error testing Jira connection: {e}")
        console.print("Please check your credentials and try again")

if __name__ == "__main__":
    test_jira_connection() 