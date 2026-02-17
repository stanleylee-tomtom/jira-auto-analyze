# Auto-Analyze Feature Guide

## Overview

The `--auto-analyze` flag automatically invokes GitHub Copilot CLI after processing a Jira ticket, creating a seamless one-command workflow.

## Usage

### Basic Command

```bash
python -m src.cli analyze TICKET-ID --keywords "error,crash" --auto-analyze
```

### What It Does

1. Fetches the Jira ticket
2. Downloads and processes attachments
3. Filters logs with your keywords
4. Generates `analysis_results/TICKET-ID/analysis.md`
5. **Automatically invokes** `gh copilot` to analyze the file

## Behavior in Different Contexts

### 1. Running from Terminal (Recommended)

When you run the command from your regular terminal, it will:
- Launch `gh copilot` automatically
- Show the full Copilot analysis interactively
- Work seamlessly with no additional steps

```bash
# From your terminal
$ python -m src.cli analyze GOSDK-196630 --keywords "crash,error" --auto-analyze

🔍 Analyzing ticket: GOSDK-196630
✓ Fetched: Cancelling map update results in a crash...
✓ Downloaded 1/1 files
✓ Analysis Ready

🤖 Preparing Copilot Analysis...
Running: gh copilot...

[Copilot analysis appears here automatically]
```

### 2. Running Inside Copilot Session

If you're already in a GitHub Copilot CLI session (like now), the tool **detects this** and shows a friendly message instead of trying to invoke Copilot recursively:

```bash
🤖 Preparing Copilot Analysis...

⚠ Already inside a GitHub Copilot CLI session
Cannot invoke gh copilot recursively.

📋 Please ask Copilot:
Analyze analysis_results/TICKET-ID/analysis.md using jira_analyzer framework
```

This prevents errors and gives you the exact prompt to use.

## When to Use Each Mode

### Use `--auto-analyze` when:
- ✅ Running from your regular terminal
- ✅ You want a fully automated workflow
- ✅ Analyzing multiple tickets in a script
- ✅ You're not already in a Copilot session

### Skip `--auto-analyze` when:
- ❌ Already inside a Copilot CLI session
- ❌ You want to review the generated file first
- ❌ You need to customize the analysis prompt
- ❌ Working with very large tickets (review before analyzing)

## Examples

### Example 1: Terminal Workflow (Fully Automated)

```bash
# From terminal - everything happens automatically
python -m src.cli analyze PROD-456 \
  --keywords "OutOfMemory,GC,heap" \
  --auto-analyze

# Output includes automatic Copilot analysis
```

### Example 2: Inside Copilot Session (Manual Prompt)

```bash
# Inside Copilot CLI session
python -m src.cli analyze PROD-456 \
  --keywords "OutOfMemory,GC,heap" \
  --auto-analyze

# Tool detects session and shows:
# "Please ask Copilot: Analyze analysis_results/PROD-456/analysis.md using jira_analyzer framework"

# Then you just ask me (Copilot):
Analyze analysis_results/PROD-456/analysis.md using jira_analyzer framework
```

### Example 3: Batch Processing from Terminal

```bash
#!/bin/bash
# Process multiple tickets automatically
for ticket in PROJ-123 PROJ-124 PROJ-125; do
  echo "Processing $ticket..."
  python -m src.cli analyze $ticket \
    --keywords "error,crash" \
    --auto-analyze
  
  echo "---"
  sleep 2
done
```

## Troubleshooting

### Error: "Permission denied and could not request permission from user"

**Cause:** You're inside a Copilot CLI session trying to invoke another instance.

**Solution:** 
1. Don't use `--auto-analyze` when already in Copilot CLI
2. Or, use the manual prompt shown in the output

### Error: "GitHub Copilot CLI (gh copilot) not found"

**Cause:** The `gh` extension for Copilot is not installed.

**Solution:**
```bash
gh extension install github/gh-copilot
```

### The command hangs or doesn't respond

**Cause:** The subprocess might be waiting for input.

**Solution:** 
- Press Ctrl+C to cancel
- Try without `--auto-analyze`
- Manually analyze the generated file

## Advanced Usage

### Custom Analysis Prompts

If you want to use a custom prompt instead of the default, skip `--auto-analyze` and run manually:

```bash
# Step 1: Generate the file
python -m src.cli analyze TICKET-ID --keywords "error,crash"

# Step 2: Use your custom prompt
# The tool shows: "Saved to: analysis_results/TICKET-ID/analysis.md"

# Then ask Copilot with your custom instructions:
Analyze analysis_results/TICKET-ID/analysis.md and focus on memory leaks
```

### Reviewing Before Analysis

```bash
# Step 1: Generate without auto-analysis
python -m src.cli analyze TICKET-ID --keywords "error,crash"

# Step 2: Review the generated file
cat analysis_results/TICKET-ID/analysis.md

# Step 3: If it looks good, ask Copilot manually
# Or re-run with --auto-analyze
```

## Best Practices

1. **Use specific keywords** - Reduces noise and improves analysis quality
   ```bash
   --keywords "NullPointerException,ConnectionTimeout"  # Good
   --keywords "error"  # Too broad
   ```

2. **Review large tickets first** - For tickets with many attachments, review the generated file before analyzing:
   ```bash
   # Generate first
   python -m src.cli analyze HUGE-TICKET --keywords "crash"
   
   # Check size
   wc -l analysis_results/HUGE-TICKET/analysis.md
   
   # If reasonable, analyze manually or re-run with --auto-analyze
   ```

3. **Use in terminal for automation** - Put in scripts for batch processing
   ```bash
   # analyze_bugs.sh
   python -m src.cli analyze "$1" --keywords "error,crash,exception" --auto-analyze
   ```

4. **Skip when in Copilot** - If you're already chatting with Copilot, don't use the flag
   - The tool will detect it and show you what to ask
   - Just copy the suggested prompt

## Summary

| Context | Command | Result |
|---------|---------|--------|
| **Terminal** | `... --auto-analyze` | ✅ Fully automated, gh copilot runs |
| **Copilot Session** | `... --auto-analyze` | ℹ️ Shows prompt to ask manually |
| **Either** | No flag | 📄 Generates file, shows path |

The `--auto-analyze` flag is smart and adapts to your context!
