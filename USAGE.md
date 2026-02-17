# How to Use the Jira Auto Analyzer

Since the GitHub Copilot CLI doesn't support custom skill files via command line, here's how to use the tool:

## Method 1: Direct Analysis (Recommended)

Since you're already talking to me (GitHub Copilot CLI), just ask me directly:

```
Analyze Jira ticket GOSDK-196102 from TomTom's Jira. 
Use these credentials from my .env file, fetch the ticket, 
comments, and any log attachments, then provide a comprehensive 
analysis with root cause, patterns, and recommendations.
```

I'll automatically:
1. Use Atlassian MCP tools to fetch the ticket
2. Process any attachments
3. Apply the analysis framework from skills/jira_analyzer.md
4. Give you a comprehensive analysis

## Method 2: Prepared Analysis Input

If you want to pre-filter logs first:

```bash
# Step 1: Prepare the analysis (filters logs, optimizes tokens)
cd /Users/stanleylee/code/jira_auto_analyze
python -m src.cli analyze GOSDK-196102 --keywords "error,exception,panic"

# Step 2: I'll tell you where the file is saved, something like:
# /tmp/jira_analysis_GOSDK-196102.txt

# Step 3: Ask me to analyze it
```

Then say to me:
```
Read the file /tmp/jira_analysis_GOSDK-196102.txt and analyze it 
following the jira_analyzer skill framework. Provide root cause analysis, 
patterns, and recommendations.
```

## Method 3: Use the Skill Framework Manually

The skill file at `skills/jira_analyzer.md` contains the analysis framework. 
You can reference it when asking me to analyze tickets:

```
Analyze ticket GOSDK-196102 following the framework in 
/Users/stanleylee/code/jira_auto_analyze/skills/jira_analyzer.md
```

## Quick Commands

### Just analyze a ticket (I'll fetch it):
```
@workspace Analyze GOSDK-196102
```

### With specific focus:
```
@workspace Analyze GOSDK-196102, focus on timeout and connection errors
```

### Get filtered logs first:
```bash
python -m src.cli analyze GOSDK-196102 --keywords "timeout,error" --max-lines 200
```
Then ask me to analyze the generated file.

## What the Tool Does

The Python tool (`src/cli.py`) is useful for:
- ✅ Filtering large log files by keywords
- ✅ Extracting relevant sections (errors, stack traces)
- ✅ Token optimization (keeping under limits)
- ✅ Processing zip files
- ✅ Sampling large logs (head + tail)

But I (Copilot) can do the actual:
- ✅ Jira ticket fetching (via Atlassian MCP)
- ✅ Analysis and root cause investigation
- ✅ Pattern recognition
- ✅ Recommendations

## Examples

### Example 1: Simple Analysis
You: `Analyze Jira ticket GOSDK-196102`
Me: *fetches ticket, analyzes, provides report*

### Example 2: Focus on Specific Issues
You: `Analyze GOSDK-196102, looking specifically for memory leaks or goroutine issues`
Me: *fetches and analyzes with that focus*

### Example 3: With Log Preprocessing
```bash
# You run:
python -m src.cli analyze GOSDK-196102 --keywords "panic,fatal,error" --output filtered.md

# Then ask me:
# "Analyze the ticket data in filtered.md following the jira_analyzer framework"
```

## Why This Approach?

GitHub Copilot CLI is interactive and works best with conversational requests. 
The tool's value is in **preprocessing** (filtering, optimizing) rather than 
as a separate pipeline. Since I have direct access to Atlassian MCP tools, 
I can fetch tickets directly when you ask.

## Need Help?

Just ask me:
- "How do I analyze ticket X?"
- "Get ticket GOSDK-196102 and analyze it"
- "What's in ticket GOSDK-196102?"
- "Analyze this ticket focusing on [specific issue]"
