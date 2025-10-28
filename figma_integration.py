"""
Figma Integration for GroomRoom
Extracts design information from Figma and converts to Jira-like ticket format
"""

import os
import re
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


class FigmaExtractor:
    """Extract design information from Figma API"""
    
    def __init__(self):
        self.figma_token = os.getenv('FIGMA_TOKEN')
        if not self.figma_token:
            raise ValueError("FIGMA_TOKEN not found in environment variables")
        
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            'X-Figma-Token': self.figma_token
        }
    
    def extract_file_key(self, figma_url: str) -> Optional[str]:
        """
        Extract file key from Figma URL
        Examples:
        - https://figma.com/design/ABC123/... -> ABC123
        - https://figma.com/file/ABC123/... -> ABC123
        """
        patterns = [
            r'figma\.com/design/([a-zA-Z0-9]+)',
            r'figma\.com/file/([a-zA-Z0-9]+)',
            r'figma\.com/proto/([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, figma_url)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_figma_file(self, file_key: str) -> Dict[str, Any]:
        """Fetch Figma file data from API"""
        try:
            url = f"{self.base_url}/files/{file_key}"
            response = requests.get(url, headers=self.headers, timeout=30, proxies={'http': None, 'https': None})
            
            if response.status_code == 403:
                raise Exception("Figma API: Access forbidden. Check token permissions.")
            elif response.status_code == 404:
                raise Exception("Figma file not found. Check URL or file permissions.")
            elif response.status_code != 200:
                raise Exception(f"Figma API error: {response.status_code} - {response.text}")
            
            return response.json()
        
        except requests.exceptions.Timeout:
            raise Exception("Figma API timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while fetching Figma file: {str(e)}")
    
    def fetch_figma_comments(self, file_key: str) -> List[Dict[str, Any]]:
        """Fetch comments from Figma file (design notes)"""
        try:
            url = f"{self.base_url}/files/{file_key}/comments"
            response = requests.get(url, headers=self.headers, timeout=30, proxies={'http': None, 'https': None})
            
            if response.status_code == 200:
                return response.json().get('comments', [])
            else:
                print(f"Warning: Could not fetch comments: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"Warning: Error fetching comments: {e}")
            return []
    
    def extract_components(self, node: Dict[str, Any], components: List[str] = None) -> List[str]:
        """Recursively extract component names from Figma file tree"""
        if components is None:
            components = []
        
        # Check if this node is a component
        node_type = node.get('type', '')
        node_name = node.get('name', '')
        
        # Collect component, frame, and important group names
        if node_type in ['COMPONENT', 'COMPONENT_SET', 'INSTANCE']:
            if node_name and node_name not in components:
                components.append(node_name)
        elif node_type == 'FRAME' and node_name:
            # Include frames as they often represent screens/sections
            if node_name not in components and not node_name.startswith('_'):
                components.append(f"Frame: {node_name}")
        
        # Recurse into children
        children = node.get('children', [])
        for child in children:
            self.extract_components(child, components)
        
        return components
    
    def extract_text_layers(self, node: Dict[str, Any], texts: List[str] = None) -> List[str]:
        """Recursively extract text content from Figma file tree"""
        if texts is None:
            texts = []
        
        node_type = node.get('type', '')
        
        # Extract text content
        if node_type == 'TEXT':
            text_content = node.get('characters', '').strip()
            if text_content and text_content not in texts:
                # Filter out single characters and very short text (likely icons)
                if len(text_content) > 2:
                    texts.append(text_content)
        
        # Recurse into children
        children = node.get('children', [])
        for child in children:
            self.extract_text_layers(child, texts)
        
        return texts
    
    def extract_design_notes(self, comments: List[Dict[str, Any]]) -> List[str]:
        """Extract design notes from Figma comments"""
        notes = []
        
        for comment in comments:
            message = comment.get('message', '').strip()
            if message and len(message) > 5:  # Filter out very short comments
                notes.append(message)
        
        return notes
    
    def convert_to_ticket_format(self, figma_url: str) -> Dict[str, Any]:
        """
        Main method: Extract Figma data and convert to Jira-like ticket format
        """
        # Extract file key
        file_key = self.extract_file_key(figma_url)
        if not file_key:
            raise ValueError(f"Invalid Figma URL: {figma_url}")
        
        print(f"📋 Extracting Figma file: {file_key}")
        
        # Fetch file data
        figma_data = self.fetch_figma_file(file_key)
        
        # Extract file name
        file_name = figma_data.get('name', 'Untitled Design')
        
        # Extract components and text
        document = figma_data.get('document', {})
        components = self.extract_components(document)
        text_layers = self.extract_text_layers(document)
        
        # Limit to top 50 components and 50 text layers for performance
        components = components[:50]
        text_layers = text_layers[:50]
        
        # Fetch comments (design notes)
        comments = self.fetch_figma_comments(file_key)
        design_notes = self.extract_design_notes(comments)
        
        print(f"✅ Extracted (limited): {len(components)} components, {len(text_layers)} text layers, {len(design_notes)} design notes")
        
        # Build description content
        description_parts = []
        
        description_parts.append(f"# {file_name}")
        description_parts.append("")
        description_parts.append(f"**Figma Design Link:** {figma_url}")
        description_parts.append("")
        
        # Add components
        if components:
            description_parts.append("## 🧩 Design Components")
            for component in components[:20]:  # Limit to top 20
                description_parts.append(f"- {component}")
            description_parts.append("")
        
        # Add text content
        if text_layers:
            description_parts.append("## 📝 Text Content")
            for text in text_layers[:30]:  # Limit to top 30
                description_parts.append(f"- {text}")
            description_parts.append("")
        
        # Add design notes
        if design_notes:
            description_parts.append("## 💬 Design Notes (from Figma comments)")
            for note in design_notes[:15]:  # Limit to top 15
                description_parts.append(f"- {note}")
            description_parts.append("")
        
        # Add metadata
        description_parts.append("## 📊 Metadata")
        description_parts.append(f"- **Source:** Figma Design")
        description_parts.append(f"- **File Key:** {file_key}")
        description_parts.append(f"- **Components Count:** {len(components)}")
        description_parts.append(f"- **Text Layers:** {len(text_layers)}")
        
        description = "\n".join(description_parts)
        
        # Build Jira-like ticket structure
        ticket_data = {
            'key': f'FIGMA-{file_key[:8].upper()}',
            'fields': {
                'summary': file_name,
                'description': description,
                'issuetype': {'name': 'Story'},
                'project': {'key': 'FIGMA'},
                # Add some extracted data as custom fields
                'customfield_design_components': ', '.join(components[:10]) if components else None,
                'customfield_figma_url': figma_url
            }
        }
        
        return ticket_data


def extract_figma_as_ticket(figma_url: str) -> Dict[str, Any]:
    """
    Public function: Extract Figma design and convert to Jira-like ticket format
    
    Args:
        figma_url: Full Figma URL (e.g., https://figma.com/design/ABC123/...)
    
    Returns:
        Ticket data in Jira format (compatible with GroomRoom analyzer)
    """
    try:
        extractor = FigmaExtractor()
        ticket_data = extractor.convert_to_ticket_format(figma_url)
        return ticket_data
    
    except ValueError as e:
        raise Exception(f"Invalid Figma URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Figma extraction failed: {str(e)}")


# Test function
if __name__ == "__main__":
    # Example usage
    test_url = "https://figma.com/design/ABC123/test-design"
    
    try:
        ticket = extract_figma_as_ticket(test_url)
        print("\n✅ Extraction successful!")
        print(f"Ticket Key: {ticket['key']}")
        print(f"Title: {ticket['fields']['summary']}")
        print(f"\nDescription preview:\n{ticket['fields']['description'][:500]}...")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

