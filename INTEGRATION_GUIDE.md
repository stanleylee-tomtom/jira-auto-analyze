# Integration Guide: Using the Tool with GitHub Copilot CLI

## The Problem

The Jira Auto Analyzer tool was designed to work as a standalone CLI, but it needs to fetch Jira data using **Atlassian MCP tools** which are only available within the GitHub Copilot CLI environment.

## The Solution: Hybrid Approach

The tool should be used in **two stages**:

### Stage 1: You Ask Copilot to Fetch Ticket Data

Instead of running `python -m src.cli analyze TICKET-ID`, start by asking me (Copilot CLI):

```
Fetch Jira ticket GOSDK-196630 from TomTom's Jira using:
- Cloud ID: 1cca41ed-de92-4455-812e-a4a463fc61a9
- Get: summary, description, status, priority, comments, and attachments

Then list all attached files and download any .log, .txt, or .zip files 
to /tmp/jira_attachments_GOSDK-196630/

Format the output as:
TICKET: GOSDK-196630
SUMMARY: [summary]
DESCRIPTION: [description]
...
ATTACHMENTS:
- filename1.log (downloaded to /tmp/...)
- filename2.zip (downloaded to /tmp/...)
```

I'll use these MCP tools:
1. `atlassian-getJiraIssue` - Get ticket details
2. `atlassian-getJiraIssueRemoteIssueLinks` - Get attachments list
3. Download the files (via MCP or direct API)

### Stage 2: Python Tool Processes the Downloaded Files

Once I've downloaded the attachments, you run:

```bash
cd /Users/stanleylee/code/jira_auto_analyze

# Process the logs I downloaded
python -m src.cli analyze GOSDK-196630 \
  --keywords "error,panic,timeout" \
  --max-lines 1000
```

But provide a `--attachment-dir` flag:
```bash
python -m src.cli analyze GOSDK-196630 \
  --attachment-dir /tmp/jira_attachments_GOSDK-196630 \
  --keywords "error,panic,timeout"
```

### Stage 3: Ask Me to Analyze

After the Python tool filters the logs:

```
Analyze the prepared ticket data in /tmp/jira_analysis_GOSDK-196630.txt
following the framework in skills/jira_analyzer.md. Focus on root cause analysis.
```

## Alternative: All-in-One Request

The simplest way is to ask me to do everything:

```
Analyze Jira ticket GOSDK-196630:
1. Fetch ticket details, comments, and attachments
2. Download any log files
3. Filter for errors and relevant sections
4. Provide comprehensive analysis with root cause, patterns, and recommendations
```

I'll handle all the steps internally.

## Why This Approach?

**What works:**
- ✅ Atlassian MCP tools (only I have access)
- ✅ Ticket fetching and attachment downloads (via MCP)
- ✅ AI analysis (that's me!)

**What the Python tool is good for:**
- ✅ Log filtering by keywords
- ✅ Token optimization
- ✅ Extracting error sections
- ✅ Processing zip files
- ✅ Sampling large files

## Update Needed

The Python tool should be enhanced to:
1. Accept `--attachment-dir` flag to process pre-downloaded files
2. Work on already-downloaded ticket data
3. Skip the MCP calls it can't make
4. Focus on log processing and filtering

Let me update the code now...
