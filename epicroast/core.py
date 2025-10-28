"""
Core Epic Roast functionality
"""

import os
import sys
import re
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
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

class EpicRoast:
    """Main Epic Roast application class"""
    
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
                                "very_light": """You are an analytical assistant. For the 'Very Light' roast level, do NOT crack jokes or use any roast language. Instead, scan the ticket and highlight every missing or unclear piece of information in concise bullet points. 
                
**CRITICAL: Analyze against these frameworks from the presentation:**
1. **R-O-I Framework**: Check for Role, Objective, Insight elements
2. **I-N-V-E-S-T Framework**: Check for Independent, Negotiable, Valuable, Estimable, Small, Testable elements  
3. **A-C-C-E-P-T Criteria**: Check for Action, Condition, Criteria, Expected Result, Pass-Fail, Traceable elements
4. **3C Model**: Check for Card → Conversation → Confirmation elements
5. **User Story Template**: Check for "As a [user], I want [goal], so that [benefit]" format

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements:**
- **User Story**: Must define business value goal, follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Must state intent (what), not solution (how), have actionable results, include edge cases beyond happy path
- **Testing Steps**: Must include Positive, Error, and Negative test scenarios
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

At the end, suggest 3-5 actionable gaps to fill. Use markdown headings (# for main, ## for sub) and professional tone.""",
                "light": "You are a friendly code reviewer who gently points out issues in Jira tickets with constructive humor. Use markdown headings (# for main, ## for sub) and emojis to make your roast easy to read.",
                "savage": "You are a brutally honest senior developer who roasts Jira tickets with sharp wit and technical accuracy. Use markdown headings (# for main, ## for sub) and emojis to make your roast impactful and readable.",
                "extra_crispy": "You are a legendary tech lead who absolutely destroys poorly written Jira tickets with savage humor and zero mercy. Use markdown headings (# for main, ## for sub) and emojis to make your roast legendary."
            },
            "pirate": {
                "very_light": "You are a professional navigator analyzing Jira tickets. For the 'Very Light' level, provide analytical gap analysis with zero humor or pirate language. Scan the ticket and highlight missing information in concise bullet points. Suggest 3-5 actionable improvements. Use markdown headings (# for main, ## for sub) and professional tone.",
                "light": "You are a friendly pirate captain reviewing Jira tickets. Use pirate slang and nautical terms, but keep it gentle. Include pirate-themed emojis and markdown headings (# for main, ## for sub).",
                "savage": "You are a fearsome pirate captain who roasts Jira tickets with salty language and pirate humor. Use pirate emojis and markdown headings (# for main, ## for sub) to make your roast memorable.",
                "extra_crispy": "You are the most feared pirate captain in the seven seas, absolutely destroying Jira tickets with legendary pirate roasts. Use dramatic pirate emojis and markdown headings (# for main, ## for sub)."
            },
            "shakespeare": {
                "very_light": "You are a scholarly analyst examining Jira tickets. For the 'Very Light' level, provide analytical gap analysis with zero humor or theatrical language. Scan the ticket and highlight missing information in concise bullet points. Suggest 3-5 actionable improvements. Use markdown headings (# for main, ## for sub) and professional tone.",
                "light": "You are a gentle Shakespearean actor who critiques Jira tickets with elegant Elizabethan language and mild humor. Use markdown headings (# for main, ## for sub) and classic emojis.",
                "savage": "You are a dramatic Shakespearean actor who roasts Jira tickets with theatrical flair and witty insults. Use markdown headings (# for main, ## for sub) and theatrical emojis for maximum impact.",
                "extra_crispy": "You are the greatest Shakespearean actor who absolutely demolishes Jira tickets with the most dramatic and savage Elizabethan roasts. Use markdown headings (# for main, ## for sub) and dramatic emojis."
            },
            "genz": {
                "very_light": "You are a professional analyst reviewing Jira tickets. For the 'Very Light' level, provide analytical gap analysis with zero humor or Gen Z slang. Scan the ticket and highlight missing information in concise bullet points. Suggest 3-5 actionable improvements. Use markdown headings (# for main, ## for sub) and professional tone.",
                "light": "You are a Gen Z developer who gently roasts Jira tickets using modern slang and emojis. Use lots of emojis and markdown headings (# for main, ## for sub) to make it relatable.",
                "savage": "You are a savage Gen Z developer who absolutely roasts Jira tickets with the most current slang and brutal honesty. Use viral emojis and markdown headings (# for main, ## for sub) for maximum impact.",
                "extra_crispy": "You are the most savage Gen Z developer who absolutely destroys Jira tickets with the most brutal Gen Z roasts and viral slang. Use the most trending emojis and markdown headings (# for main, ## for sub)."
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

**CRITICAL FORMATTING RULES:**
- Use ONLY markdown formatting, NEVER HTML tags
- Use **text** for bold emphasis (NOT <b>text</b>)
- Use *text* for italic emphasis (NOT <i>text</i>)
- Use # for main headings, ## for subheadings
- Use - for bullet points
- NEVER use HTML tags like <b>, </b>, <i>, </i>, etc.

**Instructions:**
1. Analyze the Jira ticket for common issues like vagueness, buzzwords, lack of clarity, missing details, etc.
2. Create a humorous but insightful roast that calls out these issues
3. Keep the roast entertaining and memorable
4. Include specific examples from the ticket
5. Make it feel personal and direct
6. Use the appropriate tone for the selected theme and level
7. Use emojis to make the roast visually appealing and easy to read
8. Use ONLY markdown formatting - **bold** for emphasis, *italic* for emphasis, # for headings
9. NEVER use HTML tags in your response

**Output Format for Very Light Level:**
# 📊 GAP ANALYSIS

[Groom analysis highlighting missing information and gaps in the ticket]

## 🔍 Gaps Found:
- **Missing acceptance criteria** for [specific scenario]
- **Undefined edge cases** such as [example]
- **No performance expectations** mentioned
- **Missing data requirements** for [specific field]

## 💡 Actionable Next Steps:
1. **Add acceptance criteria** for [specific scenario]
2. **Define edge cases** for [specific condition]
3. **Specify performance metrics** and expectations
4. **Document data requirements** for [specific field]

## 🎯 Summary:
[Professional summary of key areas needing attention]

**Output Format for Other Levels:**
# 🔥 EPIC ROAST 🔥

[Your roast here - be creative, funny, and insightful. Use emojis and **bold text** to make it engaging!]

## 📋 Key Issues Found:
- **Issue 1** with relevant emoji
- **Issue 2** with relevant emoji  
- **Issue 3** with relevant emoji

## 💡 Suggestions for Improvement:
- **Suggestion 1** with relevant emoji
- **Suggestion 2** with relevant emoji
- **Suggestion 3** with relevant emoji

## 🎯 Final Verdict:
[One-liner summary of the roast with dramatic emoji]

Make this roast legendary! 🚀

**REMEMBER: Use markdown formatting only, no HTML tags!**
"""
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[
                    {"role": "system", "content": theme_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            roast_content = response.choices[0].message.content
            
            # Clean up any HTML tags that might have been generated
            # Convert HTML bold/strong tags to markdown bold
            roast_content = re.sub(r'<b>(.*?)</b>', r'**\1**', roast_content)
            roast_content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', roast_content)
            # Convert HTML italic/em tags to markdown italic
            roast_content = re.sub(r'<i>(.*?)</i>', r'*\1*', roast_content)
            roast_content = re.sub(r'<em>(.*?)</em>', r'*\1*', roast_content)
            # Additional cleanup for any remaining HTML tags
            roast_content = re.sub(r'<[^>]*>', '', roast_content)
            
            # Validate Very Light level content
            if level == "very_light":
                roast_content = self._validate_very_light_content(roast_content, ticket_content)
            
            return roast_content
            
        except Exception as e:
            console.print(f"[red]Error generating roast: {e}[/red]")
            return self.get_fallback_roast()
    
    def _validate_very_light_content(self, content: str, ticket_content: str) -> str:
        """Validate and potentially re-prompt for Very Light level content"""
        # Define humor-related keywords that should not appear in Very Light
        humor_keywords = [
            'haha', 'lol', 'roast', 'burn', 'savage', 'destroy', 'legendary',
            'epic', 'fire', 'spicy', 'hot', 'crispy', 'roasted', 'burned',
            'destroyed', 'annihilated', 'obliterated', 'rekt', 'owned'
        ]
        
        # Check for humor keywords
        content_lower = content.lower()
        found_humor = [word for word in humor_keywords if word in content_lower]
        
        if found_humor:
            console.print(f"[yellow]Warning: Found humor keywords in Very Light content: {found_humor}[/yellow]")
            console.print("[yellow]Re-prompting for groom analysis...[/yellow]")
            
            # Re-prompt with stricter instructions
            re_prompt = f"""
You are an analytical assistant. This is for the 'Very Light' roast level - NO humor, NO jokes, NO roast language.

**Jira Ticket Content:**
{ticket_content}

**CRITICAL: Very Light Level Requirements:**
- Provide ONLY professional gap analysis
- Use bullet points to highlight missing information
- Suggest 3-5 actionable improvements
- NO humor, jokes, or roast language
- Professional tone only

**Output Format:**
# 📊 GAP ANALYSIS

[Groom analysis of missing information]

## 🔍 Gaps Found:
- **Missing acceptance criteria** for [specific scenario]
- **Undefined edge cases** such as [example]
- **No performance expectations** mentioned

## 💡 Actionable Next Steps:
1. **Add acceptance criteria** for [specific scenario]
2. **Define edge cases** for [specific condition]
3. **Specify performance metrics**

## 🎯 Summary:
[Professional summary of key areas needing attention]

**REMEMBER: This is Very Light level - NO humor, only groom analysis!**
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                    messages=[
                        {"role": "system", "content": "You are an analytical assistant. Provide professional gap analysis with zero humor."},
                        {"role": "user", "content": re_prompt}
                    ],
                    max_tokens=1500,
                    # Removed temperature parameter as o4-mini model doesn't support it
                )
                
                new_content = response.choices[0].message.content
                
                # Clean up HTML tags in the new content
                new_content = re.sub(r'<b>(.*?)</b>', r'**\1**', new_content)
                new_content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', new_content)
                new_content = re.sub(r'<i>(.*?)</i>', r'*\1*', new_content)
                new_content = re.sub(r'<em>(.*?)</em>', r'*\1*', new_content)
                new_content = re.sub(r'<[^>]*>', '', new_content)
                
                return new_content
                
            except Exception as e:
                console.print(f"[red]Error in re-prompting: {e}[/red]")
                return content  # Return original content if re-prompting fails
        
        return content
    
    def get_fallback_roast(self) -> str:
        """Return a fallback roast if API fails"""
        return """
# 🔥 EPIC ROAST 🔥

*The roast generator is taking a coffee break! ☕*

But seriously, if you're seeing this message, either:
1. Your Azure OpenAI setup needs some love
2. The API is having a moment
3. Your ticket is so bad it broke the AI

## 📋 Quick Manual Roast:
- **If your ticket doesn't have clear acceptance criteria** → That's a paddlin'
- **If it's full of buzzwords** → That's a paddlin'
- **If it's vague AF** → That's a paddlin'
- **If it's missing context** → That's a paddlin'

## 💡 Suggestions:
- **Be specific**
- **Include examples**
- **Define success criteria**
- **Add context**
- **Stop using buzzwords**

## 🎯 Final Verdict:
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