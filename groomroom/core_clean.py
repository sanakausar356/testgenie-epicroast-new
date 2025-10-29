"""
Core GroomRoom Refinement Agent - AI-driven Jira ticket analysis and refinement system
"""

import os
import sys
import re
import hashlib
import json
from typing import Optional, Dict, List, Any, Tuple, Union
from dotenv import load_dotenv
from rich.console import Console
import openai
try:
    from jira_integration import JiraIntegration
    from jira_field_mapper import JiraFieldMapper
except ImportError:
    # Handle import error for Railway deployment
    JiraIntegration = None
    JiraFieldMapper = None

# Load environment variables
load_dotenv()

# Initialize Rich console for better output
console = Console()

class GroomRoom:
    """AI-driven GroomRoom Refinement Agent for comprehensive Jira ticket analysis and refinement"""
    
    def __init__(self):
        self.client = None
        self.jira_integration = None
        self.field_mapper = None
        self.setup_azure_openai()
        
        # Initialize Jira integration after Azure OpenAI to avoid blocking
        if JiraIntegration:
            try:
                self.jira_integration = JiraIntegration()
                # Initialize field mapper with Jira integration
                if JiraFieldMapper:
                    self.field_mapper = JiraFieldMapper(self.jira_integration)
                    self.field_mapper.initialize()
            except Exception as e:
                console.print(f"[yellow]Warning: Jira integration failed to initialize: {e}[/yellow]")
                self.jira_integration = None
                self.field_mapper = None
        
        # Brand abbreviations mapping
        self.brand_abbreviations = {
            'MMT': 'Marmot brand',
            'ExO': 'Exo clothing brand', 
            'YCC': 'Yankee (Global-DTC)',
            'ELF': 'PWA (Progressive Web App) for YCC and MMT only',
            'EMEA': 'Yankee brand regions only (IE, FR, IT, DE, GB)'
        }
        
        # Enhanced Framework definitions for comprehensive analysis
        self.frameworks = {
            'roi': {
                'name': 'ROI Framework',
                'elements': ['Readiness', 'Objectives', 'Implementation'],
                'description': 'Readiness / Objectives / Implementation analysis',
                'max_score': 30
            },
            'invest': {
                'name': 'INVEST Framework', 
                'elements': ['Independent', 'Negotiable', 'Valuable', 'Estimable', 'Small', 'Testable'],
                'description': 'Independent / Negotiable / Valuable / Estimable / Small / Testable',
                'max_score': 30
            },
            'accept': {
                'name': 'ACCEPT Criteria',
                'elements': ['Actionable', 'Clear', 'Complete', 'Edge-case aware', 'Precise', 'Testable'],
                'description': 'Actionable / Clear / Complete / Edge-case aware / Precise / Testable',
                'max_score': 30
            },
            '3c': {
                'name': '3C Model',
                'elements': ['Card', 'Conversation', 'Confirmation'],
                'description': 'Card → Conversation → Confirmation',
                'max_score': 10
            }
        }
        
        # Enhanced Definition of Ready (DoR) requirements with weighted scoring
        self.dor_requirements = {
            'user_story': {
                'name': 'User Story',
                'description': 'Clear persona-goal-benefit format with measurable business value',
                'required': True,
                'weight': 0.20
            },
            'acceptance_criteria': {
                'name': 'Acceptance Criteria',
                'description': 'Complete, measurable, define what (not how)',
                'required': True,
                'weight': 0.25
            },
            'testing_steps': {
                'name': 'Testing Steps',
                'description': 'Cover positive, negative, and error flows',
                'required': True,
                'weight': 0.15
            },
            'implementation_details': {
                'name': 'Implementation Details',
                'description': 'Contain PR/deployment info',
                'required': True,
                'weight': 0.10
            },
            'architectural_solution': {
                'name': 'Architectural Solution',
                'description': 'Includes design or workflow links',
                'required': True,
                'weight': 0.10
            },
            'ada_criteria': {
                'name': 'ADA Criteria',
                'description': 'Address accessibility requirements',
                'required': True,
                'weight': 0.10
            },
            'additional_fields': {
                'name': 'Additional Fields',
                'description': 'Brand(s), Component(s), Agile Team, Story Points populated',
                'required': True,
                'weight': 0.10
            }
        }
        
        # Enhanced card types with specific validation rules
        self.card_types = {
            'user_story': {
                'name': 'User Story',
                'description': 'New or enhanced functionality tied to a Feature',
                'validation_rules': [
                    'Ensure persona-goal-benefit format',
                    'Measurable business value',
                    'Feature linkage required'
                ],
                'required_fields': ['user_story', 'acceptance_criteria', 'business_value']
            },
            'bug': {
                'name': 'Bug',
                'description': 'Broken functionality tied to introducing story',
                'validation_rules': [
                    'Clear Current Behaviour',
                    'Steps to Reproduce',
                    'Expected Behaviour',
                    'Feature tie required'
                ],
                'required_fields': ['current_behavior', 'steps_to_reproduce', 'expected_behavior', 'feature_tie']
            },
            'task': {
                'name': 'Task',
                'description': 'Enabling existing config or documentation',
                'validation_rules': [
                    'Verify completion outcome',
                    'Feature linkage',
                    'Clear deliverables'
                ],
                'required_fields': ['completion_outcome', 'feature_linkage', 'deliverables']
            },
            'feature': {
                'name': 'Feature',
                'description': 'Major functionality or capability',
                'validation_rules': [
                    'Epic linkage',
                    'Business justification',
                    'Technical architecture'
                ],
                'required_fields': ['epic_linkage', 'business_justification', 'technical_architecture']
            }
        }
        
        # Sprint readiness scoring weights
        self.readiness_weights = {
            'dor_completion': 0.60,  # 60% weight for DoR completion
            'framework_quality': 0.25,  # 25% weight for framework quality
            'technical_test_coverage': 0.15  # 15% weight for technical/test coverage
        }
        
        # Sprint readiness status ranges
        self.readiness_ranges = {
            'ready': {'min': 90, 'max': 100, 'status': '✅ Ready for Dev'},
            'needs_refinement': {'min': 70, 'max': 89, 'status': '⚠️ Needs Refinement'},
            'not_ready': {'min': 0, 'max': 69, 'status': '❌ Not Ready'}
        }

    def setup_azure_openai(self):
        """Setup Azure OpenAI client with error handling"""
        try:
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            
            if not all([endpoint, api_key, deployment_name]):
                console.print("[yellow]Azure OpenAI credentials not fully configured[/yellow]")
                self.client = None
                return
                
            self.client = openai.AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-02-15-preview"
            )
            console.print("[green]✅ Azure OpenAI client initialized successfully[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize Azure OpenAI client: {e}[/red]")
            self.client = None

    def _format_field_names(self, field_keys: List[str]) -> str:
        """Convert field keys to human-readable labels"""
        if not field_keys:
            return 'None'
        
        readable_names = []
        for key in field_keys:
            # Use the 'name' from dor_requirements if available
            if key in self.dor_requirements:
                readable_names.append(self.dor_requirements[key]['name'])
            else:
                # Fallback: convert underscores to spaces and title case
                readable_names.append(key.replace('_', ' ').title())
        
        return ', '.join(readable_names)

    def detect_card_type(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-detect card type and apply refinement rules"""
        issue_type = issue_data.get('issue_type', '').lower()
        summary = issue_data.get('summary', '').lower()
        description = issue_data.get('description', '').lower()
        
        # Detection logic based on issue type and content
        if 'bug' in issue_type or 'defect' in issue_type:
            detected_type = 'bug'
        elif 'story' in issue_type or 'user story' in issue_type:
            detected_type = 'user_story'
        elif 'task' in issue_type:
            detected_type = 'task'
        elif 'feature' in issue_type or 'epic' in issue_type:
            detected_type = 'feature'
        else:
            # Content-based detection
            if any(keyword in summary + description for keyword in ['as a', 'i want', 'so that']):
                detected_type = 'user_story'
            elif any(keyword in summary + description for keyword in ['bug', 'error', 'broken', 'not working']):
                detected_type = 'bug'
            elif any(keyword in summary + description for keyword in ['task', 'config', 'documentation']):
                detected_type = 'task'
            else:
                detected_type = 'user_story'  # Default fallback
        
        card_type_info = self.card_types.get(detected_type, self.card_types['user_story'])
        
        return {
            'detected_type': detected_type,
            'type_name': card_type_info['name'],
            'description': card_type_info['description'],
            'validation_rules': card_type_info['validation_rules'],
            'required_fields': card_type_info['required_fields']
        }

    def analyze_story(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect persona-goal-benefit and suggest clearer rewrite"""
        description = issue_data.get('description', '')
        summary = issue_data.get('summary', '')
        
        # Look for user story patterns
        user_story_patterns = [
            r'as\s+(?:a\s+)?([^,]+),\s*i\s+want\s+([^,]+),\s*so\s+that\s+(.+)',
            r'as\s+(?:a\s+)?([^,]+),\s*i\s+need\s+([^,]+),\s*so\s+that\s+(.+)',
            r'as\s+(?:a\s+)?([^,]+),\s*i\s+should\s+be\s+able\s+to\s+([^,]+),\s*so\s+that\s+(.+)'
        ]
        
        detected_persona = None
        detected_goal = None
        detected_benefit = None
        story_quality_score = 0
        
        for pattern in user_story_patterns:
            match = re.search(pattern, description + ' ' + summary, re.IGNORECASE)
            if match:
                detected_persona = match.group(1).strip()
                detected_goal = match.group(2).strip()
                detected_benefit = match.group(3).strip()
                story_quality_score = 80  # Good structure found
                break
        
        # If no clear pattern found, analyze content for components
        if not detected_persona:
            story_quality_score = 20
            # Try to extract components from content
            content = description + ' ' + summary
            
            # Look for persona indicators
            persona_indicators = ['user', 'customer', 'admin', 'developer', 'tester', 'manager']
            for indicator in persona_indicators:
                if indicator in content.lower():
                    detected_persona = indicator
                    break
            
            # Look for goal indicators
            goal_indicators = ['want', 'need', 'should', 'able to', 'can']
            for indicator in goal_indicators:
                if indicator in content.lower():
                    detected_goal = content[:100] + '...' if len(content) > 100 else content
                    break
            
            # Look for benefit indicators
            benefit_indicators = ['so that', 'in order to', 'because', 'to']
            for indicator in benefit_indicators:
                if indicator in content.lower():
                    detected_benefit = content[:100] + '...' if len(content) > 100 else content
                    break
        
        # Generate story rewrite if needed
        story_rewrite = None
        if story_quality_score < 70 and self.client:
            story_rewrite = self._generate_story_rewrite(description, summary, detected_persona, detected_goal, detected_benefit)
        
        return {
            'detected_persona': detected_persona,
            'detected_goal': detected_goal,
            'detected_benefit': detected_benefit,
            'story_quality_score': story_quality_score,
            'story_rewrite': story_rewrite,
            'has_clear_structure': story_quality_score >= 70
        }

    def audit_acceptance_criteria(self, acceptance_criteria: List[str]) -> Dict[str, Any]:
        """Detect vague, missing, or non-testable ACs and rewrite them"""
        if not acceptance_criteria:
            return {
                'detected': 0,
                'weak': 0,
                'suggested_rewrite': [],
                'coverage_analysis': 'No acceptance criteria found'
            }
        
        ac_analysis = []
        weak_count = 0
        
        for ac in acceptance_criteria:
            if not ac.strip():
                continue
                
            # Analyze AC quality
            quality_score = self._analyze_ac_quality(ac)
            is_weak = quality_score < 60
            
            if is_weak:
                weak_count += 1
            
            # Generate rewrite if weak
            suggested_rewrite = None
            if is_weak and self.client:
                suggested_rewrite = self._generate_ac_rewrite(ac)
            
            ac_analysis.append({
                'original': ac.strip(),
                'quality_score': quality_score,
                'is_weak': is_weak,
                'suggested_rewrite': suggested_rewrite,
                'issues': self._identify_ac_issues(ac)
            })
        
        # Generate additional ACs if coverage is poor
        additional_acs = []
        if len(acceptance_criteria) < 3 and self.client:
            additional_acs = self._generate_additional_acs(acceptance_criteria)
        
        return {
            'detected': len(acceptance_criteria),
            'weak': weak_count,
            'suggested_rewrite': [ac['suggested_rewrite'] for ac in ac_analysis if ac['suggested_rewrite']],
            'coverage_analysis': f"Found {len(acceptance_criteria)} ACs, {weak_count} need improvement",
            'detailed_analysis': ac_analysis,
            'additional_suggestions': additional_acs
        }

    def generate_test_scenarios(self, issue_data: Dict[str, Any]) -> List[str]:
        """Generate Positive, Negative, and Error test scenarios"""
        summary = issue_data.get('summary', '')
        description = issue_data.get('description', '')
        acceptance_criteria = issue_data.get('acceptance_criteria', [])
        
        test_scenarios = []
        
        if self.client:
            # Generate comprehensive test scenarios using AI
            test_scenarios = self._generate_ai_test_scenarios(summary, description, acceptance_criteria)
        else:
            # Fallback to rule-based generation
            test_scenarios = self._generate_rule_based_test_scenarios(summary, description, acceptance_criteria)
        
        return test_scenarios

    def audit_bug(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Current Behaviour, Steps to Reproduce, Expected Behaviour completeness"""
        description = issue_data.get('description', '')
        summary = issue_data.get('summary', '')
        content = description + ' ' + summary
        
        # Look for bug report components
        current_behavior = self._extract_bug_component(content, ['current behavior', 'current behaviour', 'what happens', 'actual behavior'])
        steps_to_reproduce = self._extract_bug_component(content, ['steps to reproduce', 'reproduction steps', 'how to reproduce', 'steps'])
        expected_behavior = self._extract_bug_component(content, ['expected behavior', 'expected behaviour', 'should happen', 'expected result'])
        
        # Calculate completeness score
        components_found = sum([
            bool(current_behavior),
            bool(steps_to_reproduce),
            bool(expected_behavior)
        ])
        completeness_score = (components_found / 3) * 100
        
        # Generate suggestions for missing components
        suggestions = []
        if not current_behavior:
            suggestions.append("Add clear description of current behavior")
        if not steps_to_reproduce:
            suggestions.append("Add step-by-step reproduction instructions")
        if not expected_behavior:
            suggestions.append("Add description of expected behavior")
        
        return {
            'current_behavior': current_behavior,
            'steps_to_reproduce': steps_to_reproduce,
            'expected_behavior': expected_behavior,
            'completeness_score': completeness_score,
            'is_complete': completeness_score >= 80,
            'suggestions': suggestions
        }

    def calculate_readiness(self, dor_analysis: Dict, framework_scores: Dict, technical_coverage: float) -> Dict[str, Any]:
        """Calculate Sprint Readiness Score (0-100%) with weighted scoring"""
        # Calculate DoR completion score
        dor_score = dor_analysis.get('coverage_percentage', 0)
        
        # Calculate framework quality score
        framework_score = sum(framework_scores.values()) / len(framework_scores) if framework_scores else 0
        
        # Calculate weighted total
        total_score = (
            dor_score * self.readiness_weights['dor_completion'] +
            framework_score * self.readiness_weights['framework_quality'] +
            technical_coverage * self.readiness_weights['technical_test_coverage']
        )
        
        # Determine status
        status_info = None
        for range_name, range_info in self.readiness_ranges.items():
            if range_info['min'] <= total_score <= range_info['max']:
                status_info = range_info
                break
        
        return {
            'score': round(total_score, 1),
            'status': status_info['status'] if status_info else '❌ Not Ready',
            'dor_score': dor_score,
            'framework_score': framework_score,
            'technical_score': technical_coverage,
            'breakdown': {
                'dor_weighted': dor_score * self.readiness_weights['dor_completion'],
                'framework_weighted': framework_score * self.readiness_weights['framework_quality'],
                'technical_weighted': technical_coverage * self.readiness_weights['technical_test_coverage']
            }
        }

    def _get_field_value(self, issue_fields: Dict, field_name: str) -> Any:
        """Get field value using dynamic field mapping"""
        if self.field_mapper:
            return self.field_mapper.get_field_value(issue_fields, field_name)
        else:
            # Fallback to hardcoded field IDs
            fallback_fields = {
                'Acceptance Criteria': 'customfield_10017',
                'Test Scenarios': 'customfield_10018', 
                'Story Points': 'customfield_10016',
                'Agile Team': 'customfield_10020'
            }
            field_id = fallback_fields.get(field_name)
            return issue_fields.get(field_id) if field_id else None

    def _analyze_ac_quality(self, ac: str) -> int:
        """Analyze acceptance criteria quality and return score (0-100)"""
        score = 0
        
        # Check for clarity indicators
        if len(ac.strip()) > 20:
            score += 20
        
        # Check for testability indicators
        testable_words = ['verify', 'check', 'confirm', 'validate', 'ensure', 'should', 'must', 'will']
        if any(word in ac.lower() for word in testable_words):
            score += 25
        
        # Check for specificity (avoid vague words)
        vague_words = ['good', 'nice', 'better', 'improved', 'enhanced', 'user-friendly']
        if not any(word in ac.lower() for word in vague_words):
            score += 20
        
        # Check for business intent vs technical solution
        technical_words = ['click', 'button', 'api', 'database', 'code', 'function']
        if not any(word in ac.lower() for word in technical_words):
            score += 15
        
        # Check for measurable outcomes
        measurable_words = ['display', 'show', 'appear', 'contain', 'include', 'have']
        if any(word in ac.lower() for word in measurable_words):
            score += 20
        
        return min(score, 100)

    def _identify_ac_issues(self, ac: str) -> List[str]:
        """Identify specific issues with acceptance criteria"""
        issues = []
        
        if len(ac.strip()) < 20:
            issues.append("Too short - needs more detail")
        
        if not any(word in ac.lower() for word in ['verify', 'check', 'confirm', 'validate', 'ensure']):
            issues.append("Not clearly testable")
        
        if any(word in ac.lower() for word in ['good', 'nice', 'better', 'improved']):
            issues.append("Contains vague language")
        
        if any(word in ac.lower() for word in ['click', 'button', 'api', 'database']):
            issues.append("Focuses on how rather than what")
        
        return issues

    def _generate_story_rewrite(self, description: str, summary: str, persona: str, goal: str, benefit: str) -> str:
        """Generate a clearer user story rewrite using AI"""
        if not self.client:
            return "Azure OpenAI not available for story rewrite"
        
        try:
            prompt = f"""Rewrite this user story to be clear and business-ready:

Original Summary: {summary}
Original Description: {description}

Detected Components:
- Persona: {persona or 'Not detected'}
- Goal: {goal or 'Not detected'}  
- Benefit: {benefit or 'Not detected'}

Provide a single, improved user story in the format: "As a [persona], I want [goal], so that [benefit]"
Focus on clarity, business value, and measurability."""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating story rewrite: {str(e)}"

    def _generate_ac_rewrite(self, ac: str) -> str:
        """Generate rewritten acceptance criteria using AI"""
        if not self.client:
            return "Azure OpenAI not available for AC rewrite"
        
        try:
            prompt = f"""Rewrite this acceptance criteria to be clear, testable, and business-ready:

Original: "{ac}"

Requirements:
1. Clear intent (what, not how)
2. Measurable outcomes
3. Business value focus
4. Testable format

Provide a single, improved acceptance criteria:"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating AC rewrite: {str(e)}"

    def _generate_additional_acs(self, existing_acs: List[str]) -> List[str]:
        """Generate additional acceptance criteria suggestions"""
        if not self.client:
            return []
        
        try:
            prompt = f"""Based on these existing acceptance criteria, suggest 2-3 additional ones that might be missing:

Existing ACs: {existing_acs}

Focus on:
1. Edge cases
2. Error handling
3. Accessibility
4. Performance
5. Security

Provide 2-3 additional acceptance criteria:"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse response into list
            content = response.choices[0].message.content.strip()
            return [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith(('1.', '2.', '3.', '-', '*'))]
            
        except Exception as e:
            return []

    def _generate_ai_test_scenarios(self, summary: str, description: str, acceptance_criteria: List[str]) -> List[str]:
        """Generate comprehensive test scenarios using AI"""
        try:
            prompt = f"""Generate test scenarios for this ticket:

Summary: {summary}
Description: {description}
Acceptance Criteria: {acceptance_criteria}

Provide 3-5 test scenarios covering:
1. Positive (Happy Path) scenarios
2. Negative (Error/Edge cases) scenarios  
3. Error handling scenarios

Format each as: "Type: Description" (e.g., "Positive: Verify user can login with valid credentials")"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            return [line.strip() for line in content.split('\n') if line.strip()]
            
        except Exception as e:
            return self._generate_rule_based_test_scenarios(summary, description, acceptance_criteria)

    def _generate_rule_based_test_scenarios(self, summary: str, description: str, acceptance_criteria: List[str]) -> List[str]:
        """Generate test scenarios using rule-based approach"""
        scenarios = []
        
        # Positive scenarios
        scenarios.append(f"Positive: Verify main functionality works as expected for {summary}")
        
        # Negative scenarios
        scenarios.append(f"Negative: Verify error handling when invalid input is provided")
        scenarios.append(f"Negative: Verify system behavior with edge case data")
        
        # Error scenarios
        scenarios.append(f"Error: Verify system handles API failures gracefully")
        scenarios.append(f"Error: Verify user receives appropriate error messages")
        
        return scenarios

    def _extract_bug_component(self, content: str, keywords: List[str]) -> Optional[str]:
        """Extract bug report component based on keywords"""
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in content_lower:
                # Find the section after the keyword
                start_idx = content_lower.find(keyword)
                if start_idx != -1:
                    # Extract text after keyword until next section or end
                    section_start = start_idx + len(keyword)
                    section_text = content[section_start:section_start + 200].strip()
                    
                    # Clean up the text
                    section_text = re.sub(r'^[:\-\s]+', '', section_text)
                    if section_text:
                        return section_text[:150] + '...' if len(section_text) > 150 else section_text
        
        return None

    def analyze_frameworks(self, issue_data: Dict[str, Any]) -> Dict[str, int]:
        """Analyze and score ROI, INVEST, ACCEPT, and 3C frameworks"""
        content = f"{issue_data.get('summary', '')} {issue_data.get('description', '')}"
        acceptance_criteria = issue_data.get('acceptance_criteria', [])
        
        framework_scores = {}
        
        for framework_key, framework_info in self.frameworks.items():
            elements = framework_info['elements']
            max_score = framework_info['max_score']
            found_elements = []
            
            for element in elements:
                if self._check_framework_element(element, content, acceptance_criteria, framework_key):
                    found_elements.append(element)
            
            # Calculate score based on found elements
            element_score = (len(found_elements) / len(elements)) * max_score
            framework_scores[framework_key.upper()] = round(element_score, 1)
        
        return framework_scores

    def _check_framework_element(self, element: str, content: str, acceptance_criteria: List[str], framework_key: str) -> bool:
        """Check if a framework element is present in the content"""
        content_lower = content.lower()
        ac_text = ' '.join(acceptance_criteria).lower()
        combined_text = content_lower + ' ' + ac_text
        
        # Framework-specific element checking
        if framework_key == 'roi':
            return self._check_roi_element(element, combined_text)
        elif framework_key == 'invest':
            return self._check_invest_element(element, combined_text)
        elif framework_key == 'accept':
            return self._check_accept_element(element, combined_text, acceptance_criteria)
        elif framework_key == '3c':
            return self._check_3c_element(element, combined_text)
        
        return False

    def _check_roi_element(self, element: str, content: str) -> bool:
        """Check ROI framework elements"""
        roi_indicators = {
            'readiness': ['ready', 'complete', 'defined', 'clear', 'prepared'],
            'objectives': ['goal', 'objective', 'purpose', 'aim', 'target'],
            'implementation': ['implement', 'develop', 'build', 'create', 'deliver']
        }
        
        indicators = roi_indicators.get(element.lower(), [])
        return any(indicator in content for indicator in indicators)

    def _check_invest_element(self, element: str, content: str) -> bool:
        """Check INVEST framework elements"""
        invest_indicators = {
            'independent': ['standalone', 'independent', 'separate', 'isolated'],
            'negotiable': ['flexible', 'negotiable', 'adjustable', 'modifiable'],
            'valuable': ['value', 'benefit', 'worth', 'important', 'useful'],
            'estimable': ['estimate', 'size', 'effort', 'complexity', 'points'],
            'small': ['small', 'manageable', 'focused', 'specific'],
            'testable': ['test', 'verify', 'validate', 'check', 'confirm']
        }
        
        indicators = invest_indicators.get(element.lower(), [])
        return any(indicator in content for indicator in indicators)

    def _check_accept_element(self, element: str, content: str, acceptance_criteria: List[str]) -> bool:
        """Check ACCEPT framework elements"""
        if element.lower() == 'testable':
            return len(acceptance_criteria) > 0 and any('verify' in ac.lower() or 'check' in ac.lower() for ac in acceptance_criteria)
        
        accept_indicators = {
            'actionable': ['action', 'do', 'perform', 'execute', 'complete'],
            'clear': ['clear', 'specific', 'defined', 'explicit'],
            'complete': ['complete', 'comprehensive', 'full', 'entire'],
            'edge-case aware': ['edge', 'exception', 'error', 'boundary', 'limit'],
            'precise': ['precise', 'exact', 'specific', 'detailed']
        }
        
        indicators = accept_indicators.get(element.lower(), [])
        return any(indicator in content for indicator in indicators)

    def _check_3c_element(self, element: str, content: str) -> bool:
        """Check 3C framework elements"""
        c3_indicators = {
            'card': ['card', 'ticket', 'story', 'task', 'issue'],
            'conversation': ['discuss', 'talk', 'meeting', 'review', 'refinement'],
            'confirmation': ['confirm', 'verify', 'accept', 'approve', 'sign-off']
        }
        
        indicators = c3_indicators.get(element.lower(), [])
        return any(indicator in content for indicator in indicators)

    def analyze_dor_requirements_enhanced(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced DoR analysis with weighted scoring"""
        dor_analysis = {
            'coverage_percentage': 0,
            'missing_fields': [],
            'present_fields': [],
            'detailed_analysis': {},
            'weighted_score': 0
        }
        
        total_weight = 0
        weighted_score = 0
        
        for req_key, req_info in self.dor_requirements.items():
            is_present = self._check_dor_requirement(req_key, issue_data)
            weight = req_info['weight']
            
            dor_analysis['detailed_analysis'][req_key] = {
                'name': req_info['name'],
                'description': req_info['description'],
                'required': req_info['required'],
                'weight': weight,
                'present': is_present,
                'score': weight if is_present else 0
            }
            
            if is_present:
                dor_analysis['present_fields'].append(req_info['name'])
                weighted_score += weight
            else:
                dor_analysis['missing_fields'].append(req_info['name'])
            
            total_weight += weight
        
        dor_analysis['coverage_percentage'] = (len(dor_analysis['present_fields']) / len(self.dor_requirements)) * 100
        dor_analysis['weighted_score'] = (weighted_score / total_weight) * 100 if total_weight > 0 else 0
        
        return dor_analysis

    def _check_dor_requirement(self, req_key: str, issue_data: Dict[str, Any]) -> bool:
        """Check if a specific DoR requirement is met"""
        if req_key == 'user_story':
            return self._check_user_story_requirement(issue_data)
        elif req_key == 'acceptance_criteria':
            return len(issue_data.get('acceptance_criteria', [])) > 0
        elif req_key == 'testing_steps':
            return len(issue_data.get('test_scenarios', [])) > 0
        elif req_key == 'implementation_details':
            return self._check_implementation_details(issue_data)
        elif req_key == 'architectural_solution':
            return self._check_architectural_solution(issue_data)
        elif req_key == 'ada_criteria':
            return self._check_ada_criteria(issue_data)
        elif req_key == 'additional_fields':
            return self._check_additional_fields(issue_data)
        
        return False

    def _check_user_story_requirement(self, issue_data: Dict[str, Any]) -> bool:
        """Check if user story requirement is met"""
        description = issue_data.get('description', '').lower()
        summary = issue_data.get('summary', '').lower()
        content = description + ' ' + summary
        
        # Check for user story format
        story_patterns = [
            r'as\s+(?:a\s+)?[^,]+,\s*i\s+want\s+[^,]+,\s*so\s+that\s+.+',
            r'as\s+(?:a\s+)?[^,]+,\s*i\s+need\s+[^,]+,\s*so\s+that\s+.+'
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in story_patterns)

    def _check_implementation_details(self, issue_data: Dict[str, Any]) -> bool:
        """Check if implementation details are present"""
        description = issue_data.get('description', '').lower()
        comments = issue_data.get('comments', [])
        
        # Check for PR/deployment info
        implementation_indicators = ['pr', 'pull request', 'deploy', 'deployment', 'implementation', 'technical']
        
        if any(indicator in description for indicator in implementation_indicators):
            return True
        
        # Check comments for implementation details
        for comment in comments:
            comment_text = comment.get('body', '').lower()
            if any(indicator in comment_text for indicator in implementation_indicators):
                return True
        
        return False

    def _check_architectural_solution(self, issue_data: Dict[str, Any]) -> bool:
        """Check if architectural solution is present"""
        description = issue_data.get('description', '').lower()
        figma_links = issue_data.get('figma_links', [])
        
        # Check for design/architecture links
        if figma_links:
            return True
        
        # Check for architecture keywords
        architecture_indicators = ['design', 'architecture', 'workflow', 'diagram', 'figma', 'mockup']
        return any(indicator in description for indicator in architecture_indicators)

    def _check_ada_criteria(self, issue_data: Dict[str, Any]) -> bool:
        """Check if ADA criteria are present"""
        description = issue_data.get('description', '').lower()
        acceptance_criteria = issue_data.get('acceptance_criteria', [])
        
        # Check for accessibility keywords
        ada_indicators = ['accessibility', 'ada', 'wcag', 'screen reader', 'keyboard', 'aria']
        
        if any(indicator in description for indicator in ada_indicators):
            return True
        
        # Check acceptance criteria for accessibility
        for ac in acceptance_criteria:
            if any(indicator in ac.lower() for indicator in ada_indicators):
                return True
        
        return False

    def _check_additional_fields(self, issue_data: Dict[str, Any]) -> bool:
        """Check if additional fields are populated"""
        required_fields = ['labels', 'components', 'agile_team', 'story_points']
        present_count = 0
        
        for field in required_fields:
            if issue_data.get(field):
                present_count += 1
        
        # At least 3 of 4 fields should be present
        return present_count >= 3

    def analyze_ticket(self, jira_issue_or_content: Union[Dict, str], mode: str = "actionable") -> Dict[str, Any]:
        """Main analysis pipeline for comprehensive ticket refinement"""
        try:
            # Handle input - either Jira issue dict or content string
            if isinstance(jira_issue_or_content, str):
                if re.match(r'^[A-Z]+-\d+$', jira_issue_or_content.strip()):
                    # It's a ticket number, fetch from Jira
                    if not self.jira_integration:
                        return {"error": "Jira integration not available"}
                    
                    jira_issue = self.jira_integration.get_ticket_info(jira_issue_or_content.strip())
                    if not jira_issue:
                        return {"error": f"Could not fetch ticket {jira_issue_or_content}"}
                else:
                    # It's content, create minimal issue data
                    jira_issue = {
                        'key': 'PASTED-CONTENT',
                        'fields': {
                            'summary': 'Pasted Content Analysis',
                            'description': jira_issue_or_content,
                            'issuetype': {'name': 'Unknown'},
                            'status': {'name': 'Unknown'},
                            'priority': {'name': 'None'},
                            'assignee': None,
                            'reporter': None,
                            'created': '',
                            'updated': '',
                            'project': {'name': 'Unknown'},
                            'labels': [],
                            'components': []
                        }
                    }
            else:
                jira_issue = jira_issue_or_content
            
            # Extract issue data
            issue_data = self.extract_jira_fields(jira_issue)
            
            # Detect card type
            card_type_analysis = self.detect_card_type(issue_data)
            
            # Analyze story structure
            story_analysis = self.analyze_story(issue_data)
            
            # Audit acceptance criteria
            ac_audit = self.audit_acceptance_criteria(issue_data.get('acceptance_criteria', []))
            
            # Generate test scenarios
            test_scenarios = self.generate_test_scenarios(issue_data)
            
            # Audit bug (if applicable)
            bug_audit = None
            if card_type_analysis['detected_type'] == 'bug':
                bug_audit = self.audit_bug(issue_data)
            
            # Analyze frameworks
            framework_scores = self.analyze_frameworks(issue_data)
            
            # Enhanced DoR analysis
            dor_analysis = self.analyze_dor_requirements_enhanced(issue_data)
            
            # Calculate technical coverage
            technical_coverage = self._calculate_technical_coverage(issue_data, test_scenarios)
            
            # Calculate sprint readiness
            readiness_analysis = self.calculate_readiness(dor_analysis, framework_scores, technical_coverage)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(dor_analysis, ac_audit, test_scenarios, bug_audit, framework_scores)
            
            # Build structured output
            output = {
                "TicketKey": issue_data.get('key', ''),
                "Type": card_type_analysis['type_name'],
                "SprintReadiness": readiness_analysis['score'],
                "DefinitionOfReady": {
                    "CoveragePercent": dor_analysis['coverage_percentage'],
                    "MissingFields": dor_analysis['missing_fields']
                },
                "FrameworkScores": framework_scores,
                "StoryRewrite": story_analysis.get('story_rewrite'),
                "AcceptanceCriteriaAudit": {
                    "Detected": ac_audit['detected'],
                    "Weak": ac_audit['weak'],
                    "SuggestedRewrite": ac_audit['suggested_rewrite']
                },
                "SuggestedTestScenarios": test_scenarios,
                "Recommendations": recommendations,
                "CardTypeAnalysis": card_type_analysis,
                "StoryAnalysis": story_analysis,
                "BugAudit": bug_audit,
                "DetailedAnalysis": {
                    "DOR": dor_analysis,
                    "FrameworkScores": framework_scores,
                    "Readiness": readiness_analysis,
                    "TechnicalCoverage": technical_coverage
                }
            }
            
            # Add mode-specific formatting
            if mode in ["strict", "light", "insight", "deepdive", "actionable"]:
                output = self._format_output_by_mode(output, mode)
            
            return output
            
        except Exception as e:
            console.print(f"[red]Error in ticket analysis: {e}[/red]")
            return {"error": str(e)}

    def _calculate_technical_coverage(self, issue_data: Dict[str, Any], test_scenarios: List[str]) -> float:
        """Calculate technical and test coverage score"""
        score = 0
        
        # Test scenarios coverage (40%)
        if len(test_scenarios) >= 3:
            score += 40
        elif len(test_scenarios) >= 1:
            score += 20
        
        # Implementation details (30%)
        if self._check_implementation_details(issue_data):
            score += 30
        
        # Architectural solution (20%)
        if self._check_architectural_solution(issue_data):
            score += 20
        
        # ADA criteria (10%)
        if self._check_ada_criteria(issue_data):
            score += 10
        
        return min(score, 100)

    def _generate_recommendations(self, dor_analysis: Dict, ac_audit: Dict, test_scenarios: List[str], 
                                bug_audit: Optional[Dict], framework_scores: Dict) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # DoR recommendations
        missing_fields = dor_analysis.get('missing_fields', [])
        for field in missing_fields[:3]:  # Top 3 missing fields
            recommendations.append(f"Add {field}")
        
        # AC recommendations
        if ac_audit['weak'] > 0:
            recommendations.append(f"Improve {ac_audit['weak']} weak acceptance criteria")
        
        # Test scenario recommendations
        if len(test_scenarios) < 3:
            recommendations.append("Add more comprehensive test scenarios")
        
        # Bug-specific recommendations
        if bug_audit and not bug_audit['is_complete']:
            recommendations.extend(bug_audit['suggestions'][:2])
        
        # Framework recommendations
        low_frameworks = [name for name, score in framework_scores.items() if score < 20]
        if low_frameworks:
            recommendations.append(f"Improve {', '.join(low_frameworks)} framework alignment")
        
        return recommendations[:5]  # Limit to top 5

    def _format_output_by_mode(self, output: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Format output based on analysis mode"""
        if mode == "strict":
            # Pass/fail DoR checks only
            return {
                "TicketKey": output["TicketKey"],
                "Type": output["Type"],
                "SprintReadiness": output["SprintReadiness"],
                "DoRPass": output["SprintReadiness"] >= 90,
                "CriticalGaps": output["DefinitionOfReady"]["MissingFields"][:3]
            }
        
        elif mode == "light":
            # Only critical gaps
            return {
                "TicketKey": output["TicketKey"],
                "Type": output["Type"],
                "SprintReadiness": output["SprintReadiness"],
                "CriticalGaps": output["DefinitionOfReady"]["MissingFields"][:3],
                "TopRecommendations": output["Recommendations"][:3]
            }
        
        elif mode == "insight":
            # Include rationale
            return {
                **output,
                "Insights": {
                    "ReadinessBreakdown": output["DetailedAnalysis"]["Readiness"]["breakdown"],
                    "FrameworkAnalysis": output["FrameworkScores"],
                    "QualityAssessment": f"Story quality: {output['StoryAnalysis']['story_quality_score']}/100"
                }
            }
        
        elif mode == "deepdive":
            # Full diagnostics
            return output
        
        elif mode == "actionable":
            # Focus on rewrites and actions
            return {
                "TicketKey": output["TicketKey"],
                "Type": output["Type"],
                "SprintReadiness": output["SprintReadiness"],
                "StoryRewrite": output["StoryRewrite"],
                "AcceptanceCriteriaAudit": output["AcceptanceCriteriaAudit"],
                "SuggestedTestScenarios": output["SuggestedTestScenarios"],
                "Recommendations": output["Recommendations"],
                "NextActions": self._generate_next_actions(output)
            }
        
        return output

    def _generate_next_actions(self, output: Dict[str, Any]) -> List[str]:
        """Generate specific next actions with owners"""
        actions = []
        
        # High priority actions
        if output["SprintReadiness"] < 70:
            actions.append("PO: Complete missing DoR requirements")
        
        if output["AcceptanceCriteriaAudit"]["Weak"] > 0:
            actions.append("PO: Rewrite weak acceptance criteria")
        
        if len(output["SuggestedTestScenarios"]) < 3:
            actions.append("QA: Define comprehensive test scenarios")
        
        # Technical actions
        missing_fields = output["DefinitionOfReady"]["MissingFields"]
        if "Implementation Details" in missing_fields:
            actions.append("Dev: Add implementation and deployment details")
        
        if "Architectural Solution" in missing_fields:
            actions.append("Architect: Provide design or workflow links")
        
        return actions

    def summarize_output(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary for batch analysis"""
        total_analyzed = len(analysis_results)
        ready_count = sum(1 for result in analysis_results if result.get("SprintReadiness", 0) >= 90)
        needs_refinement_count = sum(1 for result in analysis_results if 70 <= result.get("SprintReadiness", 0) < 90)
        not_ready_count = total_analyzed - ready_count - needs_refinement_count
        
        # Common issues
        all_missing_fields = []
        for result in analysis_results:
            all_missing_fields.extend(result.get("DefinitionOfReady", {}).get("MissingFields", []))
        
        common_issues = {}
        for field in all_missing_fields:
            common_issues[field] = common_issues.get(field, 0) + 1
        
        top_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "Summary": f"{total_analyzed} analyzed – {ready_count} Ready, {needs_refinement_count} Need Refinement, {not_ready_count} Not Ready",
            "ReadyCount": ready_count,
            "NeedsRefinementCount": needs_refinement_count,
            "NotReadyCount": not_ready_count,
            "TopIssues": [{"field": field, "count": count} for field, count in top_issues],
            "AverageReadiness": sum(result.get("SprintReadiness", 0) for result in analysis_results) / total_analyzed if total_analyzed > 0 else 0
        }

    def extract_jira_fields(self, jira_issue: Dict) -> Dict[str, Any]:
        """Extract all relevant fields from Jira issue dynamically"""
        try:
            fields = jira_issue.get('fields', {})
            
            # Extract basic fields
            issue_data = {
                'key': jira_issue.get('key', ''),
                'summary': fields.get('summary', ''),
                'description': self._extract_description(fields.get('description')),
                'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                'status': fields.get('status', {}).get('name', 'Unknown'),
                'priority': fields.get('priority', {}).get('name', 'None'),
                'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                'reporter': fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown',
                'created': fields.get('created', ''),
                'updated': fields.get('updated', ''),
                'project': fields.get('project', {}).get('name', 'Unknown'),
                'labels': fields.get('labels', []),
                'components': [comp.get('name', '') for comp in fields.get('components', [])],
                'story_points': self._get_field_value(fields, 'Story Points'),
                'acceptance_criteria': self._extract_acceptance_criteria(fields),
                'test_scenarios': self._extract_test_scenarios(fields),
                'figma_links': self._extract_figma_links(fields),
                'attachments': self._extract_attachments(fields),
                'linked_issues': self._extract_linked_issues(fields),
                'comments': self._extract_comments(fields),
                'agile_team': self._get_field_value(fields, 'Agile Team') or self._extract_agile_team(fields),
                'dependencies': self._extract_dependencies(fields)
            }
            
            return issue_data
            
        except Exception as e:
            console.print(f"[red]Error extracting Jira fields: {e}[/red]")
            return {}

    def _extract_description(self, description_field) -> str:
        """Safely extract description from various formats"""
        if description_field is None:
            return ''
        elif isinstance(description_field, dict):
            # Handle Atlassian Document Format
            if 'content' in description_field:
                content_parts = []
                for content_item in description_field.get('content', []):
                    if content_item.get('type') == 'paragraph':
                        for text_item in content_item.get('content', []):
                            if text_item.get('type') == 'text':
                                content_parts.append(text_item.get('text', ''))
                return ' '.join(content_parts) if content_parts else ''
            else:
                return str(description_field)
        else:
            return str(description_field)

    def _extract_acceptance_criteria(self, fields: Dict) -> List[str]:
        """Extract acceptance criteria from various possible fields"""
        ac_list = []
        
        # Try dynamic field mapping first
        ac_value = self._get_field_value(fields, 'Acceptance Criteria')
        if ac_value:
            if isinstance(ac_value, str) and ac_value.strip():
                ac_list.append(ac_value.strip())
            elif isinstance(ac_value, list):
                ac_list.extend([str(item).strip() for item in ac_value if str(item).strip()])
        
        # Fallback: Check custom fields for AC
        if not ac_list:
            for key, value in fields.items():
                if 'acceptance' in key.lower() or 'criteria' in key.lower():
                    if isinstance(value, str) and value.strip():
                        ac_list.append(value.strip())
                    elif isinstance(value, list):
                        ac_list.extend([str(item).strip() for item in value if str(item).strip()])
        
        # Check description for AC patterns
        description = self._extract_description(fields.get('description'))
        if description:
            # Look for AC patterns in description
            ac_patterns = [
                r'Acceptance Criteria[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
                r'AC[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)',
                r'Given.*?When.*?Then.*?(?=\n\n|\n[A-Z]|$)',
            ]
            
            for pattern in ac_patterns:
                matches = re.findall(pattern, description, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    if match.strip():
                        ac_list.append(match.strip())
        
        return list(set(ac_list))  # Remove duplicates

    def _extract_test_scenarios(self, fields: Dict) -> List[str]:
        """Extract test scenarios from various possible fields"""
        test_list = []
        
        # Try dynamic field mapping first
        test_value = self._get_field_value(fields, 'Test Scenarios')
        if test_value:
            if isinstance(test_value, str) and test_value.strip():
                test_list.append(test_value.strip())
            elif isinstance(test_value, list):
                test_list.extend([str(item).strip() for item in test_value if str(item).strip()])
        
        # Fallback: Check custom fields for test scenarios
        if not test_list:
            for key, value in fields.items():
                if 'test' in key.lower() and 'scenario' in key.lower():
                    if isinstance(value, str) and value.strip():
                        test_list.append(value.strip())
                    elif isinstance(value, list):
                        test_list.extend([str(item).strip() for item in value if str(item).strip()])
        
        return list(set(test_list))

    def _extract_figma_links(self, fields: Dict) -> List[str]:
        """Extract Figma links from description and comments"""
        figma_links = []
        text_content = []
        
        # Add description
        description = self._extract_description(fields.get('description'))
        if description:
            text_content.append(description)
        
        # Add comments
        comments = fields.get('comment', {}).get('comments', [])
        for comment in comments:
            if comment.get('body'):
                text_content.append(self._extract_description(comment.get('body')))
        
        # Find Figma links
        figma_pattern = r'https?://[^\s]*figma[^\s]*'
        for text in text_content:
            matches = re.findall(figma_pattern, text, re.IGNORECASE)
            figma_links.extend(matches)
        
        return list(set(figma_links))

    def _extract_attachments(self, fields: Dict) -> List[Dict]:
        """Extract attachment information"""
        attachments = []
        attachment_list = fields.get('attachment', [])
        
        for attachment in attachment_list:
            attachments.append({
                'filename': attachment.get('filename', ''),
                'url': attachment.get('content', ''),
                'size': attachment.get('size', 0),
                'mimeType': attachment.get('mimeType', '')
            })
        
        return attachments

    def _extract_linked_issues(self, fields: Dict) -> List[Dict]:
        """Extract linked issues information"""
        linked_issues = []
        issue_links = fields.get('issuelinks', [])
        
        for link in issue_links:
            outward_issue = link.get('outwardIssue')
            inward_issue = link.get('inwardIssue')
            
            if outward_issue:
                linked_issues.append({
                    'key': outward_issue.get('key', ''),
                    'summary': outward_issue.get('fields', {}).get('summary', ''),
                    'type': link.get('type', {}).get('name', ''),
                    'direction': 'outward'
                })
            
            if inward_issue:
                linked_issues.append({
                    'key': inward_issue.get('key', ''),
                    'summary': inward_issue.get('fields', {}).get('summary', ''),
                    'type': link.get('type', {}).get('name', ''),
                    'direction': 'inward'
                })
        
        return linked_issues

    def _extract_comments(self, fields: Dict) -> List[Dict]:
        """Extract comments information"""
        comments = []
        comment_list = fields.get('comment', {}).get('comments', [])
        
        for comment in comment_list:
            comments.append({
                'author': comment.get('author', {}).get('displayName', 'Unknown'),
                'body': self._extract_description(comment.get('body')),
                'created': comment.get('created', ''),
                'updated': comment.get('updated', '')
            })
        
        return comments

    def _extract_agile_team(self, fields: Dict) -> str:
        """Extract agile team information"""
        # Check various possible team fields
        team_fields = ['customfield_10020', 'customfield_10021', 'team']
        
        for field in team_fields:
            value = fields.get(field)
            if value:
                if isinstance(value, dict):
                    return value.get('name', '') or value.get('value', '')
                elif isinstance(value, str):
                    return value
        
        return ''

    def _extract_dependencies(self, fields: Dict) -> List[str]:
        """Extract dependencies information"""
        dependencies = []
        
        # Check for dependency fields
        dep_fields = ['customfield_10022', 'dependencies', 'blocks']
        
        for field in dep_fields:
            value = fields.get(field)
            if value:
                if isinstance(value, list):
                    dependencies.extend([str(item) for item in value])
                elif isinstance(value, str):
                    dependencies.append(value)
        
        return list(set(dependencies))
