# Example Usage with Auto-Analysis

## Command
```bash
python -m src.cli analyze GOSDK-196630 --keywords "crash,error,exception" --auto-analyze
```

## What Happens

1. **Fetches ticket from Jira**
   - Retrieves ticket metadata (summary, priority, status)
   - Fetches all comments
   - Gets attachment list

2. **Downloads attachments**
   - Downloads log files (`.log`, `.txt`)
   - Extracts files from `.zip` archives
   - Progress bar shows download status

3. **Processes and filters logs**
   - Searches for keyword matches (crash, error, exception)
   - Extracts context lines around matches
   - Optimizes for token limits
   - Shows: "213 keyword matches found"

4. **Generates analysis file**
   - Creates: `analysis_results/GOSDK-196630/analysis.md`
   - Includes: ticket info, description, comments, filtered logs

5. **Automatically invokes GitHub Copilot** 🤖
   - Runs: `gh copilot` with analysis prompt
   - Uses `jira_analyzer` framework
   - Generates comprehensive analysis with:
     - 📋 Summary
     - 🔍 Root Cause Analysis
     - 📊 Patterns & Observations
     - 🔧 Technical Details
     - 💡 Recommendations

## Output Structure

```
analysis_results/
└── GOSDK-196630/
    ├── analysis.md              # Main analysis file (ready for Copilot)
    ├── ticket_metadata.txt      # Raw ticket data
    └── attachments/
        └── logcat-mapupdate-crash.log
```

## Time Savings

**Without auto-analyze:**
- Run tool: `python -m src.cli analyze TICKET-ID`
- Copy file path from output
- Ask Copilot: "Analyze <path> using jira_analyzer framework"
- Total: 3 manual steps

**With auto-analyze:**
- Run: `python -m src.cli analyze TICKET-ID --auto-analyze`
- Total: 1 command ✨

## Benefits

✅ **Single command workflow** - No manual steps needed  
✅ **Consistent prompts** - Always uses the jira_analyzer framework correctly  
✅ **Faster analysis** - Go from ticket ID to insights in one command  
✅ **Less error-prone** - No copy-paste mistakes with file paths  
