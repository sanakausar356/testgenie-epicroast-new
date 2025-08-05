"""
Core Groom Room functionality for professional Jira ticket analysis
"""

import os
import sys
import re
from typing import Optional, Dict, List
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

class GroomRoom:
    """Main Groom Room application class for professional Jira ticket analysis"""
    
    def __init__(self):
        self.client = None
        self.jira_integration = JiraIntegration() if JiraIntegration else None
        self.setup_azure_openai()
        
        # Brand abbreviations mapping
        self.brand_abbreviations = {
            'MMT': 'Marmot brand',
            'ExO': 'Exo clothing brand', 
            'YCC': 'Yankee (Global-DTC)',
            'ELF': 'PWA (Progressive Web App) for YCC and MMT only',
            'EMEA': 'Yankee brand regions only (IE, FR, IT, DE, GB)'
        }
        
        # Framework definitions based on presentation
        self.frameworks = {
            'roi': {
                'name': 'R-O-I Framework',
                'elements': ['Role', 'Objective', 'Insight'],
                'description': 'Role / Objective / Insight analysis'
            },
            'invest': {
                'name': 'I-N-V-E-S-T Framework', 
                'elements': ['Independent', 'Negotiable', 'Valuable', 'Estimable', 'Small', 'Testable'],
                'description': 'Independent / Negotiable / Valuable / Estimable / Small / Testable'
            },
            'accept': {
                'name': 'A-C-C-E-P-T Criteria',
                'elements': ['Action', 'Condition', 'Criteria', 'Expected Result', 'Pass-Fail', 'Traceable'],
                'description': 'Action / Condition / Criteria / Expected Result / Pass-Fail / Traceable'
            },
            '3c': {
                'name': '3C Model',
                'elements': ['Card', 'Conversation', 'Confirmation'],
                'description': 'Card → Conversation → Confirmation'
            },
            'user_story_template': {
                'name': 'User Story Template',
                'elements': ['As a [user]', 'I want [goal]', 'so that [benefit]'],
                'description': 'As a [user], I want [goal], so that [benefit]'
            }
        }
        
        # Definition of Ready (DOR) requirements from presentation
        self.dor_requirements = {
            'user_story': {
                'name': 'User Story',
                'description': 'defining business value goal of the card',
                'responsibility': 'PO is responsible for creating',
                'template': 'As a [persona], I want to [do something], so that I can [realize a reward]',
                'questions': [
                    'Who is this user?',
                    'What makes them tick?', 
                    'Who\'s an example of such a person?',
                    'Why do they want to do this?',
                    'What\'s the benefit/reward?',
                    'How will we know if it\'s working?'
                ]
            },
            'acceptance_criteria': {
                'name': 'Acceptance Criteria',
                'description': 'defining what is expected to be completed and what will be validated in UAT',
                'responsibility': 'PO is Responsible for Creating – WHOLE TEAM is accountable for ensuring it is refined and understood',
                'characteristics': [
                    'State intent (what), not solution (how)',
                    'Have an actionable result',
                    'Does not only define happy path',
                    'Supporting documents present'
                ]
            },
            'testing_steps': {
                'name': 'Test Scenarios',
                'description': 'Defining high-level test scenarios that QA will utilize to build their test cases from',
                'responsibility': 'QA Leading - Team is responsible for adding this information',
                'test_scenarios': [
                    'Positive (Happy Path)',
                    'Negative (Error/Edge Handling)', 
                    'RBT (Risk-Based Testing)'
                ],
                'cross_browser_device': 'Cross-browser/device testing required? Y/N'
            },
            'additional_fields': {
                'name': 'Additional Card Details',
                'fields': [
                    'Brand(s)',
                    'Component(s)',
                    'Agile Team',
                    'Story Points',
                    'Figma Reference Status',
                    'Cross-browser/Device Testing Scope'
                ]
            }
        }
        
        # Card types and their definitions from presentation
        self.card_types = {
            'user_story': {
                'name': 'User Story',
                'definition': 'always tied to Features',
                'use_cases': [
                    'New functionality',
                    'Enhancement to current functionality',
                    'Change of Scope from initial ask',
                    'Missed Requirements from initial ask',
                    'Technical Enhancements',
                    'Non-Functional Requirements'
                ]
            },
            'bug': {
                'name': 'Bug',
                'definition': 'Ideally tied to feature & story that introduced',
                'use_cases': [
                    'Broken Functionality',
                    'Was working, now no longer working as it previously was'
                ]
            },
            'task': {
                'name': 'Task',
                'use_cases': [
                    'Enabling/Disabling an existing, tested, preference/config',
                    'Documentation Creation'
                ]
            }
        }
        
        # Bug card content requirements
        self.bug_requirements = {
            'clear_details': {
                'current_behavior': [
                    'Environment occurring',
                    'Product links',
                    'Screenshots'
                ],
                'replication_steps': [
                    'Outlining exactly how to replicate the bug'
                ],
                'expected_behavior': [
                    'Clear acceptance criteria on what is expected to occur'
                ]
            }
        }
        
        # Definition of Done (DoD) requirements
        self.dod_requirements = {
            'qa_signoff': {
                'name': 'QA Sign-off',
                'description': 'Quality assurance testing completed and approved',
                'checklist': ['Unit tests passed', 'Integration tests passed', 'UAT scenarios validated']
            },
            'accessibility_compliance': {
                'name': 'Accessibility Compliance',
                'description': 'WCAG guidelines and accessibility standards met',
                'checklist': ['Keyboard navigation', 'Screen reader compatibility', 'Color contrast ratios']
            },
            'uat_scenarios': {
                'name': 'UAT Scenarios',
                'description': 'User acceptance testing scenarios defined and validated',
                'checklist': ['Business user validation', 'End-to-end workflow testing', 'Stakeholder approval']
            },
            'documentation': {
                'name': 'Documentation',
                'description': 'Required documentation completed',
                'checklist': ['Technical documentation', 'User guides', 'API documentation']
            }
        }
        
        # Cross-functional concerns
        self.cross_functional_concerns = {
            'accessibility': {
                'name': 'Accessibility',
                'description': 'WCAG compliance and inclusive design',
                'indicators': ['modal', 'form', 'navigation', 'interactive', 'color', 'contrast']
            },
            'performance': {
                'name': 'Performance',
                'description': 'Performance expectations and optimization',
                'indicators': ['loading', 'response time', 'optimization', 'caching', 'database']
            },
            'security': {
                'name': 'Security',
                'description': 'Security considerations and compliance',
                'indicators': ['authentication', 'authorization', 'input validation', 'rate limiting', 'encryption']
            },
            'ux_validation': {
                'name': 'UX Validation',
                'description': 'User experience validation and testing',
                'indicators': ['user testing', 'usability', 'user feedback', 'design review']
            }
        }
    
    def setup_azure_openai(self):
        """Initialize Azure OpenAI client"""
        try:
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            
            console.print(f"[blue]Azure OpenAI Setup - Endpoint: {'Set' if endpoint else 'Not Set'}[/blue]")
            console.print(f"[blue]Azure OpenAI Setup - API Key: {'Set' if api_key else 'Not Set'}[/blue]")
            console.print(f"[blue]Azure OpenAI Setup - Deployment: {'Set' if deployment_name else 'Not Set'}[/blue]")
            
            if not all([endpoint, api_key, deployment_name]):
                console.print("[red]Error: Missing Azure OpenAI configuration in .env file[/red]")
                console.print("Please ensure you have the following variables set:")
                console.print("- AZURE_OPENAI_ENDPOINT")
                console.print("- AZURE_OPENAI_API_KEY")
                console.print("- AZURE_OPENAI_DEPLOYMENT_NAME")
                self.client = None
                return
            
            self.client = openai.AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
            
            console.print("[green]✅ Azure OpenAI client initialized successfully[/green]")
            
        except Exception as e:
            console.print(f"[red]Error setting up Azure OpenAI: {e}[/red]")
            console.print(f"[red]Error type: {type(e).__name__}[/red]")
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
                return ""
            except Exception as e:
                console.print(f"[red]Error reading file: {e}[/red]")
                return ""
        
        # Interactive input
        console.print(Panel.fit(
            "[bold blue]🧹 Groom Room[/bold blue]\n"
            "Please paste your Jira ticket content below.\n"
            "Press Ctrl+D (Unix) or Ctrl+Z (Windows) when finished, or type 'END' on a new line.",
            title="Input Jira Ticket"
        ))
        
        session = PromptSession()
        lines = []
        
        try:
            while True:
                line = session.prompt(HTML("<ansiblue>🧹 </ansiblue>"))
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass
        
        if not lines:
            console.print("[red]No ticket content provided[/red]")
            return ""
        
        return '\n'.join(lines)
    
    def get_comprehensive_jira_analysis_instructions(self) -> str:
        """Get comprehensive Jira field analysis instructions"""
        return """
**CRITICAL: Comprehensive Jira Field Analysis:**
You must read and analyze ALL available Jira fields in the ticket content, including:
- **Summary**: Main ticket title and key information
- **Description**: Detailed ticket content and context
- **Acceptance Criteria**: Specific requirements and success criteria (with enhanced validation for intent, conditions, expected results, and pass/fail logic)
- **Test Scenarios**: Custom field for testing coverage (Happy Path, Negative, RBT, Cross-browser) - must be separate from AC
- **Agile Team**: Assigned development team
- **Story Points**: Effort estimation
- **Components**: Affected system components
- **Brands**: Target brand(s) for the feature
- **Figma/Attachments**: Design references and supporting files (with enhanced Figma link analysis)
- **Comments**: Team discussions and additional context
- **Labels**: Categorization and metadata
- **Epic Link**: Parent epic relationship
- **Priority**: Business priority level
- **Linked Issues**: Related tickets and dependencies
- **Custom Fields**: Platform, Locale, Device Testing, etc.

**AI Understanding Requirements:**
- Use natural language understanding to detect vague vs specific acceptance criteria
- Validate AC structure for intent, conditions, expected results, and pass/fail logic
- Detect Figma links in AC and evaluate their context and behavioral expectations
- Check if test scenarios cover required dimensions (happy path, edge cases, RBT, cross-browser)
- Ensure test scenarios are in dedicated field, not embedded in AC
- Identify if user story follows agile template or is just high-level description
- Spot missing or mismatched fields (brand/component/story points)
- Infer PO/design sign-off likelihood from ticket language and comments
- Interpret labels/comments for blockers (e.g., "needs design", "blocked by backend")
- Generate meaningful output explaining why missing fields matter and affect sprint readiness"""

    def get_groom_level_prompt(self, level: str) -> str:
        """Get the groom prompt based on level"""
        comprehensive_instructions = self.get_comprehensive_jira_analysis_instructions()
        
        level_prompts = {
            "strict": f"""You are a rigorous Jira ticket analyst conducting strict grooming analysis. For the 'Strict' level, enforce ALL Definition of Ready requirements with zero tolerance for missing elements. Flag every gap, missing field, and potential risk. Be uncompromising in your assessment.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements - STRICT ENFORCEMENT:**
- **User Story**: MUST define business value goal, MUST follow "As a [persona], I want [do something], so that [realize reward]" template exactly
- **Acceptance Criteria**: MUST state intent (what), not solution (how), MUST have actionable results, MUST include edge cases beyond happy path
- **Test Scenarios**: MUST include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing) - ALL THREE REQUIRED
- **Additional Fields**: MUST include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope - ALL FIELDS REQUIRED

**CRITICAL: Card Type Validation - STRICT:**
- **User Story**: MUST be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: MUST include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements - STRICT:**
- **Dependencies & Blockers**: MUST identify ALL upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: MUST ensure QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: MUST confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: MUST assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: MUST consider accessibility, performance, security, and UX validation requirements

**STRICT ANALYSIS APPROACH:**
- Flag ANY missing field as a critical blocker
- Require ALL test scenario types (Happy Path, Negative, RBT, Cross-browser)
- Demand complete stakeholder sign-off evidence
- Reject tickets with vague acceptance criteria
- Require specific performance metrics and accessibility requirements
- Flag any potential security or compliance risks

{comprehensive_instructions}""",

            "light": f"""You are a flexible Jira ticket analyst conducting light grooming analysis. For the 'Light' level, focus on the most critical elements and provide constructive guidance without being overly strict. Allow for reasonable flexibility while maintaining quality standards.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements - LIGHT APPROACH:**
- **User Story**: Should define business value goal, preferably follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Should state intent (what), not solution (how), should have actionable results, consider including edge cases
- **Test Scenarios**: Should include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing) - at least 2 of 3
- **Additional Fields**: Should include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope - most fields

**CRITICAL: Card Type Validation - LIGHT:**
- **User Story**: Should be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Should include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements - LIGHT:**
- **Dependencies & Blockers**: Check for major upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: Consider QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: Confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: Assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements

**LIGHT ANALYSIS APPROACH:**
- Focus on major gaps and critical blockers only
- Allow flexibility in test scenario coverage (2 of 3 types acceptable)
- Accept reasonable stakeholder sign-off indicators
- Provide guidance for vague acceptance criteria rather than rejecting
- Suggest performance and accessibility considerations
- Note potential risks without blocking

{comprehensive_instructions}""",

            "default": f"""You are a professional Jira ticket analyst. For the 'Default' level, provide a balanced mix of feedback and gentle tone. Analyze the ticket against the specified frameworks and provide constructive feedback.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements:**
- **User Story**: Must define business value goal, follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Must state intent (what), not solution (how), have actionable results, include edge cases beyond happy path
- **Test Scenarios**: Must include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing)
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements:**
- **Dependencies & Blockers**: Check for upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: Ensure QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: Confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: Assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements

{comprehensive_instructions}""",
            
            "insight": f"""You are a focused analyst examining Jira tickets. For the 'Insight' level, provide focused analysis that calls out missing details and implied risks. Use concise bullet points and highlight specific gaps.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements:**
- **User Story**: Must define business value goal, follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Must state intent (what), not solution (how), have actionable results, include edge cases beyond happy path
- **Test Scenarios**: Must include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing)
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements:**
- **Dependencies & Blockers**: Check for upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: Ensure QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: Confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: Assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements

{comprehensive_instructions}""",
            
            "deep_dive": f"""You are a thorough analyst conducting deep analysis of Jira tickets. For the 'Deep Dive' level, provide comprehensive analysis including edge-case checks, data validations, and compliance notes. Be thorough and detailed.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements:**
- **User Story**: Must define business value goal, follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Must state intent (what), not solution (how), have actionable results, include edge cases beyond happy path
- **Test Scenarios**: Must include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing)
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements:**
- **Dependencies & Blockers**: Check for upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: Ensure QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: Confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: Assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements

{comprehensive_instructions}""",
            
            "actionable": f"""You are a practical analyst focused on actionable feedback. For the 'Actionable' level, highlight only items that directly map to user stories or acceptance criteria. Provide 'next steps' phrased as Jira tasks.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements:**
- **User Story**: Must define business value goal, follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Must state intent (what), not solution (how), have actionable results, include edge cases beyond happy path
- **Test Scenarios**: Must include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing)
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements:**
- **Dependencies & Blockers**: Check for upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: Ensure QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: Confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: Assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements

{comprehensive_instructions}""",
            
            "summary": f"""You are a concise analyst providing ultra-brief summaries. For the 'Summary' level, provide exactly 3 key gaps and 2 critical suggestions. Keep it brief and focused for quick scans.

**CRITICAL: Brand Abbreviations & Payment Rules:**
- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid and should NOT be flagged as missing context
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Do NOT flag brand abbreviations in ticket titles as missing context

**CRITICAL: Definition of Ready (DOR) Requirements:**
- **User Story**: Must define business value goal, follow "As a [persona], I want [do something], so that [realize reward]" template
- **Acceptance Criteria**: Must state intent (what), not solution (how), have actionable results, include edge cases beyond happy path
- **Test Scenarios**: Must include Positive (Happy Path), Negative (Error/Edge Handling), and RBT (Risk-Based Testing)
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points, Figma Reference Status, Cross-browser/Device Testing Scope

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation

**CRITICAL: Additional Analysis Requirements:**
- **Dependencies & Blockers**: Check for upstream/downstream dependencies, integration points, and blockers
- **Definition of Done (DoD)**: Ensure QA sign-off, accessibility compliance, UAT scenarios, and documentation requirements
- **Stakeholder Validation**: Confirm PO approval, design validation, and stakeholder alignment
- **Sprint Readiness**: Assess if story is ready for current/next sprint or needs refinement
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements

{comprehensive_instructions}"""
        }
        
        return level_prompts.get(level, level_prompts["default"])
    
    def analyze_brand_abbreviations(self, content: str) -> Dict[str, List[str]]:
        """Analyze content for brand abbreviations and their usage"""
        analysis = {
            'found_abbreviations': [],
            'potential_issues': [],
            'brand_context': {},
            'payment_flow_issues': [],
            'title_shortening_ok': []
        }
        
        content_upper = content.upper()
        
        for abbr, full_name in self.brand_abbreviations.items():
            if abbr in content_upper:
                analysis['found_abbreviations'].append(abbr)
                analysis['brand_context'][abbr] = full_name
                analysis['title_shortening_ok'].append(f"{abbr} (recognized brand abbreviation - do not flag as missing context)")
                
                # Check for potential issues based on brand rules
                if abbr == 'ELF' and ('YCC' not in content_upper and 'MMT' not in content_upper):
                    analysis['potential_issues'].append(f"ELF (PWA) mentioned but no YCC or MMT context found")
                elif abbr == 'EMEA' and not any(region in content_upper for region in ['IE', 'FR', 'IT', 'DE', 'GB']):
                    analysis['potential_issues'].append(f"EMEA mentioned but no specific regions (IE, FR, IT, DE, GB) specified")
        
        # ATC & Payment Notes Analysis
        self._analyze_payment_flows(content_upper, analysis)
        
        return analysis
    
    def _analyze_payment_flows(self, content_upper: str, analysis: Dict):
        """Analyze payment flow rules based on brand context"""
        
        # Check PWA (ELF) flow restrictions
        if 'ELF' in content_upper or 'PWA' in content_upper:
            ycc_pages = ['PLP', 'PDP', 'HOMEPAGE']
            mmt_pages = ['HOMEPAGE', 'PDP', 'PLP', 'MINICART']
            
            # Check if YCC pages are mentioned with ELF/PWA
            ycc_with_elf = 'YCC' in content_upper and any(page in content_upper for page in ycc_pages)
            mmt_with_elf = 'MMT' in content_upper and any(page in content_upper for page in mmt_pages)
            
            if not (ycc_with_elf or mmt_with_elf):
                analysis['payment_flow_issues'].append(
                    "ELF/PWA flows should only apply to: YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)"
                )
        
        # Check EMEA payment method rules
        if 'EMEA' in content_upper:
            if 'AFTERPAY' in content_upper or 'KLARNA' in content_upper:
                analysis['payment_flow_issues'].append(
                    "EMEA brands should use ClearPay instead of AfterPay/Klarna"
                )
            elif 'CLEARPAY' not in content_upper:
                analysis['payment_flow_issues'].append(
                    "EMEA context detected - consider specifying ClearPay as payment method"
                )
    
    def analyze_frameworks(self, content: str) -> Dict[str, Dict]:
        """Analyze content against the specified frameworks"""
        framework_analysis = {}
        
        for framework_key, framework_info in self.frameworks.items():
            analysis = {
                'name': framework_info['name'],
                'elements': {},
                'coverage_score': 0,
                'missing_elements': [],
                'suggestions': []
            }
            
            content_lower = content.lower()
            
            if framework_key == 'user_story_template':
                # Check for user story template pattern
                user_story_pattern = r'as\s+a\s+.*?i\s+want\s+.*?so\s+that\s+.*?'
                if re.search(user_story_pattern, content_lower):
                    analysis['elements']['template_found'] = True
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('User Story Template')
                    analysis['suggestions'].append('Follow the template: "As a [user], I want [goal], so that [benefit]"')
            
            elif framework_key == 'roi':
                # Check for Role, Objective, Insight elements
                role_indicators = ['as a', 'user', 'customer', 'admin', 'manager']
                objective_indicators = ['i want', 'need to', 'should be able to', 'goal']
                insight_indicators = ['so that', 'because', 'in order to', 'benefit']
                
                role_found = any(indicator in content_lower for indicator in role_indicators)
                objective_found = any(indicator in content_lower for indicator in objective_indicators)
                insight_found = any(indicator in content_lower for indicator in insight_indicators)
                
                analysis['elements']['role'] = role_found
                analysis['elements']['objective'] = objective_found
                analysis['elements']['insight'] = insight_found
                
                if role_found: analysis['coverage_score'] += 1
                if objective_found: analysis['coverage_score'] += 1
                if insight_found: analysis['coverage_score'] += 1
                
                if not role_found: analysis['missing_elements'].append('Role')
                if not objective_found: analysis['missing_elements'].append('Objective')
                if not insight_found: analysis['missing_elements'].append('Insight')
            
            elif framework_key == 'invest':
                # Check for INVEST criteria
                invest_criteria = {
                    'independent': ['standalone', 'independent', 'self-contained'],
                    'negotiable': ['flexible', 'negotiable', 'adjustable'],
                    'valuable': ['value', 'benefit', 'business value'],
                    'estimable': ['estimate', 'story points', 'effort'],
                    'small': ['small', 'manageable', 'focused'],
                    'testable': ['test', 'verify', 'validate', 'acceptance criteria']
                }
                
                for criterion, indicators in invest_criteria.items():
                    found = any(indicator in content_lower for indicator in indicators)
                    analysis['elements'][criterion] = found
                    if found:
                        analysis['coverage_score'] += 1
                    else:
                        analysis['missing_elements'].append(criterion.title())
            
            elif framework_key == 'accept':
                # Check for ACCEPT criteria
                accept_criteria = {
                    'action': ['action', 'behavior', 'do'],
                    'condition': ['when', 'if', 'condition', 'scenario'],
                    'criteria': ['criteria', 'requirement', 'must'],
                    'expected_result': ['expected', 'result', 'outcome'],
                    'pass_fail': ['pass', 'fail', 'success', 'failure'],
                    'traceable': ['trace', 'link', 'reference', 'ticket']
                }
                
                for criterion, indicators in accept_criteria.items():
                    found = any(indicator in content_lower for indicator in indicators)
                    analysis['elements'][criterion] = found
                    if found:
                        analysis['coverage_score'] += 1
                    else:
                        analysis['missing_elements'].append(criterion.replace('_', ' ').title())
            
            elif framework_key == '3c':
                # Check for 3C Model elements
                card_indicators = ['card', 'ticket', 'story', 'task']
                conversation_indicators = ['discuss', 'review', 'refine', 'groom']
                confirmation_indicators = ['accept', 'approve', 'sign off', 'confirm']
                
                card_found = any(indicator in content_lower for indicator in card_indicators)
                conversation_found = any(indicator in content_lower for indicator in conversation_indicators)
                confirmation_found = any(indicator in content_lower for indicator in confirmation_indicators)
                
                analysis['elements']['card'] = card_found
                analysis['elements']['conversation'] = conversation_found
                analysis['elements']['confirmation'] = confirmation_found
                
                if card_found: analysis['coverage_score'] += 1
                if conversation_found: analysis['coverage_score'] += 1
                if confirmation_found: analysis['coverage_score'] += 1
                
                if not card_found: analysis['missing_elements'].append('Card')
                if not conversation_found: analysis['missing_elements'].append('Conversation')
                if not confirmation_found: analysis['missing_elements'].append('Confirmation')
            
            # Calculate percentage coverage
            total_elements = len(framework_info['elements'])
            analysis['coverage_percentage'] = (analysis['coverage_score'] / total_elements) * 100 if total_elements > 0 else 0
            
            framework_analysis[framework_key] = analysis
        
        return framework_analysis
    
    def analyze_dor_requirements(self, content: str) -> Dict[str, Dict]:
        """Analyze content against Definition of Ready (DOR) requirements"""
        dor_analysis = {}
        
        for requirement_key, requirement_info in self.dor_requirements.items():
            analysis = {
                'name': requirement_info['name'],
                'description': requirement_info.get('description', ''),
                'responsibility': requirement_info.get('responsibility', ''),
                'coverage_score': 0,
                'missing_elements': [],
                'suggestions': []
            }
            
            content_lower = content.lower()
            
            if requirement_key == 'user_story':
                # Check for user story template and questions
                template_found = re.search(r'as\s+a\s+.*?i\s+want\s+.*?so\s+that\s+.*?', content_lower)
                if template_found:
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('User Story Template')
                    analysis['suggestions'].append(f'Follow template: "{requirement_info["template"]}"')
                
                # Check for business value indicators
                business_value_indicators = ['business value', 'goal', 'benefit', 'reward', 'value']
                if any(indicator in content_lower for indicator in business_value_indicators):
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('Business Value Goal')
                    analysis['suggestions'].append('Clearly define the business value this card will deliver')
            
            elif requirement_key == 'acceptance_criteria':
                # Check for acceptance criteria characteristics
                characteristics = requirement_info['characteristics']
                for characteristic in characteristics:
                    if 'intent' in characteristic.lower() and 'solution' in characteristic.lower():
                        # Check for "what" vs "how" language
                        what_indicators = ['should', 'must', 'will', 'expected', 'result']
                        how_indicators = ['click', 'button', 'api', 'database', 'code']
                        
                        what_found = any(indicator in content_lower for indicator in what_indicators)
                        how_heavy = sum(1 for indicator in how_indicators if indicator in content_lower)
                        
                        if what_found and how_heavy <= 2:
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('State intent (what), not solution (how)')
                            analysis['suggestions'].append('Focus on what should happen, not how to implement it')
                    
                    elif 'actionable' in characteristic.lower():
                        action_indicators = ['when', 'then', 'should', 'will', 'must']
                        if any(indicator in content_lower for indicator in action_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Actionable result')
                            analysis['suggestions'].append('Include clear, actionable outcomes')
                    
                    elif 'happy path' in characteristic.lower():
                        # Check for edge cases and negative scenarios
                        edge_case_indicators = ['if', 'when', 'error', 'invalid', 'failed', 'exception']
                        if any(indicator in content_lower for indicator in edge_case_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Edge cases beyond happy path')
                            analysis['suggestions'].append('Include error scenarios and edge cases')
                    
                    elif 'supporting documents' in characteristic.lower():
                        doc_indicators = ['link', 'url', 'screenshot', 'document', 'reference']
                        if any(indicator in content_lower for indicator in doc_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Supporting documents')
                            analysis['suggestions'].append('Include links to relevant documentation or screenshots')
            
            elif requirement_key == 'testing_steps':
                # Check for test scenarios - CRITICAL: Do NOT treat scenarios in AC as valid test scenarios
                test_scenarios = requirement_info['test_scenarios']
                
                # First, check if test scenarios are embedded in Acceptance Criteria (this is a grooming issue)
                ac_indicators = ['acceptance criteria', 'ac:', 'acceptance:', 'criteria:']
                test_scenario_indicators = ['test scenario', 'test case', 'positive test', 'negative test', 'rbt', 'risk-based']
                
                # Check if test scenarios are embedded in AC
                ac_section_found = any(indicator in content_lower for indicator in ac_indicators)
                test_scenarios_in_ac = False
                if ac_section_found:
                    # Look for test scenario indicators within AC section
                    lines = content.split('\n')
                    in_ac_section = False
                    for line in lines:
                        line_lower = line.lower()
                        if any(ac_indicator in line_lower for ac_indicator in ac_indicators):
                            in_ac_section = True
                        elif in_ac_section and any(test_indicator in line_lower for test_indicator in test_scenario_indicators):
                            test_scenarios_in_ac = True
                            break
                        elif in_ac_section and line.strip() == '':
                            in_ac_section = False
                
                if test_scenarios_in_ac:
                    analysis['missing_elements'].append('Test scenarios embedded in AC')
                    analysis['suggestions'].append('Move test scenarios from Acceptance Criteria to dedicated "Test Scenarios" field for clarity and separation of concerns')
                    # Don't add to coverage score as this is a grooming issue
                else:
                    # Check for dedicated test scenarios field
                    dedicated_test_scenarios_found = False
                    
                    # Look for dedicated test scenarios section
                    test_scenarios_section_indicators = ['test scenarios:', 'test scenarios field:', 'scenarios:', 'testing:']
                    for indicator in test_scenarios_section_indicators:
                        if indicator in content_lower:
                            dedicated_test_scenarios_found = True
                            break
                    
                    if dedicated_test_scenarios_found:
                        # Check for each required test scenario type
                        for scenario in test_scenarios:
                            scenario_lower = scenario.lower()
                            if 'positive' in scenario_lower or 'happy path' in scenario_lower:
                                positive_indicators = ['positive', 'happy path', 'success', 'valid', 'correct', 'expected']
                                if any(indicator in content_lower for indicator in positive_indicators):
                                    analysis['coverage_score'] += 1
                                else:
                                    analysis['missing_elements'].append('Positive (Happy Path)')
                            
                            elif 'negative' in scenario_lower or 'error' in scenario_lower:
                                negative_indicators = ['negative', 'error', 'edge', 'exception', 'invalid', 'failed', 'unauthorized', 'forbidden', 'denied']
                                if any(indicator in content_lower for indicator in negative_indicators):
                                    analysis['coverage_score'] += 1
                                else:
                                    analysis['missing_elements'].append('Negative (Error/Edge Handling)')
                            
                            elif 'rbt' in scenario_lower or 'risk-based' in scenario_lower:
                                rbt_indicators = ['rbt', 'risk-based', 'risk based', 'risk assessment', 'risk analysis']
                                if any(indicator in content_lower for indicator in rbt_indicators):
                                    analysis['coverage_score'] += 1
                                else:
                                    analysis['missing_elements'].append('RBT (Risk-Based Testing)')
                    else:
                        analysis['missing_elements'].append('Dedicated Test Scenarios field')
                        analysis['suggestions'].append('Add high-level test scenarios including: Positive (Happy Path), Negative (Error/Edge Handling), RBT (Risk-Based Testing)')
                
                # Check for cross-browser/device testing requirement
                cross_browser_indicators = ['cross-browser', 'cross browser', 'device testing', 'mobile', 'responsive', 'browser compatibility']
                if any(indicator in content_lower for indicator in cross_browser_indicators):
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('Cross-browser/device testing scope')
                    analysis['suggestions'].append('Confirm mobile responsiveness and cross-browser/device testing scope is defined')
            
            elif requirement_key == 'additional_fields':
                # Check for additional required fields
                fields = requirement_info['fields']
                for field in fields:
                    field_lower = field.lower()
                    if 'brand' in field_lower:
                        brand_indicators = ['brand', 'mmt', 'exo', 'ycc', 'elf', 'emea']
                        if any(indicator in content_lower for indicator in brand_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Brand(s)')
                    
                    elif 'component' in field_lower:
                        component_indicators = ['component', 'module', 'feature', 'area']
                        if any(indicator in content_lower for indicator in component_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Component(s)')
                    
                    elif 'agile team' in field_lower:
                        team_indicators = ['team', 'squad', 'scrum', 'agile']
                        if any(indicator in content_lower for indicator in team_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Agile Team')
                    
                    elif 'story points' in field_lower:
                        points_indicators = ['story points', 'points', 'estimate', 'effort']
                        if any(indicator in content_lower for indicator in points_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Story Points')
                    
                    elif 'figma reference status' in field_lower:
                        figma_indicators = ['figma', 'design', 'mockup', 'wireframe']
                        if any(indicator in content_lower for indicator in figma_indicators):
                            # Check if Figma is properly attached vs just referenced in text
                            figma_attachment_indicators = ['attached', 'embedded', 'linked', 'attachment']
                            figma_just_referenced = any(indicator in content_lower for indicator in figma_indicators) and not any(attachment_indicator in content_lower for attachment_indicator in figma_attachment_indicators)
                            
                            if figma_just_referenced:
                                analysis['coverage_score'] += 0.5  # Partial credit for reference
                                analysis['missing_elements'].append('Figma properly attached')
                                analysis['suggestions'].append('Figma reference exists in text, but not attached formally. Ensure frame is embedded or hyperlinked directly for visibility.')
                            else:
                                analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Figma Reference Status')
                    
                    elif 'cross-browser/device testing scope' in field_lower:
                        cross_browser_indicators = ['cross-browser', 'cross browser', 'device testing', 'mobile', 'responsive', 'browser compatibility']
                        if any(indicator in content_lower for indicator in cross_browser_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Cross-browser/Device Testing Scope')
                            analysis['suggestions'].append('Confirm mobile responsiveness and cross-browser/device testing scope is defined')
            
            # Calculate percentage coverage
            total_possible = 6  # Updated for additional fields (Brand, Component, Team, Story Points, Figma, Cross-browser)
            analysis['coverage_percentage'] = (analysis['coverage_score'] / total_possible) * 100 if total_possible > 0 else 0
            
            dor_analysis[requirement_key] = analysis
        
        return dor_analysis
    
    def analyze_card_type(self, content: str) -> Dict[str, Dict]:
        """Analyze content to determine card type and validate against type requirements"""
        card_analysis = {
            'detected_type': None,
            'confidence': 0,
            'validation': {},
            'suggestions': []
        }
        
        content_lower = content.lower()
        
        # Detect card type based on content
        if any(indicator in content_lower for indicator in ['bug', 'broken', 'not working', 'error', 'issue']):
            card_analysis['detected_type'] = 'bug'
            card_analysis['confidence'] = 0.8
        elif any(indicator in content_lower for indicator in ['user story', 'as a', 'i want', 'so that']):
            card_analysis['detected_type'] = 'user_story'
            card_analysis['confidence'] = 0.9
        elif any(indicator in content_lower for indicator in ['task', 'enable', 'disable', 'documentation']):
            card_analysis['detected_type'] = 'task'
            card_analysis['confidence'] = 0.7
        
        # Validate against type requirements
        if card_analysis['detected_type']:
            card_type_info = self.card_types[card_analysis['detected_type']]
            card_analysis['validation'] = {
                'name': card_type_info['name'],
                'definition': card_type_info.get('definition', ''),
                'use_cases': card_type_info.get('use_cases', []),
                'requirements_met': [],
                'requirements_missing': []
            }
            
            # Check if content aligns with card type requirements
            if card_analysis['detected_type'] == 'bug':
                bug_reqs = self.bug_requirements['clear_details']
                
                # Check current behavior
                current_behavior_indicators = ['environment', 'browser', 'device', 'screenshot', 'link']
                if any(indicator in content_lower for indicator in current_behavior_indicators):
                    card_analysis['validation']['requirements_met'].append('Current behavior details')
                else:
                    card_analysis['validation']['requirements_missing'].append('Current behavior details')
                
                # Check replication steps
                if any(indicator in content_lower for indicator in ['step', 'replicate', 'reproduce']):
                    card_analysis['validation']['requirements_met'].append('Replication steps')
                else:
                    card_analysis['validation']['requirements_missing'].append('Replication steps')
                
                # Check expected behavior
                if any(indicator in content_lower for indicator in ['expected', 'should', 'correct behavior']):
                    card_analysis['validation']['requirements_met'].append('Expected behavior')
                else:
                    card_analysis['validation']['requirements_missing'].append('Expected behavior')
            
            elif card_analysis['detected_type'] == 'user_story':
                # Check if tied to feature
                feature_indicators = ['feature', 'functionality', 'enhancement', 'new']
                if any(indicator in content_lower for indicator in feature_indicators):
                    card_analysis['validation']['requirements_met'].append('Tied to feature')
                else:
                    card_analysis['validation']['requirements_missing'].append('Should be tied to feature')
        
        return card_analysis
    
    def analyze_dependencies_and_blockers(self, content: str) -> Dict[str, Dict]:
        """Analyze content for dependencies and blockers"""
        analysis = {
            'dependencies_found': [],
            'blockers_identified': [],
            'integration_points': [],
            'upstream_dependencies': [],
            'downstream_dependencies': [],
            'recommendations': []
        }
        
        content_lower = content.lower()
        
        # Check for dependency indicators
        dependency_indicators = ['depends on', 'dependency', 'requires', 'needs', 'blocked by', 'waiting for']
        if any(indicator in content_lower for indicator in dependency_indicators):
            analysis['dependencies_found'].append('Dependencies mentioned in ticket')
        else:
            analysis['recommendations'].append('No dependencies or blockers identified. Confirm integration points (e.g., backend readiness, auth services) before sprinting.')
        
        # Check for integration points
        integration_indicators = ['api', 'backend', 'database', 'service', 'integration', 'auth', 'authentication']
        for indicator in integration_indicators:
            if indicator in content_lower:
                analysis['integration_points'].append(f'{indicator.title()} integration')
        
        # Check for upstream dependencies
        upstream_indicators = ['waiting for', 'blocked by', 'requires approval', 'needs signoff']
        if any(indicator in content_lower for indicator in upstream_indicators):
            analysis['upstream_dependencies'].append('Upstream dependencies detected')
        
        # Check for downstream dependencies
        downstream_indicators = ['will enable', 'allows', 'enables', 'supports']
        if any(indicator in content_lower for indicator in downstream_indicators):
            analysis['downstream_dependencies'].append('Downstream dependencies detected')
        
        return analysis
    
    def analyze_dod_alignment(self, content: str) -> Dict[str, Dict]:
        """Analyze content against Definition of Done (DoD) requirements"""
        dod_analysis = {}
        
        for dod_key, dod_info in self.dod_requirements.items():
            analysis = {
                'name': dod_info['name'],
                'description': dod_info['description'],
                'checklist': dod_info['checklist'],
                'coverage_score': 0,
                'missing_elements': [],
                'suggestions': []
            }
            
            content_lower = content.lower()
            
            if dod_key == 'qa_signoff':
                qa_indicators = ['qa', 'testing', 'test cases', 'validation', 'quality assurance']
                if any(indicator in content_lower for indicator in qa_indicators):
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('QA sign-off requirements')
                    analysis['suggestions'].append('Ensure the DoD checklist is addressed—QA sign-off, accessibility compliance, UAT scenarios, etc.')
            
            elif dod_key == 'accessibility_compliance':
                accessibility_indicators = ['accessibility', 'wcag', 'screen reader', 'keyboard navigation', 'contrast']
                if any(indicator in content_lower for indicator in accessibility_indicators):
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('Accessibility compliance')
                    analysis['suggestions'].append('Include accessibility requirements in DoD checklist')
            
            elif dod_key == 'uat_scenarios':
                uat_indicators = ['uat', 'user acceptance', 'business validation', 'stakeholder approval']
                if any(indicator in content_lower for indicator in uat_indicators):
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('UAT scenarios')
                    analysis['suggestions'].append('Define UAT scenarios for business validation')
            
            elif dod_key == 'documentation':
                doc_indicators = ['documentation', 'docs', 'technical docs', 'user guide', 'api docs']
                if any(indicator in content_lower for indicator in doc_indicators):
                    analysis['coverage_score'] += 1
                else:
                    analysis['missing_elements'].append('Documentation requirements')
                    analysis['suggestions'].append('Include documentation requirements in DoD')
            
            # Calculate percentage coverage
            total_possible = 1  # Base score for each DoD requirement
            analysis['coverage_percentage'] = (analysis['coverage_score'] / total_possible) * 100 if total_possible > 0 else 0
            
            dod_analysis[dod_key] = analysis
        
        return dod_analysis
    
    def analyze_stakeholder_validation(self, content: str) -> Dict[str, Dict]:
        """Analyze content for stakeholder and PO validation"""
        analysis = {
            'stakeholder_validation': {
                'found': False,
                'indicators': [],
                'missing': True,
                'recommendation': 'Confirm stakeholder alignment or PO approval of Figma design and success criteria.'
            },
            'po_approval': {
                'found': False,
                'indicators': [],
                'missing': True,
                'recommendation': 'Ensure Product Owner has reviewed and approved the current scope/design.',
                'visibility_issue': False,
                'visibility_recommendation': 'PO approval not visible—add a comment or label confirming sign-off to avoid ambiguity.'
            },
            'design_validation': {
                'found': False,
                'indicators': [],
                'missing': True,
                'recommendation': 'Confirm design validation and stakeholder sign-off.'
            }
        }
        
        content_lower = content.lower()
        
        # Check for stakeholder validation indicators
        stakeholder_indicators = ['stakeholder', 'approval', 'sign-off', 'signoff', 'validated', 'approved']
        if any(indicator in content_lower for indicator in stakeholder_indicators):
            analysis['stakeholder_validation']['found'] = True
            analysis['stakeholder_validation']['missing'] = False
            analysis['stakeholder_validation']['indicators'].append('Stakeholder validation mentioned')
        
        # Check for PO approval indicators
        po_indicators = ['product owner', 'po', 'product manager', 'pm approval']
        po_approval_mentioned = any(indicator in content_lower for indicator in po_indicators)
        
        if po_approval_mentioned:
            analysis['po_approval']['found'] = True
            analysis['po_approval']['missing'] = False
            analysis['po_approval']['indicators'].append('PO approval mentioned')
            
            # Check if PO approval is visible (has comment/label indicators)
            po_visibility_indicators = ['comment', 'label', 'approved', 'sign-off', 'signoff', 'confirmed']
            po_visible = any(indicator in content_lower for indicator in po_visibility_indicators)
            
            if not po_visible:
                analysis['po_approval']['visibility_issue'] = True
                analysis['po_approval']['indicators'].append('PO approval mentioned but not visibly confirmed')
        else:
            analysis['po_approval']['visibility_issue'] = True
        
        # Check for design validation indicators
        design_indicators = ['figma', 'design', 'mockup', 'wireframe', 'prototype', 'design review']
        if any(indicator in content_lower for indicator in design_indicators):
            analysis['design_validation']['found'] = True
            analysis['design_validation']['missing'] = False
            analysis['design_validation']['indicators'].append('Design validation mentioned')
        
        return analysis
    
    def analyze_sprint_readiness(self, content: str) -> Dict[str, Dict]:
        """Analyze content for sprint readiness indicators"""
        analysis = {
            'sprint_ready': False,
            'readiness_score': 0,
            'missing_for_sprint': [],
            'sprint_context': 'unknown',
            'recommendations': []
        }
        
        content_lower = content.lower()
        
        # Check for sprint readiness indicators
        ready_indicators = ['ready for sprint', 'sprint ready', 'ready to implement', 'implementation ready']
        if any(indicator in content_lower for indicator in ready_indicators):
            analysis['sprint_ready'] = True
            analysis['readiness_score'] += 1
        
        # Check for missing elements that would prevent sprint readiness
        missing_indicators = ['tbd', 'to be determined', 'pending', 'blocked', 'waiting']
        if any(indicator in content_lower for indicator in missing_indicators):
            analysis['missing_for_sprint'].append('Pending items identified')
            analysis['recommendations'].append('Confirm if this story is expected to be pulled in the next sprint, or requires refinement backlog.')
        
        # Check for sprint context
        if 'next sprint' in content_lower or 'current sprint' in content_lower:
            analysis['sprint_context'] = 'current/next sprint'
        elif 'backlog' in content_lower or 'refinement' in content_lower:
            analysis['sprint_context'] = 'backlog/refinement'
        
        return analysis
    
    def analyze_cross_functional_concerns(self, content: str) -> Dict[str, Dict]:
        """Analyze content for cross-functional concerns"""
        analysis = {}
        
        for concern_key, concern_info in self.cross_functional_concerns.items():
            concern_analysis = {
                'name': concern_info['name'],
                'description': concern_info['description'],
                'indicators_found': [],
                'coverage_score': 0,
                'missing': True,
                'recommendations': []
            }
            
            content_lower = content.lower()
            
            # Check for concern indicators
            for indicator in concern_info['indicators']:
                if indicator in content_lower:
                    concern_analysis['indicators_found'].append(indicator)
                    concern_analysis['coverage_score'] += 1
            
            if concern_analysis['coverage_score'] > 0:
                concern_analysis['missing'] = False
            else:
                concern_analysis['recommendations'].append(f'Consider {concern_info["name"].lower()} requirements if applicable')
            
            analysis[concern_key] = concern_analysis
        
        # Add general recommendation
        if not any(analysis[concern]['coverage_score'] > 0 for concern in analysis):
            analysis['general_recommendation'] = 'Ensure accessibility, performance, and security expectations are documented if applicable.'
        
        return analysis

    def analyze_test_scenarios(self, content: str) -> Dict[str, Dict]:
        """Analyze test scenarios field for comprehensive coverage"""
        analysis = {
            'happy_path': {'status': 'not_found', 'coverage': [], 'missing': []},
            'negative': {'status': 'not_found', 'coverage': [], 'missing': []},
            'rbt': {'status': 'not_found', 'coverage': [], 'missing': []},
            'cross_browser': {'status': 'not_found', 'coverage': [], 'missing': []},
            'overall_coverage': 'incomplete',
            'recommendations': []
        }
        
        content_lower = content.lower()
        
        # Check for Test Scenarios field or section
        test_scenarios_section = self._extract_test_scenarios_section(content)
        
        if test_scenarios_section:
            # Analyze Happy Path coverage
            if any(term in test_scenarios_section.lower() for term in ['happy path', 'positive', 'success', 'normal flow', 'expected behavior']):
                analysis['happy_path']['status'] = 'found'
                analysis['happy_path']['coverage'].append('Basic happy path scenarios identified')
            else:
                analysis['happy_path']['missing'].append('No happy path scenarios defined')
                analysis['recommendations'].append('Add positive test scenarios for normal user flows')
            
            # Analyze Negative/Edge case coverage
            if any(term in test_scenarios_section.lower() for term in ['negative', 'error', 'edge case', 'exception', 'invalid', 'failure']):
                analysis['negative']['status'] = 'found'
                analysis['negative']['coverage'].append('Error handling scenarios identified')
            else:
                analysis['negative']['missing'].append('No negative test scenarios defined')
                analysis['recommendations'].append('Add negative test scenarios for error conditions and edge cases')
            
            # Analyze RBT (Risk-Based Testing) coverage
            if any(term in test_scenarios_section.lower() for term in ['rbt', 'risk-based', 'risk', 'critical path', 'high impact']):
                analysis['rbt']['status'] = 'found'
                analysis['rbt']['coverage'].append('Risk-based testing scenarios identified')
            else:
                analysis['rbt']['missing'].append('No RBT scenarios defined')
                analysis['recommendations'].append('Add risk-based testing scenarios for critical user paths')
            
            # Analyze Cross-browser/Device testing coverage
            if any(term in test_scenarios_section.lower() for term in ['cross-browser', 'cross browser', 'device', 'mobile', 'responsive', 'browser compatibility']):
                analysis['cross_browser']['status'] = 'found'
                analysis['cross_browser']['coverage'].append('Cross-browser/device testing identified')
            else:
                analysis['cross_browser']['missing'].append('No cross-browser/device testing defined')
                analysis['recommendations'].append('Specify cross-browser and device testing requirements')
        else:
            # No test scenarios section found
            analysis['happy_path']['missing'].append('No test scenarios section found')
            analysis['negative']['missing'].append('No test scenarios section found')
            analysis['rbt']['missing'].append('No test scenarios section found')
            analysis['cross_browser']['missing'].append('No test scenarios section found')
            analysis['recommendations'].append('Add comprehensive test scenarios section with Happy Path, Negative, RBT, and Cross-browser coverage')
        
        # Determine overall coverage
        found_count = sum(1 for category in ['happy_path', 'negative', 'rbt', 'cross_browser'] 
                         if analysis[category]['status'] == 'found')
        
        if found_count == 4:
            analysis['overall_coverage'] = 'complete'
        elif found_count >= 2:
            analysis['overall_coverage'] = 'partial'
        else:
            analysis['overall_coverage'] = 'incomplete'
        
        return analysis

    def _extract_test_scenarios_section(self, content: str) -> str:
        """Extract test scenarios section from content"""
        
        # First try to find the entire test scenarios section
        # Look for "Test Scenarios:" and capture everything until the next major section
        test_scenarios_match = re.search(
            r'test scenarios?[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)', 
            content, 
            re.IGNORECASE | re.DOTALL
        )
        if test_scenarios_match:
            return test_scenarios_match.group(1).strip()
        
        # If not found, look for individual patterns and combine them
        patterns = [
            r'positive[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'negative[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'rbt[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'cross-browser[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'cross browser[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        sections = []
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                sections.append(match.group(1).strip())
        
        if sections:
            return '\n'.join(sections)
        
        return ""
    
    def calculate_groom_readiness_score(self, all_analyses: Dict) -> Dict[str, any]:
        """Calculate groom readiness score as a percentage"""
        score_data = {
            'overall_score': 0,
            'total_possible': 0,
            'completed_items': 0,
            'missing_items': 0,
            'score_breakdown': {},
            'critical_gaps': []
        }
        
        # Analyze DOR requirements
        dor_analysis = all_analyses.get('dor_analysis', {})
        dor_score = 0
        dor_total = 0
        
        for requirement_key, analysis in dor_analysis.items():
            coverage = analysis['coverage_percentage']
            dor_total += 100  # Each requirement is worth 100 points
            dor_score += coverage
            
            if coverage < 50:
                score_data['critical_gaps'].append(f"DOR: {analysis['name']} - {coverage:.1f}% coverage")
        
        score_data['score_breakdown']['dor'] = {
            'score': dor_score,
            'total': dor_total,
            'percentage': (dor_score / dor_total * 100) if dor_total > 0 else 0
        }
        
        # Analyze dependencies
        dep_analysis = all_analyses.get('dependencies_analysis', {})
        dep_score = 100 if not dep_analysis.get('dependencies_found') else 50
        score_data['score_breakdown']['dependencies'] = {
            'score': dep_score,
            'total': 100,
            'percentage': dep_score
        }
        
        # Analyze stakeholder validation
        stakeholder_analysis = all_analyses.get('stakeholder_analysis', {})
        stakeholder_score = 0
        stakeholder_total = len(stakeholder_analysis) * 100
        
        for section_key, section_data in stakeholder_analysis.items():
            if not section_data.get('missing', True):
                stakeholder_score += 100
            elif section_key == 'po_approval' and section_data.get('visibility_issue', False):
                stakeholder_score += 50  # Partial credit for PO approval with visibility issue
        
        score_data['score_breakdown']['stakeholder'] = {
            'score': stakeholder_score,
            'total': stakeholder_total,
            'percentage': (stakeholder_score / stakeholder_total * 100) if stakeholder_total > 0 else 0
        }
        
        # Analyze test scenarios
        test_scenarios_analysis = all_analyses.get('test_scenarios_analysis', {})
        test_scenarios_score = 0
        test_scenarios_total = 400  # 100 points each for happy_path, negative, rbt, cross_browser
        
        categories = ['happy_path', 'negative', 'rbt', 'cross_browser']
        for category in categories:
            category_data = test_scenarios_analysis.get(category, {})
            if category_data.get('status') == 'found':
                test_scenarios_score += 100
        
        score_data['score_breakdown']['test_scenarios'] = {
            'score': test_scenarios_score,
            'total': test_scenarios_total,
            'percentage': (test_scenarios_score / test_scenarios_total * 100) if test_scenarios_total > 0 else 0
        }
        
        # Calculate overall score
        total_score = dor_score + dep_score + stakeholder_score + test_scenarios_score
        total_possible = dor_total + 100 + stakeholder_total + test_scenarios_total  # 100 for dependencies
        
        score_data['overall_score'] = total_score
        score_data['total_possible'] = total_possible
        score_data['completed_items'] = total_score
        score_data['missing_items'] = total_possible - total_score
        
        return score_data
    
    def create_visual_checklist(self, all_analyses: Dict) -> Dict[str, Dict]:
        """Create a visual checklist summary for quick scanning"""
        checklist = {
            'overall_status': 'yellow',  # red, yellow, green
            'sections': {},
            'summary': {
                'total_items': 0,
                'completed_items': 0,
                'missing_items': 0,
                'critical_gaps': []
            },
            'groom_score': self.calculate_groom_readiness_score(all_analyses)
        }
        
        # Analyze DOR requirements
        dor_analysis = all_analyses.get('dor_analysis', {})
        dor_status = 'green'
        dor_completed = 0
        dor_total = 0
        
        for requirement_key, analysis in dor_analysis.items():
            dor_total += 1
            if analysis['coverage_percentage'] >= 75:
                dor_completed += 1
            elif analysis['coverage_percentage'] < 50:
                dor_status = 'red'
                checklist['summary']['critical_gaps'].append(f"DOR: {analysis['name']} - {analysis['coverage_percentage']:.1f}% coverage")
        
        if dor_status == 'green' and dor_completed < dor_total:
            dor_status = 'yellow'
        
        checklist['sections']['dor'] = {
            'name': 'Definition of Ready',
            'status': dor_status,
            'completed': dor_completed,
            'total': dor_total,
            'percentage': (dor_completed / dor_total * 100) if dor_total > 0 else 0
        }
        
        # Analyze dependencies
        dep_analysis = all_analyses.get('dependencies_analysis', {})
        dep_status = 'green' if not dep_analysis.get('dependencies_found') else 'yellow'
        checklist['sections']['dependencies'] = {
            'name': 'Dependencies & Blockers',
            'status': dep_status,
            'completed': 1 if dep_status == 'green' else 0,
            'total': 1,
            'percentage': 100 if dep_status == 'green' else 50
        }
        
        # Analyze stakeholder validation
        stakeholder_analysis = all_analyses.get('stakeholder_analysis', {})
        stakeholder_completed = sum(1 for section in stakeholder_analysis.values() if not section.get('missing', True))
        stakeholder_total = len(stakeholder_analysis)
        stakeholder_status = 'green' if stakeholder_completed == stakeholder_total else 'yellow' if stakeholder_completed > 0 else 'red'
        
        checklist['sections']['stakeholder'] = {
            'name': 'Stakeholder Validation',
            'status': stakeholder_status,
            'completed': stakeholder_completed,
            'total': stakeholder_total,
            'percentage': (stakeholder_completed / stakeholder_total * 100) if stakeholder_total > 0 else 0
        }
        
        # Analyze test scenarios
        test_scenarios_analysis = all_analyses.get('test_scenarios_analysis', {})
        test_scenarios_completed = 0
        test_scenarios_total = 4  # happy_path, negative, rbt, cross_browser
        
        categories = ['happy_path', 'negative', 'rbt', 'cross_browser']
        for category in categories:
            category_data = test_scenarios_analysis.get(category, {})
            if category_data.get('status') == 'found':
                test_scenarios_completed += 1
        
        test_scenarios_status = 'green' if test_scenarios_completed == test_scenarios_total else 'yellow' if test_scenarios_completed >= 2 else 'red'
        
        if test_scenarios_completed < 2:
            checklist['summary']['critical_gaps'].append(f"Test Scenarios: Only {test_scenarios_completed}/4 categories covered")
        
        checklist['sections']['test_scenarios'] = {
            'name': 'Test Scenarios',
            'status': test_scenarios_status,
            'completed': test_scenarios_completed,
            'total': test_scenarios_total,
            'percentage': (test_scenarios_completed / test_scenarios_total * 100) if test_scenarios_total > 0 else 0
        }
        
        # Calculate overall status
        total_sections = len(checklist['sections'])
        green_sections = sum(1 for section in checklist['sections'].values() if section['status'] == 'green')
        red_sections = sum(1 for section in checklist['sections'].values() if section['status'] == 'red')
        
        if red_sections > 0:
            checklist['overall_status'] = 'red'
        elif green_sections == total_sections:
            checklist['overall_status'] = 'green'
        else:
            checklist['overall_status'] = 'yellow'
        
        # Calculate summary
        checklist['summary']['total_items'] = sum(section['total'] for section in checklist['sections'].values())
        checklist['summary']['completed_items'] = sum(section['completed'] for section in checklist['sections'].values())
        checklist['summary']['missing_items'] = checklist['summary']['total_items'] - checklist['summary']['completed_items']
        
        return checklist
    
    def generate_groom_analysis(self, ticket_content: str, level: str = "default") -> str:
        """Generate professional groom analysis using Azure OpenAI"""
        try:
            level_prompt = self.get_groom_level_prompt(level)
            
            # Analyze content for all aspects
            ticket_summary_analysis = self.analyze_ticket_summary(ticket_content)
            brand_analysis = self.analyze_brand_abbreviations(ticket_content)
            framework_analysis = self.analyze_frameworks(ticket_content)
            dor_analysis = self.analyze_dor_requirements(ticket_content)
            card_analysis = self.analyze_card_type(ticket_content)
            dependencies_analysis = self.analyze_dependencies_and_blockers(ticket_content)
            dod_analysis = self.analyze_dod_alignment(ticket_content)
            stakeholder_analysis = self.analyze_stakeholder_validation(ticket_content)
            sprint_readiness_analysis = self.analyze_sprint_readiness(ticket_content)
            cross_functional_analysis = self.analyze_cross_functional_concerns(ticket_content)
            test_scenarios_analysis = self.analyze_test_scenarios(ticket_content)
            enhanced_test_scenarios_analysis = self.analyze_enhanced_test_scenarios_v2(ticket_content)
            enhanced_ac_analysis = self.analyze_enhanced_acceptance_criteria(ticket_content)
            additional_jira_fields_analysis = self.analyze_additional_jira_fields(ticket_content)
            
            # Create visual checklist
            all_analyses = {
                'dor_analysis': dor_analysis,
                'dependencies_analysis': dependencies_analysis,
                'stakeholder_analysis': stakeholder_analysis,
                'test_scenarios_analysis': test_scenarios_analysis
            }
            visual_checklist = self.create_visual_checklist(all_analyses)
            
            # Create summaries
            ticket_summary_summary = self._create_ticket_summary_summary(ticket_summary_analysis)
            framework_summary = self._create_framework_summary(framework_analysis)
            brand_summary = self._create_brand_summary(brand_analysis)
            dor_summary = self._create_dor_summary(dor_analysis)
            card_summary = self._create_card_summary(card_analysis)
            dependencies_summary = self._create_dependencies_summary(dependencies_analysis)
            dod_summary = self._create_dod_summary(dod_analysis)
            stakeholder_summary = self._create_stakeholder_summary(stakeholder_analysis)
            sprint_readiness_summary = self._create_sprint_readiness_summary(sprint_readiness_analysis)
            cross_functional_summary = self._create_cross_functional_summary(cross_functional_analysis)
            test_scenarios_summary = self._create_test_scenarios_summary(test_scenarios_analysis)
            enhanced_test_scenarios_summary = self._create_enhanced_test_scenarios_summary(enhanced_test_scenarios_analysis)
            enhanced_ac_summary = self._create_enhanced_acceptance_criteria_summary(enhanced_ac_analysis)
            additional_jira_fields_summary = self._create_additional_jira_fields_summary(additional_jira_fields_analysis)
            checklist_summary = self._create_checklist_summary(visual_checklist)
            
            prompt = f"""
{level_prompt}

**Jira Ticket Content:**
{ticket_content}

**Ticket Summary Analysis:**
{ticket_summary_summary}

**Brand Analysis:**
{brand_summary}

**Framework Analysis:**
{framework_summary}

**Definition of Ready (DOR) Analysis:**
{dor_summary}

**Card Type Analysis:**
{card_summary}

**Dependencies & Blockers Analysis:**
{dependencies_summary}

**Definition of Done (DoD) Alignment:**
{dod_summary}

**Stakeholder Validation Analysis:**
{stakeholder_summary}

**Sprint Readiness Analysis:**
{sprint_readiness_summary}

**Cross-Functional Concerns Analysis:**
{cross_functional_summary}

**Test Scenarios Analysis:**
{test_scenarios_summary}

**Enhanced Test Scenarios Analysis:**
{enhanced_test_scenarios_summary}

**Enhanced Acceptance Criteria Analysis:**
{enhanced_ac_summary}

**Additional Jira Fields Analysis:**
{additional_jira_fields_summary}

**Visual Checklist Summary:**
{checklist_summary}

**CRITICAL FORMATTING RULES:**
- Use ONLY markdown formatting, NEVER HTML tags
- Use **text** for bold emphasis (NOT <b>text</b>)
- Use *text* for italic emphasis (NOT <i>text</i>)
- Use # for main headings, ## for subheadings
- Use - for bullet points
- NEVER use HTML tags like <b>, </b>, <i>, </i>, etc.

**Instructions:**
1. Analyze the Jira ticket against the provided framework analysis
2. Provide professional feedback based on the selected level
3. Use the exact terminology from the presentation frameworks
4. Include specific suggestions for improvement
5. Reference the brand analysis if relevant
6. Use ONLY markdown formatting - **bold** for emphasis, *italic* for emphasis, # for headings
7. NEVER use HTML tags in your response
8. **AVOID REPETITIVE FEEDBACK**: If a missing element (e.g., test scenarios or Figma link) has already been mentioned in one section, do not repeat it verbatim in other sections. Refer to it briefly if needed (e.g., "See Key Findings" or "As noted above"). Each issue should only be fully explained once or twice.

**Output Format for Strict Level:**
# 🔒 Strict Groom Analysis

[Zero-tolerance comprehensive review - enforcing ALL Definition of Ready requirements]

## 📋 Ticket Summary:
[1-3 sentence summary of what the ticket is about, derived from Summary, Description, and Card Type fields]

## 🚨 Critical Blockers:
- **Blocker 1** - MUST be resolved before sprint inclusion
- **Blocker 2** - MUST be resolved before sprint inclusion
- **Blocker 3** - MUST be resolved before sprint inclusion

## ❌ Missing Required Fields:
- **Missing field 1** - CRITICAL: Required for Definition of Ready
- **Missing field 2** - CRITICAL: Required for Definition of Ready
- **Missing field 3** - CRITICAL: Required for Definition of Ready

## ⚠️ Definition of Ready Violations:
- **DOR violation 1** - Must be corrected
- **DOR violation 2** - Must be corrected
- **DOR violation 3** - Must be corrected

## 🔗 Dependencies & Blockers:
- **Dependency status** - MUST be resolved
- **Blocker assessment** - MUST be addressed

## ✅ Definition of Done Alignment:
- **DoD coverage** - MUST meet all requirements
- **QA and accessibility** - MUST be specified

## 👥 Stakeholder Validation:
- **PO approval status** - MUST be confirmed
- **Design validation** - MUST be completed

## 🚀 Sprint Readiness:
- **Readiness assessment** - NOT READY until all blockers resolved
- **Sprint context** - Cannot proceed until requirements met

## 🎯 Framework Coverage:
[Strict framework analysis - ALL elements required]

## 🧪 Test Scenario Breakdown:
[ALL test scenario types required: Happy Path, Negative, RBT, Cross-browser]

## 🏗 Technical Detail Feedback:
[Analysis of Implementation Details, ADA Acceptance Criteria, Architectural Solution, Performance Impact, Linked Issues]

## 📊 Groom Readiness Score:
[AI-estimated % readiness - likely low due to strict requirements]

## 🧾 Grooming Checklist:
[Visual reference - ALL items must be completed]

## 🎯 Summary:
[Strict assessment - ticket NOT ready for sprint until all issues resolved]

**Output Format for Light Level:**
# 💡 Light Groom Analysis

[Flexible approach focusing on critical elements with reasonable flexibility]

## 📋 Ticket Summary:
[1-3 sentence summary of what the ticket is about, derived from Summary, Description, and Card Type fields]

## 🔍 Key Areas for Improvement:
- **Area 1** - Consider addressing for better quality
- **Area 2** - Consider addressing for better quality
- **Area 3** - Consider addressing for better quality

## 💡 Suggestions for Enhancement:
- **Suggestion 1** - Optional improvement
- **Suggestion 2** - Optional improvement
- **Suggestion 3** - Optional improvement

## 🔗 Dependencies & Blockers:
- **Dependency status** - Check if major blockers exist
- **Blocker assessment** - Note any significant issues

## ✅ Definition of Done Alignment:
- **DoD coverage** - Consider key requirements
- **QA and accessibility** - Consider important aspects

## 👥 Stakeholder Validation:
- **PO approval status** - Confirm if reasonable indicators present
- **Design validation** - Check if design considerations noted

## 🚀 Sprint Readiness:
- **Readiness assessment** - Likely ready with minor improvements
- **Sprint context** - Consider for inclusion with noted areas

## 🎯 Framework Coverage:
[Flexible framework analysis - focus on key elements]

## 🧪 Test Scenario Breakdown:
[Test scenario review - 2 of 3 types acceptable]

## 🏗 Technical Detail Feedback:
[Analysis of Implementation Details, ADA Acceptance Criteria, Architectural Solution, Performance Impact, Linked Issues]

## 📊 Groom Readiness Score:
[AI-estimated % readiness - likely moderate to high]

## 🧾 Grooming Checklist:
[Visual reference - focus on major items]

## 🎯 Summary:
[Light assessment - ticket likely ready with minor improvements]

**Output Format for Default Level:**
# 📋 Groom Analysis

[AI-powered comprehensive review of Jira ticket fields - analyzing all available data for sprint readiness]

## 📋 Ticket Summary:
[1-3 sentence summary of what the ticket is about, derived from Summary, Description, and Card Type fields]

## 🔍 Key Findings:
- **Finding 1** with relevant context
- **Finding 2** with relevant context
- **Finding 3** with relevant context

## 💡 Improvement Suggestions:
- **Suggestion 1** with specific guidance
- **Suggestion 2** with specific guidance
- **Suggestion 3** with specific guidance

## 🔗 Dependencies & Blockers:
- **Dependency status** with integration points
- **Blocker assessment** with recommendations

## ✅ Definition of Done Alignment:
- **DoD coverage** with missing elements
- **QA and accessibility** requirements

## 👥 Stakeholder Validation:
- **PO approval status** with recommendations
- **Design validation** requirements

## 🚀 Sprint Readiness:
- **Readiness assessment** with missing items
- **Sprint context** and recommendations

## 🎯 Framework Coverage:
[Summary of framework analysis with specific findings]

## ✅ Acceptance Criteria Review:
[Enhanced AC analysis - validates intent, conditions, expected results, pass/fail logic, detects vague AC and Figma links]

## 🧪 Test Scenario Breakdown:
[Enhanced Test Scenarios analysis - validates Happy Path, Negative, RBT, Cross-browser coverage, detects field misuse]

## 🎨 Figma Design Reference:
[Figma link analysis - evaluates context, behavioral expectations, and placement recommendations]

## 🏗 Technical Detail Feedback:
[Analysis of Implementation Details, ADA Acceptance Criteria, Architectural Solution, Performance Impact, Linked Issues]

## 📊 Groom Readiness Score:
[AI-estimated % readiness based on all analyzed fields]

## 🧾 Grooming Checklist:
[Visual reference for sprint team alignment on missing items]

## 🎯 Summary:
[Professional summary of key areas needing attention]

**Output Format for Insight Level:**
# 🔍 Insight Analysis

[Focused analysis highlighting missing details and implied risks]

## ⚠️ Missing Details:
- **Missing detail 1** with risk assessment
- **Missing detail 2** with risk assessment

## 🚨 Implied Risks:
- **Risk 1** with impact assessment
- **Risk 2** with impact assessment

## 💡 Recommendations:
- **Recommendation 1** with specific action
- **Recommendation 2** with specific action

**Output Format for Deep Dive Level:**
# 🔬 Deep Dive Analysis

[Comprehensive analysis including edge cases, validations, and compliance]

## 🔍 Edge Cases:
- **Edge case 1** with validation approach
- **Edge case 2** with validation approach

## 📋 Data Validations:
- **Validation 1** with specific requirements
- **Validation 2** with specific requirements

## ⚖️ Compliance Notes:
- **Compliance item 1** with requirements
- **Compliance item 2** with requirements

## 💡 Comprehensive Recommendations:
- **Recommendation 1** with detailed guidance
- **Recommendation 2** with detailed guidance

**Output Format for Actionable Level:**
# ⚡ Actionable Analysis

[Direct mapping to user stories with next steps as Jira tasks]

## 📋 Jira Tasks to Create:
- **[JIRA-XXX] Task 1** - Specific action item
- **[JIRA-XXX] Task 2** - Specific action item
- **[JIRA-XXX] Task 3** - Specific action item

## 🎯 Next Steps:
- **Step 1** with assignee and timeline
- **Step 2** with assignee and timeline

**Output Format for Summary Level:**
# 📝 Summary Analysis

[Ultra-brief: exactly 3 key gaps and 2 critical suggestions]

## 🔍 3 Key Gaps:
1. **Gap 1** - Brief description
2. **Gap 2** - Brief description  
3. **Gap 3** - Brief description

## 💡 2 Critical Suggestions:
1. **Suggestion 1** - Brief action
2. **Suggestion 2** - Brief action

**REMEMBER: Use markdown formatting only, no HTML tags!**
"""
            
            if not self.client:
                console.print("[red]Azure OpenAI client not available[/red]")
                return self.get_fallback_groom_analysis()
            
            # Debug: Check environment variables
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            if not deployment_name:
                console.print("[red]AZURE_OPENAI_DEPLOYMENT_NAME not set[/red]")
                return self.get_fallback_groom_analysis()
                
            console.print(f"[blue]Using deployment: {deployment_name}[/blue]")
                
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": level_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000
                # Removed temperature parameter as o4-mini model doesn't support it
            )
            
            groom_content = response.choices[0].message.content
            
            # Clean up any HTML tags that might have been generated
            groom_content = re.sub(r'<b>(.*?)</b>', r'**\1**', groom_content)
            groom_content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', groom_content)
            groom_content = re.sub(r'<i>(.*?)</i>', r'*\1*', groom_content)
            groom_content = re.sub(r'<em>(.*?)</em>', r'*\1*', groom_content)
            groom_content = re.sub(r'<[^>]*>', '', groom_content)
            
            return groom_content
            
        except Exception as e:
            console.print(f"[red]Error generating groom analysis: {e}[/red]")
            console.print(f"[red]Error type: {type(e).__name__}[/red]")
            console.print(f"[red]Error details: {str(e)}[/red]")
            return self.get_fallback_groom_analysis()
    
    def _create_framework_summary(self, framework_analysis: Dict) -> str:
        """Create a summary of framework analysis"""
        summary = []
        
        for framework_key, analysis in framework_analysis.items():
            framework_name = analysis['name']
            coverage = analysis['coverage_percentage']
            missing = analysis['missing_elements']
            
            summary.append(f"**{framework_name}**: {coverage:.1f}% coverage")
            if missing:
                summary.append(f"  Missing: {', '.join(missing)}")
            summary.append("")
        
        return '\n'.join(summary)
    
    def _create_brand_summary(self, brand_analysis: Dict) -> str:
        """Create a summary of brand analysis"""
        summary = []
        
        if brand_analysis['found_abbreviations']:
            summary.append("**Brand Abbreviations Found:**")
            for abbr in brand_analysis['found_abbreviations']:
                summary.append(f"  - {abbr}: {brand_analysis['brand_context'][abbr]}")
        
        if brand_analysis['title_shortening_ok']:
            summary.append("**Title Shortening Validation:**")
            for validation in brand_analysis['title_shortening_ok']:
                summary.append(f"  - ✅ {validation}")
        
        if brand_analysis['potential_issues']:
            summary.append("**Potential Brand Issues:**")
            for issue in brand_analysis['potential_issues']:
                summary.append(f"  - ⚠️ {issue}")
        
        if brand_analysis['payment_flow_issues']:
            summary.append("**Payment Flow Issues:**")
            for issue in brand_analysis['payment_flow_issues']:
                summary.append(f"  - 💳 {issue}")
        
        return '\n'.join(summary) if summary else "No brand abbreviations found."
    
    def _create_dor_summary(self, dor_analysis: Dict) -> str:
        """Create a summary of DOR analysis"""
        summary = []
        
        for requirement_key, analysis in dor_analysis.items():
            requirement_name = analysis['name']
            coverage = analysis['coverage_percentage']
            missing = analysis['missing_elements']
            responsibility = analysis['responsibility']
            
            summary.append(f"**{requirement_name}**: {coverage:.1f}% coverage")
            summary.append(f"  Responsibility: {responsibility}")
            if missing:
                summary.append(f"  Missing: {', '.join(missing)}")
            summary.append("")
        
        return '\n'.join(summary)
    
    def _create_card_summary(self, card_analysis: Dict) -> str:
        """Create a summary of card type analysis"""
        summary = []
        
        if card_analysis['detected_type']:
            card_type = card_analysis['detected_type'].replace('_', ' ').title()
            confidence = card_analysis['confidence'] * 100
            validation = card_analysis['validation']
            
            summary.append(f"**Detected Card Type**: {card_type} ({confidence:.0f}% confidence)")
            
            if validation.get('definition'):
                summary.append(f"  Definition: {validation['definition']}")
            
            if validation.get('requirements_met'):
                summary.append(f"  ✅ Requirements Met: {', '.join(validation['requirements_met'])}")
            
            if validation.get('requirements_missing'):
                summary.append(f"  ❌ Missing Requirements: {', '.join(validation['requirements_missing'])}")
        else:
            summary.append("**Card Type**: Unable to determine card type")
        
        return '\n'.join(summary)
    
    def _create_dependencies_summary(self, dependencies_analysis: Dict) -> str:
        """Create a summary of dependencies and blockers analysis"""
        summary = []
        
        if dependencies_analysis['dependencies_found']:
            summary.append("**Dependencies Found:**")
            for dep in dependencies_analysis['dependencies_found']:
                summary.append(f"  - 🔗 {dep}")
        
        if dependencies_analysis['integration_points']:
            summary.append("**Integration Points:**")
            for point in dependencies_analysis['integration_points']:
                summary.append(f"  - 🔌 {point}")
        
        if dependencies_analysis['upstream_dependencies']:
            summary.append("**Upstream Dependencies:**")
            for dep in dependencies_analysis['upstream_dependencies']:
                summary.append(f"  - ⬆️ {dep}")
        
        if dependencies_analysis['downstream_dependencies']:
            summary.append("**Downstream Dependencies:**")
            for dep in dependencies_analysis['downstream_dependencies']:
                summary.append(f"  - ⬇️ {dep}")
        
        if dependencies_analysis['recommendations']:
            summary.append("**Recommendations:**")
            for rec in dependencies_analysis['recommendations']:
                summary.append(f"  - 💡 {rec}")
        
        return '\n'.join(summary) if summary else "No dependencies or blockers identified."
    
    def _create_dod_summary(self, dod_analysis: Dict) -> str:
        """Create a summary of Definition of Done analysis"""
        summary = []
        
        for dod_key, analysis in dod_analysis.items():
            dod_name = analysis['name']
            coverage = analysis['coverage_percentage']
            missing = analysis['missing_elements']
            suggestions = analysis['suggestions']
            
            summary.append(f"**{dod_name}**: {coverage:.1f}% coverage")
            if missing:
                summary.append(f"  Missing: {', '.join(missing)}")
            if suggestions:
                summary.append(f"  Suggestions: {', '.join(suggestions)}")
            summary.append("")
        
        return '\n'.join(summary)
    
    def _create_stakeholder_summary(self, stakeholder_analysis: Dict) -> str:
        """Create a summary of stakeholder validation analysis"""
        summary = []
        
        for section_key, section_data in stakeholder_analysis.items():
            section_name = section_key.replace('_', ' ').title()
            found = section_data['found']
            missing = section_data['missing']
            recommendation = section_data.get('recommendation', '')
            
            status = "✅ Found" if found else "❌ Missing"
            summary.append(f"**{section_name}**: {status}")
            
            if section_data.get('indicators'):
                for indicator in section_data['indicators']:
                    summary.append(f"  - {indicator}")
            
            if missing and recommendation:
                summary.append(f"  💡 {recommendation}")
            
            # Add visibility issue for PO approval
            if section_key == 'po_approval' and section_data.get('visibility_issue', False):
                visibility_rec = section_data.get('visibility_recommendation', '')
                if visibility_rec:
                    summary.append(f"  👁️ {visibility_rec}")
        
        return '\n'.join(summary)
    
    def _create_sprint_readiness_summary(self, sprint_readiness_analysis: Dict) -> str:
        """Create a summary of sprint readiness analysis"""
        summary = []
        
        readiness_status = "✅ Ready" if sprint_readiness_analysis['sprint_ready'] else "❌ Not Ready"
        summary.append(f"**Sprint Readiness**: {readiness_status}")
        
        if sprint_readiness_analysis['sprint_context'] != 'unknown':
            summary.append(f"**Sprint Context**: {sprint_readiness_analysis['sprint_context']}")
        
        if sprint_readiness_analysis['missing_for_sprint']:
            summary.append("**Missing for Sprint:**")
            for item in sprint_readiness_analysis['missing_for_sprint']:
                summary.append(f"  - ⚠️ {item}")
        
        if sprint_readiness_analysis['recommendations']:
            summary.append("**Recommendations:**")
            for rec in sprint_readiness_analysis['recommendations']:
                summary.append(f"  - 💡 {rec}")
        
        return '\n'.join(summary)
    
    def _create_cross_functional_summary(self, cross_functional_analysis: Dict) -> str:
        """Create a summary of cross-functional concerns analysis"""
        summary = []
        
        for concern_key, concern_data in cross_functional_analysis.items():
            if concern_key == 'general_recommendation':
                continue
                
            concern_name = concern_data['name']
            coverage = concern_data['coverage_score']
            missing = concern_data['missing']
            recommendations = concern_data['recommendations']
            
            status = "✅ Addressed" if not missing else "❌ Not Addressed"
            summary.append(f"**{concern_name}**: {status} ({coverage} indicators)")
            
            if concern_data['indicators_found']:
                summary.append(f"  Indicators: {', '.join(concern_data['indicators_found'])}")
            
            if recommendations:
                for rec in recommendations:
                    summary.append(f"  💡 {rec}")
        
        if cross_functional_analysis.get('general_recommendation'):
            summary.append(f"**General**: {cross_functional_analysis['general_recommendation']}")
        
        return '\n'.join(summary)

    def _create_test_scenarios_summary(self, test_scenarios_analysis: Dict) -> str:
        """Create summary for test scenarios analysis"""
        summary = []
        
        # Overall coverage status
        coverage_status = test_scenarios_analysis.get('overall_coverage', 'incomplete')
        if coverage_status == 'complete':
            summary.append("✅ **Test Scenarios**: Complete coverage (Happy Path, Negative, RBT, Cross-browser)")
        elif coverage_status == 'partial':
            summary.append("⚠️ **Test Scenarios**: Partial coverage - some areas missing")
        else:
            summary.append("🔴 **Test Scenarios**: Incomplete coverage - major gaps identified")
        
        # Individual category analysis
        categories = ['happy_path', 'negative', 'rbt', 'cross_browser']
        category_names = {
            'happy_path': 'Happy Path',
            'negative': 'Negative/Edge Cases',
            'rbt': 'RBT (Risk-Based Testing)',
            'cross_browser': 'Cross-browser/Device'
        }
        
        for category in categories:
            category_data = test_scenarios_analysis.get(category, {})
            status = category_data.get('status', 'not_found')
            category_name = category_names.get(category, category.replace('_', ' ').title())
            
            if status == 'found':
                coverage = category_data.get('coverage', [])
                summary.append(f"  ✅ **{category_name}**: {coverage[0] if coverage else 'Covered'}")
            else:
                missing = category_data.get('missing', [])
                summary.append(f"  🔴 **{category_name}**: {missing[0] if missing else 'Missing'}")
        
        # Recommendations
        recommendations = test_scenarios_analysis.get('recommendations', [])
        if recommendations:
            summary.append("\n**Recommendations:**")
            for rec in recommendations[:3]:  # Limit to 3 recommendations
                summary.append(f"  • {rec}")
        
        return '\n'.join(summary)
    
    def _create_checklist_summary(self, visual_checklist: Dict) -> str:
        """Create a summary of visual checklist"""
        summary = []
        
        status_emoji = {
            'green': '🟢',
            'yellow': '🟡', 
            'red': '🔴'
        }
        
        overall_status = visual_checklist['overall_status']
        summary.append(f"**Overall Status**: {status_emoji[overall_status]} {overall_status.upper()}")
        
        summary.append("**Section Status:**")
        for section_key, section_data in visual_checklist['sections'].items():
            section_name = section_data['name']
            section_status = section_data['status']
            completed = section_data['completed']
            total = section_data['total']
            percentage = section_data['percentage']
            
            status_icon = status_emoji[section_status]
            summary.append(f"  {status_icon} {section_name}: {completed}/{total} ({percentage:.0f}%)")
        
        checklist_summary = visual_checklist['summary']
        summary.append(f"**Summary**: {checklist_summary['completed_items']}/{checklist_summary['total_items']} items complete")
        
        # Add groom score
        groom_score_data = visual_checklist.get('groom_score', {})
        if groom_score_data:
            overall_percentage = (groom_score_data['overall_score'] / groom_score_data['total_possible'] * 100) if groom_score_data['total_possible'] > 0 else 0
            summary.append(f"**Groom Readiness Score**: {overall_percentage:.0f}%")
            
            if groom_score_data['critical_gaps']:
                summary.append("**Critical Gaps:**")
                for gap in groom_score_data['critical_gaps']:
                    summary.append(f"  🔴 {gap}")
        
        return '\n'.join(summary)
    
    def get_fallback_groom_analysis(self) -> str:
        """Return a fallback groom analysis if API fails"""
        return """
# 📋 Groom Analysis

*The groom analysis generator is temporarily unavailable! 🔧*

## 🔍 Key Issues to Address:
- **Check User Story Template** - Ensure "As a [user], I want [goal], so that [benefit]" format
- **Verify Acceptance Criteria** - Look for clear, testable criteria (separate from test scenarios)
- **Review Test Scenarios** - Check for Positive (Happy Path), Negative (Error/Edge Handling), RBT (Risk-Based Testing)
- **Review Framework Coverage** - Check R-O-I, I-N-V-E-S-T, A-C-C-E-P-T, and 3C Model elements
- **Brand Context** - Ensure brand abbreviations are used correctly
- **Figma Reference** - Check if Figma is properly attached vs just referenced
- **Cross-browser/Device Testing** - Confirm testing scope is defined

## 💡 General Recommendations:
- **Be specific** in user stories and acceptance criteria
- **Include examples** where appropriate
- **Define success criteria** clearly
- **Add context** for brand-specific requirements
- **Follow framework guidelines** for comprehensive coverage

## 🎯 Next Steps:
1. Review the ticket against the presentation frameworks
2. Identify missing elements from each framework
3. Add specific acceptance criteria
4. Ensure brand context is clear and accurate
5. Add comprehensive test scenarios (Happy Path, Negative, RBT, Cross-browser)
6. Calculate groom readiness score based on all field coverage

## 🔧 Technical Information:
- **Service Status**: Azure OpenAI API temporarily unavailable
- **Recommended Action**: Try again in a few minutes
- **Alternative**: Use manual framework checklist below

## 📋 Framework Checklist:
### R-O-I Framework
- [ ] **Role**: Clear user persona defined
- [ ] **Objective**: Specific goal or action stated
- [ ] **Insight**: Business value or benefit explained

### I-N-V-E-S-T Framework
- [ ] **Independent**: Can be developed/tested separately
- [ ] **Negotiable**: Scope can be adjusted if needed
- [ ] **Valuable**: Delivers business value
- [ ] **Estimable**: Effort can be estimated
- [ ] **Small**: Manageable size for one sprint
- [ ] **Testable**: Clear acceptance criteria

### A-C-C-E-P-T Criteria
- [ ] **Action**: Clear action or behavior defined
- [ ] **Condition**: When/if scenarios covered
- [ ] **Criteria**: Specific requirements listed
- [ ] **Expected Result**: Clear outcome defined
- [ ] **Pass-Fail**: Binary success criteria
- [ ] **Traceable**: Links to requirements/features

### Test Scenarios Checklist
- [ ] **Positive (Happy Path)**: Success scenarios defined
- [ ] **Negative (Error/Edge Handling)**: Error and edge cases covered
- [ ] **RBT (Risk-Based Testing)**: Risk assessment included
- [ ] **Cross-browser/Device Testing**: Scope confirmed Y/N
- [ ] **Figma Reference**: Properly attached vs just referenced

### 3C Model
- [ ] **Card**: Well-written user story
- [ ] **Conversation**: Team discussion points covered
- [ ] **Confirmation**: Acceptance criteria defined

*Please try again later or contact support if the issue persists.*
"""
    
    def save_groom_analysis(self, content: str, output_file: str):
        """Save groom analysis to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[green]Groom analysis saved to {output_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving file: {e}[/red]")
    
    def display_ascii_art(self):
        """Display ASCII art banner"""
        art = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██████╗ ██████╗  ██████╗ ███╗   ███╗    ██████╗  ██████╗ ║
    ║   ██╔════╝██╔═══██╗██╔═══██╗████╗ ████║    ██╔══██╗██╔═══██╗║
    ║   ██║     ██║   ██║██║   ██║██╔████╔██║    ██████╔╝██║   ██║║
    ║   ██║     ██║   ██║██║   ██║██║╚██╔╝██║    ██╔══██╗██║   ██║║
    ║   ╚██████╗╚██████╔╝╚██████╔╝██║ ╚═╝ ██║    ██║  ██║╚██████╔╝║
    ║    ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ║
    ║                                                              ║
    ║                    🧹 GROOM ROOM 🧹                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        console.print(art, style="blue") 

    def analyze_ticket_summary(self, content: str) -> Dict[str, any]:
        """Generate a concise summary of the Jira ticket"""
        analysis = {
            'summary': '',
            'card_type': 'unknown',
            'purpose': '',
            'confidence': 0
        }
        
        content_lower = content.lower()
        
        # Detect card type
        if any(indicator in content_lower for indicator in ['bug', 'broken', 'not working', 'error', 'issue']):
            analysis['card_type'] = 'Bug'
        elif any(indicator in content_lower for indicator in ['user story', 'as a', 'i want', 'so that']):
            analysis['card_type'] = 'Story'
        elif any(indicator in content_lower for indicator in ['task', 'enable', 'disable', 'documentation']):
            analysis['card_type'] = 'Task'
        elif any(indicator in content_lower for indicator in ['spike', 'research', 'investigation']):
            analysis['card_type'] = 'Spike'
        
        # Extract key information for summary
        lines = content.split('\n')
        summary_line = ''
        description_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if 'summary:' in line_lower or 'title:' in line_lower:
                summary_line = line.split(':', 1)[1].strip() if ':' in line else line.strip()
            elif 'description:' in line_lower:
                # Start collecting description
                continue
            elif summary_line and not line.strip():
                # Empty line after summary, likely end of description
                break
            elif summary_line:
                description_lines.append(line.strip())
        
        # Generate summary
        if summary_line:
            analysis['summary'] = summary_line
            analysis['purpose'] = f"This {analysis['card_type']} introduces {summary_line.lower()}"
            analysis['confidence'] = 0.8
        else:
            # Fallback: use first meaningful line
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    analysis['summary'] = line.strip()
                    analysis['purpose'] = f"This {analysis['card_type']} addresses {line.strip().lower()}"
                    analysis['confidence'] = 0.6
                    break
        
        return analysis

    def analyze_additional_jira_fields(self, content: str) -> Dict[str, Dict]:
        """Analyze additional Jira fields for comprehensive feedback"""
        analysis = {
            'implementation_details': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'ada_acceptance_criteria': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'architectural_solution': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'performance_impact': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'linked_issues': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'story_points': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'agile_team': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'components': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            },
            'brands': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'recommendations': []
            }
        }
        
        content_lower = content.lower()
        
        # Analyze Implementation Details
        implementation_indicators = ['implementation', 'technical approach', 'component', 'module', 'code ownership']
        if any(indicator in content_lower for indicator in implementation_indicators):
            analysis['implementation_details']['status'] = 'found'
            analysis['implementation_details']['coverage'].append('Technical approach mentioned')
            
            # Check for specific details
            if 'component' in content_lower or 'module' in content_lower:
                analysis['implementation_details']['coverage'].append('Component/module scope defined')
            else:
                analysis['implementation_details']['missing'].append('Component/module scope')
                analysis['implementation_details']['recommendations'].append('Add specific component/module information (e.g., "impacts Auth modal on PWA-MMT")')
        else:
            analysis['implementation_details']['missing'].append('Implementation details')
            analysis['implementation_details']['recommendations'].append('Add technical approach, component scope, or code ownership information')
        
        # Analyze ADA Acceptance Criteria
        ada_indicators = ['ada', 'accessibility', 'wcag', 'screen reader', 'keyboard navigation', 'aria', 'contrast']
        if any(indicator in content_lower for indicator in ada_indicators):
            analysis['ada_acceptance_criteria']['status'] = 'found'
            analysis['ada_acceptance_criteria']['coverage'].append('Accessibility requirements mentioned')
            
            # Check for specific ADA requirements
            if 'screen reader' in content_lower or 'aria' in content_lower:
                analysis['ada_acceptance_criteria']['coverage'].append('Screen reader support defined')
            else:
                analysis['ada_acceptance_criteria']['missing'].append('Screen reader support')
                analysis['ada_acceptance_criteria']['recommendations'].append('Add checks for screen-reader support and ARIA labels')
            
            if 'keyboard' in content_lower:
                analysis['ada_acceptance_criteria']['coverage'].append('Keyboard navigation defined')
            else:
                analysis['ada_acceptance_criteria']['missing'].append('Keyboard navigation')
                analysis['ada_acceptance_criteria']['recommendations'].append('Add keyboard navigation requirements')
        else:
            analysis['ada_acceptance_criteria']['missing'].append('ADA acceptance criteria')
            analysis['ada_acceptance_criteria']['recommendations'].append('Add checks for screen-reader support and ARIA labels')
        
        # Analyze Architectural Solution
        architecture_indicators = ['architecture', 'backend', 'integration', 'api', 'service', 'database', 'infrastructure']
        if any(indicator in content_lower for indicator in architecture_indicators):
            analysis['architectural_solution']['status'] = 'found'
            analysis['architectural_solution']['coverage'].append('Architecture/integration points mentioned')
            
            # Check for specific architectural details
            if 'backend' in content_lower or 'api' in content_lower:
                analysis['architectural_solution']['coverage'].append('Backend/API integration defined')
            else:
                analysis['architectural_solution']['missing'].append('Backend integration details')
                analysis['architectural_solution']['recommendations'].append('Clarify if it requires backend auth or service integration')
        else:
            analysis['architectural_solution']['missing'].append('Architectural solution')
            analysis['architectural_solution']['recommendations'].append('Clarify if it requires backend auth or loyalty service integration')
        
        # Analyze Performance Impact
        performance_indicators = ['performance', 'load', 'response time', 'async', 'optimization', 'threshold', 'nfr']
        if any(indicator in content_lower for indicator in performance_indicators):
            analysis['performance_impact']['status'] = 'found'
            analysis['performance_impact']['coverage'].append('Performance considerations mentioned')
            
            # Check for specific performance metrics
            if 'response time' in content_lower or 'threshold' in content_lower:
                analysis['performance_impact']['coverage'].append('Performance thresholds defined')
            else:
                analysis['performance_impact']['missing'].append('Performance thresholds')
                analysis['performance_impact']['recommendations'].append('Consider load thresholds, async loading, modal response time goals')
        else:
            analysis['performance_impact']['missing'].append('Performance impact evaluation')
            analysis['performance_impact']['recommendations'].append('Consider load thresholds, async loading, modal response time goals')
        
        # Analyze Linked Issues
        linked_indicators = ['linked', 'dependency', 'blocked by', 'depends on', 'related', 'upstream', 'downstream']
        if any(indicator in content_lower for indicator in linked_indicators):
            analysis['linked_issues']['status'] = 'found'
            analysis['linked_issues']['coverage'].append('Dependencies/related issues mentioned')
            
            # Check for specific linkage types
            if 'upstream' in content_lower or 'downstream' in content_lower:
                analysis['linked_issues']['coverage'].append('Upstream/downstream linkage noted')
            else:
                analysis['linked_issues']['missing'].append('Upstream/downstream linkage')
                analysis['linked_issues']['recommendations'].append('Check if upstream/downstream linkage is noted')
        else:
            analysis['linked_issues']['missing'].append('Linked issues/dependencies')
            analysis['linked_issues']['recommendations'].append('Check if upstream/downstream linkage is noted')
        
        # Analyze Story Points (from custom fields)
        story_points_indicators = ['story points', 'points', 'estimate', 'effort', 'story point']
        if any(indicator in content_lower for indicator in story_points_indicators):
            analysis['story_points']['status'] = 'found'
            analysis['story_points']['coverage'].append('Story points/effort estimation mentioned')
            
            # Check for numeric values
            import re
            points_match = re.search(r'(\d+)\s*(?:story\s*)?points?', content_lower)
            if points_match:
                analysis['story_points']['coverage'].append(f'Story points value: {points_match.group(1)}')
            else:
                analysis['story_points']['missing'].append('Specific story points value')
                analysis['story_points']['recommendations'].append('Add specific story points value (e.g., "5 story points")')
        else:
            analysis['story_points']['missing'].append('Story points estimation')
            analysis['story_points']['recommendations'].append('Add story points for effort estimation')
        
        # Analyze Agile Team
        agile_team_indicators = ['agile team', 'team', 'squad', 'scrum team', 'development team']
        if any(indicator in content_lower for indicator in agile_team_indicators):
            analysis['agile_team']['status'] = 'found'
            analysis['agile_team']['coverage'].append('Agile team assignment mentioned')
            
            # Check for specific team names
            team_names = ['everest', 'silver surfers', 'batman', 'pwa kit', 'odcd']
            found_team = None
            for team in team_names:
                if team in content_lower:
                    found_team = team
                    break
            
            if found_team:
                analysis['agile_team']['coverage'].append(f'Specific team identified: {found_team}')
            else:
                analysis['agile_team']['missing'].append('Specific team identification')
                analysis['agile_team']['recommendations'].append('Specify the agile team (e.g., "ODCD Everest", "Silver Surfers")')
        else:
            analysis['agile_team']['missing'].append('Agile team assignment')
            analysis['agile_team']['recommendations'].append('Specify the agile team assignment')
        
        # Analyze Components
        components_indicators = ['components', 'component', 'module', 'feature', 'area']
        if any(indicator in content_lower for indicator in components_indicators):
            analysis['components']['status'] = 'found'
            analysis['components']['coverage'].append('Component/module information mentioned')
            
            # Check for specific component types
            component_types = ['auth', 'payment', 'checkout', 'pdp', 'plp', 'homepage', 'cart', 'search']
            found_components = []
            for comp_type in component_types:
                if comp_type in content_lower:
                    found_components.append(comp_type)
            
            if found_components:
                analysis['components']['coverage'].append(f'Specific components: {", ".join(found_components)}')
            else:
                analysis['components']['missing'].append('Specific component identification')
                analysis['components']['recommendations'].append('Specify affected components (e.g., "Auth modal", "Checkout flow")')
        else:
            analysis['components']['missing'].append('Component information')
            analysis['components']['recommendations'].append('Specify affected components or modules')
        
        # Analyze Brands
        brands_indicators = ['brands', 'brand', 'mmt', 'exo', 'ycc', 'elf', 'emea']
        if any(indicator in content_lower for indicator in brands_indicators):
            analysis['brands']['status'] = 'found'
            analysis['brands']['coverage'].append('Brand information mentioned')
            
            # Check for specific brand abbreviations
            brand_abbreviations = ['mmt', 'exo', 'ycc', 'elf', 'emea']
            found_brands = []
            for brand in brand_abbreviations:
                if brand in content_lower:
                    found_brands.append(brand.upper())
            
            if found_brands:
                analysis['brands']['coverage'].append(f'Specific brands: {", ".join(found_brands)}')
            else:
                analysis['brands']['missing'].append('Specific brand identification')
                analysis['brands']['recommendations'].append('Specify target brands (e.g., "MMT", "YCC", "ELF")')
        else:
            analysis['brands']['missing'].append('Brand information')
            analysis['brands']['recommendations'].append('Specify target brands for the feature')
        
        return analysis

    def analyze_enhanced_test_scenarios(self, content: str) -> Dict[str, Dict]:
        """Enhanced analysis of Test Scenarios field with detailed breakdown"""
        analysis = {
            'happy_path': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'details': ''
            },
            'negative': {
                'status': 'not_found', 
                'coverage': [],
                'missing': [],
                'details': ''
            },
            'rbt': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'details': ''
            },
            'cross_browser': {
                'status': 'not_found',
                'coverage': [],
                'missing': [],
                'details': ''
            },
            'overall_coverage': 'incomplete',
            'detailed_feedback': [],
            'recommendations': []
        }
        
        # Extract test scenarios section
        test_scenarios_section = self._extract_test_scenarios_section(content)
        
        if test_scenarios_section:
            # Analyze Happy Path (Positive) scenarios
            happy_path_indicators = ['happy path', 'positive', 'success', 'normal flow', 'expected behavior', 'valid input']
            if any(indicator in test_scenarios_section.lower() for indicator in happy_path_indicators):
                analysis['happy_path']['status'] = 'found'
                analysis['happy_path']['coverage'].append('Positive (Happy Path): ✅ Documented')
                
                # Extract specific details
                lines = test_scenarios_section.split('\n')
                for line in lines:
                    if any(indicator in line.lower() for indicator in happy_path_indicators):
                        analysis['happy_path']['details'] = line.strip()
                        break
            else:
                analysis['happy_path']['status'] = 'missing'
                analysis['happy_path']['missing'].append('Positive (Happy Path): ❌ Missing')
                analysis['detailed_feedback'].append('Happy Path scenarios not found - add normal user flow testing')
            
            # Analyze Negative/Error scenarios
            negative_indicators = ['negative', 'error', 'edge case', 'exception', 'invalid', 'failure', 'unauthorized', 'forbidden']
            if any(indicator in test_scenarios_section.lower() for indicator in negative_indicators):
                analysis['negative']['status'] = 'found'
                analysis['negative']['coverage'].append('Negative/Error Handling: ✅ Documented')
                
                # Extract specific details
                lines = test_scenarios_section.split('\n')
                for line in lines:
                    if any(indicator in line.lower() for indicator in negative_indicators):
                        analysis['negative']['details'] = line.strip()
                        break
            else:
                analysis['negative']['status'] = 'missing'
                analysis['negative']['missing'].append('Negative/Error Handling: ❌ Missing')
                analysis['detailed_feedback'].append('Error handling scenarios not found - add edge case and exception testing')
            
            # Analyze RBT (Risk-Based Testing) scenarios
            rbt_indicators = ['rbt', 'risk-based', 'risk based', 'risk assessment', 'risk analysis', 'critical path', 'high impact']
            if any(indicator in test_scenarios_section.lower() for indicator in rbt_indicators):
                analysis['rbt']['status'] = 'found'
                analysis['rbt']['coverage'].append('RBT: ✅ Documented')
                
                # Extract specific details
                lines = test_scenarios_section.split('\n')
                for line in lines:
                    if any(indicator in line.lower() for indicator in rbt_indicators):
                        analysis['rbt']['details'] = line.strip()
                        break
            else:
                analysis['rbt']['status'] = 'missing'
                analysis['rbt']['missing'].append('RBT: ❌ Missing')
                analysis['detailed_feedback'].append('Risk-based testing not found - add critical path and high-impact scenario testing')
            
            # Analyze Cross-browser/Device testing
            cross_browser_indicators = ['cross-browser', 'cross browser', 'device', 'mobile', 'responsive', 'browser compatibility', 'platform']
            if any(indicator in test_scenarios_section.lower() for indicator in cross_browser_indicators):
                analysis['cross_browser']['status'] = 'found'
                analysis['cross_browser']['coverage'].append('Cross-browser/device: ✅ Documented')
                
                # Extract specific details
                lines = test_scenarios_section.split('\n')
                for line in lines:
                    if any(indicator in line.lower() for indicator in cross_browser_indicators):
                        analysis['cross_browser']['details'] = line.strip()
                        break
            else:
                analysis['cross_browser']['status'] = 'missing'
                analysis['cross_browser']['missing'].append('Cross-browser/device: ❌ Not mentioned')
                analysis['detailed_feedback'].append('Cross-browser/device testing not mentioned - specify device/browser scope')
        else:
            # Also check the full content for test scenario indicators
            content_lower = content.lower()
            
            # Check for Happy Path
            if any(indicator in content_lower for indicator in ['happy path', 'positive', 'success']):
                analysis['happy_path']['status'] = 'found'
                analysis['happy_path']['coverage'].append('Positive (Happy Path): ✅ Documented')
            else:
                analysis['happy_path']['status'] = 'missing'
                analysis['happy_path']['missing'].append('Positive (Happy Path): ❌ Missing')
            
            # Check for Negative/Error
            if any(indicator in content_lower for indicator in ['negative', 'error', 'edge case']):
                analysis['negative']['status'] = 'found'
                analysis['negative']['coverage'].append('Negative/Error Handling: ✅ Documented')
            else:
                analysis['negative']['status'] = 'missing'
                analysis['negative']['missing'].append('Negative/Error Handling: ❌ Missing')
            
            # Check for RBT
            if any(indicator in content_lower for indicator in ['rbt', 'risk-based', 'risk based']):
                analysis['rbt']['status'] = 'found'
                analysis['rbt']['coverage'].append('RBT: ✅ Documented')
            else:
                analysis['rbt']['status'] = 'missing'
                analysis['rbt']['missing'].append('RBT: ❌ Missing')
            
            # Check for Cross-browser
            if any(indicator in content_lower for indicator in ['cross-browser', 'cross browser', 'device']):
                analysis['cross_browser']['status'] = 'found'
                analysis['cross_browser']['coverage'].append('Cross-browser/device: ✅ Documented')
            else:
                analysis['cross_browser']['status'] = 'missing'
                analysis['cross_browser']['missing'].append('Cross-browser/device: ❌ Not mentioned')
            
            # Add feedback for missing test scenarios section
            analysis['detailed_feedback'].append('No Test Scenarios field found - add comprehensive testing coverage')
        
        # Determine overall coverage
        found_count = sum(1 for category in ['happy_path', 'negative', 'rbt', 'cross_browser'] 
                         if analysis[category]['status'] == 'found')
        
        if found_count == 4:
            analysis['overall_coverage'] = 'complete'
        elif found_count >= 2:
            analysis['overall_coverage'] = 'partial'
        else:
            analysis['overall_coverage'] = 'incomplete'
        
        # Generate recommendations
        if analysis['overall_coverage'] != 'complete':
            missing_categories = []
            for category in ['happy_path', 'negative', 'rbt', 'cross_browser']:
                if analysis[category]['status'] == 'missing':
                    missing_categories.append(category.replace('_', ' ').title())
            
            if missing_categories:
                analysis['recommendations'].append(f"Expand coverage to include: {', '.join(missing_categories)}")
        
        return analysis

    def _create_ticket_summary_summary(self, ticket_summary_analysis: Dict) -> str:
        """Create a summary of ticket summary analysis"""
        summary = []
        
        if ticket_summary_analysis['summary']:
            summary.append(f"**Ticket Summary**: {ticket_summary_analysis['summary']}")
            summary.append(f"**Card Type**: {ticket_summary_analysis['card_type']}")
            summary.append(f"**Purpose**: {ticket_summary_analysis['purpose']}")
            summary.append(f"**Confidence**: {ticket_summary_analysis['confidence']:.1f}")
        else:
            summary.append("**Ticket Summary**: Unable to extract summary")
            summary.append("**Card Type**: Unknown")
            summary.append("**Purpose**: Not determined")
        
        return '\n'.join(summary)

    def _create_additional_jira_fields_summary(self, additional_fields_analysis: Dict) -> str:
        """Create a summary of additional Jira fields analysis"""
        summary = []
        
        field_names = {
            'implementation_details': 'Implementation Details',
            'ada_acceptance_criteria': 'ADA Acceptance Criteria',
            'architectural_solution': 'Architectural Solution',
            'performance_impact': 'Performance Impact',
            'linked_issues': 'Linked Issues',
            'story_points': 'Story Points',
            'agile_team': 'Agile Team',
            'components': 'Components',
            'brands': 'Brands'
        }
        
        summary.append("**Additional Jira Fields Analysis:**")
        
        for field_key, field_name in field_names.items():
            field_data = additional_fields_analysis.get(field_key, {})
            status = field_data.get('status', 'not_found')
            
            if status == 'found':
                coverage = field_data.get('coverage', [])
                summary.append(f"  ✅ **{field_name}**: {coverage[0] if coverage else 'Present'}")
            else:
                missing = field_data.get('missing', [])
                summary.append(f"  ❌ **{field_name}**: {missing[0] if missing else 'Missing'}")
        
        # Add recommendations
        all_recommendations = []
        for field_data in additional_fields_analysis.values():
            recommendations = field_data.get('recommendations', [])
            all_recommendations.extend(recommendations)
        
        if all_recommendations:
            summary.append("\n**Recommendations:**")
            for rec in all_recommendations[:5]:  # Limit to 5 recommendations
                summary.append(f"  • {rec}")
        
        return '\n'.join(summary)

    def _create_enhanced_test_scenarios_summary(self, enhanced_test_scenarios_analysis: Dict) -> str:
        """Create summary for enhanced test scenarios analysis"""
        if not enhanced_test_scenarios_analysis:
            return "Enhanced Test Scenarios Analysis: No data available"
        
        summary = []
        summary.append("**Enhanced Test Scenarios Analysis:**")
        
        # Field presence
        if enhanced_test_scenarios_analysis.get('test_scenarios_field_present'):
            summary.append("- Test Scenarios field: ✅ Present")
        else:
            summary.append("- Test Scenarios field: ❌ Missing")
            summary.append("  - Add comprehensive test scenarios including Positive, Negative, RBT, and Cross-browser coverage")
            return '\n'.join(summary)
        
        # Coverage analysis
        coverage = enhanced_test_scenarios_analysis.get('coverage_analysis', {})
        summary.append("\n**Coverage Breakdown:**")
        
        for category, data in coverage.items():
            if data.get('status') == 'found':
                summary.append(f"- {category.replace('_', ' ').title()}: ✅ {data.get('coverage', ['Mentioned'])[0]}")
            else:
                summary.append(f"- {category.replace('_', ' ').title()}: ❌ {data.get('missing', ['Missing'])[0]}")
        
        # Field quality
        quality = enhanced_test_scenarios_analysis.get('field_quality', 'poor')
        summary.append(f"\n**Field Quality:** {quality.title()}")
        
        # Misuse detection
        if enhanced_test_scenarios_analysis.get('misuse_detected'):
            summary.append("\n**⚠️ Field Misuse Detected:**")
            for detail in enhanced_test_scenarios_analysis.get('misuse_details', []):
                summary.append(f"- {detail}")
        
        # Recommendations
        recommendations = enhanced_test_scenarios_analysis.get('recommendations', [])
        if recommendations:
            summary.append("\n**Recommendations:**")
            for rec in recommendations:
                summary.append(f"- {rec}")
        
        return '\n'.join(summary)
    
    def _create_enhanced_acceptance_criteria_summary(self, enhanced_ac_analysis: Dict) -> str:
        """Create summary for enhanced acceptance criteria analysis"""
        if not enhanced_ac_analysis:
            return "Enhanced Acceptance Criteria Analysis: No data available"
        
        summary = []
        summary.append("**Enhanced Acceptance Criteria Analysis:**")
        
        # AC presence
        if enhanced_ac_analysis.get('ac_present'):
            summary.append("- AC present: ✅")
        else:
            summary.append("- AC present: ❌")
            summary.append("  - Add specific requirements and success criteria")
            return '\n'.join(summary)
        
        # Overall quality
        quality = enhanced_ac_analysis.get('overall_quality', 'poor')
        summary.append(f"- Overall quality: {quality.title()}")
        
        # Validation results
        validation = enhanced_ac_analysis.get('validation_results', {})
        summary.append("\n**Validation Results:**")
        
        for validation_type, data in validation.items():
            if data.get('status'):
                summary.append(f"- {validation_type.replace('_', ' ').title()}: ✅ {data.get('details', 'Valid')}")
            else:
                summary.append(f"- {validation_type.replace('_', ' ').title()}: ❌ Missing")
        
        # Vague AC detection
        vague_ac = enhanced_ac_analysis.get('vague_ac_detected', [])
        if vague_ac:
            summary.append("\n**⚠️ Vague AC Detected:**")
            for vague_item in vague_ac:
                summary.append(f"- {vague_item.get('issue', 'Vague AC found')}")
        
        # Figma links
        figma_links = enhanced_ac_analysis.get('figma_links', [])
        if figma_links:
            summary.append("\n**🎨 Figma Design Reference:**")
            for link in figma_links:
                summary.append(f"- Figma link detected: ✅ {link.get('url', 'URL')}")
                if link.get('is_generic'):
                    summary.append(f"  - Design frame or state references: ❌ Not specified")
                    summary.append(f"  - Contextual guidance: ❌ AC just says 'match Figma'")
                else:
                    summary.append(f"  - Design frame or state references: ✅ Specified")
                    summary.append(f"  - Contextual guidance: ✅ Behavioral expectations included")
                summary.append(f"  - Recommendation: {link.get('recommendation', 'Consider moving to Design field')}")
        
        # Test scenarios in AC
        if enhanced_ac_analysis.get('test_scenarios_in_ac'):
            summary.append("\n**⚠️ Test Scenarios in AC:**")
            summary.append("- Test scenarios were found inside Acceptance Criteria. Please move them to the dedicated 'Test Scenarios' field for clarity.")
        
        # Recommendations
        recommendations = enhanced_ac_analysis.get('recommendations', [])
        if recommendations:
            summary.append("\n**Recommendations:**")
            for rec in recommendations:
                summary.append(f"- {rec}")
        
        return '\n'.join(summary)

    def analyze_enhanced_acceptance_criteria(self, content: str) -> Dict[str, Dict]:
        """Enhanced analysis of Acceptance Criteria field with detailed validation"""
        analysis = {
            'ac_present': False,
            'ac_content': '',
            'validation_results': {
                'intent_defined': {'status': False, 'details': '', 'issues': []},
                'conditions_specified': {'status': False, 'details': '', 'issues': []},
                'expected_results': {'status': False, 'details': '', 'issues': []},
                'pass_fail_logic': {'status': False, 'details': '', 'issues': []}
            },
            'vague_ac_detected': [],
            'figma_links': [],
            'test_scenarios_in_ac': False,
            'overall_quality': 'poor',
            'recommendations': []
        }
        
        # Extract Acceptance Criteria section
        ac_section = self._extract_acceptance_criteria_section(content)
        
        if ac_section:
            analysis['ac_present'] = True
            analysis['ac_content'] = ac_section
            
            # Check for Figma links in AC
            figma_links = self._detect_figma_links(ac_section)
            if figma_links:
                analysis['figma_links'] = figma_links
                analysis['recommendations'].append('Figma links detected in AC - consider moving to dedicated Design/Attachments field')
            
            # Check if test scenarios are embedded in AC (grooming issue)
            if self._detect_test_scenarios_in_ac(ac_section):
                analysis['test_scenarios_in_ac'] = True
                analysis['recommendations'].append('Test scenarios found in AC - move to dedicated "Test Scenarios" field for clarity')
            
            # Validate each AC line
            ac_lines = [line.strip() for line in ac_section.split('\n') if line.strip()]
            
            for line in ac_lines:
                # Skip empty lines and section headers
                if not line or line.lower().startswith(('acceptance criteria', 'ac:', 'criteria:')):
                    continue
                
                # Check for vague AC patterns
                vague_patterns = [
                    r'should match figma',
                    r'works like current version',
                    r'fixes the bug',
                    r'as expected',
                    r'properly',
                    r'correctly',
                    r'as designed'
                ]
                
                for pattern in vague_patterns:
                    if re.search(pattern, line.lower()):
                        analysis['vague_ac_detected'].append({
                            'line': line,
                            'issue': f"Vague AC: '{pattern}' lacks specific behavior or edge case handling"
                        })
                        break
                
                # Validate AC structure
                self._validate_ac_line(line, analysis)
            
            # Determine overall quality
            valid_count = sum(1 for validation in analysis['validation_results'].values() 
                            if validation['status'])
            
            if valid_count == 4:
                analysis['overall_quality'] = 'excellent'
            elif valid_count >= 3:
                analysis['overall_quality'] = 'good'
            elif valid_count >= 2:
                analysis['overall_quality'] = 'fair'
            else:
                analysis['overall_quality'] = 'poor'
            
            # Generate recommendations
            if analysis['vague_ac_detected']:
                analysis['recommendations'].append('Rewrite vague AC to define conditions and outcomes clearly. Follow: "When [condition], then [expected result]"')
            
            missing_validations = [key for key, validation in analysis['validation_results'].items() 
                                 if not validation['status']]
            if missing_validations:
                analysis['recommendations'].append(f'Add missing AC elements: {", ".join(missing_validations)}')
        
        else:
            analysis['recommendations'].append('No Acceptance Criteria field found - add specific requirements and success criteria')
        
        return analysis
    
    def _extract_acceptance_criteria_section(self, content: str) -> str:
        """Extract Acceptance Criteria section from content"""
        
        # Look for Acceptance Criteria section
        ac_patterns = [
            r'acceptance criteria[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'ac:[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'criteria[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        for pattern in ac_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _detect_figma_links(self, content: str) -> List[Dict]:
        """Detect and analyze Figma links in content"""
        figma_links = []
        
        # Regex pattern for Figma links
        figma_pattern = r'https?://(?:www\.)?figma\.com/file/[a-zA-Z0-9_-]+'
        
        matches = re.finditer(figma_pattern, content, re.IGNORECASE)
        
        for match in matches:
            figma_url = match.group(0)
            
            # Check if link has context/references
            context_indicators = [
                'frame', 'screen', 'design', 'mockup', 'wireframe', 'prototype',
                'modal', 'button', 'form', 'layout', 'component'
            ]
            
            has_context = any(indicator in content.lower() for indicator in context_indicators)
            has_behavioral_expectation = any(term in content.lower() for term in [
                'should', 'must', 'expected', 'when', 'then', 'user', 'click', 'see'
            ])
            
            figma_links.append({
                'url': figma_url,
                'has_context': has_context,
                'has_behavioral_expectation': has_behavioral_expectation,
                'is_generic': not has_context and not has_behavioral_expectation,
                'recommendation': self._generate_figma_recommendation(has_context, has_behavioral_expectation)
            })
        
        return figma_links
    
    def _generate_figma_recommendation(self, has_context: bool, has_behavioral_expectation: bool) -> str:
        """Generate recommendation for Figma link usage"""
        if not has_context and not has_behavioral_expectation:
            return "Replace vague instruction 'match Figma' with specific expectations: layout, states, validations, animations"
        elif not has_context:
            return "Specify what part of the Figma file the ticket refers to (e.g., 'Sign-Up Modal v3 – Frame #2')"
        elif not has_behavioral_expectation:
            return "Include behavioral expectations alongside Figma reference"
        else:
            return "Consider moving Figma link to dedicated Design/Attachments field for better visibility"
    
    def _detect_test_scenarios_in_ac(self, ac_content: str) -> bool:
        """Detect if test scenarios are embedded in Acceptance Criteria"""
        test_scenario_indicators = [
            'test scenario', 'test case', 'positive test', 'negative test', 
            'rbt', 'risk-based', 'happy path', 'edge case', 'error handling'
        ]
        
        ac_lower = ac_content.lower()
        return any(indicator in ac_lower for indicator in test_scenario_indicators)
    
    def _validate_ac_line(self, line: str, analysis: Dict):
        """Validate a single AC line for required elements"""
        line_lower = line.lower()
        
        # Check for Intent (what the user should experience or trigger)
        intent_indicators = ['user', 'customer', 'visitor', 'should', 'must', 'will', 'can', 'able to']
        if any(indicator in line_lower for indicator in intent_indicators):
            analysis['validation_results']['intent_defined']['status'] = True
            analysis['validation_results']['intent_defined']['details'] = 'User intent clearly defined'
        else:
            analysis['validation_results']['intent_defined']['issues'].append(f'Line lacks user intent: "{line}"')
        
        # Check for Conditions (input or state required)
        condition_indicators = ['when', 'if', 'given', 'upon', 'after', 'before', 'while', 'during']
        if any(indicator in line_lower for indicator in condition_indicators):
            analysis['validation_results']['conditions_specified']['status'] = True
            analysis['validation_results']['conditions_specified']['details'] = 'Conditions specified'
        else:
            analysis['validation_results']['conditions_specified']['issues'].append(f'Line lacks conditions: "{line}"')
        
        # Check for Expected Result (clear outcome)
        result_indicators = ['then', 'result', 'outcome', 'see', 'display', 'show', 'appear', 'receive']
        if any(indicator in line_lower for indicator in result_indicators):
            analysis['validation_results']['expected_results']['status'] = True
            analysis['validation_results']['expected_results']['details'] = 'Expected results defined'
        else:
            analysis['validation_results']['expected_results']['issues'].append(f'Line lacks expected result: "{line}"')
        
        # Check for Pass/Fail Logic
        pass_fail_indicators = ['success', 'failure', 'error', 'invalid', 'correct', 'incorrect', 'pass', 'fail']
        if any(indicator in line_lower for indicator in pass_fail_indicators):
            analysis['validation_results']['pass_fail_logic']['status'] = True
            analysis['validation_results']['pass_fail_logic']['details'] = 'Pass/fail logic present'
        else:
            analysis['validation_results']['pass_fail_logic']['issues'].append(f'Line lacks pass/fail logic: "{line}"')
    
    def analyze_enhanced_test_scenarios_v2(self, content: str) -> Dict[str, Dict]:
        """Enhanced Test Scenarios analysis with NLP-based detection and detailed breakdown"""
        analysis = {
            'test_scenarios_field_present': False,
            'test_scenarios_content': '',
            'coverage_analysis': {
                'positive': {'status': 'not_found', 'coverage': [], 'missing': [], 'details': ''},
                'negative': {'status': 'not_found', 'coverage': [], 'missing': [], 'details': ''},
                'rbt': {'status': 'not_found', 'coverage': [], 'missing': [], 'details': ''},
                'cross_browser': {'status': 'not_found', 'coverage': [], 'missing': [], 'details': ''}
            },
            'field_quality': 'poor',
            'misuse_detected': False,
            'misuse_details': [],
            'recommendations': []
        }
        
        # Extract Test Scenarios field
        test_scenarios_section = self._extract_test_scenarios_field(content)
        
        if test_scenarios_section:
            analysis['test_scenarios_field_present'] = True
            analysis['test_scenarios_content'] = test_scenarios_section
            
            # Check for field misuse
            misuse_indicators = self._detect_test_scenarios_misuse(test_scenarios_section)
            if misuse_indicators:
                analysis['misuse_detected'] = True
                analysis['misuse_details'] = misuse_indicators
                analysis['recommendations'].append('Test Scenarios field appears to be misused - ensure it contains actual test scenarios, not copied AC or irrelevant notes')
            
            # Analyze coverage using enhanced NLP patterns
            self._analyze_test_scenario_coverage(test_scenarios_section, analysis)
            
            # Determine field quality
            found_categories = sum(1 for category in analysis['coverage_analysis'].values() 
                                 if category['status'] == 'found')
            
            if found_categories == 4:
                analysis['field_quality'] = 'excellent'
            elif found_categories >= 3:
                analysis['field_quality'] = 'good'
            elif found_categories >= 2:
                analysis['field_quality'] = 'fair'
            else:
                analysis['field_quality'] = 'poor'
            
            # Generate recommendations
            missing_categories = []
            for category_name, category_data in analysis['coverage_analysis'].items():
                if category_data['status'] == 'not_found':
                    missing_categories.append(category_name.replace('_', ' ').title())
            
            if missing_categories:
                analysis['recommendations'].append(f'Add missing test types: {", ".join(missing_categories)}')
                analysis['recommendations'].append('Include device/browser matrix if applicable')
        
        else:
            analysis['recommendations'].append('No Test Scenarios field found - add comprehensive test coverage')
        
        return analysis
    
    def _extract_test_scenarios_field(self, content: str) -> str:
        """Extract Test Scenarios field specifically (not embedded in AC)"""
        
        # Look for dedicated Test Scenarios field
        test_scenarios_patterns = [
            r'test scenarios[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'test scenarios field[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'scenarios[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'testing[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        for pattern in test_scenarios_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _detect_test_scenarios_misuse(self, content: str) -> List[str]:
        """Detect if Test Scenarios field is being misused"""
        misuse_indicators = []
        
        content_lower = content.lower()
        
        # Check if it's just copied AC
        ac_indicators = ['acceptance criteria', 'user story', 'as a', 'i want', 'so that']
        if any(indicator in content_lower for indicator in ac_indicators):
            misuse_indicators.append('Contains Acceptance Criteria content instead of test scenarios')
        
        # Check if it's empty or irrelevant
        if len(content.strip()) < 20:
            misuse_indicators.append('Field appears to be empty or contains minimal content')
        
        # Check for irrelevant notes
        irrelevant_indicators = ['todo', 'tbd', 'to be determined', 'pending', 'notes:', 'comments:']
        if any(indicator in content_lower for indicator in irrelevant_indicators):
            misuse_indicators.append('Contains irrelevant notes or placeholders instead of test scenarios')
        
        return misuse_indicators
    
    def _analyze_test_scenario_coverage(self, content: str, analysis: Dict):
        """Analyze test scenario coverage using enhanced NLP patterns"""
        content_lower = content.lower()
        
        # Enhanced Positive (Happy Path) detection
        positive_patterns = [
            r'positive[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'happy path[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'success[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'valid[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'expected[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        positive_indicators = ['happy path', 'positive', 'success', 'valid', 'correct', 'expected', 'normal flow']
        if any(indicator in content_lower for indicator in positive_indicators):
            analysis['coverage_analysis']['positive']['status'] = 'found'
            analysis['coverage_analysis']['positive']['coverage'].append('Positive (Happy Path): ✅ Mentioned')
            
            # Extract specific details
            for pattern in positive_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    analysis['coverage_analysis']['positive']['details'] = match.group(1).strip()
                    break
        else:
            analysis['coverage_analysis']['positive']['status'] = 'missing'
            analysis['coverage_analysis']['positive']['missing'].append('Positive (Happy Path): ❌ Missing')
        
        # Enhanced Negative (Error/Edge Handling) detection
        negative_patterns = [
            r'negative[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'error[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'edge case[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'exception[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'invalid[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        negative_indicators = ['negative', 'error', 'edge case', 'exception', 'invalid', 'failed', 'unauthorized', 'forbidden', 'denied', 'timeout', 'broken']
        if any(indicator in content_lower for indicator in negative_indicators):
            analysis['coverage_analysis']['negative']['status'] = 'found'
            analysis['coverage_analysis']['negative']['coverage'].append('Negative (Error/Edge Handling): ✅ Mentioned')
            
            # Extract specific details
            for pattern in negative_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    analysis['coverage_analysis']['negative']['details'] = match.group(1).strip()
                    break
        else:
            analysis['coverage_analysis']['negative']['status'] = 'missing'
            analysis['coverage_analysis']['negative']['missing'].append('Negative (Error/Edge Handling): ❌ Missing')
        
        # Enhanced RBT (Risk-Based Testing) detection
        rbt_patterns = [
            r'rbt[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'risk-based[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'risk based[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'risk assessment[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        rbt_indicators = ['rbt', 'risk-based', 'risk based', 'risk assessment', 'risk analysis', 'critical path', 'high impact', 'data corruption', 'edge', 'performance', 'integration']
        if any(indicator in content_lower for indicator in rbt_indicators):
            analysis['coverage_analysis']['rbt']['status'] = 'found'
            analysis['coverage_analysis']['rbt']['coverage'].append('RBT: 🟡 Mentioned but may need clarification')
            
            # Extract specific details
            for pattern in rbt_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    analysis['coverage_analysis']['rbt']['details'] = match.group(1).strip()
                    break
        else:
            analysis['coverage_analysis']['rbt']['status'] = 'missing'
            analysis['coverage_analysis']['rbt']['missing'].append('RBT: ❌ Missing')
        
        # Enhanced Cross-browser/Device testing detection
        cross_browser_patterns = [
            r'cross-browser[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'cross browser[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'device[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'mobile[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            r'responsive[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        cross_browser_indicators = ['cross-browser', 'cross browser', 'device', 'mobile', 'responsive', 'browser compatibility', 'ios', 'android', 'chrome', 'safari', 'firefox', 'edge']
        if any(indicator in content_lower for indicator in cross_browser_indicators):
            analysis['coverage_analysis']['cross_browser']['status'] = 'found'
            analysis['coverage_analysis']['cross_browser']['coverage'].append('Cross-browser/device: ✅ Mentioned')
            
            # Extract specific details
            for pattern in cross_browser_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    analysis['coverage_analysis']['cross_browser']['details'] = match.group(1).strip()
                    break
        else:
            analysis['coverage_analysis']['cross_browser']['status'] = 'missing'
            analysis['coverage_analysis']['cross_browser']['missing'].append('Cross-browser/device: ❌ Not defined')

    # ============================================================================
    # NEW METHODS FOR JIRA FIELD READING ACCURACY FIXES
    # ============================================================================

    def detect_user_story_enhanced(self, content: str) -> Dict[str, any]:
        """
        Enhanced user story detection that scans both description and Acceptance Criteria fields
        Fixes false negatives on tickets like ODCD-33741
        """
        analysis = {
            'user_story_found': False,
            'location': None,
            'pattern_matched': None,
            'confidence': 0.0,
            'debug_info': []
        }
        
        # Enhanced regex patterns to catch variations
        user_story_patterns = [
            r"As a .*?, I want .*?, so that .*?\.",
            r"As a .*? I want .*? so that .*?\.",
            r"As a .*?, I want .*? so I can .*?\.",
            r"As a .*? I want to .*? so that .*?\.",
            r"As a .*?, I want to .*? so I can .*?\.",
            r"As a .*? I want .*? so I can .*?\.",
            r"As a .*?, I want .*? so that .*?",
            r"As a .*? I want .*? so that .*?",
            r"As a .*?, I want .*? so I can .*?",
            r"As a .*? I want to .*? so that .*?",
            r"As a .*?, I want to .*? so I can .*?",
            r"As a .*? I want .*? so I can .*?",
            # Additional patterns for variations
            r"As a .*?, I want .*?, so I can .*?\.",
            r"As a .*? I want .*?, so I can .*?\.",
            r"As a .*?, I want to .*?, so that .*?\.",
            r"As a .*? I want to .*?, so that .*?\.",
            r"As a .*?, I want to .*?, so I can .*?\.",
            r"As a .*? I want to .*?, so I can .*?\."
        ]
        
        # Search in description field
        description_section = self._extract_field_section(content, 'description')
        if description_section:
            for pattern in user_story_patterns:
                match = re.search(pattern, description_section, re.IGNORECASE | re.DOTALL)
                if match:
                    analysis['user_story_found'] = True
                    analysis['location'] = 'description'
                    analysis['pattern_matched'] = pattern
                    analysis['confidence'] = 0.9
                    analysis['debug_info'].append(f"User story found in description with pattern: {pattern}")
                    break
        
        # Also search in the entire content for description-like patterns if not found in specific field
        if not analysis['user_story_found']:
            # Look for description-like content after "Description:" in the main content
            description_match = re.search(r'Description:\s*(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)', content, re.IGNORECASE | re.DOTALL)
            if description_match:
                description_text = description_match.group(1).strip()
                for pattern in user_story_patterns:
                    match = re.search(pattern, description_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        analysis['user_story_found'] = True
                        analysis['location'] = 'description'
                        analysis['pattern_matched'] = pattern
                        analysis['confidence'] = 0.9
                        analysis['debug_info'].append(f"User story found in description with pattern: {pattern}")
                        break
        
        # Search in Acceptance Criteria field if not found in description
        if not analysis['user_story_found']:
            ac_section = self._extract_field_section(content, 'acceptance criteria')
            if ac_section:
                for pattern in user_story_patterns:
                    match = re.search(pattern, ac_section, re.IGNORECASE | re.DOTALL)
                    if match:
                        analysis['user_story_found'] = True
                        analysis['location'] = 'acceptance_criteria'
                        analysis['pattern_matched'] = pattern
                        analysis['confidence'] = 0.8
                        analysis['debug_info'].append(f"User story found in AC with pattern: {pattern}")
                        break
        
        # Search in comments field if still not found
        if not analysis['user_story_found']:
            comments_section = self._extract_field_section(content, 'comments')
            if comments_section:
                for pattern in user_story_patterns:
                    match = re.search(pattern, comments_section, re.IGNORECASE | re.DOTALL)
                    if match:
                        analysis['user_story_found'] = True
                        analysis['location'] = 'comments'
                        analysis['pattern_matched'] = pattern
                        analysis['confidence'] = 0.7
                        analysis['debug_info'].append(f"User story found in comments with pattern: {pattern}")
                        break
        
        if not analysis['user_story_found']:
            analysis['debug_info'].append("No user story pattern found in any field")
        
        return analysis

    def detect_figma_links_enhanced(self, content: str) -> Dict[str, any]:
        """
        Enhanced Figma link detection that scans multiple fields
        Fixes missed Figma links in Acceptance Criteria and other fields
        """
        analysis = {
            'figma_link_found': False,
            'locations': [],
            'links': [],
            'confidence': 0.0,
            'debug_info': []
        }
        
        # Enhanced Figma link regex pattern - more specific to avoid partial matches
        figma_pattern = r"https:\/\/(www\.)?figma\.com\/file\/[a-zA-Z0-9]+(?:\/.*)?"
        
        # Search in Acceptance Criteria field
        ac_section = self._extract_field_section(content, 'acceptance criteria')
        if ac_section:
            matches = re.finditer(figma_pattern, ac_section, re.IGNORECASE)
            matches_list = [match.group(0) for match in matches]
            if matches_list:
                analysis['figma_link_found'] = True
                analysis['locations'].append('acceptance_criteria')
                analysis['links'].extend(matches_list)
                analysis['confidence'] = 0.9
                analysis['debug_info'].append(f"Figma links found in AC: {len(matches_list)} links")
        
        # Search in description field
        description_section = self._extract_field_section(content, 'description')
        if description_section:
            matches = re.finditer(figma_pattern, description_section, re.IGNORECASE)
            matches_list = [match.group(0) for match in matches]
            if matches_list:
                analysis['figma_link_found'] = True
                if 'description' not in analysis['locations']:
                    analysis['locations'].append('description')
                analysis['links'].extend(matches_list)
                analysis['confidence'] = max(analysis['confidence'], 0.8)
                analysis['debug_info'].append(f"Figma links found in description: {len(matches_list)} links")
        
        # Search in comments field
        comments_section = self._extract_field_section(content, 'comments')
        if comments_section:
            matches = re.finditer(figma_pattern, comments_section, re.IGNORECASE)
            matches_list = [match.group(0) for match in matches]
            if matches_list:
                analysis['figma_link_found'] = True
                if 'comments' not in analysis['locations']:
                    analysis['locations'].append('comments')
                analysis['links'].extend(matches_list)
                analysis['confidence'] = max(analysis['confidence'], 0.7)
                analysis['debug_info'].append(f"Figma links found in comments: {len(matches_list)} links")
        
        # Remove duplicates from links
        analysis['links'] = list(set(analysis['links']))
        
        if not analysis['figma_link_found']:
            analysis['debug_info'].append("No Figma links found in any field")
        
        return analysis

    def should_evaluate_dod(self, content: str) -> Dict[str, any]:
        """
        Determine if Definition of Done should be evaluated based on ticket status
        Fixes premature DoD analysis for grooming-stage tickets
        """
        analysis = {
            'should_evaluate': False,
            'status_found': None,
            'status_category_found': None,
            'reason': None,
            'debug_info': []
        }
        
        # Extract status and status category fields
        status_section = self._extract_field_section(content, 'status')
        status_category_section = self._extract_field_section(content, 'status category')
        
        # Check for release-ready statuses
        release_statuses = [
            'release', 'ready for release', 'prod release queue', 'production release',
            'ready for production', 'prod ready', 'release ready'
        ]
        
        content_lower = content.lower()
        
        # Check if any release status is mentioned
        for status in release_statuses:
            if status in content_lower:
                analysis['should_evaluate'] = True
                analysis['status_found'] = status
                analysis['reason'] = f"Status indicates release readiness: {status}"
                analysis['debug_info'].append(f"Release status detected: {status}")
                break
        
        # Check status category field specifically
        if status_category_section:
            status_category_lower = status_category_section.lower()
            if 'release' in status_category_lower:
                analysis['should_evaluate'] = True
                analysis['status_category_found'] = 'release'
                analysis['reason'] = "Status category indicates release readiness"
                analysis['debug_info'].append("Release status category detected")
        
        # Check status field specifically
        if status_section:
            status_lower = status_section.lower()
            for status in release_statuses:
                if status in status_lower:
                    analysis['should_evaluate'] = True
                    analysis['status_found'] = status
                    analysis['reason'] = f"Status field indicates release readiness: {status}"
                    analysis['debug_info'].append(f"Release status in status field: {status}")
                    break
        
        if not analysis['should_evaluate']:
            analysis['reason'] = "Ticket not in release-ready status - DoD evaluation suppressed for grooming"
            analysis['debug_info'].append("No release-ready status detected - suppressing DoD evaluation")
        
        return analysis

    def calculate_groom_readiness_score_enhanced(self, all_analyses: Dict, user_story_found: bool = False, figma_link_found: bool = False) -> Dict[str, any]:
        """
        Enhanced groom readiness score calculation that uses detection flags
        Fixes scoring penalties when user story and figma are actually present
        """
        score_data = {
            'overall_score': 0,
            'total_possible': 0,
            'completed_items': 0,
            'missing_items': 0,
            'score_breakdown': {},
            'critical_gaps': [],
            'enhanced_scoring': {
                'user_story_penalty_applied': False,
                'figma_penalty_applied': False,
                'corrections_made': []
            }
        }
        
        # Analyze DOR requirements with enhanced user story detection
        dor_analysis = all_analyses.get('dor_analysis', {})
        dor_score = 0
        dor_total = 0
        
        for requirement_key, analysis in dor_analysis.items():
            coverage = analysis['coverage_percentage']
            
            # Apply user story correction if detected
            if requirement_key == 'user_story' and user_story_found and coverage < 50:
                original_coverage = coverage
                coverage = 100  # Full credit if user story is actually found
                score_data['enhanced_scoring']['user_story_penalty_applied'] = True
                score_data['enhanced_scoring']['corrections_made'].append(
                    f"User Story: Corrected from {original_coverage:.1f}% to 100% (detected via enhanced analysis)"
                )
            
            dor_total += 100  # Each requirement is worth 100 points
            dor_score += coverage
            
            if coverage < 50:
                score_data['critical_gaps'].append(f"DOR: {analysis['name']} - {coverage:.1f}% coverage")
        
        score_data['score_breakdown']['dor'] = {
            'score': dor_score,
            'total': dor_total,
            'percentage': (dor_score / dor_total * 100) if dor_total > 0 else 0
        }
        
        # Analyze dependencies
        dep_analysis = all_analyses.get('dependencies_analysis', {})
        dep_score = 100 if not dep_analysis.get('dependencies_found') else 50
        score_data['score_breakdown']['dependencies'] = {
            'score': dep_score,
            'total': 100,
            'percentage': dep_score
        }
        
        # Analyze stakeholder validation with enhanced Figma detection
        stakeholder_analysis = all_analyses.get('stakeholder_analysis', {})
        stakeholder_score = 0
        stakeholder_total = len(stakeholder_analysis) * 100
        
        for section_key, section_data in stakeholder_analysis.items():
            if not section_data.get('missing', True):
                stakeholder_score += 100
            elif section_key == 'po_approval' and section_data.get('visibility_issue', False):
                stakeholder_score += 50  # Partial credit for PO approval with visibility issue
            elif section_key == 'design_validation' and figma_link_found:
                # Apply Figma correction if detected
                stakeholder_score += 100  # Full credit if Figma is actually found
                score_data['enhanced_scoring']['figma_penalty_applied'] = True
                score_data['enhanced_scoring']['corrections_made'].append(
                    f"Design Validation: Corrected to 100% (Figma link detected via enhanced analysis)"
                )
        
        score_data['score_breakdown']['stakeholder'] = {
            'score': stakeholder_score,
            'total': stakeholder_total,
            'percentage': (stakeholder_score / stakeholder_total * 100) if stakeholder_total > 0 else 0
        }
        
        # Analyze test scenarios
        test_scenarios_analysis = all_analyses.get('test_scenarios_analysis', {})
        test_scenarios_score = 0
        test_scenarios_total = 400  # 100 points each for happy_path, negative, rbt, cross_browser
        
        categories = ['happy_path', 'negative', 'rbt', 'cross_browser']
        for category in categories:
            category_data = test_scenarios_analysis.get(category, {})
            if category_data.get('status') == 'found':
                test_scenarios_score += 100
        
        score_data['score_breakdown']['test_scenarios'] = {
            'score': test_scenarios_score,
            'total': test_scenarios_total,
            'percentage': (test_scenarios_score / test_scenarios_total * 100) if test_scenarios_total > 0 else 0
        }
        
        # Calculate overall score
        total_score = dor_score + dep_score + stakeholder_score + test_scenarios_score
        total_possible = dor_total + 100 + stakeholder_total + test_scenarios_total  # 100 for dependencies
        
        score_data['overall_score'] = total_score
        score_data['total_possible'] = total_possible
        score_data['completed_items'] = total_score
        score_data['missing_items'] = total_possible - total_score
        
        return score_data

    def _extract_field_section(self, content: str, field_name: str) -> str:
        """
        Extract content from a specific Jira field section
        """
        # Common field patterns
        field_patterns = [
            rf'{field_name}[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            rf'{field_name.replace(" ", "_")}[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)',
            rf'{field_name.replace(" ", "")}[:\s]*\n(.*?)(?=\n\s*[A-Z][a-zA-Z\s]+:|\n\s*$)'
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""

    def generate_groom_analysis_enhanced(self, ticket_content: str, level: str = "default", debug_mode: bool = False) -> str:
        """
        Enhanced groom analysis that incorporates the new field reading accuracy fixes
        """
        try:
            # Run enhanced detection methods
            user_story_analysis = self.detect_user_story_enhanced(ticket_content)
            figma_analysis = self.detect_figma_links_enhanced(ticket_content)
            dod_evaluation = self.should_evaluate_dod(ticket_content)
            
            # Log debug information if enabled
            if debug_mode:
                console.print(f"[blue]Enhanced Analysis Debug:[/blue]")
                console.print(f"[blue]User Story Found: {user_story_analysis['user_story_found']} (Location: {user_story_analysis['location']})[/blue]")
                console.print(f"[blue]Figma Link Found: {figma_analysis['figma_link_found']} (Locations: {figma_analysis['locations']})[/blue]")
                console.print(f"[blue]DoD Evaluation: {dod_evaluation['should_evaluate']} (Reason: {dod_evaluation['reason']})[/blue]")
            
            # Run original analysis methods
            level_prompt = self.get_groom_level_prompt(level)
            
            # Analyze content for all aspects
            ticket_summary_analysis = self.analyze_ticket_summary(ticket_content)
            brand_analysis = self.analyze_brand_abbreviations(ticket_content)
            framework_analysis = self.analyze_frameworks(ticket_content)
            dor_analysis = self.analyze_dor_requirements(ticket_content)
            card_analysis = self.analyze_card_type(ticket_content)
            dependencies_analysis = self.analyze_dependencies_and_blockers(ticket_content)
            dod_analysis = self.analyze_dod_alignment(ticket_content) if dod_evaluation['should_evaluate'] else {}
            stakeholder_analysis = self.analyze_stakeholder_validation(ticket_content)
            sprint_readiness_analysis = self.analyze_sprint_readiness(ticket_content)
            cross_functional_analysis = self.analyze_cross_functional_concerns(ticket_content)
            test_scenarios_analysis = self.analyze_test_scenarios(ticket_content)
            enhanced_test_scenarios_analysis = self.analyze_enhanced_test_scenarios_v2(ticket_content)
            enhanced_ac_analysis = self.analyze_enhanced_acceptance_criteria(ticket_content)
            additional_jira_fields_analysis = self.analyze_additional_jira_fields(ticket_content)
            
            # Create visual checklist with enhanced scoring
            all_analyses = {
                'dor_analysis': dor_analysis,
                'dependencies_analysis': dependencies_analysis,
                'stakeholder_analysis': stakeholder_analysis,
                'test_scenarios_analysis': test_scenarios_analysis
            }
            visual_checklist = self.create_visual_checklist(all_analyses)
            
            # Apply enhanced scoring
            enhanced_score_data = self.calculate_groom_readiness_score_enhanced(
                all_analyses, 
                user_story_analysis['user_story_found'], 
                figma_analysis['figma_link_found']
            )
            
            # Create summaries with enhanced information
            ticket_summary_summary = self._create_ticket_summary_summary(ticket_summary_analysis)
            framework_summary = self._create_framework_summary(framework_analysis)
            brand_summary = self._create_brand_summary(brand_analysis)
            dor_summary = self._create_dor_summary_enhanced(dor_analysis, user_story_analysis)
            card_summary = self._create_card_summary(card_analysis)
            dependencies_summary = self._create_dependencies_summary(dependencies_analysis)
            dod_summary = self._create_dod_summary_enhanced(dod_analysis, dod_evaluation)
            stakeholder_summary = self._create_stakeholder_summary_enhanced(stakeholder_analysis, figma_analysis)
            sprint_readiness_summary = self._create_sprint_readiness_summary(sprint_readiness_analysis)
            cross_functional_summary = self._create_cross_functional_summary(cross_functional_analysis)
            test_scenarios_summary = self._create_test_scenarios_summary(test_scenarios_analysis)
            enhanced_test_scenarios_summary = self._create_enhanced_test_scenarios_summary(enhanced_test_scenarios_analysis)
            enhanced_ac_summary = self._create_enhanced_acceptance_criteria_summary(enhanced_ac_analysis)
            additional_jira_fields_summary = self._create_additional_jira_fields_summary(additional_jira_fields_analysis)
            checklist_summary = self._create_checklist_summary_enhanced(visual_checklist, enhanced_score_data)
            
            # Add enhanced analysis information to the prompt
            enhanced_analysis_info = f"""
**Enhanced Field Analysis Results:**
- User Story Detection: {'✅ Found' if user_story_analysis['user_story_found'] else '❌ Not Found'} (Location: {user_story_analysis['location'] or 'None'})
- Figma Link Detection: {'✅ Found' if figma_analysis['figma_link_found'] else '❌ Not Found'} (Locations: {', '.join(figma_analysis['locations']) if figma_analysis['locations'] else 'None'})
- DoD Evaluation: {'✅ Enabled' if dod_evaluation['should_evaluate'] else '❌ Suppressed'} (Reason: {dod_evaluation['reason']})

**Enhanced Scoring Corrections:**
{chr(10).join(enhanced_score_data['enhanced_scoring']['corrections_made']) if enhanced_score_data['enhanced_scoring']['corrections_made'] else 'No corrections needed'}
"""
            
            prompt = f"""
{level_prompt}

{enhanced_analysis_info}

**Jira Ticket Content:**
{ticket_content}

**Ticket Summary Analysis:**
{ticket_summary_summary}

**Brand Analysis:**
{brand_summary}

**Framework Analysis:**
{framework_summary}

**Definition of Ready (DOR) Analysis:**
{dor_summary}

**Card Type Analysis:**
{card_summary}

**Dependencies & Blockers Analysis:**
{dependencies_summary}

**Definition of Done (DoD) Alignment:**
{dod_summary}

**Stakeholder Validation Analysis:**
{stakeholder_summary}

**Sprint Readiness Analysis:**
{sprint_readiness_summary}

**Cross-Functional Concerns Analysis:**
{cross_functional_summary}

**Test Scenarios Analysis:**
{test_scenarios_summary}

**Enhanced Test Scenarios Analysis:**
{enhanced_test_scenarios_summary}

**Enhanced Acceptance Criteria Analysis:**
{enhanced_ac_summary}

**Additional Jira Fields Analysis:**
{additional_jira_fields_summary}

**Visual Checklist Summary:**
{checklist_summary}

**CRITICAL FORMATTING RULES:**
- Use ONLY markdown formatting, NEVER HTML tags
- Use **text** for bold emphasis (NOT <b>text</b>)
- Use *text* for italic emphasis (NOT <i>text</i>)
- Use # for main headings, ## for subheadings
- Use - for bullet points
- NEVER use HTML tags like <b>, </b>, <i>, </i>, etc.

**ENHANCED ANALYSIS INSTRUCTIONS:**
1. **User Story Detection**: If the enhanced analysis shows a user story was found, do NOT report it as missing in any section
2. **Figma Link Detection**: If the enhanced analysis shows Figma links were found, do NOT report them as missing in Design Specifications, Stakeholder Validation, or Figma Design Reference sections
3. **DoD Evaluation**: Only evaluate Definition of Done if the enhanced analysis shows it should be evaluated (release-ready status)
4. **Avoid Duplicate Warnings**: If an issue has been addressed by enhanced detection, reference it briefly rather than repeating the full warning
5. **Scoring Corrections**: The enhanced scoring has already corrected for detected user stories and Figma links - do not penalize again

**Instructions:**
1. Analyze the Jira ticket against the provided framework analysis
2. Provide professional feedback based on the selected level
3. Use the exact terminology from the presentation frameworks
4. Include specific suggestions for improvement
5. Reference the brand analysis if relevant
6. Use ONLY markdown formatting - **bold** for emphasis, *italic* for emphasis, # for headings
7. NEVER use HTML tags in your response
8. **AVOID REPETITIVE FEEDBACK**: If a missing element (e.g., test scenarios or Figma link) has already been mentioned in one section, do not repeat it verbatim in other sections. Refer to it briefly if needed (e.g., "See Key Findings" or "As noted above"). Each issue should only be fully explained once or twice.
9. **RESPECT ENHANCED DETECTION**: Use the enhanced analysis results to avoid false negatives and duplicate warnings.

**Output Format for Default Level:**
# 📋 Enhanced Groom Analysis

[AI-powered comprehensive review with enhanced field detection - analyzing all available data for sprint readiness]

## 📋 Ticket Summary:
[1-3 sentence summary of what the ticket is about, derived from Summary, Description, and Card Type fields]

## 🔍 Key Findings:
- **Finding 1** with relevant context (respecting enhanced detection results)
- **Finding 2** with relevant context (respecting enhanced detection results)
- **Finding 3** with relevant context (respecting enhanced detection results)

## 💡 Improvement Suggestions:
- **Suggestion 1** with specific guidance
- **Suggestion 2** with specific guidance
- **Suggestion 3** with specific guidance

## 🔗 Dependencies & Blockers:
- **Dependency status** with integration points
- **Blocker assessment** with recommendations

## ✅ Definition of Done Alignment:
- **DoD coverage** with missing elements (only if release-ready status)
- **QA and accessibility** requirements (only if release-ready status)

## 👥 Stakeholder Validation:
- **PO approval status** with recommendations
- **Design validation** requirements (respecting Figma link detection)

## 🚀 Sprint Readiness:
- **Readiness assessment** with missing items
- **Sprint context** and recommendations

## 🎯 Framework Coverage:
[Summary of framework analysis with specific findings]

## ✅ Acceptance Criteria Review:
[Enhanced AC analysis - validates intent, conditions, expected results, pass/fail logic, detects vague AC and Figma links]

## 🧪 Test Scenario Breakdown:
[Enhanced Test Scenarios analysis - validates Happy Path, Negative, RBT, Cross-browser coverage, detects field misuse]

## 🎨 Figma Design Reference:
[Figma link analysis - evaluates context, behavioral expectations, and placement recommendations]

## 🏗 Technical Detail Feedback:
[Analysis of Implementation Details, ADA Acceptance Criteria, Architectural Solution, Performance Impact, Linked Issues]

## 📊 Enhanced Groom Readiness Score:
[AI-estimated % readiness based on all analyzed fields with enhanced detection corrections]

## 🧾 Grooming Checklist:
[Visual reference for sprint team alignment on missing items]

## 🎯 Summary:
[Professional summary of key areas needing attention, respecting enhanced detection results]
"""
            
            if not self.client:
                return self.get_fallback_groom_analysis()
            
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[
                    {"role": "system", "content": "You are a professional Jira ticket analyst with expertise in agile methodologies and Definition of Ready requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            console.print(f"[red]Error generating enhanced groom analysis: {e}[/red]")
            return self.get_fallback_groom_analysis()

    def _create_dor_summary_enhanced(self, dor_analysis: Dict, user_story_analysis: Dict) -> str:
        """
        Enhanced DOR summary that respects user story detection results
        """
        summary = "**Definition of Ready (DOR) Analysis:**\n"
        
        for requirement_key, analysis in dor_analysis.items():
            summary += f"- **{analysis['name']}**: "
            
            if requirement_key == 'user_story' and user_story_analysis['user_story_found']:
                summary += f"✅ Found via enhanced detection (Location: {user_story_analysis['location']})\n"
            else:
                coverage = analysis['coverage_percentage']
                if coverage >= 75:
                    summary += f"✅ Good coverage ({coverage:.1f}%)\n"
                elif coverage >= 50:
                    summary += f"⚠️ Partial coverage ({coverage:.1f}%)\n"
                else:
                    summary += f"❌ Poor coverage ({coverage:.1f}%)\n"
                
                if analysis['missing_elements']:
                    summary += f"  - Missing: {', '.join(analysis['missing_elements'])}\n"
                if analysis['suggestions']:
                    summary += f"  - Suggestions: {', '.join(analysis['suggestions'])}\n"
        
        return summary

    def _create_dod_summary_enhanced(self, dod_analysis: Dict, dod_evaluation: Dict) -> str:
        """
        Enhanced DoD summary that respects evaluation conditions
        """
        if not dod_evaluation['should_evaluate']:
            return f"**Definition of Done (DoD) Alignment:**\n- ⏸️ Evaluation suppressed: {dod_evaluation['reason']}\n"
        
        summary = "**Definition of Done (DoD) Alignment:**\n"
        
        if not dod_analysis:
            summary += "- ❌ No DoD requirements found\n"
            return summary
        
        for dod_key, analysis in dod_analysis.items():
            summary += f"- **{analysis['name']}**: "
            coverage = analysis['coverage_percentage']
            if coverage >= 75:
                summary += f"✅ Good coverage ({coverage:.1f}%)\n"
            elif coverage >= 50:
                summary += f"⚠️ Partial coverage ({coverage:.1f}%)\n"
            else:
                summary += f"❌ Poor coverage ({coverage:.1f}%)\n"
            
            if analysis['missing_elements']:
                summary += f"  - Missing: {', '.join(analysis['missing_elements'])}\n"
            if analysis['suggestions']:
                summary += f"  - Suggestions: {', '.join(analysis['suggestions'])}\n"
        
        return summary

    def _create_stakeholder_summary_enhanced(self, stakeholder_analysis: Dict, figma_analysis: Dict) -> str:
        """
        Enhanced stakeholder summary that respects Figma link detection results
        """
        summary = "**Stakeholder Validation Analysis:**\n"
        
        for section_key, section_data in stakeholder_analysis.items():
            summary += f"- **{section_key.replace('_', ' ').title()}**: "
            
            if section_key == 'design_validation' and figma_analysis['figma_link_found']:
                summary += f"✅ Design validation found (Figma links detected in: {', '.join(figma_analysis['locations'])})\n"
            elif not section_data.get('missing', True):
                summary += "✅ Validation found\n"
            else:
                summary += "❌ Validation missing\n"
                if section_data.get('recommendation'):
                    summary += f"  - Recommendation: {section_data['recommendation']}\n"
                if section_data.get('visibility_issue'):
                    summary += f"  - Visibility issue: {section_data.get('visibility_recommendation', 'Add visible confirmation')}\n"
        
        return summary

    def _create_checklist_summary_enhanced(self, visual_checklist: Dict, enhanced_score_data: Dict) -> str:
        """
        Enhanced checklist summary that includes scoring corrections
        """
        summary = "**Visual Checklist Summary:**\n"
        
        # Add enhanced scoring information
        if enhanced_score_data['enhanced_scoring']['corrections_made']:
            summary += "**Enhanced Scoring Corrections Applied:**\n"
            for correction in enhanced_score_data['enhanced_scoring']['corrections_made']:
                summary += f"- {correction}\n"
            summary += "\n"
        
        # Add overall status
        status_emoji = {
            'red': '🔴',
            'yellow': '🟡', 
            'green': '🟢'
        }
        overall_status = visual_checklist['overall_status']
        summary += f"**Overall Status**: {status_emoji.get(overall_status, '⚪')} {overall_status.upper()}\n"
        
        # Add section breakdown
        for section_key, section_data in visual_checklist['sections'].items():
            section_status = status_emoji.get(section_data['status'], '⚪')
            summary += f"- **{section_data['name']}**: {section_status} {section_data['completed']}/{section_data['total']} ({section_data['percentage']:.1f}%)\n"
        
        # Add enhanced score
        enhanced_score = enhanced_score_data['overall_score']
        enhanced_total = enhanced_score_data['total_possible']
        enhanced_percentage = (enhanced_score / enhanced_total * 100) if enhanced_total > 0 else 0
        summary += f"\n**Enhanced Groom Readiness Score**: {enhanced_percentage:.1f}% ({enhanced_score}/{enhanced_total})\n"
        
        return summary