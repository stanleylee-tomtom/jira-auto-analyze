"""Output formatting for analysis results."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


class OutputFormatter:
    """Format and output analysis results."""
    
    @staticmethod
    def format_terminal(result: Dict[str, Any]) -> str:
        """
        Format result for terminal display with rich formatting.
        
        Args:
            result: Analysis result
            
        Returns:
            Formatted string
        """
        # If result contains markdown, render it
        if isinstance(result, str):
            md = Markdown(result)
            console.print(Panel(md, title="Analysis Result", border_style="blue"))
            return result
        
        # Otherwise format structured data
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"Analysis for {result.get('ticket_id', 'Unknown')}")
        output.append(f"{'='*60}\n")
        
        if 'summary' in result:
            output.append(f"Summary: {result['summary']}\n")
        
        if 'root_cause' in result:
            output.append(f"Root Cause:\n{result['root_cause']}\n")
        
        if 'recommendations' in result:
            output.append("Recommendations:")
            for rec in result['recommendations']:
                output.append(f"  - {rec}")
            output.append("")
        
        return '\n'.join(output)
    
    @staticmethod
    def format_markdown(result: Dict[str, Any], ticket_id: str = None) -> str:
        """
        Format result as markdown.
        
        Args:
            result: Analysis result
            ticket_id: Optional ticket ID
            
        Returns:
            Markdown formatted string
        """
        if isinstance(result, str):
            # Already markdown
            return result
        
        lines = []
        
        # Header
        tid = ticket_id or result.get('ticket_id', 'Unknown')
        lines.append(f"# Analysis for {tid}")
        lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # Summary
        if 'summary' in result:
            lines.append("## 📋 Summary\n")
            lines.append(result['summary'])
            lines.append("")
        
        # Root Cause
        if 'root_cause' in result:
            lines.append("## 🔍 Root Cause\n")
            lines.append(result['root_cause'])
            lines.append("")
        
        # Patterns
        if 'patterns' in result:
            lines.append("## 📊 Patterns & Observations\n")
            for pattern in result['patterns']:
                lines.append(f"- {pattern}")
            lines.append("")
        
        # Technical Details
        if 'technical_details' in result:
            lines.append("## 🔧 Technical Details\n")
            lines.append(result['technical_details'])
            lines.append("")
        
        # Recommendations
        if 'recommendations' in result:
            lines.append("## 💡 Recommendations\n")
            
            if isinstance(result['recommendations'], dict):
                if 'immediate' in result['recommendations']:
                    lines.append("### Immediate Actions\n")
                    for action in result['recommendations']['immediate']:
                        lines.append(f"1. {action}")
                    lines.append("")
                
                if 'investigation' in result['recommendations']:
                    lines.append("### Further Investigation\n")
                    for step in result['recommendations']['investigation']:
                        lines.append(f"1. {step}")
                    lines.append("")
                
                if 'long_term' in result['recommendations']:
                    lines.append("### Long-term Solutions\n")
                    for solution in result['recommendations']['long_term']:
                        lines.append(f"1. {solution}")
                    lines.append("")
            else:
                for rec in result['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
        
        # Risk Assessment
        if 'risk_assessment' in result:
            lines.append("## ⚠️ Risk Assessment\n")
            lines.append(result['risk_assessment'])
            lines.append("")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_json(result: Dict[str, Any]) -> str:
        """
        Format result as JSON.
        
        Args:
            result: Analysis result
            
        Returns:
            JSON formatted string
        """
        return json.dumps(result, indent=2, default=str)
    
    @staticmethod
    def save_to_file(content: str, output_path: str) -> None:
        """
        Save content to file.
        
        Args:
            content: Content to save
            output_path: Path to output file
        """
        path = Path(output_path)
        
        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        console.print(f"[green]✓ Analysis saved to: {output_path}[/green]")
    
    @staticmethod
    def output(
        result: Any,
        format: str = 'terminal',
        output_path: str = None,
        ticket_id: str = None
    ) -> str:
        """
        Output analysis result in specified format.
        
        Args:
            result: Analysis result
            format: Output format ('terminal', 'markdown', 'json')
            output_path: Optional path to save output
            ticket_id: Optional ticket ID for context
            
        Returns:
            Formatted content
        """
        # Format based on type
        if format == 'json':
            content = OutputFormatter.format_json(result)
        elif format == 'markdown':
            content = OutputFormatter.format_markdown(result, ticket_id)
        else:  # terminal
            content = OutputFormatter.format_terminal(result)
        
        # Save to file if path provided
        if output_path:
            # Determine format from extension if not specified
            ext = Path(output_path).suffix.lower()
            if ext == '.json' and format == 'terminal':
                content = OutputFormatter.format_json(result)
            elif ext == '.md' and format == 'terminal':
                content = OutputFormatter.format_markdown(result, ticket_id)
            
            OutputFormatter.save_to_file(content, output_path)
        
        return content


def create_analysis_report(
    ticket_data: Dict[str, Any],
    analysis: str,
    logs_summary: Dict[str, Any],
    output_path: str = None
) -> str:
    """
    Create a comprehensive analysis report.
    
    Args:
        ticket_data: Jira ticket data
        analysis: Analysis text from Copilot
        logs_summary: Summary of processed logs
        output_path: Optional path to save report
        
    Returns:
        Report content
    """
    lines = []
    
    # Title
    lines.append(f"# Bug Analysis Report: {ticket_data['key']}")
    lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Ticket Info
    lines.append("## Ticket Information\n")
    lines.append(f"- **Key:** {ticket_data['key']}")
    lines.append(f"- **Summary:** {ticket_data.get('summary', 'N/A')}")
    lines.append(f"- **Status:** {ticket_data.get('status', 'N/A')}")
    lines.append(f"- **Priority:** {ticket_data.get('priority', 'N/A')}")
    lines.append("")
    
    # Logs Summary
    if logs_summary:
        lines.append("## Logs Analyzed\n")
        lines.append(f"- **Files Processed:** {logs_summary.get('count', 0)}")
        lines.append(f"- **Total Lines:** {logs_summary.get('total_lines', 0)}")
        if 'files' in logs_summary:
            lines.append("\n**Files:**")
            for filename in logs_summary['files']:
                lines.append(f"  - {filename}")
        lines.append("")
    
    # Analysis
    lines.append("## Analysis\n")
    lines.append(analysis)
    
    report = '\n'.join(lines)
    
    if output_path:
        OutputFormatter.save_to_file(report, output_path)
    
    return report
