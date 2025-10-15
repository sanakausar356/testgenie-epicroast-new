"""
Core Groom Room functionality for professional Jira ticket analysis
"""

import os
import sys
import re
import hashlib
import json
from typing import Optional, Dict, List, Any, Tuple
from dotenv import load_dotenv
from rich.console import Console
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
            'summary': {
                'name': 'Summary',
                'description': 'Clear, concise ticket title',
                'required': True
            },
            'description': {
                'name': 'Description',
                'description': 'Detailed ticket description with context',
                'required': True
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
                ],
                'required': True
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
                'cross_browser_device': 'Cross-browser/device testing required? Y/N',
                'required': True
            },
            'additional_fields': {
                'name': 'Additional Card Details',
                'fields': [
                    'Brand(s)',
                    'Component(s)',
                    'Agile Team',
                    'Story Points',
                    'Figma Link',
                    'Dependencies'
                ],
                'required': True
            }
        }
        
        # Card types and their requirements
        self.card_types = {
            'user_story': {
                'name': 'User Story',
                'description': 'New functionality, enhancements, scope changes, technical enhancements',
                'requirements': ['Feature tie', 'Business value', 'User story template']
            },
            'bug': {
                'name': 'Bug',
                'description': 'Defects in existing functionality',
                'requirements': ['Clear details', 'Environment', 'Replication steps', 'Expected behavior', 'Feature tie']
            },
            'task': {
                'name': 'Task',
                'description': 'Enabling/disabling configs or documentation creation',
                'requirements': ['Clear scope', 'Deliverables', 'Acceptance criteria']
            }
        }
        
        # Bug requirements for detailed analysis
        self.bug_requirements = {
            'environment': 'Environment where bug occurs',
            'replication_steps': 'Step-by-step replication instructions',
            'expected_behavior': 'What should happen',
            'actual_behavior': 'What actually happens',
            'feature_tie': 'Which feature introduced this bug'
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
                'story_points': fields.get('customfield_10016', None),  # Story Points field
                'acceptance_criteria': self._extract_acceptance_criteria(fields),
                'test_scenarios': self._extract_test_scenarios(fields),
                'figma_links': self._extract_figma_links(fields),
                'attachments': self._extract_attachments(fields),
                'linked_issues': self._extract_linked_issues(fields),
                'comments': self._extract_comments(fields),
                'agile_team': self._extract_agile_team(fields),
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
        
        # Check custom fields for AC
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
        
        # Check custom fields for test scenarios
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