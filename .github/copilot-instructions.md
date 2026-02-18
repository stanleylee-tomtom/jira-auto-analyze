# GitHub Copilot Development Instructions

## Project Overview

CLI tool that fetches Jira tickets, downloads attachments, filters logs, and prepares data for AI analysis.

**Architecture Flow:**
```
User → CLI → JiraAPI → Analyzer → OutputGenerator → [Optional: gh copilot]
```

**Key Components:**
- `src/cli.py` - Click-based CLI (analyze, list, config)
- `src/jira_api.py` - REST API v3 client
- `src/analyzer.py` - Main orchestration + bot filtering
- `src/attachment_handler.py` - Download/extract logs
- `src/log_processor.py` - Keyword filtering, token optimization
- `src/output_generator.py` - Prepare analysis input
- `skills/jira_analyzer.md` - **Analysis rules for Copilot CLI**

## Critical Design Rules

### 1. REST API Only (No MCP)
- Use Jira REST API v3 via `requests` library
- Single-command workflow: `jira-analyze TICKET-123`
- **Never** suggest or add MCP/Atlassian MCP integration

### 2. Bot Comment Filtering
- Auto-filter service accounts: `svc_*` pattern
- Configured in `config.yaml` → `ignore_bot_users`
- Filter logic in `src/analyzer.py` lines 95-108

### 3. Auto-Analyze Session Detection
- Detects env vars: `GITHUB_COPILOT_CLI_SESSION`, `COPILOT_SESSION_ID`
- Prevents recursive `gh copilot` invocation
- Implementation in `src/analyzer.py` lines 138-170

## Development Patterns

### Adding CLI Options
```python
# src/cli.py
@click.option('--new-option', help='Description')
def analyze(ticket_id, new_option):
    analyzer = TicketAnalyzer(config, new_option=new_option)
```

### Adding Log Filters
```python
# src/log_processor.py
def filter_by_keywords(self, content, keywords):
    lines = content.split('\n')
    return '\n'.join([l for l in lines if any(k in l for k in keywords)])
```

### Modifying Bot Filter
```python
# src/analyzer.py - _filter_bot_comments()
# Update ignore_bot_users list or pattern matching
```

### API Changes
```python
# src/jira_api.py
# Jira API v3: /rest/api/3/search/jql (not /rest/api/3/search)
# Returns ADF format - extract text from content nodes
```

## Testing Requirements

```bash
# Always test with real ticket before committing
jira-analyze GOSDK-196630 --auto-analyze

# Verify bot filtering works
jira-analyze GOSDK-196630 --keywords "error"

# Test list command
jira-analyze list "project = GOSDK"
```

## What NOT to Do

❌ Add MCP/Atlassian MCP integration  
❌ Remove bot filtering logic  
❌ Skip testing with real Jira tickets  
❌ Break single-command workflow  
❌ Modify analysis rules (those belong in `skills/jira_analyzer.md`)

## File Reference

**Core Logic:**
- `src/analyzer.py` (lines 95-108: bot filtering, 138-170: auto-analyze)
- `src/jira_api.py` (lines 58-116: get_issue_formatted)
- `src/cli.py` (lines 36-120: analyze command)

**Configuration:**
- `.env` - Credentials (never commit)
- `examples/sample_config.yaml` - Bot user list

**Analysis Rules:**
- `skills/jira_analyzer.md` - **All analysis guidelines live here**

## Pre-Commit Checklist

- [ ] Tested with real Jira ticket (GOSDK-196630)
- [ ] Bot filtering still works
- [ ] No MCP references added
- [ ] Documentation updated if needed
- [ ] No credentials in code

