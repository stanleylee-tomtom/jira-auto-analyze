# How to Use: Simple 2-Step Process

## For Ticket GOSDK-196630 (or any ticket)

### Step 1: Ask Me (Copilot) to Download Attachments

Just say to me in this chat:

```
Download all attachments from Jira ticket GOSDK-196630. 
Use cloud ID: 1cca41ed-de92-4455-812e-a4a463fc61a9
Save log files to: /tmp/jira_attachments_GOSDK-196630/
```

I'll:
- Fetch the ticket using `atlassian-getJiraIssue`
- Get the attachments list
- Download .log, .txt, and .zip files

### Step 2: Run the Python Tool to Process Logs

```bash
cd /Users/stanleylee/code/jira_auto_analyze

python -m src.cli analyze GOSDK-196630 \
  --attachment-dir /tmp/jira_attachments_GOSDK-196630 \
  --keywords "error,panic,timeout" \
  --max-lines 1000 \
  --output analysis_GOSDK-196630.md
```

This will:
- Process all downloaded logs
- Filter by your keywords
- Extract error sections
- Optimize for token limits
- Create a comprehensive input file

### Step 3: Ask Me to Analyze

```
Analyze the ticket data in analysis_GOSDK-196630.md 
following the jira_analyzer skill framework. 
Provide root cause analysis and recommendations.
```

---

## Even Simpler: All-in-One

Just ask me:

```
Analyze Jira ticket GOSDK-196630 completely:
1. Fetch ticket details and comments
2. Download all log attachments  
3. Look for errors, panics, and timeouts
4. Provide comprehensive analysis with root cause
```

I'll do everything and give you the analysis directly.

---

## For Next Time

The tool now supports `--attachment-dir` flag, so the workflow is:
1. Ask me to download attachments
2. Run Python tool with `--attachment-dir` 
3. Ask me to analyze the processed output

This gives you control over the filtering while leveraging my MCP access for downloads.
