"""
CLI interface for Epic Roast
"""

import click
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from .core import EpicRoast

# Initialize Rich console for better output
console = Console()

@click.command()
@click.option('--input', '-i', 'input_file', help='Input file containing Jira ticket content')
@click.option('--ticket', '-t', 'ticket_number', help='Jira ticket number (e.g., PROJ-123)')
@click.option('--export', '-e', 'output_file', help='Export roast to file')
@click.option('--theme', '-th', 
              type=click.Choice(['default', 'pirate', 'shakespeare', 'genz']),
              default='default',
              help='Roast theme/style')
@click.option('--level', '-l',
              type=click.Choice(['very_light', 'light', 'savage', 'extra_crispy']),
              default='savage',
              help='Roast intensity level')
@click.option('--rerun', '-r', is_flag=True, help='Generate a new roast for the same ticket')
def main(input_file: Optional[str], ticket_number: Optional[str], output_file: Optional[str], theme: str, level: str, rerun: bool):
    """Epic Roast - AI-Powered Jira Ticket Roaster"""
    
    # Initialize Epic Roast
    epicroast = EpicRoast()
    
    # Display ASCII art banner
    epicroast.display_ascii_art()
    
    # Display theme and level info
    theme_emojis = {
        'default': '🎯',
        'pirate': '🏴‍☠️',
        'shakespeare': '🎭',
        'genz': '💅'
    }
    
    level_emojis = {
        'very_light': '📊',
        'light': '😊',
        'savage': '🔥',
        'extra_crispy': '💀'
    }
    
    console.print(f"\n[bold]Theme:[/bold] {theme_emojis.get(theme, '🎯')} {theme.title()}")
    console.print(f"[bold]Level:[/bold] {level_emojis.get(level, '🔥')} {level.replace('_', ' ').title()}")
    
    # Get ticket content
    ticket_content = epicroast.get_ticket_content(input_file, ticket_number)
    
    # Display ticket summary
    console.print(f"\n[bold]Ticket Content:[/bold]")
    console.print(Panel(ticket_content[:200] + "..." if len(ticket_content) > 200 else ticket_content, 
                       title="Jira Ticket"))
    
    # Generate roast
    console.print(f"\n[bold yellow]Generating {level} roast in {theme} style...[/bold yellow]")
    with console.status(f"[bold red]🔥 Roasting your ticket...[/bold red]"):
        roast = epicroast.generate_roast(ticket_content, theme, level)
    
    # Display roast
    console.print(f"\n[bold]🔥 EPIC ROAST 🔥[/bold]")
    console.print(Panel(roast, title="The Roast", border_style="red"))
    
    # Save to file if requested
    if output_file:
        epicroast.save_roast(roast, output_file)
    
    # Rerun option
    if rerun:
        console.print("\n[bold yellow]Generating another roast...[/bold yellow]")
        with console.status(f"[bold red]🔥 Roasting again...[/bold red]"):
            new_roast = epicroast.generate_roast(ticket_content, theme, level)
        
        console.print(f"\n[bold]🔥 EPIC ROAST (Rerun) 🔥[/bold]")
        console.print(Panel(new_roast, title="The Second Roast", border_style="red"))
        
        if output_file:
            epicroast.save_roast(new_roast, output_file.replace('.txt', '_rerun.txt'))
    
    console.print("\n[green]✅ Epic Roast completed![/green]")
    console.print("[italic]Remember: It's all in good fun! 😄[/italic]")

if __name__ == '__main__':
    main() 