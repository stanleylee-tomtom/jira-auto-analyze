"""Analysis orchestrator using REST API to fetch and process Jira tickets."""
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from .jira_api import JiraRestAPI
from .downloader import AttachmentDownloader
from .log_processor import LogProcessor
from .filter import LogFilter

console = Console()

class TicketAnalyzer:
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.jira_api = JiraRestAPI()
        self.downloader = AttachmentDownloader(options.get('output_dir', './analysis_results'))
        self.log_processor = LogProcessor()
        keywords = options.get('keywords', [])
        context_lines = options.get('context_lines', 5)
        self.log_filter = LogFilter(keywords=keywords, context_lines_before=context_lines, context_lines_after=context_lines)
        
        # Get bot users to ignore from config, with defaults
        # These are typically service accounts for auto-triage/automation
        self.ignore_bot_users = options.get('ignore_bot_users', [
            'svc_kaizen_atlassian',
            'svc_jiradel_svc',
            'svc_navsdk_jira',
            'automation', 
            'bot',
            'svc_'  # Catch any service account starting with svc_
        ])
    
    def analyze(self, ticket_id: str) -> Dict[str, Any]:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task1 = progress.add_task("Fetching ticket...", total=None)
            ticket_data = self.jira_api.get_issue_formatted(ticket_id)
            comments = self.jira_api.get_comments(ticket_id)
            progress.update(task1, completed=True)
            console.print(f"[green]✓ Fetched: {ticket_data['summary'][:60]}...[/green]")
            
            if not self.options.get('no_attachments'):
                task2 = progress.add_task("Downloading attachments...", total=None)
                attachments = self.downloader.get_downloadable_attachments(ticket_data['attachments'])
                download_result = self.downloader.download_all(ticket_id, attachments)
                progress.update(task2, completed=True)
            else:
                download_result = {'downloaded': 0, 'files': []}
            
            task3 = progress.add_task("Saving ticket data...", total=None)
            self.downloader.save_ticket_data(ticket_id, ticket_data, comments)
            progress.update(task3, completed=True)
            
            task4 = progress.add_task("Processing logs...", total=None)
            logs = [self.log_processor.process_attachment(f) for f in download_result.get('files', [])]
            logs = [item for sublist in logs for item in sublist]
            progress.update(task4, completed=True)
            
            if logs:
                task5 = progress.add_task("Filtering logs...", total=None)
                filtered_logs = self._filter_logs(logs)
                progress.update(task5, completed=True)
            else:
                filtered_logs = []
            
            task6 = progress.add_task("Generating analysis...", total=None)
            analysis_path = self._generate_analysis_file(ticket_id, ticket_data, comments, filtered_logs)
            progress.update(task6, completed=True)
        
        self._display_summary(ticket_id, ticket_data, download_result, filtered_logs, analysis_path)
        
        # Auto-analyze with gh copilot if requested
        if self.options.get('auto_analyze'):
            self._invoke_copilot(analysis_path)
        
        return {'ticket_id': ticket_id, 'analysis_path': analysis_path}
    
    def _filter_logs(self, logs):
        filtered = []
        for log in logs:
            result = self.log_filter.filter_log(log['content'], max_lines=self.options.get('max_lines', 500))
            optimized = self.log_filter.optimize_for_token_limit(result['content'], max_tokens=4000, strategy='smart')
            filtered.append({
                'filename': log['filename'],
                'original_lines': log.get('lines', 0),
                'filtered_lines': result['filtered_lines'],
                'matched_lines': result['matched_lines'],
                'content': optimized['content'],
                'estimated_tokens': optimized['final_tokens'],
                'matches': result.get('matches', [])
            })
        return filtered
    
    def _filter_bot_comments(self, comments):
        """Filter out bot comments (e.g., svc_kaizen_atlassian for auto-triage)."""
        filtered = []
        for comment in comments:
            author_name = comment.get('author', {}).get('displayName', '').lower()
            account_id = comment.get('author', {}).get('accountId', '').lower()
            
            # Check if author name or account ID contains bot identifiers
            is_bot = any(bot.lower() in author_name or bot.lower() in account_id 
                        for bot in self.ignore_bot_users)
            
            if not is_bot:
                filtered.append(comment)
        
        return filtered
    
    def _generate_analysis_file(self, ticket_id, ticket_data, comments, filtered_logs):
        output_dir = Path(self.options.get('output_dir', './analysis_results')) / ticket_id
        output_dir.mkdir(parents=True, exist_ok=True)
        analysis_file = output_dir / 'analysis.md'
        lines = [f"# Jira Ticket Analysis: {ticket_id}", "", "## Ticket Information"]
        lines.append(f"- **Key:** {ticket_data['key']}")
        lines.append(f"- **Summary:** {ticket_data['summary']}")
        lines.append(f"- **Status:** {ticket_data['status']}")
        lines.append(f"- **Priority:** {ticket_data['priority']}")
        lines.append("")
        lines.append("## Description")
        lines.append(ticket_data.get('description', 'No description'))
        lines.append("")
        
        # Filter out bot comments
        human_comments = self._filter_bot_comments(comments)
        
        if human_comments:
            lines.append(f"## Comments ({len(human_comments)})")
            for i, c in enumerate(human_comments[:10], 1):
                author = c.get('author', {}).get('displayName', 'Unknown')
                body = c.get('body', '')
                if isinstance(body, dict):
                    body = self.downloader._extract_adf_text(body)
                lines.extend([f"### Comment {i} - {author}", body[:500], ""])
        if filtered_logs:
            lines.append(f"## Log Analysis ({len(filtered_logs)} files)")
            for log in filtered_logs:
                lines.extend([f"\n### {log['filename']}", f"*(Showing {log['filtered_lines']} of {log['original_lines']} lines)*", "", "```", log['content'], "```", ""])
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return str(analysis_file)
    
    def _display_summary(self, ticket_id, ticket_data, download_result, filtered_logs, analysis_path):
        console.print(f"\n{'='*70}\n")
        console.print(f"[bold green]✓ Analysis Ready: {ticket_id}[/bold green]")
        console.print(f"[dim]{ticket_data['summary']}[/dim]\n")
        console.print(f"  • Attachments: [cyan]{download_result.get('downloaded', 0)}[/cyan]")
        console.print(f"  • Log files: [cyan]{len(filtered_logs)}[/cyan]")
        if filtered_logs:
            total_matches = sum(log.get('matched_lines', 0) for log in filtered_logs)
            console.print(f"  • Keyword matches: [cyan]{total_matches}[/cyan]")
        console.print(f"\n[bold]📁 Saved to:[/bold] [cyan]{Path(analysis_path).parent}[/cyan]\n")
        next_steps = f"""Ask GitHub Copilot to analyze:
{analysis_path}

Example: "Analyze {analysis_path} using jira_analyzer framework"
"""
        console.print(Panel(next_steps, title="[yellow]Ready for Analysis[/yellow]", border_style="yellow"))
    
    def _invoke_copilot(self, analysis_path: str):
        """Invoke GitHub Copilot CLI to analyze the generated file."""
        console.print("\n[bold blue]🤖 Preparing Copilot Analysis...[/bold blue]\n")
        
        # Check if we're already inside a Copilot CLI session
        if os.environ.get('GITHUB_COPILOT_CLI_SESSION') or os.environ.get('COPILOT_SESSION_ID'):
            console.print("[yellow]⚠ Already inside a GitHub Copilot CLI session[/yellow]")
            console.print("[dim]Cannot invoke gh copilot recursively.[/dim]\n")
            console.print(f"[bold cyan]📋 Please ask Copilot:[/bold cyan]")
            console.print(f"[green]Analyze {analysis_path} using jira_analyzer framework[/green]\n")
            return
        
        # Construct the prompt
        prompt = f"Analyze {analysis_path} using jira_analyzer framework"
        
        try:
            console.print(f"[dim]Running: gh copilot...[/dim]\n")
            
            # Use subprocess to invoke gh copilot with the prompt via stdin
            process = subprocess.Popen(
                ['gh', 'copilot'],
                stdin=subprocess.PIPE,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            
            # Send the prompt to gh copilot
            process.communicate(input=prompt)
            
            if process.returncode != 0:
                console.print(f"\n[yellow]⚠ GitHub Copilot exited with code {process.returncode}[/yellow]")
                console.print(f"[dim]You can manually ask: Analyze {analysis_path} using jira_analyzer framework[/dim]")
        except FileNotFoundError:
            console.print("[red]✗ GitHub Copilot CLI (gh copilot) not found. Please install it first.[/red]")
            console.print("[dim]Install with: gh extension install github/gh-copilot[/dim]")
        except Exception as e:
            console.print(f"[red]✗ Error invoking GitHub Copilot: {str(e)}[/red]")
            console.print(f"[dim]You can manually ask: Analyze {analysis_path} using jira_analyzer framework[/dim]")

def analyze_ticket(options: Dict[str, Any]) -> str:
    analyzer = TicketAnalyzer(options)
    result = analyzer.analyze(options['ticket_id'])
    return result['analysis_path']
