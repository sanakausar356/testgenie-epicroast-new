"""
Core TestGenie functionality
"""

import os
import sys
from typing import List, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
import openai
try:
    from jira_integration import JiraIntegration
except ImportError:
    # Handle import error for Railway deployment
    JiraIntegration = None

# Load environment variables
load_dotenv()

# Initialize Rich console for better output
console = Console()

class TestGenie:
    """Main TestGenie application class"""
    
    def __init__(self):
        self.client = None
        self.jira_integration = JiraIntegration() if JiraIntegration else None
        self.setup_azure_openai()
    
    def setup_azure_openai(self):
        """Initialize Azure OpenAI client"""
        try:
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            
            if not all([endpoint, api_key, deployment_name]):
                console.print("[red]Error: Missing Azure OpenAI configuration in .env file[/red]")
                console.print("Please ensure you have the following variables set:")
                console.print("- AZURE_OPENAI_ENDPOINT")
                console.print("- AZURE_OPENAI_API_KEY")
                console.print("- AZURE_OPENAI_DEPLOYMENT_NAME")
                sys.exit(1)
            
            self.client = openai.AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
            
        except Exception as e:
            console.print(f"[red]Error setting up Azure OpenAI: {e}[/red]")
            sys.exit(1)
    
    def get_acceptance_criteria(self, input_file: Optional[str] = None, ticket_number: Optional[str] = None) -> str:
        """Get acceptance criteria from user input, file, or Jira ticket"""
        
        # Check if Jira integration is available and ticket number is provided
        if ticket_number and self.jira_integration.is_available():
            console.print(f"[blue]Fetching ticket {ticket_number} from Jira...[/blue]")
            ticket_info = self.jira_integration.get_ticket_info(ticket_number)
            
            if ticket_info:
                console.print(f"[green]✅ Successfully fetched ticket {ticket_info['key']}[/green]")
                
                # Display ticket summary
                console.print(f"\n[bold]Ticket Summary:[/bold]")
                console.print(Panel(
                    f"**{ticket_info['key']}**: {ticket_info['summary']}\n"
                    f"Status: {ticket_info['status']} | Priority: {ticket_info['priority']} | Type: {ticket_info['issue_type']}",
                    title="Jira Ticket Info"
                ))
                
                # Return formatted ticket for analysis
                return self.jira_integration.format_ticket_for_analysis(ticket_info)
            else:
                console.print(f"[red]Failed to fetch ticket {ticket_number}[/red]")
                console.print("[yellow]Falling back to manual input...[/yellow]")
        
        # File input
        if input_file:
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                console.print(f"[green]Loaded acceptance criteria from {input_file}[/green]")
                return content
            except FileNotFoundError:
                console.print(f"[red]Error: File {input_file} not found[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]Error reading file: {e}[/red]")
                sys.exit(1)
        
        # Interactive input
        console.print(Panel.fit(
            "[bold blue]TestGenie[/bold blue]\n"
            "Please paste your acceptance criteria below.\n"
            "Press Ctrl+D (Unix) or Ctrl+Z (Windows) when finished, or type 'END' on a new line.",
            title="Input Acceptance Criteria"
        ))
        
        session = PromptSession()
        lines = []
        
        try:
            while True:
                line = session.prompt(HTML("<ansiblue>→ </ansiblue>"))
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass
        
        if not lines:
            console.print("[red]No acceptance criteria provided[/red]")
            sys.exit(1)
        
        return '\n'.join(lines)
    
    def generate_test_scenarios(self, acceptance_criteria: str, scenario_types: List[str]) -> str:
        """Generate test scenarios using Azure OpenAI with updated template"""
        scenario_type_text = ", ".join(scenario_types) if scenario_types else "positive, negative, edge"
        
        prompt = f"""
You are a senior QA engineer tasked with creating comprehensive test scenarios and test cases based on acceptance criteria.

**Acceptance Criteria:**
{acceptance_criteria}

**Requirements:**
1. Generate at least 3 high-level test scenarios
2. For each scenario, provide 2-3 specific test cases
3. Include {scenario_type_text} scenarios
4. Focus on both happy path and edge cases
5. Make test cases specific and actionable

**Output Format:**
# Test Scenarios for [Feature Name]

## Test Scenarios

### Scenario 1: [Scenario Name]
**Objective:** [What this scenario tests]

#### Test Cases:
1. **Test Case 1.1:** [Test case description]
   - **Preconditions:** [What needs to be set up]
   - **Steps:** [Step-by-step test steps]
   - **Expected Result:** [Expected outcome]

2. **Test Case 1.2:** [Test case description]
   - **Preconditions:** [What needs to be set up]
   - **Steps:** [Step-by-step test steps]
   - **Expected Result:** [Expected outcome]

### Scenario 2: [Scenario Name]
[Continue format...]

## Edge Cases

### Edge Case 1: [Edge case description]
**Description:** [What makes this an edge case]
**Test Steps:** [How to test this edge case]
**Expected Result:** [Expected outcome]

### Edge Case 2: [Edge case description]
[Continue format...]

## Cross Browser/Device Testing

### Browser Compatibility
- **Chrome:** [Required/Not Required] - [Reason]
- **Firefox:** [Required/Not Required] - [Reason]
- **Safari:** [Required/Not Required] - [Reason]
- **Edge:** [Required/Not Required] - [Reason]

### Device Testing
- **Desktop:** [Required/Not Required] - [Reason]
- **Tablet:** [Required/Not Required] - [Reason]
- **Mobile:** [Required/Not Required] - [Reason]

### Responsive Design Testing
- **Viewport Sizes:** [List specific viewport sizes to test]
- **Orientation:** [Portrait/Landscape testing requirements]

Please provide comprehensive, well-structured test scenarios that cover all aspects of the acceptance criteria.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[
                    {"role": "system", "content": "You are a senior QA engineer with expertise in test case design and acceptance criteria analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]Error generating test scenarios: {e}[/red]")
            return self.get_fallback_message()
    
    def get_fallback_message(self) -> str:
        """Return a simplified fallback message for poorly written input"""
        return """
# Test Scenarios - Simplified Response

The acceptance criteria provided may need clarification. Here's a simplified template:

## Test Scenarios

### Scenario 1: Basic Functionality
**Objective:** Verify core feature works as expected

#### Test Cases:
1. **Test Case 1.1:** Happy path test
   - **Preconditions:** System is ready
   - **Steps:** Perform basic operation
   - **Expected Result:** Feature works correctly

## Edge Cases

### Edge Case 1: Invalid Input
**Description:** Test with invalid data
**Test Steps:** Enter invalid input
**Expected Result:** Proper error handling

## Cross Browser/Device Testing

### Browser Compatibility
- **Chrome:** Required - Primary browser
- **Firefox:** Required - Secondary browser
- **Safari:** Not Required - Limited usage
- **Edge:** Not Required - Limited usage

### Device Testing
- **Desktop:** Required - Primary platform
- **Tablet:** Not Required - Limited usage
- **Mobile:** Not Required - Limited usage

Please provide clearer acceptance criteria with specific requirements and try again.
"""
    
    def save_output(self, content: str, output_file: str):
        """Save output to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[green]Output saved to {output_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving file: {e}[/red]") 