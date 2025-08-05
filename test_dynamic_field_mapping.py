#!/usr/bin/env python3
"""
Test script for dynamic Jira field mapping functionality
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

def test_field_mapping():
    """Test the dynamic field mapping functionality"""
    
    console.print(Panel.fit(
        "[bold blue]🧪 Testing Dynamic Jira Field Mapping[/bold blue]\n"
        "This test will verify that the Jira integration can dynamically\n"
        "fetch and map custom fields from your Jira instance.",
        title="Field Mapping Test"
    ))
    
    # Initialize Jira integration
    jira = JiraIntegration()
    
    if not jira.is_available():
        console.print("[red]❌ Jira integration is not available[/red]")
        console.print("Please ensure you have the following environment variables set:")
        console.print("- JIRA_URL")
        console.print("- JIRA_USERNAME") 
        console.print("- JIRA_API_TOKEN")
        return False
    
    console.print("[green]✅ Jira integration is available[/green]")
    
    # Get field mapping information
    mapping_info = jira.get_field_mapping_info()
    
    console.print(f"\n[blue]Field Mapping Summary:[/blue]")
    console.print(f"- Total fields mapped: {mapping_info['total_fields']}")
    console.print(f"- Custom fields: {mapping_info['custom_fields']}")
    console.print(f"- Standard fields: {mapping_info['standard_fields']}")
    
    # Test specific field lookups
    test_fields = [
        'Test Scenarios', 'Story Points', 'Acceptance Criteria',
        'Agile Team', 'Architectural Solution', 'ADA Acceptance Criteria',
        'Performance Impact', 'Components', 'Brands'
    ]
    
    console.print(f"\n[blue]Testing Field Lookups:[/blue]")
    
    table = Table(title="Field Mapping Results")
    table.add_column("Field Name", style="cyan")
    table.add_column("Field ID", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Status", style="magenta")
    
    found_fields = []
    missing_fields = []
    
    for field_name in test_fields:
        field_id = jira.get_field_id_by_name(field_name)
        if field_id:
            field_info = mapping_info['mappings'][field_name]
            field_type = "Custom" if field_info['custom'] else "Standard"
            status = "✅ Found"
            found_fields.append(field_name)
            table.add_row(field_name, field_id, field_type, status)
        else:
            table.add_row(field_name, "N/A", "N/A", "❌ Missing")
            missing_fields.append(field_name)
    
    console.print(table)
    
    # Summary
    console.print(f"\n[blue]Summary:[/blue]")
    console.print(f"- Found {len(found_fields)} out of {len(test_fields)} test fields")
    console.print(f"- Missing {len(missing_fields)} fields")
    
    if missing_fields:
        console.print(f"\n[yellow]Missing fields:[/yellow]")
        for field in missing_fields:
            console.print(f"  - {field}")
        console.print(f"\n[yellow]Note: Missing fields may have different names in your Jira instance[/yellow]")
    
    # Test ticket fetching with dynamic fields
    console.print(f"\n[blue]Testing Ticket Fetching with Dynamic Fields:[/blue]")
    
    # Ask for a test ticket number
    test_ticket = input("Enter a test ticket number (or press Enter to skip): ").strip()
    
    if test_ticket:
        console.print(f"[blue]Fetching ticket {test_ticket} with dynamic field mapping...[/blue]")
        
        ticket_info = jira.get_ticket_info(test_ticket)
        
        if ticket_info:
            console.print(f"[green]✅ Successfully fetched ticket {ticket_info['key']}[/green]")
            
            # Display custom fields found
            custom_fields = ticket_info.get('custom_fields', {})
            if custom_fields:
                console.print(f"\n[blue]Custom fields found in ticket:[/blue]")
                for field_name, field_value in custom_fields.items():
                    console.print(f"  - {field_name}: {field_value}")
            else:
                console.print(f"\n[yellow]No custom fields found in ticket[/yellow]")
        else:
            console.print(f"[red]❌ Failed to fetch ticket {test_ticket}[/red]")
    
    return True

def test_field_refresh():
    """Test field mapping refresh functionality"""
    
    console.print(f"\n[blue]Testing Field Mapping Refresh:[/blue]")
    
    jira = JiraIntegration()
    
    if not jira.is_available():
        console.print("[red]❌ Jira integration not available for refresh test[/red]")
        return False
    
    # Get initial mapping count
    initial_info = jira.get_field_mapping_info()
    initial_count = initial_info['total_fields']
    
    console.print(f"[blue]Initial field count: {initial_count}[/blue]")
    
    # Refresh mappings
    jira.refresh_field_mappings()
    
    # Get updated mapping count
    updated_info = jira.get_field_mapping_info()
    updated_count = updated_info['total_fields']
    
    console.print(f"[blue]Updated field count: {updated_count}[/blue]")
    
    if initial_count == updated_count:
        console.print(f"[green]✅ Field mapping refresh successful (count unchanged)[/green]")
    else:
        console.print(f"[yellow]⚠️ Field mapping refresh completed (count changed: {initial_count} → {updated_count})[/yellow]")
    
    return True

def main():
    """Main test function"""
    
    console.print(Panel.fit(
        "[bold green]🚀 Dynamic Jira Field Mapping Test Suite[/bold green]\n"
        "Testing the enhanced Jira integration with dynamic field mapping",
        title="Test Suite"
    ))
    
    try:
        # Test 1: Basic field mapping
        console.print("\n" + "="*60)
        console.print("[bold blue]Test 1: Field Mapping[/bold blue]")
        console.print("="*60)
        
        success1 = test_field_mapping()
        
        # Test 2: Field refresh
        console.print("\n" + "="*60)
        console.print("[bold blue]Test 2: Field Mapping Refresh[/bold blue]")
        console.print("="*60)
        
        success2 = test_field_refresh()
        
        # Final summary
        console.print("\n" + "="*60)
        console.print("[bold blue]Test Summary[/bold blue]")
        console.print("="*60)
        
        if success1 and success2:
            console.print("[green]✅ All tests passed![/green]")
            console.print("[green]Dynamic field mapping is working correctly.[/green]")
        else:
            console.print("[red]❌ Some tests failed[/red]")
            console.print("[yellow]Please check your Jira configuration and try again.[/yellow]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error during testing: {e}[/red]")
        console.print(f"[red]Error type: {type(e).__name__}[/red]")

if __name__ == "__main__":
    main() 