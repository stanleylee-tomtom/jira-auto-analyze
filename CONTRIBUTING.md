# Contributing to Jira Auto Analyze

Thank you for your interest in contributing! This guide is designed for both human and AI contributors to understand the project structure, design decisions, and development practices.

## 🤖 For AI Contributors

This project is designed to be AI-friendly. When contributing with AI assistance:

1. **Read this file first** - It contains critical context
2. **Review [AI_DEVELOPMENT_GUIDE.md](AI_DEVELOPMENT_GUIDE.md)** - Detailed instructions for AI tools
3. **Check [docs/ANALYSIS_GUIDELINES.md](docs/ANALYSIS_GUIDELINES.md)** - Core philosophy
4. **Follow the existing patterns** - Consistency is key

## 📋 Project Overview

### What This Tool Does

A CLI tool that:
1. Fetches Jira tickets via REST API
2. Downloads and processes log file attachments
3. Filters logs by keywords to reduce noise
4. Generates markdown analysis files
5. Optionally invokes GitHub Copilot CLI for analysis

### Core Philosophy

**Diagnostic, Not Prescriptive**
- Focus on identifying **possible root causes**
- Present findings as **hypotheses needing confirmation**
- Avoid suggesting solutions (root cause not confirmed yet)
- Use uncertainty language ("likely", "suggests", "indicates")

## 🏗️ Project Structure

```
jira-auto-analyze/
├── src/                    # Source code
│   ├── cli.py             # CLI entry point (Click framework)
│   ├── analyzer.py        # Main orchestration + bot filtering
│   ├── jira_api.py        # REST API client for Jira
│   ├── downloader.py      # Attachment downloader
│   ├── log_processor.py   # Log file processing (text, zip)
│   ├── filter.py          # Keyword filtering + token optimization
│   └── output.py          # Output formatting
│
├── skills/                 # Analysis framework for Copilot
│   └── jira_analyzer.md   # CRITICAL: Analysis guidelines
│
├── docs/                   # Documentation
│   ├── ANALYSIS_GUIDELINES.md    # Philosophy and examples
│   ├── AUTO_ANALYZE_GUIDE.md     # Auto-analyze feature
│   └── CREDENTIALS.md            # Setup instructions
│
├── examples/
│   └── sample_config.yaml  # Configuration template
│
└── tests/                  # Test directory
```

## 🎯 Key Design Decisions

### 1. REST API, Not MCP
- **Why**: MCP required too many manual steps
- **Result**: Single-command workflow
- **Don't**: Add MCP dependencies or references

### 2. Bot Comment Filtering
- **Why**: Auto-triage comments add noise
- **Implementation**: Filter `svc_*`, `automation`, `bot` users
- **Configurable**: Via `ignore_bot_users` in config

### 3. Diagnostic Analysis
- **Why**: Root causes need confirmation before suggesting fixes
- **Language**: Use "likely", "suggests", "indicates"
- **Structure**: Possible Causes → Investigation Steps (NOT Solutions)

### 4. Auto-Analyze with Session Detection
- **Why**: Prevent recursive Copilot invocations
- **Implementation**: Detect `GITHUB_COPILOT_CLI_SESSION` env var
- **Fallback**: Show manual prompt if in session

## 🛠️ Development Guidelines

### Before Making Changes

1. **Understand the context**:
   ```bash
   # Read the analysis framework
   cat skills/jira_analyzer.md
   
   # Check current implementation
   grep -r "def analyze" src/
   
   # Review recent changes
   git log --oneline -10
   ```

2. **Test existing functionality**:
   ```bash
   python test_connection.py
   python -m src.cli analyze TICKET-ID --keywords "error" --no-attachments
   ```

### Making Changes

#### Code Changes

**Follow these principles:**

1. **Minimal changes** - Modify as few lines as possible
2. **Consistent style** - Match existing code patterns
3. **No breaking changes** - Maintain backward compatibility
4. **Test changes** - Verify with real Jira tickets

**Example patterns to follow:**

```python
# CLI commands use Click decorators
@cli.command()
@click.argument('ticket_id')
@click.option('--keywords', '-k', help='...')
def analyze(ticket_id, keywords):
    pass

# Use Rich console for output
from rich.console import Console
console = Console()
console.print("[green]✓ Success[/green]")

# Use JiraRestAPI for all Jira access
from .jira_api import JiraRestAPI
api = JiraRestAPI()
ticket = api.get_issue_formatted(ticket_id)
```

#### Documentation Changes

**When updating docs:**

1. **Keep consistency** - Use the same terminology across all files
2. **No outdated references** - Remove mentions of deprecated features
3. **Update all affected files** - If changing terminology, update everywhere

**Critical files to keep in sync:**
- `skills/jira_analyzer.md` - Analysis framework (used by Copilot)
- `docs/ANALYSIS_GUIDELINES.md` - Detailed guidelines
- `README.md` - Quick reference
- `QUICKSTART.md` - Getting started

#### Testing Changes

**Minimum testing requirements:**

```bash
# 1. Verify tool works
python -m src.cli --help

# 2. Test analyze command
python -m src.cli analyze GOSDK-196630 --keywords "error" --no-attachments

# 3. Test list command
python -m src.cli list --query "project = GOSDK" --limit 3

# 4. Verify no Python errors
python -m py_compile src/*.py
```

### Commit Messages

Use conventional commits format:

```
<type>: <subject>

<body>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

**Examples:**
```
feat: Add support for PDF attachments

- Added PDF text extraction to log_processor.py
- Updated filter.py to handle PDF content
- Added PyPDF2 to requirements.txt

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## 🚫 What NOT to Do

### ❌ Don't Add These

1. **MCP Integration** - Project uses REST API, not MCP
2. **Prescriptive Solutions** - Analysis should be diagnostic only
3. **New Dependencies** - Unless absolutely necessary
4. **Breaking Changes** - Maintain backward compatibility
5. **Hardcoded Values** - Use config files or env vars

### ❌ Don't Change These

1. **Analysis Framework** - The diagnostic philosophy is core
2. **Bot Filtering Logic** - Unless fixing a bug
3. **REST API Approach** - Don't switch back to MCP
4. **File Structure** - Keep the same organization

### ❌ Don't Forget These

1. **Update documentation** - Keep docs in sync with code
2. **Test with real tickets** - Verify against actual Jira
3. **Check .gitignore** - Never commit `.env` or credentials
4. **Add Co-authored-by** - Credit Copilot in commits

## 📝 Specific Contribution Areas

### Adding New Features

**Example: Adding support for new attachment types**

1. Update `log_processor.py`:
   ```python
   def process_attachment(self, file_path):
       if file_path.endswith('.pdf'):
           return self._process_pdf(file_path)
       # ... existing code
   ```

2. Update `requirements.txt` if needed:
   ```
   PyPDF2==3.0.0
   ```

3. Update documentation:
   - README.md: Add PDF to supported formats
   - QUICKSTART.md: Mention PDF support

4. Test thoroughly:
   ```bash
   # Test with a ticket that has PDF attachments
   python -m src.cli analyze TICKET-WITH-PDF --keywords "error"
   ```

### Fixing Bugs

**Process:**

1. Reproduce the bug
2. Write a test case (if possible)
3. Fix with minimal changes
4. Verify fix works
5. Check for side effects
6. Update docs if behavior changed

### Improving Documentation

**Guidelines:**

1. **Accuracy** - Ensure all information is current
2. **Clarity** - Use clear, simple language
3. **Examples** - Include practical examples
4. **Consistency** - Use same terms across all docs

**Review checklist:**
- [ ] No MCP references (except in PROJECT_STATUS.md explaining why we don't use it)
- [ ] Terminology matches (Possible Root Causes, not Root Cause)
- [ ] Instructions tested and work
- [ ] Links to other docs are correct
- [ ] Code examples are accurate

## 🤝 Pull Request Process

1. **Fork and create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following guidelines above

3. **Test thoroughly**:
   ```bash
   python test_connection.py
   python -m src.cli analyze TEST-TICKET --keywords "error"
   ```

4. **Update documentation** if needed

5. **Commit with clear message**:
   ```bash
   git commit -m "feat: Add feature X

   - Detailed description
   - What changed
   - Why it changed
   
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

## 🔍 Code Review Checklist

Before submitting, verify:

- [ ] Code follows existing patterns
- [ ] No breaking changes
- [ ] Documentation updated
- [ ] Tested with real Jira tickets
- [ ] No hardcoded values
- [ ] No credentials committed
- [ ] Error handling present
- [ ] Console output is clear
- [ ] Follows diagnostic philosophy (if analysis-related)

## 📚 Additional Resources

- **Analysis Framework**: [skills/jira_analyzer.md](skills/jira_analyzer.md)
- **AI Development Guide**: [AI_DEVELOPMENT_GUIDE.md](AI_DEVELOPMENT_GUIDE.md)
- **Analysis Guidelines**: [docs/ANALYSIS_GUIDELINES.md](docs/ANALYSIS_GUIDELINES.md)
- **Auto-Analyze Guide**: [docs/AUTO_ANALYZE_GUIDE.md](docs/AUTO_ANALYZE_GUIDE.md)
- **Project Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 💡 Questions?

If you're unsure about something:

1. Check existing code for similar patterns
2. Review the documentation
3. Test your approach with a simple example
4. Open an issue for discussion

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
