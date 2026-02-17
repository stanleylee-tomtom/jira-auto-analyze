"""Attachment downloader with progress tracking."""

import os
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from .jira_api import JiraRestAPI

console = Console()


class AttachmentDownloader:
    """Downloads and organizes Jira attachments."""
    
    def __init__(self, base_dir: str = "./analysis_results"):
        """
        Initialize downloader.
        
        Args:
            base_dir: Base directory for downloads
        """
        self.base_dir = Path(base_dir)
        self.jira_api = JiraRestAPI()
    
    def download_all(self, issue_key: str, attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Download all attachments for an issue.
        
        Args:
            issue_key: Jira issue key
            attachments: List of attachment metadata
            
        Returns:
            Download summary with paths and stats
        """
        if not attachments:
            console.print("[dim]No attachments to download[/dim]")
            return {'downloaded': 0, 'failed': 0, 'files': []}
        
        # Create issue directory
        issue_dir = self.base_dir / issue_key / 'attachments'
        issue_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n[cyan]📥 Downloading {len(attachments)} attachment(s)...[/cyan]")
        
        downloaded_files = []
        failed_files = []
        
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            for att in attachments:
                filename = att['filename']
                file_path = issue_dir / filename
                
                # Skip if already downloaded
                if file_path.exists() and file_path.stat().st_size == att['size']:
                    console.print(f"[dim]✓ {filename} (already exists)[/dim]")
                    downloaded_files.append(str(file_path))
                    continue
                
                # Download
                task = progress.add_task(f"[cyan]{filename}", total=att['size'])
                
                try:
                    success = self._download_with_progress(
                        att['content'],
                        file_path,
                        progress,
                        task
                    )
                    
                    if success:
                        downloaded_files.append(str(file_path))
                        console.print(f"[green]✓ {filename}[/green]")
                    else:
                        failed_files.append(filename)
                except Exception as e:
                    console.print(f"[red]✗ {filename}: {str(e)}[/red]")
                    failed_files.append(filename)
                finally:
                    progress.remove_task(task)
        
        # Summary
        summary = {
            'downloaded': len(downloaded_files),
            'failed': len(failed_files),
            'total': len(attachments),
            'files': downloaded_files,
            'failed_files': failed_files,
            'directory': str(issue_dir)
        }
        
        console.print(f"\n[green]✓ Downloaded {len(downloaded_files)}/{len(attachments)} files[/green]")
        if failed_files:
            console.print(f"[yellow]⚠ Failed: {', '.join(failed_files)}[/yellow]")
        
        return summary
    
    def _download_with_progress(
        self, 
        url: str, 
        save_path: Path,
        progress: Progress,
        task_id: Any
    ) -> bool:
        """Download file with progress tracking."""
        import requests
        
        try:
            response = requests.get(
                url,
                auth=self.jira_api.auth,
                headers={'Accept': '*/*'},
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))
            
            return True
        except Exception as e:
            console.print(f"[red]Download error: {str(e)}[/red]")
            return False
    
    def get_downloadable_attachments(self, attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter attachments to only include downloadable types.
        
        Args:
            attachments: List of all attachments
            
        Returns:
            List of downloadable attachments (logs, text files, zips)
        """
        downloadable_types = {
            'text/plain',
            'application/x-log',
            'application/log',
            'application/zip',
            'application/x-zip-compressed',
            'application/gzip',
            'application/x-gzip',
            'application/x-tar',
            'text/x-log'
        }
        
        downloadable_extensions = {
            '.log', '.txt', '.out', '.err', '.trace',
            '.zip', '.gz', '.tar', '.tgz'
        }
        
        filtered = []
        for att in attachments:
            mime_type = att.get('mimeType', '')
            filename = att.get('filename', '')
            ext = Path(filename).suffix.lower()
            
            if mime_type in downloadable_types or ext in downloadable_extensions:
                filtered.append(att)
            else:
                console.print(f"[dim]Skipping {filename} ({mime_type})[/dim]")
        
        return filtered
    
    def save_ticket_data(self, issue_key: str, ticket_data: Dict[str, Any], comments: List[Dict[str, Any]]):
        """
        Save ticket metadata to file.
        
        Args:
            issue_key: Issue key
            ticket_data: Formatted ticket data
            comments: List of comments
        """
        issue_dir = self.base_dir / issue_key
        issue_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_file = issue_dir / 'ticket_metadata.txt'
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"TICKET: {ticket_data['key']}\n")
            f.write(f"SUMMARY: {ticket_data['summary']}\n")
            f.write(f"STATUS: {ticket_data['status']}\n")
            f.write(f"PRIORITY: {ticket_data['priority']}\n")
            f.write(f"REPORTER: {ticket_data['reporter']}\n")
            f.write(f"ASSIGNEE: {ticket_data['assignee']}\n")
            f.write(f"CREATED: {ticket_data['created']}\n")
            f.write(f"UPDATED: {ticket_data['updated']}\n")
            
            if ticket_data.get('labels'):
                f.write(f"LABELS: {', '.join(ticket_data['labels'])}\n")
            
            if ticket_data.get('components'):
                f.write(f"COMPONENTS: {', '.join(ticket_data['components'])}\n")
            
            f.write(f"\nDESCRIPTION:\n{ticket_data['description']}\n")
            
            if comments:
                f.write(f"\n\nCOMMENTS ({len(comments)}):\n")
                for i, comment in enumerate(comments, 1):
                    author = comment.get('author', {}).get('displayName', 'Unknown')
                    created = comment.get('created', '')
                    body = comment.get('body', '')
                    
                    # Extract text from ADF if needed
                    if isinstance(body, dict):
                        body = self._extract_adf_text(body)
                    
                    f.write(f"\n--- Comment {i} by {author} at {created} ---\n")
                    f.write(f"{body}\n")
        
        console.print(f"[dim]✓ Saved metadata to {metadata_file}[/dim]")
    
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
