"""
GroomRoom No-Scoring Implementation
Context-specific story rewrites, ACs, scenarios, and recommendations without framework scoring
"""

import os
import re
import json
import hashlib
from typing import Optional, Dict, List, Any, Tuple, Union
from dataclasses import dataclass
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

@dataclass
class DesignLink:
    """Figma design link with metadata"""
    url: str
    file_key: str
    node_ids: List[str] = None
    title: str = None
    anchor_text: str = None
    section: str = None

@dataclass
class GroomroomResponse:
    """Structured response from GroomRoom analysis"""
    markdown: str
    data: Dict[str, Any]

class GroomRoomNoScoring:
    """Enhanced GroomRoom Refinement Agent - No Framework Scoring, Context-Specific Outputs"""
    
    def __init__(self):
        self.client = None
        self.setup_azure_openai()
        
        # Field presence synonyms and patterns (case/space tolerant)
        self.field_patterns = {
            'user_story': [
                r'(?i)(user\s+story|story|user\s+story\s+statement)',
                r'(?i)as\s+a\s+.*?\s+i\s+want\s+.*?\s+so\s+that'
            ],
            'acceptance_criteria': [
                r'(?i)(acceptance\s+criteria|ac|acs|acceptance)',
                r'(?i)criteria:',
                r'(?i)given\s+.*?\s+when\s+.*?\s+then'
            ],
            'testing_steps': [
                r'(?i)(testing\s+steps|test\s+steps|test\s+scenarios|qa\s+scenarios|scenarios)',
                r'(?i)test\s+plan:',
                r'(?i)qa\s+steps:'
            ],
            'ada_criteria': [
                r'(?i)(ada\s+acceptance\s+criteria|accessibility|a11y|wcag)',
                r'(?i)ada\s+criteria:',
                r'(?i)accessibility\s+requirements:'
            ],
            'architecture': [
                r'(?i)(architectural\s+solution|architecture|tech\s+flow|design|technical\s+design)',
                r'(?i)technical\s+approach:',
                r'(?i)system\s+design:'
            ],
            'implementation': [
                r'(?i)(implementation\s+details|implementation|dev\s+notes|deployment\s+notes)',
                r'(?i)dev\s+approach:',
                r'(?i)technical\s+implementation:'
            ],
            'non_functional': [
                r'(?i)(performance\s+impact|security\s+impact|devops\s+impact|nfrs|non-functional)',
                r'(?i)performance\s+requirements:',
                r'(?i)security\s+considerations:'
            ]
        }
        
        # Human-readable field labels for Definition of Ready output
        self.field_labels = {
            'user_story': 'User Story',
            'acceptance_criteria': 'Acceptance Criteria',
            'testing_steps': 'Testing Steps',
            'ada_criteria': 'ADA Criteria',
            'architectural_solution': 'Architectural Solution',
            'architecture': 'Architecture',
            'implementation_details': 'Implementation Details',
            'implementation': 'Implementation',
            'brands': 'Brands',
            'components': 'Components',
            'agile_team': 'Agile Team',
            'story_points': 'Story Points',
            'current_behaviour': 'Current Behaviour',
            'steps_to_reproduce': 'Steps to Reproduce',
            'expected_behaviour': 'Expected Behaviour',
            'environment': 'Environment',
            'links_to_story': 'Links to Story',
            'severity_priority': 'Severity/Priority',
            'outcome_definition': 'Outcome Definition',
            'dependencies_links': 'Dependencies/Links',
            'testing_validation': 'Testing Validation',
            'kpi_metrics': 'KPI Metrics',
            'non_functional': 'Non-Functional Requirements'
        }
        
        # Figma link patterns with anchor text detection
        self.figma_patterns = [
            r'https?://(?:www\.)?figma\.com/file/([A-Za-z0-9]+)/([^)\s]+)',
            r'https?://(?:www\.)?figma\.com/proto/([A-Za-z0-9]+)/([^)\s]+)',
            r'(?i)(figma|design|link):\s*(https?://[^\s]+)',
            r'(?i)figma\s+link:\s*(https?://[^\s]+)'
        ]
        
        # Figma anchor text terms (case-insensitive)
        self.figma_anchor_terms = [
            "figma", "figma link", "figma design", "design (figma)", "design file", "prototype (figma)"
        ]
        
        # Card type detection patterns
        self.card_type_patterns = {
            'story': [
                r'(?i)as\s+a\s+.*?\s+i\s+want\s+.*?\s+so\s+that',
                r'(?i)user\s+story',
                r'(?i)story\s+statement'
            ],
            'bug': [
                r'(?i)current\s+behaviour',
                r'(?i)steps\s+to\s+reproduce',
                r'(?i)expected\s+behaviour',
                r'(?i)reproduction\s+steps',
                r'(?i)bug\s+report'
            ],
            'task': [
                r'(?i)task\s+description',
                r'(?i)enabling\s+task',
                r'(?i)configuration\s+task',
                r'(?i)documentation\s+task'
            ],
            'feature': [
                r'(?i)feature\s+description',
                r'(?i)epic\s+description',
                r'(?i)capability\s+description',
                r'(?i)major\s+functionality'
            ]
        }
        
        # DoR (Definition of Ready) fields by card type
        # Each field must be present for the ticket to be considered "Sprint Ready"
        self.dor_fields = {
            'story': [
                # Core Requirements (Business & Testing):
                'user_story',              # Defining business value goal of the card
                'acceptance_criteria',     # Defining what is expected to be completed and validated in UAT
                'testing_steps',           # Test scenarios that QA will utilize to build test cases
                
                # Technical Requirements:
                'implementation_details',  # Technical approach and implementation notes for developers
                'architectural_solution',  # Architecture decisions, patterns, and system design considerations
                
                # Compliance & Accessibility:
                'ada_criteria',            # ADA/Accessibility compliance requirements and standards
                
                # Additional Card Details (Metadata):
                'brands',                  # Brand(s) affected by this story
                'components',              # Component(s) or modules involved
                'agile_team',              # Agile team responsible for implementation
                'story_points'             # Effort estimation in story points
            ],
            'bug': [
                'current_behaviour', 'steps_to_reproduce', 'expected_behaviour', 'environment',
                'acceptance_criteria', 'testing_steps', 'links_to_story', 'severity_priority',
                'components', 'agile_team', 'story_points'
            ],
            'task': [
                'outcome_definition', 'dependencies_links', 'testing_validation',
                'components', 'agile_team', 'story_points'
            ],
            'feature': [
                'user_story', 'acceptance_criteria', 'testing_steps',
                'implementation_details', 'architectural_solution', 'ada_criteria',
                'brands', 'components', 'agile_team', 'story_points', 'kpi_metrics'
            ]
        }
        
        # Domain pattern library for contextual content generation
        self.domain_patterns = {
            'checkout_paypal': [
                "popup opens on first CTA via user gesture",
                "remove second CTA/copy", 
                "popup-blocked fallback",
                "ABTasty disabled for validation",
                "no changes on cart page",
                "focus return",
                "analytics events"
            ],
            'plp_filters': [
                "top 5 pinned filters",
                "More Filters flyout",
                "sticky bar",
                "token remove (×)",
                "horizontal overflow",
                "grid update ≤1s"
            ],
            'auth_reset': [
                "email sent",
                "expired token",
                "rate limit",
                "screen-reader announcement"
            ],
            'payments_general': [
                "retry on timeout",
                "idempotency",
                "analytics events"
            ]
        }
        
        # Banned generic phrases for AC validation
        self.banned_ac_phrases = [
            "valid input", "gracefully", "meets requirements", "works as expected"
        ]
        
        # ========================================
        # Jira Status → Grooming Stage Mapping
        # ========================================
        # Toggle: Set to False to use readiness-based stage (original logic)
        self.use_jira_status = True
        
        # Jira status mapping to grooming stages
        self.status_mapping = {
            'discovery': [
                'to do', 'backlog', 'open', 'new', 'draft',
                'pending', 'pending po review', 'awaiting approval'
            ],
            'grooming': [
                'in progress', 'grooming', 'refinement', 'ready for grooming',
                'in refinement', 'tech review', 'qa grooming', 'under review'
            ],
            'ready': [
                'done', 'ready for dev', 'ready for development', 
                'closed', 'resolved', 'ready', 'approved'
            ]
        }

    def setup_azure_openai(self):
        """Initialize Azure OpenAI client"""
        try:
            openai.api_type = "azure"
            openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
            openai.api_version = "2024-02-15-preview"
            openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            if openai.api_base and openai.api_key:
                self.client = openai
            else:
                print("Warning: Azure OpenAI credentials not configured")
        except Exception as e:
            print(f"Warning: Azure OpenAI setup failed: {e}")
    
    def _format_field_names(self, field_keys: List[str]) -> str:
        """Convert field keys to human-readable labels"""
        if not field_keys:
            return 'None'
        
        readable_names = []
        for key in field_keys:
            # Use the field label if available, otherwise convert underscore to title case
            if key in self.field_labels:
                readable_names.append(self.field_labels[key])
            else:
                # Fallback: convert underscores to spaces and title case
                readable_names.append(key.replace('_', ' ').title())
        
        return ', '.join(readable_names)
    
    def get_manual_figma_link(self, ticket_key: str) -> Optional[str]:
        """Get manually configured Figma link for a ticket"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'figma_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Check for ticket-specific link
                    if ticket_key in config.get('default_figma_links', {}):
                        return config['default_figma_links'][ticket_key]
                    # Fall back to project default if configured
                    return config.get('project_default')
        except Exception as e:
            print(f"Warning: Could not load Figma config: {e}")
        return None

    def parse_jira_content(self, ticket_data: Dict[str, Any], status_fallback: str = None) -> Dict[str, Any]:
        """Robust parser with Figma detection and section recognition"""
        # Get fields and renderedFields
        fields = ticket_data.get('fields', {})
        rendered_fields = ticket_data.get('renderedFields', {})
        
        # Extract status - check multiple possible locations with robust extraction
        # CRITICAL: Check renderedFields FIRST (it's most reliable when fields is empty)
        status = 'Unknown'
        
        # PRIORITY 1: Check renderedFields.status FIRST (most reliable when fields is empty)
        if rendered_fields:
            print(f"🔍 PRIORITY 1 - Checking renderedFields for status...")
            print(f"   rendered_fields type: {type(rendered_fields)}")
            print(f"   rendered_fields keys: {list(rendered_fields.keys())[:20] if rendered_fields else 'None'}")
            print(f"   'status' in rendered_fields: {'status' in rendered_fields if rendered_fields else False}")
            
            if 'status' in rendered_fields:
                status_obj = rendered_fields.get('status')
                print(f"   rendered_fields.get('status'): {status_obj}")
                print(f"   status_obj type: {type(status_obj)}")
                
                if status_obj:
                    if isinstance(status_obj, dict):
                        print(f"   status_obj keys: {list(status_obj.keys()) if isinstance(status_obj, dict) else 'Not a dict'}")
                        status = status_obj.get('name', 'Unknown')
                        if status and status != 'Unknown':
                            print(f"✅ PRIORITY 1: Status extracted from renderedFields.status.name: {status}")
                        # Try statusCategory if name is Unknown
                        if status == 'Unknown' and status_obj.get('statusCategory'):
                            status_category = status_obj.get('statusCategory')
                            if isinstance(status_category, dict):
                                status = status_category.get('name', 'Unknown')
                                if status and status != 'Unknown':
                                    print(f"✅ PRIORITY 1: Status extracted from renderedFields.status.statusCategory.name: {status}")
                    elif isinstance(status_obj, str):
                        status = status_obj
                        if status and status != 'Unknown':
                            print(f"✅ PRIORITY 1: Status extracted from renderedFields.status (string): {status}")
                else:
                    print(f"❌ rendered_fields.get('status') returned None/empty even though 'status' is in keys!")
                    # Try direct access
                    try:
                        status_obj_direct = rendered_fields['status']
                        if status_obj_direct:
                            if isinstance(status_obj_direct, dict) and 'name' in status_obj_direct:
                                status = status_obj_direct['name']
                                print(f"✅ PRIORITY 1b: Status extracted using direct access rendered_fields['status']['name']: {status}")
                    except Exception as e:
                        print(f"   Direct access failed: {e}")
            else:
                print(f"❌ 'status' NOT in rendered_fields keys!")
        
        # PRIORITY 2: Use status_fallback if provided and status is still Unknown
        if (not status or status == 'Unknown') and status_fallback and status_fallback != 'Unknown':
            status = status_fallback
            print(f"✅ PRIORITY 2: Status using status_fallback: {status}")
        
        # PRIORITY 2b: If status is still Unknown, try to get from ticket_data.renderedFields directly
        if (not status or status == 'Unknown') and isinstance(ticket_data, dict) and 'renderedFields' in ticket_data:
            rendered_direct = ticket_data.get('renderedFields', {})
            if rendered_direct and rendered_direct.get('status'):
                status_obj_direct = rendered_direct.get('status')
                if isinstance(status_obj_direct, dict) and 'name' in status_obj_direct:
                    status = status_obj_direct['name']
                    print(f"✅ PRIORITY 2b: Status extracted from ticket_data['renderedFields']['status']['name']: {status}")
        
        # PRIORITY 3: Try fields.status if status is still Unknown
        if not status or status == 'Unknown':
            # Try fields.status first (most common)
            if fields:
                status_obj = fields.get('status')
                if status_obj:
                    if isinstance(status_obj, dict):
                        # Standard Jira API format: {"name": "Ready to Dev", "id": "...", ...}
                        status = status_obj.get('name', 'Unknown')
                        if status and status != 'Unknown':
                            print(f"✅ Status extracted from fields.status.name: {status}")
                    elif isinstance(status_obj, str):
                        status = status_obj
                        if status and status != 'Unknown':
                            print(f"✅ Status extracted from fields.status (string): {status}")
                    elif hasattr(status_obj, 'name'):
                        status = status_obj.name
                        if status and status != 'Unknown':
                            print(f"✅ Status extracted from fields.status.name (attr): {status}")
                    elif hasattr(status_obj, '__getitem__'):
                        try:
                            status = status_obj['name'] if 'name' in status_obj else str(status_obj)
                            if status and status != 'Unknown':
                                print(f"✅ Status extracted from fields.status['name']: {status}")
                        except:
                            status = str(status_obj)
                            if status and status != 'Unknown':
                                print(f"✅ Status extracted from fields.status (str): {status}")
            
            # Fallback to renderedFields if status still Unknown
            # CRITICAL: Check renderedFields FIRST if fields is empty
            if (not status or status == 'Unknown') and rendered_fields:
                print(f"🔍 Checking renderedFields for status...")
                print(f"   renderedFields keys: {list(rendered_fields.keys())[:20]}")
                print(f"   'status' in renderedFields: {'status' in rendered_fields}")
                status_obj = rendered_fields.get('status')
                print(f"   rendered_fields.get('status'): {status_obj}")
                print(f"   status_obj type: {type(status_obj)}")
                
                if status_obj:
                    if isinstance(status_obj, dict):
                        status = status_obj.get('name', 'Unknown')
                        if status and status != 'Unknown':
                            print(f"✅ Status extracted from renderedFields.status.name: {status}")
                        # Also try statusCategory if name is Unknown
                        if status == 'Unknown' and status_obj.get('statusCategory'):
                            status_category = status_obj.get('statusCategory')
                            if isinstance(status_category, dict):
                                status = status_category.get('name', 'Unknown')
                                if status and status != 'Unknown':
                                    print(f"✅ Status extracted from renderedFields.status.statusCategory.name: {status}")
                    elif isinstance(status_obj, str):
                        status = status_obj
                        if status and status != 'Unknown':
                            print(f"✅ Status extracted from renderedFields.status (string): {status}")
                else:
                    print(f"❌ renderedFields.get('status') returned None or empty")
                    print(f"   renderedFields full content: {list(rendered_fields.keys())}")
            
            # Final fallback: check root level if status field was requested
            if (not status or status == 'Unknown') and 'status' in ticket_data:
                status_obj = ticket_data['status']
                if isinstance(status_obj, dict):
                    status = status_obj.get('name', 'Unknown')
                    if status and status != 'Unknown':
                        print(f"✅ Status extracted from ticket_data.status.name: {status}")
                elif isinstance(status_obj, str):
                    status = status_obj
                    if status and status != 'Unknown':
                        print(f"✅ Status extracted from ticket_data.status (string): {status}")
        
        # ULTIMATE FALLBACK: Use status_fallback if all extraction methods failed
        # CRITICAL: This should ALWAYS work if status_fallback is provided
        print(f"\n🔍🔍🔍 DEBUG parse_jira_content - STATUS FALLBACK CHECK:")
        print(f"   Current status: '{status}'")
        print(f"   status_fallback: '{status_fallback}'")
        print(f"   status_fallback type: {type(status_fallback)}")
        print(f"   status is None: {status is None}")
        print(f"   status == 'Unknown': {status == 'Unknown'}")
        print(f"   status_fallback is not None: {status_fallback is not None}")
        print(f"   status_fallback != 'Unknown': {status_fallback != 'Unknown' if status_fallback else 'N/A'}")
        
        # CRITICAL: Use status_fallback if status is Unknown/None/empty
        if (not status or status == 'Unknown' or status is None) and status_fallback and status_fallback != 'Unknown' and status_fallback is not None:
            status = status_fallback
            print(f"✅✅✅ Status using fallback: '{status}'")
        elif status_fallback and status_fallback != 'Unknown' and status_fallback is not None:
            # Even if status was extracted, prefer status_fallback if it's different
            # (status_fallback is more reliable as it comes from jira_integration.py)
            if status == 'Unknown' or not status or status is None:
                status = status_fallback
                print(f"✅✅✅ Status forced from fallback (status was Unknown/empty): '{status}'")
        else:
            print(f"❌❌❌ Status fallback NOT used!")
            print(f"   Reason: status='{status}', status_fallback='{status_fallback}'")
        
        if not status or status == 'Unknown':
            print(f"⚠️ WARNING: Status extraction failed - all methods returned Unknown")
            print(f"   fields keys: {list(fields.keys())[:20] if fields else 'No fields'}")
            print(f"   renderedFields keys: {list(rendered_fields.keys())[:20] if rendered_fields else 'No renderedFields'}")
            print(f"   ticket_data top-level keys: {list(ticket_data.keys())[:20]}")
            print(f"   status_fallback: {status_fallback}")
            print(f"   status_fallback type: {type(status_fallback)}")
            if status_fallback:
                print(f"   status_fallback value: '{status_fallback}'")
        
        # Extract status category
        status_category = 'Unknown'
        if fields and fields.get('status'):
            status_obj = fields['status']
            if isinstance(status_obj, dict):
                status_category_obj = status_obj.get('statusCategory', {})
                if isinstance(status_category_obj, dict):
                    status_category = status_category_obj.get('name', 'Unknown')
        
        # Extract issuetype
        issuetype = ''
        if fields and fields.get('issuetype'):
            if isinstance(fields['issuetype'], dict):
                issuetype = fields['issuetype'].get('name', '')
            elif isinstance(fields['issuetype'], str):
                issuetype = fields['issuetype']
        elif rendered_fields and rendered_fields.get('issuetype'):
            if isinstance(rendered_fields['issuetype'], dict):
                issuetype = rendered_fields['issuetype'].get('name', '')
            elif isinstance(rendered_fields['issuetype'], str):
                issuetype = rendered_fields['issuetype']
        
        # Debug: Print status before creating parsed dict
        print(f"\n🔍 DEBUG parse_jira_content - Final status before parsed dict:")
        print(f"   status variable: {status}")
        print(f"   status type: {type(status)}")
        print(f"   status_fallback: {status_fallback}")
        print(f"   status_fallback type: {type(status_fallback)}")
        
        # FINAL SAFETY CHECK: If status is still Unknown but status_fallback exists, use it
        print(f"\n🔍🔍🔍 DEBUG parse_jira_content - FINAL STATUS FALLBACK CHECK:")
        print(f"   Current status: '{status}'")
        print(f"   status_fallback: '{status_fallback}'")
        print(f"   status_fallback type: {type(status_fallback)}")
        if (not status or status == 'Unknown') and status_fallback and status_fallback != 'Unknown' and status_fallback is not None:
            print(f"   🔧 FINAL FIX: Setting status from status_fallback: {status_fallback}")
            status = status_fallback
        else:
            print(f"   ❌ FINAL FIX FAILED: status='{status}', status_fallback='{status_fallback}'")
        
        if not status or status == 'Unknown':
            print(f"   ⚠️ WARNING: parsed['status'] will be Unknown!")
            print(f"   This should NOT happen if status_fallback was provided correctly")
        
        parsed = {
            'ticket_key': ticket_data.get('key', ''),
            'title': fields.get('summary', '') if fields else rendered_fields.get('summary', ''),
            'description': fields.get('description', '') if fields else rendered_fields.get('description', ''),
            'issuetype': issuetype,
            'status': status,
            'status_category': status_category,
            'fields': {},
            'design_links': [],
            'card_type': 'unknown'
        }
        
        # Debug: Verify status was set correctly
        print(f"   parsed['status'] after creation: {parsed.get('status')}")
        if parsed.get('status') == 'Unknown':
            print(f"   ⚠️ WARNING: parsed['status'] is still Unknown!")
        
        # Extract all text content for analysis
        # Priority 1: Use renderedFields (HTML) - often has more complete content including all sections
        rendered_description = ticket_data.get('renderedFields', {}).get('description', '')
        if rendered_description:
            # Strip HTML tags from rendered description
            description_text = re.sub(r'<[^>]+>', ' ', rendered_description)
            description_text = re.sub(r'\s+', ' ', description_text).strip()
        else:
            # Priority 2: Extract from ADF format
            description_text = self._extract_text_from_field(parsed['description'])
        
        all_text = f"{parsed['title']} {description_text}"
        
        # Also get raw description for ADF/JSON parsing
        raw_description = ticket_data.get('fields', {}).get('description')
        
        # Detect card type
        parsed['card_type'] = self.detect_card_type(all_text, parsed['issuetype'])
        
        # Parse fields using patterns from description/text
        for field_name, patterns in self.field_patterns.items():
            content = self.extract_field_content(all_text, patterns)
            parsed['fields'][field_name] = content
        
        # Extract Figma links from multiple sources
        # 3. Fall back to text extraction if no links found
        if not parsed['design_links']:
            parsed['design_links'] = self.extract_figma_links_with_anchors(all_text)
        
        # Deduplicate design links by URL
        seen_urls = set()
        unique_links = []
        
        # Parse additional Jira fields (custom fields and standard fields)
        fields = ticket_data.get('fields', {})
        print(f"\n🔍 DEBUG - parse_jira_content:")
        print(f"  ticket_data keys: {list(ticket_data.keys())}")
        print(f"  fields type: {type(fields)}, value: {fields if not isinstance(fields, dict) or len(fields) < 5 else 'dict with ' + str(len(fields)) + ' keys'}")
        print(f"  renderedFields in ticket_data: {'renderedFields' in ticket_data}")
        if 'renderedFields' in ticket_data:
            rendered_fields_check = ticket_data.get('renderedFields', {})
            print(f"  renderedFields type: {type(rendered_fields_check)}, empty: {not rendered_fields_check}")
            if rendered_fields_check:
                print(f"  renderedFields keys count: {len(rendered_fields_check)}")
                print(f"  customfield_13482 in renderedFields: {'customfield_13482' in rendered_fields_check}")
                print(f"  customfield_10117 in renderedFields: {'customfield_10117' in rendered_fields_check}")
        
        # Fallback to renderedFields if fields is empty/None (some Jira API calls return only renderedFields)
        if not fields:
            rendered_fields = ticket_data.get('renderedFields', {})
            if rendered_fields:
                # Convert HTML rendered fields to usable format
                fields = {}
                for key, value in rendered_fields.items():
                    if value:
                        # Strip HTML tags for rendered fields
                        if isinstance(value, str) and value.startswith('<'):
                            fields[key] = re.sub(r'<[^>]+>', ' ', value).strip()
                        else:
                            fields[key] = value
        
        # Extract all DoR fields from Jira custom fields (priority check)
        # These custom fields override text extraction if present
        custom_field_extractions = {
            'user_story': self.extract_user_story(fields, all_text),
            'acceptance_criteria': self.extract_acceptance_criteria(fields, all_text),
            'testing_steps': self.extract_testing_steps(fields, all_text),
            'implementation_details': self.extract_implementation_details(fields, all_text),
            'architectural_solution': self.extract_architectural_solution(fields, all_text),
            'ada_criteria': self.extract_ada_criteria(fields, all_text),
            'brands': self.extract_brands(fields),
            'components': self.extract_components(fields),
            'agile_team': self.extract_agile_team(fields),
            'story_points': self.extract_story_points(fields),
            'environment': self.extract_environment(fields),
            'severity_priority': self.extract_severity_priority(fields),
            'kpi_metrics': self.extract_kpi_metrics(fields)
        }
        
        # For brands and story_points, also check renderedFields as fallback if not found in fields
        # Also merge renderedFields into fields dict for better extraction
        rendered_fields = ticket_data.get('renderedFields', {})
        if rendered_fields:
            print(f"\n🔍 DEBUG - Checking renderedFields for brands/story_points")
            print(f"  renderedFields keys: {list(rendered_fields.keys())[:10]}...")
            
            # Check renderedFields directly for brands and story_points
            if 'customfield_13482' in rendered_fields:
                rendered_brand_value = rendered_fields['customfield_13482']
                print(f"  renderedFields['customfield_13482']: {rendered_brand_value}, type: {type(rendered_brand_value)}")
                # If it's HTML, parse it
                if isinstance(rendered_brand_value, str) and rendered_brand_value:
                    # Extract brand names from HTML - strip HTML tags
                    brand_text = re.sub(r'<[^>]+>', ' ', rendered_brand_value)
                    brand_text = re.sub(r'\s+', ' ', brand_text).strip()
                    # Look for brand names (common ones: Yankee Candle, Graco, Marmot, etc.)
                    if brand_text and brand_text.lower() not in ['none', 'n/a', 'na', '']:
                        print(f"  ✅ Extracted brand from HTML: {brand_text}")
                        if not custom_field_extractions['brands']:
                            custom_field_extractions['brands'] = brand_text
            
            if 'customfield_10117' in rendered_fields:
                rendered_sp_value = rendered_fields['customfield_10117']
                print(f"  renderedFields['customfield_10117']: {rendered_sp_value}, type: {type(rendered_sp_value)}")
                # Extract number from HTML or value
                if isinstance(rendered_sp_value, str) and rendered_sp_value:
                    sp_text = re.sub(r'<[^>]+>', ' ', rendered_sp_value)
                    sp_text = re.sub(r'\s+', ' ', sp_text).strip()
                    # Extract number
                    match = re.search(r'\d+', sp_text)
                    if match:
                        print(f"  ✅ Extracted story points from HTML: {match.group()}")
                        if not custom_field_extractions['story_points']:
                            custom_field_extractions['story_points'] = match.group()
                elif isinstance(rendered_sp_value, (int, float)):
                    print(f"  ✅ Story points (numeric): {rendered_sp_value}")
                    if not custom_field_extractions['story_points']:
                        custom_field_extractions['story_points'] = str(int(rendered_sp_value))
            
            # Merge ALL renderedFields into fields (overwrite if exists but empty/None)
            for key, value in rendered_fields.items():
                if key not in fields or not fields.get(key) or fields.get(key) is None:
                    fields[key] = value
            
            # CRITICAL: Check renderedFields directly if fields merge didn't work
            # Sometimes renderedFields has the key but value is None, need to check raw ticket_data
            if not custom_field_extractions['brands'] and 'customfield_13482' in rendered_fields:
                rendered_brand_value = rendered_fields.get('customfield_13482')
                print(f"🔍 DEBUG - Direct check renderedFields['customfield_13482']: {rendered_brand_value}, type: {type(rendered_brand_value)}")
                if rendered_brand_value is not None:
                    # Try extracting from the raw value
                    if isinstance(rendered_brand_value, list) and rendered_brand_value:
                        brand_names = []
                        for item in rendered_brand_value:
                            if isinstance(item, dict):
                                brand_name = item.get('value', item.get('name', ''))
                                if brand_name:
                                    brand_names.append(str(brand_name))
                        if brand_names:
                            custom_field_extractions['brands'] = ', '.join(brand_names)
                            print(f"✅✅✅ Direct extraction from renderedFields['customfield_13482']: {custom_field_extractions['brands']}")
                    elif isinstance(rendered_brand_value, str) and rendered_brand_value.strip():
                        custom_field_extractions['brands'] = rendered_brand_value.strip()
                        print(f"✅✅✅ Direct extraction from renderedFields['customfield_13482'] (string): {custom_field_extractions['brands']}")
            
            if not custom_field_extractions['story_points'] and 'customfield_10117' in rendered_fields:
                rendered_sp_value = rendered_fields.get('customfield_10117')
                print(f"🔍 DEBUG - Direct check renderedFields['customfield_10117']: {rendered_sp_value}, type: {type(rendered_sp_value)}")
                if rendered_sp_value is not None:
                    if isinstance(rendered_sp_value, (int, float)):
                        custom_field_extractions['story_points'] = str(int(rendered_sp_value))
                        print(f"✅✅✅ Direct extraction from renderedFields['customfield_10117']: {custom_field_extractions['story_points']}")
                    elif isinstance(rendered_sp_value, str) and rendered_sp_value.strip():
                        # Extract number from string
                        match = re.search(r'\d+', rendered_sp_value)
                        if match:
                            custom_field_extractions['story_points'] = match.group()
                            print(f"✅✅✅ Direct extraction from renderedFields['customfield_10117'] (string): {custom_field_extractions['story_points']}")
            
            # Try extracting again after merging (even if previous extraction returned empty)
            if not custom_field_extractions['brands']:
                rendered_brands = self.extract_brands(fields)
                if rendered_brands:
                    custom_field_extractions['brands'] = rendered_brands
                    print(f"🔍 DEBUG - Brands found in renderedFields after merge: {rendered_brands}")
            if not custom_field_extractions['story_points']:
                rendered_story_points = self.extract_story_points(fields)
                if rendered_story_points:
                    custom_field_extractions['story_points'] = rendered_story_points
                    print(f"🔍 DEBUG - Story Points found in renderedFields after merge: {rendered_story_points}")
        
        # CRITICAL: Check raw ticket_data['fields'] if renderedFields has None values
        # Sometimes the actual data is in ticket_data['fields'] not renderedFields
        if not custom_field_extractions['brands'] and 'fields' in ticket_data:
            raw_fields = ticket_data.get('fields', {})
            if 'customfield_13482' in raw_fields:
                raw_brand_value = raw_fields.get('customfield_13482')
                print(f"🔍 DEBUG - Checking ticket_data['fields']['customfield_13482']: {raw_brand_value}, type: {type(raw_brand_value)}")
                if raw_brand_value is not None:
                    # Extract from raw fields
                    if isinstance(raw_brand_value, list) and raw_brand_value:
                        brand_names = []
                        for item in raw_brand_value:
                            if isinstance(item, dict):
                                brand_name = item.get('value', item.get('name', ''))
                                if brand_name:
                                    brand_names.append(str(brand_name))
                        if brand_names:
                            custom_field_extractions['brands'] = ', '.join(brand_names)
                            print(f"✅✅✅ Found brands in ticket_data['fields']['customfield_13482']: {custom_field_extractions['brands']}")
        
        if not custom_field_extractions['story_points'] and 'fields' in ticket_data:
            raw_fields = ticket_data.get('fields', {})
            if 'customfield_10117' in raw_fields:
                raw_sp_value = raw_fields.get('customfield_10117')
                print(f"🔍 DEBUG - Checking ticket_data['fields']['customfield_10117']: {raw_sp_value}, type: {type(raw_sp_value)}")
                if raw_sp_value is not None:
                    if isinstance(raw_sp_value, (int, float)):
                        custom_field_extractions['story_points'] = str(int(raw_sp_value))
                        print(f"✅✅✅ Found story points in ticket_data['fields']['customfield_10117']: {custom_field_extractions['story_points']}")
                    elif isinstance(raw_sp_value, str) and raw_sp_value.strip():
                        match = re.search(r'\d+', raw_sp_value)
                        if match:
                            custom_field_extractions['story_points'] = match.group()
                            print(f"✅✅✅ Found story points in ticket_data['fields']['customfield_10117'] (string): {custom_field_extractions['story_points']}")
        
        # Also check if fields are directly in ticket_data (not in fields dict)
        if not custom_field_extractions['brands'] and 'customfield_13482' in ticket_data:
            direct_brands = self.extract_brands({'customfield_13482': ticket_data['customfield_13482']})
            if direct_brands:
                custom_field_extractions['brands'] = direct_brands
                print(f"🔍 DEBUG - Brands found in ticket_data root: {direct_brands}")
        if not custom_field_extractions['story_points'] and 'customfield_10117' in ticket_data:
            direct_story_points = self.extract_story_points({'customfield_10117': ticket_data['customfield_10117']})
            if direct_story_points:
                custom_field_extractions['story_points'] = direct_story_points
                print(f"🔍 DEBUG - Story Points found in ticket_data root: {direct_story_points}")
        
        # Merge: Custom fields override pattern-based extraction
        print(f"\n🔍🔍🔍 DEBUG parse_jira_content - CUSTOM FIELDS MERGE:")
        for field_name, custom_value in custom_field_extractions.items():
            print(f"   Processing field: '{field_name}'")
            print(f"   custom_value: {custom_value}")
            print(f"   custom_value type: {type(custom_value)}")
            print(f"   custom_value is truthy: {bool(custom_value)}")
            if custom_value:  # If custom field has value, use it
                parsed['fields'][field_name] = custom_value
                print(f"   ✅✅✅ Set parsed['fields']['{field_name}'] = {custom_value}")
            elif field_name not in parsed['fields'] or not parsed['fields'][field_name]:
                # Fallback to pattern extraction if custom field is empty
                parsed['fields'][field_name] = parsed['fields'].get(field_name, '')
                print(f"   ⚠️ Field '{field_name}' is empty, using fallback: '{parsed['fields'][field_name]}'")
        
        # CRITICAL: ALWAYS store status in parsed['fields']['status'] (for report generation)
        # Even if status is 'Unknown', store it so report generation can see it
        final_status = status if status else 'Unknown'
        if not parsed.get('fields'):
            parsed['fields'] = {}
        
        # Store status in both locations
        parsed['status'] = final_status
        parsed['fields']['status'] = {'name': final_status}
        print(f"✅ FORCING: Setting status in BOTH locations: parsed['status']='{final_status}', parsed['fields']['status']={{'name': '{final_status}'}}")
        
        # Also ensure status_category is set if available
        if status_category and status_category != 'Unknown':
            parsed['status_category'] = status_category
        
        # Debug: Print extracted values for brands and story_points
        print(f"\n🔍 DEBUG - Extracted Brands: '{parsed['fields'].get('brands', 'NOT FOUND')}'")
        print(f"🔍 DEBUG - Extracted Story Points: '{parsed['fields'].get('story_points', 'NOT FOUND')}'")
        print(f"🔍 DEBUG - Status in parsed['status']: '{parsed.get('status')}'")
        print(f"🔍 DEBUG - Status in parsed['fields']['status']: '{parsed['fields'].get('status')}'")
        print(f"🔍 DEBUG - Brands in fields dict: {'customfield_13482' in fields}")
        print(f"🔍 DEBUG - Story Points in fields dict: {'customfield_10117' in fields}")
        if 'customfield_13482' in fields:
            print(f"🔍 DEBUG - customfield_13482 value: {fields['customfield_13482']}")
        if 'customfield_10117' in fields:
            print(f"🔍 DEBUG - customfield_10117 value: {fields['customfield_10117']}")
        
        return parsed

    def get_grooming_stage(self, parsed_data: Dict[str, Any], dor: Dict[str, List[str]], readiness_percentage: int) -> str:
        """
        Determine grooming stage based on Jira status OR readiness percentage.
        
        Toggle behavior with self.use_jira_status:
        - True: Use Jira status field mapping (Option 1)
        - False: Use readiness-based logic (Original)
        """
        
        # ========================================
        # ORIGINAL LOGIC (Readiness-based)
        # ========================================
        if not self.use_jira_status:
            # Original hard-coded logic based on DoR completeness
            if 'user_story' in dor.get('present', []) and readiness_percentage >= 80:
                return "🟢 **Ready For Dev**"
            elif 'user_story' in dor.get('present', []):
                return "🟡 **To Groom**"
            else:
                return "🔴 **In Discovery**"
        
        # ========================================
        # NEW LOGIC (Jira Status-based)
        # ========================================
        jira_status = (parsed_data.get('status') or '').lower()
        
        # Critical validation: If User Story missing, force Discovery stage
        if 'user_story' not in dor.get('present', []):
            return "🔴 **In Discovery**"
        
        # Map Jira status to grooming stage
        for stage, status_list in self.status_mapping.items():
            if jira_status in status_list:
                if stage == 'discovery':
                    return "🔴 **In Discovery**"
                elif stage == 'grooming':
                    return "🟡 **To Groom**"
                elif stage == 'ready':
                    # Additional validation: Must have >= 80% readiness for "Ready"
                    if readiness_percentage >= 80:
                        return "🟢 **Ready For Dev**"
                    else:
                        return "🟡 **To Groom**"  # Downgrade if not ready enough
        
        # Fallback: Use readiness percentage if Jira status not recognized
        if readiness_percentage >= 80:
            return "🟢 **Ready For Dev**"
        elif readiness_percentage >= 50:
            return "🟡 **To Groom**"
        else:
            return "🔴 **In Discovery**"

    def detect_card_type(self, text: str, issuetype: str) -> str:
        """Detect card type from content and Jira issuetype"""
        text = text or ''
        issuetype = issuetype or ''
        text_lower = text.lower()
        issuetype_lower = issuetype.lower()
        
        # Check issuetype first
        if 'story' in issuetype_lower or 'user story' in issuetype_lower:
            return 'story'
        elif 'bug' in issuetype_lower:
            return 'bug'
        elif 'task' in issuetype_lower:
            return 'task'
        elif 'feature' in issuetype_lower or 'epic' in issuetype_lower:
            return 'feature'
        
        # Fallback to content analysis
        for card_type, patterns in self.card_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return card_type
        
        return 'story'  # Default fallback

    def extract_field_content(self, text: str, patterns: List[str]) -> str:
        """Extract field content using multiple patterns"""
        # Handle None text
        if text is None:
            text = ''
        text = text or ''
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                # Extract content after the pattern
                start_pos = match.end()
                # Find the next heading or end of text
                next_heading = re.search(r'\n\s*#+\s+', text[start_pos:])
                if next_heading:
                    content = text[start_pos:start_pos + next_heading.start()].strip()
                else:
                    content = text[start_pos:].strip()
                
                if content and not self.is_placeholder_content(content):
                    return content
        
        return ""

    def is_placeholder_content(self, content: str) -> bool:
        """Check if content is placeholder/empty"""
        # Handle None values
        if content is None:
            return True
        
        # Convert to string if not already
        if not isinstance(content, str):
            content = str(content) if content else ''
        
        placeholder_terms = ['tbd', 'n/a', 'tba', 'to be determined', 'not applicable', 'todo', 'pending']
        content_lower = content.lower().strip()
        # IMPORTANT: "None" alone is NOT considered placeholder - field is present with explicit None value
        # Only consider truly empty or very short content as placeholder
        if content_lower == 'none':
            return False  # "None" means field is present, just explicitly empty
        return content_lower in placeholder_terms or len(content_lower) < 3

    def extract_figma_from_adf_structure(self, adf_data: Any) -> List[DesignLink]:
        """Extract Figma links from Atlassian Document Format (ADF) JSON structure"""
        design_links = []
        
        try:
            # Handle string input (try to parse as JSON)
            if isinstance(adf_data, str):
                try:
                    adf_data = json.loads(adf_data)
                except:
                    return design_links
            
            # Handle dict (ADF structure)
            if isinstance(adf_data, dict):
                # Check if this node is a link mark with Figma URL
                if 'marks' in adf_data:
                    for mark in adf_data.get('marks', []):
                        if mark.get('type') == 'link':
                            href = mark.get('attrs', {}).get('href', '')
                            if self.is_figma_url(href):
                                # Get anchor text from node content
                                anchor_text = self._extract_text_from_adf_node(adf_data)
                                design_link = self.process_figma_url(href, anchor_text or 'Figma', '')
                                if design_link:
                                    design_links.append(design_link)
                
                # Recursively check content
                if 'content' in adf_data:
                    for node in adf_data.get('content', []):
                        design_links.extend(self.extract_figma_from_adf_structure(node))
            
            # Handle list (array of nodes)
            elif isinstance(adf_data, list):
                for item in adf_data:
                    design_links.extend(self.extract_figma_from_adf_structure(item))
        
        except Exception as e:
            print(f"Warning: ADF Figma extraction error: {e}")
        
        return design_links
    
    def _extract_text_from_adf_node(self, node: Dict[str, Any]) -> str:
        """Extract text content from a single ADF node"""
        if not isinstance(node, dict):
            return ""
        
        text_parts = []
        
        # Check for direct text
        if node.get('type') == 'text':
            text_parts.append(node.get('text', ''))
        
        # Check for content nodes
        if 'content' in node:
            for child in node.get('content', []):
                text_parts.append(self._extract_text_from_adf_node(child))
        
        return ' '.join(text_parts).strip()

    def extract_figma_links_with_anchors(self, text: str) -> List[DesignLink]:
        """Extract and normalize Figma links with anchor text detection"""
        design_links = []
        
        # First, try to extract from ADF structure if text looks like JSON
        if text.strip().startswith('{'):
            design_links.extend(self.extract_figma_from_adf_structure(text))
        
        # Then, try to find HTML anchor tags
        html_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
        for match in re.finditer(html_pattern, text, re.IGNORECASE):
            href = match.group(1)
            anchor_text = match.group(2).strip()
            
            if self.is_figma_url(href):
                design_link = self.process_figma_url(href, anchor_text, text)
                if design_link:
                    design_links.append(design_link)
        
        # Then, try markdown links
        md_pattern = r'\[([^\]]*)\]\(([^)]*)\)'
        for match in re.finditer(md_pattern, text, re.IGNORECASE):
            anchor_text = match.group(1).strip()
            href = match.group(2).strip()
            
            if self.is_figma_url(href):
                design_link = self.process_figma_url(href, anchor_text, text)
                if design_link:
                    design_links.append(design_link)
        
        # Try Jira wiki format
        wiki_pattern = r'\[([^|]*)\|([^\]]*)\]'
        for match in re.finditer(wiki_pattern, text, re.IGNORECASE):
            anchor_text = match.group(1).strip()
            href = match.group(2).strip()
            
            if self.is_figma_url(href):
                design_link = self.process_figma_url(href, anchor_text, text)
                if design_link:
                    design_links.append(design_link)
        
        # Finally, try plain URLs (not in any markup)
        # Match figma.com URLs that are standalone (more permissive pattern)
        plain_url_pattern = r'https?://(?:www\.)?figma\.com/[^\s<>\[\]"\'\),;]+(?:\?[^\s<>\[\]"\'\),;]*)?'
        for match in re.finditer(plain_url_pattern, text, re.IGNORECASE):
            href = match.group(0).rstrip('.,;:')  # Remove trailing punctuation
            # Check if this URL is not already captured by previous patterns
            already_captured = any(href in link.url or link.url in href for link in design_links)
            if not already_captured and self.is_figma_url(href):
                design_link = self.process_figma_url(href, "Figma", text)
                if design_link:
                    design_links.append(design_link)
        
        # Deduplicate by clean URL
        seen_urls = set()
        unique_links = []
        for link in design_links:
            if link.url not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link.url)
        
        return unique_links

    def is_figma_url(self, url: str) -> bool:
        """Check if URL is a Figma URL"""
        url = url or ''
        return 'figma.com' in url.lower()

    def is_anchor_suggesting_figma(self, anchor_text: str) -> bool:
        """Check if anchor text suggests Figma"""
        anchor_text = anchor_text or ''
        anchor_lower = anchor_text.lower().strip()
        return any(term in anchor_lower for term in self.figma_anchor_terms)

    def process_figma_url(self, href: str, anchor_text: str, full_text: str) -> Optional[DesignLink]:
        """Process and normalize Figma URL"""
        try:
            # Normalize URL
            clean_url = self.normalize_url(href)
            if not self.is_figma_url(clean_url):
                return None
            
            # Extract file key and node IDs
            file_key_match = re.search(r'/file/([A-Za-z0-9]+)', clean_url)
            proto_match = re.search(r'/proto/([A-Za-z0-9]+)', clean_url)
            node_match = re.search(r'node-id=([^&]+)', clean_url)
            
            file_key = None
            if file_key_match:
                file_key = file_key_match.group(1)
            elif proto_match:
                file_key = proto_match.group(1)
            
            node_ids = [node_match.group(1)] if node_match else None
            
            # Determine section
            section = self.determine_section(full_text, href)
            
            return DesignLink(
                url=clean_url,
                file_key=file_key or '',
                node_ids=node_ids,
                title=None,
                anchor_text=anchor_text,
                section=section
            )
        except Exception:
            return None

    def normalize_url(self, url: str) -> str:
        """Normalize URL by handling redirects and shorteners"""
        # Handle common redirect patterns
        redirect_patterns = [
            r'https?://[^/]+/link\?url=([^&]+)',
            r'https?://[^/]+/\?url=([^&]+)',
            r'url=([^&]+)'
        ]
        
        for pattern in redirect_patterns:
            match = re.search(pattern, url)
            if match:
                decoded_url = match.group(1)
                # URL decode
                import urllib.parse
                decoded_url = urllib.parse.unquote(decoded_url)
                return decoded_url
        
        return url

    def determine_section(self, full_text: str, url: str) -> str:
        """Determine which section the Figma link appears in"""
        # Find the position of the URL in the text
        url_pos = full_text.find(url)
        if url_pos == -1:
            return "Description"
        
        # Look backwards for the nearest heading
        text_before = full_text[:url_pos]
        headings = re.findall(r'\n\s*#+\s+([^\n]+)', text_before)
        if headings:
            last_heading = (headings[-1] or '').strip().lower()
            if 'acceptance' in last_heading or 'ac' in last_heading:
                return "Acceptance Criteria"
            elif 'test' in last_heading or 'qa' in last_heading:
                return "Test Scenarios"
            elif 'story' in last_heading:
                return "User Story"
            elif 'ada' in last_heading or 'accessibility' in last_heading:
                return "ADA"
        
        return "Description"

    def extract_brands(self, fields: Dict[str, Any]) -> str:
        """Extract brand information from Jira fields"""
        # Known Brands custom field ID: customfield_13482
        brand_fields = ['customfield_13482', 'brand', 'brands', 'product', 'market']
        print(f"\n🔍 DEBUG extract_brands - Checking fields: {brand_fields}")
        for field_name in brand_fields:
            field_exists = field_name in fields
            field_value = fields.get(field_name) if field_exists else None
            print(f"  Checking '{field_name}': exists={field_exists}, value={field_value}, type={type(field_value)}")
            # Check if field exists (even if value is None initially, might be in renderedFields)
            if field_name in fields:
                # If value is None, skip this iteration (might be populated later)
                if fields[field_name] is None:
                    continue
                # If value exists and is not empty
                if fields[field_name]:
                    # Handle list format (like [{'value': 'Marmot'}] or [{'name': 'Yankee Candle'}])
                    value = fields[field_name]
                
                # If value is HTML string (from renderedFields), strip HTML tags
                if isinstance(value, str) and '<' in value:
                    # Strip HTML and extract text
                    value = re.sub(r'<[^>]+>', ' ', value)
                    value = re.sub(r'\s+', ' ', value).strip()
                    if value and value.lower() not in ['none', 'n/a', 'na', '']:
                        return value
                
                if isinstance(value, list) and value:
                    if isinstance(value[0], dict):
                        # Extract from list of dicts
                        brand_names = []
                        for item in value:
                            brand_name = item.get('value', item.get('name', item.get('displayName', '')))
                            if brand_name:
                                brand_names.append(str(brand_name))
                        if brand_names:
                            result = ', '.join(brand_names)
                            print(f"  ✅ Found brands (list of dicts): {result}")
                            return result
                    else:
                        # Simple list of strings
                        result = ', '.join(str(v) for v in value if v)
                        print(f"  ✅ Found brands (list of strings): {result}")
                        return result
                elif value:
                    # Single value (string or dict)
                    if isinstance(value, dict):
                        result = value.get('value', value.get('name', value.get('displayName', str(value))))
                        if result and result.strip() and result.lower() not in ['none', 'n/a', 'na', '']:
                            print(f"  ✅ Found brands (dict): {result}")
                            return result
                        else:
                            print(f"  ⚠️ Brands dict result is empty/invalid: '{result}'")
                    elif isinstance(value, str) and value.strip() and value.lower() not in ['none', 'n/a', 'na', '']:
                        print(f"  ✅ Found brands (string): {value}")
                        return value.strip()
                    else:
                        # Try converting to string as last resort
                        value_str = str(value).strip()
                        if value_str and value_str.lower() not in ['none', 'n/a', 'na', '']:
                            print(f"  ✅ Found brands (converted to string): {value_str}")
                            return value_str
                        else:
                            print(f"  ⚠️ Brands value is empty/invalid: '{value}'")
        print(f"  ❌ No brands found, returning empty string")
        return ""

    def extract_components(self, fields: Dict[str, Any]) -> str:
        """Extract component information"""
        if 'components' in fields and fields['components']:
            return ', '.join([comp.get('name', '') for comp in fields['components']])
        return ""

    def extract_agile_team(self, fields: Dict[str, Any]) -> str:
        """Extract agile team information"""
        # NOTE: Agile Team custom field NOT found in this Jira instance
        # Only check explicit team fields, NOT assignee/reporter (those are individuals, not teams)
        team_fields = ['team', 'agile_team', 'squad', 'tribe']
        for field_name in team_fields:
            if field_name in fields and fields[field_name]:
                if isinstance(fields[field_name], dict):
                    return fields[field_name].get('displayName', fields[field_name].get('name', ''))
                return str(fields[field_name])
        return ""

    def extract_story_points(self, fields: Dict[str, Any]) -> str:
        """Extract story points"""
        # Known Story Points custom field ID: customfield_10117
        story_point_fields = ['customfield_10117', 'customfield_10002', 'story_points', 'storypoints']
        print(f"\n🔍 DEBUG extract_story_points - Checking fields: {story_point_fields}")
        for field_name in story_point_fields:
            field_exists = field_name in fields
            field_value = fields.get(field_name) if field_exists else None
            print(f"  Checking '{field_name}': exists={field_exists}, value={field_value}, type={type(field_value)}")
            # Check if field exists (even if value is None initially)
            if field_name in fields:
                # If value is None, skip this iteration (might be populated later)
                if fields[field_name] is None:
                    continue
                # Process the value
                value = fields[field_name]
                
                # If value is HTML string (from renderedFields), strip HTML tags
                if isinstance(value, str) and '<' in value:
                    # Strip HTML and extract text
                    value = re.sub(r'<[^>]+>', ' ', value)
                    value = re.sub(r'\s+', ' ', value).strip()
                    # Try to extract numeric value
                    match = re.search(r'\d+', value)
                    if match:
                        return match.group()
                
                # Handle numeric values (0, 1, 2, etc.)
                if isinstance(value, (int, float)):
                    result = str(int(value))
                    print(f"  ✅ Found story points (numeric): {result}")
                    return result
                # Handle string values
                if isinstance(value, str) and value.strip():
                    value_str = value.strip()
                    # Extract number from string if present
                    match = re.search(r'\d+', value_str)
                    if match:
                        result = match.group()
                        print(f"  ✅ Found story points (string with number): {result}")
                        return result
                    print(f"  ✅ Found story points (string): {value_str}")
                    return value_str
                # Handle dict format (if story points are in object format)
                if isinstance(value, dict):
                    points = value.get('value', value.get('name', ''))
                    if points:
                        result = str(points)
                        print(f"  ✅ Found story points (dict): {result}")
                        return result
        print(f"  ❌ No story points found, returning empty string")
        return ""

    def extract_environment(self, fields: Dict[str, Any]) -> str:
        """Extract environment information"""
        env_fields = ['environment', 'browser', 'device', 'platform']
        for field_name in env_fields:
            if field_name in fields and fields[field_name]:
                return str(fields[field_name])
        return ""

    def extract_severity_priority(self, fields: Dict[str, Any]) -> str:
        """Extract severity/priority information"""
        priority_info = []
        if 'priority' in fields and fields['priority']:
            priority_info.append(f"Priority: {fields['priority'].get('name', '')}")
        if 'severity' in fields and fields['severity']:
            priority_info.append(f"Severity: {fields['severity']}")
        return "; ".join(priority_info)

    def extract_kpi_metrics(self, fields: Dict[str, Any]) -> str:
        """Extract KPI/metrics information"""
        kpi_fields = ['kpi', 'metrics', 'success_criteria', 'measurement']
        for field_name in kpi_fields:
            if field_name in fields and fields[field_name]:
                return str(fields[field_name])
        return ""

    # ====================================================================================
    # DoR Field Extractors - Check Jira Custom Fields + Description Text
    # ====================================================================================
    
    def extract_user_story(self, fields: Dict[str, Any], all_text: str) -> str:
        """Extract user story from Jira custom fields or description"""
        # Known User Story custom field IDs: customfield_13389 (current), customfield_13287 (old)
        story_field_ids = ['customfield_13389', 'customfield_13287', 'user_story', 'userstory']
        
        print("\n" + "="*80)
        print("🔍 DEBUG: extract_user_story() called")
        print("="*80)
        
        for field_id in story_field_ids:
            if field_id in fields and fields[field_id]:
                content = self._extract_text_from_field(fields[field_id])
                print(f"✅ Found in {field_id}: {content[:100] if content else 'EMPTY'}...")
                if content and content.strip():  # Even "None" counts as present
                    print(f"✅ RETURNING User Story from {field_id} (length: {len(content)})")
                    return content
            else:
                print(f"❌ {field_id} not in fields or is empty")
        
        # Fallback: Iterate through all fields to find user story
        for field_key, field_value in fields.items():
            if field_value:
                # Check if field name contains user_story indicators
                field_str = str(field_key).lower()
                if 'story' in field_str or 'user' in field_str:
                    content = self._extract_text_from_field(field_value)
                    # Check if it looks like a user story
                    if content and ('as a' in content.lower() or 'as an' in content.lower()):
                        return content
        
        # Fallback: check if description contains user story section
        print("\n🔍 Checking description for User Story section...")
        description = fields.get('description', '')
        desc_text = self._extract_text_from_field(description)
        if desc_text:
            print(f"📄 Description length: {len(desc_text)} chars")
            print(f"📄 First 200 chars: {desc_text[:200]}")
            # Simple and robust: look for "User Story" followed by content until next section
            # Handle various formats: "User Story\nContent" or "User Story\n\nContent"
            if 'user story' in desc_text.lower():
                print("✅ Found 'User Story' in description!")
                # Find "User Story" section
                parts = re.split(r'(?i)user\s+story', desc_text, maxsplit=1)
                if len(parts) > 1:
                    after_heading = parts[1].strip()
                    # Extract until next major section (like "Acceptance Criteria", "Test Scenarios", etc.)
                    # Look for next capitalized heading
                    next_section_match = re.search(r'\n\s*([A-Z][A-Za-z\s]+(?:Criteria|Details|Solution|Scenarios|Notes|Impact|Estimate))', after_heading)
                    if next_section_match:
                        story_content = after_heading[:next_section_match.start()].strip()
                    else:
                        # No next section found, take everything
                        story_content = after_heading.strip()
                    
                    # Clean up the content (remove leading colons, newlines, etc.)
                    story_content = re.sub(r'^[\s:\n]+', '', story_content)
                    
                    print(f"📝 Extracted story content: {story_content[:150]}...")
                    
                    if story_content and len(story_content) > 15:
                        print(f"✅ RETURNING User Story from description (length: {len(story_content)})")
                        return story_content
                    else:
                        print(f"❌ Story content too short or empty (length: {len(story_content) if story_content else 0})")
            else:
                print("❌ 'User Story' not found in description")
            
            # Also try to find "As a..." pattern directly (more flexible pattern)
            as_pattern = re.search(r'(as\s+a\s+\w+.*?(?:i\s+want|we\s+need).*?(?:so\s+that|to).*?)(?:\.|$|\n\n)', desc_text, re.IGNORECASE | re.DOTALL)
            if as_pattern:
                extracted = as_pattern.group(1).strip()
                if len(extracted) > 20:  # Valid user story should be substantial
                    print(f"✅ RETURNING User Story from 'As a...' pattern (length: {len(extracted)})")
                    return extracted
        
        print("❌ NO USER STORY FOUND - Returning empty string")
        print("="*80 + "\n")
        return ""
    
    def extract_acceptance_criteria(self, fields: Dict[str, Any], all_text: str) -> str:
        """Extract acceptance criteria from Jira custom fields"""
        # Known AC custom field IDs: customfield_13281 (correct), customfield_13383 (fallback)
        ac_field_ids = ['customfield_13281', 'customfield_13383', 'acceptance_criteria', 'acceptancecriteria', 'ac']
        
        for field_id in ac_field_ids:
            if field_id in fields and fields[field_id]:
                content = self._extract_text_from_field(fields[field_id])
                if content:  # Field exists, even if content is minimal
                    return content
        
        # Fallback to description section search
        description = fields.get('description', '')
        desc_text = self._extract_text_from_field(description)
        if desc_text and 'acceptance criteria' in desc_text.lower():
            # Simple extraction: find section and get content
            parts = re.split(r'(?i)acceptance\s+criteria', desc_text, maxsplit=1)
            if len(parts) > 1:
                after_heading = parts[1].strip()
                # Get content until next major section (like "ADA", "Architectural", "Implementation", "Test")
                next_section = re.search(r'\n\s*\n(?:ADA|Architectural|Implementation|Test|User Story)', after_heading, re.IGNORECASE)
                if next_section:
                    content = after_heading[:next_section.start()].strip()
                else:
                    # Take large chunk - AC can be extensive
                    lines = after_heading.split('\n')
                    # Take until we see another capitalized heading or 100 lines
                    content_lines = []
                    for line in lines[:100]:
                        if line.strip() and re.match(r'^[A-Z][a-z]+\s+(?:Criteria|Details|Solution|Story)', line):
                            break
                        content_lines.append(line)
                    content = '\n'.join(content_lines).strip()
                
                if content:
                    return content
        
        return ""
    
    def extract_testing_steps(self, fields: Dict[str, Any], all_text: str) -> str:
        """Extract testing steps from Jira custom fields"""
        # Known Test Scenarios custom field ID (from logs: customfield_13286)
        test_field_ids = ['customfield_13286', 'test_scenarios', 'testing_steps', 'test_steps']
        
        for field_id in test_field_ids:
            if field_id in fields and fields[field_id]:
                content = self._extract_text_from_field(fields[field_id])
                if content:  # Field exists, even if content is minimal
                    return content
        
        # Fallback to description section search
        description = fields.get('description', '')
        desc_text = self._extract_text_from_field(description)
        if desc_text and 'test scenario' in desc_text.lower():
            # Simple extraction: find section and get content
            parts = re.split(r'(?i)test\s+scenarios?', desc_text, maxsplit=1)
            if len(parts) > 1:
                after_heading = parts[1].strip()
                # Get content until next major section or end
                next_section = re.search(r'\n\s*\n[A-Z][a-z]+.*?(?:Criteria|Details|Solution|Notes|Story)', after_heading)
                if next_section:
                    content = after_heading[:next_section.start()].strip()
                else:
                    # Take large chunk - test scenarios can be extensive
                    lines = after_heading.split('\n')
                    content_lines = []
                    for line in lines[:100]:
                        if line.strip() and re.match(r'^[A-Z][a-z]+\s+(?:Criteria|Details|Solution|Story)', line):
                            break
                        content_lines.append(line)
                    content = '\n'.join(content_lines).strip()
                
                if content:
                    return content
        
        return ""
    
    def extract_implementation_details(self, fields: Dict[str, Any], all_text: str) -> str:
        """Extract implementation details from Jira custom fields"""
        impl_field_ids = ['implementation_details', 'implementation', 'dev_notes', 'technical_notes']
        
        for field_id in impl_field_ids:
            if field_id in fields and fields[field_id]:
                content = self._extract_text_from_field(fields[field_id])
                if content:  # Even "None" counts as present
                    return content
        
        # Fallback to description section search
        description = fields.get('description', '')
        desc_text = self._extract_text_from_field(description)
        if desc_text and 'implementation details' in desc_text.lower():
            # Simple extraction: find section and get content until next section
            parts = re.split(r'(?i)implementation\s+details', desc_text, maxsplit=1)
            if len(parts) > 1:
                after_heading = parts[1].strip()
                # Get content until next section or end
                next_section = re.search(r'\n\s*\n[A-Z][a-z]+.*?(?:Criteria|Details|Solution|Scenarios|Story)', after_heading)
                if next_section:
                    content = after_heading[:next_section.start()].strip()
                else:
                    content = re.split(r'\n\s*\n', after_heading, maxsplit=1)[0].strip()
                
                # Even "None" is valid - means field exists but not applicable
                if content:
                    return content
        
        return ""
    
    def extract_architectural_solution(self, fields: Dict[str, Any], all_text: str) -> str:
        """Extract architectural solution from Jira custom fields"""
        # Known Architectural Solution custom field ID (from logs: customfield_13597)
        arch_field_ids = ['customfield_13597', 'architectural_solution', 'architecture', 'technical_design']
        
        for field_id in arch_field_ids:
            if field_id in fields and fields[field_id]:
                content = self._extract_text_from_field(fields[field_id])
                if content:  # Even "None" counts as present
                    return content
        
        # Fallback to description section search
        description = fields.get('description', '')
        desc_text = self._extract_text_from_field(description)
        if desc_text and 'architectural solution' in desc_text.lower():
            # Simple extraction: find section and get content
            parts = re.split(r'(?i)architectural\s+solution', desc_text, maxsplit=1)
            if len(parts) > 1:
                after_heading = parts[1].strip()
                # Get content until next section
                next_section = re.search(r'\n\s*\n[A-Z][a-z]+.*?(?:Criteria|Details|Solution|Scenarios|Story)', after_heading)
                if next_section:
                    content = after_heading[:next_section.start()].strip()
                else:
                    content = re.split(r'\n\s*\n', after_heading, maxsplit=1)[0].strip()
                
                # Even "None" is valid
                if content:
                    return content
        
        return ""
    
    def extract_ada_criteria(self, fields: Dict[str, Any], all_text: str) -> str:
        """Extract ADA criteria from Jira custom fields"""
        # Known ADA custom field ID (from logs: customfield_13298)
        ada_field_ids = ['customfield_13298', 'ada_acceptance_criteria', 'ada_criteria', 'accessibility', 'a11y']
        
        for field_id in ada_field_ids:
            if field_id in fields and fields[field_id]:
                content = self._extract_text_from_field(fields[field_id])
                # If content is explicitly "None", treat as missing (not present)
                if content and content.strip().lower() not in ['none', 'n/a', 'na', 'null', '']:
                    return content
        
        # Fallback to description section search
        description = fields.get('description', '')
        desc_text = self._extract_text_from_field(description)
        if desc_text and 'ada' in desc_text.lower():
            # Look for "ADA Acceptance Criteria" or "ADA Criteria"
            parts = re.split(r'(?i)ada\s+(?:acceptance\s+)?criteria', desc_text, maxsplit=1)
            if len(parts) > 1:
                after_heading = parts[1].strip()
                # Get content until next section
                next_section = re.search(r'\n\s*\n[A-Z][a-z]+.*?(?:Criteria|Details|Solution|Scenarios|Story)', after_heading)
                if next_section:
                    content = after_heading[:next_section.start()].strip()
                else:
                    content = re.split(r'\n\s*\n', after_heading, maxsplit=1)[0].strip()
                
                # If content is explicitly "None", treat as missing (not present)
                if content and content.strip().lower() not in ['none', 'n/a', 'na', 'null', '']:
                    return content
        
        return ""
    
    def _extract_text_from_field(self, field_value: Any) -> str:
        """Helper: Extract plain text from various Jira field formats (string, dict, list)"""
        if not field_value:
            return ""
        
        # If it's a string, return it
        if isinstance(field_value, str):
            return field_value.strip()
        
        # If it's a dict (Atlassian Document Format or other structured data)
        if isinstance(field_value, dict):
            # Handle Atlassian Document Format (ADF)
            if 'type' in field_value and 'content' in field_value:
                return self._extract_from_adf(field_value)
            # Handle simple dict with 'value' key
            if 'value' in field_value:
                return str(field_value['value']).strip()
            # Fallback: convert dict to string
            return str(field_value).strip()
        
        # If it's a list
        if isinstance(field_value, list):
            if field_value and isinstance(field_value[0], dict):
                # List of objects (like brands)
                values = [item.get('value', item.get('name', str(item))) for item in field_value]
                return ', '.join(str(v) for v in values if v)
            # Simple list
            return ', '.join(str(item) for item in field_value if item)
        
        return str(field_value).strip()
    
    def _extract_from_adf(self, adf_content: Dict[str, Any]) -> str:
        """Extract plain text from Atlassian Document Format (ADF)"""
        text_parts = []
        
        def traverse(node, depth=0):
            if isinstance(node, dict):
                node_type = node.get('type', '')
                
                # Handle text nodes
                if node_type == 'text' and 'text' in node:
                    text_parts.append(node['text'])
                
                # Handle paragraphs - add newline after each
                elif node_type == 'paragraph':
                    if 'content' in node:
                        for child in node['content']:
                            traverse(child, depth + 1)
                        # Add newline after paragraph
                        text_parts.append('\n')
                
                # Handle headings
                elif node_type == 'heading':
                    if 'content' in node:
                        text_parts.append('\n')  # Newline before heading
                        for child in node['content']:
                            traverse(child, depth + 1)
                        text_parts.append('\n')  # Newline after heading
                
                # Handle lists
                elif node_type in ['bulletList', 'orderedList']:
                    if 'content' in node:
                        for child in node['content']:
                            traverse(child, depth + 1)
                        text_parts.append('\n')
                
                # Handle list items
                elif node_type == 'listItem':
                    if 'content' in node:
                        for child in node['content']:
                            traverse(child, depth + 1)
                        text_parts.append('\n')
                
                # Generic traversal for other node types
                elif 'content' in node:
                    for child in node['content']:
                        traverse(child, depth + 1)
                        
            elif isinstance(node, list):
                for item in node:
                    traverse(item, depth)
        
        traverse(adf_content)
        # Join and clean up excessive newlines
        text = ''.join(text_parts)
        # Normalize multiple newlines to double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip().strip()
    
    def _search_in_description(self, description: Any, keywords: List[str]) -> str:
        """Helper: Search for keywords in description and extract content"""
        desc_text = self._extract_text_from_field(description)
        if not desc_text:
            return ""
        
        for keyword in keywords:
            pattern = rf'(?i){re.escape(keyword)}:?\s*([^\n]{{20,}})'
            match = re.search(pattern, desc_text)
            if match:
                return match.group(1).strip()
        
        return ""

    def calculate_dor_coverage(self, parsed_data: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """Calculate DoR coverage - present, missing, and conflicts"""
        card_type = parsed_data['card_type']
        applicable_fields = self.dor_fields.get(card_type, [])

        print(f"\n🔍 DoR Coverage Check - Card Type: {card_type}")
        print(f"Applicable DoR fields: {applicable_fields}")
        print(f"Fields in parsed_data: {list(parsed_data['fields'].keys())}")

        present_fields = []
        missing_fields = []
        conflicts = []

        for field in applicable_fields:
            field_value = parsed_data['fields'].get(field)
            print(f"\nChecking '{field}': {field_value[:100] if field_value else 'EMPTY'}...")
            
            # Special handling for story_points: 0 is a valid value
            if field == 'story_points':
                if field in parsed_data['fields'] and parsed_data['fields'][field] is not None and str(parsed_data['fields'][field]).strip():
                    if not self.is_placeholder_content(parsed_data['fields'][field]):
                        print(f"  ✅ PRESENT")
                        present_fields.append(field)
                    else:
                        print(f"  ❌ MISSING (placeholder)")
                        missing_fields.append(field)
                else:
                    print(f"  ❌ MISSING (not in fields or empty)")
                    missing_fields.append(field)
            else:
                # For other fields, empty string means missing
                if field in parsed_data['fields'] and parsed_data['fields'][field]:
                    if not self.is_placeholder_content(parsed_data['fields'][field]):
                        print(f"  ✅ PRESENT")
                        present_fields.append(field)
                    else:
                        print(f"  ❌ MISSING (placeholder)")
                        missing_fields.append(field)
                else:
                    print(f"  ❌ MISSING (not in fields or empty)")
                    missing_fields.append(field)
        
        # Detect conflicts in ACs
        ac_content = parsed_data['fields'].get('acceptance_criteria', '')
        if ac_content:
            conflicts.extend(self.detect_ac_conflicts(ac_content))
        
        return present_fields, missing_fields, conflicts

    def detect_ac_conflicts(self, ac_content: str) -> List[str]:
        """Detect contradictory ACs"""
        conflicts = []
        contradictory_terms = [
            ('immediately', 'after delay'),
            ('always', 'sometimes'),
            ('required', 'optional'),
            ('popup opens immediately', 'second CTA opens popup')
        ]
        
        ac_content = ac_content or ''
        for term1, term2 in contradictory_terms:
            if term1 in ac_content.lower() and term2 in ac_content.lower():
                conflicts.append(f"Contradictory ACs: '{term1}' and '{term2}' found")
        
        return conflicts

    def determine_status(self, present_fields: List[str], missing_fields: List[str], conflicts: List[str], card_type: str) -> str:
        """Determine readiness status based on rules, not scores"""
        # Check for critical missing elements
        if card_type in ['story', 'feature']:
            if 'user_story' not in present_fields:
                return "Not Ready"
        
        if not any(field in present_fields for field in ['acceptance_criteria', 'testing_steps']):
            return "Not Ready"
        
        # Check for refinement needs
        if conflicts or any(field in missing_fields for field in ['implementation_details', 'architectural_solution']):
            return "Needs Refinement"
        
        # Check for UI elements without ADA
        if any(field in present_fields for field in ['user_story', 'acceptance_criteria']) and 'ada_criteria' in missing_fields:
            return "Needs Refinement"
        
        # If all critical elements present and no conflicts
        if len(missing_fields) == 0 and len(conflicts) == 0:
            return "Ready"
        
        return "Needs Refinement"

    def generate_suggested_rewrite(self, parsed_data: Dict[str, Any]) -> str:
        """Generate detailed improvement suggestions for user story (not just rewrite)"""
        current_story = parsed_data['fields'].get('user_story', '') or ''
        description = self._extract_text_from_field(parsed_data.get('description', '')) or ''
        title = parsed_data.get('title', '') or ''
        acceptance_criteria = parsed_data['fields'].get('acceptance_criteria', '') or ''
        
        # Extract domain terms from the ticket
        domain_terms = self.extract_domain_terms(parsed_data)
        
        # Analyze current story for issues
        issues = []
        improvements = []
        
        current_story_lower = (current_story or '').lower()
        
        # Check for common issues
        if not current_story or len(current_story.strip()) < 20:
            issues.append("User story is missing or too short")
            improvements.append("Add a complete user story following the format: 'As a [persona], I want [goal], so that [benefit]'")
        else:
            # Check for persona issues
            if 'as a' not in current_story_lower:
                issues.append("Missing persona ('As a...')")
                improvements.append("Specify a clear persona (e.g., 'As a shopper', 'As a registered user', 'As a guest user')")
            elif 'user' in current_story_lower and current_story_lower.count('user') == 1:
                issues.append("Persona is too generic ('user')")
                improvements.append("Replace generic 'user' with a specific persona that reflects the actual user type (e.g., 'shopper', 'customer', 'admin', 'guest visitor')")
            
            # Check for goal issues
            if 'i want' not in current_story_lower:
                issues.append("Missing goal ('I want...')")
                improvements.append("Clearly state what the user wants to accomplish with specific, measurable actions")
            else:
                # Check if goal is too vague
                vague_words = ['better', 'improve', 'nice', 'good', 'easier', 'faster']
                if any(word in current_story_lower for word in vague_words):
                    issues.append("Goal contains vague language")
                    improvements.append("Replace vague terms with specific, actionable goals. Instead of 'better filters', use 'filters accessible at the top of the page'")
                
                # Check if goal focuses on implementation details
                implementation_words = ['click', 'button', 'api', 'database', 'code', 'implement']
                if any(word in current_story_lower for word in implementation_words):
                    issues.append("Goal focuses on 'how' instead of 'what'")
                    improvements.append("Focus on user needs and outcomes, not technical implementation. Remove references to buttons, clicks, or technical details")
            
            # Check for benefit issues
            if 'so that' not in current_story_lower:
                issues.append("Missing benefit ('so that...')")
                improvements.append("Add a clear business value or user benefit that explains why this feature matters")
            else:
                # Check if benefit is missing or weak
                benefit_part = current_story.split('so that')[-1] if 'so that' in current_story else ''
                if len(benefit_part.strip()) < 15:
                    issues.append("Benefit is too short or unclear")
                    improvements.append("Expand the benefit to clearly explain the value: impact on user experience, business metrics, or user goals")
            
            # Check for specificity
            if len(current_story) < 80:
                issues.append("Story lacks detail and context")
                improvements.append("Add more context about what specifically the user wants, where it applies, and what constraints or considerations exist")
            
            # Check for business value
            business_value_words = ['revenue', 'conversion', 'engagement', 'satisfaction', 'efficiency', 'time', 'cost']
            if not any(word in current_story_lower for word in business_value_words):
                issues.append("Story doesn't clearly communicate business value")
                improvements.append("Enhance the 'so that' clause to include measurable outcomes or business impact (e.g., 'reduce time to find products', 'increase conversion rates', 'improve user satisfaction')")
        
        # Build detailed improvement suggestions
        suggestion_parts = []
        
        if issues:
            suggestion_parts.append("**Issues Identified:**")
            for i, issue in enumerate(issues, 1):
                suggestion_parts.append(f"{i}. {issue}")
            suggestion_parts.append("")
        
        suggestion_parts.append("**Recommended Improvements:**")
        for i, improvement in enumerate(improvements, 1):
            suggestion_parts.append(f"{i}. {improvement}")
        suggestion_parts.append("")
        
        # Provide a suggested enhanced version
        persona = self.extract_persona(description, title) or 'shopper'
        goal = self.extract_goal(description, title) or ''
        benefit = self.extract_benefit(description, title) or ''
        
        # Extract specific details from title and description
        title_lower = (title or '').lower()
        description_lower = (description or '').lower()
        
        # Enhance goal with specific details
        if 'filter' in title_lower or 'filter' in description_lower:
            if not goal or 'filter' not in goal.lower():
                goal = "access top filters at the top of the page with the left filter panel removed"
            if not benefit or len(benefit) < 20:
                benefit = "quickly find what I'm looking for, view more products on my screen, and reduce the number of clicks needed to apply filters"
        elif 'checkout' in title_lower or 'payment' in description_lower:
            if not benefit or len(benefit) < 20:
                benefit = "complete purchases faster with fewer steps, reducing cart abandonment and improving my overall shopping experience"
        elif 'search' in title_lower or 'search' in description_lower:
            if not benefit or len(benefit) < 20:
                benefit = "find products more efficiently, saving time and improving my shopping experience"
        
        # Build enhanced story suggestion
        if goal and benefit:
            enhanced_story = f"As a {persona}, I want {goal}, so that {benefit}."
            
            # Add context from acceptance criteria if available
            if acceptance_criteria and len(acceptance_criteria) > 20:
                ac_lines = [line.strip('- •*1234567890.').strip() for line in acceptance_criteria.split('\n') if line.strip()]
                if ac_lines:
                    key_requirement = ac_lines[0][:100] if len(ac_lines[0]) > 100 else ac_lines[0]
                    enhanced_story += f" This includes ensuring {key_requirement.lower()}."
            
            # Add business value context
            if 'revenue' in description_lower or 'conversion' in description_lower:
                enhanced_story += " This improvement will drive business outcomes by reducing friction in the user journey and increasing conversion rates."
            elif 'performance' in description_lower or 'speed' in description_lower:
                enhanced_story += " This enhancement will optimize performance and deliver a faster, more responsive experience for all users."
            elif 'accessibility' in description_lower or 'ada' in description_lower:
                enhanced_story += " This feature will improve accessibility and ensure compliance with ADA standards, making the experience inclusive for all users."
            else:
                enhanced_story += " This improvement aligns with user needs and enhances overall product usability while maintaining high standards for performance and accessibility."
            
            suggestion_parts.append("**Suggested Enhanced Story:**")
            suggestion_parts.append(f'"{enhanced_story}"')
        else:
            suggestion_parts.append("**Note:** Unable to generate enhanced story - please review the ticket description and acceptance criteria for more context.")
        
        return "\n".join(suggestion_parts)

    def extract_domain_terms(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Extract domain-specific terms from ticket content"""
        title = parsed_data.get('title', '') or ''
        description = parsed_data.get('description', '') or ''
        all_text = f"{title} {description}"
        domain_keywords = [
            'PayPal', 'ABTasty', 'SFCC-Checkout', 'PLP', 'Filters', 'Yankee', 'Marmot', 'Graco',
            'checkout', 'payment', 'filter', 'search', 'cart', 'login', 'auth', 'password'
        ]
        return [term for term in domain_keywords if term.lower() in all_text.lower()]

    def extract_persona(self, description: str, title: str) -> str:
        """Extract persona from content"""
        title = title or ''
        description = description or ''
        text = f"{title} {description}".lower()
        persona_synonyms = ['shopper', 'user', 'customer', 'visitor', 'admin', 'registered user']
        
        for persona in persona_synonyms:
            if persona in text:
                return persona
        
        return "user"

    def extract_goal(self, description: str, title: str) -> str:
        """Extract main goal from content (NO truncation for detailed suggestions)"""
        title = title or ''
        description = description or ''
        text = f"{title} {description}".lower()
        
        # Look for "I want" pattern first
        want_match = re.search(r'i want (?:to )?([^,\.]+)', text, re.IGNORECASE)
        if want_match:
            return want_match.group(1).strip()
        
        # Look for imperative verbs (what user wants to DO)
        goal_patterns = [
            r'(access|view|see|use|enable|disable|configure|create|update|delete|manage|filter|search|select|open|close|add|remove)\s+([^.,;]+)',
            r'(implement|build|develop|integrate|upgrade|migrate|refactor)\s+([^.,;]+)',
        ]
        
        for pattern in goal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                verb = match.group(1)
                object_phrase = match.group(2).strip()
                # NO TRUNCATION - keep full text for detailed suggestions!
                return f"{verb} {object_phrase}"
        
        # Fallback to first meaningful sentence from title/description
        if title:
            sentences = [s.strip() for s in title.split('.') if len(s.strip()) > 10]
            if sentences:
                goal = sentences[0]
                # NO TRUNCATION - keep full goal text!
                return goal
        
        return "achieve the desired functionality"

    def extract_benefit(self, description: str, title: str) -> str:
        """Extract benefit from content"""
        title = title or ''
        description = description or ''
        text = f"{title} {description}".lower()
        
        # Look for "so that" pattern (strongest indicator)
        so_that_match = re.search(r'so that (?:i can )?([^.,]+)', text, re.IGNORECASE)
        if so_that_match:
            return so_that_match.group(1).strip()
        
        # Look for benefit indicators
        benefit_patterns = [
            r'(?:in order to|to allow|to enable|enabling|allowing)\s+(?:users? to )?([^.,;]+)',
            r'(?:benefit|advantage|value):\s*([^.,;]+)',
            r'(?:improve|enhance|increase|reduce|optimize)\s+([^.,;]+)',
        ]
        
        for pattern in benefit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                benefit = match.group(1).strip()
                # NO TRUNCATION - keep full benefit text!
                return benefit
        
        # Generic fallback based on ticket type
        if any(word in text for word in ['filter', 'search', 'find']):
            return "quickly find what I'm looking for"
        elif any(word in text for word in ['performance', 'speed', 'load']):
            return "have a faster and smoother experience"
        elif any(word in text for word in ['bug', 'fix', 'broken']):
            return "use the feature as intended without issues"
        
        return "improve my overall experience"

    def generate_acceptance_criteria_rewrites(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Generate contextual AC rewrites from card content"""
        current_ac = parsed_data['fields'].get('acceptance_criteria', '')
        domain_terms = self.extract_domain_terms(parsed_data)
        design_links = parsed_data['design_links']
        
        if current_ac and not self.is_placeholder_content(current_ac):
            # Normalize and rewrite existing ACs
            ac_lines = [line.strip() for line in current_ac.split('\n') if line.strip()]
            rewritten_acs = []
            
            for ac in ac_lines:
                ac = ac or ''
                if not any(phrase in ac.lower() for phrase in self.banned_ac_phrases):
                    # Enhance with domain terms and measurability
                    enhanced_ac = self.enhance_ac_with_domain(ac, domain_terms, design_links)
                    rewritten_acs.append(enhanced_ac)
                else:
                    # Replace banned phrases with specific requirements
                    enhanced_ac = self.replace_banned_phrases(ac, domain_terms)
                    rewritten_acs.append(enhanced_ac)
            
            return rewritten_acs
        else:
            # Generate new ACs from description + domain terms
            return self.generate_new_acceptance_criteria(parsed_data, domain_terms, design_links)

    def enhance_ac_with_domain(self, ac: str, domain_terms: List[str], design_links: List[DesignLink]) -> str:
        """Enhance AC with domain terms and design context"""
        ac = ac or ''
        enhanced = ac
        
        # Add timing if not present
        if enhanced and not re.search(r'\d+\s*(ms|s|seconds?)', enhanced.lower()):
            enhanced += " (≤300ms response time)"
        
        # Add domain context if missing
        if enhanced and not any(term.lower() in enhanced.lower() for term in domain_terms):
            if domain_terms:
                enhanced += f" (using {domain_terms[0]})"
        
        # Add Figma reference if design links present
        if enhanced and design_links and 'design' in enhanced.lower():
            figma_ref = f" per Figma {design_links[0].file_key}"
            if design_links[0].node_ids:
                figma_ref += f" node {design_links[0].node_ids[0]}"
            enhanced += figma_ref
        
        return enhanced

    def replace_banned_phrases(self, ac: str, domain_terms: List[str]) -> str:
        """Replace banned generic phrases with specific requirements"""
        ac = ac or ''
        enhanced = ac
        
        replacements = {
            "valid input": "input that passes validation rules",
            "gracefully": "with appropriate error handling",
            "meets requirements": "satisfies the specified acceptance criteria",
            "works as expected": "functions according to the defined behavior"
        }
        
        for banned, replacement in replacements.items():
            enhanced = enhanced.replace(banned, replacement)
        
        return enhanced

    def generate_new_acceptance_criteria(self, parsed_data: Dict[str, Any], domain_terms: List[str], design_links: List[DesignLink]) -> List[str]:
        """Generate new ACs derived from description + domain terms"""
        description = parsed_data.get('description', '') or ''
        title = parsed_data.get('title', '') or ''
        
        # Template ACs based on domain patterns
        ac_templates = []
        
        # Check for specific domain patterns
        if any(term in f"{title} {description}".lower() for term in ['paypal', 'payment', 'checkout']):
            ac_templates.extend([
                "PayPal popup opens immediately (≤300ms) on first CTA click via user gesture",
                "Secondary PayPal CTA and helper copy are not rendered after first click",
                "ABTasty PayPal patches are disabled during validation",
                "If browser blocks popup, show inline message with Retry action",
                "Focus returns to PayPal CTA when popup closes (success or cancel)",
                "Analytics log: paypal_cta_click, paypal_popup_opened, paypal_completed with site context"
            ])
        elif any(term in f"{title} {description}".lower() for term in ['filter', 'search', 'plp']):
            ac_templates.extend([
                "Filter selection updates results count within 500ms",
                "Top 5 pinned filters remain visible during scroll",
                "More Filters flyout opens/closes with keyboard navigation",
                "Sticky bar shows selected filter tokens with remove (×) option",
                "Horizontal overflow enables scroll with keyboard arrows",
                "Grid updates within ≤1s after filter changes"
            ])
        else:
            # Generic but contextual ACs
            ac_templates.extend([
                f"User action triggers expected response within ≤300ms",
                f"Error states display appropriate messages with retry options",
                f"All interactive elements support keyboard navigation",
                f"Screen reader announces content changes appropriately",
                f"Analytics capture relevant user interactions"
            ])
        
        # Add Figma reference if design links present
        if design_links:
            figma_ref = f" (matches Figma {design_links[0].file_key}"
            if design_links[0].node_ids:
                figma_ref += f" node {design_links[0].node_ids[0]}"
            figma_ref += ")"
            ac_templates[0] += figma_ref
        
        return ac_templates[:7]  # Return 5-7 ACs

    def generate_test_scenarios(self, parsed_data: Dict[str, Any], ac_rewrites: List[str]) -> Dict[str, List[str]]:
        """Generate mature, descriptive test scenarios directly mapped from acceptance criteria"""
        scenarios = {
            'positive': [],
            'negative': [],
            'error': []
        }
        
        # Extract context from ticket
        title = parsed_data.get('title', '') or ''
        description = self._extract_text_from_field(parsed_data.get('description', '')) or ''
        acceptance_criteria = parsed_data['fields'].get('acceptance_criteria', '') or ''
        testing_steps = parsed_data['fields'].get('testing_steps', '') or ''
        
        # Combine all text for context analysis
        all_context = f"{title} {description} {acceptance_criteria}".lower()
        
        # Parse acceptance criteria into individual ACs
        ac_lines = []
        if acceptance_criteria:
            # Split by common delimiters
            for line in acceptance_criteria.split('\n'):
                line = re.sub(r'<[^>]+>', '', line).strip()  # Remove HTML
                line = re.sub(r'^\d+[\.\)]\s*', '', line)  # Remove numbering
                line = re.sub(r'^[-•*]\s*', '', line)  # Remove bullets
                if len(line) > 15 and line not in ['', 'None', 'N/A']:
                    ac_lines.append(line)
        
        # Generate positive scenarios from ACs
        for ac in ac_lines[:8]:  # Limit to 8 ACs to avoid too many scenarios
            if not ac or len(ac) < 15:
                continue
                
            ac_lower = ac.lower()
            
            # Create mature, descriptive positive scenario from AC
            # Extract key actions and outcomes
            if 'filter' in ac_lower:
                if 'panel' in ac_lower or 'left' in ac_lower:
                    scenarios['positive'].append(f"Left filter panel is removed and top filters are accessible, ensuring the product grid displays with maximum screen real estate as specified in the design requirements")
                elif 'bar' in ac_lower or 'top' in ac_lower:
                    scenarios['positive'].append(f"Filter bar is correctly positioned at the top of the page and styled according to design specifications, maintaining visual consistency and accessibility standards")
                elif 'quick' in ac_lower or 'relevant' in ac_lower:
                    scenarios['positive'].append(f"Only relevant quick filters are displayed (up to maximum of 5, configurable by merchandising team), ensuring users see the most applicable filtering options without visual clutter")
                elif 'flyout' in ac_lower or 'panel' in ac_lower:
                    scenarios['positive'].append(f"Flyout panel slides out smoothly with proper animation timing, displaying only the relevant filter options with controls that match design requirements and accessibility guidelines")
                elif 'apply' in ac_lower or 'trigger' in ac_lower:
                    scenarios['positive'].append(f"Filter application triggers immediate product grid refresh with updated results, maintaining responsive user experience and clear visual feedback of applied filters")
                elif 'sticky' in ac_lower or 'bar' in ac_lower:
                    scenarios['positive'].append(f"Applied filters are correctly displayed in the sticky filter bar with proper visual indicators, allowing users to see and manage active filters throughout their browsing session")
                elif 'remove' in ac_lower or 'clear' in ac_lower:
                    scenarios['positive'].append(f"Filter removal updates product results in real-time without page refresh, maintaining smooth user experience and ensuring data consistency across the product listing page")
                elif 'collapse' in ac_lower or 'close' in ac_lower:
                    scenarios['positive'].append(f"All filters are visible in collapsed state with proper UI animations matching Figma specifications, and panel closes as expected with state preservation")
                else:
                    scenarios['positive'].append(f"Filter functionality works as specified: {ac[:100]}...")
            
            elif 'desktop' in ac_lower or 'tablet' in ac_lower or 'mobile' in ac_lower or 'device' in ac_lower:
                devices = []
                if 'desktop' in ac_lower:
                    devices.append('desktop')
                if 'tablet' in ac_lower:
                    devices.append('tablet')
                if 'mobile' in ac_lower:
                    devices.append('mobile')
                device_list = ' and '.join(devices) if devices else 'all supported devices'
                scenarios['positive'].append(f"Feature is fully functional and displays correctly on {device_list}, maintaining responsive design principles and consistent user experience across different screen sizes and orientations")
            
            elif 'validation' in ac_lower or 'validate' in ac_lower or 'required' in ac_lower:
                scenarios['positive'].append(f"Validation rules are correctly implemented: {ac[:120]}...")
            
            elif 'display' in ac_lower or 'show' in ac_lower or 'visible' in ac_lower:
                scenarios['positive'].append(f"Content displays correctly as specified: {ac[:120]}...")
            
            elif 'user' in ac_lower and ('can' in ac_lower or 'able' in ac_lower):
                scenarios['positive'].append(f"User can successfully complete the intended action: {ac[:120]}...")
            
            else:
                # Generic but mature positive scenario
                scenarios['positive'].append(f"{ac[:150]}...")
        
        # Generate negative scenarios based on ACs and context
        negative_keywords = ['invalid', 'error', 'incorrect', 'wrong', 'prevent', 'block', 'reject', 'deny', 'unauthorized', 'boundary', 'limit', 'max', 'min', 'empty', 'null']
        has_negative_ac = any(keyword in all_context for keyword in negative_keywords)
        
        if not has_negative_ac and ac_lines:
            # Generate negative scenarios from positive ACs (inverse testing)
            for ac in ac_lines[:4]:
                ac_lower = ac.lower()
                if 'filter' in ac_lower:
                    scenarios['negative'].append(f"Invalid filter combinations or out-of-range values are rejected with clear error messaging, preventing system errors and maintaining data integrity")
                elif 'required' in ac_lower or 'must' in ac_lower:
                    scenarios['negative'].append(f"Required field validation prevents submission with appropriate user feedback when mandatory fields are left empty or contain invalid data")
                elif 'display' in ac_lower or 'show' in ac_lower:
                    scenarios['negative'].append(f"System handles edge cases gracefully when data is unavailable, showing appropriate fallback content or messaging without breaking the user interface")
                else:
                    scenarios['negative'].append(f"Invalid input or unauthorized actions are prevented with appropriate error handling and user guidance, maintaining system security and data integrity")
        
        # Add standard negative scenarios if needed
        if len(scenarios['negative']) < 4:
            scenarios['negative'].extend([
                "Invalid input shows appropriate error message with clear guidance and actionable next steps for the user",
                "System prevents unauthorized access and maintains security boundaries with proper authentication and authorization checks",
                "Boundary conditions are handled correctly (empty, null, max values) with appropriate validation and user feedback",
                "Required fields validation works correctly with real-time feedback and prevents form submission until all mandatory fields are properly completed"
            ])
        
        # Generate error/resilience scenarios
        if len(scenarios['error']) < 4:
            scenarios['error'].extend([
                "System handles network timeout gracefully with retry mechanism and user notification, ensuring data consistency and preventing partial state updates",
                "Database connection failure is handled with appropriate fallback mechanism, displaying user-friendly error messages while logging technical details for troubleshooting",
                "API errors return user-friendly messages and log technical details for debugging, maintaining system stability and providing clear communication to end users",
                "Partial data loads are handled without breaking functionality, showing available content immediately while gracefully handling missing data with appropriate placeholders or loading states"
            ])
        
        # Add non-functional test scenarios
        if 'filter' in all_context or 'ui' in all_context or 'interface' in all_context:
            scenarios['positive'].append("Keyboard navigation works seamlessly for all interactive filter elements (Tab, Enter, Escape, Arrow keys), ensuring full accessibility compliance")
            scenarios['positive'].append("Screen reader announces all filter state changes and product grid updates with proper ARIA labels, maintaining WCAG 2.1 AA compliance")
        
        scenarios['negative'].extend([
            "System prevents SQL injection and XSS attacks on all filter inputs and search parameters, maintaining security best practices and data protection",
            "CSRF tokens are validated for all state-changing operations including filter applications, ensuring protection against cross-site request forgery attacks"
        ])
        
        scenarios['error'].extend([
            "Session expiration redirects user appropriately with state preservation, allowing users to return to their filtered product view after re-authentication",
            "Concurrent operations maintain data integrity without conflicts when multiple filters are applied rapidly, ensuring consistent product grid updates",
            "Memory leaks are prevented during long browsing sessions with multiple filter interactions, maintaining optimal browser performance and user experience",
            "Browser crashes or tab closes preserve critical user data including applied filters, allowing users to restore their previous session state upon return"
        ])
        
        # Limit to reasonable number (keep similar count)
        scenarios['positive'] = scenarios['positive'][:12]
        scenarios['negative'] = scenarios['negative'][:8]
        scenarios['error'] = scenarios['error'][:8]
        
        # Remove duplicates while preserving order
        seen = set()
        for key in scenarios:
            unique_scenarios = []
            for scenario in scenarios[key]:
                scenario_lower = scenario.lower()
                if scenario_lower not in seen:
                    seen.add(scenario_lower)
                    unique_scenarios.append(scenario)
            scenarios[key] = unique_scenarios
        
        # Hyperlink Figma references in test scenarios
        design_links = parsed_data.get('design_links', [])
        if design_links:
            scenarios['positive'] = [self.hyperlink_figma_references(s, design_links) for s in scenarios['positive']]
            scenarios['negative'] = [self.hyperlink_figma_references(s, design_links) for s in scenarios['negative']]
            scenarios['error'] = [self.hyperlink_figma_references(s, design_links) for s in scenarios['error']]
        
        return scenarios

    def generate_recommendations(self, parsed_data: Dict[str, Any], conflicts: List[str]) -> Dict[str, List[str]]:
        """Generate detailed, role-tagged, actionable recommendations with metrics"""
        recommendations = {
            'po': [],
            'qa': [],
            'dev': []
        }
        
        domain_terms = self.extract_domain_terms(parsed_data)
        conflicts_present = len(conflicts) > 0
        title_desc = f"{parsed_data['title']} {parsed_data['description']}".lower()
        design_links = parsed_data.get('design_links', [])
        
        # === PO RECOMMENDATIONS (Business & Metrics) ===
        if conflicts_present:
            recommendations['po'].append("🚨 Resolve conflicting acceptance criteria before sprint planning to avoid rework and delays")
        
        # KPI and success metrics
        if 'filter' in domain_terms or 'plp' in title_desc:
            recommendations['po'].append("Define measurable KPIs: filter engagement rate (target ≥40%), time-to-first-filter (target ≤3s), conversion uplift (track +5% goal)")
            recommendations['po'].append("Ensure alignment with business objectives: validate filter order matches merchandising strategy and seasonal priorities")
            recommendations['po'].append("Plan A/B testing: control vs. new horizontal filters with 50/50 traffic split, measure for 2 weeks minimum")
        elif 'checkout' in title_desc or 'payment' in title_desc:
            recommendations['po'].append("Define measurable KPIs: checkout completion rate (target +3%), payment failure rate (target ≤0.5%), average checkout time (target ≤90s)")
            recommendations['po'].append("Ensure alignment with business objectives: validate payment flow matches compliance requirements and fraud prevention policies")
        else:
            recommendations['po'].append("Define measurable success metrics: user task completion rate, error rate reduction target, user satisfaction score (NPS/CSAT)")
            recommendations['po'].append("Ensure alignment with business objectives and quarterly OKRs before development begins")
        
        # Domain-specific PO guidance
        if 'PayPal' in domain_terms:
            recommendations['po'].append("Approve immediate-open behavior and ABTasty disablement as explicit acceptance conditions with legal/compliance sign-off")
        if 'ABTasty' in domain_terms:
            recommendations['po'].append("Define ABTasty toggle guidance: document kill-switch criteria and rollback plan for validation phase")
        
        # === QA RECOMMENDATIONS (Testing & Quality) ===
        recommendations['qa'].append("Expand test coverage to include:")
        
        # Accessibility testing
        if design_links or 'ui' in title_desc or 'interface' in title_desc:
            recommendations['qa'].append("  • Accessibility: keyboard navigation (Tab, Shift+Tab, Enter, Escape), screen reader validation (NVDA/JAWS), color contrast verification (WCAG 2.1 AA)")
            recommendations['qa'].append("  • UI responsiveness: test on mobile (320px), tablet (768px), desktop (1920px) viewports with Chrome DevTools")
            if design_links:
                recommendations['qa'].append(f"  • Visual validation: pixel-perfect comparison against Figma prototype using Percy or Chromatic, validate animations match design specs")
        else:
            recommendations['qa'].append("  • Accessibility: keyboard-only navigation, screen reader announcements, focus management")
        
        # Functional testing
        if 'filter' in domain_terms:
            recommendations['qa'].append("  • Functional: verify all 5 quick filters load correctly, 'More Filters' opens full panel, applied filters display with remove (×) button")
            recommendations['qa'].append("  • Performance: measure filter response time (target ≤500ms), validate sticky behavior on scroll, test horizontal overflow with 10+ filters")
        elif 'popup' in title_desc or 'modal' in title_desc:
            recommendations['qa'].append("  • Functional: popup-blocked fallback behavior, keyboard-only activation (Enter key), focus trap inside modal, Escape key closes")
            recommendations['qa'].append("  • Edge cases: test with popup blockers enabled, validate behavior on slow connections (throttle to 3G)")
        else:
            recommendations['qa'].append("  • Functional: happy path validation, error state handling, edge cases (empty states, max limits)")
        
        # Analytics and monitoring
        if 'analytics' in title_desc or 'tracking' in title_desc:
            recommendations['qa'].append("  • Analytics: capture event payloads as test evidence, validate tracking fires on all interactions, verify data layer accuracy")
        else:
            recommendations['qa'].append("  • Analytics: validate key user interactions fire correct tracking events (clicks, form submissions)")
        
        # Browser and device testing
        recommendations['qa'].append("  • Cross-browser: test on Chrome, Firefox, Safari (latest 2 versions), document any browser-specific issues")
        
        # === DEV / TECH LEAD RECOMMENDATIONS (Technical Implementation) ===
        
        # Performance and optimization
        if 'filter' in domain_terms or 'plp' in title_desc:
            recommendations['dev'].append("Implement smooth horizontal scroll with full keyboard navigation support (Arrow Left/Right, Tab, Home/End keys)")
            recommendations['dev'].append("Optimize performance: use CSS `position: sticky` for filter bar, debounce filter API calls (300ms), implement virtual scrolling for 100+ filters")
        elif 'popup' in title_desc or 'modal' in title_desc:
            recommendations['dev'].append("Implement focus trap: use `focus-trap` library, restore focus to trigger element on close, handle Escape key properly")
        
        # Telemetry and monitoring
        recommendations['dev'].append("Add structured telemetry for user interactions:")
        if 'filter' in domain_terms:
            recommendations['dev'].append("  • Track: filter_opened, filter_closed, quick_filter_clicked, more_filters_opened, filter_applied, filter_removed, clear_all_clicked")
            recommendations['dev'].append("  • Include metadata: filter_type, filter_value, applied_filters_count, time_to_interaction")
        else:
            recommendations['dev'].append("  • Track: feature_used, action_completed, error_occurred with relevant context (user_id, session_id, timestamp)")
        
        # Error handling and resilience
        if 'api' in title_desc or 'data' in title_desc:
            recommendations['dev'].append("Document error handling patterns: API timeout (5s) with retry (3 attempts), network failure fallback (cached data), validation error display (inline with field)")
        else:
            recommendations['dev'].append("Document error handling patterns and edge-case recovery within Confluence or codebase README (include retry logic, fallback states)")
        
        # Code quality and documentation
        recommendations['dev'].append("Code quality: add unit tests (target 80% coverage), write integration tests for critical paths, document component props/API contracts")
        if 'PayPal' in domain_terms:
            recommendations['dev'].append("PayPal integration: bind popup to user gesture only, add debounce/guard (500ms), implement ABTasty kill-switch for validation")
        
        return recommendations

    def generate_technical_details(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed technical, ADA, and architecture information based on ticket context"""
        title = (parsed_data.get('title', '') or '').lower()
        description_raw = self._extract_text_from_field(parsed_data.get('description', ''))
        description = (description_raw or '').lower()
        domain_terms = self.extract_domain_terms(parsed_data)
        design_links = parsed_data.get('design_links', [])
        
        # Implementation Details
        impl_details = []
        if 'filter' in title or 'plp' in title:
            impl_details = [
                "Update PLP layout component to remove left filter panel",
                "Integrate new horizontal filter bar component above product grid",
                "Use existing filter API endpoints for data; no new API required",
                "Add configuration support for top 5 quick filters (Category, Size, Color, Fit, Price)",
                "Implement sticky behavior using CSS position: sticky and intersection observer for performance",
                "Apply Figma design tokens for consistent UI"
            ]
        elif 'form' in title or 'input' in title:
            impl_details = [
                "Update form component with new validation logic",
                "Integrate with existing validation library/framework",
                "Add error state handling and user feedback mechanisms",
                "Implement field-level and form-level validation",
                "Apply design system patterns for consistency"
            ]
        else:
            impl_details = [
                "Update existing components per design specifications",
                "Integrate with current API endpoints (no new backend required)",
                "Add necessary state management for new functionality",
                "Apply design system tokens for consistent UI/UX",
                "Ensure backward compatibility with existing functionality"
            ]
        
        # Architectural Solution
        arch_solution = []
        if 'filter' in title or 'plp' in title:
            arch_solution = [
                "No backend schema changes required",
                "Reuses existing product listing API (no new endpoints)",
                "Filter logic handled client-side with existing Redux/Context state management",
                "Components designed to be reusable across other PLP variants (e.g., mobile, brand pages)",
                "Ensure horizontal filters integrate with existing analytics event tracking module"
            ]
        else:
            arch_solution = [
                "No backend schema changes required",
                "Reuses existing APIs and data models",
                "Client-side logic with existing state management (Redux/Context)",
                "Components designed to be reusable across variants",
                "Integrates with existing analytics and monitoring modules"
            ]
        
        # ADA (Accessibility)
        ada_list = [
            "Keyboard navigation: Tab, Enter, and Escape keys should fully control filter flyout" if 'filter' in title else "Keyboard navigation: Tab, Enter, Escape keys fully control all interactions",
            "Screen reader labels for filter names, close buttons, and applied filters" if 'filter' in title else "Screen reader labels for all interactive elements and state changes",
            "Color contrast ratios to meet WCAG 2.1 Level AA standards",
            "Focus state visible for all interactive elements",
            "Announce applied filter changes to screen readers (ARIA live region)" if 'filter' in title else "ARIA live regions announce dynamic content changes to assistive technologies"
        ]
        
        # NFRs
        nfr_list = []
        if 'filter' in title or 'plp' in title:
            nfr_list = [
                "**Performance:** Page should re-render filtered products within ≤500ms after filter selection",
                "**Security:** All API calls use HTTPS; ensure no PII exposure in filter analytics events",
                "**Reliability:** Filters must maintain state on page reload or back-navigation",
                "**Analytics:** Filter interactions should fire correct tracking events (category, filter type)",
                "**Accessibility:** Meets WCAG 2.1 Level AA"
            ]
        else:
            nfr_list = [
                "**Performance:** Page interactions respond within ≤500ms; initial load ≤2s",
                "**Security:** All API calls use HTTPS; no PII exposure in logs/analytics",
                "**Reliability:** State persists on page reload or back-navigation",
                "**Analytics:** All user interactions fire correct tracking events",
                "**Accessibility:** Full WCAG 2.1 Level AA compliance"
            ]
        
        # Hyperlink Figma references in technical details
        if design_links:
            impl_details = [self.hyperlink_figma_references(detail, design_links) for detail in impl_details]
            arch_solution = [self.hyperlink_figma_references(sol, design_links) for sol in arch_solution]
        
        return {
            'implementation_details_list': impl_details,
            'architectural_solution_list': arch_solution,
            'ada_list': ada_list,
            'nfr_list': nfr_list
        }

    def _generate_ai_ac_rewrite(self, original_ac: str, description: str, title: str, domain_terms: List[str], design_links: List[DesignLink]) -> str:
        """Generate comprehensive AI-powered rewrite of acceptance criteria using description context"""
        if not self.client:
            return ""
        
        try:
            # Build comprehensive context from description
            description_context = description[:2000] if description else ""  # Limit description length
            domain_context = ", ".join(domain_terms[:5]) if domain_terms else ""
            figma_context = f"Design reference: {design_links[0].url}" if design_links else ""
            
            prompt = f"""You are an expert product manager and QA engineer. Rewrite the following acceptance criterion to be comprehensive, testable, and detailed. Use the ticket description and context to make it specific and actionable.

**Original Acceptance Criterion:**
{original_ac}

**Ticket Title:** {title}

**Ticket Description Context:**
{description_context}

**Domain Terms:** {domain_context}

**Design Reference:** {figma_context}

**Requirements for the rewrite:**
1. Make it specific and testable (include measurable metrics like timing, counts, specific behaviors)
2. Include UX details (visual feedback, loading states, error messages, keyboard navigation)
3. Add performance requirements (response times, load times)
4. Include accessibility requirements (keyboard navigation, screen readers, WCAG compliance)
5. Add error handling and edge cases
6. Make it comprehensive but concise (aim for 200-400 words)
7. Use the description context to add relevant details
8. Format as a single paragraph with clear, actionable statements

**Rewritten Acceptance Criterion:**"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            rewrite = response.choices[0].message.content.strip()
            return rewrite if rewrite and len(rewrite) > 50 else ""
            
        except Exception as e:
            print(f"⚠️ AI rewrite error: {str(e)}")
            return ""

    def generate_professional_ac_suggestions(self, original_acs: List[str], parsed_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate detailed, professional rewrite suggestions for each acceptance criterion using description context"""
        suggestions = []
        title = (parsed_data.get('title', '') or '').lower()
        description = self._extract_text_from_field(parsed_data.get('description', ''))
        description_lower = (description or '').lower()
        domain_terms = self.extract_domain_terms(parsed_data)
        design_links = parsed_data.get('design_links', [])
        
        for i, original_ac in enumerate(original_acs):
            if not original_ac or len(original_ac.strip()) < 5:
                continue
            
            original_ac = original_ac or ''
            ac_lower = original_ac.lower()
            
            # Use OpenAI to generate comprehensive rewrite based on AC + description context
            rewrite = ""
            why_better = ""
            
            # Try to generate AI-powered rewrite if client is available
            if self.client:
                try:
                    ai_rewrite = self._generate_ai_ac_rewrite(original_ac, description, title, domain_terms, design_links)
                    if ai_rewrite and len(ai_rewrite.strip()) > 50:
                        rewrite = ai_rewrite
                        why_better = "AI-generated comprehensive rewrite incorporating description context, specific requirements, performance metrics, UX details, accessibility, and error handling"
                except Exception as e:
                    print(f"⚠️ AI rewrite failed for AC #{i+1}: {str(e)}")
                    # Fall back to rule-based rewrite
            
            # If AI rewrite failed or not available, use rule-based approach
            if not rewrite or len(rewrite.strip()) < 50:
                # Context-aware rewrites based on common patterns
                if 'filter' in ac_lower or 'filter' in title:
                    if 'display' in ac_lower or 'show' in ac_lower:
                        rewrite = f"On the Product Listing Page, selecting filter options (Brand, Size, Color, Price) must update the product grid to display only matching items within 1 second. Applied filters should appear as removable tokens above the grid with '×' close buttons for easy removal. The product count must update dynamically with messaging like 'Showing 24 of 156 results' to provide context. Filter state needs to be preserved in the URL for shareability and browser back/forward navigation support. If no products match the selected filters, display a helpful message: 'No products match your filters. Try adjusting your selections.' Loading indicators should be shown during grid updates to indicate processing. On mobile devices (<768px), filters must be accessible via a slide-out panel or modal for better screen space utilization. All filter interactions need to support keyboard navigation with visible focus indicators. Screen readers should announce filter changes and updated product counts for accessibility compliance."
                        why_better = "Covers core filter functionality with performance, UX, persistence, accessibility, and responsive design"
                    elif 'sticky' in ac_lower or 'fixed' in ac_lower:
                        rewrite = f"When viewing the PLP and scrolling down beyond 200px, the filter bar must remain fixed at the top of the viewport while maintaining full filter functionality. On mobile devices (<768px width), the sticky filter bar should collapse to a compact view to optimize screen space. The sticky behavior needs to support keyboard navigation for accessibility, ensuring users can navigate filters using Tab/Shift+Tab keys."
                        why_better = "Defines scroll trigger point (200px), specifies sticky behavior, addresses responsive design, includes accessibility"
                    elif 'select' in ac_lower or 'click' in ac_lower or 'apply' in ac_lower:
                        rewrite = f"On the PLP with available filter options, selecting one or more filter values (e.g., Brand: Nike, Size: Large) must apply filters immediately without requiring a separate 'Apply' button. The product grid should update within 1 second to show matching products for responsive user experience. Filter selections need to be highlighted with active state styling to provide clear visual feedback. The URL must update to reflect current filter state, enabling shareability and proper browser back/forward navigation."
                        why_better = "Defines immediate application (no Apply button needed), specifies performance, includes visual feedback and URL state management"
                    else:
                        rewrite = f"On the Product Listing Page with the new horizontal filter layout, the top 5 most relevant filters (Brand, Size, Color, Price, Category) must be displayed prominently for easy access. Additional filters should be accessible via a 'More Filters' expandable section to reduce visual clutter. All filter interactions need to trigger product grid updates within 1 second to maintain responsiveness. Filter selections must persist across page refreshes and browser back/forward navigation to preserve user context."
                        why_better = "Specifies filter hierarchy (top 5 + More Filters), defines performance requirements, addresses navigation persistence"
                
                elif 'checkout' in ac_lower or 'payment' in ac_lower or 'checkout' in title:
                    if 'validate' in ac_lower or 'error' in ac_lower:
                        rewrite = f"On the checkout payment step, all required fields must be validated in real-time (<200ms per field) as users enter payment information. Specific, actionable error messages should be displayed directly next to invalid fields for immediate feedback. The submit button needs to remain disabled until all validations pass to prevent invalid submissions. Error messages must support screen readers with appropriate ARIA labels to ensure accessibility compliance."
                        why_better = "Defines real-time validation timing, specifies error message placement and clarity, includes accessibility requirements"
                    elif 'submit' in ac_lower or 'complete' in ac_lower:
                        rewrite = f"After completing all required checkout fields, clicking the 'Complete Purchase' button must display a loading indicator immediately to acknowledge the action. The payment should be processed within 3 seconds under normal network conditions to meet user expectations. Upon successful payment, a confirmation page needs to be displayed with order details. An order confirmation email must be sent within 5 minutes of successful payment. If payment fails, appropriate error handling should display specific failure reasons (declined card, timeout, insufficient funds) with a clear retry option for user recovery."
                        why_better = "Defines loading feedback, specifies performance expectations (3s processing), addresses success and failure paths with clear actions"
                    else:
                        rewrite = f"On the checkout page payment selection step, all supported payment methods (Credit Card, PayPal, Apple Pay) must be displayed with clear, recognizable icons. For logged-in users, the checkout form should be pre-populated with saved billing/shipping information to streamline the process. Guest checkout needs to be available with only minimal required fields to reduce friction. The total order amount must be displayed prominently with a complete itemized breakdown showing subtotal, taxes, shipping, and discounts for transparency. All payment data transmission requires secure HTTPS with full PCI compliance standards. The interface must be fully responsive across desktop, tablet, and mobile devices with WCAG 2.1 Level AA accessibility compliance. Form validation should provide real-time feedback with specific, actionable error messages rather than generic warnings. Loading states need to be shown during payment processing (typically 2-5 seconds) to indicate progress. Error handling must display clear, actionable messages for all payment failure scenarios including declined cards, timeouts, and insufficient funds. Successful payments should redirect immediately to a confirmation page displaying the order number and estimated delivery date."
                        why_better = "Covers payment methods, security, UX, accessibility, validation, error handling, and confirmation flow"
                
                elif 'form' in ac_lower or 'input' in ac_lower:
                    if 'validate' in ac_lower or 'validation' in ac_lower:
                        rewrite = f"When filling out forms with required fields, inline validation must occur within 200ms on each field blur to provide immediate feedback. Error messages need to be specific and actionable, such as 'Email must include @' rather than generic 'Invalid email' messages. Valid fields should display a checkmark icon to provide positive confirmation and build user confidence. Field validation errors must be announced to screen readers using appropriate ARIA live regions for accessibility compliance."
                        why_better = "Specifies validation timing and trigger (on blur), defines error message quality, includes positive feedback, addresses accessibility"
                    elif 'submit' in ac_lower:
                        rewrite = f"After completing all form fields and clicking submit, client-side validation must run on all fields before form submission to catch errors early. The submit button should show a loading state and become disabled during processing to prevent duplicate submissions. The form needs to submit within 2 seconds under normal network conditions to meet performance expectations. A clear success or error message must be displayed after submission with specific next steps. The form should not lose user data if validation fails, preserving entered information for correction."
                        why_better = "Defines validation sequence, includes loading state UX, specifies performance, addresses data persistence on errors"
                    else:
                        rewrite = f"When users interact with form fields, real-time character count must be displayed for fields with length limits to guide input. Contextual help text should appear for complex fields, such as password strength requirements or format examples. Autocomplete suggestions need to be provided where applicable, particularly for standard fields like addresses and names. All form fields must support standard keyboard navigation including Tab, Shift+Tab for field traversal and Enter for submission."
                        why_better = "Adds helpful UX features (character count, help text, autocomplete), ensures keyboard accessibility"
                
                elif 'performance' in ac_lower or 'load' in ac_lower or 'speed' in ac_lower:
                    rewrite = f"Under normal network conditions (3G or better), the page must display initial content within 2 seconds (First Contentful Paint) to meet user expectations. The page needs to become fully interactive within 3.5 seconds (Time to Interactive) for responsive user experience. Images should be optimized and lazy-loaded for content below the fold to reduce initial load time. Smooth scrolling must be maintained at 60fps for fluid interactions. Core Web Vitals performance targets need to be met: Largest Contentful Paint under 2.5 seconds, First Input Delay under 100 milliseconds, and Cumulative Layout Shift under 0.1 to ensure optimal user experience."
                    why_better = "Defines specific performance metrics (FCP, TTI, Core Web Vitals) with optimization strategies"
                
                elif 'accessibility' in ac_lower or 'ada' in ac_lower or 'screen reader' in ac_lower:
                    rewrite = f"When users navigate the interface using assistive technology, all interactive elements must have appropriate ARIA labels and semantic roles for proper identification. Keyboard navigation needs to follow a logical tab order that matches visual flow. Focus indicators must be clearly visible with a minimum 3:1 contrast ratio against the background. All functionality should be operable via keyboard alone without requiring a mouse. Color cannot be the sole means of conveying information to support users with color vision deficiencies. The interface must meet WCAG 2.1 Level AA compliance standards for accessibility."
                    why_better = "Specifies WCAG compliance level, defines contrast requirements, ensures keyboard-only operation, addresses multiple accessibility concerns"
                
                elif 'responsive' in ac_lower or 'mobile' in ac_lower or 'device' in ac_lower:
                    rewrite = f"When users access the interface on various devices (desktop, tablet, mobile), the layout must adapt using responsive breakpoints at 320px, 768px, and 1024px widths. Touch targets need to be at least 44x44px on mobile devices for easy finger interaction. Text must remain readable without requiring horizontal scrolling on any screen size. Functionality should be consistent across all devices with no feature degradation on smaller screens. The interface needs to be tested and validated on iOS Safari, Android Chrome, and all major desktop browsers for compatibility."
                    why_better = "Defines breakpoints, touch target standards, and ensures cross-device consistency"
                
                elif 'display' in ac_lower or 'show' in ac_lower or 'visible' in ac_lower:
                    rewrite = f"The information must be presented with clear visual hierarchy to guide user attention. Loading states should be displayed for asynchronous data to indicate progress. Empty states must provide helpful guidance when no data exists, explaining why the state is empty. Error states need to be clearly distinguished with appropriate icons and colors to draw attention. All text must maintain sufficient contrast ratios: 4.5:1 for normal text, 3:1 for large text to ensure readability. The interface should respond within 500ms to user interactions to maintain perceived performance."
                    why_better = "Addresses UI states (loading, empty, error), visual hierarchy, and accessibility contrast"
                
                elif 'error' in ac_lower:
                    rewrite = f"When errors occur during user interaction or system processing, a user-friendly error message must be displayed immediately to acknowledge the issue. The message needs to explain what went wrong in plain language without technical jargon that users won't understand. Actionable next steps should be provided, such as a 'Try again' button or 'Contact support' link with contact information. Errors must be logged with sufficient detail for debugging including error codes, timestamps, and the user action that triggered the error. Critical errors need to be reported automatically to monitoring systems for immediate team awareness and response."
                    why_better = "Defines error message clarity and timing, provides user recovery path, includes logging and monitoring for developers"
                
                else:
                    # Generic professional rewrite - concise but comprehensive
                    rewrite = f"For the action '{original_ac.strip()}', the system must respond within 2 seconds with clear visual feedback such as loading indicators or confirmation messages. Upon successful completion, a specific confirmation needs to be displayed like 'Item added to cart' rather than generic 'Success' messages. If errors occur, user-friendly messages should be shown with actionable next steps including 'Try again' or 'Contact support' options. The functionality must work consistently across major browsers including Chrome, Firefox, Safari, and Edge (latest 2 versions). The interface needs to be fully responsive on desktop, tablet, and mobile devices with no degradation. All interactive elements should be keyboard accessible with clearly visible focus indicators for navigation. Screen readers must announce dynamic content updates appropriately to meet WCAG 2.1 Level AA accessibility standards. User data transmission requires secure HTTPS encryption throughout. The feature should handle edge cases gracefully including network timeouts, invalid input validation, and concurrent user actions."
                    why_better = "Converts vague requirement into testable format with performance, UX, error handling, cross-browser support, accessibility, and security"
            
            # Additional improvements based on common weak patterns
            if 'should' in ac_lower or 'must' in ac_lower:
                why_better += " | Removes vague modal verbs ('should', 'must') and replaces with specific, testable behaviors"
            if any(word in ac_lower for word in ['appropriate', 'reasonable', 'good', 'properly']):
                why_better += " | Eliminates subjective terms by defining specific, measurable criteria"
            if len(original_ac.split()) < 8:
                why_better += " | Expands brief requirement into detailed, comprehensive acceptance criterion with context and edge cases"
            
            suggestions.append({
                'original': original_ac.strip(),
                'rewrite': rewrite,
                'why_better': why_better.strip(' |')
            })
        
        return suggestions

    def _generate_ai_description_rewrite(self, original_description: str, title: str, ac_list: List[str], domain_terms: List[str], design_links: List[DesignLink]) -> str:
        """Generate comprehensive AI-powered rewrite of description using AC context"""
        if not self.client:
            return ""
        
        try:
            # Build comprehensive context from ACs
            ac_context = "\n".join(ac_list[:5]) if ac_list else ""  # Limit to first 5 ACs
            domain_context = ", ".join(domain_terms[:5]) if domain_terms else ""
            figma_context = f"Design reference: {design_links[0].url}" if design_links else ""
            
            prompt = f"""You are an expert product manager and technical writer. Rewrite the following ticket description to be comprehensive, clear, and detailed. Use the acceptance criteria and context to make it specific and actionable.

**Original Description:**
{original_description[:2000]}

**Ticket Title:** {title}

**Acceptance Criteria Context:**
{ac_context}

**Domain Terms:** {domain_context}

**Design Reference:** {figma_context}

**Requirements for the rewrite:**
1. Make it clear and comprehensive (include all key requirements and context)
2. Add specific details about functionality, user interactions, and expected behavior
3. Include technical context where relevant (APIs, components, integrations)
4. Add UX/UI details (visual feedback, loading states, error handling)
5. Include performance and accessibility considerations
6. Make it well-structured with clear sections if needed
7. Use the acceptance criteria context to add relevant details
8. Format as a comprehensive description (aim for 300-600 words)

**Rewritten Description:**"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1200
            )
            
            rewrite = response.choices[0].message.content.strip()
            return rewrite if rewrite and len(rewrite) > 100 else ""
            
        except Exception as e:
            print(f"⚠️ AI description rewrite error: {str(e)}")
            return ""

    def generate_description_improvements(self, parsed_data: Dict[str, Any], ac_list: List[str]) -> Dict[str, str]:
        """Generate improved description rewrite using AC context"""
        original_description = self._extract_text_from_field(parsed_data.get('description', ''))
        if not original_description or len(original_description.strip()) < 20:
            return {
                'original': original_description or 'No description available',
                'rewrite': 'Description is missing or too short. Please add a comprehensive description of the feature or requirement.',
                'why_better': 'No description available to improve'
            }
        
        title = parsed_data.get('title', '')
        domain_terms = self.extract_domain_terms(parsed_data)
        design_links = parsed_data.get('design_links', [])
        
        rewrite = ""
        why_better = ""
        
        # Try to generate AI-powered rewrite if client is available
        if self.client:
            try:
                ai_rewrite = self._generate_ai_description_rewrite(original_description, title, ac_list, domain_terms, design_links)
                if ai_rewrite and len(ai_rewrite.strip()) > 100:
                    rewrite = ai_rewrite
                    why_better = "AI-generated comprehensive rewrite incorporating acceptance criteria context, specific requirements, technical details, UX considerations, performance metrics, and accessibility requirements"
            except Exception as e:
                print(f"⚠️ AI description rewrite failed: {str(e)}")
        
        # If AI rewrite failed or not available, use rule-based approach
        if not rewrite or len(rewrite.strip()) < 100:
            # Extract key information from original description
            desc_lower = original_description.lower()
            title_lower = title.lower()
            
            # Build improved description based on context
            improved_parts = []
            
            # Add context about what the feature does
            if any(word in desc_lower for word in ['filter', 'search', 'sort']):
                improved_parts.append("This feature enables users to filter, search, and sort content dynamically with real-time updates. The interface provides immediate visual feedback when filters are applied, showing updated results within 1 second. Filter state is preserved in the URL for shareability and browser navigation support.")
            
            if any(word in desc_lower for word in ['form', 'input', 'submit']):
                improved_parts.append("This feature includes form interactions with real-time validation, providing immediate feedback on field blur (<200ms response time). Error messages are specific and actionable, displayed directly next to invalid fields. Valid fields show positive confirmation indicators. All form fields support keyboard navigation (Tab, Shift+Tab, Enter) for accessibility compliance.")
            
            if any(word in desc_lower for word in ['checkout', 'payment', 'cart']):
                improved_parts.append("This feature handles checkout and payment processing with secure HTTPS transmission and PCI compliance. The interface supports multiple payment methods (Credit Card, PayPal, Apple Pay) with clear, recognizable icons. Form validation occurs in real-time with specific error messages. Payment processing includes loading indicators and clear success/error feedback.")
            
            if any(word in desc_lower for word in ['display', 'show', 'render']):
                improved_parts.append("This feature displays content with clear visual hierarchy and responsive design. Loading states are shown for asynchronous data. Empty states provide helpful guidance. Error states are clearly distinguished with appropriate icons and colors. The interface maintains 60fps smooth scrolling and responds to user interactions within 500ms.")
            
            # Add performance considerations
            if not any(word in desc_lower for word in ['performance', 'speed', 'load']):
                improved_parts.append("Performance: Page interactions respond within ≤500ms; initial load ≤2s. Images are optimized and lazy-loaded for content below the fold.")
            
            # Add accessibility considerations
            if not any(word in desc_lower for word in ['accessibility', 'ada', 'wcag', 'keyboard']):
                improved_parts.append("Accessibility: Full keyboard navigation support (Tab, Shift+Tab, Enter, Escape). Screen reader labels for all interactive elements. WCAG 2.1 Level AA compliance with proper contrast ratios and focus indicators.")
            
            # Combine improved parts
            if improved_parts:
                rewrite = " ".join(improved_parts)
                why_better = "Enhanced description with specific functionality details, performance requirements, UX considerations, and accessibility compliance"
            else:
                # Generic improvement
                rewrite = f"{original_description}\n\n**Additional Context:** This feature requires responsive design across desktop, tablet, and mobile devices. All interactions must support keyboard navigation and screen readers for accessibility compliance. Performance targets: page interactions ≤500ms, initial load ≤2s."
                why_better = "Added performance, accessibility, and responsive design requirements"
        
        return {
            'original': original_description[:500] + ('...' if len(original_description) > 500 else ''),
            'rewrite': rewrite,
            'why_better': why_better
        }

    def analyze_ac_quality(self, ac_list: List[str]) -> Dict[str, int]:
        """Analyze acceptance criteria for testability, measurability, and clarity"""
        testable_count = 0
        measurable_count = 0
        clear_count = 0
        weak_count = 0
        
        testable_keywords = ['verify', 'confirm', 'check', 'validate', 'ensure', 'displays', 'shows', 'opens', 'closes', 'updates']
        measurable_keywords = ['within', 'ms', 'seconds', 'count', 'number', 'percentage', '≤', '>=', '<', '>']
        vague_phrases = ['should', 'may', 'might', 'appropriate', 'reasonable', 'good', 'better', 'properly', 'correctly']
        
        for ac in ac_list:
            ac_lower = ac.lower()
            is_weak = False
            
            # Testable: Has action verbs
            if any(keyword in ac_lower for keyword in testable_keywords):
                testable_count += 1
            else:
                is_weak = True
            
            # Measurable: Has specific metrics
            if any(keyword in ac_lower for keyword in measurable_keywords):
                measurable_count += 1
            else:
                is_weak = True
            
            # Clear: Not vague, has specific details
            if not any(phrase in ac_lower for phrase in vague_phrases) and len(ac) > 20:
                clear_count += 1
            else:
                is_weak = True
            
            # Count as weak if it fails any criteria
            if is_weak or any(phrase in ac_lower for phrase in vague_phrases):
                weak_count += 1
        
        return {
            'testable_count': testable_count,
            'measurable_count': measurable_count,
            'clear_count': clear_count,
            'weak_count': weak_count
        }
    
    def generate_gwt_format(self, parsed_data: Dict[str, Any], ac_list: List[str]) -> List[Dict[str, str]]:
        """Convert acceptance criteria to Given-When-Then format"""
        gwt_suggestions = []
        domain_terms = self.extract_domain_terms(parsed_data)
        
        for i, ac in enumerate(ac_list[:5]):  # Limit to first 5
            # Extract context from AC
            ac_lower = ac.lower()
            
            # Determine Given (initial state)
            if 'user' in ac_lower:
                given = f"user is on {domain_terms[0] if domain_terms else 'the page'}"
            elif 'filter' in ac_lower or 'plp' in ac_lower:
                given = "user is viewing the product listing page"
            elif 'form' in ac_lower or 'input' in ac_lower:
                given = "user has opened the form"
            else:
                given = f"system is in ready state for {parsed_data['title'][:40]}"
            
            # Determine When (action)
            action_verbs = ['clicks', 'selects', 'enters', 'opens', 'closes', 'applies', 'removes']
            when_action = next((verb for verb in action_verbs if verb in ac_lower), 'interacts with')
            
            if 'filter' in ac_lower:
                when = f"user {when_action} a filter option"
            elif 'button' in ac_lower:
                when = f"user {when_action} the button"
            else:
                when = f"user performs the action: {ac[:50]}"
            
            # Determine Then (outcome)
            if 'display' in ac_lower or 'show' in ac_lower:
                then = f"system displays the expected result within ≤500ms"
            elif 'update' in ac_lower or 'refresh' in ac_lower:
                then = "system updates the content and shows feedback"
            elif 'error' in ac_lower:
                then = "system shows appropriate error message with recovery option"
            else:
                then = f"system confirms: {ac[:60]}"
            
            gwt_suggestions.append({
                'given': given,
                'when': when,
                'then': then
            })
        
        return gwt_suggestions
    
    def identify_missing_nfrs(self, parsed_data: Dict[str, Any], ac_list: List[str]) -> List[Dict[str, str]]:
        """Identify missing non-functional requirements"""
        missing_nfrs = []
        all_ac_text = ' '.join(ac_list).lower()
        
        # Check for Performance NFR
        if not any(word in all_ac_text for word in ['performance', 'speed', 'load time', 'response time', 'ms', 'seconds']):
            missing_nfrs.append({
                'type': 'Performance',
                'suggestion': 'Page load time ≤2s, Filter updates ≤500ms, API responses ≤1s'
            })
        
        # Check for Security NFR
        if not any(word in all_ac_text for word in ['security', 'authentication', 'authorization', 'encrypt', 'secure']):
            missing_nfrs.append({
                'type': 'Security',
                'suggestion': 'All API calls use HTTPS, User data is encrypted, CSRF tokens required'
            })
        
        # Check for Accessibility NFR
        if not any(word in all_ac_text for word in ['accessibility', 'ada', 'wcag', 'keyboard', 'screen reader', 'aria']):
            missing_nfrs.append({
                'type': 'Accessibility',
                'suggestion': 'WCAG 2.1 Level AA compliance, Keyboard navigation support, Screen reader compatibility'
            })
        
        # Check for Browser Compatibility
        if not any(word in all_ac_text for word in ['browser', 'chrome', 'firefox', 'safari', 'edge', 'compatibility']):
            missing_nfrs.append({
                'type': 'Browser Compatibility',
                'suggestion': 'Support latest 2 versions of Chrome, Firefox, Safari, Edge'
            })
        
        # Check for Error Handling
        if not any(word in all_ac_text for word in ['error', 'failure', 'timeout', 'retry', 'fallback']):
            missing_nfrs.append({
                'type': 'Error Handling',
                'suggestion': 'Graceful error handling, User-friendly error messages, Retry mechanism for failed requests'
            })
        
        return missing_nfrs

    def _convert_rewrite_to_bullets(self, rewrite_text: str) -> str:
        """Convert long rewrite text into concise bullet points"""
        if not rewrite_text or len(rewrite_text.strip()) < 20:
            return rewrite_text
        
        # Split by sentences and key phrases to create bullet points
        sentences = re.split(r'[.!?]\s+', rewrite_text)
        bullets = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 15:
                continue
            
            # Remove leading "On the", "When", "After", etc. for cleaner bullets
            sentence = re.sub(r'^(On the|When|After|If|The|All|For|Upon|In|At|By|With|As)\s+', '', sentence, flags=re.IGNORECASE)
            
            # Capitalize first letter
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            
            # Limit bullet length (max 120 chars, but keep important info)
            if len(sentence) > 120:
                # Try to break at natural points
                if ';' in sentence:
                    parts = sentence.split(';')
                    for part in parts:
                        part = part.strip()
                        if part and len(part) > 15:
                            bullets.append(f"- {part}")
                    continue
                elif ',' in sentence[:120]:
                    # Split at last comma before 120 chars
                    last_comma = sentence[:120].rfind(',')
                    if last_comma > 50:
                        bullets.append(f"- {sentence[:last_comma]}")
                        remaining = sentence[last_comma+1:].strip()
                        if remaining and len(remaining) > 15:
                            bullets.append(f"- {remaining}")
                        continue
            
            bullets.append(f"- {sentence}")
        
        # If we couldn't create good bullets, return original with some formatting
        if len(bullets) == 0 or len(bullets) > 15:
            # Too many or too few bullets - create key points instead
            key_phrases = []
            # Extract key requirements
            if 'must' in rewrite_text.lower() or 'should' in rewrite_text.lower():
                # Extract requirements
                requirements = re.findall(r'(?:must|should|needs to|requires?)\s+([^.,;]+)', rewrite_text, re.IGNORECASE)
                for req in requirements[:8]:  # Limit to 8 key points
                    req = req.strip()
                    if req and len(req) > 10 and len(req) < 100:
                        key_phrases.append(f"- {req}")
            
            if key_phrases:
                return '\n'.join(key_phrases)
            else:
                # Fallback: split by periods and take first 5-6 meaningful sentences
                sentences = [s.strip() for s in rewrite_text.split('.') if s.strip() and len(s.strip()) > 20]
                return '\n'.join([f"- {s[:100]}" for s in sentences[:6]])
        
        return '\n'.join(bullets[:10])  # Limit to 10 bullets max

    def _format_description_improvements(self, description_improvements: Dict[str, str], newline: str) -> str:
        """Format description improvements as bullet points"""
        if not description_improvements or not description_improvements.get('rewrite'):
            return "_No description improvements available_"
        
        rewrite = description_improvements.get('rewrite', '')
        bullets = self._convert_rewrite_to_bullets(rewrite)
        
        return f"**Improved Description:**{newline}{bullets}{newline}{newline}**Why Better:** {description_improvements.get('why_better', 'Enhanced with comprehensive details')}"

    def _format_ac_improvements_with_description(self, description_improvements: Dict[str, str], ac_suggestions: List[Dict[str, str]], newline: str) -> str:
        """Format description and AC improvements together - description first, then ACs"""
        formatted_parts = []
        
        # Add description improvements first
        if description_improvements and description_improvements.get('rewrite'):
            rewrite = description_improvements.get('rewrite', '')
            bullets = self._convert_rewrite_to_bullets(rewrite)
            formatted_parts.append(f"**📝 Description Improvement:**{newline}{bullets}")
        
        # Add AC improvements
        if ac_suggestions:
            for i, sugg in enumerate(ac_suggestions):
                rewrite = sugg.get('rewrite', 'No suggestion available')
                bullets = self._convert_rewrite_to_bullets(rewrite)
                formatted_parts.append(f"**AC #{i+1}:**{newline}{bullets}")
        
        if not formatted_parts:
            return "_No suggestions available_"
        
        return newline.join(formatted_parts)

    def _format_ac_improvements(self, ac_suggestions: List[Dict[str, str]], newline: str) -> str:
        """Format AC improvements as bullet points"""
        if not ac_suggestions:
            return "_No suggestions available_"
        
        formatted = []
        for i, sugg in enumerate(ac_suggestions):
            rewrite = sugg.get('rewrite', 'No suggestion available')
            bullets = self._convert_rewrite_to_bullets(rewrite)
            formatted.append(f"**AC #{i+1}:**{newline}{bullets}")
        
        return newline.join(formatted)

    def hyperlink_figma_references(self, text: str, design_links: List[DesignLink]) -> str:
        """Replace Figma text references with clickable markdown links (avoid double-linking)"""
        if not design_links or not text:
            return text
        
        # Don't hyperlink if text already contains markdown links
        text = text or ''
        if '[' in text and '](' in text and 'figma.com' in text.lower():
            return text  # Already has Figma links
        
        # Get the first Figma link (primary design reference)
        figma_url = design_links[0].url
        
        # Replace common Figma references with hyperlinks
        # Use negative lookbehind/ahead to avoid matching inside existing markdown links
        patterns = [
            (r'(?<!\[)\bFigma prototype\b(?!\])', f'[Figma prototype]({figma_url})'),
            (r'(?<!\[)\bFigma\b(?! prototype)(?!\])', f'[Figma]({figma_url})'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def generate_markdown_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate markdown report without framework scores"""
        mode = analysis_results.get('mode', 'Actionable')
        status = analysis_results.get('status', 'Not Ready')
        readiness_percentage = analysis_results.get('readiness_percentage', 0)
        dor = analysis_results.get('dor', {})
        
        # Hyperlink Figma references in acceptance criteria
        ac_rewrites = analysis_results.get('ac_rewrites', [])
        if parsed_data.get('design_links'):
            ac_rewrites = [self.hyperlink_figma_references(ac, parsed_data['design_links']) for ac in ac_rewrites]
            analysis_results['ac_rewrites'] = ac_rewrites
        
        # Check if Figma is mentioned anywhere in ticket
        title_text = parsed_data.get('title', '')
        desc_text = self._extract_text_from_field(parsed_data.get('description', ''))
        ac_text = parsed_data.get('fields', {}).get('acceptance_criteria', '')
        test_text = parsed_data.get('fields', {}).get('testing_steps', '')
        impl_text = parsed_data.get('fields', {}).get('implementation_details', '')
        all_content = f"{title_text} {desc_text} {ac_text} {test_text} {impl_text}"
        figma_mentioned = 'figma' in all_content.lower()
        
        # Calculate weak areas based on missing/incomplete fields
        weak_areas = []
        if 'user_story' in dor.get('missing', []):
            weak_areas.append('User story format')
        if 'acceptance_criteria' in dor.get('missing', []):
            weak_areas.append('Acceptance criteria completeness')
        if 'implementation_details' in dor.get('missing', []) or 'architectural_solution' in dor.get('missing', []):
            weak_areas.append('Technical details')
        if 'testing_steps' in dor.get('missing', []):
            weak_areas.append('Test coverage')
        if 'ada_criteria' in dor.get('missing', []):
            weak_areas.append('Accessibility requirements')
        if 'story_points' in dor.get('missing', []):
            weak_areas.append('Effort estimation')
        if not weak_areas:
            weak_areas.append('Minor refinements needed')
        
        # Generate mode-specific reports
        if mode == "Summary":
            return self._generate_summary_report(parsed_data, analysis_results, status, readiness_percentage, dor, weak_areas, figma_mentioned)
        elif mode == "Insight":
            return self._generate_insight_report(parsed_data, analysis_results, status, readiness_percentage, dor, weak_areas, figma_mentioned)
        else:  # Actionable (default)
            return self._generate_actionable_report(parsed_data, analysis_results, status, readiness_percentage, dor, weak_areas, figma_mentioned)
    
    def _generate_actionable_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                                     status: str, readiness_percentage: int, dor: Dict[str, List[str]], 
                                     weak_areas: List[str], figma_mentioned: bool) -> str:
        """Generate detailed Actionable report with all sections"""
        mode = "Actionable"
        newline = '\n'  # Can't use chr(10) or \n in f-string expressions
        
        # Debug: Check status in parsed_data
        # PRIORITY 1: Check parsed_data['status'] FIRST (most reliable)
        jira_status = parsed_data.get('status', 'Unknown')
        print(f"\n🔍🔍🔍 DEBUG _generate_actionable_report - STATUS EXTRACTION:")
        print(f"   parsed_data.get('status'): '{jira_status}'")
        print(f"   parsed_data type: {type(parsed_data)}")
        print(f"   parsed_data keys: {list(parsed_data.keys())}")
        print(f"   'status' in parsed_data: {'status' in parsed_data}")
        print(f"   'fields' in parsed_data: {'fields' in parsed_data}")
        
        if 'fields' in parsed_data:
            print(f"   parsed_data['fields'] type: {type(parsed_data['fields'])}")
            print(f"   parsed_data['fields'] keys: {list(parsed_data['fields'].keys())[:20]}")
            print(f"   'status' in parsed_data['fields']: {'status' in parsed_data['fields']}")
            if 'status' in parsed_data['fields']:
                print(f"   parsed_data['fields']['status']: {parsed_data['fields']['status']}")
                print(f"   parsed_data['fields']['status'] type: {type(parsed_data['fields']['status'])}")
        
        # PRIORITY 2: If status is Unknown, try parsed_data['fields']['status']
        if not jira_status or jira_status == 'Unknown' or jira_status is None:
            print(f"   ⚠️ Status is '{jira_status}', trying parsed_data['fields']['status']...")
            if 'fields' in parsed_data and 'status' in parsed_data['fields']:
                fields_status = parsed_data['fields']['status']
                print(f"   fields_status: {fields_status}")
                print(f"   fields_status type: {type(fields_status)}")
                if isinstance(fields_status, dict):
                    print(f"   fields_status keys: {list(fields_status.keys()) if isinstance(fields_status, dict) else 'N/A'}")
                    if 'name' in fields_status:
                        jira_status = fields_status['name']
                        print(f"   ✅✅✅ Got status from parsed_data['fields']['status']['name']: '{jira_status}'")
                    else:
                        print(f"   ❌ 'name' not in fields_status dict")
                elif isinstance(fields_status, str):
                    jira_status = fields_status
                    print(f"   ✅✅✅ Got status from parsed_data['fields']['status'] (string): '{jira_status}'")
                else:
                    print(f"   ❌ fields_status is not dict or string: {type(fields_status)}")
            else:
                print(f"   ❌ 'fields' not in parsed_data OR 'status' not in parsed_data['fields']")
        
        # PRIORITY 3: Try status_category as last resort (if still Unknown)
        if (not jira_status or jira_status == 'Unknown') and parsed_data.get('status_category') and parsed_data.get('status_category') != 'Unknown':
            jira_status = parsed_data.get('status_category')
            print(f"   ✅ Got status from status_category: {jira_status}")
        
        # FINAL CHECK: If still Unknown, try ONE MORE TIME from parsed_data['fields']['status']
        if not jira_status or jira_status == 'Unknown':
            print(f"   ❌ CRITICAL: Status is still Unknown after all checks!")
            print(f"   Trying ONE MORE TIME from parsed_data['fields']['status']...")
            if 'fields' in parsed_data and 'status' in parsed_data['fields']:
                fields_status = parsed_data['fields']['status']
                if isinstance(fields_status, dict) and 'name' in fields_status:
                    jira_status = fields_status['name']
                    print(f"   ✅ FINAL FIX: Got status from parsed_data['fields']['status']['name']: {jira_status}")
                elif isinstance(fields_status, str):
                    jira_status = fields_status
                    print(f"   ✅ FINAL FIX: Got status from parsed_data['fields']['status'] (string): {jira_status}")
        
        # If STILL Unknown, set to Unknown (don't use "Not Available")
        if not jira_status or jira_status == 'Unknown':
            jira_status = 'Unknown'
            print(f"   ⚠️ Status will show as 'Unknown' (could not be extracted)")
        
        # Get brands and components for display
        print(f"\n🔍🔍🔍 DEBUG _generate_actionable_report - BRANDS EXTRACTION:")
        brands_display = 'Not specified'
        if 'fields' in parsed_data:
            print(f"   'fields' in parsed_data: True")
            print(f"   'brands' in parsed_data['fields']: {'brands' in parsed_data['fields']}")
            if 'brands' in parsed_data['fields']:
                brands_value = parsed_data['fields']['brands']
                print(f"   brands_value: {brands_value}")
                print(f"   brands_value type: {type(brands_value)}")
                if isinstance(brands_value, list) and brands_value:
                    print(f"   brands_value is list with {len(brands_value)} items")
                    if isinstance(brands_value[0], dict):
                        print(f"   First item is dict: {brands_value[0]}")
                        brands_display = ', '.join([item.get('value', item.get('name', '')) for item in brands_value if item.get('value') or item.get('name')])
                        print(f"   ✅✅✅ Extracted brands from list[dict]: '{brands_display}'")
                    else:
                        brands_display = ', '.join(str(b) for b in brands_value if b)
                        print(f"   ✅✅✅ Extracted brands from list: '{brands_display}'")
                elif isinstance(brands_value, str) and brands_value.strip():
                    brands_display = brands_value.strip()
                    print(f"   ✅✅✅ Extracted brands from string: '{brands_display}'")
                elif brands_value:
                    brands_display = str(brands_value)
                    print(f"   ✅✅✅ Extracted brands (other): '{brands_display}'")
                else:
                    print(f"   ❌ brands_value is empty or invalid")
            else:
                print(f"   ❌ 'brands' not in parsed_data['fields']")
        else:
            print(f"   ❌ 'fields' not in parsed_data")
        
        components_display = 'Not specified'
        if 'fields' in parsed_data and parsed_data['fields'].get('components'):
            components_value = parsed_data['fields']['components']
            if isinstance(components_value, list) and components_value:
                components_display = ', '.join([item.get('name', str(item)) for item in components_value if item])
            elif isinstance(components_value, str) and components_value.strip():
                components_display = components_value.strip()
            elif components_value:
                components_display = str(components_value)
        
        story_points_display = 'Not estimated'
        if 'fields' in parsed_data and parsed_data['fields'].get('story_points'):
            sp_value = parsed_data['fields']['story_points']
            if sp_value:
                story_points_display = str(sp_value) if not isinstance(sp_value, (list, dict)) else str(sp_value)
        
        report = f"""# {mode} Groom Report — {parsed_data['ticket_key']} | {parsed_data['title']}
**Sprint Readiness:** {status}
**Coverage:** {readiness_percentage}%

## Definition of Ready
- **Present:** {self._format_field_names(dor.get('present', []))}
- **Missing:** {self._format_field_names(dor.get('missing', []))}
- **Conflicts:** {self._format_field_names(dor.get('conflicts', []))}
- **Weak Areas:** {', '.join(weak_areas) if weak_areas else 'None'}
- **Jira Status:** {jira_status}
- **Story Points:** {story_points_display} | **Brand:** {brands_display} | **Component:** {components_display}

## User Story (for Stories/Features)

### ✨ Suggested Improvement:
{analysis_results.get('suggested_rewrite', 'Story rewrite pending')}

**Next Steps:**
{("- Story is well-formed and meets DoR ✅" if 'user_story' in dor.get('present', []) and readiness_percentage >= 80 else ("- Refine user story with Scrum team" + newline + "- Add missing acceptance criteria" + newline + "- Define technical implementation details" if 'user_story' in dor.get('present', []) else "- Create user story using format: As a [persona], I want [goal], so that [benefit]" + newline + "- Discuss with PO to understand user needs" + newline + "- Identify acceptance criteria"))}

## ✅ Acceptance Criteria

### ✨ Improvement Suggestions:
{self._format_ac_improvements_with_description(analysis_results.get('description_improvements', {}), analysis_results.get('ac_professional_suggestions', []), newline)}

## 🧪 Test Scenarios (Functional + Non-Functional)

### ✅ Positive Scenarios:
{(newline.join([f"{i+1}. {scenario}" for i, scenario in enumerate(analysis_results.get('test_scenarios', {}).get('positive', []))]) if analysis_results.get('test_scenarios', {}).get('positive') else "_No positive scenarios defined_")}

### ⚠️ Negative Scenarios:
{(newline.join([f"{i+1}. {scenario}" for i, scenario in enumerate(analysis_results.get('test_scenarios', {}).get('negative', []))]) if analysis_results.get('test_scenarios', {}).get('negative') else "_No negative scenarios defined_")}

### 🔥 Error/Resilience Scenarios:
{(newline.join([f"{i+1}. {scenario}" for i, scenario in enumerate(analysis_results.get('test_scenarios', {}).get('error', []))]) if analysis_results.get('test_scenarios', {}).get('error') else "_No error/resilience scenarios defined_")}

_Note: Test scenarios are testable, non-overlapping, and map directly to acceptance criteria. Ready for QA to convert into detailed test cases._

## 🧱 Technical / ADA / Architecture

### 💻 Implementation Details:
{(newline.join([f"• {detail}" for detail in analysis_results.get('technical_ada', {}).get('implementation_details_list', [])]) if analysis_results.get('technical_ada', {}).get('implementation_details_list') else "• Implementation approach to be defined during sprint planning" + newline + "• Update existing components per design specifications" + newline + "• Integrate with current API endpoints (no new backend required)" + newline + "• Apply design system tokens for consistent UI/UX" + newline + "• Ensure backward compatibility with existing functionality")}

### 🏗️ Architectural Solution:
{(newline.join([f"• {solution}" for solution in analysis_results.get('technical_ada', {}).get('architectural_solution_list', [])]) if analysis_results.get('technical_ada', {}).get('architectural_solution_list') else "• No backend schema changes required" + newline + "• Reuses existing APIs and data models" + newline + "• Client-side logic with existing state management (Redux/Context)" + newline + "• Components designed to be reusable across variants" + newline + "• Integrates with existing analytics and monitoring modules")}

### ♿ ADA (Accessibility):
{(newline.join([f"• {ada}" for ada in analysis_results.get('technical_ada', {}).get('ada_list', [])]) if analysis_results.get('technical_ada', {}).get('ada_list') else "• Keyboard navigation: Tab, Enter, Escape keys fully control all interactions" + newline + "• Screen reader labels for all interactive elements and state changes" + newline + "• Color contrast ratios meet WCAG 2.1 Level AA standards" + newline + "• Focus state visible for all interactive elements" + newline + "• ARIA live regions announce dynamic content changes to assistive technologies")}

### 📊 NFRs (Non-Functional Requirements):
{(newline.join([f"• {nfr}" for nfr in analysis_results.get('technical_ada', {}).get('nfr_list', [])]) if analysis_results.get('technical_ada', {}).get('nfr_list') else "• **Performance:** Page interactions respond within ≤500ms; initial load ≤2s" + newline + "• **Security:** All API calls use HTTPS; no PII exposure in logs/analytics" + newline + "• **Reliability:** State persists on page reload or back-navigation" + newline + "• **Analytics:** All user interactions fire correct tracking events" + newline + "• **Accessibility:** Full WCAG 2.1 Level AA compliance")}

## 🎨 Design
Links: {', '.join([f"[{link.anchor_text or 'Figma'}]({link.url})" for link in parsed_data['design_links']]) if parsed_data['design_links'] else ('_Figma referenced in ticket but no direct link found. Please add Figma URL to Jira._' if figma_mentioned else 'None')}

## 💡 Recommendations

### 📊 Product Owner (PO):
{(newline.join([f"{rec}" for rec in analysis_results.get('recommendations', {}).get('po', [])]) if analysis_results.get('recommendations', {}).get('po') else "_No specific PO recommendations for this ticket_")}

### 🧪 QA Team:
{(newline.join([f"{rec}" for rec in analysis_results.get('recommendations', {}).get('qa', [])]) if analysis_results.get('recommendations', {}).get('qa') else "_No specific QA recommendations for this ticket_")}

### 💻 Dev / Tech Lead:
{(newline.join([f"{rec}" for rec in analysis_results.get('recommendations', {}).get('dev', [])]) if analysis_results.get('recommendations', {}).get('dev') else "_No specific Dev recommendations for this ticket_")}

---

## ✅ Quality Check

**Persona:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("as a") > 0 else "✗ Missing"}  
**Goal:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("i want") > 0 else "✗ Missing"}  
**Benefit:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("so that") > 0 else "✗ Missing"}
"""
        
        return report
    
    def _generate_insight_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                                  status: str, readiness_percentage: int, dor: Dict[str, List[str]], 
                                  weak_areas: List[str], figma_mentioned: bool) -> str:
        """Generate balanced Insight report (medium detail)"""
        mode = "Insight (Balanced Groom)"
        newline = '\n'  # Can't use chr(10) or \n in f-string expressions
        
        report = f"""# 🔍 {mode} — {parsed_data['ticket_key']} | {parsed_data['title']}
**Sprint Readiness:** {status} | **Coverage:** {readiness_percentage}%

## 📋 Definition of Ready
- **Present:** {self._format_field_names(dor.get('present', []))}
- **Missing:** {self._format_field_names(dor.get('missing', []))}
- **Weak Areas:** {', '.join(weak_areas[:3])}

## 🧩 User Story
{parsed_data['fields'].get('user_story') if parsed_data['fields'].get('user_story') else '_⚠️ User story missing. Suggested: "' + analysis_results.get('suggested_rewrite', 'Define user story with persona, goal, and benefit') + '"_'}

**Jira Status:** {parsed_data.get('status', 'Unknown')}

## ✅ Acceptance Criteria
**Detected:** {len(analysis_results.get('ac_rewrites', []))} | **Quality:** {analysis_results.get('ac_analysis', {}).get('testable_count', 0)}/{len(analysis_results.get('ac_rewrites', []))} testable

### Key Criteria:
{(newline.join([f"{i+1}. {ac}" for i, ac in enumerate(analysis_results.get('ac_rewrites', [])[:5])]) if analysis_results.get('ac_rewrites') else "1. Feature displays correctly per design specifications" + newline + "2. User interactions trigger expected responses" + newline + "3. Error states display clear messages")}

_Missing NFRs:_ {', '.join([nfr.get('type', '') for nfr in analysis_results.get('missing_nfrs', [])[:3]]) if analysis_results.get('missing_nfrs') else 'None'}

## 🧪 Test Scenarios
**Positive:** {len(analysis_results.get('test_scenarios', {}).get('positive', []))} | **Negative:** {len(analysis_results.get('test_scenarios', {}).get('negative', []))} | **Error:** {len(analysis_results.get('test_scenarios', {}).get('error', []))}

## 🧱 Technical / ADA / Architecture
### Implementation:
{(newline.join([f"• {detail}" for detail in analysis_results.get('technical_ada', {}).get('implementation_details_list', [])[:3]]) if analysis_results.get('technical_ada', {}).get('implementation_details_list') else "• Update components per design specifications" + newline + "• Integrate with current API endpoints")}

### ADA:
{(newline.join([f"• {ada}" for ada in analysis_results.get('technical_ada', {}).get('ada_list', [])[:3]]) if analysis_results.get('technical_ada', {}).get('ada_list') else "• Keyboard navigation support" + newline + "• Screen reader compatibility")}

## 🎨 Design
Links: {', '.join([f"[{link.anchor_text or 'Figma'}]({link.url})" for link in parsed_data['design_links']]) if parsed_data['design_links'] else ('_Figma mentioned but no link_' if figma_mentioned else 'None')}

## 💡 Key Recommendations
**PO:** {analysis_results.get('recommendations', {}).get('po', ['Define success metrics'])[0] if analysis_results.get('recommendations', {}).get('po') else 'Define measurable KPIs for this story'}

**QA:** {analysis_results.get('recommendations', {}).get('qa', ['Expand test coverage'])[0] if analysis_results.get('recommendations', {}).get('qa') else 'Include accessibility and cross-browser testing'}

**Dev:** {analysis_results.get('recommendations', {}).get('dev', ['Document implementation'])[0] if analysis_results.get('recommendations', {}).get('dev') else 'Add telemetry and document error handling'}

---

## ✅ Quality Check

**Persona:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("as a") > 0 else "✗ Missing"}  
**Goal:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("i want") > 0 else "✗ Missing"}  
**Benefit:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("so that") > 0 else "✗ Missing"}
"""
        
        return report
    
    def _generate_summary_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                                  status: str, readiness_percentage: int, dor: Dict[str, List[str]], 
                                  weak_areas: List[str], figma_mentioned: bool) -> str:
        """Generate concise Summary report (snapshot)"""
        mode = "Summary (Snapshot)"
        
        report = f"""# 📸 {mode} — {parsed_data.get('ticket_key', '') or ''}
## {parsed_data.get('title', '') or ''}

**Status:** {status} | **Coverage:** {readiness_percentage}%

### ✅ Present
{self._format_field_names(dor.get('present', [])[:5])}

### ❌ Missing
{self._format_field_names(dor.get('missing', [])[:5])}

### ⚠️ Weak Areas
{', '.join(weak_areas[:3])}

### 📊 Quick Stats
- **Acceptance Criteria:** {len(analysis_results.get('ac_rewrites', []))} detected
- **Test Scenarios:** {len(analysis_results.get('test_scenarios', {}).get('positive', []))} positive, {len(analysis_results.get('test_scenarios', {}).get('negative', []))} negative
- **User Story:** {"✅ Present" if parsed_data['fields'].get('user_story') else "❌ Missing"}
- **Story Points:** {parsed_data['fields'].get('story_points', 'Not estimated')}
- **Jira Status:** {parsed_data.get('status', 'Unknown')}

### 🎯 Next Steps
{"✅ **Ready for Sprint** - Review with team and start development" if readiness_percentage >= 80 else "🟡 **Needs Grooming** - " + (self._format_field_names(dor.get('missing', [])[:3])) if readiness_percentage >= 40 else "🔴 **Not Ready** - Significant work needed: " + (self._format_field_names(dor.get('missing', [])[:3]))}

### 💡 Top Recommendations
- **PO:** {analysis_results.get('recommendations', {}).get('po', ['Define KPIs'])[0][:80] + '...' if len(analysis_results.get('recommendations', {}).get('po', ['Define KPIs'])[0]) > 80 else analysis_results.get('recommendations', {}).get('po', ['Define KPIs'])[0] if analysis_results.get('recommendations', {}).get('po') else 'Define success metrics'}
- **QA:** {analysis_results.get('recommendations', {}).get('qa', ['Expand tests'])[0][:80] + '...' if len(analysis_results.get('recommendations', {}).get('qa', ['Expand tests'])[0]) > 80 else analysis_results.get('recommendations', {}).get('qa', ['Expand tests'])[0] if analysis_results.get('recommendations', {}).get('qa') else 'Include accessibility testing'}
- **Dev:** {analysis_results.get('recommendations', {}).get('dev', ['Add telemetry'])[0][:80] + '...' if len(analysis_results.get('recommendations', {}).get('dev', ['Add telemetry'])[0]) > 80 else analysis_results.get('recommendations', {}).get('dev', ['Add telemetry'])[0] if analysis_results.get('recommendations', {}).get('dev') else 'Document error handling'}

---

## ✅ Quality Check

**Persona:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("as a") > 0 else "✗ Missing"}  
**Goal:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("i want") > 0 else "✗ Missing"}  
**Benefit:** {"✓" if (str(analysis_results.get('suggested_rewrite') or '')).lower().count("so that") > 0 else "✗ Missing"}
"""
        
        return report

    def analyze_ticket(self, ticket_data: Dict[str, Any], mode: str = "Actionable", status_fallback: str = None) -> GroomroomResponse:
        """Main analysis method - comprehensive ticket analysis without scoring"""
        try:
            # Extract status_fallback from ticket_data if available
            if not status_fallback and isinstance(ticket_data, dict):
                # Try to get status from ticket_info if it's nested
                if 'status' in ticket_data and isinstance(ticket_data['status'], str):
                    status_fallback = ticket_data['status']
                # Or from fields.status.name
                elif 'fields' in ticket_data and 'status' in ticket_data['fields']:
                    status_obj = ticket_data['fields']['status']
                    if isinstance(status_obj, dict) and 'name' in status_obj:
                        status_fallback = status_obj['name']
            
            # Parse Jira content with status_fallback
            parsed_data = self.parse_jira_content(ticket_data, status_fallback=status_fallback)
            
            # AGGRESSIVE FIX: ALWAYS set status from status_fallback if available
            # CRITICAL: Force set status from status_fallback FIRST, before checking anything else
            current_status = parsed_data.get('status', 'Unknown')
            
            # PRIORITY 1: Use status_fallback if it's valid
            if status_fallback and status_fallback != 'Unknown' and status_fallback is not None:
                print(f"🔧 FORCING: Setting status from status_fallback: {status_fallback}")
                parsed_data['status'] = status_fallback
                # ALSO store in fields for redundancy
                if 'fields' not in parsed_data:
                    parsed_data['fields'] = {}
                parsed_data['fields']['status'] = {'name': status_fallback}
                print(f"🔧 Status set in both locations: {status_fallback}")
            # PRIORITY 2: Use current_status if it's valid and status_fallback is not
            elif current_status and current_status != 'Unknown':
                print(f"✅ Keeping existing status from parsed_data: {current_status}")
                if 'fields' not in parsed_data:
                    parsed_data['fields'] = {}
                parsed_data['fields']['status'] = {'name': current_status}
            # PRIORITY 3: Try to get from fields.status
            elif 'fields' in parsed_data and 'status' in parsed_data['fields']:
                fields_status = parsed_data['fields']['status']
                if isinstance(fields_status, dict) and 'name' in fields_status:
                    final_status = fields_status['name']
                    if final_status and final_status != 'Unknown':
                        parsed_data['status'] = final_status
                        print(f"✅ Got status from fields.status: {final_status}")
            # PRIORITY 4: Last resort - try to get from ticket_data directly
            elif isinstance(ticket_data, dict):
                # Try renderedFields
                if 'renderedFields' in ticket_data:
                    rendered = ticket_data.get('renderedFields', {})
                    if rendered and rendered.get('status'):
                        status_obj = rendered.get('status')
                        if isinstance(status_obj, dict) and 'name' in status_obj:
                            final_status = status_obj['name']
                            if final_status and final_status != 'Unknown':
                                parsed_data['status'] = final_status
                                print(f"✅ Got status from ticket_data['renderedFields']['status']: {final_status}")
            else:
                print(f"⚠️ WARNING: Status is Unknown and no status_fallback available")
                print(f"   current_status: {current_status}")
                print(f"   status_fallback: {status_fallback}")
            
            # Debug: Print final status
            print(f"\n🔍 DEBUG analyze_ticket - Final parsed_data status: {parsed_data.get('status')}")
            print(f"   parsed_data['fields'].get('status'): {parsed_data.get('fields', {}).get('status')}")
            
            # Calculate DoR coverage
            present_fields, missing_fields, conflicts = self.calculate_dor_coverage(parsed_data)
            
            # Calculate readiness percentage
            total_fields = len(present_fields) + len(missing_fields)
            readiness_percentage = int((len(present_fields) / total_fields * 100)) if total_fields > 0 else 0
            
            # Determine status based on rules
            status = self.determine_status(present_fields, missing_fields, conflicts, parsed_data['card_type'])
            
            # Format status with percentage
            status_with_percentage = f"{readiness_percentage}% - {status}"
            
            # Generate contextual content
            suggested_rewrite = self.generate_suggested_rewrite(parsed_data)
            ac_rewrites = self.generate_acceptance_criteria_rewrites(parsed_data)
            test_scenarios = self.generate_test_scenarios(parsed_data, ac_rewrites)
            recommendations = self.generate_recommendations(parsed_data, conflicts)
            
            # Analyze AC quality
            ac_analysis = self.analyze_ac_quality(ac_rewrites)
            ac_gwt_suggestions = self.generate_gwt_format(parsed_data, ac_rewrites)
            missing_nfrs = self.identify_missing_nfrs(parsed_data, ac_rewrites)
            
            # Generate professional AC improvement suggestions
            # Extract raw acceptance criteria from Jira (before any processing)
            raw_ac_text = self._extract_text_from_field(ticket_data.get('fields', {}).get('customfield_13383', ''))
            if not raw_ac_text or len(raw_ac_text.strip()) < 10:
                # Fallback to description if no custom field
                raw_ac_text = parsed_data['fields'].get('acceptance_criteria', '')
            
            # Split by newlines and clean each line
            original_acs = []
            for line in raw_ac_text.split('\n'):
                cleaned = line.strip().strip('-•*1234567890. ').strip()
                # Skip headers, empty lines, and very short lines
                if cleaned and len(cleaned) > 10 and not cleaned.lower().startswith('acceptance') and not cleaned.lower().startswith('applicable'):
                    original_acs.append(cleaned)
            
            ac_professional_suggestions = self.generate_professional_ac_suggestions(original_acs, parsed_data)
            
            # Generate description improvements using AC context
            description_improvements = self.generate_description_improvements(parsed_data, ac_rewrites)
            
            # Generate detailed technical/ADA/architecture content
            technical_details = self.generate_technical_details(parsed_data)
            
            # Build analysis results
            analysis_results = {
                'mode': mode,
                'status': status_with_percentage,
                'readiness_percentage': readiness_percentage,
                'dor': {
                    'present': present_fields,
                    'missing': missing_fields,
                    'conflicts': conflicts
                },
                'suggested_rewrite': suggested_rewrite,
                'ac_rewrites': ac_rewrites,
                'ac_analysis': ac_analysis,
                'ac_gwt_suggestions': ac_gwt_suggestions,
                'missing_nfrs': missing_nfrs,
                'ac_professional_suggestions': ac_professional_suggestions,
                'description_improvements': description_improvements,
                'test_scenarios': test_scenarios,
                'technical_ada': technical_details,
                'recommendations': recommendations
            }
            
            # Generate Markdown report
            markdown_report = self.generate_markdown_report(parsed_data, analysis_results)
            
            # Build structured data
            structured_data = {
                'TicketKey': parsed_data['ticket_key'],
                'Title': parsed_data['title'],
                'Type': parsed_data['card_type'].title(),
                'Mode': mode,
                'SprintReadiness': readiness_percentage,
                'Status': status_with_percentage,
                'DoR': {
                    'Present': present_fields,
                    'Missing': missing_fields,
                    'Conflicts': conflicts
                },
                'StoryReview': {
                    'Persona': True,
                    'Goal': True,
                    'Benefit': True,
                    'SuggestedRewrite': suggested_rewrite
                } if parsed_data['card_type'] in ['story', 'feature'] else None,
                'AcceptanceCriteria': {
                    'Detected': len(parsed_data['fields'].get('acceptance_criteria', '').split('\n')),
                    'Rewrites': ac_rewrites
                },
                'TestScenarios': test_scenarios,
                'TechnicalADA': analysis_results['technical_ada'],
                'DesignLinks': [link.url for link in parsed_data['design_links']],
                'Recommendations': recommendations,
                'Brands': parsed_data['fields'].get('brands', ''),
                'StoryPoints': parsed_data['fields'].get('story_points', ''),
                'Components': parsed_data['fields'].get('components', ''),
                'AgileTeam': parsed_data['fields'].get('agile_team', '')
            }
            
            return GroomroomResponse(
                markdown=markdown_report,
                data=structured_data
            )
            
        except Exception as e:
            # Fallback response
            return GroomroomResponse(
                markdown=f"# Error in Analysis\n\nAnalysis failed: {str(e)}",
                data={
                    'TicketKey': ticket_data.get('key', 'UNKNOWN'),
                    'Title': ticket_data.get('fields', {}).get('summary', 'Unknown'),
                    'Type': 'Unknown',
                    'Mode': mode,
                    'Error': str(e)
                }
            )

# Convenience function for backward compatibility
def analyze_ticket(ticket_data: Dict[str, Any], mode: str = "Actionable") -> GroomroomResponse:
    """Convenience function for ticket analysis"""
    groomroom = GroomRoomNoScoring()
    return groomroom.analyze_ticket(ticket_data, mode)
