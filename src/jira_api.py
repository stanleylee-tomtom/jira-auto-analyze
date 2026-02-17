"""Jira REST API client for fetching tickets and attachments directly."""

import os
import requests
from typing import Dict, Any, List, Optional
from rich.console import Console
from requests.auth import HTTPBasicAuth

console = Console()


class JiraRestAPI:
    """Direct Jira REST API client using v3 API."""
    
    def __init__(self):
        """Initialize Jira REST API client with credentials from environment."""
        self.cloud_id = os.getenv('ATLASSIAN_CLOUD_ID')
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.base_url = os.getenv('JIRA_SITE_URL', f'https://{self.cloud_id}')
        
        if not all([self.cloud_id, self.api_token, self.email]):
            raise ValueError(
                "Missing required environment variables. "
                "Please set ATLASSIAN_CLOUD_ID, ATLASSIAN_API_TOKEN, and ATLASSIAN_EMAIL"
            )
        
        # Ensure base_url has proper format
        if not self.base_url.startswith('http'):
            self.base_url = f'https://{self.base_url}'
        if not self.base_url.endswith('.atlassian.net') and '.' not in self.cloud_id:
            self.base_url = f'https://{self.cloud_id}.atlassian.net'
        
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def get_issue(self, issue_key: str, expand: str = 'renderedFields') -> Dict[str, Any]:
        """
        Fetch a Jira issue by key.
        
        Args:
            issue_key: Issue key (e.g., PROJ-123)
            expand: Fields to expand (default: renderedFields)
            
        Returns:
            Issue data dictionary
        """
        url = f'{self.base_url}/rest/api/3/issue/{issue_key}'
        params = {'expand': expand}
        
        console.print(f"[dim]Fetching {issue_key} from {self.base_url}...[/dim]")
        
        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Issue {issue_key} not found")
            elif e.response.status_code == 401:
                raise ValueError("Authentication failed. Check your API token and email.")
            else:
                raise ValueError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch issue: {str(e)}")
    
    def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Fetch comments for an issue.
        
        Args:
            issue_key: Issue key
            
        Returns:
            List of comment dictionaries
        """
        url = f'{self.base_url}/rest/api/3/issue/{issue_key}/comment'
        
        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('comments', [])
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]⚠ Could not fetch comments: {str(e)}[/yellow]")
            return []
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum results to return
            
        Returns:
            List of issues
        """
        url = f'{self.base_url}/rest/api/3/search/jql'
        
        try:
            response = requests.post(
                url,
                auth=self.auth,
                headers=self.headers,
                json={'jql': jql, 'maxResults': max_results},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('issues', [])
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]⚠ Search failed: {str(e)}[/yellow]")
            return []
    
    def get_attachments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get attachment metadata for an issue.
        
        Args:
            issue_key: Issue key
            
        Returns:
            List of attachment metadata dictionaries
        """
        issue = self.get_issue(issue_key)
        fields = issue.get('fields', {})
        attachments = fields.get('attachment', [])
        
        return [{
            'id': att.get('id'),
            'filename': att.get('filename'),
            'size': att.get('size'),
            'mimeType': att.get('mimeType'),
            'content': att.get('content'),  # Download URL
            'created': att.get('created')
        } for att in attachments]
    
    def download_attachment(self, url: str, save_path: str) -> bool:
        """
        Download an attachment from URL.
        
        Args:
            url: Attachment content URL
            save_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers={'Accept': '*/*'},
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Failed to download: {str(e)}[/red]")
            return False
    
    def get_issue_formatted(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue in formatted structure for analysis.
        
        Args:
            issue_key: Issue key
            
        Returns:
            Formatted issue data
        """
        issue = self.get_issue(issue_key)
        fields = issue.get('fields', {})
        
        # Get description - try rendered first, fallback to plain
        description = ''
        if 'renderedFields' in issue:
            description = issue['renderedFields'].get('description', '')
        if not description:
            desc_obj = fields.get('description')
            if desc_obj:
                # Handle Atlassian Document Format
                description = self._extract_adf_text(desc_obj)
        
        return {
            'key': issue.get('key'),
            'id': issue.get('id'),
            'summary': fields.get('summary', ''),
            'description': description,
            'status': fields.get('status', {}).get('name', ''),
            'priority': fields.get('priority', {}).get('name', ''),
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'reporter': fields.get('reporter', {}).get('displayName', ''),
            'assignee': fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else 'Unassigned',
            'labels': fields.get('labels', []),
            'components': [c.get('name') for c in fields.get('components', [])],
            'attachments': self.get_attachments(issue_key)
        }
    
    def _extract_adf_text(self, adf: Any) -> str:
        """Extract plain text from Atlassian Document Format."""
        if isinstance(adf, str):
            return adf
        if isinstance(adf, dict):
            if adf.get('type') == 'text':
                return adf.get('text', '')
            if 'content' in adf:
                return ' '.join(self._extract_adf_text(item) for item in adf['content'])
        if isinstance(adf, list):
            return ' '.join(self._extract_adf_text(item) for item in adf)
        return ''
