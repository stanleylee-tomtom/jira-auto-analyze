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
        """Fetch ticket data from Jira.
        
        Note: This creates a placeholder. The actual ticket fetching should be done
        by GitHub Copilot CLI using Atlassian MCP tools when you ask:
        
        "Fetch and analyze Jira ticket {ticket_id} using my credentials"
        
        For now, this returns a template that reminds you to fetch via Copilot.
        """
        console.print(f"[yellow]⚠ Ticket data fetch requires GitHub Copilot CLI with Atlassian MCP[/yellow]")
        console.print(f"[dim]Creating analysis template for {ticket_id}...[/dim]")
        
        return {
            'id': ticket_id,
            'key': ticket_id,
            'summary': f'[ASK COPILOT: Fetch summary for {ticket_id}]',
            'description': f'[ASK COPILOT: Fetch description for {ticket_id}]',
            'status': '[TO BE FETCHED]',
            'priority': '[TO BE FETCHED]',
            'comments': ['[ASK COPILOT: Fetch comments using atlassian-getJiraIssue]'],
            'attachments': ['[ASK COPILOT: List attachments and download log files]'],
            'note': f'To fetch real data, ask Copilot: "Fetch Jira ticket {ticket_id} from cloudId {os.getenv("ATLASSIAN_CLOUD_ID")}"'
        }
    
    def _process_attachments(self, ticket_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process ticket attachments."""
        # Check if attachments were pre-downloaded
        attachment_dir = self.options.get('attachment_dir')
        
        if attachment_dir:
            return self._process_local_attachments(attachment_dir)
        
        attachments = ticket_data.get('attachments', [])
        
        if not attachments:
            console.print("[yellow]⚠ No attachments found in ticket data[/yellow]")
            console.print("[dim]Tip: Ask Copilot CLI to download attachments first,[/dim]")
            console.print("[dim]     then use --attachment-dir flag[/dim]")
            return []
        
        console.print("[yellow]⚠ Cannot download attachments directly (requires Copilot CLI with MCP)[/yellow]")
        console.print(f"[dim]Ask Copilot: 'Download attachments from {ticket_data['key']} to /tmp/jira_attachments_{ticket_data['key']}'[/dim]")
        return []
    
    def _process_local_attachments(self, attachment_dir: str) -> List[Dict[str, Any]]:
        """Process pre-downloaded attachments from a directory."""
        from pathlib import Path
        
        attachment_path = Path(attachment_dir)
        if not attachment_path.exists():
            console.print(f"[red]✗ Attachment directory not found: {attachment_dir}[/red]")
            return []
        
        console.print(f"[cyan]Processing attachments from: {attachment_dir}[/cyan]")
        
        all_logs = []
        log_files = list(attachment_path.glob('**/*'))
        
        for file_path in log_files:
            if file_path.is_file():
                result = self.log_processor.process_attachment(str(file_path))
                all_logs.extend(result)
        
        if all_logs:
            console.print(f"[green]✓ Processed {len(all_logs)} log file(s)[/green]")
        else:
            console.print("[yellow]⚠ No processable log files found[/yellow]")
        
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
    console.print("[bold yellow]📋 Next Steps:[/bold yellow]")
    console.print("")
    console.print("1️⃣  [bold]Option 1: Use GitHub Copilot CLI interactively[/bold]")
    console.print("   Run: [cyan]gh copilot[/cyan]")
    console.print("   Then ask: [cyan]\"Analyze this Jira ticket and provide root cause analysis\"[/cyan]")
    console.print(f"   Then paste the content from: [cyan]{temp_file}[/cyan]")
    console.print("")
    console.print("2️⃣  [bold]Option 2: Use as a prompt (recommended)[/bold]")
    console.print(f"   [cyan]cat {temp_file} | gh copilot[/cyan]")
    console.print("")
    console.print("3️⃣  [bold]Option 3: Copy the analysis input[/bold]")
    console.print(f"   [cyan]cat {temp_file}[/cyan]")
    console.print("   Then paste into any AI assistant with the skill instructions")
    console.print("")
    console.print(f"[dim]Skill instructions: {result['skill_file']}[/dim]")
    
    return result['analysis_input']
