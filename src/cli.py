"""CLI entry point for jira-auto-analyze."""

import click
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

console = Console()

# Load environment variables
load_dotenv()


def load_config(config_path):
    """Load configuration from YAML file."""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Jira Auto Analyze - Analyze Jira bug tickets using GitHub Copilot.
    
    This tool fetches Jira tickets, processes log files, and uses GitHub Copilot
    to generate comprehensive analysis including summaries, patterns, and root causes.
    """
    pass


@cli.command()
@click.argument('ticket_id')
@click.option(
    '--keywords', '-k',
    help='Comma-separated keywords to filter logs (e.g., "error,timeout,failed")'
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to configuration YAML file'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Save analysis to file (supports .md, .json)'
)
@click.option(
    '--max-lines',
    type=int,
    default=500,
    help='Maximum log lines to process (default: 500)'
)
@click.option(
    '--context-lines',
    type=int,
    default=5,
    help='Context lines around keywords (default: 5)'
)
@click.option(
    '--depth',
    type=click.Choice(['quick', 'normal', 'deep']),
    default='normal',
    help='Analysis depth (default: normal)'
)
@click.option(
    '--no-attachments',
    is_flag=True,
    help='Skip processing attachments'
)
@click.option(
    '--attachment-dir',
    type=click.Path(exists=True),
    help='Directory containing pre-downloaded attachments (use when Copilot CLI downloaded them)'
)
@click.option(
    '--auto-analyze',
    is_flag=True,
    help='Automatically invoke GitHub Copilot CLI to analyze the results'
)
def analyze(ticket_id, keywords, config, output, max_lines, context_lines, depth, no_attachments, attachment_dir, auto_analyze):
    """Analyze a Jira ticket by ID.
    
    Example:
        jira-analyze analyze PROJ-123
        jira-analyze analyze PROJ-123 --keywords "error,timeout" --output report.md
    """
    from .analyzer import analyze_ticket
    
    # Load config file if provided
    config_data = load_config(config)
    
    # Override config with CLI options
    options = {
        'ticket_id': ticket_id,
        'keywords': keywords.split(',') if keywords else config_data.get('keywords', []),
        'max_lines': max_lines,
        'context_lines': context_lines,
        'depth': depth,
        'no_attachments': no_attachments,
        'attachment_dir': attachment_dir,
        'output_path': output,
        'auto_analyze': auto_analyze,
    }
    
    # Merge with config data
    options.update({k: v for k, v in config_data.items() if k not in options})
    
    console.print(f"\n[bold blue]🔍 Analyzing ticket: {ticket_id}[/bold blue]\n")
    
    try:
        result = analyze_ticket(options)
        
        if output:
            console.print(f"[green]✓ Analysis saved to: {output}[/green]")
        else:
            console.print(result)
            
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise click.Abort()


@cli.command()
@click.option(
    '--query', '-q',
    help='JQL query to filter tickets'
)
@click.option(
    '--project', '-p',
    help='Project key to list tickets from'
)
@click.option(
    '--status',
    help='Filter by status (e.g., "Open", "In Progress")'
)
@click.option(
    '--limit',
    type=int,
    default=10,
    help='Maximum tickets to list (default: 10)'
)
def list(query, project, status, limit):
    """List Jira tickets.
    
    Example:
        jira-analyze list --project PROJ --status "Open"
        jira-analyze list --query "project = PROJ AND status = Open"
    """
    from .jira_client import JiraClient
    
    console.print("\n[bold blue]📋 Fetching tickets...[/bold blue]\n")
    
    try:
        client = JiraClient()
        
        # Build JQL query
        if query:
            jql = query
        else:
            filters = []
            if project:
                filters.append(f'project = {project}')
            if status:
                filters.append(f'status = "{status}"')
            jql = ' AND '.join(filters) if filters else 'order by created DESC'
        
        tickets = client.search_tickets(jql, limit=limit)
        
        # Display results in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Summary", style="white")
        table.add_column("Status", style="yellow")
        table.add_column("Priority", style="red")
        
        for ticket in tickets:
            table.add_row(
                ticket.get('key', 'N/A'),
                ticket.get('summary', 'N/A')[:50],
                ticket.get('status', 'N/A'),
                ticket.get('priority', 'N/A')
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing {len(tickets)} ticket(s)[/dim]\n")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise click.Abort()


@cli.command()
def config():
    """Show current configuration and validate setup.
    
    Checks environment variables and displays configuration status.
    """
    console.print("\n[bold blue]⚙️  Configuration Status[/bold blue]\n")
    
    # Check required environment variables
    required_vars = {
        'ATLASSIAN_CLOUD_ID': os.getenv('ATLASSIAN_CLOUD_ID'),
        'ATLASSIAN_API_TOKEN': os.getenv('ATLASSIAN_API_TOKEN'),
        'ATLASSIAN_EMAIL': os.getenv('ATLASSIAN_EMAIL'),
    }
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Variable", style="cyan")
    table.add_column("Status", style="white")
    
    all_set = True
    for var, value in required_vars.items():
        if value:
            table.add_row(var, "[green]✓ Set[/green]")
        else:
            table.add_row(var, "[red]✗ Not set[/red]")
            all_set = False
    
    console.print(table)
    
    if all_set:
        console.print("\n[green]✓ All required variables are set[/green]\n")
    else:
        console.print("\n[yellow]⚠ Please set missing variables in .env file[/yellow]")
        console.print("[dim]Copy .env.example to .env and fill in your credentials[/dim]\n")


if __name__ == '__main__':
    cli()
