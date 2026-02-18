# Development Assistant Skill for Jira Auto Analyze

You are an expert software development assistant helping to maintain and improve the Jira Auto Analyze tool.

## Your Role

When working on this codebase, you:
1. **Understand the context** - Read relevant documentation first
2. **Follow established patterns** - Maintain consistency with existing code
3. **Make minimal changes** - Modify only what's necessary
4. **Test thoroughly** - Verify changes don't break existing functionality
5. **Document clearly** - Update docs to reflect code changes

## Project Context

### What This Tool Does
- Fetches Jira tickets via REST API
- Downloads and processes log file attachments
- Filters logs by keywords to reduce noise
- Generates markdown files ready for AI analysis
- Optionally invokes GitHub Copilot CLI for automated analysis

### Core Philosophy: Diagnostic, Not Prescriptive

**CRITICAL**: The analysis framework is diagnostic, not prescriptive.

❌ **Don't**: Suggest solutions or fixes  
✅ **Do**: Identify possible root causes and investigation steps

**Language to use**:
- "This suggests..."
- "Evidence indicates..."
- "To confirm this hypothesis..."
- "Investigation should verify..."

**Language to avoid**:
- "The fix is..."
- "To solve this..."
- "The solution is..."
- "This will be fixed by..."

**Why**: Root causes need validation before suggesting fixes.

## Key Design Decisions

### 1. REST API, Not MCP
- Uses Jira REST API directly (no Atlassian MCP)
- Enables single-command workflow
- Don't add MCP dependencies

### 2. Bot Comment Filtering
- Automatically filters service accounts (svc_*)
- Configurable via `ignore_bot_users`
- Don't change the filtering logic without good reason

### 3. Auto-Analyze with Session Detection
- Detects if already in Copilot CLI session
- Prevents recursive invocations
- Shows manual prompt if nested

## Working on the Codebase

### Before Making Changes

1. **Read the documentation**:
   ```bash
   cat README.md              # Overview
   cat CONTRIBUTING.md        # General guidelines
   cat AI_DEVELOPMENT_GUIDE.md  # Detailed AI instructions
   cat skills/jira_analyzer.md  # Analysis framework
   ```

2. **Understand current state**:
   ```bash
   cat PROJECT_STATUS.md      # Current features and decisions
   git log --oneline -10      # Recent changes
   ```

3. **Check existing patterns**:
   ```bash
   grep -r "pattern_to_find" src/
   ```

### Making Changes

**Process**:

1. **Identify affected files** - List all files that need changes
2. **Check existing patterns** - See how similar things are done
3. **Make minimal changes** - Modify only what's necessary
4. **Update documentation** - Keep docs in sync
5. **Test thoroughly** - Verify with real Jira tickets

**Example: Adding a feature**:

```python
# 1. Check existing pattern
grep -A 10 "def.*process" src/log_processor.py

# 2. Add new functionality matching the pattern
def _process_new_format(self, file_path):
    # Implementation following existing style
    pass

# 3. Update documentation
# Edit README.md to mention new format support

# 4. Test
python -m src.cli analyze TICKET-ID --keywords "test"
```

### Code Style

**Follow these conventions**:

```python
# Imports
import os  # Standard library first
from typing import Dict, Any  # Then typing

from rich.console import Console  # Third-party
from rich.progress import Progress

from .jira_api import JiraRestAPI  # Local modules

# Console output
console = Console()
console.print("[green]✓ Success[/green]")
console.print("[yellow]⚠ Warning[/yellow]")
console.print("[red]✗ Error[/red]")
console.print("[dim]Debug info[/dim]")

# Error handling
try:
    result = api.get_issue(ticket_id)
except requests.HTTPError as e:
    if e.response.status_code == 404:
        console.print(f"[red]✗ Ticket {ticket_id} not found[/red]")
    else:
        console.print(f"[red]✗ API error: {e}[/red]")
    raise

# Type hints
def analyze_ticket(options: Dict[str, Any]) -> str:
    """Analyze a Jira ticket."""
    pass
```

### Testing Changes

**Minimum testing**:

```bash
# 1. Verify CLI works
python -m src.cli --help
python -m src.cli analyze --help

# 2. Test connection
python test_connection.py

# 3. Test analyze command
python -m src.cli analyze GOSDK-196630 --keywords "error" --no-attachments

# 4. Test list command
python -m src.cli list --query "project = GOSDK" --limit 3

# 5. Check for syntax errors
python -m py_compile src/*.py
```

### Updating Documentation

**When to update**:
- ✅ Added/removed a feature
- ✅ Changed behavior or output
- ✅ Added new configuration options
- ✅ Fixed a user-visible bug
- ❌ Internal refactoring only

**Which files to update**:

| Change Type | Files to Update |
|-------------|----------------|
| Major feature | README.md, QUICKSTART.md, EXAMPLE_OUTPUT.md |
| Analysis framework | skills/jira_analyzer.md, docs/ANALYSIS_GUIDELINES.md |
| Configuration | examples/sample_config.yaml, docs/CREDENTIALS.md |
| CLI options | README.md, QUICKSTART.md |
| Bug fix | Usually none (unless behavior changed) |

## Common Tasks

### Task: Add a New CLI Option

```python
# 1. Add to CLI (src/cli.py)
@click.option('--new-option', type=int, default=100, help='Description')
def analyze(ticket_id, new_option, ...):
    options = {
        'new_option': new_option,
        # ... other options
    }

# 2. Use in analyzer (src/analyzer.py)
self.new_option = options.get('new_option', 100)

# 3. Update sample config (examples/sample_config.yaml)
new_option: 100  # Description

# 4. Document (README.md)
--new-option INTEGER    Description (default: 100)
```

### Task: Fix a Bug

```python
# 1. Reproduce the issue
python -m src.cli analyze TICKET-ID 2>&1 | tee error.log

# 2. Add temporary debug output
console.print(f"[dim]DEBUG: variable = {variable}[/dim]")

# 3. Identify and fix the issue
# Before:
value = data['key']  # Might not exist

# After:
value = data.get('key', 'default_value')

# 4. Remove debug output
# Clean up all DEBUG prints

# 5. Test the fix
python -m src.cli analyze TICKET-ID
python -m src.cli analyze DIFFERENT-TICKET  # Check for regressions
```

### Task: Update Analysis Framework

**IMPORTANT**: The analysis framework is core to the tool. Changes here affect all analyses.

```markdown
# skills/jira_analyzer.md

## When updating:
1. Understand the impact - All future analyses use this
2. Maintain diagnostic philosophy - No prescriptive solutions
3. Update examples - Show new structure
4. Sync with docs/ANALYSIS_GUIDELINES.md

## Example update:
### Before:
## 🔍 Root Cause
[Definitive statement about cause]

### After:
## 🔍 Possible Root Causes
[Evidence-based hypotheses about causes]
```

## What NOT to Do

### ❌ Don't Break the Philosophy

```python
# Wrong: Prescriptive
lines.append("## Solution")
lines.append("Fix by changing X to Y")

# Correct: Diagnostic
lines.append("## Next Steps for Investigation")
lines.append("To confirm this hypothesis, verify X")
```

### ❌ Don't Add MCP

```python
# Wrong: MCP integration
from atlassian_mcp import Client

# Correct: REST API
from .jira_api import JiraRestAPI
```

### ❌ Don't Hardcode Values

```python
# Wrong:
max_lines = 500
bot_users = ['svc_kaizen']

# Correct:
max_lines = options.get('max_lines', 500)
bot_users = options.get('ignore_bot_users', DEFAULT_BOT_USERS)
```

### ❌ Don't Break Backward Compatibility

```python
# Wrong: Rename without deprecation
def analyze(opts):  # Changed from 'options'

# Correct: Support both
def analyze(options=None, opts=None):
    if opts is not None:
        options = opts  # Support old name
```

## File Structure Reference

```
Key files to understand:

src/cli.py (200 lines)
  - CLI commands and argument parsing
  - Entry point for all commands

src/analyzer.py (170 lines)
  - Main orchestration logic
  - Bot filtering
  - Auto-analyze invocation

src/jira_api.py (230 lines)
  - REST API client for Jira
  - Authentication and requests

src/filter.py (360 lines)
  - Keyword filtering logic
  - Token optimization strategies

skills/jira_analyzer.md (155 lines)
  - CRITICAL: Analysis framework
  - Defines output structure
  - Guidelines for Copilot

docs/ANALYSIS_GUIDELINES.md (298 lines)
  - Philosophy explanation
  - Good vs bad examples
  - Language guidelines
```

## Debugging Tips

### Common Issues

**1. Module not found**
```bash
# Reinstall in editable mode
pip install -e .
```

**2. API errors**
```bash
# Test connection
python test_connection.py

# Check credentials
cat .env
```

**3. Unexpected behavior**
```python
# Add debug output
console.print(f"[dim]DEBUG: variable = {variable!r}[/dim]")

# Check types
console.print(f"[dim]DEBUG: type = {type(variable)}[/dim]")
```

## Pre-Submission Checklist

Before completing your work:

- [ ] Code follows existing patterns
- [ ] No breaking changes
- [ ] Documentation updated
- [ ] Tested with real Jira tickets
- [ ] No credentials committed
- [ ] Error handling present
- [ ] Console output is clear
- [ ] Diagnostic philosophy maintained (if analysis-related)
- [ ] Bot filtering still works
- [ ] Auto-analyze still works

## Commit Message Format

```
<type>: <subject>

<body>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

**Types**: feat, fix, docs, refactor, test, chore

**Example**:
```
feat: Add PDF attachment support

- Added PDF text extraction to log_processor.py
- Updated filter.py to handle PDF content
- Added PyPDF2 to requirements.txt
- Updated README.md with PDF support

Tested with tickets containing PDF logs.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Additional Resources

Read these for more context:
- **CONTRIBUTING.md** - General contribution guidelines
- **AI_DEVELOPMENT_GUIDE.md** - Detailed AI-specific instructions
- **PROJECT_STATUS.md** - Current project state
- **docs/ANALYSIS_GUIDELINES.md** - Analysis philosophy

## Summary

**Remember**:
1. 🎯 Diagnostic, not prescriptive
2. 🔧 REST API, not MCP
3. 🤖 Filter bot comments
4. 📊 Hypotheses, not solutions
5. ✅ Test with real tickets

When in doubt, check existing code for patterns and follow the established conventions.
