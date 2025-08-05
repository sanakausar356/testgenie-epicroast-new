#!/usr/bin/env python3
"""
Simple script to test Jira field mappings
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

def main():
    """Main function to test Jira field mappings"""
    
    console.print("[bold blue]🔍 Testing Jira Field Mappings[/bold blue]")
    
    # Initialize Jira integration
    jira = JiraIntegration()
    
    if not jira.is_available():
        console.print("[red]❌ Jira integration is not available[/red]")
        return
    
    console.print("[green]✅ Jira integration is available[/green]")
    
    # Get field mapping information
    mapping_info = jira.get_field_mapping_info()
    
    console.print(f"\n[blue]Field Mapping Summary:[/blue]")
    console.print(f"- Total fields: {mapping_info['total_fields']}")
    console.print(f"- Custom fields: {mapping_info['custom_fields']}")
    console.print(f"- Standard fields: {mapping_info['standard_fields']}")
    
    # Show key custom fields
    key_fields = [
        'Test Scenarios', 'Story Points', 'Acceptance Criteria',
        'Agile Team', 'Architectural Solution', 'ADA Acceptance Criteria',
        'Performance Impact', 'Components', 'Brands'
    ]
    
    console.print(f"\n[blue]Key Custom Fields:[/blue]")
    
    table = Table(title="Custom Field Mappings")
    table.add_column("Field Name", style="cyan")
    table.add_column("Field ID", style="green")
    table.add_column("Status", style="yellow")
    
    for field_name in key_fields:
        field_id = jira.get_field_id_by_name(field_name)
        if field_id:
            table.add_row(field_name, field_id, "✅ Found")
        else:
            table.add_row(field_name, "N/A", "❌ Missing")
    
    console.print(table)
    
    # Show all custom fields (first 20)
    console.print(f"\n[blue]All Custom Fields (showing first 20):[/blue]")
    
    custom_fields_table = Table(title="All Custom Fields")
    custom_fields_table.add_column("Field Name", style="cyan")
    custom_fields_table.add_column("Field ID", style="green")
    
    custom_field_count = 0
    for field_name, field_info in mapping_info['mappings'].items():
        if field_info['custom']:
            custom_fields_table.add_row(field_name, field_info['id'])
            custom_field_count += 1
            if custom_field_count >= 20:
                break
    
    console.print(custom_fields_table)
    
    if custom_field_count >= 20:
        console.print(f"[yellow]... and {mapping_info['custom_fields'] - 20} more custom fields[/yellow]")

if __name__ == "__main__":
    main() 