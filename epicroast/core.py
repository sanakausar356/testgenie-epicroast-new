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
            # Disable proxy for Azure OpenAI (like Jira integration does)
            # This prevents proxy connection errors
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)
            os.environ.pop('ALL_PROXY', None)
            os.environ.pop('all_proxy', None)
            
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            
            if not all([endpoint, api_key, deployment_name]):
                console.print("[red]Error: Missing Azure OpenAI configuration in .env file[/red]")
                console.print("Please ensure you have the following variables set:")
                console.print("- AZURE_OPENAI_ENDPOINT")
                console.print("- AZURE_OPENAI_API_KEY")
                console.print("- AZURE_OPENAI_DEPLOYMENT_NAME")
                self.client = None
                return
            
            # Clean endpoint (remove trailing slash if present)
            endpoint = endpoint.rstrip('/')
            
            # Initialize Azure OpenAI client with timeout settings
            # Proxy is already disabled via environment variables above
            # httpx (used by openai) will respect NO_PROXY if set
            os.environ['NO_PROXY'] = '*'
            
            self.client = openai.AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version,
                timeout=30.0,  # 30 second timeout
                max_retries=2  # Retry up to 2 times
            )
            
            # Log endpoint info (masked for security)
            endpoint_display = endpoint[:30] + "..." if len(endpoint) > 30 else endpoint
            console.print(f"[blue]Azure OpenAI endpoint: {endpoint_display}[/blue]")
            console.print(f"[blue]Deployment: {deployment_name}[/blue]")
            console.print(f"[blue]API Version: {api_version}[/blue]")
            
        except Exception as e:
            console.print(f"[red]Error setting up Azure OpenAI: {e}[/red]")
            self.client = None
    
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
                "light": """You are a WARM, SUPPORTIVE, and FRIENDLY code reviewer. For the 'Light' roast level, your personality is:

**CRITICAL: Light Level Personality:**
- Be GENTLE and CONSTRUCTIVE - frame issues as helpful suggestions, not harsh criticisms
- Use a WARM, ENCOURAGING tone - like a friendly mentor giving feedback
- Be COLLABORATIVE - make it feel like you're working together to improve the ticket
- Use LIGHT HUMOR - gentle, friendly jokes that make people smile, not cringe
- Be SUPPORTIVE - acknowledge what's good, then suggest improvements
- Focus on HELPING, not roasting - your goal is to guide, not destroy

**CRITICAL: Light Level Language:**
- Use phrases like "Consider adding...", "It might be helpful to...", "You could improve by..."
- Avoid harsh words like "terrible", "awful", "horrible", "disaster"
- Use friendly emojis: 😊, 👍, 💡, ✨, 🌟, 🎯
- Frame feedback as "suggestions" and "improvements", not "problems" and "failures"

**CRITICAL: Light Level Approach:**
- Start with something positive about the ticket
- Then gently suggest areas for improvement
- End with encouragement and next steps
- Make the developer feel supported, not attacked

Use markdown headings (# for main, ## for sub) and friendly emojis to make your roast warm and approachable.""",
                "savage": """You are a SHARP, BRUTALLY HONEST, and HILARIOUSLY WITTY senior developer. For the 'Savage' roast level, your personality is:

**CRITICAL: Savage Level Personality:**
- Be DIRECT and NO-NONSENSE - call out issues exactly as they are, no sugar-coating
- Use SHARP WIT, MAXIMUM HUMOR, and TECHNICAL ACCURACY - your roasts should be EXTREMELY FUNNY and technically correct
- Be BRUTALLY HONEST with HILARIOUS comparisons - if something is vague, roast it with creative analogies
- Use CUTTING HUMOR with CLEVER METAPHORS - make developers laugh while they realize their mistakes
- Be IMPACTFUL and MEMORABLE - your words should hit hard and be so funny they're unforgettable
- Focus on ROASTING with MAXIMUM ENTERTAINMENT - your goal is to make people laugh while calling out problems

**CRITICAL: Savage Level Language:**
- Use HILARIOUS phrases with creative comparisons: "This is like...", "That's basically...", "Imagine if..."
- Use sharp, funny words: "chaos", "disaster", "confusion sandwich", "treasure hunt", "buzzword jungle"
- Use impactful emojis: 🔥, ⚡, 💥, 🎯, ⚠️, 💡, 🙃, 🏆, 🎨
- Frame feedback as HILARIOUS "roasts" that are both funny and accurate

**CRITICAL: Savage Level Approach:**
- Start with a HILARIOUS opening that makes people laugh
- Then roast each issue with MAXIMUM HUMOR and creative analogies
- End with a MEMORABLE, FUNNY verdict that will be quoted
- Make the developer think "this is hilarious AND accurate, I need to fix this"

Use markdown headings (# for main, ## for sub) and powerful emojis to make your roast EXTREMELY FUNNY, sharp, direct, and impactful.""",
                "extra_crispy": """You are a LEGENDARY tech lead with MAXIMUM SAVAGE POWER, ZERO MERCY, and ABSOLUTELY HILARIOUS HUMOR. For the 'Extra Crispy' roast level, your personality is:

**CRITICAL: Extra Crispy Level Personality:**
- Be ABSOLUTELY DESTRUCTIVE with MAXIMUM HUMOR - this is the funniest, most savage level
- Use LEGENDARY, HILARIOUS ROASTS - the funniest roasts that will be remembered forever and make people laugh out loud
- Be ZERO MERCY with CREATIVE COMEDY - if a ticket is bad, absolutely demolish it with maximum wit, humor, and clever comparisons
- Use MAXIMUM SAVAGE with ENTERTAINMENT - push the boundaries of humor while staying professional but EXTREMELY FUNNY
- Be UNFORGETTABLE and HILARIOUS - your roasts should be so funny and good they become legendary
- Focus on ABSOLUTE DESTRUCTION with MAXIMUM ENTERTAINMENT - your goal is to create a roast so savage and funny it's legendary

**CRITICAL: Extra Crispy Level Language:**
- Use maximum impact, HILARIOUS phrases with creative analogies: "This ticket is riding a one-way ticket to Confusion City...", "Imagine you're handed a treasure map with an X marking 'Somewhere over there'...", "This is like ordering all the toppings on a pizza but getting delivered a single slice of plain cheese..."
- Use legendary, funny words: "disaster", "chaos", "legendary mess", "epic failure", "confusion sandwich", "treasure hunt", "buzzword jungle", "quicksand"
- Use dramatic, funny emojis: 🔥🔥🔥, 💀, ⚡⚡⚡, 🎭, 🏆, 💥💥💥, 🙃, 🎨, 🚀
- Frame feedback as "LEGENDARY, HILARIOUS ROASTS" that are both extremely funny and accurate

**CRITICAL: Extra Crispy Level Approach:**
- Start with a LEGENDARY, HILARIOUS opening that makes everyone laugh
- Then absolutely demolish each issue with MAXIMUM SAVAGE HUMOR and creative, funny comparisons
- End with a LEGENDARY, MEMORABLE, FUNNY verdict that will be quoted forever
- Make the developer think "this roast is LEGENDARY and HILARIOUS, I need to completely rewrite this ticket"

Use markdown headings (# for main, ## for sub) and dramatic emojis to make your roast LEGENDARY, UNFORGETTABLE, MAXIMUM SAVAGE, and EXTREMELY FUNNY."""
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
        """Generate a roast using Azure OpenAI - Simplified working logic"""
        theme_prompt = self.get_roast_theme_prompt(theme, level)
        
        # ⬅️ Map level names (handle both formats)
        level_mapping = {
            'very-light': 'very_light',
            'very_light': 'very_light',
            'light': 'light',
            'savage': 'savage',
            'extra-crispy': 'extra_crispy',
            'extra_crispy': 'extra_crispy'
        }
        normalized_level = level_mapping.get(level.lower(), 'savage')
        
        # ⬅️ Simple, working roast level instructions (from separate project)
        roast_level_instructions = {
            'very_light': 'Create a very gentle, friendly roast with light humor. Be constructive and positive.',
            'light': 'Create a light roast with mild humor. Be playful but respectful.',
            'savage': 'Create a savage roast with sharp wit and humor. Be funny but still professional.',
            'extra_crispy': 'Create an extra crispy, brutally honest roast with maximum humor and wit. Be savage but constructive.'
        }
        
        # ⬅️ Build detailed, structured prompt matching the user's example style
        roast_instruction = roast_level_instructions.get(normalized_level, roast_level_instructions['savage'])
        
        prompt = f"""Create an EPIC, HILARIOUS, and MEMORABLE roast of the following Jira ticket/content. 

{roast_instruction}

**🎭 HUMOR REQUIREMENTS (CRITICAL - Make it EXTREMELY FUNNY):**
- Use WITTY comparisons and clever metaphors (e.g., "like ordering all the toppings on a pizza but getting delivered a single slice of plain cheese")
- Add PERSONALITY and DRAMA to every sentence
- Use CREATIVE analogies (e.g., "treasure map with an X marking 'Somewhere over there'", "one-way ticket to Confusion City")
- Make it ENTERTAINING - readers should LAUGH OUT LOUD
- Use SARCASM and IRONY where appropriate
- Add WITTY one-liners and clever wordplay
- Make comparisons RELATABLE and FUNNY (e.g., "more images than a Kardashian's Instagram", "like a frat party beer pong table")
- Be SAVAGE but CLEVER - not just mean, but intelligently funny

**CRITICAL: Output Structure (Follow this EXACT format - match the style of the examples below):**

# 🔥 EPIC ROAST 🔥

[Start with an ENGAGING, HILARIOUS introduction (2-4 sentences). Reference specific content from the ticket with quotes. Use maximum humor and personality. Examples:
- "Alright, buckle up folks—this Jira ticket feels like someone copy-pasted a novel, forgot the plot, and then slapped on **High Priority** because decimals are scary. Let's slice through the data-feed drama:"
- "Buckle up, folks, because this Jira ticket is riding a one-way ticket to Confusion City with a layover in Vague-Ville. Sit back as we dissect this 'masterpiece' of ambiguity, served piping hot and extra crispy."
- "Imagine you're handed a treasure map with an X marking 'Somewhere over there' and told, 'Good luck!' That's basically what this ticket feels like."]

[Add 2-3 MORE witty observations with specific quotes from the ticket, like:
- "Update datatype to Integer" Great. So we ignore 0.5 capacity? Perfect. Who needs half a shipping slot anyway? 🙃
- "In Discovery" Yeah, we're still **discovering** that decimals aren't integers. Nobel Prize material right here. 🏆
- "Test 24.001 v2: Sticky Top 5 + Flyout"? Great, so we're QA'ing filters or auditioning NASA's next launch sequence? 🙃]

---

## 📋 Key Issues Found:

[Use bullet points with bold titles and emojis. Each issue should be HILARIOUS and SPECIFIC:]

- **[Issue Name with Emoji]** ❓  
  "[Direct quote from ticket showing the problem]"  
  [EXTREMELY WITTY comment with clever comparison. Examples:
  - "Umm… update where? In SFCC, Deck, OMS, or our dreams? Pick one."
  - "That's like saying 'Drive to Mars and then back,' with no rocket or fuel plan."
  - "We've got more images than a Kardashian's Instagram. No context, no clarity, just a gallery of 'Here's some XML… maybe fix it?' 🎨"
  - "Who picked 'Test 24.001'? This reads like a rogue lottery ticket—no clear steps, no context, just a cryptic code that makes QA feel like treasure hunters."
  - "Unless these filters personally deposit 600K into the bank, this figure belongs in the CFO's keynote, not buried in a dev ticket."]

- **[Issue Name 2 with Emoji]** 🎯  
  "[Another direct quote from ticket]"  
  [Another HILARIOUS, specific comment with creative analogy. Examples:
  - "Zero labels on a Medium-priority Jira story? It's like launching a rocket with no coordinates—nobody knows how to track or triage this mess."
  - "These acceptance criteria are a blender of scenarios—QA needs a sextant and a crystal ball to navigate this storm."
  - "We've got at least four 'AI-generated' disclaimers clogging the comment feed. Is this ticket a filter story or an AI experiment?"]

- **[Issue Name 3 with Emoji]** 🗃️  
  "[Quote or specific example]"  
  [Witty comment with funny comparison. Examples:
  - "You dropped 'Joomla migration,' 'SAP feed,' 'Everest,' and 'Collab' in the same paragraph. We're lost in the buzzword jungle."
  - "Using a decimal in story points? What's next, velocity measured in millimeters? Either round it or call it Fibonacci—this 5.0 stunt is just flexing your Python background."
  - "Tossed in every buzzword from 'PWA' to 'MMT' like a frat party beer pong table. Less is more, people—this looks like the War and Peace of Jira stories."]

[Continue with 4-6 major issues, each following the format above. Be SPECIFIC - quote actual content from the ticket. Make each one FUNNIER than the last!]

---

## 💡 Suggestions for Improvement:

[Use bullet points with bold titles and emojis. Each suggestion should be actionable, specific, AND include a witty comment:]

- **[Suggestion Title]** ✍️  
  [Specific, actionable suggestion with example AND a funny comment. Examples:
  - "Spell out exactly which service, object, and field you're changing. No more treasure hunts."
  - "Replace 'Test 24.001 v2' with a descriptive title like 'Filter Flyout Opening – Desktop & Tablet Steps' and enumerate steps. No more cryptic decimals that make QA feel like codebreakers."]

- **[Suggestion Title 2]** ✅  
  [Another specific suggestion with example AND humor. Examples:
  - "'Priority must truncate decimals by rounding down, verified by these three unit tests.' Because 'it works on my machine' isn't a test plan."
  - "Move the 'Annual Domain… $600,550' to a Business Case doc or remove it entirely. Stick to filter functionality here—we're not running a finance seminar."]

- **[Suggestion Title 3]** 📷  
  [Another specific suggestion with wit. Examples:
  - "One sample XML snippet beats ten unlabeled screenshots. Quality over quantity, people."
  - "Add labels like PWA-Filter-UX, QA-Ready, Design-Complete to guide triage and filtering. No more 'Labels: None'—even a lost puppy has a tag."]

[Add 4-6 specific, actionable suggestions based on the actual ticket content. Make each one CLEVER and FUNNY!]

---

## 🎯 Final Verdict:

[End with a MEMORABLE, HILARIOUS one-liner or 2-3 sentences that summarize the roast. Use a CLEVER metaphor or comparison. Examples:
- "This ticket is basically a game of **'pin the decimal on the integer'** with no roadmap—time to tighten up before we drown in data-level quicksand. 🚀"
- "This ticket currently reads like modern art—open to interpretation but leaving everyone scratching their heads. With some ruthless pruning, crystal-clear criteria, and real metrics, it has the potential to be less 'abstract chaos' and more 'engineered brilliance.' Until then, it's serving up confusion sandwiches with a side of developer frustration."
- "This ticket is basically a game of 'Guess Who?' meets 'Pin the Decimal on the Story Point,' with a side of AI spam and budget flexing. Time to trim the fat, tighten the bullet points, and give QA a fighting chance before they drown in this filter-themed quicksand. 🚀"]

**CRITICAL REQUIREMENTS:**
1. **Quote actual content** from the ticket - use quotes like "Update datatype to Integer" or "Test 24.001 v2"
2. **Be EXTREMELY WITTY and FUNNY** - use clever comparisons, creative metaphors, and maximum humor
3. **Be specific** - reference exact phrases, fields, or sections from the ticket
4. **Use emojis strategically** - ❓ 🎯 🗃️ 📊 🔄 ✍️ ✅ 📷 📈 🕵️‍♀️ 🚀 🙃 🏆 🎨 💰 🌊 🤖 🔢
5. **Match the example style** - engaging intro, bullet points with bold titles, quotes from ticket, HILARIOUS comments, memorable verdict
6. **Make it ENTERTAINING** - readers should laugh, smile, and remember this roast
7. **Use CREATIVE analogies** - compare to relatable, funny situations (pizza orders, treasure maps, rocket launches, etc.)

Here's the content to roast:

{ticket_content}

Generate the roast now (follow the structure and style above EXACTLY - quote actual content, be EXTREMELY WITTY and FUNNY, be specific, make it MEMORABLE and ENTERTAINING):"""
        
        try:
            # Check if client is initialized
            if not self.client:
                console.print("[red]Azure OpenAI client not initialized. Check your environment variables.[/red]")
                return self.get_fallback_roast()
            
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            if not deployment_name:
                console.print("[red]AZURE_OPENAI_DEPLOYMENT_NAME not set[/red]")
                return self.get_fallback_roast()
            
            # Make API call with explicit timeout and retry handling
            console.print("[blue]Calling Azure OpenAI API...[/blue]")
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": theme_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=3000,  # o4-mini requires max_completion_tokens instead of max_tokens
                timeout=60.0  # 60 second timeout for longer responses
                # Note: o4-mini model only supports default temperature, so we don't set it
            )
            console.print("[green]✅ API call successful![/green]")
            
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
            if normalized_level == "very_light":
                roast_content = self._validate_very_light_content(roast_content, ticket_content)
            
            return roast_content
            
        except openai.APIError as e:
            error_msg = str(e)
            console.print(f"[red]Azure OpenAI API Error: {error_msg}[/red]")
            if hasattr(e, 'message'):
                console.print(f"[yellow]Error message: {e.message}[/yellow]")
            if hasattr(e, 'status_code'):
                console.print(f"[yellow]Status code: {e.status_code}[/yellow]")
            return self.get_fallback_roast()
        except openai.APIConnectionError as e:
            error_msg = str(e)
            console.print(f"[red]Azure OpenAI Connection Error: {error_msg}[/red]")
            console.print("[yellow]Check your network connection and Azure OpenAI endpoint.[/yellow]")
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET')
            console.print(f"[yellow]Endpoint: {endpoint[:50]}...[/yellow]")
            return self.get_fallback_roast()
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            console.print(f"[red]Error generating roast: {error_type}: {error_msg}[/red]")
            import traceback
            console.print(f"[yellow]Full traceback:[/yellow]")
            console.print(f"[yellow]{traceback.format_exc()}[/yellow]")
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
