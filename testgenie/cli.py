"""
CLI interface for TestGenie
"""

import click
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from .core import TestGenie

# Initialize Rich console for better output
console = Console()

@click.command()
@click.option('--input', '-i', 'input_file', help='Input file containing acceptance criteria')
@click.option('--ticket', '-t', 'ticket_number', help='Jira ticket number (e.g., PROJ-123)')
@click.option('--export', '-e', 'output_file', help='Export results to file (supports .txt and .md)')
@click.option('--scenarios', '-s', multiple=True, 
              type=click.Choice(['positive', 'negative', 'edge']),
              default=['positive', 'negative', 'edge'],
              help='Types of scenarios to generate')
def main(input_file: Optional[str], ticket_number: Optional[str], output_file: Optional[str], scenarios: List[str]):
    """TestGenie - Generate test scenarios from acceptance criteria"""
    
    # Display banner
    console.print(Panel.fit(
        "[bold blue]🎯 TestGenie[/bold blue]\n"
        "[italic]AI-Powered Test Scenario Generator[/italic]",
        title="Welcome"
    ))
    
    # Initialize TestGenie
    testgenie = TestGenie()
    
    # Get acceptance criteria
    acceptance_criteria = testgenie.get_acceptance_criteria(input_file, ticket_number)
    
    # Display input summary
    console.print(f"\n[bold]Acceptance Criteria:[/bold]")
    console.print(Panel(acceptance_criteria, title="Input"))
    
    # Generate test scenarios
    console.print("\n[bold yellow]Generating test scenarios...[/bold yellow]")
    with console.status("[bold green]Processing with Azure OpenAI..."):
        result = testgenie.generate_test_scenarios(acceptance_criteria, list(scenarios))
    
    # Display results
    console.print(f"\n[bold]Generated Test Scenarios:[/bold]")
    console.print(Panel(result, title="Output"))
    
    # Save to file if requested
    if output_file:
        testgenie.save_output(result, output_file)
    
    console.print("\n[green]✅ TestGenie completed successfully![/green]")

if __name__ == '__main__':
    main() 