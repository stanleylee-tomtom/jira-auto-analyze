"""Log file processor for extracting and handling log attachments."""

import zipfile
import io
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, BinaryIO
from rich.console import Console

console = Console()


class LogProcessor:
    """Process log files from Jira attachments."""
    
    SUPPORTED_TEXT_EXTENSIONS = {'.txt', '.log', '.out', '.err', '.trace'}
    SUPPORTED_ZIP_EXTENSIONS = {'.zip', '.gz', '.tar', '.tgz'}
    
    def __init__(self, max_size_mb: int = 50):
        """
        Initialize log processor.
        
        Args:
            max_size_mb: Maximum file size to process in MB
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def process_attachment(self, file_path: str, filename: str = None) -> List[Dict[str, Any]]:
        """
        Process a single attachment file.
        
        Args:
            file_path: Path to the file
            filename: Original filename (if different from path)
            
        Returns:
            List of extracted log entries with metadata
        """
        if filename is None:
            filename = Path(file_path).name
        
        file_ext = Path(filename).suffix.lower()
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.max_size_bytes:
            console.print(f"[yellow]⚠ Skipping {filename}: too large ({file_size / 1024 / 1024:.1f} MB)[/yellow]")
            return []
        
        try:
            if file_ext in self.SUPPORTED_TEXT_EXTENSIONS:
                return self._process_text_file(file_path, filename)
            elif file_ext in self.SUPPORTED_ZIP_EXTENSIONS:
                return self._process_zip_file(file_path, filename)
            else:
                console.print(f"[dim]Skipping unsupported file type: {filename}[/dim]")
                return []
        except Exception as e:
            console.print(f"[red]✗ Error processing {filename}: {str(e)}[/red]")
            return []
    
    def _process_text_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Process a text log file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return [{
                'filename': filename,
                'type': 'text',
                'content': content,
                'lines': content.count('\n') + 1,
                'size': len(content)
            }]
        except Exception as e:
            console.print(f"[red]Error reading {filename}: {str(e)}[/red]")
            return []
    
    def _process_zip_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Process a zip archive and extract text files."""
        extracted_logs = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for zip_info in zip_ref.filelist:
                    # Skip directories
                    if zip_info.is_dir():
                        continue
                    
                    # Check if it's a text file
                    file_ext = Path(zip_info.filename).suffix.lower()
                    if file_ext not in self.SUPPORTED_TEXT_EXTENSIONS:
                        continue
                    
                    # Check size
                    if zip_info.file_size > self.max_size_bytes:
                        console.print(f"[yellow]⚠ Skipping {zip_info.filename} in {filename}: too large[/yellow]")
                        continue
                    
                    # Extract and read
                    try:
                        with zip_ref.open(zip_info.filename) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                        
                        extracted_logs.append({
                            'filename': f"{filename}/{zip_info.filename}",
                            'type': 'text',
                            'source_archive': filename,
                            'content': content,
                            'lines': content.count('\n') + 1,
                            'size': len(content)
                        })
                    except Exception as e:
                        console.print(f"[red]Error extracting {zip_info.filename}: {str(e)}[/red]")
                        continue
            
            return extracted_logs
        except Exception as e:
            console.print(f"[red]Error processing zip {filename}: {str(e)}[/red]")
            return []
    
    def extract_log_section(
        self, 
        content: str, 
        start_pattern: str = None, 
        end_pattern: str = None,
        max_lines: int = None
    ) -> str:
        """
        Extract a section of log based on patterns.
        
        Args:
            content: Full log content
            start_pattern: Regex pattern for start of section
            end_pattern: Regex pattern for end of section
            max_lines: Maximum lines to return
            
        Returns:
            Extracted section
        """
        import re
        
        lines = content.split('\n')
        
        if start_pattern or end_pattern:
            start_idx = 0
            end_idx = len(lines)
            
            if start_pattern:
                for i, line in enumerate(lines):
                    if re.search(start_pattern, line):
                        start_idx = i
                        break
            
            if end_pattern:
                for i in range(start_idx, len(lines)):
                    if re.search(end_pattern, lines[i]):
                        end_idx = i + 1
                        break
            
            lines = lines[start_idx:end_idx]
        
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
        
        return '\n'.join(lines)
    
    def sample_large_log(
        self, 
        content: str, 
        head_lines: int = 200, 
        tail_lines: int = 200
    ) -> Tuple[str, bool]:
        """
        Sample a large log file by taking head and tail.
        
        Args:
            content: Full log content
            head_lines: Number of lines from the start
            tail_lines: Number of lines from the end
            
        Returns:
            Tuple of (sampled content, was_truncated)
        """
        lines = content.split('\n')
        total_lines = len(lines)
        
        if total_lines <= (head_lines + tail_lines):
            return content, False
        
        head = lines[:head_lines]
        tail = lines[-tail_lines:]
        
        truncated_marker = [
            f"\n... [TRUNCATED: {total_lines - head_lines - tail_lines} lines omitted] ...\n"
        ]
        
        sampled = '\n'.join(head + truncated_marker + tail)
        return sampled, True
    
    def detect_log_format(self, content: str) -> str:
        """
        Detect log format (plain text, JSON logs, structured logs, etc.).
        
        Args:
            content: Log content
            
        Returns:
            Detected format name
        """
        import json
        
        lines = content.strip().split('\n')[:10]  # Check first 10 lines
        
        # Check for JSON logs
        json_count = 0
        for line in lines:
            try:
                json.loads(line)
                json_count += 1
            except:
                pass
        
        if json_count >= len(lines) * 0.8:
            return 'json'
        
        # Check for common log patterns
        if any('ERROR' in line or 'Exception' in line for line in lines):
            return 'error_log'
        
        if any('INFO' in line or 'DEBUG' in line or 'WARN' in line for line in lines):
            return 'structured'
        
        return 'plain_text'
    
    def get_summary_stats(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for processed logs.
        
        Args:
            logs: List of log entries
            
        Returns:
            Summary statistics
        """
        if not logs:
            return {'count': 0, 'total_lines': 0, 'total_size': 0}
        
        return {
            'count': len(logs),
            'total_lines': sum(log.get('lines', 0) for log in logs),
            'total_size': sum(log.get('size', 0) for log in logs),
            'files': [log['filename'] for log in logs]
        }
