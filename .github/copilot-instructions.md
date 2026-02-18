# GitHub Copilot Instructions for jira-auto-analyze

## Project Overview

A CLI tool that analyzes Jira bug tickets using AI. It fetches ticket data, downloads attachments (including logs), filters noise, and generates diagnostic analysis using GitHub Copilot.

**Core Philosophy: DIAGNOSTIC, NOT PRESCRIPTIVE**
- Identify possible root causes (NOT solutions)
- Present findings as hypotheses requiring confirmation
- Use uncertainty language ("suggests", "likely", "indicates")
- Avoid prescriptive recommendations ("the fix is", "to solve this")

## Architecture

```
User → CLI → JiraAPI → Analyzer → OutputGenerator → [Optional: gh copilot]
                ↓
         Download attachments
                ↓
         Filter logs (keywords)
                ↓
         Generate analysis input
```

**Key Components:**
- `src/cli.py` - Click-based CLI (analyze, list, config commands)
- `src/jira_api.py` - REST API v3 client (NO MCP)
- `src/analyzer.py` - Main orchestration + bot filtering
- `src/attachment_handler.py` - Download/extract logs
- `src/log_processor.py` - Keyword filtering, token optimization
- `src/output_generator.py` - Prepare analysis input
- `skills/jira_analyzer.md` - Analysis framework for Copilot

## Critical Design Decisions

### 1. REST API, Not MCP
- Direct Jira REST API v3 usage via `requests`
- Single-command workflow: `jira-analyze TICKET-123`
- Never suggest or implement MCP/Atlassian integration

### 2. Bot Comment Filtering
- Automatically filters service accounts: `svc_kaizen_atlassian`, `svc_jiradel_svc`, `svc_navsdk_jira`, `svc_*`
- Configured via `ignore_bot_users` in config.yaml
- Critical for reducing noise in analysis

### 3. Auto-Analyze with Session Detection
- `--auto-analyze` flag invokes `gh copilot` automatically
- Detects nested sessions (GITHUB_COPILOT_CLI_SESSION, COPILOT_SESSION_ID)
- Falls back to manual prompt when inside Copilot session

### 4. Diagnostic Analysis Framework
- **Sections:** Summary → Possible Root Causes → Patterns & Observations → Technical Details → Next Steps for Investigation → Risk Assessment
- **Language:** "likely", "suggests", "to confirm" (NOT "the fix is", "the solution")
- **Defined in:** `skills/jira_analyzer.md` (read this first!)

## Common Tasks

### Adding a CLI Option
```python
# In src/cli.py
@click.option('--new-option', help='Description')
def analyze(ticket_id, new_option):
    # Update Analyzer initialization
    analyzer = TicketAnalyzer(config, new_option=new_option)
```

### Adding a Log Filter
```python
# In src/log_processor.py - LogProcessor.filter_by_keywords()
def filter_by_keywords(self, content, keywords):
    lines = content.split('\n')
    filtered = [line for line in lines if any(kw in line for kw in keywords)]
    return '\n'.join(filtered)
```

### Updating Analysis Framework
**⚠️ Changes affect ALL future analyses**
1. Edit `skills/jira_analyzer.md`
2. Test with: `jira-analyze GOSDK-196630 --auto-analyze`
3. Review output to verify changes applied

### Fixing API Issues
```python
# In src/jira_api.py
# Jira API v3 uses /rest/api/3/search/jql (not /rest/api/3/search)
# Returns ADF format - extract text from content nodes
```

## Testing

```bash
# Test with real ticket
jira-analyze GOSDK-196630 --auto-analyze

# Test bot filtering (should remove svc_* comments)
jira-analyze GOSDK-196630 --keywords "error,exception" 

# Test list command
jira-analyze list "project = GOSDK AND status = Open"
```

## What NOT to Do

❌ **Don't** add MCP/Atlassian integration (removed for good reasons)  
❌ **Don't** make analysis prescriptive (provide solutions)  
❌ **Don't** remove bot filtering (svc_* accounts add noise)  
❌ **Don't** change diagnostic language to certainty ("the fix is...")  
❌ **Don't** skip testing with real Jira tickets  
❌ **Don't** break the single-command workflow  

## File Reference

**Core Logic:**
- `src/analyzer.py` - Main workflow, bot filtering (lines 95-108)
- `src/jira_api.py` - REST API client (lines 58-116: get_issue_formatted)
- `src/cli.py` - CLI interface (lines 36-120: analyze command)

**Critical Framework:**
- `skills/jira_analyzer.md` - **MOST CRITICAL** - defines analysis structure
- `docs/ANALYSIS_GUIDELINES.md` - Detailed philosophy and examples

**Configuration:**
- `.env` - Credentials (excluded from git)
- `examples/sample_config.yaml` - Default settings + bot user list

## Pre-Submission Checklist

- [ ] Maintains diagnostic (not prescriptive) approach
- [ ] Uses REST API (no MCP references)
- [ ] Preserves bot comment filtering
- [ ] Tested with real Jira ticket
- [ ] Updated relevant documentation
- [ ] No credentials in code

## Quick Wins

**Fix a bug:** Check PROJECT_STATUS.md → Technical Quirks  
**Add feature:** Follow existing patterns in src/analyzer.py  
**Update docs:** Keep README, QUICKSTART, and EXAMPLE_OUTPUT in sync  
**Test changes:** Use GOSDK-196630 (known ticket with attachments)
