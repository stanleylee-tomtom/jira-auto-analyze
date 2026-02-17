"""Filtering and optimization for log content to reduce token usage."""

import re
from typing import List, Dict, Any, Set
from rich.console import Console

console = Console()


class LogFilter:
    """Filter and optimize log content based on keywords and patterns."""
    
    # Common error/exception patterns to prioritize
    DEFAULT_PATTERNS = [
        r'(?i)error',
        r'(?i)exception',
        r'(?i)fail(ed|ure)?',
        r'(?i)timeout',
        r'(?i)null\s*pointer',
        r'(?i)stack\s*trace',
        r'(?i)fatal',
        r'(?i)critical',
    ]
    
    def __init__(
        self, 
        keywords: List[str] = None,
        patterns: List[str] = None,
        context_lines_before: int = 5,
        context_lines_after: int = 5,
        case_sensitive: bool = False
    ):
        """
        Initialize log filter.
        
        Args:
            keywords: List of keywords to search for
            patterns: List of regex patterns
            context_lines_before: Lines of context before match
            context_lines_after: Lines of context after match
            case_sensitive: Whether to use case-sensitive matching
        """
        self.keywords = keywords or []
        self.patterns = patterns or []
        self.context_before = context_lines_before
        self.context_after = context_lines_after
        self.case_sensitive = case_sensitive
        
        # Compile regex patterns
        flags = 0 if case_sensitive else re.IGNORECASE
        self.compiled_patterns = [
            re.compile(pattern, flags) for pattern in self.patterns
        ]
        
        # Add keyword patterns
        for keyword in self.keywords:
            pattern = re.escape(keyword)
            self.compiled_patterns.append(re.compile(pattern, flags))
    
    def filter_log(self, content: str, max_lines: int = None) -> Dict[str, Any]:
        """
        Filter log content based on keywords and patterns.
        
        Args:
            content: Full log content
            max_lines: Maximum lines to return
            
        Returns:
            Filtered result with metadata
        """
        lines = content.split('\n')
        total_lines = len(lines)
        
        if not self.compiled_patterns:
            # No filtering - return with optional truncation
            if max_lines and total_lines > max_lines:
                filtered_lines = lines[:max_lines]
                return {
                    'content': '\n'.join(filtered_lines),
                    'matched_lines': 0,
                    'total_lines': total_lines,
                    'filtered_lines': len(filtered_lines),
                    'truncated': True,
                    'matches': []
                }
            return {
                'content': content,
                'matched_lines': 0,
                'total_lines': total_lines,
                'filtered_lines': total_lines,
                'truncated': False,
                'matches': []
            }
        
        # Find matching lines with context
        matched_indices = set()
        matches = []
        
        for idx, line in enumerate(lines):
            for pattern in self.compiled_patterns:
                if pattern.search(line):
                    # Add this line and context
                    start = max(0, idx - self.context_before)
                    end = min(len(lines), idx + self.context_after + 1)
                    matched_indices.update(range(start, end))
                    
                    matches.append({
                        'line_number': idx + 1,
                        'line': line,
                        'pattern': pattern.pattern
                    })
                    break
        
        if not matched_indices:
            # No matches found
            console.print("[yellow]⚠ No matches found for specified keywords/patterns[/yellow]")
            # Return a small sample anyway
            sample_size = min(100, total_lines)
            return {
                'content': '\n'.join(lines[:sample_size]),
                'matched_lines': 0,
                'total_lines': total_lines,
                'filtered_lines': sample_size,
                'truncated': sample_size < total_lines,
                'matches': []
            }
        
        # Extract matched lines maintaining order
        filtered_lines = [lines[i] for i in sorted(matched_indices)]
        
        # Apply max_lines limit if specified
        if max_lines and len(filtered_lines) > max_lines:
            filtered_lines = filtered_lines[:max_lines]
            truncated = True
        else:
            truncated = len(matched_indices) < total_lines
        
        return {
            'content': '\n'.join(filtered_lines),
            'matched_lines': len(matches),
            'total_lines': total_lines,
            'filtered_lines': len(filtered_lines),
            'truncated': truncated,
            'matches': matches[:20]  # Limit match details to first 20
        }
    
    def extract_error_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract error/exception sections with stack traces.
        
        Args:
            content: Log content
            
        Returns:
            List of error sections with metadata
        """
        lines = content.split('\n')
        error_sections = []
        current_section = None
        
        # Patterns for error markers
        error_start = re.compile(r'(?i)(error|exception|fatal|critical)', re.IGNORECASE)
        stack_trace = re.compile(r'^\s+at\s+|^\s+File\s+"|^\s+\d+\s+')
        
        for idx, line in enumerate(lines):
            if error_start.search(line):
                # Start new error section
                if current_section:
                    error_sections.append(current_section)
                
                current_section = {
                    'start_line': idx + 1,
                    'lines': [line],
                    'type': 'error'
                }
            elif current_section and stack_trace.search(line):
                # Continue stack trace
                current_section['lines'].append(line)
            elif current_section and line.strip():
                # Continue with non-empty lines
                current_section['lines'].append(line)
            elif current_section and not line.strip():
                # Empty line might end the section
                current_section['end_line'] = idx
                error_sections.append(current_section)
                current_section = None
        
        # Add last section if exists
        if current_section:
            current_section['end_line'] = len(lines)
            error_sections.append(current_section)
        
        # Format sections
        formatted_sections = []
        for section in error_sections:
            formatted_sections.append({
                'start_line': section['start_line'],
                'end_line': section.get('end_line', section['start_line']),
                'content': '\n'.join(section['lines']),
                'line_count': len(section['lines'])
            })
        
        return formatted_sections
    
    def estimate_tokens(self, content: str) -> int:
        """
        Estimate token count for content.
        
        Uses rough approximation: ~4 characters per token.
        
        Args:
            content: Text content
            
        Returns:
            Estimated token count
        """
        return len(content) // 4
    
    def optimize_for_token_limit(
        self, 
        content: str, 
        max_tokens: int = 4000,
        strategy: str = 'smart'
    ) -> Dict[str, Any]:
        """
        Optimize content to fit within token limit.
        
        Args:
            content: Full content
            max_tokens: Maximum tokens allowed
            strategy: 'smart' (extract errors), 'head_tail', or 'head'
            
        Returns:
            Optimized content with metadata
        """
        current_tokens = self.estimate_tokens(content)
        
        if current_tokens <= max_tokens:
            return {
                'content': content,
                'original_tokens': current_tokens,
                'final_tokens': current_tokens,
                'optimized': False,
                'strategy': None
            }
        
        if strategy == 'smart':
            # Try to extract error sections first
            error_sections = self.extract_error_sections(content)
            if error_sections:
                error_content = '\n\n--- Error Section ---\n\n'.join(
                    section['content'] for section in error_sections
                )
                error_tokens = self.estimate_tokens(error_content)
                
                if error_tokens <= max_tokens:
                    return {
                        'content': error_content,
                        'original_tokens': current_tokens,
                        'final_tokens': error_tokens,
                        'optimized': True,
                        'strategy': 'error_extraction',
                        'sections_extracted': len(error_sections)
                    }
        
        # Fall back to head/tail strategy
        lines = content.split('\n')
        chars_per_line = len(content) / len(lines) if lines else 0
        target_chars = max_tokens * 4
        target_lines = int(target_chars / chars_per_line) if chars_per_line > 0 else 100
        
        head_lines = target_lines // 2
        tail_lines = target_lines // 2
        
        if len(lines) > (head_lines + tail_lines):
            head = lines[:head_lines]
            tail = lines[-tail_lines:]
            truncated_content = '\n'.join(head) + \
                f"\n\n... [TRUNCATED: {len(lines) - head_lines - tail_lines} lines] ...\n\n" + \
                '\n'.join(tail)
            
            return {
                'content': truncated_content,
                'original_tokens': current_tokens,
                'final_tokens': self.estimate_tokens(truncated_content),
                'optimized': True,
                'strategy': 'head_tail',
                'lines_kept': head_lines + tail_lines,
                'lines_removed': len(lines) - head_lines - tail_lines
            }
        
        # Just take head
        truncated_content = '\n'.join(lines[:target_lines])
        return {
            'content': truncated_content,
            'original_tokens': current_tokens,
            'final_tokens': self.estimate_tokens(truncated_content),
            'optimized': True,
            'strategy': 'head_only',
            'lines_kept': min(target_lines, len(lines))
        }
    
    def highlight_matches(self, content: str, format: str = 'terminal') -> str:
        """
        Highlight matched keywords in content.
        
        Args:
            content: Text content
            format: 'terminal' (ANSI colors) or 'markdown' (bold)
            
        Returns:
            Content with highlighted matches
        """
        highlighted = content
        
        for pattern in self.compiled_patterns:
            if format == 'terminal':
                highlighted = pattern.sub(
                    lambda m: f'\033[1;31m{m.group(0)}\033[0m',
                    highlighted
                )
            elif format == 'markdown':
                highlighted = pattern.sub(
                    lambda m: f'**{m.group(0)}**',
                    highlighted
                )
        
        return highlighted
