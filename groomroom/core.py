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
from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()

# Initialize Rich console for better output
console = Console()

class GroomRoom:
    """Main Groom Room application class for professional Jira ticket analysis"""
    
    def __init__(self):
        self.client = None
        self.jira_integration = JiraIntegration()
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
                'name': 'Testing Steps',
                'description': 'Defining test scenarios that QA will utilize to build their test cases from',
                'responsibility': 'QA Leading - Team is responsible for adding this information',
                'test_scenarios': [
                    'Positive Test Cases',
                    'Error Test Cases', 
                    'Negative Test Cases'
                ]
            },
            'additional_fields': {
                'name': 'Additional Card Details',
                'fields': [
                    'Brand(s)',
                    'Component(s)',
                    'Agile Team',
                    'Story Points'
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
            sys.exit(1)
        
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
- **Testing Steps**: Must include Positive, Error, and Negative test scenarios
- **Additional Fields**: Must include Brand(s), Component(s), Agile Team, Story Points

**CRITICAL: Card Type Validation:**
- **User Story**: Must be tied to Features (new functionality, enhancements, scope changes, technical enhancements)
- **Bug**: Must include clear details (environment, replication steps, expected behavior), ideally tied to feature that introduced it
- **Task**: For enabling/disabling configs or documentation creation""",
            
            "insight": """You are a focused analyst examining Jira tickets. For the 'Insight' level, provide focused analysis that calls out missing details and implied risks. Use concise bullet points and highlight specific gaps.

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
- **Task**: For enabling/disabling configs or documentation creation""",
            
            "deep_dive": """You are a thorough analyst conducting deep analysis of Jira tickets. For the 'Deep Dive' level, provide comprehensive analysis including edge-case checks, data validations, and compliance notes. Be thorough and detailed.

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
- **Task**: For enabling/disabling configs or documentation creation""",
            
            "actionable": """You are a practical analyst focused on actionable feedback. For the 'Actionable' level, highlight only items that directly map to user stories or acceptance criteria. Provide 'next steps' phrased as Jira tasks.

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
- **Task**: For enabling/disabling configs or documentation creation""",
            
            "summary": """You are a concise analyst providing ultra-brief summaries. For the 'Summary' level, provide exactly 3 key gaps and 2 critical suggestions. Keep it brief and focused for quick scans.

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
- **Task**: For enabling/disabling configs or documentation creation"""
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
                'description': requirement_info['description'],
                'responsibility': requirement_info['responsibility'],
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
                # Check for test scenarios
                test_scenarios = requirement_info['test_scenarios']
                for scenario in test_scenarios:
                    scenario_lower = scenario.lower()
                    if 'positive' in scenario_lower:
                        positive_indicators = ['success', 'valid', 'correct', 'expected']
                        if any(indicator in content_lower for indicator in positive_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Positive Test Cases')
                    
                    elif 'error' in scenario_lower:
                        error_indicators = ['error', 'exception', 'invalid', 'failed']
                        if any(indicator in content_lower for indicator in error_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Error Test Cases')
                    
                    elif 'negative' in scenario_lower:
                        negative_indicators = ['unauthorized', 'forbidden', 'denied', 'prevent']
                        if any(indicator in content_lower for indicator in negative_indicators):
                            analysis['coverage_score'] += 1
                        else:
                            analysis['missing_elements'].append('Negative Test Cases')
            
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
            
            # Calculate percentage coverage
            total_possible = 4  # Base score for each requirement type
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
    
    def generate_groom_analysis(self, ticket_content: str, level: str = "default") -> str:
        """Generate professional groom analysis using Azure OpenAI"""
        level_prompt = self.get_groom_level_prompt(level)
        
        # Analyze content for brand abbreviations, frameworks, DOR requirements, and card type
        brand_analysis = self.analyze_brand_abbreviations(ticket_content)
        framework_analysis = self.analyze_frameworks(ticket_content)
        dor_analysis = self.analyze_dor_requirements(ticket_content)
        card_analysis = self.analyze_card_type(ticket_content)
        
        # Create summaries
        framework_summary = self._create_framework_summary(framework_analysis)
        brand_summary = self._create_brand_summary(brand_analysis)
        dor_summary = self._create_dor_summary(dor_analysis)
        card_summary = self._create_card_summary(card_analysis)
        
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

## 🎯 Framework Coverage:
[Summary of framework analysis with specific findings]

## 🔍 Key Findings:
- **Finding 1** with relevant context
- **Finding 2** with relevant context
- **Finding 3** with relevant context

## 💡 Improvement Suggestions:
- **Suggestion 1** with specific guidance
- **Suggestion 2** with specific guidance
- **Suggestion 3** with specific guidance

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
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[
                    {"role": "system", "content": level_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000,
                temperature=0.3  # Lower temperature for more consistent output
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
    
    def get_fallback_groom_analysis(self) -> str:
        """Return a fallback groom analysis if API fails"""
        return """
# 📊 Professional Analysis

*The groom analysis generator is temporarily unavailable! 🔧*

## 🔍 Quick Manual Analysis:
- **Check User Story Template** - Ensure "As a [user], I want [goal], so that [benefit]" format
- **Verify Acceptance Criteria** - Look for clear, testable criteria
- **Review Framework Coverage** - Check R-O-I, I-N-V-E-S-T, A-C-C-E-P-T, and 3C Model elements
- **Brand Context** - Ensure brand abbreviations are used correctly

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