# AI Development Guide for Jira Auto Analyze

This guide is specifically for AI tools (like GitHub Copilot CLI, ChatGPT, Claude, etc.) working on this codebase. It provides structured instructions to ensure consistent, high-quality contributions.

## 🎯 Quick Start for AI Tools

When you start working on this project:

1. **Read this file completely first**
2. **Review [CONTRIBUTING.md](CONTRIBUTING.md)** for general guidelines
3. **Read [skills/jira_analyzer.md](skills/jira_analyzer.md)** for analysis framework
4. **Check [PROJECT_STATUS.md](PROJECT_STATUS.md)** for current state

## 📖 Project Context

### What This Tool Does

**Purpose**: Analyze Jira bug tickets using AI assistance

**Workflow**:
```
User runs command → Fetch Jira ticket → Download logs → Filter by keywords 
→ Generate analysis.md → Optionally invoke Copilot CLI
```

**Key Point**: The tool prepares data for analysis; the actual analysis is done by GitHub Copilot CLI using the `jira_analyzer` framework.

### Critical Philosophy: Diagnostic, Not Prescriptive

⚠️ **MOST IMPORTANT CONCEPT**:
- Analysis should identify **possible root causes**, NOT solutions
- Present findings as **hypotheses needing confirmation**
- Use uncertainty language: "likely", "suggests", "indicates"
- Avoid: "The fix is...", "To solve this...", "The solution..."
- Prefer: "This suggests...", "To confirm...", "Investigation should..."

**Why**: Root causes need validation before suggesting fixes. Premature solutions can be misleading.

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────┐
│  CLI (cli.py)                                       │
│  - Click-based command interface                    │
│  - Commands: analyze, list, config                  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Analyzer (analyzer.py)                             │
│  - Main orchestration                               │
│  - Bot comment filtering                            │
│  - Progress tracking                                │
└──┬────────┬────────┬────────┬────────┬─────────────┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌────┐ ┌──────┐ ┌──────┐ ┌────────┐
│ Jira │ │Down│ │ Log  │ │Filter│ │ Output │
│ API  │ │load│ │Proces│ │      │ │        │
└──────┘ └────┘ └──────┘ └──────┘ └────────┘
```

### Data Flow

```
1. JiraRestAPI (jira_api.py)
   └─> Fetches ticket metadata, comments, attachments
   
2. AttachmentDownloader (downloader.py)
   └─> Downloads log files to analysis_results/TICKET-ID/
   
3. LogProcessor (log_processor.py)
   └─> Extracts text from .log, .txt, .zip files
   
4. LogFilter (filter.py)
   └─> Applies keyword filtering + token optimization
   
5. Analyzer (analyzer.py)
   └─> Generates analysis.md with formatted data
   
6. (Optional) Auto-analyze
   └─> Invokes `gh copilot` with the analysis.md path
```

## 🔧 How to Make Changes

### Understanding Existing Code

**Before modifying any file, understand its role:**

```bash
# View file with line numbers
cat -n src/analyzer.py | head -50

# Find where a function is called
grep -r "filter_log" src/

# Check imports
grep "^import\|^from" src/analyzer.py
```

**Key files and their responsibilities:**

| File | Purpose | Don't Change |
|------|---------|--------------|
| `src/jira_api.py` | REST API client | API endpoints, auth logic |
| `src/analyzer.py` | Main orchestration | Bot filtering logic |
| `src/filter.py` | Keyword filtering | Token optimization algorithms |
| `skills/jira_analyzer.md` | Analysis framework | Core philosophy |

### Adding Features

**Step-by-step process:**

1. **Understand the requirement**
   ```
   Example: "Add support for .csv log files"
   ```

2. **Identify affected files**
   ```
   - log_processor.py (needs CSV parsing)
   - requirements.txt (may need pandas)
   - README.md (document new format)
   ```

3. **Check existing patterns**
   ```python
   # How are other formats handled?
   grep -A 10 "def.*process" src/log_processor.py
   ```

4. **Make minimal changes**
   ```python
   # Add CSV support to log_processor.py
   def process_attachment(self, file_path):
       if file_path.endswith('.csv'):
           return self._process_csv(file_path)
       # ... existing code ...
   
   def _process_csv(self, file_path):
       import csv
       lines = []
       with open(file_path, 'r') as f:
           reader = csv.reader(f)
           for row in reader:
               lines.append(','.join(row))
       return [{'filename': Path(file_path).name, 
                'content': '\n'.join(lines),
                'lines': len(lines)}]
   ```

5. **Update documentation**
   ```markdown
   # In README.md
   - 📦 **Zip Support**: Handles compressed log files (.zip, .csv)
   ```

6. **Test thoroughly**
   ```bash
   # Create test CSV
   echo "timestamp,level,message" > test.csv
   echo "2024-01-01,ERROR,Test error" >> test.csv
   
   # Test processing
   python -c "from src.log_processor import LogProcessor; p = LogProcessor(); print(p.process_attachment('test.csv'))"
   ```

### Fixing Bugs

**Debugging approach:**

1. **Reproduce the issue**
   ```bash
   # Get exact error
   python -m src.cli analyze TICKET-ID --keywords "test" 2>&1 | tee error.log
   ```

2. **Add debug output** (temporarily)
   ```python
   # In analyzer.py
   console.print(f"[dim]DEBUG: ticket_data keys: {ticket_data.keys()}[/dim]")
   ```

3. **Identify root cause**
   ```python
   # Add assertions to catch issues early
   assert 'summary' in ticket_data, f"Missing summary in {ticket_data.keys()}"
   ```

4. **Fix with minimal changes**
   ```python
   # Before:
   summary = ticket_data['summary']
   
   # After:
   summary = ticket_data.get('summary', 'No summary available')
   ```

5. **Remove debug code**
   ```bash
   # Clean up
   git diff src/analyzer.py  # Review changes
   # Remove any DEBUG prints
   ```

6. **Test the fix**
   ```bash
   # Verify fix works
   python -m src.cli analyze TICKET-ID --keywords "test"
   
   # Check for regressions
   python -m src.cli analyze DIFFERENT-TICKET --keywords "error"
   ```

### Updating Documentation

**When to update docs:**

- ✅ Added/removed a feature
- ✅ Changed behavior or output
- ✅ Fixed a bug that affects usage
- ✅ Added new dependencies
- ❌ Internal refactoring (no user-visible change)

**Which docs to update:**

```
Feature change:
  → README.md (if major feature)
  → QUICKSTART.md (if affects usage)
  → EXAMPLE_OUTPUT.md (if changes output)

Analysis framework change:
  → skills/jira_analyzer.md (CRITICAL)
  → docs/ANALYSIS_GUIDELINES.md
  → EXAMPLE_OUTPUT.md

Configuration change:
  → examples/sample_config.yaml
  → docs/CREDENTIALS.md (if affects setup)

Bug fix:
  → Usually no doc changes needed
  → Unless behavior changed
```

## 🎨 Code Style Guidelines

### Python Style

**Follow existing patterns:**

```python
# Good: Matches project style
from rich.console import Console
console = Console()

def analyze_ticket(options: Dict[str, Any]) -> str:
    """Analyze a Jira ticket.
    
    Args:
        options: Configuration dictionary with ticket_id, keywords, etc.
        
    Returns:
        Path to generated analysis file
    """
    analyzer = TicketAnalyzer(options)
    return analyzer.analyze(options['ticket_id'])

# Bad: Different style
import rich
def analyze(opts):
    return TicketAnalyzer(opts).analyze(opts['ticket_id'])
```

### Imports

**Order imports consistently:**

```python
# 1. Standard library
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# 2. Third-party
import click
from rich.console import Console
from rich.progress import Progress

# 3. Local
from .jira_api import JiraRestAPI
from .filter import LogFilter
```

### Error Handling

**Always handle errors gracefully:**

```python
# Good: Clear error messages
try:
    ticket_data = self.jira_api.get_issue_formatted(ticket_id)
except requests.HTTPError as e:
    if e.response.status_code == 404:
        console.print(f"[red]✗ Ticket {ticket_id} not found[/red]")
    else:
        console.print(f"[red]✗ API error: {e}[/red]")
    raise

# Bad: Generic error handling
try:
    ticket_data = self.jira_api.get_issue_formatted(ticket_id)
except:
    print("Error")
```

### Console Output

**Use Rich console consistently:**

```python
from rich.console import Console
console = Console()

# Success
console.print("[green]✓ Fetched ticket[/green]")

# Info
console.print("[cyan]📥 Downloading 3 attachments[/cyan]")

# Warning
console.print("[yellow]⚠ No attachments found[/yellow]")

# Error
console.print("[red]✗ Failed to connect[/red]")

# Dim (less important)
console.print("[dim]Saved to: /path/to/file[/dim]")
```

## 🧪 Testing Strategy

### Manual Testing

**Minimum testing for any change:**

```bash
# 1. Help text works
python -m src.cli --help
python -m src.cli analyze --help

# 2. Connection works
python test_connection.py

# 3. Basic analysis works
python -m src.cli analyze GOSDK-196630 --keywords "error" --no-attachments

# 4. List command works
python -m src.cli list --query "project = GOSDK" --limit 3
```

### Testing Bot Filtering

```python
# Test filtering logic
from src.analyzer import TicketAnalyzer

analyzer = TicketAnalyzer({'keywords': []})

# Mock comments
comments = [
    {'author': {'displayName': 'John Doe'}},
    {'author': {'displayName': 'svc_kaizen_atlassian'}},
    {'author': {'displayName': 'Jane Smith'}},
]

filtered = analyzer._filter_bot_comments(comments)
assert len(filtered) == 2, f"Expected 2, got {len(filtered)}"
assert filtered[0]['author']['displayName'] == 'John Doe'
```

### Testing with Real Tickets

```bash
# Test with different ticket types
python -m src.cli analyze GOSDK-196630 --keywords "crash,error"      # With logs
python -m src.cli analyze SOME-TICKET --no-attachments               # No logs
python -m src.cli analyze ANOTHER-TICKET --keywords "timeout" --depth quick
```

## 📋 Common Tasks

### Task 1: Add a New CLI Option

```python
# 1. Add option to CLI (src/cli.py)
@click.option(
    '--new-option',
    type=int,
    default=100,
    help='Description of new option'
)
def analyze(ticket_id, keywords, ..., new_option):
    # Add to options dict
    options = {
        # ... existing options ...
        'new_option': new_option,
    }

# 2. Use in analyzer (src/analyzer.py)
class TicketAnalyzer:
    def __init__(self, options: Dict[str, Any]):
        self.new_option = options.get('new_option', 100)
    
    def analyze(self, ticket_id: str):
        # Use self.new_option ...

# 3. Update sample config (examples/sample_config.yaml)
new_option: 100  # Description

# 4. Document in README.md
--new-option INTEGER    Description (default: 100)
```

### Task 2: Add a New Keyword Filter Strategy

```python
# 1. Add method to LogFilter (src/filter.py)
def filter_by_custom_strategy(self, content: str) -> Dict[str, Any]:
    """New filtering strategy.
    
    Args:
        content: Log content to filter
        
    Returns:
        Dictionary with filtered content and metadata
    """
    # Implementation...
    return {
        'content': filtered_content,
        'filtered_lines': len(filtered_lines),
        'matched_lines': len(matches)
    }

# 2. Add option to select strategy (src/cli.py)
@click.option(
    '--strategy',
    type=click.Choice(['smart', 'simple', 'custom']),
    default='smart'
)

# 3. Use in analyzer (src/analyzer.py)
strategy = self.options.get('strategy', 'smart')
if strategy == 'custom':
    result = self.log_filter.filter_by_custom_strategy(log['content'])
```

### Task 3: Improve Bot Detection

```python
# In analyzer.py _filter_bot_comments()

# Add more sophisticated detection
def _filter_bot_comments(self, comments):
    filtered = []
    for comment in comments:
        author_name = comment.get('author', {}).get('displayName', '').lower()
        account_id = comment.get('author', {}).get('accountId', '').lower()
        email = comment.get('author', {}).get('emailAddress', '').lower()
        
        # Check multiple fields
        is_bot = any(bot.lower() in author_name or 
                     bot.lower() in account_id or
                     bot.lower() in email
                     for bot in self.ignore_bot_users)
        
        # Additional heuristics
        if 'noreply' in email or 'automation' in email:
            is_bot = True
            
        if not is_bot:
            filtered.append(comment)
    
    return filtered
```

## ⚠️ Common Pitfalls

### Pitfall 1: Breaking the Analysis Framework

❌ **Wrong**:
```python
# Don't change the analysis philosophy
lines.append("## Root Cause")
lines.append("The root cause is X")
lines.append("## Solution")
lines.append("Fix by doing Y")
```

✅ **Correct**:
```python
# Keep the diagnostic approach
lines.append("## Possible Root Causes")
lines.append("Evidence suggests X may be caused by Y")
lines.append("## Next Steps for Investigation")
lines.append("To confirm this hypothesis, verify Z")
```

### Pitfall 2: Adding MCP Dependencies

❌ **Wrong**:
```python
# Don't add MCP tools
from atlassian_mcp import AtlassianClient
client = AtlassianClient()
```

✅ **Correct**:
```python
# Use REST API
from .jira_api import JiraRestAPI
api = JiraRestAPI()
```

### Pitfall 3: Hardcoding Values

❌ **Wrong**:
```python
# Don't hardcode
max_lines = 500
bot_users = ['svc_kaizen_atlassian']
```

✅ **Correct**:
```python
# Use config
max_lines = self.options.get('max_lines', 500)
bot_users = self.options.get('ignore_bot_users', DEFAULT_BOT_USERS)
```

### Pitfall 4: Breaking Backward Compatibility

❌ **Wrong**:
```python
# Renaming parameters breaks existing usage
def analyze_ticket(opts):  # Changed from 'options'
```

✅ **Correct**:
```python
# Add new parameter, keep old one working
def analyze_ticket(options: Dict[str, Any], opts: Dict[str, Any] = None):
    if opts is not None:
        # Support old parameter name
        options = opts
```

## 📚 Key Files Reference

### Must-Read Files

1. **skills/jira_analyzer.md** - Analysis framework (90 lines)
   - Core philosophy
   - Output structure
   - Guidelines for analysis

2. **docs/ANALYSIS_GUIDELINES.md** - Detailed guidelines (200+ lines)
   - Philosophy explanation
   - Good vs bad examples
   - Language guidelines

3. **PROJECT_STATUS.md** - Current state (200+ lines)
   - Architecture
   - Design decisions
   - Statistics

### Key Code Files

```python
# src/cli.py (200 lines)
# - CLI commands
# - Argument parsing
# - Command orchestration

# src/analyzer.py (170 lines)
# - Main workflow
# - Bot filtering
# - Auto-analyze invocation

# src/jira_api.py (230 lines)
# - REST API client
# - Authentication
# - Ticket fetching

# src/filter.py (360 lines)
# - Keyword filtering
# - Token optimization
# - Context extraction
```

## 🎓 Learning Resources

### Understand the Project

```bash
# 1. Read the main README
cat README.md

# 2. Try the quickstart
cat QUICKSTART.md

# 3. Understand the analysis framework
cat skills/jira_analyzer.md

# 4. See example output
cat EXAMPLE_OUTPUT.md
```

### Explore the Code

```bash
# See the main workflow
grep -A 20 "def analyze" src/analyzer.py

# Understand bot filtering
grep -A 15 "_filter_bot_comments" src/analyzer.py

# Check keyword filtering
grep -A 20 "def filter_log" src/filter.py
```

## 🤝 Working with Human Contributors

When collaborating:

1. **Explain your reasoning** - Add comments to complex logic
2. **Ask for clarification** - If requirements are unclear
3. **Suggest alternatives** - Propose multiple approaches
4. **Respect existing decisions** - Don't change core philosophy
5. **Document changes** - Update docs with code changes

## ✅ Pre-Submission Checklist

Before finishing your work:

- [ ] Code follows existing patterns
- [ ] No breaking changes introduced
- [ ] Documentation updated if needed
- [ ] Tested with real Jira tickets
- [ ] No credentials in code
- [ ] Error handling present
- [ ] Console output is clear
- [ ] Follows diagnostic philosophy (if analysis-related)
- [ ] Bot filtering still works
- [ ] Auto-analyze detection still works

## 🆘 Troubleshooting

### "Module not found" errors

```bash
# Ensure you're in the right directory
pwd  # Should end with jira_auto_analyze

# Reinstall package
pip install -e .
```

### "Permission denied" errors

```bash
# Check file permissions
ls -la src/*.py

# Make files readable
chmod 644 src/*.py
```

### API errors

```bash
# Test connection
python test_connection.py

# Check credentials
cat .env  # Ensure proper format
```

## 📝 Summary

**Key Takeaways:**

1. 🎯 **Philosophy**: Diagnostic, not prescriptive
2. 🔧 **Approach**: REST API, not MCP
3. 🤖 **Filtering**: Automatically remove bot comments
4. 📊 **Analysis**: Present hypotheses, not solutions
5. ✅ **Testing**: Always test with real Jira tickets

**When in doubt:**
- Check existing code for patterns
- Read the analysis framework
- Test your changes thoroughly
- Ask for clarification

Happy contributing! 🚀
