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

    def parse_jira_content(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Robust parser with Figma detection and section recognition"""
        parsed = {
            'ticket_key': ticket_data.get('key', ''),
            'title': ticket_data.get('fields', {}).get('summary', ''),
            'description': ticket_data.get('fields', {}).get('description', ''),
            'issuetype': ticket_data.get('fields', {}).get('issuetype', {}).get('name', ''),
            'status': ticket_data.get('fields', {}).get('status', {}).get('name', 'Unknown'),
            'status_category': ticket_data.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', 'Unknown'),
            'fields': {},
            'design_links': [],
            'card_type': 'unknown'
        }
        
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
        
        # Merge: Custom fields override pattern-based extraction
        for field_name, custom_value in custom_field_extractions.items():
            if custom_value:  # If custom field has value, use it
                parsed['fields'][field_name] = custom_value
            elif field_name not in parsed['fields'] or not parsed['fields'][field_name]:
                # Fallback to pattern extraction if custom field is empty
                parsed['fields'][field_name] = parsed['fields'].get(field_name, '')
        
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
        jira_status = parsed_data.get('status', '').lower()
        
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
        return 'figma.com' in url.lower()

    def is_anchor_suggesting_figma(self, anchor_text: str) -> bool:
        """Check if anchor text suggests Figma"""
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
            last_heading = headings[-1].strip().lower()
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
        for field_name in brand_fields:
            if field_name in fields and fields[field_name]:
                # Handle list format (like [{'value': 'Marmot'}])
                value = fields[field_name]
                if isinstance(value, list) and value:
                    if isinstance(value[0], dict):
                        return ', '.join([item.get('value', item.get('name', '')) for item in value])
                    return ', '.join(str(v) for v in value)
                return str(value)
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
        for field_name in story_point_fields:
            if field_name in fields and fields[field_name]:
                return str(fields[field_name])
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
                if content:  # Even "None" counts as present
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
                
                # Even "None" is valid
                if content:
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
        """Generate detailed, realistic user story rewrite (4-5+ lines minimum)"""
        current_story = parsed_data['fields'].get('user_story', '')
        description = self._extract_text_from_field(parsed_data.get('description', ''))
        title = parsed_data['title']
        acceptance_criteria = parsed_data['fields'].get('acceptance_criteria', '')
        
        # Extract domain terms from the ticket
        domain_terms = self.extract_domain_terms(parsed_data)
        
        # If story exists and is well-formed, return it as-is
        if current_story and 'as a' in current_story.lower() and 'i want' in current_story.lower() and 'so that' in current_story.lower() and len(current_story) > 100:
            # Story is already detailed and good!
            return current_story
        
        # If story exists but needs improvement, enhance it
        if current_story and 'as a' in current_story.lower():
            # Build upon existing story with more detail
            persona = self.extract_persona(description, title)
            goal = self.extract_goal(description, title)
            benefit = self.extract_benefit(description, title)
            
            # Add context from acceptance criteria for detail
            context_detail = ""
            if acceptance_criteria and len(acceptance_criteria) > 20:
                # Extract first key requirement for context
                ac_lines = acceptance_criteria.split('\n')
                if ac_lines:
                    first_ac = ac_lines[0].strip('- •*1234567890.').strip()
                    if len(first_ac) > 20:
                        context_detail = f" This includes {first_ac.lower()}"
            
            # Create detailed, multi-line suggestion
            detailed_story = f"As a {persona}, I want to {goal}, so that I can {benefit}.{context_detail}"
            
            # Add business value context if available from description
            if 'revenue' in description.lower() or 'conversion' in description.lower() or 'engagement' in description.lower():
                detailed_story += " This will improve user engagement and drive business outcomes by reducing friction in the user journey."
            elif 'performance' in description.lower() or 'speed' in description.lower():
                detailed_story += " This enhancement will optimize performance and deliver a faster, more responsive experience."
            else:
                detailed_story += " This improvement aligns with user needs and enhances overall product usability."
            
            return detailed_story
        
        # Synthesize detailed story from description + domain terms + AC
        persona = self.extract_persona(description, title)
        goal = self.extract_goal(description, title)
        benefit = self.extract_benefit(description, title)
        
        # NO TRUNCATION - keep full detail!
        goal = goal.replace(title, '').strip()
        
        # Ensure domain terms are included for realism
        if domain_terms and not any(term.lower() in f"{goal} {benefit}".lower() for term in domain_terms):
            goal = f"{goal} using {domain_terms[0]}"
        
        # Build detailed, context-aware suggestion (4-5 lines minimum)
        detailed_story = f"As a {persona}, I want to {goal}, so that I can {benefit}."
        
        # Add specific implementation context from description
        if 'filter' in title.lower() or 'search' in title.lower():
            detailed_story += " The enhanced filtering system will allow me to narrow down results efficiently, saving time and improving my shopping experience. This feature should be intuitive, responsive, and accessible across all devices."
        elif 'checkout' in title.lower() or 'payment' in title.lower():
            detailed_story += " By streamlining the checkout process, I can complete purchases faster with fewer steps, reducing cart abandonment and improving conversion rates. The flow should be secure, clear, and optimized for both desktop and mobile."
        elif 'form' in title.lower() or 'input' in title.lower():
            detailed_story += " Clear validation and helpful error messages will guide me through the form completion process, reducing frustration and submission errors. The interface should provide real-time feedback and support accessibility standards."
        else:
            # Generic but detailed enhancement
            detailed_story += " This improvement will streamline my workflow, reduce unnecessary steps, and deliver a more intuitive experience. The implementation should follow best practices for usability, performance, and accessibility to ensure all users benefit."
        
        return detailed_story

    def extract_domain_terms(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Extract domain-specific terms from ticket content"""
        all_text = f"{parsed_data['title']} {parsed_data['description']}"
        domain_keywords = [
            'PayPal', 'ABTasty', 'SFCC-Checkout', 'PLP', 'Filters', 'Yankee', 'Marmot', 'Graco',
            'checkout', 'payment', 'filter', 'search', 'cart', 'login', 'auth', 'password'
        ]
        return [term for term in domain_keywords if term.lower() in all_text.lower()]

    def extract_persona(self, description: str, title: str) -> str:
        """Extract persona from content"""
        text = f"{title} {description}".lower()
        persona_synonyms = ['shopper', 'user', 'customer', 'visitor', 'admin', 'registered user']
        
        for persona in persona_synonyms:
            if persona in text:
                return persona
        
        return "user"

    def extract_goal(self, description: str, title: str) -> str:
        """Extract main goal from content (NO truncation for detailed suggestions)"""
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
        sentences = [s.strip() for s in title.split('.') if len(s.strip()) > 10]
        if sentences:
            goal = sentences[0]
            # NO TRUNCATION - keep full goal text!
            return goal
        
        return "achieve the desired functionality"

    def extract_benefit(self, description: str, title: str) -> str:
        """Extract benefit from content"""
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
        enhanced = ac
        
        # Add timing if not present
        if not re.search(r'\d+\s*(ms|s|seconds?)', enhanced.lower()):
            enhanced += " (≤300ms response time)"
        
        # Add domain context if missing
        if not any(term.lower() in enhanced.lower() for term in domain_terms):
            if domain_terms:
                enhanced += f" (using {domain_terms[0]})"
        
        # Add Figma reference if design links present
        if design_links and 'design' in enhanced.lower():
            figma_ref = f" per Figma {design_links[0].file_key}"
            if design_links[0].node_ids:
                figma_ref += f" node {design_links[0].node_ids[0]}"
            enhanced += figma_ref
        
        return enhanced

    def replace_banned_phrases(self, ac: str, domain_terms: List[str]) -> str:
        """Replace banned generic phrases with specific requirements"""
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
        description = parsed_data['description']
        title = parsed_data['title']
        
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
        """Generate P/N/E test scenarios mapped directly from ACs"""
        scenarios = {
            'positive': [],
            'negative': [],
            'error': []
        }
        
        # Get actual test steps from Jira if available
        testing_steps = parsed_data['fields'].get('testing_steps', '')
        
        # Parse testing steps if available
        if testing_steps and len(testing_steps) > 50:
            # Extract numbered test scenarios from Jira
            test_lines = [line.strip() for line in testing_steps.split('\n') if line.strip()]
            for line in test_lines:
                # Clean up HTML tags and numbering
                clean_line = re.sub(r'<[^>]+>', '', line)
                clean_line = re.sub(r'^\d+[\.\)]\s*', '', clean_line)
                clean_line = re.sub(r'^[-•]\s*', '', clean_line)
                
                if len(clean_line) > 20:
                    # Categorize based on keywords
                    line_lower = clean_line.lower()
                    
                    if any(word in line_lower for word in ['invalid', 'error', 'incorrect', 'wrong', 'negative', 'edge', 'unauthorized', 'prevent']):
                        scenarios['negative'].append(clean_line)
                    elif any(word in line_lower for word in ['timeout', 'failure', 'network', 'connection', 'resilience', 'handles', 'gracefully']):
                        scenarios['error'].append(clean_line)
                    else:
                        scenarios['positive'].append(clean_line)
        
        # If no testing steps or need more scenarios, generate from context
        if len(scenarios['positive']) < 3:
            # Generate positive scenarios
            base_positives = [
                "Valid input produces expected output with correct data",
                "User completes primary workflow successfully from start to finish",
                "Feature displays correctly per design specifications on all devices",
                "All interactive elements respond within acceptable performance thresholds (≤300ms)",
                "Data persists correctly and remains consistent across sessions",
                "Navigation flows work as expected with proper state management"
            ]
            scenarios['positive'].extend(base_positives[:6 - len(scenarios['positive'])])
        
        if len(scenarios['negative']) < 3:
            # Generate negative scenarios
            base_negatives = [
                "Invalid input shows appropriate error message with clear guidance",
                "System prevents unauthorized access and maintains security boundaries",
                "Boundary conditions are handled correctly (empty, null, max values)",
                "Duplicate actions are prevented or handled appropriately",
                "Required fields validation works correctly with user feedback",
                "Conflicting operations are blocked with explanatory messages"
            ]
            scenarios['negative'].extend(base_negatives[:6 - len(scenarios['negative'])])
        
        if len(scenarios['error']) < 3:
            # Generate error/resilience scenarios
            base_errors = [
                "System handles network timeout gracefully with retry mechanism",
                "Database connection failure is handled with appropriate fallback",
                "API errors return user-friendly messages and log technical details",
                "Partial data loads are handled without breaking functionality",
                "Session expiration redirects user appropriately with state preservation",
                "Concurrent operations maintain data integrity without conflicts"
            ]
            scenarios['error'].extend(base_errors[:6 - len(scenarios['error'])])
        
        # Add non-functional test scenarios if not covered
        nfr_positives = [
            "Page load completes within 2 seconds on standard connection",
            "Keyboard navigation works for all interactive elements (Tab, Enter, Escape)",
            "Screen reader announces all content changes with proper ARIA labels"
        ]
        
        nfr_negatives = [
            "System prevents SQL injection and XSS attacks on all inputs",
            "CSRF tokens are validated for all state-changing operations"
        ]
        
        nfr_errors = [
            "Memory leaks are prevented during long sessions or repeated actions",
            "Browser crashes or tab closes preserve critical user data"
        ]
        
        # Add NFRs if space available
        if len(scenarios['positive']) < 8:
            scenarios['positive'].extend(nfr_positives[:8 - len(scenarios['positive'])])
        if len(scenarios['negative']) < 8:
            scenarios['negative'].extend(nfr_negatives[:8 - len(scenarios['negative'])])
        if len(scenarios['error']) < 8:
            scenarios['error'].extend(nfr_errors[:8 - len(scenarios['error'])])
        
        # Limit to reasonable number
        scenarios['positive'] = scenarios['positive'][:12]
        scenarios['negative'] = scenarios['negative'][:12]
        scenarios['error'] = scenarios['error'][:12]
        
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
        title = parsed_data['title'].lower()
        description = self._extract_text_from_field(parsed_data.get('description', '')).lower()
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

    def generate_professional_ac_suggestions(self, original_acs: List[str], parsed_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate detailed, professional rewrite suggestions for each acceptance criterion"""
        suggestions = []
        title = parsed_data.get('title', '').lower()
        description = self._extract_text_from_field(parsed_data.get('description', ''))
        
        for i, original_ac in enumerate(original_acs):
            if not original_ac or len(original_ac.strip()) < 5:
                continue
            
            ac_lower = original_ac.lower()
            
            # Determine context and create professional rewrite
            rewrite = ""
            why_better = ""
            
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

    def hyperlink_figma_references(self, text: str, design_links: List[DesignLink]) -> str:
        """Replace Figma text references with clickable markdown links (avoid double-linking)"""
        if not design_links or not text:
            return text
        
        # Don't hyperlink if text already contains markdown links
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
        
        report = f"""# {mode} Groom Report — {parsed_data['ticket_key']} | {parsed_data['title']}
**Sprint Readiness:** {status}
**Coverage:** {readiness_percentage}%

## Definition of Ready
- **Present:** {self._format_field_names(dor.get('present', []))}
- **Missing:** {self._format_field_names(dor.get('missing', []))}
- **Conflicts:** {self._format_field_names(dor.get('conflicts', []))}
- **Weak Areas:** {', '.join(weak_areas) if weak_areas else 'None'}

## User Story (for Stories/Features)

### ✨ Suggested Improvement:
**Rewrite:** "{analysis_results.get('suggested_rewrite', 'Story rewrite pending')}"

**Quality Check:**
- Persona ✅ ({"✓" if "as a" in analysis_results.get('suggested_rewrite', '').lower() else "✗ Missing"})
- Goal ✅ ({"✓" if "i want" in analysis_results.get('suggested_rewrite', '').lower() else "✗ Missing"})
- Benefit ✅ ({"✓" if "so that" in analysis_results.get('suggested_rewrite', '').lower() else "✗ Missing"})

### 📍 Grooming Guidance:
**Jira Status:** {parsed_data.get('status', 'Unknown')}

**Next Steps:**
{"- Story is well-formed and meets DoR ✅" if 'user_story' in dor.get('present', []) and readiness_percentage >= 80 else "- Refine user story with Scrum team" + chr(10) + "- Add missing acceptance criteria" + chr(10) + "- Define technical implementation details" if 'user_story' in dor.get('present', []) else "- Create user story using format: As a [persona], I want [goal], so that [benefit]" + chr(10) + "- Discuss with PO to understand user needs" + chr(10) + "- Identify acceptance criteria"}

**Story Points:** {parsed_data['fields'].get('story_points', '❌ Not estimated')}
**Team:** {parsed_data['fields'].get('agile_team', '❌ Not assigned')}
**Brand/Component:** {parsed_data['fields'].get('brands', 'N/A')} / {parsed_data['fields'].get('components', 'N/A')}

## ✅ Acceptance Criteria

**Detected {len(analysis_results.get('ac_professional_suggestions', []))} | Weak {analysis_results.get('ac_analysis', {}).get('weak_count', 0)}**

### ✨ Professional Improvement Suggestions:

{chr(10).join([f'''**AC #{i+1} Improvement:**
{sugg.get('rewrite', 'No suggestion available')}

''' for i, sugg in enumerate(analysis_results.get('ac_professional_suggestions', []))]) if analysis_results.get('ac_professional_suggestions') else "_No suggestions available_"}

## 🧪 Test Scenarios (Functional + Non-Functional)

### ✅ Positive Scenarios:
{chr(10).join([f"{i+1}. {scenario}" for i, scenario in enumerate(analysis_results.get('test_scenarios', {}).get('positive', []))]) if analysis_results.get('test_scenarios', {}).get('positive') else "_No positive scenarios defined_"}

### ⚠️ Negative Scenarios:
{chr(10).join([f"{i+1}. {scenario}" for i, scenario in enumerate(analysis_results.get('test_scenarios', {}).get('negative', []))]) if analysis_results.get('test_scenarios', {}).get('negative') else "_No negative scenarios defined_"}

### 🔥 Error/Resilience Scenarios:
{chr(10).join([f"{i+1}. {scenario}" for i, scenario in enumerate(analysis_results.get('test_scenarios', {}).get('error', []))]) if analysis_results.get('test_scenarios', {}).get('error') else "_No error/resilience scenarios defined_"}

_Note: Test scenarios are testable, non-overlapping, and map directly to acceptance criteria. Ready for QA to convert into detailed test cases._

## 🧱 Technical / ADA / Architecture

### 💻 Implementation Details:
{chr(10).join([f"• {detail}" for detail in analysis_results.get('technical_ada', {}).get('implementation_details_list', [])]) if analysis_results.get('technical_ada', {}).get('implementation_details_list') else "• Implementation approach to be defined during sprint planning" + chr(10) + "• Update existing components per design specifications" + chr(10) + "• Integrate with current API endpoints (no new backend required)" + chr(10) + "• Apply design system tokens for consistent UI/UX" + chr(10) + "• Ensure backward compatibility with existing functionality"}

### 🏗️ Architectural Solution:
{chr(10).join([f"• {solution}" for solution in analysis_results.get('technical_ada', {}).get('architectural_solution_list', [])]) if analysis_results.get('technical_ada', {}).get('architectural_solution_list') else "• No backend schema changes required" + chr(10) + "• Reuses existing APIs and data models" + chr(10) + "• Client-side logic with existing state management (Redux/Context)" + chr(10) + "• Components designed to be reusable across variants" + chr(10) + "• Integrates with existing analytics and monitoring modules"}

### ♿ ADA (Accessibility):
{chr(10).join([f"• {ada}" for ada in analysis_results.get('technical_ada', {}).get('ada_list', [])]) if analysis_results.get('technical_ada', {}).get('ada_list') else "• Keyboard navigation: Tab, Enter, Escape keys fully control all interactions" + chr(10) + "• Screen reader labels for all interactive elements and state changes" + chr(10) + "• Color contrast ratios meet WCAG 2.1 Level AA standards" + chr(10) + "• Focus state visible for all interactive elements" + chr(10) + "• ARIA live regions announce dynamic content changes to assistive technologies"}

### 📊 NFRs (Non-Functional Requirements):
{chr(10).join([f"• {nfr}" for nfr in analysis_results.get('technical_ada', {}).get('nfr_list', [])]) if analysis_results.get('technical_ada', {}).get('nfr_list') else "• **Performance:** Page interactions respond within ≤500ms; initial load ≤2s" + chr(10) + "• **Security:** All API calls use HTTPS; no PII exposure in logs/analytics" + chr(10) + "• **Reliability:** State persists on page reload or back-navigation" + chr(10) + "• **Analytics:** All user interactions fire correct tracking events" + chr(10) + "• **Accessibility:** Full WCAG 2.1 Level AA compliance"}

## 🎨 Design
Links: {', '.join([f"[{link.anchor_text or 'Figma'}]({link.url})" for link in parsed_data['design_links']]) if parsed_data['design_links'] else ('_Figma referenced in ticket but no direct link found. Please add Figma URL to Jira._' if figma_mentioned else 'None')}

## 💡 Recommendations

### 📊 Product Owner (PO):
{chr(10).join([f"{rec}" for rec in analysis_results.get('recommendations', {}).get('po', [])]) if analysis_results.get('recommendations', {}).get('po') else "_No specific PO recommendations for this ticket_"}

### 🧪 QA Team:
{chr(10).join([f"{rec}" for rec in analysis_results.get('recommendations', {}).get('qa', [])]) if analysis_results.get('recommendations', {}).get('qa') else "_No specific QA recommendations for this ticket_"}

### 💻 Dev / Tech Lead:
{chr(10).join([f"{rec}" for rec in analysis_results.get('recommendations', {}).get('dev', [])]) if analysis_results.get('recommendations', {}).get('dev') else "_No specific Dev recommendations for this ticket_"}
"""
        
        return report
    
    def _generate_insight_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                                  status: str, readiness_percentage: int, dor: Dict[str, List[str]], 
                                  weak_areas: List[str], figma_mentioned: bool) -> str:
        """Generate balanced Insight report (medium detail)"""
        mode = "Insight (Balanced Groom)"
        
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
{chr(10).join([f"{i+1}. {ac}" for i, ac in enumerate(analysis_results.get('ac_rewrites', [])[:5])]) if analysis_results.get('ac_rewrites') else "1. Feature displays correctly per design specifications" + chr(10) + "2. User interactions trigger expected responses" + chr(10) + "3. Error states display clear messages"}

_Missing NFRs:_ {', '.join([nfr.get('type', '') for nfr in analysis_results.get('missing_nfrs', [])[:3]]) if analysis_results.get('missing_nfrs') else 'None'}

## 🧪 Test Scenarios
**Positive:** {len(analysis_results.get('test_scenarios', {}).get('positive', []))} | **Negative:** {len(analysis_results.get('test_scenarios', {}).get('negative', []))} | **Error:** {len(analysis_results.get('test_scenarios', {}).get('error', []))}

## 🧱 Technical / ADA / Architecture
### Implementation:
{chr(10).join([f"• {detail}" for detail in analysis_results.get('technical_ada', {}).get('implementation_details_list', [])[:3]]) if analysis_results.get('technical_ada', {}).get('implementation_details_list') else "• Update components per design specifications" + chr(10) + "• Integrate with current API endpoints"}

### ADA:
{chr(10).join([f"• {ada}" for ada in analysis_results.get('technical_ada', {}).get('ada_list', [])[:3]]) if analysis_results.get('technical_ada', {}).get('ada_list') else "• Keyboard navigation support" + chr(10) + "• Screen reader compatibility"}

## 🎨 Design
Links: {', '.join([f"[{link.anchor_text or 'Figma'}]({link.url})" for link in parsed_data['design_links']]) if parsed_data['design_links'] else ('_Figma mentioned but no link_' if figma_mentioned else 'None')}

## 💡 Key Recommendations
**PO:** {analysis_results.get('recommendations', {}).get('po', ['Define success metrics'])[0] if analysis_results.get('recommendations', {}).get('po') else 'Define measurable KPIs for this story'}

**QA:** {analysis_results.get('recommendations', {}).get('qa', ['Expand test coverage'])[0] if analysis_results.get('recommendations', {}).get('qa') else 'Include accessibility and cross-browser testing'}

**Dev:** {analysis_results.get('recommendations', {}).get('dev', ['Document implementation'])[0] if analysis_results.get('recommendations', {}).get('dev') else 'Add telemetry and document error handling'}
"""
        
        return report
    
    def _generate_summary_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                                  status: str, readiness_percentage: int, dor: Dict[str, List[str]], 
                                  weak_areas: List[str], figma_mentioned: bool) -> str:
        """Generate concise Summary report (snapshot)"""
        mode = "Summary (Snapshot)"
        
        report = f"""# 📸 {mode} — {parsed_data['ticket_key']}
## {parsed_data['title']}

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
"""
        
        return report

    def analyze_ticket(self, ticket_data: Dict[str, Any], mode: str = "Actionable") -> GroomroomResponse:
        """Main analysis method - comprehensive ticket analysis without scoring"""
        try:
            # Parse Jira content
            parsed_data = self.parse_jira_content(ticket_data)
            
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
                'Recommendations': recommendations
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
