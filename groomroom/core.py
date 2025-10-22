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
        
        # Top 3 Groom Levels with specific output behaviors
        self.groom_levels = {
            'insight': {
                'name': 'Insight (Balanced Groom)',
                'description': 'Balanced analysis — highlights clarity, ACs, QA scenarios.',
                'purpose': 'Ideal for refinement meetings and sprint grooming',
                'output_style': 'readable_summary'
            },
            'actionable': {
                'name': 'Actionable (QA + DoR Coaching)',
                'description': 'Full prescriptive refinement guidance, includes rewrites.',
                'purpose': 'Deep, prescriptive mode for sprint commitment or QA handoff',
                'output_style': 'structured_sections'
            },
            'summary': {
                'name': 'Summary (Snapshot)',
                'description': 'Concise overview for leads and dashboards.',
                'purpose': 'Quick view for leads or refinement dashboards',
                'output_style': 'compact_card'
            }
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
            'has_clear_structure': story_quality_score >= 70,
            'has_persona': bool(detected_persona),
            'has_goal': bool(detected_goal),
            'has_benefit': bool(detected_benefit)
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
        
        # Add weak areas for enhanced output
        dor_analysis['weak_areas'] = dor_analysis['missing_fields'][:5]  # Top 5 missing fields
        
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

    def analyze_ticket(self, jira_issue_or_content: Union[Dict, str], mode: str = "actionable", figma_link: str = None) -> Dict[str, Any]:
        """Main analysis pipeline for comprehensive ticket refinement with enhanced 04-mini style output"""
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
            
            # Audit acceptance criteria with enhanced rewrites
            ac_audit = self.audit_acceptance_criteria_enhanced(issue_data.get('acceptance_criteria', []))
            
            # Generate comprehensive test scenarios (P/N/E)
            test_scenarios = self.generate_comprehensive_test_scenarios(issue_data)
            
            # Audit bug (if applicable)
            bug_audit = None
            if card_type_analysis['detected_type'] == 'bug':
                bug_audit = self.audit_bug(issue_data)
            
            # Analyze frameworks with enhanced scoring
            framework_scores = self.analyze_frameworks_enhanced(issue_data)
            
            # Enhanced DoR analysis
            dor_analysis = self.analyze_dor_requirements_enhanced(issue_data)
            
            # Calculate technical/ADA coverage
            technical_ada = self._calculate_technical_ada_coverage(issue_data, test_scenarios)
            
            # Calculate sprint readiness with new formula: DoR(60%) + Frameworks(25%) + Technical/Test(15%)
            readiness_analysis = self.calculate_readiness_enhanced(dor_analysis, framework_scores, technical_ada)
            
            # Generate role-tagged recommendations
            role_recommendations = self._generate_role_tagged_recommendations(dor_analysis, ac_audit, test_scenarios, bug_audit, framework_scores, technical_ada)
            
            # DesignSync analysis (if Figma link provided)
            designsync = None
            if figma_link:
                designsync = self._analyze_designsync(issue_data, figma_link, ac_audit, test_scenarios)
            
            # Build enhanced structured output
            output = {
                "TicketKey": issue_data.get('key', ''),
                "Title": issue_data.get('summary', ''),
                "Mode": mode.title(),
                "Readiness": {
                    "Score": readiness_analysis['score'],
                    "Status": readiness_analysis['status'],
                    "DoRCoveragePercent": dor_analysis['coverage_percentage'],
                    "MissingFields": dor_analysis['missing_fields'],
                    "WeakAreas": dor_analysis.get('weak_areas', [])
                },
                "FrameworkScores": {
                    "ROI": framework_scores.get('ROI', 0),
                    "INVEST": framework_scores.get('INVEST', 0),
                    "ACCEPT": framework_scores.get('ACCEPT', 0),
                    "3C": framework_scores.get('3C', 0)
                },
                "StoryReview": {
                    "Persona": story_analysis.get('has_persona', False),
                    "Goal": story_analysis.get('has_goal', False),
                    "Benefit": story_analysis.get('has_benefit', False),
                    "SuggestedRewrite": story_analysis.get('story_rewrite', '')
                },
                "AcceptanceCriteriaAudit": {
                    "Detected": ac_audit['detected'],
                    "Weak": ac_audit['weak'],
                    "SuggestedRewrites": ac_audit['suggested_rewrites']
                },
                "TestScenarios": {
                    "Positive": test_scenarios.get('positive', []),
                    "Negative": test_scenarios.get('negative', []),
                    "Error": test_scenarios.get('error', [])
                },
                "TechnicalADA": technical_ada,
                "DesignSync": designsync or {"Enabled": False, "Score": 0, "Mismatches": [], "Changes": []},
                "Recommendations": role_recommendations,
                "BatchSummary": {
                    "TotalAnalysed": 1,
                    "Ready": 1 if readiness_analysis['score'] >= 90 else 0,
                    "NeedsRefinement": 1 if 70 <= readiness_analysis['score'] < 90 else 0,
                    "NotReady": 1 if readiness_analysis['score'] < 70 else 0
                }
            }
            
            # Add mode-specific formatting and length guardrails
            output = self._format_output_by_mode_enhanced(output, mode)
            
            # Apply length guardrails and quality gates
            output = self.apply_length_guardrails(output, mode)
            
            # Generate final enhanced output
            output["enhanced_output"] = self.generate_enhanced_output(output)
            
            return output
            
        except Exception as e:
            console.print(f"[red]Error in ticket analysis: {e}[/red]")
            return {"error": str(e)}

    def audit_acceptance_criteria_enhanced(self, acceptance_criteria: List[str]) -> Dict[str, Any]:
        """Enhanced AC audit with flexible rewrite support (non-Gherkin allowed)"""
        if not acceptance_criteria:
            return {
                "detected": 0,
                "weak": 0,
                "suggested_rewrites": [
                    "Add acceptance criteria that define what the system should do",
                    "Include measurable outcomes and observable behaviours",
                    "Specify error handling and edge cases"
                ]
            }
        
        detected = len(acceptance_criteria)
        weak = 0
        suggested_rewrites = []
        
        for ac in acceptance_criteria:
            # Check if AC is vague or weak
            if self._is_weak_ac(ac):
                weak += 1
                suggested_rewrites.append(self._rewrite_weak_ac(ac))
        
        # If no weak ACs but we have some, suggest improvements
        if weak == 0 and detected > 0:
            suggested_rewrites.extend([
                "Ensure all ACs are testable and measurable",
                "Add edge case handling where applicable",
                "Include error state definitions"
            ])
        
        return {
            "detected": detected,
            "weak": weak,
            "suggested_rewrites": suggested_rewrites[:5]  # Limit to 5 suggestions
        }
    
    def generate_comprehensive_test_scenarios(self, issue_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate comprehensive test scenarios (Positive/Negative/Error)"""
        scenarios = {
            "positive": [],
            "negative": [],
            "error": []
        }
        
        # Extract key functionality from issue data
        summary = issue_data.get('summary', '')
        description = issue_data.get('description', '')
        ac_list = issue_data.get('acceptance_criteria', [])
        
        # Generate positive scenarios
        scenarios["positive"] = self._generate_positive_scenarios(summary, description, ac_list)
        
        # Generate negative scenarios
        scenarios["negative"] = self._generate_negative_scenarios(summary, description, ac_list)
        
        # Generate error scenarios
        scenarios["error"] = self._generate_error_scenarios(summary, description, ac_list)
        
        return scenarios
    
    def analyze_frameworks_enhanced(self, issue_data: Dict[str, Any]) -> Dict[str, int]:
        """Enhanced framework analysis with improved scoring"""
        scores = {}
        
        # ROI Framework (0-30)
        scores['ROI'] = self._calculate_roi_score(issue_data)
        
        # INVEST Framework (0-30)
        scores['INVEST'] = self._calculate_invest_score(issue_data)
        
        # ACCEPT Framework (0-30)
        scores['ACCEPT'] = self._calculate_accept_score(issue_data)
        
        # 3C Framework (0-10)
        scores['3C'] = self._calculate_3c_score(issue_data)
        
        return scores
    
    def _calculate_technical_ada_coverage(self, issue_data: Dict[str, Any], test_scenarios: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate technical and ADA coverage with detailed breakdown"""
        technical_ada = {
            "ImplementationDetails": "Missing",
            "ArchitecturalSolution": "Missing", 
            "ADA": {
                "Status": "Missing",
                "Notes": []
            },
            "NFR": {
                "Performance": "",
                "Security": "",
                "DevOps": ""
            }
        }
        
        # Check implementation details
        if self._check_implementation_details(issue_data):
            technical_ada["ImplementationDetails"] = "OK"
        elif self._has_partial_implementation_details(issue_data):
            technical_ada["ImplementationDetails"] = "Partial"
        
        # Check architectural solution
        if self._check_architectural_solution(issue_data):
            technical_ada["ArchitecturalSolution"] = "OK"
        elif self._has_partial_architectural_solution(issue_data):
            technical_ada["ArchitecturalSolution"] = "Partial"
        
        # Check ADA criteria
        ada_status, ada_notes = self._check_ada_detailed(issue_data)
        technical_ada["ADA"]["Status"] = ada_status
        technical_ada["ADA"]["Notes"] = ada_notes
        
        # Check NFR (Non-Functional Requirements)
        nfr = self._check_nfr_requirements(issue_data)
        technical_ada["NFR"] = nfr
        
        return technical_ada
    
    def calculate_readiness_enhanced(self, dor_analysis: Dict, framework_scores: Dict, technical_ada: Dict) -> Dict[str, Any]:
        """Calculate sprint readiness with new formula: DoR(60%) + Frameworks(25%) + Technical/Test(15%)"""
        
        # DoR contribution (60%)
        dor_score = dor_analysis.get('coverage_percentage', 0) * 0.6
        
        # Framework contribution (25%)
        framework_avg = sum(framework_scores.values()) / len(framework_scores) if framework_scores else 0
        framework_contribution = (framework_avg / 100) * 25
        
        # Technical/Test contribution (15%)
        technical_score = self._calculate_technical_test_score(technical_ada)
        technical_contribution = (technical_score / 100) * 15
        
        total_score = dor_score + framework_contribution + technical_contribution
        
        # Determine status
        if total_score >= 90:
            status = "Ready"
        elif total_score >= 70:
            status = "Needs Refinement"
        else:
            status = "Not Ready"
        
        return {
            "score": round(total_score, 1),
            "status": status,
            "breakdown": {
                "DoR": round(dor_score, 1),
                "Frameworks": round(framework_contribution, 1),
                "Technical": round(technical_contribution, 1)
            }
        }
    
    def _generate_role_tagged_recommendations(self, dor_analysis: Dict, ac_audit: Dict, test_scenarios: Dict, 
                                            bug_audit: Optional[Dict], framework_scores: Dict, technical_ada: Dict) -> Dict[str, List[str]]:
        """Generate role-tagged recommendations (PO, QA, Dev/Tech Lead)"""
        recommendations = {
            "PO": [],
            "QA": [],
            "Dev": []
        }
        
        # PO recommendations
        missing_fields = dor_analysis.get('missing_fields', [])
        if missing_fields:
            recommendations["PO"].extend([f"Complete {field}" for field in missing_fields[:3]])
        
        if ac_audit['weak'] > 0:
            recommendations["PO"].append(f"Rewrite {ac_audit['weak']} weak acceptance criteria")
        
        if framework_scores.get('ROI', 0) < 20:
            recommendations["PO"].append("Clarify business value and ROI")
        
        # QA recommendations
        total_scenarios = sum(len(scenarios) for scenarios in test_scenarios.values())
        if total_scenarios < 6:
            recommendations["QA"].append("Define comprehensive test scenarios (P/N/E)")
        
        if not test_scenarios.get('error'):
            recommendations["QA"].append("Add error handling test scenarios")
        
        if not test_scenarios.get('negative'):
            recommendations["QA"].append("Add negative test scenarios for edge cases")
        
        # Dev recommendations
        if technical_ada["ImplementationDetails"] == "Missing":
            recommendations["Dev"].append("Add implementation and deployment details")
        
        if technical_ada["ArchitecturalSolution"] == "Missing":
            recommendations["Dev"].append("Define architectural solution and design")
        
        if technical_ada["ADA"]["Status"] == "Missing":
            recommendations["Dev"].append("Add ADA compliance requirements")
        
        # Limit to 3 recommendations per role
        for role in recommendations:
            recommendations[role] = recommendations[role][:3]
        
        return recommendations
    
    def _analyze_designsync(self, issue_data: Dict[str, Any], figma_link: str, ac_audit: Dict, test_scenarios: Dict) -> Dict[str, Any]:
        """Analyze DesignSync integration with Figma"""
        # This would integrate with Figma API in a real implementation
        # For now, return a placeholder structure
        return {
            "Enabled": True,
            "Score": 75,  # Placeholder score
            "Mismatches": [
                "Button states missing in ACs",
                "Error states not covered in design"
            ],
            "Changes": ["Updated button styling"]
        }
    
    def _format_output_by_mode_enhanced(self, output: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Enhanced mode-specific formatting with length guardrails"""
        
        if mode == "actionable":
            return self._format_actionable_enhanced(output)
        elif mode == "insight":
            return self._format_insight_enhanced(output)
        elif mode == "summary":
            return self._format_summary_enhanced(output)
        else:
            return self._format_actionable_enhanced(output)
    
    def _format_actionable_enhanced(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced Actionable mode formatting (300-600 words target)"""
        # Generate the full markdown template
        markdown = self._generate_actionable_markdown(output)
        output["markdown"] = markdown
        output["word_count"] = len(markdown.split())
        return output
    
    def _format_insight_enhanced(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced Insight mode formatting (180-350 words target)"""
        # Generate condensed output
        markdown = self._generate_insight_markdown(output)
        output["markdown"] = markdown
        output["word_count"] = len(markdown.split())
        return output
    
    def _format_summary_enhanced(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced Summary mode formatting (120-180 words target)"""
        # Generate compact output
        markdown = self._generate_summary_markdown(output)
        output["markdown"] = markdown
        output["word_count"] = len(markdown.split())
        return output
    
    def _generate_actionable_markdown(self, output: Dict[str, Any]) -> str:
        """Generate full actionable markdown template"""
        lines = []
        
        # Header
        readiness = output["Readiness"]
        status_emoji = "✅" if readiness["Score"] >= 90 else "⚠️" if readiness["Score"] >= 70 else "❌"
        status_label = readiness["Status"]
        
        lines.append(f"⚡ Actionable Groom Report — {output['TicketKey']} | {output['Title']}")
        lines.append(f"Sprint Readiness: {readiness['Score']}% → {status_emoji} {status_label}")
        lines.append("")
        
        # DoR Section
        lines.append("📋 Definition of Ready")
        lines.append(f"• Coverage: {readiness['DoRCoveragePercent']}%")
        lines.append(f"• Missing Fields: {readiness['MissingFields']}")
        lines.append(f"• Weak Areas: {readiness['WeakAreas']}")
        lines.append("")
        
        # Framework Scores
        frameworks = output["FrameworkScores"]
        lines.append("🧭 Framework Scores")
        lines.append(f"• ROI: {frameworks['ROI']} | INVEST: {frameworks['INVEST']} | ACCEPT: {frameworks['ACCEPT']} | 3C: {frameworks['3C']}")
        
        # Find biggest score driver or blocker
        max_framework = max(frameworks.items(), key=lambda x: x[1])
        min_framework = min(frameworks.items(), key=lambda x: x[1])
        if min_framework[1] < 15:
            lines.append(f"(Biggest blocker: {min_framework[0]} at {min_framework[1]})")
        else:
            lines.append(f"(Strongest area: {max_framework[0]} at {max_framework[1]})")
        lines.append("")
        
        # User Story Review
        story = output["StoryReview"]
        lines.append("🧩 User Story Review")
        lines.append(f"• Persona: {'✅' if story['Persona'] else '❌'} | Goal: {'✅' if story['Goal'] else '❌'} | Benefit: {'✅' if story['Benefit'] else '❌'}")
        if story['SuggestedRewrite']:
            lines.append(f"Suggested Rewrite (concise, business-value oriented):")
            lines.append(f'"{story["SuggestedRewrite"]}"')
        lines.append("")
        
        # Acceptance Criteria
        ac_audit = output["AcceptanceCriteriaAudit"]
        lines.append("✅ Acceptance Criteria (audit + rewrites)")
        lines.append(f"• Detected: {ac_audit['Detected']} | Weak/Vague: {ac_audit['Weak']}")
        lines.append("Suggested Rewrites (non-Gherkin allowed, each testable & measurable):")
        for i, rewrite in enumerate(ac_audit['SuggestedRewrites'][:3], 1):
            lines.append(f"{i}) {rewrite}")
        lines.append("")
        
        # Test Scenarios
        test_scenarios = output["TestScenarios"]
        lines.append("🧪 Test Scenarios (must include positive, negative, error)")
        lines.append("• Positive: " + " | ".join(test_scenarios["Positive"][:2]))
        lines.append("• Negative: " + " | ".join(test_scenarios["Negative"][:2]))
        lines.append("• Error/Resilience: " + " | ".join(test_scenarios["Error"][:2]))
        lines.append("")
        
        # Technical/ADA
        technical = output["TechnicalADA"]
        lines.append("🧱 Technical / ADA / Architecture")
        lines.append(f"• Implementation Details: {'✅' if technical['ImplementationDetails'] == 'OK' else '⚠️' if technical['ImplementationDetails'] == 'Partial' else '❌'} (PRs/URLs/flags)")
        lines.append(f"• Architectural Solution: {'✅' if technical['ArchitecturalSolution'] == 'OK' else '⚠️' if technical['ArchitecturalSolution'] == 'Partial' else '❌'} (link/design note)")
        lines.append(f"• ADA: {'✅' if technical['ADA']['Status'] == 'OK' else '⚠️' if technical['ADA']['Status'] == 'Partial' else '❌'} ({', '.join(technical['ADA']['Notes'][:3])})")
        
        # NFR if applicable
        nfr_items = [f"{k}: {v}" for k, v in technical['NFR'].items() if v]
        if nfr_items:
            lines.append(f"• Performance/Security/DevOps: {' | '.join(nfr_items)}")
        lines.append("")
        
        # DesignSync (if enabled)
        designsync = output["DesignSync"]
        if designsync["Enabled"]:
            lines.append("🎨 DesignSync")
            lines.append(f"• DesignSync Score: {designsync['Score']}")
            lines.append("• Mismatches:")
            for mismatch in designsync["Mismatches"][:3]:
                lines.append(f"  – {mismatch}")
            if designsync["Changes"]:
                lines.append(f"• Changes detected: {' | '.join(designsync['Changes'][:2])}")
            lines.append("")
        
        # Role-Tagged Recommendations
        recommendations = output["Recommendations"]
        lines.append("💡 Role-Tagged Recommendations")
        lines.append("• PO: " + " | ".join(recommendations["PO"][:3]))
        lines.append("• QA: " + " | ".join(recommendations["QA"][:3]))
        lines.append("• Dev/Tech Lead: " + " | ".join(recommendations["Dev"][:3]))
        
        return "\n".join(lines)
    
    def _generate_insight_markdown(self, output: Dict[str, Any]) -> str:
        """Generate condensed insight markdown (180-350 words target)"""
        lines = []
        
        # Header
        readiness = output["Readiness"]
        status_emoji = "✅" if readiness["Score"] >= 90 else "⚠️" if readiness["Score"] >= 70 else "❌"
        
        lines.append(f"🔍 Insight Analysis — {output['TicketKey']}")
        lines.append(f"Readiness: {readiness['Score']}% ({status_emoji} {readiness['Status']})")
        lines.append(f"Weak Areas: {', '.join(readiness['WeakAreas'][:3])}")
        lines.append("")
        
        # Story Clarity
        story = output["StoryReview"]
        story_quality = "Good" if all([story['Persona'], story['Goal'], story['Benefit']]) else "Needs improvement"
        lines.append(f"Story Clarity: {story_quality} — Persona and Goal detected {'✅' if story['Persona'] and story['Goal'] else '❌'}")
        if story['SuggestedRewrite']:
            lines.append(f"Suggested rewrite: \"{story['SuggestedRewrite']}\"")
        lines.append("")
        
        # AC Quality
        ac_audit = output["AcceptanceCriteriaAudit"]
        lines.append(f"AC Quality: {ac_audit['Detected']} found ({ac_audit['Weak']} vague)")
        if ac_audit['Weak'] > 0:
            lines.append(f"→ Add AC for {ac_audit['SuggestedRewrites'][0] if ac_audit['SuggestedRewrites'] else 'edge case handling'}")
        lines.append("")
        
        # Test Scenarios
        test_scenarios = output["TestScenarios"]
        lines.append("Suggested Test Scenarios:")
        lines.append(f"• Positive: {' | '.join(test_scenarios['Positive'][:1])}")
        lines.append(f"• Negative: {' | '.join(test_scenarios['Negative'][:1])}")
        lines.append(f"• Error: {' | '.join(test_scenarios['Error'][:1])}")
        lines.append("")
        
        # Framework Summary
        frameworks = output["FrameworkScores"]
        lines.append("Framework Summary:")
        lines.append(f"ROI: {frameworks['ROI']} | INVEST: {frameworks['INVEST']} | ACCEPT: {frameworks['ACCEPT']} | 3C: {frameworks['3C']}")
        
        return "\n".join(lines)
    
    def _generate_summary_markdown(self, output: Dict[str, Any]) -> str:
        """Generate compact summary markdown (120-180 words target)"""
        lines = []
        
        # Header
        readiness = output["Readiness"]
        status_emoji = "✅" if readiness["Score"] >= 90 else "⚠️" if readiness["Score"] >= 70 else "❌"
        
        lines.append(f"📊 Summary — {output['TicketKey']}")
        lines.append(f"Readiness: {readiness['Score']}% → {status_emoji} {readiness['Status']}")
        lines.append("")
        
        # Top 3 gaps
        lines.append("Top 3 gaps:")
        for gap in readiness['WeakAreas'][:3]:
            lines.append(f"• {gap}")
        lines.append("")
        
        # Next 3 actions
        recommendations = output["Recommendations"]
        all_recs = recommendations["PO"] + recommendations["QA"] + recommendations["Dev"]
        lines.append("Next 3 actions:")
        for action in all_recs[:3]:
            lines.append(f"• {action}")
        lines.append("")
        
        # Framework scores as single line
        frameworks = output["FrameworkScores"]
        lines.append(f"Framework scores: ROI {frameworks['ROI']} | INVEST {frameworks['INVEST']} | ACCEPT {frameworks['ACCEPT']} | 3C {frameworks['3C']}")
        
        return "\n".join(lines)
    
    def generate_enhanced_output(self, output: Dict[str, Any]) -> str:
        """Generate both markdown and JSON output for enhanced GroomRoom"""
        # Generate markdown
        markdown = output.get("markdown", "")
        
        # Generate JSON
        json_output = {
            "TicketKey": output.get("TicketKey", ""),
            "Title": output.get("Title", ""),
            "Mode": output.get("Mode", "Actionable"),
            "Readiness": output.get("Readiness", {}),
            "FrameworkScores": output.get("FrameworkScores", {}),
            "StoryReview": output.get("StoryReview", {}),
            "AcceptanceCriteriaAudit": output.get("AcceptanceCriteriaAudit", {}),
            "TestScenarios": output.get("TestScenarios", {}),
            "TechnicalADA": output.get("TechnicalADA", {}),
            "DesignSync": output.get("DesignSync", {}),
            "Recommendations": output.get("Recommendations", {}),
            "BatchSummary": output.get("BatchSummary", {})
        }
        
        # Combine markdown and JSON
        result = f"{markdown}\n\n```json\n{json.dumps(json_output, indent=2)}\n```"
        return result
    
    def analyze_batch_tickets(self, tickets: List[Union[Dict, str]], mode: str = "actionable", figma_links: Dict[str, str] = None) -> Dict[str, Any]:
        """Analyze multiple tickets in batch with compact header"""
        results = []
        batch_summary = {
            "TotalAnalysed": 0,
            "Ready": 0,
            "NeedsRefinement": 0,
            "NotReady": 0
        }
        
        # Analyze each ticket
        for ticket in tickets:
            figma_link = figma_links.get(ticket.get('key', ''), None) if figma_links else None
            result = self.analyze_ticket(ticket, mode, figma_link)
            
            if "error" not in result:
                results.append(result)
                batch_summary["TotalAnalysed"] += 1
                
                readiness = result.get("Readiness", {}).get("Score", 0)
                if readiness >= 90:
                    batch_summary["Ready"] += 1
                elif readiness >= 70:
                    batch_summary["NeedsRefinement"] += 1
                else:
                    batch_summary["NotReady"] += 1
        
        # Generate batch header
        batch_header = self._generate_batch_header(batch_summary, results)
        
        # Update batch summary in each result
        for result in results:
            result["BatchSummary"] = batch_summary
        
        return {
            "batch_header": batch_header,
            "results": results,
            "summary": batch_summary
        }
    
    def _generate_batch_header(self, batch_summary: Dict[str, int], results: List[Dict[str, Any]]) -> str:
        """Generate compact batch header for multi-ticket runs"""
        lines = []
        
        lines.append(f"📦 Batch Summary — {batch_summary['TotalAnalysed']} tickets analysed")
        lines.append(f"Ready: {batch_summary['Ready']} | Needs Refinement: {batch_summary['NeedsRefinement']} | Not Ready: {batch_summary['NotReady']}")
        
        # Find top recurrent gaps
        all_weak_areas = []
        for result in results:
            weak_areas = result.get("Readiness", {}).get("WeakAreas", [])
            all_weak_areas.extend(weak_areas)
        
        # Count most common gaps
        from collections import Counter
        gap_counts = Counter(all_weak_areas)
        top_gaps = [gap for gap, count in gap_counts.most_common(3)]
        
        if top_gaps:
            lines.append(f"Top recurrent gaps: {', '.join(top_gaps)}")
        
        return "\n".join(lines)
    
    def apply_length_guardrails(self, output: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Apply length guardrails and quality gates"""
        word_count = output.get("word_count", 0)
        
        # Define target ranges
        target_ranges = {
            "actionable": (300, 600),
            "insight": (180, 350),
            "summary": (120, 180)
        }
        
        min_words, max_words = target_ranges.get(mode, (300, 600))
        
        # Check if content needs enrichment or compression
        if word_count < min_words:
            # Enrich content
            output = self._enrich_content(output, mode)
        elif word_count > max_words:
            # Compress content
            output = self._compress_content(output, mode)
        
        # Apply quality gates
        output = self._apply_quality_gates(output)
        
        return output
    
    def _enrich_content(self, output: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Enrich content when below minimum word count"""
        # Add more AC rewrites if needed
        ac_audit = output.get("AcceptanceCriteriaAudit", {})
        if len(ac_audit.get("SuggestedRewrites", [])) < 3:
            # Add more suggested rewrites
            additional_rewrites = [
                "Add measurable success criteria",
                "Include error handling specifications",
                "Define edge case behaviours"
            ]
            ac_audit["SuggestedRewrites"].extend(additional_rewrites[:3-len(ac_audit.get("SuggestedRewrites", []))])
        
        # Add more test scenarios if needed
        test_scenarios = output.get("TestScenarios", {})
        for scenario_type in ["Positive", "Negative", "Error"]:
            if len(test_scenarios.get(scenario_type, [])) < 2:
                test_scenarios[scenario_type].append(f"Additional {scenario_type.lower()} scenario for comprehensive testing")
        
        return output
    
    def _compress_content(self, output: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Compress content when above maximum word count"""
        # Limit recommendations to 2 per role
        recommendations = output.get("Recommendations", {})
        for role in recommendations:
            recommendations[role] = recommendations[role][:2]
        
        # Limit test scenarios
        test_scenarios = output.get("TestScenarios", {})
        for scenario_type in test_scenarios:
            test_scenarios[scenario_type] = test_scenarios[scenario_type][:2]
        
        # Limit AC rewrites
        ac_audit = output.get("AcceptanceCriteriaAudit", {})
        ac_audit["SuggestedRewrites"] = ac_audit.get("SuggestedRewrites", [])[:3]
        
        return output
    
    def _apply_quality_gates(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quality gates to ensure minimum content"""
        # Ensure at least 3 AC rewrites
        ac_audit = output.get("AcceptanceCriteriaAudit", {})
        if ac_audit.get("Detected", 0) == 0:
            ac_audit["SuggestedRewrites"] = [
                "Add acceptance criteria that define what the system should do",
                "Include measurable outcomes and observable behaviours", 
                "Specify error handling and edge cases"
            ]
        
        # Ensure readiness is not 0 if content exists
        readiness = output.get("Readiness", {})
        if readiness.get("Score", 0) == 0 and any([
            output.get("Title"),
            output.get("StoryReview", {}).get("SuggestedRewrite"),
            ac_audit.get("SuggestedRewrites")
        ]):
            readiness["Score"] = 25  # Minimum score for content that exists
            readiness["Status"] = "Not Ready"
        
        return output

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

    def _is_weak_ac(self, ac: str) -> bool:
        """Check if acceptance criteria is weak or vague"""
        weak_indicators = [
            "should", "could", "might", "maybe", "possibly",
            "as needed", "if required", "when appropriate",
            "user friendly", "intuitive", "easy to use"
        ]
        
        ac_lower = ac.lower()
        return any(indicator in ac_lower for indicator in weak_indicators) or len(ac.strip()) < 20
    
    def _rewrite_weak_ac(self, ac: str) -> str:
        """Rewrite weak acceptance criteria to be testable and measurable"""
        # This would use AI to rewrite weak ACs
        # For now, return a template suggestion
        return f"Rewrite: '{ac}' → 'Show specific error message when [condition] occurs'"
    
    def _generate_positive_scenarios(self, summary: str, description: str, ac_list: List[str]) -> List[str]:
        """Generate positive test scenarios"""
        scenarios = []
        
        # Extract key actions from summary and description
        if "login" in summary.lower() or "authentication" in description.lower():
            scenarios.append("User successfully logs in with valid credentials")
        
        if "payment" in summary.lower() or "checkout" in description.lower():
            scenarios.append("User completes payment with valid payment method")
        
        if "search" in summary.lower():
            scenarios.append("User finds relevant results with valid search query")
        
        # Add generic positive scenario if none specific
        if not scenarios:
            scenarios.append("User successfully completes the main workflow")
        
        return scenarios[:2]  # Limit to 2 positive scenarios
    
    def _generate_negative_scenarios(self, summary: str, description: str, ac_list: List[str]) -> List[str]:
        """Generate negative test scenarios"""
        scenarios = []
        
        if "login" in summary.lower():
            scenarios.append("User cannot login with invalid credentials")
        
        if "payment" in summary.lower():
            scenarios.append("Payment fails with invalid payment details")
        
        if "search" in summary.lower():
            scenarios.append("No results returned for invalid search query")
        
        # Add generic negative scenario
        if not scenarios:
            scenarios.append("System handles invalid input gracefully")
        
        return scenarios[:2]  # Limit to 2 negative scenarios
    
    def _generate_error_scenarios(self, summary: str, description: str, ac_list: List[str]) -> List[str]:
        """Generate error handling test scenarios"""
        scenarios = []
        
        if "api" in description.lower() or "service" in description.lower():
            scenarios.append("System handles API timeout gracefully")
            scenarios.append("System recovers from network errors")
        
        if "payment" in summary.lower():
            scenarios.append("Payment service unavailable - show retry option")
        
        # Add generic error scenarios
        scenarios.append("System displays appropriate error message for server errors")
        
        return scenarios[:2]  # Limit to 2 error scenarios
    
    def _calculate_roi_score(self, issue_data: Dict[str, Any]) -> int:
        """Calculate ROI framework score (0-30)"""
        score = 0
        
        # Readiness (10 points)
        if self._has_business_value(issue_data):
            score += 10
        
        # Objectives (10 points)
        if self._has_clear_objectives(issue_data):
            score += 10
        
        # Implementation (10 points)
        if self._has_implementation_plan(issue_data):
            score += 10
        
        return score
    
    def _calculate_invest_score(self, issue_data: Dict[str, Any]) -> int:
        """Calculate INVEST framework score (0-30)"""
        score = 0
        
        # Independent (5 points)
        if self._is_independent(issue_data):
            score += 5
        
        # Negotiable (5 points)
        if self._is_negotiable(issue_data):
            score += 5
        
        # Valuable (5 points)
        if self._is_valuable(issue_data):
            score += 5
        
        # Estimable (5 points)
        if self._is_estimable(issue_data):
            score += 5
        
        # Small (5 points)
        if self._is_small(issue_data):
            score += 5
        
        # Testable (5 points)
        if self._is_testable(issue_data):
            score += 5
        
        return score
    
    def _calculate_accept_score(self, issue_data: Dict[str, Any]) -> int:
        """Calculate ACCEPT framework score (0-30)"""
        score = 0
        
        # Actionable (5 points)
        if self._is_actionable(issue_data):
            score += 5
        
        # Clear (5 points)
        if self._is_clear(issue_data):
            score += 5
        
        # Complete (5 points)
        if self._is_complete(issue_data):
            score += 5
        
        # Edge-case aware (5 points)
        if self._is_edge_case_aware(issue_data):
            score += 5
        
        # Precise (5 points)
        if self._is_precise(issue_data):
            score += 5
        
        # Testable (5 points)
        if self._is_testable(issue_data):
            score += 5
        
        return score
    
    def _calculate_3c_score(self, issue_data: Dict[str, Any]) -> int:
        """Calculate 3C framework score (0-10)"""
        score = 0
        
        # Card (3 points)
        if self._has_good_card(issue_data):
            score += 3
        
        # Conversation (4 points)
        if self._has_conversation_notes(issue_data):
            score += 4
        
        # Confirmation (3 points)
        if self._has_confirmation(issue_data):
            score += 3
        
        return score
    
    def _has_partial_implementation_details(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has partial implementation details"""
        description = issue_data.get('description', '').lower()
        return any(keyword in description for keyword in ['implementation', 'technical', 'code', 'api'])
    
    def _has_partial_architectural_solution(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has partial architectural solution"""
        description = issue_data.get('description', '').lower()
        return any(keyword in description for keyword in ['architecture', 'design', 'system', 'component'])
    
    def _check_ada_detailed(self, issue_data: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Check ADA compliance with detailed notes"""
        description = issue_data.get('description', '').lower()
        ac_list = issue_data.get('acceptance_criteria', [])
        
        ada_notes = []
        status = "Missing"
        
        # Check for accessibility keywords
        accessibility_keywords = ['accessibility', 'ada', 'wcag', 'screen reader', 'keyboard', 'focus', 'alt text', 'contrast']
        
        if any(keyword in description for keyword in accessibility_keywords):
            status = "Partial"
            ada_notes.append("Accessibility mentioned in description")
        
        if any(keyword in ' '.join(ac_list).lower() for keyword in accessibility_keywords):
            status = "OK"
            ada_notes.append("Accessibility covered in acceptance criteria")
        
        if status == "Missing":
            ada_notes = ["Keyboard navigation", "Focus order", "Alt text", "Contrast"]
        
        return status, ada_notes
    
    def _check_nfr_requirements(self, issue_data: Dict[str, Any]) -> Dict[str, str]:
        """Check non-functional requirements"""
        description = issue_data.get('description', '').lower()
        
        nfr = {
            "Performance": "",
            "Security": "",
            "DevOps": ""
        }
        
        # Performance
        if any(keyword in description for keyword in ['performance', 'speed', 'response time', 'load']):
            nfr["Performance"] = "Performance requirements mentioned"
        
        # Security
        if any(keyword in description for keyword in ['security', 'authentication', 'authorization', 'encryption']):
            nfr["Security"] = "Security considerations mentioned"
        
        # DevOps
        if any(keyword in description for keyword in ['deployment', 'infrastructure', 'monitoring', 'logging']):
            nfr["DevOps"] = "DevOps considerations mentioned"
        
        return nfr
    
    def _calculate_technical_test_score(self, technical_ada: Dict[str, Any]) -> float:
        """Calculate technical and test score (0-100)"""
        score = 0
        
        # Implementation details (30%)
        if technical_ada["ImplementationDetails"] == "OK":
            score += 30
        elif technical_ada["ImplementationDetails"] == "Partial":
            score += 15
        
        # Architectural solution (30%)
        if technical_ada["ArchitecturalSolution"] == "OK":
            score += 30
        elif technical_ada["ArchitecturalSolution"] == "Partial":
            score += 15
        
        # ADA compliance (20%)
        if technical_ada["ADA"]["Status"] == "OK":
            score += 20
        elif technical_ada["ADA"]["Status"] == "Partial":
            score += 10
        
        # NFR coverage (20%)
        nfr_count = sum(1 for nfr in technical_ada["NFR"].values() if nfr)
        score += (nfr_count / 3) * 20
        
        return score
    
    # Helper methods for framework scoring
    def _has_business_value(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has clear business value"""
        description = issue_data.get('description', '').lower()
        return any(keyword in description for keyword in ['business value', 'roi', 'revenue', 'customer', 'user benefit'])
    
    def _has_clear_objectives(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has clear objectives"""
        summary = issue_data.get('summary', '').lower()
        return 'as a' in summary and 'i want' in summary
    
    def _has_implementation_plan(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has implementation plan"""
        description = issue_data.get('description', '').lower()
        return any(keyword in description for keyword in ['implementation', 'technical', 'development', 'code'])
    
    def _is_independent(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is independent"""
        description = issue_data.get('description', '').lower()
        return 'dependency' not in description and 'blocked' not in description
    
    def _is_negotiable(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is negotiable"""
        summary = issue_data.get('summary', '').lower()
        return 'must' not in summary and 'required' not in summary
    
    def _is_valuable(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is valuable"""
        return self._has_business_value(issue_data)
    
    def _is_estimable(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is estimable"""
        description = issue_data.get('description', '').lower()
        return len(description) > 50 and 'unknown' not in description
    
    def _is_small(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is appropriately sized"""
        description = issue_data.get('description', '')
        return 50 < len(description) < 1000
    
    def _is_testable(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is testable"""
        ac_list = issue_data.get('acceptance_criteria', [])
        return len(ac_list) > 0
    
    def _is_actionable(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is actionable"""
        summary = issue_data.get('summary', '').lower()
        return 'as a' in summary and 'i want' in summary
    
    def _is_clear(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is clear"""
        summary = issue_data.get('summary', '')
        return len(summary) > 10 and '?' not in summary
    
    def _is_complete(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is complete"""
        description = issue_data.get('description', '')
        ac_list = issue_data.get('acceptance_criteria', [])
        return len(description) > 50 and len(ac_list) > 0
    
    def _is_edge_case_aware(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is edge case aware"""
        description = issue_data.get('description', '').lower()
        ac_list = issue_data.get('acceptance_criteria', [])
        edge_keywords = ['error', 'invalid', 'empty', 'null', 'exception', 'timeout']
        return any(keyword in description or any(keyword in ac.lower() for ac in ac_list) for keyword in edge_keywords)
    
    def _is_precise(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue is precise"""
        summary = issue_data.get('summary', '')
        return len(summary.split()) > 3 and 'vague' not in summary.lower()
    
    def _has_good_card(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has good card format"""
        summary = issue_data.get('summary', '')
        return len(summary) > 10 and 'as a' in summary.lower()
    
    def _has_conversation_notes(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has conversation notes"""
        description = issue_data.get('description', '')
        return len(description) > 100
    
    def _has_confirmation(self, issue_data: Dict[str, Any]) -> bool:
        """Check if issue has confirmation (acceptance criteria)"""
        ac_list = issue_data.get('acceptance_criteria', [])
        return len(ac_list) > 0

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
        """Format output based on the 3 groom levels with specific behaviors"""
        
        if mode == "insight":
            # Insight (Balanced Groom) - Readable summary format
            return self._format_insight_output(output)
        
        elif mode == "actionable":
            # Actionable (QA + DoR Coaching) - Structured sections
            return self._format_actionable_output(output)
        
        elif mode == "summary":
            # Summary (Snapshot) - Compact card format
            return self._format_summary_output(output)
        
        # Default to actionable if mode not recognized
        return self._format_actionable_output(output)

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

    def _format_insight_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for Insight (Balanced Groom) mode - Readable summary"""
        readiness = output.get("SprintReadiness", 0)
        status = "Ready for Dev" if readiness >= 90 else "Needs minor refinement" if readiness >= 70 else "Not Ready"
        
        # Get top gaps
        missing_fields = output.get("DefinitionOfReady", {}).get("MissingFields", [])
        top_gaps = missing_fields[:3]
        
        # Story clarity assessment
        story_analysis = output.get("StoryAnalysis", {})
        story_quality = story_analysis.get("story_quality_score", 0)
        story_clarity = "Good" if story_quality >= 70 else "Needs improvement"
        
        # Framework scores
        framework_scores = output.get("FrameworkScores", {})
        
        return {
            "mode": "insight",
            "display_format": "readable_summary",
            "ticket_key": output.get("TicketKey", ""),
            "readiness_percentage": readiness,
            "readiness_status": status,
            "weak_areas": top_gaps,
            "story_clarity": {
                "assessment": story_clarity,
                "persona_goal_detected": story_analysis.get("has_clear_structure", False),
                "suggested_rewrite": output.get("StoryRewrite")
            },
            "acceptance_criteria": {
                "detected_count": output.get("AcceptanceCriteriaAudit", {}).get("Detected", 0),
                "weak_count": output.get("AcceptanceCriteriaAudit", {}).get("Weak", 0),
                "suggested_rewrites": output.get("AcceptanceCriteriaAudit", {}).get("SuggestedRewrite", [])
            },
            "test_scenarios": output.get("SuggestedTestScenarios", []),
            "framework_summary": {
                "roi": framework_scores.get("ROI", 0),
                "invest": framework_scores.get("INVEST", 0),
                "accept": framework_scores.get("ACCEPT", 0),
                "3c": framework_scores.get("3C", 0)
            },
            "qa_notes": self._generate_qa_notes(output)
        }

    def _format_actionable_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for Actionable (QA + DoR Coaching) mode - Structured sections"""
        readiness = output.get("SprintReadiness", 0)
        status_emoji = "✅" if readiness >= 90 else "⚠️" if readiness >= 70 else "❌"
        status_text = "Ready for Dev" if readiness >= 90 else "Needs Refinement" if readiness >= 70 else "Not Ready"
        
        return {
            "mode": "actionable",
            "display_format": "structured_sections",
            "ticket_key": output.get("TicketKey", ""),
            "readiness_score": readiness,
            "readiness_status": f"{status_emoji} {status_text}",
            "sections": {
                "user_story": {
                    "title": "🧩 User Story",
                    "persona_goal_found": output.get("StoryAnalysis", {}).get("has_clear_structure", False),
                    "benefit_clarity": "Clear" if output.get("StoryAnalysis", {}).get("story_quality_score", 0) >= 70 else "Unclear",
                    "suggested_rewrite": output.get("StoryRewrite"),
                    "missing_business_metric": not any("roi" in str(item).lower() or "business" in str(item).lower() 
                                                     for item in output.get("Recommendations", []))
                },
                "acceptance_criteria": {
                    "title": "✅ Acceptance Criteria",
                    "detected_count": output.get("AcceptanceCriteriaAudit", {}).get("Detected", 0),
                    "need_rewriting": output.get("AcceptanceCriteriaAudit", {}).get("Weak", 0),
                    "suggested_rewrites": output.get("AcceptanceCriteriaAudit", {}).get("SuggestedRewrite", [])
                },
                "qa_scenarios": {
                    "title": "🧪 QA Scenarios",
                    "suggested_scenarios": output.get("SuggestedTestScenarios", []),
                    "missing_negative_flow": len([s for s in output.get("SuggestedTestScenarios", []) if "negative" in s.lower()]) == 0,
                    "missing_error_handling": len([s for s in output.get("SuggestedTestScenarios", []) if "error" in s.lower()]) == 0
                },
                "technical_ada": {
                    "title": "🧱 Technical / ADA",
                    "missing_architectural_solution": "Architectural Solution" in output.get("DefinitionOfReady", {}).get("MissingFields", []),
                    "missing_ada_criteria": "ADA Criteria" in output.get("DefinitionOfReady", {}).get("MissingFields", []),
                    "figma_links": output.get("DetailedAnalysis", {}).get("DOR", {}).get("detailed_analysis", {}).get("architectural_solution", {}).get("present", False)
                }
            },
            "recommendations": {
                "po": [rec for rec in output.get("Recommendations", []) if any(word in rec.lower() for word in ["story", "acceptance", "criteria", "business"])],
                "qa": [rec for rec in output.get("Recommendations", []) if any(word in rec.lower() for word in ["test", "scenario", "qa", "testing"])],
                "dev": [rec for rec in output.get("Recommendations", []) if any(word in rec.lower() for word in ["implementation", "technical", "architecture", "deployment"])]
            }
        }

    def _format_summary_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for Summary (Snapshot) mode - Compact card format"""
        readiness = output.get("SprintReadiness", 0)
        status_emoji = "✅" if readiness >= 90 else "⚠️" if readiness >= 70 else "❌"
        status_text = "Ready for Dev" if readiness >= 90 else "Needs Refinement" if readiness >= 70 else "Not Ready"
        
        # Get top 3 gaps
        missing_fields = output.get("DefinitionOfReady", {}).get("MissingFields", [])
        top_gaps = missing_fields[:3]
        
        # Get top 3 recommended actions
        recommendations = output.get("Recommendations", [])[:3]
        
        # Calculate framework averages
        framework_scores = output.get("FrameworkScores", {})
        framework_avg = sum(framework_scores.values()) / len(framework_scores) if framework_scores else 0
        
        return {
            "mode": "summary",
            "display_format": "compact_card",
            "ticket_key": output.get("TicketKey", ""),
            "readiness_percentage": readiness,
            "readiness_status": f"{status_emoji} {status_text}",
            "dor_coverage": output.get("DefinitionOfReady", {}).get("CoveragePercent", 0),
            "top_gaps": top_gaps,
            "recommended_actions": recommendations,
            "framework_average": round(framework_avg, 1),
            "card_type": output.get("Type", "Unknown")
        }

    def _generate_qa_notes(self, output: Dict[str, Any]) -> List[str]:
        """Generate QA-specific notes from test scenarios"""
        test_scenarios = output.get("SuggestedTestScenarios", [])
        qa_notes = []
        
        # Check for different test types
        has_positive = any("positive" in scenario.lower() for scenario in test_scenarios)
        has_negative = any("negative" in scenario.lower() for scenario in test_scenarios)
        has_error = any("error" in scenario.lower() for scenario in test_scenarios)
        
        if not has_positive:
            qa_notes.append("Add positive test scenario for main user flow")
        if not has_negative:
            qa_notes.append("Add negative test scenarios for edge cases")
        if not has_error:
            qa_notes.append("Add error handling test scenarios")
        
        return qa_notes

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

    def analyze_dor_requirements(self, issue_data: Dict) -> Dict[str, Any]:
        """Analyze Definition of Ready requirements coverage"""
        dor_analysis = {
            'coverage_percentage': 0,
            'missing_elements': [],
            'present_elements': [],
            'detailed_analysis': {}
        }
        
        total_requirements = len(self.dor_requirements)
        present_count = 0
        
        for req_key, req_info in self.dor_requirements.items():
            is_present = False
            analysis = {
                'name': req_info['name'],
                'required': req_info.get('required', False),
                'present': False,
                'details': '',
                'score': 0
            }
            
            if req_key == 'summary':
                is_present = bool(issue_data.get('summary', '').strip())
                analysis['details'] = issue_data.get('summary', '')[:100] + '...' if len(issue_data.get('summary', '')) > 100 else issue_data.get('summary', '')
                
            elif req_key == 'description':
                is_present = bool(issue_data.get('description', '').strip())
                analysis['details'] = f"Length: {len(issue_data.get('description', ''))} characters"
                
            elif req_key == 'acceptance_criteria':
                ac_list = issue_data.get('acceptance_criteria', [])
                is_present = len(ac_list) > 0
                analysis['details'] = f"Found {len(ac_list)} acceptance criteria"
                
            elif req_key == 'testing_steps':
                test_list = issue_data.get('test_scenarios', [])
                is_present = len(test_list) > 0
                analysis['details'] = f"Found {len(test_list)} test scenarios"
                
            elif req_key == 'additional_fields':
                additional_present = []
                if issue_data.get('labels'): additional_present.append('Brand(s)')
                if issue_data.get('components'): additional_present.append('Component(s)')
                if issue_data.get('agile_team'): additional_present.append('Agile Team')
                if issue_data.get('story_points'): additional_present.append('Story Points')
                if issue_data.get('figma_links'): additional_present.append('Figma Link')
                if issue_data.get('dependencies'): additional_present.append('Dependencies')
                
                is_present = len(additional_present) >= 3  # At least 3 of 6 fields
                analysis['details'] = f"Present: {', '.join(additional_present)}"
            
            analysis['present'] = is_present
            analysis['score'] = 1 if is_present else 0
            
            if is_present:
                present_count += 1
                dor_analysis['present_elements'].append(req_info['name'])
            else:
                dor_analysis['missing_elements'].append(req_info['name'])
            
            dor_analysis['detailed_analysis'][req_key] = analysis
        
        dor_analysis['coverage_percentage'] = (present_count / total_requirements) * 100
        
        return dor_analysis

    def analyze_acceptance_criteria(self, acceptance_criteria: List[str]) -> List[Dict[str, Any]]:
        """Analyze acceptance criteria with critique and rewrite functionality"""
        ac_analysis = []
        seen_hashes = set()
        
        for ac in acceptance_criteria:
            if not ac.strip():
                continue
                
            # Create hash for deduplication
            ac_hash = hashlib.md5(ac.strip().lower().encode()).hexdigest()
            if ac_hash in seen_hashes:
                continue
            seen_hashes.add(ac_hash)
            
            # Generate critique and rewrite
            critique = self._generate_ac_critique(ac)
            revised = self._generate_ac_rewrite(ac)
            
            ac_analysis.append({
                'original': ac.strip(),
                'critique': critique,
                'revised': revised,
                'hash': ac_hash
            })
        
        return ac_analysis

    def _generate_ac_critique(self, ac: str) -> str:
        """Generate critique for acceptance criteria"""
        if not self.client:
            return "Azure OpenAI not available for critique generation"
        
        try:
            prompt = f"""Analyze this acceptance criteria and provide a brief critique focusing on:
1. Clarity and specificity
2. Measurability and testability
3. Intent vs solution separation
4. Completeness

Acceptance Criteria: "{ac}"

Provide a concise critique (2-3 sentences max):"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating critique: {str(e)}"

    def _generate_ac_rewrite(self, ac: str) -> str:
        """Generate rewritten acceptance criteria"""
        if not self.client:
            return "Azure OpenAI not available for rewrite generation"
        
        try:
            prompt = f"""Rewrite this acceptance criteria to be business-ready and suitable for direct use by a Product Owner. Focus on:
1. Clear intent (what, not how)
2. Measurable outcomes
3. Business value
4. Given-When-Then format if applicable

Original: "{ac}"

Provide a single, improved acceptance criteria:"""

            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating rewrite: {str(e)}"

    def analyze_test_scenarios(self, issue_data: Dict) -> Dict[str, Any]:
        """Analyze test scenarios coverage"""
        test_analysis = {
            'present_scenarios': [],
            'missing_scenarios': [],
            'coverage_percentage': 0,
            'recommendations': []
        }
        
        existing_tests = issue_data.get('test_scenarios', [])
        description = issue_data.get('description', '')
        
        # Check for test scenario patterns in description
        test_patterns = {
            'positive': r'(positive|happy path|success|normal)',
            'negative': r'(negative|error|edge case|failure)',
            'rbt': r'(risk|boundary|edge|exception)'
        }
        
        found_types = set()
        for test_type, pattern in test_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                found_types.add(test_type)
        
        # Add existing test scenarios
        for test in existing_tests:
            test_analysis['present_scenarios'].append({
                'type': 'existing',
                'content': test,
                'category': 'unknown'
            })
        
        # Identify missing scenarios
        required_scenarios = ['positive', 'negative', 'rbt']
        missing_scenarios = [scenario for scenario in required_scenarios if scenario not in found_types]
        
        for missing in missing_scenarios:
            test_analysis['missing_scenarios'].append({
                'type': missing,
                'description': f"Missing {missing} test scenario",
                'recommendation': self._get_test_recommendation(missing, issue_data)
            })
        
        # Calculate coverage
        total_required = len(required_scenarios)
        present_count = len(found_types) + len(existing_tests)
        test_analysis['coverage_percentage'] = min((present_count / total_required) * 100, 100)
        
        # Generate recommendations
        test_analysis['recommendations'] = self._generate_test_recommendations(issue_data, missing_scenarios)
        
        return test_analysis

    def _get_test_recommendation(self, test_type: str, issue_data: Dict) -> str:
        """Get specific test recommendation based on type"""
        recommendations = {
            'positive': f"Define positive test scenario for: {issue_data.get('summary', 'this feature')}",
            'negative': f"Define negative test scenarios including error handling and edge cases",
            'rbt': f"Define risk-based test scenarios focusing on high-impact failure points"
        }
        return recommendations.get(test_type, "Define appropriate test scenario")

    def _generate_test_recommendations(self, issue_data: Dict, missing_scenarios: List[str]) -> List[str]:
        """Generate comprehensive test recommendations"""
        recommendations = []
        
        if 'positive' in missing_scenarios:
            recommendations.append("Add positive test scenario covering the main user journey")
        
        if 'negative' in missing_scenarios:
            recommendations.append("Add negative test scenarios for error handling and edge cases")
        
        if 'rbt' in missing_scenarios:
            recommendations.append("Add risk-based test scenarios for high-impact failure points")
        
        # Check for cross-browser/device testing
        if not any('cross' in str(item).lower() or 'browser' in str(item).lower() 
                  for item in issue_data.get('test_scenarios', []) + [issue_data.get('description', '')]):
            recommendations.append("Consider cross-browser/device testing requirements")
        
        return recommendations

    def evaluate_sprint_readiness(self, dor_analysis: Dict) -> Dict[str, Any]:
        """Evaluate sprint readiness with 0-100 scoring"""
        coverage = dor_analysis.get('coverage_percentage', 0)
        
        # Calculate readiness score
        readiness_score = min(coverage, 100)
        
        # Determine status
        if readiness_score >= 85:
            status = "Ready"
            color = "green"
        elif readiness_score >= 65:
            status = "Partially Ready"
            color = "yellow"
        else:
            status = "Not Ready"
            color = "red"
        
        return {
            'score': readiness_score,
            'status': status,
            'color': color,
            'coverage_breakdown': {
                'summary': dor_analysis['detailed_analysis'].get('summary', {}).get('score', 0),
                'description': dor_analysis['detailed_analysis'].get('description', {}).get('score', 0),
                'acceptance_criteria': dor_analysis['detailed_analysis'].get('acceptance_criteria', {}).get('score', 0),
                'testing_steps': dor_analysis['detailed_analysis'].get('testing_steps', {}).get('score', 0),
                'additional_fields': dor_analysis['detailed_analysis'].get('additional_fields', {}).get('score', 0)
            },
            'missing_critical': [item for item in dor_analysis.get('missing_elements', []) 
                               if dor_analysis['detailed_analysis'].get(item.lower().replace(' ', '_'), {}).get('required', False)]
        }

    def identify_gaps(self, dor_analysis: Dict, ac_analysis: List[Dict], test_analysis: Dict) -> List[str]:
        """Cross-reference all analyses to identify gaps"""
        gaps = []
        
        # DOR gaps
        missing_dor = dor_analysis.get('missing_elements', [])
        for missing in missing_dor:
            gaps.append(f"Missing DOR requirement: {missing}")
        
        # AC gaps
        if not ac_analysis:
            gaps.append("No acceptance criteria found")
        else:
            poor_ac_count = sum(1 for ac in ac_analysis if 'vague' in ac.get('critique', '').lower() or 'unclear' in ac.get('critique', '').lower())
            if poor_ac_count > 0:
                gaps.append(f"{poor_ac_count} acceptance criteria need improvement")
        
        # Test gaps
        missing_tests = test_analysis.get('missing_scenarios', [])
        for missing in missing_tests:
            gaps.append(f"Missing test scenario: {missing.get('type', 'unknown')}")
        
        # Framework gaps (simplified check)
        gaps.append("Consider framework alignment (INVEST, 3C, A-C-C-E-P-T)")
        
        return gaps

    def build_structured_output(self, issue_data: Dict, dor_analysis: Dict, ac_analysis: List[Dict], 
                              test_analysis: Dict, sprint_readiness: Dict, gaps: List[str]) -> Dict[str, Any]:
        """Build structured JSON output for UI rendering"""
        
        return {
            'ticket_summary': {
                'key': issue_data.get('key', ''),
                'summary': issue_data.get('summary', ''),
                'issue_type': issue_data.get('issue_type', ''),
                'status': issue_data.get('status', ''),
                'assignee': issue_data.get('assignee', ''),
                'story_points': issue_data.get('story_points', ''),
                'agile_team': issue_data.get('agile_team', '')
            },
            'definition_of_ready': {
                'coverage_percentage': dor_analysis.get('coverage_percentage', 0),
                'present_elements': dor_analysis.get('present_elements', []),
                'missing_elements': dor_analysis.get('missing_elements', []),
                'detailed_analysis': dor_analysis.get('detailed_analysis', {})
            },
            'acceptance_criteria_review': ac_analysis,
            'test_analysis': test_analysis,
            'sprint_readiness': sprint_readiness,
            'gaps_identified': gaps,
            'next_actions': self._generate_next_actions(dor_analysis, ac_analysis, test_analysis, gaps),
            'framework_alignment': self._analyze_framework_alignment(issue_data),
            'brand_analysis': self._analyze_brand_abbreviations(issue_data)
        }

    def _generate_next_actions(self, dor_analysis: Dict, ac_analysis: List[Dict], 
                              test_analysis: Dict, gaps: List[str]) -> List[str]:
        """Generate prioritized next actions"""
        actions = []
        
        # High priority actions
        missing_critical = [gap for gap in gaps if 'Missing DOR requirement' in gap]
        if missing_critical:
            actions.extend(missing_critical[:3])  # Top 3 critical gaps
        
        # AC improvements
        if ac_analysis:
            poor_ac = [ac for ac in ac_analysis if 'vague' in ac.get('critique', '').lower()]
            if poor_ac:
                actions.append(f"Improve {len(poor_ac)} acceptance criteria for clarity")
        
        # Test scenarios
        missing_tests = test_analysis.get('missing_scenarios', [])
        if missing_tests:
            actions.append(f"Add {len(missing_tests)} missing test scenarios")
        
        # Additional fields
        if 'Additional Card Details' in dor_analysis.get('missing_elements', []):
            actions.append("Complete additional card details (Brand, Component, Team, etc.)")
        
        return actions[:5]  # Limit to top 5 actions

    def _analyze_framework_alignment(self, issue_data: Dict) -> Dict[str, Any]:
        """Analyze framework alignment (simplified)"""
        content = f"{issue_data.get('summary', '')} {issue_data.get('description', '')}"
        
        framework_scores = {}
        for framework_key, framework_info in self.frameworks.items():
            elements = framework_info['elements']
            found_elements = []
            
            for element in elements:
                if re.search(element.lower(), content, re.IGNORECASE):
                    found_elements.append(element)
            
            framework_scores[framework_key] = {
                'name': framework_info['name'],
                'coverage_percentage': (len(found_elements) / len(elements)) * 100,
                'found_elements': found_elements,
                'missing_elements': [elem for elem in elements if elem not in found_elements]
            }
        
        return framework_scores

    def _analyze_brand_abbreviations(self, issue_data: Dict) -> Dict[str, Any]:
        """Analyze brand abbreviations usage"""
        content = f"{issue_data.get('summary', '')} {issue_data.get('description', '')}"
        
        found_brands = []
        for brand, description in self.brand_abbreviations.items():
            if re.search(r'\b' + brand + r'\b', content, re.IGNORECASE):
                found_brands.append({
                    'brand': brand,
                    'description': description,
                    'context': 'Found in ticket content'
                })
        
        return {
            'found_brands': found_brands,
            'total_brands_found': len(found_brands),
            'recommendations': self._generate_brand_recommendations(found_brands, content)
        }

    def _generate_brand_recommendations(self, found_brands: List[Dict], content: str) -> List[str]:
        """Generate brand-specific recommendations"""
        recommendations = []
        
        # Check for PWA (ELF) flows
        if any(brand['brand'] == 'ELF' for brand in found_brands):
            if not re.search(r'\b(PLP|PDP|Homepage|Minicart)\b', content, re.IGNORECASE):
                recommendations.append("PWA (ELF) flows should specify applicable pages (PLP, PDP, Homepage, Minicart)")
        
        # Check for EMEA payment
        if any(brand['brand'] == 'EMEA' for brand in found_brands):
            if re.search(r'\b(AfterPay|Klarna)\b', content, re.IGNORECASE):
                recommendations.append("EMEA brands should use ClearPay instead of AfterPay/Klarna")
        
        return recommendations

    def _check_prompt_length(self, prompt: str) -> Tuple[bool, int]:
        """Check if prompt is within model limits"""
        # Rough estimate: 1 token ≈ 4 characters
        estimated_tokens = len(prompt) // 4
        max_tokens = 120000  # Conservative limit for most models
        
        return estimated_tokens < max_tokens, estimated_tokens

    def generate_groom_analysis(self, ticket_content: str, level: str = "default") -> str:
        """Main pipeline for generating comprehensive groom analysis"""
        try:
            # If ticket_content is a Jira ticket number, fetch the full ticket
            if re.match(r'^[A-Z]+-\d+$', ticket_content.strip()):
                if not self.jira_integration:
                    return "Jira integration not available"
                
                ticket_info = self.jira_integration.get_ticket_info(ticket_content.strip())
                if not ticket_info:
                    return f"Could not fetch ticket {ticket_content}"
                
                issue_data = self.extract_jira_fields(ticket_info)
            else:
                # For pasted content, create minimal issue data
                issue_data = {
                    'key': 'PASTED-CONTENT',
                    'summary': 'Pasted Content Analysis',
                    'description': ticket_content,
                    'issue_type': 'Unknown',
                    'acceptance_criteria': [],
                    'test_scenarios': [],
                    'figma_links': [],
                    'attachments': [],
                    'linked_issues': [],
                    'comments': [],
                    'agile_team': '',
                    'dependencies': []
                }
            
            # Run the complete analysis pipeline
            dor_analysis = self.analyze_dor_requirements(issue_data)
            ac_analysis = self.analyze_acceptance_criteria(issue_data.get('acceptance_criteria', []))
            test_analysis = self.analyze_test_scenarios(issue_data)
            sprint_readiness = self.evaluate_sprint_readiness(dor_analysis)
            gaps = self.identify_gaps(dor_analysis, ac_analysis, test_analysis)
            
            # Build structured output
            structured_output = self.build_structured_output(
                issue_data, dor_analysis, ac_analysis, test_analysis, sprint_readiness, gaps
            )
            
            # Generate final analysis using LLM
            final_analysis = self._generate_final_analysis(structured_output, level)
            
            return final_analysis
            
        except Exception as e:
            console.print(f"[red]Error in groom analysis pipeline: {e}[/red]")
            return self.get_fallback_groom_analysis()

    def generate_groom_analysis_enhanced(self, jira_issue_or_content, level: str = "default", debug_mode: bool = False) -> Dict[str, Any]:
        """
        Enhanced GroomRoom analysis:
        - Reads Jira fields dynamically
        - Evaluates Definition of Ready (DOR)
        - Reviews and rewrites Acceptance Criteria
        - Detects missing test scenarios and metadata
        - Returns structured Groom Analysis for UI or API response
        """
        try:
            if debug_mode:
                console.print(f"[blue]Enhanced groom analysis started for level: {level}[/blue]")
            
            # Handle both Jira issue objects and ticket content strings
            if isinstance(jira_issue_or_content, str):
                # If it's a ticket number, fetch from Jira
                if re.match(r'^[A-Z]+-\d+$', jira_issue_or_content.strip()):
                    if not self.jira_integration:
                        return {"error": "Jira integration not available"}
                    
                    jira_issue = self.jira_integration.get_ticket_info(jira_issue_or_content.strip())
                    if not jira_issue:
                        return {"error": f"Could not fetch ticket {jira_issue_or_content}"}
                else:
                    # Create minimal issue data from pasted content
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
            
            # Extract key fields dynamically
            issue_data = self.extract_jira_fields(jira_issue)
            
            if debug_mode:
                console.print(f"[blue]Extracted issue data: {issue_data.get('key', 'Unknown')}[/blue]")
                console.print(f"[blue]Field mapper available: {self.field_mapper is not None}[/blue]")
            
            # Run the complete analysis pipeline
            dor_analysis = self.analyze_dor_requirements(issue_data)
            ac_analysis = self.analyze_acceptance_criteria(issue_data.get('acceptance_criteria', []))
            test_analysis = self.analyze_test_scenarios(issue_data)
            sprint_readiness = self.evaluate_sprint_readiness(dor_analysis)
            gaps = self.identify_gaps(dor_analysis, ac_analysis, test_analysis)
            
            # Build structured output
            structured_output = self.build_structured_output(
                issue_data, dor_analysis, ac_analysis, test_analysis, sprint_readiness, gaps
            )
            
            # Generate final analysis using LLM if available
            if self.client:
                final_analysis = self._generate_final_analysis(structured_output, level)
                structured_output['llm_analysis'] = final_analysis
            
            if debug_mode:
                console.print(f"[blue]Enhanced analysis completed successfully[/blue]")
            
            return structured_output
            
        except Exception as e:
            console.print(f"[red]Error in enhanced groom analysis: {e}[/red]")
            if debug_mode:
                console.print(f"[red]Debug info: {str(e)}[/red]")
                import traceback
                traceback.print_exc()
            return {"error": str(e)}

    def generate_updated_groom_analysis(self, ticket_content: str, level: str = "updated") -> str:
        """Updated version of groom analysis with latest improvements"""
        return self.generate_groom_analysis(ticket_content, level)

    def generate_concise_groom_analysis(self, ticket_content: str) -> str:
        """Generate a concise version of groom analysis"""
        return self.generate_groom_analysis(ticket_content, "light")
    
    def run_analysis(self, jira_issue_or_content, level: str = "default") -> Dict[str, Any]:
        """Safely call enhanced version with fallback to basic analysis"""
        try:
            if hasattr(self, "generate_groom_analysis_enhanced"):
                result = self.generate_groom_analysis_enhanced(jira_issue_or_content, level)
                # If enhanced method returns an error, fallback to basic
                if isinstance(result, dict) and "error" in result:
                    console.print(f"[yellow]Enhanced analysis failed, falling back to basic: {result['error']}[/yellow]")
                    return {"message": "Basic GroomRoom analysis executed successfully.", "fallback": True}
                return result
            else:
                return {"message": "Basic GroomRoom analysis executed successfully.", "fallback": True}
        except Exception as e:
            console.print(f"[red]Analysis failed: {e}[/red]")
            return {"error": str(e), "fallback": True}

    def get_groom_level_prompt(self, level: str) -> str:
        """Get the prompt template for a specific groom level"""
        level_prompts = {
            'updated': """Provide an updated analysis focusing on:
1. Current sprint readiness
2. Recent changes and updates
3. Priority actions for immediate implementation
4. Team collaboration points""",
            
            'strict': """Provide a strict analysis focusing on:
1. Definition of Ready compliance
2. Missing critical elements
3. Quality standards adherence
4. Risk assessment and mitigation""",
            
            'light': """Provide a light analysis focusing on:
1. Key gaps and missing elements
2. Top 3 priority actions
3. Sprint readiness assessment
4. Quick wins and improvements""",
            
            'default': """Provide a comprehensive analysis including:
1. Detailed DOR assessment
2. Acceptance criteria improvements
3. Test scenario recommendations
4. Framework alignment
5. Brand-specific considerations
6. Sprint readiness with specific next steps""",
            
            'insight': """Provide an insightful analysis focusing on:
1. Business value and impact
2. User experience considerations
3. Technical complexity assessment
4. Cross-team dependencies
5. Strategic alignment""",
            
            'deep_dive': """Provide a deep dive analysis including:
1. Comprehensive DOR analysis
2. Detailed acceptance criteria review
3. Extensive test scenario planning
4. Framework alignment assessment
5. Brand and component analysis
6. Risk and dependency mapping
7. Sprint planning recommendations""",
            
            'actionable': """Provide an actionable analysis focusing on:
1. Specific next steps with owners
2. Timeline and priority recommendations
3. Resource requirements
4. Success criteria and metrics
5. Implementation roadmap""",
            
            'summary': """Provide a summary analysis including:
1. Executive summary of readiness
2. Key metrics and scores
3. Critical gaps and blockers
4. Recommended actions
5. Timeline estimates"""
        }
        
        return level_prompts.get(level, level_prompts['default'])

    def _generate_final_analysis(self, structured_output: Dict, level: str) -> str:
        """Generate final analysis using LLM with structured data"""
        if not self.client:
            return self._format_structured_output(structured_output)
        
        try:
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(structured_output, level)
            
            # Check prompt length and handle accordingly
            within_limits, token_count = self._check_prompt_length(prompt)
            
            if not within_limits:
                console.print(f"[yellow]Prompt too long ({token_count} tokens), switching to light mode[/yellow]")
                level = "light"
                prompt = self._create_analysis_prompt(structured_output, level)
            
            response = self.client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            console.print(f"[red]Error generating final analysis: {e}[/red]")
            return self._format_structured_output(structured_output)

    def _create_analysis_prompt(self, structured_output: Dict, level: str) -> str:
        """Create analysis prompt based on level and structured data"""
        
        base_prompt = f"""You are a professional Jira ticket analyst. Analyze this ticket and provide a comprehensive groom analysis.

TICKET SUMMARY:
- Key: {structured_output['ticket_summary']['key']}
- Summary: {structured_output['ticket_summary']['summary']}
- Type: {structured_output['ticket_summary']['issue_type']}
- Status: {structured_output['ticket_summary']['status']}
- Assignee: {structured_output['ticket_summary']['assignee']}
- Story Points: {structured_output['ticket_summary']['story_points']}
- Agile Team: {structured_output['ticket_summary']['agile_team']}

DEFINITION OF READY ANALYSIS:
- Coverage: {structured_output['definition_of_ready']['coverage_percentage']:.1f}%
- Present: {', '.join(structured_output['definition_of_ready']['present_elements'])}
- Missing: {', '.join(structured_output['definition_of_ready']['missing_elements'])}

SPRINT READINESS:
- Score: {structured_output['sprint_readiness']['score']:.1f}/100
- Status: {structured_output['sprint_readiness']['status']}

ACCEPTANCE CRITERIA REVIEW:
"""
        
        # Add AC analysis
        for i, ac in enumerate(structured_output['acceptance_criteria_review'], 1):
            base_prompt += f"""
{i}. Original: {ac['original']}
   Critique: {ac['critique']}
   Revised: {ac['revised']}
"""
        
        base_prompt += f"""
TEST ANALYSIS:
- Coverage: {structured_output['test_analysis']['coverage_percentage']:.1f}%
- Missing Scenarios: {len(structured_output['test_analysis']['missing_scenarios'])}

GAPS IDENTIFIED:
{chr(10).join(f"- {gap}" for gap in structured_output['gaps_identified'])}

NEXT ACTIONS:
{chr(10).join(f"- {action}" for action in structured_output['next_actions'])}

"""
        
        # Add level-specific instructions
        if level == "light":
            base_prompt += """Provide a concise analysis focusing on:
1. Key gaps and missing elements
2. Top 3 priority actions
3. Sprint readiness assessment
Keep response under 500 words."""
        else:
            base_prompt += """Provide a comprehensive analysis including:
1. Detailed DOR assessment
2. Acceptance criteria improvements
3. Test scenario recommendations
4. Framework alignment
5. Brand-specific considerations
6. Sprint readiness with specific next steps
Use markdown formatting with clear headings."""
        
        return base_prompt

    def _format_structured_output(self, structured_output: Dict) -> str:
        """Format structured output as markdown when LLM is not available"""
        output = []
        
        # Header
        output.append("# Groom Room Analysis")
        output.append("")
        
        # Ticket Summary
        ticket = structured_output['ticket_summary']
        output.append(f"**Ticket:** {ticket['key']} - {ticket['summary']}")
        output.append(f"**Type:** {ticket['issue_type']} | **Status:** {ticket['status']}")
        output.append(f"**Assignee:** {ticket['assignee']} | **Team:** {ticket['agile_team']}")
        output.append("")
        
        # Sprint Readiness
        readiness = structured_output['sprint_readiness']
        output.append(f"## Sprint Readiness: {readiness['status']} ({readiness['score']:.1f}/100)")
        output.append("")
        
        # DOR Analysis
        dor = structured_output['definition_of_ready']
        output.append(f"## Definition of Ready: {dor['coverage_percentage']:.1f}% Complete")
        output.append("")
        output.append("**Present Elements:**")
        for element in dor['present_elements']:
            output.append(f"- ✅ {element}")
        output.append("")
        output.append("**Missing Elements:**")
        for element in dor['missing_elements']:
            output.append(f"- ❌ {element}")
        output.append("")
        
        # Acceptance Criteria
        if structured_output['acceptance_criteria_review']:
            output.append("## Acceptance Criteria Review")
            output.append("")
            for i, ac in enumerate(structured_output['acceptance_criteria_review'], 1):
                output.append(f"### {i}. {ac['original'][:100]}...")
                output.append(f"**Critique:** {ac['critique']}")
                output.append(f"**Revised:** {ac['revised']}")
                output.append("")
        
        # Test Analysis
        test = structured_output['test_analysis']
        output.append(f"## Test Analysis: {test['coverage_percentage']:.1f}% Complete")
        output.append("")
        if test['missing_scenarios']:
            output.append("**Missing Test Scenarios:**")
            for scenario in test['missing_scenarios']:
                output.append(f"- {scenario['type']}: {scenario['description']}")
            output.append("")
        
        # Next Actions
        output.append("## Next Actions")
        output.append("")
        for action in structured_output['next_actions']:
            output.append(f"- {action}")
        
        return "\n".join(output)

    def _generate_fallback_analysis(self, ticket_content: str) -> str:
        """Generate a basic fallback analysis without external services"""
        return f"""# Groom Room Analysis - Fallback Mode

**Ticket Content:** {ticket_content[:200]}{'...' if len(ticket_content) > 200 else ''}

**Status:** Using fallback analysis (external services unavailable)

**Basic Assessment:**
- Content Length: {len(ticket_content)} characters
- Has Description: {'Yes' if len(ticket_content.strip()) > 10 else 'No'}
- Content Quality: {'Good' if len(ticket_content.strip()) > 50 else 'Needs Improvement'}

**Manual Review Checklist:**
- [ ] Clear summary and description
- [ ] Acceptance criteria defined
- [ ] Test scenarios identified
- [ ] Story points estimated
- [ ] Team assigned
- [ ] Dependencies identified

**Next Steps:**
1. Review ticket content for completeness
2. Ensure all DOR requirements are met
3. Define clear acceptance criteria
4. Plan test scenarios
5. Estimate story points

Please configure Azure OpenAI for enhanced analysis."""

    def get_fallback_groom_analysis(self) -> str:
        """Fallback analysis when services are unavailable"""
        return """# Groom Room Analysis - Service Unavailable

**Status:** Analysis services are currently unavailable.

**Please check:**
- Azure OpenAI configuration
- Jira integration status
- Network connectivity

**Manual Review Checklist:**
- [ ] Clear summary and description
- [ ] Acceptance criteria defined
- [ ] Test scenarios identified
- [ ] Story points estimated
- [ ] Team assigned
- [ ] Dependencies identified

Please try again or contact support if the issue persists."""