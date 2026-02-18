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

**⭐ Recommended: Single command with auto-analysis:**
```bash
# Fetches ticket, processes logs, and automatically invokes GitHub Copilot
python -m src.cli analyze PROJ-123 --keywords "error,crash" --auto-analyze
```

**Basic analysis (manual):**
```bash
python -m src.cli analyze PROJ-123
# Then manually ask Copilot to analyze the generated file
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
  --auto-analyze \
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

1. **Fetch Ticket Data**: Uses Jira REST API to retrieve ticket details, comments, and attachments
2. **Download Attachments**: Downloads log files and zip archives
3. **Process Logs**: Extracts text from log files and zip archives
4. **Filter & Optimize**: Applies keyword filtering and token optimization
5. **Generate Analysis File**: Creates a markdown file with structured ticket data
6. **Analyze with Copilot** (if --auto-analyze): Automatically invokes GitHub Copilot CLI for analysis

## Using Auto-Analysis

With the `--auto-analyze` flag, the tool automatically invokes GitHub Copilot CLI:

```bash
# Single command does everything
python -m src.cli analyze PROJ-123 --keywords "error,crash" --auto-analyze
```

**Without auto-analyze:**
```bash
# Step 1: Generate analysis file
python -m src.cli analyze PROJ-123

# Step 2: Manually ask Copilot
# The tool shows the path, e.g.: analysis_results/PROJ-123/analysis.md
# Then you can ask: "Analyze analysis_results/PROJ-123/analysis.md using jira_analyzer framework"
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
  --auto-analyze
```

### Example 2: Timeout Issues
```bash
python -m src.cli analyze API-789 \
  --keywords "timeout,connection,slow" \
  --context-lines 10 \
  --auto-analyze
```

### Example 3: Batch Analysis
```bash
# List high priority bugs
python -m src.cli list --query "priority = High AND status = Open" --limit 5

# Analyze each one with auto-analysis
for ticket in PROJ-123 PROJ-124 PROJ-125; do
  python -m src.cli analyze $ticket --auto-analyze
done
```
