#!/usr/bin/env python3
"""
Test script for the updated Groom Room implementation
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom
from rich.console import Console

console = Console()

def test_updated_groomroom():
    """Test the updated Groom Room implementation"""
    
    # Sample Jira ticket content for testing
    sample_ticket = """
Title: Add ClearPay payment option for EMEA checkout
Description: As a customer in EMEA regions, I want to see ClearPay as a payment option during checkout so that I can use this preferred payment method.

Acceptance Criteria:
- ClearPay option appears in payment methods for EMEA brands
- ClearPay integration works with existing payment flow
- Error handling for failed ClearPay transactions

Components: Checkout, Payment
Brands: EMEA
Story Points: 5
    """
    
    try:
        console.print("[blue]Testing Updated Groom Room Implementation...[/blue]")
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        
        if not groomroom.client:
            console.print("[red]Error: GroomRoom not properly configured. Check environment variables.[/red]")
            return False
        
        # Test the updated system prompt
        console.print("[green]✅ Testing updated system prompt...[/green]")
        updated_prompt = groomroom.get_updated_groom_room_system_prompt()
        if "QA Refinement Assistant" in updated_prompt:
            console.print("[green]✅ Updated system prompt generated successfully[/green]")
        else:
            console.print("[red]❌ Updated system prompt not generated correctly[/red]")
            return False
        
        # Test the updated analysis
        console.print("[green]✅ Testing updated analysis generation...[/green]")
        analysis = groomroom.generate_updated_groom_analysis(sample_ticket)
        
        if analysis and len(analysis) > 100:
            console.print("[green]✅ Updated analysis generated successfully[/green]")
            console.print(f"[blue]Analysis length: {len(analysis)} characters[/blue]")
            
            # Check for expected sections
            expected_sections = [
                "Ticket Summary",
                "Acceptance Criteria",
                "Questions to Clarify",
                "High-Level Test Scenarios",
                "Observability & Evidence Plan",
                "Definition of Ready Gate"
            ]
            
            found_sections = []
            for section in expected_sections:
                if section in analysis:
                    found_sections.append(section)
            
            console.print(f"[blue]Found {len(found_sections)}/{len(expected_sections)} expected sections[/blue]")
            for section in found_sections:
                console.print(f"  ✅ {section}")
            
            for section in expected_sections:
                if section not in found_sections:
                    console.print(f"  ❌ {section} (missing)")
            
            # Display a preview of the analysis
            console.print("\n[bold blue]Analysis Preview:[/bold blue]")
            preview_lines = analysis.split('\n')[:20]
            for line in preview_lines:
                console.print(line)
            
            if len(analysis.split('\n')) > 20:
                console.print("...")
            
        else:
            console.print("[red]❌ Updated analysis generation failed[/red]")
            return False
        
        # Test the level-based analysis
        console.print("[green]✅ Testing level-based analysis...[/green]")
        level_analysis = groomroom.generate_groom_analysis(sample_ticket, level="updated")
        
        if level_analysis and len(level_analysis) > 100:
            console.print("[green]✅ Level-based analysis works correctly[/green]")
        else:
            console.print("[red]❌ Level-based analysis failed[/red]")
            return False
        
        console.print("\n[bold green]🎉 All tests passed! Updated Groom Room implementation is working correctly.[/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Test failed with error: {e}[/red]")
        console.print(f"[red]Error type: {type(e).__name__}[/red]")
        return False

if __name__ == '__main__':
    success = test_updated_groomroom()
    sys.exit(0 if success else 1)
