"""
Core Epic Roast functionality
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
import openai
from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()

# Initialize Rich console for better output
console = Console()

class EpicRoast:
    """Main Epic Roast application class"""
    
    def __init__(self):
        self.client = None
        self.jira_integration = JiraIntegration()
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
    
    def get_ticket_content(self, input_file: Optional[str] = None, ticket_number: Optional[str] = None) -> str:
        """Get Jira ticket content from user input, file, or Jira ticket number"""
        
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
                console.print(f"[green]Loaded ticket content from {input_file}[/green]")
                return content
            except FileNotFoundError:
                console.print(f"[red]Error: File {input_file} not found[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]Error reading file: {e}[/red]")
                sys.exit(1)
        
        # Interactive input
        console.print(Panel.fit(
            "[bold red]🔥 Epic Roast[/bold red]\n"
            "Please paste your Jira ticket content below.\n"
            "Press Ctrl+D (Unix) or Ctrl+Z (Windows) when finished, or type 'END' on a new line.",
            title="Input Jira Ticket"
        ))
        
        session = PromptSession()
        lines = []
        
        try:
            while True:
                line = session.prompt(HTML("<ansired>🔥 </ansired>"))
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass
        
        if not lines:
            console.print("[red]No ticket content provided[/red]")
            sys.exit(1)
        
        return '\n'.join(lines)
    
    def get_roast_theme_prompt(self, theme: str, level: str) -> str:
        """Get the roast prompt based on theme and level"""
        themes = {
            "default": {
                "light": "You are a friendly code reviewer who gently points out issues in Jira tickets with constructive humor. Use clear headings and emojis to make your roast easy to read.",
                "savage": "You are a brutally honest senior developer who roasts Jira tickets with sharp wit and technical accuracy. Use bold headings and emojis to make your roast impactful and readable.",
                "extra_crispy": "You are a legendary tech lead who absolutely destroys poorly written Jira tickets with savage humor and zero mercy. Use dramatic headings and emojis to make your roast legendary."
            },
            "pirate": {
                "light": "You are a friendly pirate captain reviewing Jira tickets. Use pirate slang and nautical terms, but keep it gentle. Include pirate-themed emojis and clear headings.",
                "savage": "You are a fearsome pirate captain who roasts Jira tickets with salty language and pirate humor. Use pirate emojis and bold headings to make your roast memorable.",
                "extra_crispy": "You are the most feared pirate captain in the seven seas, absolutely destroying Jira tickets with legendary pirate roasts. Use dramatic pirate emojis and epic headings."
            },
            "shakespeare": {
                "light": "You are a gentle Shakespearean actor who critiques Jira tickets with elegant Elizabethan language and mild humor. Use theatrical headings and classic emojis.",
                "savage": "You are a dramatic Shakespearean actor who roasts Jira tickets with theatrical flair and witty insults. Use dramatic headings and theatrical emojis for maximum impact.",
                "extra_crispy": "You are the greatest Shakespearean actor who absolutely demolishes Jira tickets with the most dramatic and savage Elizabethan roasts. Use epic theatrical headings and dramatic emojis."
            },
            "genz": {
                "light": "You are a Gen Z developer who gently roasts Jira tickets using modern slang and emojis. Use lots of emojis and trendy headings to make it relatable.",
                "savage": "You are a savage Gen Z developer who absolutely roasts Jira tickets with the most current slang and brutal honesty. Use viral emojis and bold headings for maximum impact.",
                "extra_crispy": "You are the most savage Gen Z developer who absolutely destroys Jira tickets with the most brutal Gen Z roasts and viral slang. Use the most trending emojis and epic headings."
            }
        }
        
        return themes.get(theme, themes["default"]).get(level, themes["default"]["savage"])
    
    def generate_roast(self, ticket_content: str, theme: str = "default", level: str = "savage") -> str:
        """Generate a roast using Azure OpenAI"""
        theme_prompt = self.get_roast_theme_prompt(theme, level)
        
        prompt = f"""
{theme_prompt}

**Jira Ticket Content:**
{ticket_content}

**Instructions:**
1. Analyze the Jira ticket for common issues like vagueness, buzzwords, lack of clarity, missing details, etc.
2. Create a humorous but insightful roast that calls out these issues
3. Keep the roast entertaining and memorable
4. Include specific examples from the ticket
5. Make it feel personal and direct
6. Use the appropriate tone for the selected theme and level
7. Use HTML bold tags (<b>text</b>) for headings and important text to make them stand out
8. Use emojis to make the roast visually appealing and easy to read

**Output Format:**
🔥 <b>EPIC ROAST</b> 🔥

[Your roast here - be creative, funny, and insightful. Use emojis and <b>bold text</b> to make it engaging!]

📋 <b>Key Issues Found:</b>
- [Issue 1 with relevant emoji]
- [Issue 2 with relevant emoji]
- [Issue 3 with relevant emoji]

💡 <b>Suggestions for Improvement:</b>
- [Suggestion 1 with relevant emoji]
- [Suggestion 2 with relevant emoji]
- [Suggestion 3 with relevant emoji]

🎯 <b>Final Verdict:</b>
[One-liner summary of the roast with dramatic emoji]

Make this roast legendary! 🚀
"""
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[
                    {"role": "system", "content": theme_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]Error generating roast: {e}[/red]")
            return self.get_fallback_roast()
    
    def get_fallback_roast(self) -> str:
        """Return a fallback roast if API fails"""
        return """
🔥 <b>EPIC ROAST</b> 🔥

*The roast generator is taking a coffee break! ☕*

But seriously, if you're seeing this message, either:
1. Your Azure OpenAI setup needs some love
2. The API is having a moment
3. Your ticket is so bad it broke the AI

📋 <b>Quick Manual Roast:</b>
- If your ticket doesn't have clear acceptance criteria → That's a paddlin'
- If it's full of buzzwords → That's a paddlin'
- If it's vague AF → That's a paddlin'
- If it's missing context → That's a paddlin'

💡 <b>Suggestions:</b>
- Be specific
- Include examples
- Define success criteria
- Add context
- Stop using buzzwords

🎯 <b>Final Verdict:</b>
Your ticket needs work, but at least you're trying! 

Now go write a better ticket! 🚀
"""
    
    def save_roast(self, content: str, output_file: str):
        """Save roast to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[green]Roast saved to {output_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving file: {e}[/red]")
    
    def display_ascii_art(self):
        """Display ASCII art banner"""
        art = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ███████╗██████╗  ██████╗ ████████╗███████╗███████╗       ║
    ║    ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝██╔════╝       ║
    ║    █████╗  ██████╔╝██║   ██║   ██║   █████╗  ███████╗       ║
    ║    ██╔══╝  ██╔══██╗██║   ██║   ██║   ██╔══╝  ╚════██║       ║
    ║    ███████╗██║  ██║╚██████╔╝   ██║   ███████╗███████║       ║
    ║    ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝╚══════╝       ║
    ║                                                              ║
    ║                    🔥 EPIC ROAST 🔥                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        console.print(art, style="red") 