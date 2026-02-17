# Jira Auto Analyze

A CLI tool that analyzes Jira bug tickets using GitHub Copilot as the analysis engine. It intelligently processes ticket comments and log file attachments (including zipped files) to provide comprehensive analysis with summaries, pattern detection, and root cause suggestions.

## Features

- 🎯 **Smart Log Processing**: Extracts and filters relevant sections from log files
- 🔍 **Keyword Filtering**: Reduces noise and optimizes token usage
- 📊 **Comprehensive Analysis**: Summaries, patterns, and root cause suggestions
- 📦 **Zip Support**: Handles compressed log files
- 🔌 **Direct Jira API**: Fetches tickets, comments, and attachments via REST API
- 💾 **Flexible Output**: Terminal display or save to files (Markdown/JSON)
- 🤖 **Auto-Analysis**: Automatically invoke GitHub Copilot CLI after processing

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd jira_auto_analyze

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your Atlassian credentials:
```
ATLASSIAN_CLOUD_ID=your-cloud-id-here
ATLASSIAN_API_TOKEN=your-api-token-here
ATLASSIAN_EMAIL=your-email@example.com
```

3. (Optional) Customize `examples/sample_config.yaml` and save as `config.yaml`

## Usage

### Quick Start (Recommended)

**Single command with automatic analysis:**
```bash
# Analyze ticket and automatically invoke GitHub Copilot
python -m src.cli analyze TICKET-123 --keywords "error,crash,exception" --auto-analyze
```

**Or use the wrapper script:**
```bash
# Use the wrapper script - handles everything automatically
./analyze_ticket.sh TICKET-123

# With options
./analyze_ticket.sh TICKET-123 --keywords "error,timeout"
```

### Manual Usage

```bash
# Step 1: Prepare analysis (without auto-analysis)
python -m src.cli analyze TICKET-123

# Step 2: Manually ask Copilot to analyze
# (Path shown in output: analysis_results/TICKET-123/analysis.md)

# Or analyze with keywords
python -m src.cli analyze TICKET-123 --keywords "error,timeout,failed"

# Save output to file
python -m src.cli analyze TICKET-123 --output results.md

# Use custom config
python -m src.cli analyze TICKET-123 --config my_config.yaml
```

## Requirements

- Python 3.8+
- GitHub Copilot CLI access
- Atlassian account with API access

## License

MIT
