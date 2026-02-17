"""
Direct Jira ticket fetcher using Atlassian MCP tools.

This script is meant to be referenced by GitHub Copilot CLI to fetch ticket data.
It provides the structure for what data to fetch using MCP tools.
"""

import os
from dotenv import load_dotenv

load_dotenv()

CLOUD_ID = os.getenv('ATLASSIAN_CLOUD_ID')
TICKET_ID = "GOSDK-196102"  # Replace with actual ticket

# Instructions for Copilot CLI to fetch the ticket
FETCH_INSTRUCTIONS = f"""
Please use these Atlassian MCP tools to fetch ticket {TICKET_ID}:

1. Get ticket details:
   Tool: atlassian-getJiraIssue
   Params: cloudId="{CLOUD_ID}", issueIdOrKey="{TICKET_ID}"

2. Get comments (if available):
   Tool: atlassian-searchJiraIssuesUsingJql
   Params: cloudId="{CLOUD_ID}", jql="key = {TICKET_ID}"

3. Format the output as:
   TICKET: {TICKET_ID}
   SUMMARY: [from fields.summary]
   DESCRIPTION: [from fields.description]
   STATUS: [from fields.status.name]
   PRIORITY: [from fields.priority.name]
   
   COMMENTS:
   [list each comment]
   
   ATTACHMENTS:
   [list attachment names and IDs]

Then save this to /tmp/jira_data_{TICKET_ID}.txt
"""

if __name__ == "__main__":
    print(FETCH_INSTRUCTIONS)
