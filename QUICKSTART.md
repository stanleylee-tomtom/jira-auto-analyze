# Quick Start Guide

## Installation

1. **Install the package:**
   ```bash
   cd jira_auto_analyze
   pip install -e .
   ```

2. **Configure credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your Atlassian credentials
   ```

3. **Verify setup:**
   ```bash
   python -m src.cli config
   ```

## Usage

### Analyze a Ticket

**Basic analysis:**
```bash
python -m src.cli analyze PROJ-123
```

**With keywords to filter logs:**
```bash
python -m src.cli analyze PROJ-123 --keywords "error,timeout,nullpointer"
```

**Save results to file:**
```bash
python -m src.cli analyze PROJ-123 --output report.md
```

**Custom configuration:**
```bash
python -m src.cli analyze PROJ-123 --config my_config.yaml
```

**Advanced options:**
```bash
python -m src.cli analyze PROJ-123 \
  --keywords "error,exception" \
  --max-lines 1000 \
  --context-lines 10 \
  --depth deep \
  --output analysis_results/PROJ-123.md
```

### List Tickets

**By project:**
```bash
python -m src.cli list --project MYPROJ --status "Open"
```

**With JQL query:**
```bash
python -m src.cli list --query "project = MYPROJ AND priority = High"
```

## How It Works

1. **Fetch Ticket Data**: Uses Atlassian MCP to retrieve ticket details, comments, and attachments
2. **Process Logs**: Extracts text from log files and zip archives
3. **Filter & Optimize**: Applies keyword filtering and token optimization
4. **Generate Analysis Input**: Prepares structured data for GitHub Copilot
5. **Analyze with Copilot**: Uses the `jira_analyzer` skill to perform analysis

## Using the Copilot Skill

The tool generates an analysis input file. To complete the analysis:

```bash
# After running analyze command, you'll get a temp file path
gh copilot --skill skills/jira_analyzer.md < /tmp/jira_analysis_PROJ-123.txt
```

Or use the skill directly in Copilot CLI:
```
@jira_analyzer analyze this ticket:
[paste analysis input]
```

## Configuration File

Create a `config.yaml` based on `examples/sample_config.yaml`:

```yaml
keywords:
  - "error"
  - "exception"
  - "timeout"

context_lines_before: 5
context_lines_after: 5
max_log_lines: 500

sampling:
  enabled: true
  head_lines: 200
  tail_lines: 200

output:
  format: "markdown"
  save_to_file: true
  output_dir: "./analysis_results"

analysis_depth: "deep"
```

## Tips for Better Analysis

1. **Use Specific Keywords**: More specific keywords reduce noise
   - Good: "NullPointerException", "ConnectionTimeout"
   - Too broad: "error", "log"

2. **Adjust Context Lines**: For stack traces, increase context
   ```bash
   --context-lines 15
   ```

3. **Handle Large Logs**: Enable sampling for very large files
   ```bash
   --max-lines 1000
   ```

4. **Focus on Recent Issues**: Use JQL to filter recent tickets
   ```bash
   python -m src.cli list --query "created >= -7d AND priority = High"
   ```

## Troubleshooting

**Missing credentials:**
- Check `.env` file exists and has correct values
- Run `python -m src.cli config` to verify

**No log files found:**
- Verify attachments exist on the ticket
- Check file extensions are supported (.txt, .log, .zip)

**Token limit exceeded:**
- Reduce `--max-lines`
- Add more specific `--keywords`
- Use sampling in config file

## Examples

### Example 1: Production Error Investigation
```bash
python -m src.cli analyze PROD-456 \
  --keywords "OutOfMemory,GC,heap" \
  --depth deep \
  --output reports/oom-analysis.md
```

### Example 2: Timeout Issues
```bash
python -m src.cli analyze API-789 \
  --keywords "timeout,connection,slow" \
  --context-lines 10 \
  --output reports/timeout-analysis.md
```

### Example 3: Batch Analysis
```bash
# List high priority bugs
python -m src.cli list --query "priority = High AND status = Open" --limit 5

# Analyze each one
for ticket in PROJ-123 PROJ-124 PROJ-125; do
  python -m src.cli analyze $ticket --output "reports/${ticket}.md"
done
```

## Next Steps

After Phase 5, the tool has:
- ✅ Project structure and CLI
- ✅ Atlassian MCP integration
- ✅ Log processing (text and zip files)
- ✅ Keyword filtering and token optimization
- ✅ GitHub Copilot skill file
- ✅ Analysis orchestration
- ✅ Output formatting (terminal, markdown, JSON)

Future enhancements (Phases 6-7):
- Testing suite
- Comprehensive documentation
- Caching for faster repeated analysis
- Batch processing mode
