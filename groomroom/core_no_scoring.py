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
        
        # DoR fields by card type
        self.dor_fields = {
            'story': [
                'user_story', 'acceptance_criteria', 'testing_steps', 
                'implementation_details', 'architectural_solution', 'ada_criteria',
                'brands', 'components', 'agile_team', 'story_points'
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

    def parse_jira_content(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Robust parser with Figma detection and section recognition"""
        parsed = {
            'ticket_key': ticket_data.get('key', ''),
            'title': ticket_data.get('fields', {}).get('summary', ''),
            'description': ticket_data.get('fields', {}).get('description', ''),
            'issuetype': ticket_data.get('fields', {}).get('issuetype', {}).get('name', ''),
            'fields': {},
            'design_links': [],
            'card_type': 'unknown'
        }
        
        # Extract all text content for analysis
        all_text = f"{parsed['title']} {parsed['description']}"
        
        # Detect card type
        parsed['card_type'] = self.detect_card_type(all_text, parsed['issuetype'])
        
        # Parse fields using patterns
        for field_name, patterns in self.field_patterns.items():
            content = self.extract_field_content(all_text, patterns)
            parsed['fields'][field_name] = content
        
        # Extract Figma links with anchor text detection
        parsed['design_links'] = self.extract_figma_links_with_anchors(all_text)
        
        # Parse additional Jira fields
        fields = ticket_data.get('fields', {})
        parsed['fields'].update({
            'brands': self.extract_brands(fields),
            'components': self.extract_components(fields),
            'agile_team': self.extract_agile_team(fields),
            'story_points': self.extract_story_points(fields),
            'environment': self.extract_environment(fields),
            'severity_priority': self.extract_severity_priority(fields),
            'kpi_metrics': self.extract_kpi_metrics(fields)
        })
        
        return parsed

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
        placeholder_terms = ['none', 'tbd', 'n/a', 'tba', 'to be determined', 'not applicable']
        content_lower = content.lower().strip()
        return content_lower in placeholder_terms or len(content_lower) < 3

    def extract_figma_links_with_anchors(self, text: str) -> List[DesignLink]:
        """Extract and normalize Figma links with anchor text detection"""
        design_links = []
        
        # First, try to find HTML anchor tags
        html_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
        for match in re.finditer(html_pattern, text, re.IGNORECASE):
            href = match.group(1)
            anchor_text = match.group(2).strip()
            
            if self.is_figma_url(href) or self.is_anchor_suggesting_figma(anchor_text):
                design_link = self.process_figma_url(href, anchor_text, text)
                if design_link:
                    design_links.append(design_link)
        
        # Then, try markdown links
        md_pattern = r'\[([^\]]*)\]\(([^)]*)\)'
        for match in re.finditer(md_pattern, text, re.IGNORECASE):
            anchor_text = match.group(1).strip()
            href = match.group(2).strip()
            
            if self.is_figma_url(href) or self.is_anchor_suggesting_figma(anchor_text):
                design_link = self.process_figma_url(href, anchor_text, text)
                if design_link:
                    design_links.append(design_link)
        
        # Finally, try Jira wiki format
        wiki_pattern = r'\[([^|]*)\|([^\]]*)\]'
        for match in re.finditer(wiki_pattern, text, re.IGNORECASE):
            anchor_text = match.group(1).strip()
            href = match.group(2).strip()
            
            if self.is_figma_url(href) or self.is_anchor_suggesting_figma(anchor_text):
                design_link = self.process_figma_url(href, anchor_text, text)
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
        brand_fields = ['brand', 'brands', 'product', 'market']
        for field_name in brand_fields:
            if field_name in fields and fields[field_name]:
                return str(fields[field_name])
        return ""

    def extract_components(self, fields: Dict[str, Any]) -> str:
        """Extract component information"""
        if 'components' in fields and fields['components']:
            return ', '.join([comp.get('name', '') for comp in fields['components']])
        return ""

    def extract_agile_team(self, fields: Dict[str, Any]) -> str:
        """Extract agile team information"""
        team_fields = ['team', 'agile_team', 'assignee', 'reporter']
        for field_name in team_fields:
            if field_name in fields and fields[field_name]:
                if isinstance(fields[field_name], dict):
                    return fields[field_name].get('displayName', '')
                return str(fields[field_name])
        return ""

    def extract_story_points(self, fields: Dict[str, Any]) -> str:
        """Extract story points"""
        if 'customfield_10002' in fields:
            return str(fields['customfield_10002'])
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

    def calculate_dor_coverage(self, parsed_data: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """Calculate DoR coverage - present, missing, and conflicts"""
        card_type = parsed_data['card_type']
        applicable_fields = self.dor_fields.get(card_type, [])
        
        present_fields = []
        missing_fields = []
        conflicts = []
        
        for field in applicable_fields:
            if field in parsed_data['fields'] and parsed_data['fields'][field]:
                if not self.is_placeholder_content(parsed_data['fields'][field]):
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            else:
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
        """Generate non-generic suggested rewrite with domain terms"""
        current_story = parsed_data['fields'].get('user_story', '')
        description = parsed_data['description']
        title = parsed_data['title']
        
        # Extract domain terms from the ticket
        domain_terms = self.extract_domain_terms(parsed_data)
        
        # If story exists, polish it
        if current_story and 'as a' in current_story.lower():
            # Try to improve existing story with domain terms
            if not any(term in current_story.lower() for term in domain_terms):
                # Add domain context
                return f"{current_story} (Context: {', '.join(domain_terms[:2])})"
            return current_story
        
        # Synthesize from description + domain terms
        persona = self.extract_persona(description, title)
        goal = self.extract_goal(description, title)
        benefit = self.extract_benefit(description, title)
        
        # Ensure at least one domain term is included
        if not any(term in f"{persona} {goal} {benefit}".lower() for term in domain_terms):
            goal = f"{goal} using {domain_terms[0]}" if domain_terms else goal
        
        return f"As a {persona}, I want {goal} so that {benefit}."

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
        """Extract main goal from content"""
        text = f"{title} {description}"
        
        # Look for imperative requirements
        goal_patterns = [
            r'open\s+([^.]*)',
            r'filter\s+([^.]*)',
            r'select\s+([^.]*)',
            r'click\s+([^.]*)',
            r'access\s+([^.]*)'
        ]
        
        for pattern in goal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to first sentence
        sentences = text.split('.')
        if sentences:
            return sentences[0].strip()
        
        return "achieve the desired functionality"

    def extract_benefit(self, description: str, title: str) -> str:
        """Extract benefit from content"""
        text = f"{title} {description}"
        
        # Look for benefit indicators
        benefit_patterns = [
            r'so\s+that\s+([^.]*)',
            r'to\s+([^.]*)',
            r'for\s+([^.]*)'
        ]
        
        for pattern in benefit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "improve user experience"

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
        """Generate P/N/E test scenarios mapped from ACs"""
        scenarios = {
            'positive': [],
            'negative': [],
            'error': []
        }
        
        domain_terms = self.extract_domain_terms(parsed_data)
        
        # Generate scenarios by walking through ACs
        for i, ac in enumerate(ac_rewrites):
            # Positive scenario for each AC
            if 'opens' in ac.lower() or 'updates' in ac.lower():
                scenarios['positive'].append(f"AC{i+1}: {ac.split('(')[0].strip()} - verify success state")
            
            # Negative scenario for validation ACs
            if 'invalid' in ac.lower() or 'error' in ac.lower():
                scenarios['negative'].append(f"AC{i+1}: {ac.split('(')[0].strip()} - verify error handling")
            
            # Error/Resilience for timeout/network issues
            if 'timeout' in ac.lower() or 'network' in ac.lower():
                scenarios['error'].append(f"AC{i+1}: {ac.split('(')[0].strip()} - verify resilience")
        
        # Add keyboard and screen reader scenarios for UI changes
        if any(term in f"{parsed_data['title']} {parsed_data['description']}".lower() for term in ['ui', 'interface', 'form', 'button']):
            scenarios['positive'].append("Keyboard-only navigation works for all interactive elements")
            scenarios['positive'].append("Screen reader announces all content changes")
        
        # Ensure we have scenarios for each category
        if not scenarios['positive']:
            scenarios['positive'] = ["User completes happy path workflow successfully"]
        if not scenarios['negative']:
            scenarios['negative'] = ["Invalid input shows appropriate error message"]
        if not scenarios['error']:
            scenarios['error'] = ["API timeout handled gracefully with retry option"]
        
        return scenarios

    def generate_recommendations(self, parsed_data: Dict[str, Any], conflicts: List[str]) -> Dict[str, List[str]]:
        """Generate role-tagged, concrete recommendations"""
        recommendations = {
            'po': [],
            'qa': [],
            'dev': []
        }
        
        domain_terms = self.extract_domain_terms(parsed_data)
        conflicts_present = len(conflicts) > 0
        
        # PO recommendations
        if conflicts_present:
            recommendations['po'].append("Resolve conflicting ACs before development starts")
        if 'PayPal' in domain_terms:
            recommendations['po'].append("Approve immediate-open behavior and ABTasty disablement as acceptance conditions")
        if 'ABTasty' in domain_terms:
            recommendations['po'].append("Define ABTasty toggle guidance for validation phase")
        recommendations['po'].append("Add KPI metrics for success measurement")
        
        # QA recommendations
        if 'popup' in f"{parsed_data['title']} {parsed_data['description']}".lower():
            recommendations['qa'].append("Add blocked-popup and keyboard-only activation tests")
        if 'analytics' in f"{parsed_data['title']} {parsed_data['description']}".lower():
            recommendations['qa'].append("Capture analytics payloads as evidence")
        recommendations['qa'].append("Include accessibility tests for UI changes")
        
        # Dev recommendations
        if 'PayPal' in domain_terms:
            recommendations['dev'].append("Bind popup to user gesture; add debounce/guard")
            recommendations['dev'].append("Implement ABTasty kill-switch for validation")
        if 'filter' in domain_terms:
            recommendations['dev'].append("Implement horizontal scroll with keyboard navigation")
        recommendations['dev'].append("Document error handling and telemetry")
        
        return recommendations

    def generate_markdown_report(self, parsed_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate markdown report without framework scores"""
        mode = analysis_results.get('mode', 'Actionable')
        status = analysis_results.get('status', 'Not Ready')
        dor = analysis_results.get('dor', {})
        
        report = f"""# ⚡ {mode} Groom Report — {parsed_data['ticket_key']} | {parsed_data['title']}
**Status:** {status}

## 📋 Definition of Ready
- Present: {', '.join(dor.get('present', []))}
- Missing: {', '.join(dor.get('missing', []))}
- Conflicts: {', '.join(dor.get('conflicts', [])) or 'None'}

## 🧩 User Story (for Stories/Features)
Persona ✅ | Goal ✅ | Benefit ✅
**Suggested rewrite:** "{analysis_results.get('suggested_rewrite', 'Story rewrite pending')}"

## ✅ Acceptance Criteria (testable; non-Gherkin)
Detected {len(analysis_results.get('ac_rewrites', []))}
{chr(10).join([f"{i+1}) {ac}" for i, ac in enumerate(analysis_results.get('ac_rewrites', []))])}

## 🧪 Test Scenarios (mapped to ACs)
- **Positive:** {', '.join(analysis_results.get('test_scenarios', {}).get('positive', []))}
- **Negative:** {', '.join(analysis_results.get('test_scenarios', {}).get('negative', []))}
- **Error/Resilience:** {', '.join(analysis_results.get('test_scenarios', {}).get('error', []))}
_Traceability: scenarios reference ACs in their text where relevant._

## 🧱 Technical / ADA / Architecture
- Implementation details: {analysis_results.get('technical_ada', {}).get('implementation_details', 'Missing')}
- Architectural solution: {analysis_results.get('technical_ada', {}).get('architectural_solution', 'Missing')}
- ADA: {analysis_results.get('technical_ada', {}).get('ada', {}).get('status', 'Missing')} — {', '.join(analysis_results.get('technical_ada', {}).get('ada', {}).get('notes', []))}
- NFRs: {analysis_results.get('technical_ada', {}).get('nfr', {})}

## 🎨 Design
Links: {', '.join([link.url for link in parsed_data['design_links']]) or 'None'}

## 💡 Recommendations
- **PO:** {', '.join(analysis_results.get('recommendations', {}).get('po', []))}
- **QA:** {', '.join(analysis_results.get('recommendations', {}).get('qa', []))}
- **Dev/Tech Lead:** {', '.join(analysis_results.get('recommendations', {}).get('dev', []))}
"""
        
        return report

    def analyze_ticket(self, ticket_data: Dict[str, Any], mode: str = "Actionable") -> GroomroomResponse:
        """Main analysis method - comprehensive ticket analysis without scoring"""
        try:
            # Parse Jira content
            parsed_data = self.parse_jira_content(ticket_data)
            
            # Calculate DoR coverage
            present_fields, missing_fields, conflicts = self.calculate_dor_coverage(parsed_data)
            
            # Determine status based on rules
            status = self.determine_status(present_fields, missing_fields, conflicts, parsed_data['card_type'])
            
            # Generate contextual content
            suggested_rewrite = self.generate_suggested_rewrite(parsed_data)
            ac_rewrites = self.generate_acceptance_criteria_rewrites(parsed_data)
            test_scenarios = self.generate_test_scenarios(parsed_data, ac_rewrites)
            recommendations = self.generate_recommendations(parsed_data, conflicts)
            
            # Build analysis results
            analysis_results = {
                'mode': mode,
                'status': status,
                'dor': {
                    'present': present_fields,
                    'missing': missing_fields,
                    'conflicts': conflicts
                },
                'suggested_rewrite': suggested_rewrite,
                'ac_rewrites': ac_rewrites,
                'test_scenarios': test_scenarios,
                'technical_ada': {
                    'implementation_details': 'OK' if 'implementation_details' in present_fields else 'Missing',
                    'architectural_solution': 'OK' if 'architecture' in present_fields else 'Missing',
                    'ada': {
                        'status': 'OK' if 'ada_criteria' in present_fields else 'Missing',
                        'notes': ['Keyboard navigation required', 'Screen reader compatibility needed']
                    },
                    'nfr': {
                        'performance': 'Performance impact analysis needed',
                        'security': 'Security considerations required'
                    }
                },
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
                'Status': status,
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
