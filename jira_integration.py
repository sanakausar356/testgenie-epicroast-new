"""
Jira Integration Module
"""

import os
import sys
import base64
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from rich.console import Console
import requests

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

class JiraIntegration:
    """Jira integration for fetching ticket information using REST API"""
    
    def __init__(self):
        self.base_url = None
        self.auth_header = None
        self.setup_jira_client()
    
    def setup_jira_client(self):
        """Initialize Jira client using REST API"""
        try:
            jira_url = os.getenv('JIRA_URL')
            jira_username = os.getenv('JIRA_USERNAME')
            jira_api_token = os.getenv('JIRA_API_TOKEN')
            
            if not all([jira_url, jira_username, jira_api_token]):
                console.print("[yellow]Warning: Jira credentials not found in .env file[/yellow]")
                console.print("Jira integration will be disabled. Add these variables to enable:")
                console.print("- JIRA_URL")
                console.print("- JIRA_USERNAME")
                console.print("- JIRA_API_TOKEN")
                return
            
            # Clean up URL
            self.base_url = jira_url.rstrip('/')
            
            # Create auth header
            auth_string = f"{jira_username}:{jira_api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            self.auth_header = f"Basic {auth_b64}"
            
            # Test connection
            self._test_connection()
            console.print("[green]✅ Jira connection successful[/green]")
            
        except Exception as e:
            console.print(f"[red]Error setting up Jira client: {e}[/red]")
            self.base_url = None
            self.auth_header = None
    
    def _test_connection(self):
        """Test Jira connection"""
        headers = {
            'Authorization': self.auth_header,
            'Accept': 'application/json'
        }
        
        response = requests.get(f"{self.base_url}/rest/api/3/myself", headers=headers)
        response.raise_for_status()
    
    def is_available(self) -> bool:
        """Check if Jira integration is available"""
        return self.base_url is not None and self.auth_header is not None
    
    def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make a request to Jira REST API"""
        if not self.is_available():
            return None
        
        headers = {
            'Authorization': self.auth_header,
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            console.print(f"[blue]Response status: {response.status_code}[/blue]")
            
            # Check if response is successful
            if response.status_code == 404:
                console.print(f"[red]Ticket not found (404)[/red]")
                return None
            elif response.status_code == 403:
                console.print(f"[red]Access denied (403) - Check ticket permissions[/red]")
                return None
            elif response.status_code != 200:
                console.print(f"[red]API request failed with status {response.status_code}[/red]")
                return None
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                console.print(f"[red]Invalid JSON response: {e}[/red]")
                console.print(f"[yellow]Response content: {response.text[:200]}...[/yellow]")
                return None
            except Exception as e:
                console.print(f"[red]Unexpected error parsing response: {e}[/red]")
                return None
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API request failed: {e}[/red]")
            return None
    
    def get_ticket_info(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """Fetch ticket information by ticket number"""
        if not self.is_available():
            console.print("[red]Jira integration is not available[/red]")
            return None
        
        try:
            # Clean ticket number
            clean_ticket = ticket_number.upper().strip()
            console.print(f"[blue]Fetching ticket {clean_ticket}...[/blue]")
            
            # Fetch the issue
            endpoint = f"/rest/api/3/issue/{clean_ticket}"
            issue_data = self._make_request(endpoint)
            
            console.print(f"[blue]API response received: {issue_data is not None}[/blue]")
            
            if issue_data is None:
                console.print(f"[red]Ticket {ticket_number} not found or access denied[/red]")
                return None
            
            console.print(f"[blue]Issue data keys: {list(issue_data.keys()) if issue_data else 'None'}[/blue]")
            
            # Extract relevant information
            fields = issue_data.get('fields', {})
            console.print(f"[blue]Fields data: {fields is not None}[/blue]")
            
            if not fields:
                console.print(f"[red]No fields data found in ticket {ticket_number}[/red]")
                return None
            
            console.print(f"[blue]Creating ticket info...[/blue]")
            
            # Safely get nested values with explicit None checks
            status_obj = fields.get('status')
            priority_obj = fields.get('priority')
            assignee_obj = fields.get('assignee')
            reporter_obj = fields.get('reporter')
            issue_type_obj = fields.get('issuetype')
            project_obj = fields.get('project')
            
            ticket_info = {
                'key': issue_data.get('key', ''),
                'summary': fields.get('summary', ''),
                'description': fields.get('description', ''),
                'status': status_obj.get('name', 'Unknown') if status_obj else 'Unknown',
                'priority': priority_obj.get('name', 'None') if priority_obj else 'None',
                'assignee': assignee_obj.get('displayName', 'Unassigned') if assignee_obj else 'Unassigned',
                'reporter': reporter_obj.get('displayName', 'Unknown') if reporter_obj else 'Unknown',
                'created': fields.get('created', ''),
                'updated': fields.get('updated', ''),
                'issue_type': issue_type_obj.get('name', 'Unknown') if issue_type_obj else 'Unknown',
                'project': project_obj.get('name', 'Unknown') if project_obj else 'Unknown',
                'labels': fields.get('labels', []),
                'components': [c.get('name', '') for c in fields.get('components', [])],
                'comments': []
            }
            
            console.print(f"[blue]Ticket info created successfully[/blue]")
            
            # Fetch comments
            comments_endpoint = f"/rest/api/3/issue/{clean_ticket}/comment"
            comments_data = self._make_request(comments_endpoint)
            
            if comments_data:
                for comment in comments_data.get('comments', []):
                    ticket_info['comments'].append({
                        'author': comment.get('author', {}).get('displayName', 'Unknown'),
                        'body': comment.get('body', ''),
                        'created': comment.get('created', '')
                    })
            
            return ticket_info
            
        except Exception as e:
            console.print(f"[red]Unexpected error fetching ticket {ticket_number}: {e}[/red]")
            return None
    
    def format_ticket_for_display(self, ticket_info: Dict[str, Any]) -> str:
        """Format ticket information for display"""
        if not ticket_info:
            return "No ticket information available"
        
        formatted = f"""
# Jira Ticket: {ticket_info['key']}

## Summary
{ticket_info['summary']}

## Description
{ticket_info['description']}

## Details
- **Status**: {ticket_info['status']}
- **Priority**: {ticket_info['priority']}
- **Type**: {ticket_info['issue_type']}
- **Project**: {ticket_info['project']}
- **Assignee**: {ticket_info['assignee']}
- **Reporter**: {ticket_info['reporter']}
- **Created**: {ticket_info['created']}
- **Updated**: {ticket_info['updated']}

## Labels
{', '.join(ticket_info['labels']) if ticket_info['labels'] else 'None'}

## Components
{', '.join(ticket_info['components']) if ticket_info['components'] else 'None'}

## Comments ({len(ticket_info['comments'])})
"""
        
        for i, comment in enumerate(ticket_info['comments'], 1):
            formatted += f"""
### Comment {i} by {comment['author']} ({comment['created']})
{comment['body']}
"""
        
        return formatted
    
    def format_ticket_for_analysis(self, ticket_info: Dict[str, Any]) -> str:
        """Format ticket information for AI analysis (TestGenie/Epic Roast)"""
        if not ticket_info:
            return "No ticket information available"
        
        formatted = f"""
Jira Ticket: {ticket_info['key']}
Summary: {ticket_info['summary']}
Status: {ticket_info['status']}
Priority: {ticket_info['priority']}
Type: {ticket_info['issue_type']}
Project: {ticket_info['project']}
Assignee: {ticket_info['assignee']}
Reporter: {ticket_info['reporter']}

Description:
{ticket_info['description']}

Labels: {', '.join(ticket_info['labels']) if ticket_info['labels'] else 'None'}
Components: {', '.join(ticket_info['components']) if ticket_info['components'] else 'None'}

Comments ({len(ticket_info['comments'])}):
"""
        
        for i, comment in enumerate(ticket_info['comments'], 1):
            formatted += f"""
Comment {i} by {comment['author']}:
{comment['body']}
"""
        
        return formatted
    
    def search_tickets(self, query: str, max_results: int = 10) -> list:
        """Search for tickets using JQL"""
        if not self.is_available():
            console.print("[red]Jira integration is not available[/red]")
            return []
        
        try:
            endpoint = f"/rest/api/3/search"
            params = {
                'jql': query,
                'maxResults': max_results,
                'fields': 'summary,status,assignee'
            }
            
            headers = {
                'Authorization': self.auth_header,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(f"{self.base_url}{endpoint}", 
                                   headers=headers, 
                                   params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for issue in data.get('issues', []):
                fields = issue.get('fields', {})
                results.append({
                    'key': issue.get('key', ''),
                    'summary': fields.get('summary', ''),
                    'status': fields.get('status', {}).get('name', 'Unknown'),
                    'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned')
                })
            
            return results
            
        except Exception as e:
            console.print(f"[red]Error searching tickets: {e}[/red]")
            return []

    def get_dashboard_cards(self, team_filter: str = 'all', status_filter: str = 'all') -> list:
        """Get Jira dashboard cards for the web interface"""
        if not self.is_available():
            console.print("[red]Jira integration is not available[/red]")
            return self._get_mock_dashboard_cards()
        
        try:
            # Define team to board mapping with labels
            team_board_mapping = {
                'odcd-everest': { 'boardId': '1806', 'projectKey': 'ODCD', 'labels': ['everest', 'odcd-everest', 'GTM', 'MarTech'] },
                'odcd-silver-surfers': { 'boardId': '1558', 'projectKey': 'ODCD', 'labels': ['silver-surfers', 'odcd-silver-surfers', 'SFMC', 'AMS-SFMC'] },
                'the-batman': { 'boardId': '400', 'projectKey': 'ODCD', 'labels': ['batman', 'the-batman', 'ODCD-Batman', 'BatmanRadar', 'batman-portal'] },
                'everest-pwa-kit': { 'boardId': '1772', 'projectKey': 'ODCD', 'labels': ['pwa-kit', 'everest-pwa-kit', 'PWA'] }
            }
            
            # Define status filters
            status_filters = {
                'ready-to-groom': ['To Groom'],
                'ready-for-dev': ['Ready For Dev']
            }
            
            # Build JQL query
            project_keys = list(set([config['projectKey'] for config in team_board_mapping.values()]))  # Remove duplicates
            jql_parts = [f"project in ({', '.join(project_keys)})"]
            
            # Add status filter
            if status_filter in status_filters:
                status_list = status_filters[status_filter]
                jql_parts.append(f'status in ("{", ".join(status_list)}")')
            
            jql = " AND ".join(jql_parts) + " ORDER BY created DESC"
            
            console.print(f"[blue]Using JQL: {jql}[/blue]")
            
            endpoint = f"/rest/api/3/search"
            params = {
                'jql': jql,
                'maxResults': 50,
                'fields': 'summary,status,priority,assignee,issuetype,created,description,project,labels'
            }
            
            headers = {
                'Authorization': self.auth_header,
                'Accept': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}{endpoint}", 
                                   headers=headers, 
                                   params=params)
            response.raise_for_status()
            
            console.print(f"[blue]Response status: {response.status_code}[/blue]")
            console.print(f"[blue]Response content: {response.text[:200]}...[/blue]")
            
            try:
                data = response.json()
                console.print(f"[blue]Parsed JSON data: {data is not None}[/blue]")
                if data:
                    console.print(f"[blue]Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}[/blue]")
            except Exception as json_error:
                console.print(f"[red]JSON parsing error: {json_error}[/red]")
                console.print(f"[red]Response text: {response.text}[/red]")
                data = None
            cards = []
            
            console.print(f"[blue]Processing {len(data.get('issues', []))} issues[/blue]")
            
            for issue in data.get('issues', []):
                console.print(f"[blue]Processing issue: {issue.get('key', 'Unknown')}[/blue]")
                fields = issue.get('fields', {})
                console.print(f"[blue]Fields: {fields is not None}[/blue]")
                
                project_obj = fields.get('project', {})
                console.print(f"[blue]Project object: {project_obj is not None}[/blue]")
                project_key = project_obj.get('key', 'ODCD') if project_obj else 'ODCD'
                
                # Determine team from labels and summary
                team = 'unknown'
                ticket_labels = fields.get('labels', [])
                ticket_summary = fields.get('summary', '').lower()
                console.print(f"[blue]Ticket labels: {ticket_labels}[/blue]")
                console.print(f"[blue]Ticket summary: {ticket_summary}[/blue]")
                
                # First try to match by labels
                for team_name, config in team_board_mapping.items():
                    team_labels = config.get('labels', [])
                    if any(label in ticket_labels for label in team_labels):
                        team = team_name
                        console.print(f"[blue]Matched team by labels: {team_name}[/blue]")
                        break
                
                # If no label match, try to match by summary keywords
                if team == 'unknown':
                    if any(keyword in ticket_summary for keyword in ['gtm', 'martech', 'tagging', 'analytics', 'data layer']):
                        team = 'odcd-everest'
                        console.print(f"[blue]Matched team by summary (Everest): {team}[/blue]")
                    elif any(keyword in ticket_summary for keyword in ['sfmc', 'ams-sfmc', 'dev_sfmc', 'loyalty']):
                        team = 'odcd-silver-surfers'
                        console.print(f"[blue]Matched team by summary (Silver Surfers): {team}[/blue]")
                    elif any(keyword in ticket_summary for keyword in ['batman', 'batmanradar', 'batman-portal']):
                        team = 'the-batman'
                        console.print(f"[blue]Matched team by summary (Batman): {team}[/blue]")
                    elif any(keyword in ticket_summary for keyword in ['pwa', 'pwa kit']):
                        team = 'everest-pwa-kit'
                        console.print(f"[blue]Matched team by summary (PWA Kit): {team}[/blue]")
                
                # Apply team filter
                if team_filter != 'all' and team != team_filter:
                    continue
                
                # Safely get nested fields
                status_obj = fields.get('status', {})
                priority_obj = fields.get('priority', {})
                assignee_obj = fields.get('assignee', {})
                issue_type_obj = fields.get('issuetype', {})
                
                console.print(f"[blue]Status object: {status_obj is not None}[/blue]")
                console.print(f"[blue]Priority object: {priority_obj is not None}[/blue]")
                console.print(f"[blue]Assignee object: {assignee_obj is not None}[/blue]")
                console.print(f"[blue]Issue type object: {issue_type_obj is not None}[/blue]")
                
                card = {
                    'key': issue.get('key', ''),
                    'summary': fields.get('summary', ''),
                    'status': status_obj.get('name', 'Unknown') if status_obj else 'Unknown',
                    'priority': priority_obj.get('name', 'Medium') if priority_obj else 'Medium',
                    'assignee': assignee_obj.get('displayName', 'Unassigned') if assignee_obj else 'Unassigned',
                    'project': project_key,
                    'issueType': issue_type_obj.get('name', 'Story') if issue_type_obj else 'Story',
                    'created': fields.get('created', ''),
                    'description': fields.get('description', ''),
                    'team': team
                }
                cards.append(card)
            
            console.print(f"[green]Successfully fetched {len(cards)} cards[/green]")
            return cards
            
        except Exception as e:
            console.print(f"[red]Error fetching dashboard cards: {e}[/red]")
            return self._get_mock_dashboard_cards()

    def get_available_teams(self) -> list:
        """Get available Jira teams"""
        return [
            { 'key': 'all', 'name': 'All Scrum Teams' },
            { 'key': 'odcd-everest', 'name': 'ODCD - Everest' },
            { 'key': 'odcd-silver-surfers', 'name': 'ODCD - Silver Surfers Scrum' },
            { 'key': 'the-batman', 'name': 'The Batman' },
            { 'key': 'everest-pwa-kit', 'name': 'Everest - PWA Kit Upgrade Project' }
        ]

    def get_available_statuses(self) -> list:
        """Get available Jira statuses"""
        return [
            { 'key': 'all', 'name': 'All Statuses' },
            { 'key': 'ready-to-groom', 'name': 'Ready to Groom' },
            { 'key': 'ready-for-dev', 'name': 'Ready for Dev' }
        ]

    def _get_mock_dashboard_cards(self) -> list:
        """Get mock dashboard cards for fallback"""
        return [
            {
                'key': 'ODCD-33741',
                'summary': 'Implement user authentication flow',
                'status': 'To Groom',
                'priority': 'High',
                'assignee': 'John Doe',
                'project': 'ODCD',
                'issueType': 'Story',
                'created': '2024-01-15',
                'team': 'odcd-everest'
            },
            {
                'key': 'ODCD-33742',
                'summary': 'Add payment gateway integration',
                'status': 'Ready For Dev',
                'priority': 'Medium',
                'assignee': 'Jane Smith',
                'project': 'ODCD',
                'issueType': 'Story',
                'created': '2024-01-16',
                'team': 'odcd-everest'
            },
            {
                'key': 'ODCD-33743',
                'summary': 'Upgrade PWA Kit to latest version',
                'status': 'To Groom',
                'priority': 'High',
                'assignee': 'Mike Johnson',
                'project': 'ODCD',
                'issueType': 'Epic',
                'created': '2024-01-14',
                'team': 'everest-pwa-kit'
            },
            {
                'key': 'ODCD-33744',
                'summary': 'Implement dark mode feature',
                'status': 'Ready For Dev',
                'priority': 'Low',
                'assignee': 'Sarah Wilson',
                'project': 'ODCD',
                'issueType': 'Story',
                'created': '2024-01-17',
                'team': 'the-batman'
            },
            {
                'key': 'ODCD-33745',
                'summary': 'Optimize database queries',
                'status': 'To Groom',
                'priority': 'High',
                'assignee': 'Alex Brown',
                'project': 'ODCD',
                'issueType': 'Task',
                'created': '2024-01-18',
                'team': 'odcd-silver-surfers'
            }
        ] 