"""Analysis orchestrator that coordinates ticket fetching, log processing, and Copilot analysis."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .jira_client import JiraClient
from .log_processor import LogProcessor
from .filter import LogFilter

console = Console()


class TicketAnalyzer:
    """Orchestrates the analysis of Jira tickets."""
    
    def __init__(self, options: Dict[str, Any]):
        """
        Initialize analyzer with options.
        
        Args:
            options: Configuration options including keywords, filters, etc.
        """
        self.options = options
        self.jira_client = JiraClient()
        self.log_processor = LogProcessor()
        
        # Setup filter
        keywords = options.get('keywords', [])
        context_lines = options.get('context_lines', 5)
        self.log_filter = LogFilter(
            keywords=keywords,
            context_lines_before=context_lines,
            context_lines_after=context_lines
        )
    
    def analyze(self, ticket_id: str) -> Dict[str, Any]:
        """
        Analyze a Jira ticket.
        
        Args:
            ticket_id: Jira ticket ID
            
        Returns:
            Analysis result
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Step 1: Fetch ticket data
            task1 = progress.add_task("Fetching ticket data...", total=None)
            ticket_data = self._fetch_ticket_data(ticket_id)
            progress.update(task1, completed=True)
            
            # Step 2: Process attachments
            if not self.options.get('no_attachments'):
                task2 = progress.add_task("Processing attachments...", total=None)
                logs = self._process_attachments(ticket_data)
                progress.update(task2, completed=True)
            else:
                logs = []
            
            # Step 3: Filter and optimize logs
            task3 = progress.add_task("Filtering logs...", total=None)
            filtered_logs = self._filter_logs(logs)
            progress.update(task3, completed=True)
            
            # Step 4: Prepare analysis input
            task4 = progress.add_task("Preparing analysis...", total=None)
            analysis_input = self._prepare_analysis_input(ticket_data, filtered_logs)
            progress.update(task4, completed=True)
        
        # Display what will be analyzed
        self._display_analysis_preview(ticket_data, filtered_logs)
        
        return {
            'ticket_id': ticket_id,
            'ticket_data': ticket_data,
            'logs': filtered_logs,
            'analysis_input': analysis_input,
            'skill_file': str(Path(__file__).parent.parent / 'skills' / 'jira_analyzer.md')
        }
    
    def _fetch_ticket_data(self, ticket_id: str) -> Dict[str, Any]:
        """Fetch ticket data from Jira."""
        console.print(f"[dim]Fetching ticket {ticket_id}...[/dim]")
        
        # Note: This would use Atlassian MCP tools in the actual Copilot CLI environment
        # For now, return a structure that the skill will populate
        return {
            'id': ticket_id,
            'key': ticket_id,
            'summary': '',
            'description': '',
            'status': '',
            'priority': '',
            'comments': [],
            'attachments': []
        }
    
    def _process_attachments(self, ticket_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process ticket attachments."""
        attachments = ticket_data.get('attachments', [])
        
        if not attachments:
            console.print("[dim]No attachments found[/dim]")
            return []
        
        all_logs = []
        for attachment in attachments:
            # In actual implementation, download and process
            # For now, this is a placeholder
            pass
        
        return all_logs
    
    def _filter_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter logs based on keywords and optimize for token usage."""
        if not logs:
            return []
        
        filtered_logs = []
        max_lines = self.options.get('max_lines', 500)
        max_tokens = self.options.get('max_tokens', 4000)
        
        for log in logs:
            content = log.get('content', '')
            
            # Apply keyword filtering
            filtered_result = self.log_filter.filter_log(content, max_lines=max_lines)
            
            # Optimize for token limit
            optimized = self.log_filter.optimize_for_token_limit(
                filtered_result['content'],
                max_tokens=max_tokens,
                strategy='smart'
            )
            
            filtered_logs.append({
                'filename': log['filename'],
                'original_lines': log.get('lines', 0),
                'filtered_lines': filtered_result['filtered_lines'],
                'matched_lines': filtered_result['matched_lines'],
                'content': optimized['content'],
                'estimated_tokens': optimized['final_tokens'],
                'optimized': optimized['optimized'],
                'strategy': optimized.get('strategy')
            })
        
        return filtered_logs
    
    def _prepare_analysis_input(
        self, 
        ticket_data: Dict[str, Any], 
        filtered_logs: List[Dict[str, Any]]
    ) -> str:
        """Prepare input text for Copilot analysis."""
        lines = []
        
        # Ticket header
        lines.append(f"TICKET: {ticket_data['key']}")
        lines.append(f"SUMMARY: {ticket_data.get('summary', 'N/A')}")
        lines.append(f"STATUS: {ticket_data.get('status', 'N/A')}")
        lines.append(f"PRIORITY: {ticket_data.get('priority', 'N/A')}")
        lines.append("")
        
        # Description
        if ticket_data.get('description'):
            lines.append("DESCRIPTION:")
            lines.append(ticket_data['description'])
            lines.append("")
        
        # Comments
        comments = ticket_data.get('comments', [])
        if comments:
            lines.append("COMMENTS:")
            for comment in comments[:10]:  # Limit to 10 most recent
                author = comment.get('author', 'Unknown')
                body = comment.get('body', '')
                lines.append(f"- {author}: {body}")
            lines.append("")
        
        # Log files
        if filtered_logs:
            lines.append("LOG FILES:")
            for log in filtered_logs:
                lines.append(f"\n--- {log['filename']} ---")
                lines.append(f"(Showing {log['filtered_lines']} of {log['original_lines']} lines, "
                           f"~{log['estimated_tokens']} tokens)")
                if log['matched_lines'] > 0:
                    lines.append(f"(Matched {log['matched_lines']} keyword occurrences)")
                lines.append("")
                lines.append(log['content'])
                lines.append("")
        
        return '\n'.join(lines)
    
    def _display_analysis_preview(
        self, 
        ticket_data: Dict[str, Any], 
        filtered_logs: List[Dict[str, Any]]
    ):
        """Display preview of what will be analyzed."""
        console.print("\n[bold]Analysis Preview:[/bold]")
        console.print(f"  Ticket: [cyan]{ticket_data['key']}[/cyan]")
        
        if filtered_logs:
            total_tokens = sum(log['estimated_tokens'] for log in filtered_logs)
            console.print(f"  Log files: [cyan]{len(filtered_logs)}[/cyan]")
            console.print(f"  Estimated tokens: [cyan]~{total_tokens}[/cyan]")
            
            for log in filtered_logs:
                status = "✓ optimized" if log['optimized'] else "✓"
                console.print(f"    - {log['filename']}: {log['filtered_lines']} lines ({status})")
        else:
            console.print("  Log files: [yellow]None[/yellow]")
        
        console.print("")


def analyze_ticket(options: Dict[str, Any]) -> str:
    """
    Main entry point for ticket analysis.
    
    This function coordinates the entire analysis process:
    1. Fetch ticket data from Jira
    2. Process and filter log files
    3. Prepare input for Copilot
    4. Return formatted result
    
    Args:
        options: Analysis options
        
    Returns:
        Analysis result or path to skill invocation
    """
    analyzer = TicketAnalyzer(options)
    result = analyzer.analyze(options['ticket_id'])
    
    # Save analysis input to temp file
    temp_file = Path(tempfile.gettempdir()) / f"jira_analysis_{result['ticket_id']}.txt"
    with open(temp_file, 'w') as f:
        f.write(result['analysis_input'])
    
    console.print(f"[dim]Analysis input saved to: {temp_file}[/dim]")
    console.print("")
    console.print("[bold yellow]To complete the analysis, run:[/bold yellow]")
    console.print(f"[cyan]gh copilot --skill {result['skill_file']} < {temp_file}[/cyan]")
    console.print("")
    console.print("[dim]Or copy the skill file path and analysis input to use with @jira_analyzer skill[/dim]")
    
    return result['analysis_input']
