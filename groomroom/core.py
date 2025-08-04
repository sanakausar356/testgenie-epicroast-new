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
    
    def get_groom_level_prompt(self, level: str) -> str:
        """Get the groom prompt based on level"""
        level_prompts = {
            "default": """You are a professional Jira ticket analyst. For the 'Default' level, provide a balanced mix of feedback and gentle tone. Analyze the ticket against the specified frameworks and provide constructive feedback.

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
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements""",
            
            "insight": """You are a focused analyst examining Jira tickets. For the 'Insight' level, provide focused analysis that calls out missing details and implied risks. Use concise bullet points and highlight specific gaps.

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
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements""",
            
            "deep_dive": """You are a thorough analyst conducting deep analysis of Jira tickets. For the 'Deep Dive' level, provide comprehensive analysis including edge-case checks, data validations, and compliance notes. Be thorough and detailed.

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
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements""",
            
            "actionable": """You are a practical analyst focused on actionable feedback. For the 'Actionable' level, highlight only items that directly map to user stories or acceptance criteria. Provide 'next steps' phrased as Jira tasks.

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
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements""",
            
            "summary": """You are a concise analyst providing ultra-brief summaries. For the 'Summary' level, provide exactly 3 key gaps and 2 critical suggestions. Keep it brief and focused for quick scans.

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
- **Cross-Functional Concerns**: Consider accessibility, performance, security, and UX validation requirements"""
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
        
        # Calculate overall score
        total_score = dor_score + dep_score + stakeholder_score
        total_possible = dor_total + 100 + stakeholder_total  # 100 for dependencies
        
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
            brand_analysis = self.analyze_brand_abbreviations(ticket_content)
            framework_analysis = self.analyze_frameworks(ticket_content)
            dor_analysis = self.analyze_dor_requirements(ticket_content)
            card_analysis = self.analyze_card_type(ticket_content)
            dependencies_analysis = self.analyze_dependencies_and_blockers(ticket_content)
            dod_analysis = self.analyze_dod_alignment(ticket_content)
            stakeholder_analysis = self.analyze_stakeholder_validation(ticket_content)
            sprint_readiness_analysis = self.analyze_sprint_readiness(ticket_content)
            cross_functional_analysis = self.analyze_cross_functional_concerns(ticket_content)
            
            # Create visual checklist
            all_analyses = {
                'dor_analysis': dor_analysis,
                'dependencies_analysis': dependencies_analysis,
                'stakeholder_analysis': stakeholder_analysis
            }
            visual_checklist = self.create_visual_checklist(all_analyses)
            
            # Create summaries
            framework_summary = self._create_framework_summary(framework_analysis)
            brand_summary = self._create_brand_summary(brand_analysis)
            dor_summary = self._create_dor_summary(dor_analysis)
            card_summary = self._create_card_summary(card_analysis)
            dependencies_summary = self._create_dependencies_summary(dependencies_analysis)
            dod_summary = self._create_dod_summary(dod_analysis)
            stakeholder_summary = self._create_stakeholder_summary(stakeholder_analysis)
            sprint_readiness_summary = self._create_sprint_readiness_summary(sprint_readiness_analysis)
            cross_functional_summary = self._create_cross_functional_summary(cross_functional_analysis)
            checklist_summary = self._create_checklist_summary(visual_checklist)
            
            prompt = f"""
{level_prompt}

**Jira Ticket Content:**
{ticket_content}

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

**Output Format for Default Level:**
# 📊 Professional Analysis

[Balanced analysis with constructive feedback]

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
# 📊 Professional Analysis

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