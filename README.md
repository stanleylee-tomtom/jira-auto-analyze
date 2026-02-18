# Jira Auto Analyze

[![GitHub](https://img.shields.io/badge/GitHub-jira--auto--analyze-blue?logo=github)](https://github.com/stanleylee-tomtom/jira-auto-analyze)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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
git clone https://github.com/stanleylee-tomtom/jira-auto-analyze.git
cd jira-auto-analyze

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
- GitHub Copilot CLI (with `gh copilot` extension installed)
- Atlassian account with API access

## Next Steps

Once installed and configured:

1. **Test your setup:**
   ```bash
   python test_connection.py
   ```

2. **Try analyzing a ticket:**
   ```bash
   python -m src.cli analyze YOUR-TICKET-ID --keywords "error,crash" --auto-analyze
   ```

3. **Customize for your needs:**
   - Create a `config.yaml` based on `examples/sample_config.yaml`
   - Add your commonly-used keywords
   - Configure bot user filters for your organization

4. **Learn more:**
   - Read [QUICKSTART.md](QUICKSTART.md) for detailed usage
   - Check [docs/AUTO_ANALYZE_GUIDE.md](docs/AUTO_ANALYZE_GUIDE.md) for auto-analysis options
   - See [docs/ANALYSIS_GUIDELINES.md](docs/ANALYSIS_GUIDELINES.md) for analysis philosophy

## Contributing

We welcome contributions! This project is designed to work well with AI-assisted development tools.

**For GitHub Copilot users:** See [.github/copilot-instructions.md](.github/copilot-instructions.md)  
**For all contributors:** Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for current state and technical decisions

Key guidelines:
- Maintain diagnostic (not prescriptive) analysis approach
- Use REST API (no MCP integration)
- Test with real Jira tickets
- Follow existing code patterns

## License

MIT
