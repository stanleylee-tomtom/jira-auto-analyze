"""Analysis orchestrator using REST API to fetch and process Jira tickets."""
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
        if comments:
            lines.append(f"## Comments ({len(comments)})")
            for i, c in enumerate(comments[:10], 1):
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

def analyze_ticket(options: Dict[str, Any]) -> str:
    analyzer = TicketAnalyzer(options)
    result = analyzer.analyze(options['ticket_id'])
    return result['analysis_path']
