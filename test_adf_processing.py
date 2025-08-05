#!/usr/bin/env python3
"""
Test script to verify ADF (Atlassian Document Format) processing for custom fields
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jira_integration import JiraIntegration

load_dotenv()
console = Console()

def test_adf_processing():
    """Test ADF processing for custom fields"""
    console.print(Panel.fit("🧪 Testing ADF Processing", style="blue"))
    
    # Initialize Jira integration
    jira = JiraIntegration()
    if not jira.is_available():
        console.print("❌ Jira integration not available")
        return
    
    console.print("✅ Jira integration available")
    
    # Test with a known ticket that has custom fields
    test_ticket = "ODCD-33856"  # From the deployment logs
    
    console.print(f"🔍 Testing ticket: {test_ticket}")
    
    # Get ticket info
    ticket_info = jira.get_ticket_info(test_ticket)
    if not ticket_info:
        console.print("❌ Could not fetch ticket info")
        return
    
    console.print("✅ Ticket info fetched successfully")
    
    # Check custom fields
    custom_fields = ticket_info.get('custom_fields', {})
    console.print(f"📊 Found {len(custom_fields)} custom fields")
    
    for field_name, field_value in custom_fields.items():
        console.print(f"\n🔍 Field: {field_name}")
        console.print(f"   Type: {type(field_value).__name__}")
        
        if isinstance(field_value, dict):
            if 'type' in field_value and field_value.get('type') == 'doc':
                console.print("   📄 ADF Document detected")
                # Test ADF extraction
                adf_content = jira._extract_adf_content(field_value)
                console.print(f"   📝 Extracted content length: {len(adf_content)}")
                console.print(f"   📝 Content preview: {adf_content[:100]}...")
            else:
                console.print(f"   📋 Complex field: {list(field_value.keys())}")
        else:
            console.print(f"   📋 Simple field: {field_value}")
    
    # Test formatted output
    console.print("\n" + "="*50)
    console.print("📄 FORMATTED FOR ANALYSIS:")
    console.print("="*50)
    
    formatted_analysis = jira.format_ticket_for_analysis(ticket_info)
    console.print(formatted_analysis)
    
    console.print("\n" + "="*50)
    console.print("📄 FORMATTED FOR DISPLAY:")
    console.print("="*50)
    
    formatted_display = jira.format_ticket_for_display(ticket_info)
    console.print(formatted_display)

if __name__ == "__main__":
    test_adf_processing() 