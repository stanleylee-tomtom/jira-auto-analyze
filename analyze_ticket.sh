#!/bin/bash
# Jira Analyzer - Wrapper script for GitHub Copilot CLI integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="$SCRIPT_DIR/skills/jira_analyzer.md"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    cat << EOF
Jira Auto Analyze - Analyze Jira tickets with GitHub Copilot

USAGE:
    ./analyze_ticket.sh TICKET-ID [OPTIONS]

EXAMPLES:
    # Analyze a ticket
    ./analyze_ticket.sh PROJ-123
    
    # With keywords
    ./analyze_ticket.sh PROJ-123 --keywords "error,timeout"
    
    # Save output
    ./analyze_ticket.sh PROJ-123 --output report.md

The script will:
1. Fetch ticket data from Jira
2. Process log files
3. Prepare analysis input
4. Launch GitHub Copilot CLI with the prepared prompt

For more options, run:
    python -m src.cli analyze --help

EOF
}

if [ "$1" == "--help" ] || [ "$1" == "-h" ] || [ -z "$1" ]; then
    show_help
    exit 0
fi

# Change to project directory
cd "$SCRIPT_DIR"

# Check if gh copilot is available
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠ GitHub CLI (gh) is not installed${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Prepare the analysis
echo -e "${BLUE}🔍 Preparing ticket analysis...${NC}"
python -m src.cli analyze "$@"

# Get the temp file path
TICKET_ID="$1"
TEMP_FILE="/tmp/jira_analysis_${TICKET_ID}.txt"

if [ ! -f "$TEMP_FILE" ]; then
    echo -e "${YELLOW}⚠ Could not find analysis file: $TEMP_FILE${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Analysis prepared${NC}"
echo ""
echo -e "${BLUE}📋 Analysis Input Preview:${NC}"
head -20 "$TEMP_FILE"
echo "..."
echo ""

# Read the skill instructions
SKILL_INSTRUCTIONS=$(cat "$SKILL_FILE")

# Create the combined prompt
PROMPT_FILE="/tmp/jira_copilot_prompt_${TICKET_ID}.txt"
cat > "$PROMPT_FILE" << PROMPT_EOF
You are a Jira bug analyst. Analyze this ticket following the framework below:

$SKILL_INSTRUCTIONS

---

Here is the ticket data to analyze:

$(cat "$TEMP_FILE")
PROMPT_EOF

echo -e "${YELLOW}🤖 Launching GitHub Copilot CLI...${NC}"
echo ""
echo -e "${BLUE}Prompt:${NC} Analyze this Jira ticket"
echo ""

# Launch gh copilot with the prompt
cat "$PROMPT_FILE" | gh copilot

# Cleanup
rm -f "$PROMPT_FILE"

echo ""
echo -e "${GREEN}✓ Analysis complete${NC}"
