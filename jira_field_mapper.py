"""
Jira Field Mapper Utility
Automatically detects and maps Jira custom field IDs for dynamic field access
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraFieldMapper:
    """Utility class for mapping Jira field names to field IDs dynamically"""
    
    def __init__(self, jira_client=None):
        self.jira_client = jira_client
        self.field_map = {}
        self.cache_file = Path('.cache/jira_fields.json')
        self.cache_file.parent.mkdir(exist_ok=True)
        
    def initialize(self):
        """Initialize field mappings from Jira API or cache"""
        try:
            # Try to load from cache first
            if self._load_from_cache():
                logger.info(f"Loaded {len(self.field_map)} Jira fields from cache")
                return True
            
            # If no cache or jira_client available, use fallback mappings
            if not self.jira_client or not hasattr(self.jira_client, 'get_all_fields'):
                logger.warning("Jira client not available, using fallback field mappings")
                self._load_fallback_mappings()
                return True
            
            # Fetch from Jira API
            fields = self.jira_client.get_all_fields()
            if fields:
                self.field_map = {f["name"].lower(): f["id"] for f in fields}
                self._save_to_cache()
                logger.info(f"Loaded {len(self.field_map)} Jira fields from API")
                return True
            else:
                logger.warning("Failed to fetch fields from Jira API, using fallback")
                self._load_fallback_mappings()
                return True
                
        except Exception as e:
            logger.exception("Failed to initialize field mappings")
            self._load_fallback_mappings()
            return False
    
    def get_field_id(self, field_name: str) -> Optional[str]:
        """Get field ID by field name (case-insensitive)"""
        if not self.field_map:
            self.initialize()
        
        # Try exact match first
        if field_name.lower() in self.field_map:
            return self.field_map[field_name.lower()]
        
        # Try partial matches for common field variations
        field_lower = field_name.lower()
        for mapped_name, field_id in self.field_map.items():
            if field_lower in mapped_name or mapped_name in field_lower:
                logger.info(f"Found partial match: '{field_name}' -> '{mapped_name}' ({field_id})")
                return field_id
        
        logger.warning(f"Field '{field_name}' not found in mappings")
        return None
    
    def get_field_value(self, issue_fields: Dict, field_name: str) -> Any:
        """Get field value from issue fields using dynamic field ID lookup"""
        field_id = self.get_field_id(field_name)
        if field_id and field_id in issue_fields:
            return issue_fields[field_id]
        return None
    
    def get_common_field_ids(self) -> Dict[str, str]:
        """Get common field IDs for GroomRoom analysis"""
        common_fields = [
            'Acceptance Criteria',
            'Test Scenarios', 
            'Story Points',
            'Agile Team',
            'Components',
            'Brands',
            'Figma Reference Status',
            'Cross-browser/Device Testing Scope',
            'Architectural Solution',
            'ADA Acceptance Criteria',
            'Performance Impact'
        ]
        
        field_mappings = {}
        for field_name in common_fields:
            field_id = self.get_field_id(field_name)
            if field_id:
                field_mappings[field_name] = field_id
                logger.info(f"Mapped '{field_name}' -> {field_id}")
            else:
                logger.warning(f"Could not map field: {field_name}")
        
        return field_mappings
    
    def _load_from_cache(self) -> bool:
        """Load field mappings from cache file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cached_data = json.load(f)
                    self.field_map = cached_data.get('field_map', {})
                    return len(self.field_map) > 0
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return False
    
    def _save_to_cache(self):
        """Save field mappings to cache file"""
        try:
            cache_data = {
                'field_map': self.field_map,
                'timestamp': str(Path().cwd())
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info(f"Saved {len(self.field_map)} field mappings to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _load_fallback_mappings(self):
        """Load fallback field mappings for common Jira fields"""
        # Common Jira field mappings (these are standard across most Jira instances)
        fallback_mappings = {
            'summary': 'summary',
            'description': 'description', 
            'status': 'status',
            'priority': 'priority',
            'assignee': 'assignee',
            'reporter': 'reporter',
            'issuetype': 'issuetype',
            'project': 'project',
            'labels': 'labels',
            'components': 'components',
            'created': 'created',
            'updated': 'updated',
            'comments': 'comment',
            'story points': 'customfield_10016',  # Common Story Points field
            'acceptance criteria': 'customfield_10017',  # Common AC field
            'test scenarios': 'customfield_10018',  # Common Test Scenarios field
            'agile team': 'customfield_10020',  # Common Agile Team field
        }
        
        self.field_map = {k.lower(): v for k, v in fallback_mappings.items()}
        logger.info(f"Loaded {len(self.field_map)} fallback field mappings")
    
    def refresh_mappings(self):
        """Force refresh field mappings from Jira API"""
        if self.cache_file.exists():
            self.cache_file.unlink()
        return self.initialize()
    
    def get_mapping_info(self) -> Dict[str, Any]:
        """Get information about current field mappings"""
        return {
            'total_fields': len(self.field_map),
            'custom_fields': len([f for f in self.field_map.values() if f.startswith('customfield_')]),
            'standard_fields': len([f for f in self.field_map.values() if not f.startswith('customfield_')]),
            'cache_file': str(self.cache_file),
            'cache_exists': self.cache_file.exists()
        }
