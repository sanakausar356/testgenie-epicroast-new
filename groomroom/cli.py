#!/usr/bin/env python3
"""
GroomRoom CLI - Command-line interface for concise Jira ticket refinement guidance
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groomroom.core import GroomRoom
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GroomRoom - Concise Jira ticket refinement guidance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  groomroom "As a user, I want to reset my password so that I can access my account"
  groomroom --file ticket.txt
  groomroom --ticket PROJ-123
        """
    )
    
    parser.add_argument(
        'content',
        nargs='?',
        help='Jira ticket content to analyze'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Read ticket content from file'
    )
    
    parser.add_argument(
        '--ticket', '-t',
        help='Jira ticket number to fetch and analyze'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for results (default: stdout)'
    )
    
    parser.add_argument(
        '--level', '-l',
        choices=['updated', 'strict', 'light', 'default', 'insight', 'deep_dive', 'actionable', 'summary'],
        default='default',
        help='Analysis level (default: default - Enhanced Groom Analysis format)'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.content and not args.file and not args.ticket:
        console.print("[red]Error: Must provide either content, file, or ticket number[/red]")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize GroomRoom
        console.print("[blue]Initializing GroomRoom...[/blue]")
        groomroom = GroomRoom()
        
        if not groomroom.client:
            console.print("[red]Error: GroomRoom not properly configured. Check environment variables.[/red]")
            sys.exit(1)
        
        # Get ticket content
        ticket_content = ""
        
        if args.content:
            ticket_content = args.content
        elif args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                console.print(f"[red]Error: File not found: {args.file}[/red]")
                sys.exit(1)
            ticket_content = file_path.read_text(encoding='utf-8')
        elif args.ticket:
            # Try to fetch from Jira if integration is available
            try:
                from jira_integration import JiraIntegration
                jira = JiraIntegration()
                if jira.is_available():
                    ticket_info = jira.get_ticket_info(args.ticket)
                    if ticket_info:
                        ticket_content = jira.format_ticket_for_analysis(ticket_info)
                    else:
                        console.print(f"[red]Error: Could not fetch ticket {args.ticket}[/red]")
                        sys.exit(1)
                else:
                    console.print(f"[yellow]Warning: Jira integration not available. Please provide ticket content manually.[/yellow]")
                    sys.exit(1)
            except ImportError:
                console.print(f"[yellow]Warning: Jira integration not available. Please provide ticket content manually.[/yellow]")
                sys.exit(1)
        
        if not ticket_content.strip():
            console.print("[red]Error: No ticket content to analyze[/red]")
            sys.exit(1)
        
        # Generate analysis
        console.print(f"[blue]Generating groom analysis with level: {args.level}...[/blue]")
        analysis = groomroom.generate_groom_analysis(ticket_content, level=args.level)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(analysis, encoding='utf-8')
            console.print(f"[green]Analysis saved to: {args.output}[/green]")
        else:
            # Display in console with rich formatting
            panel = Panel(
                Text(analysis, style="white"),
                title="[bold blue]Groom Analysis[/bold blue]",
                border_style="blue"
            )
            console.print(panel)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
