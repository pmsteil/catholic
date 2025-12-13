# ✟ Chapter Review Scripts

Automated chapter review tools for Catholic book manuscripts using Claude Code agents.

## Setup

First, ensure you have `uv` installed (the script will auto-install dependencies):

```bash
./bin/setup-chapter-reviewer.sh
```

Or install `uv` manually:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

No need to manually install dependencies - `uv` handles everything automatically!

## Usage

### Review All Chapters with an Agent

Run the chapter reviewer with any agent name. Here are examples for each available agent:

**Review all chapters:**
```bash
./bin/chapter-reviewer.py CCCR           # All chapters with CCCR
./bin/chapter-reviewer.py DOCTRINE       # All chapters with DOCTRINE
./bin/chapter-reviewer.py SCRIBE         # All chapters with SCRIBE
```

**Review specific chapters:**
```bash
./bin/chapter-reviewer.py CCCR chapter_01.md
./bin/chapter-reviewer.py DOCTRINE chapter_01.md chapter_02.md chapter_03.md
```

Or use any other agent following the naming pattern in `.agents/workflows/`

### What It Does

1. **Finds all chapters** matching the pattern `chapter_*.md`
2. **Locates the agent workflow** in `.agents/workflows/`
3. **Reviews each chapter** using Claude Code in batch mode
4. **Displays beautiful results** with Catholic-themed colors and formatting
5. **Generates a professional HTML report** saved as `{AGENT}-review1.html` (incremented to never overwrite)

### Output

The script provides:

- **Live progress** with real-time updates for each chapter:
  - Status (✓ PASS / ✗ FAIL)
  - Check counts (passed/failed)
  - Token usage and cost
  - Processing time
- **Incremental HTML updates** - report updates after each chapter (safe if interrupted)
- **Summary statistics** showing passed/failed/error counts
- **Detailed failure reports** with:
  - Failed checks
  - Issue descriptions
  - Location references
  - Recommendations for fixes
- **Success summary** of chapters that passed
- **Token usage totals** - cumulative input/output tokens, cost, and time
- **Professional HTML report** saved to `{AGENT}-review{N}.html` (suitable for Bishop's office submission)

### Example Output

```
✟ Catholic Book Chapter Reviewer ✟
      Ad Maiorem Dei Gloriam

📂 Looking for chapters in: /path/to/chapters
Found 16 chapters
🤖 Looking for agent workflow: CCCR
Found workflow: CCCR-ccc-quote-reviewer.md

Reviewing chapters...
  ✓ chapter_01.md (5✓ 0✗) 3,245tok $0.0089 4.2s
  ✓ chapter_02.md (4✓ 0✗) 2,891tok $0.0076 3.8s
  ✗ chapter_03.md (3✓ 2✗) 4,103tok $0.0112 5.1s
  ...

✟ Chapter Review Results ✟
Agent: CCCR
Chapters Reviewed: 16

📊 Summary
┌─────────┬───────┬────────────┐
│ Status  │ Count │ Percentage │
├─────────┼───────┼────────────┤
│ ✓ Passed│    14 │      87.5% │
│ ✗ Failed│     2 │      12.5% │
└─────────┴───────┴────────────┘

✓ Review Complete
Report saved to: CCCR-review1.html

📊 Total Usage:
  Input tokens: 48,203
  Output tokens: 12,847
  Total tokens: 61,050
  Total cost: $0.1429
  Total time: 67.3s (1.1m)
```

### Available Agents

Agent workflows are stored in [.agents/workflows/](.agents/workflows/). Current agents include:

- **CCCR** - Catechism of the Catholic Church quote reviewer
- **DOCTRINE** - Doctrinal accuracy reviewer
- **SCRIBE** - General writing and grammar reviewer

Add new agents by creating workflow files following the pattern in `.agents/workflows/`.

### Advanced Options

```bash
# Specify custom chapters directory
./bin/chapter-reviewer.py CCCR --chapters-dir /path/to/chapters

# Specify custom output directory for reports
./bin/chapter-reviewer.py CCCR --output-dir /path/to/reports

# Get help
./bin/chapter-reviewer.py --help
```

## How It Works

1. The script uses the Claude Code CLI in batch mode (`claude -p`)
2. It passes chapter files and agent workflow files using `@` file references
3. It requests JSON-formatted output for easy parsing
4. It assembles results and generates both console and professional HTML reports
5. HTML reports feature Catholic theming, professional styling, and are print-ready
6. Review files are incrementally numbered (review1.html, review2.html, etc.) to preserve history

## API Call Logging

When using the Anthropic API (`--api` flag), all API calls are logged to `reports/.chapter-reviewer-logs/` for cost tracking and debugging.

### Log Location
```
reports/.chapter-reviewer-logs/
├── 20251213_054700_CONCISE_chapter_01.json
├── 20251213_054815_CONCISE_chapter_02.json
└── ...
```

### Log Contents
Each JSON log file contains:
```json
{
  "timestamp": "2025-12-13T05:47:00.123456",
  "chapter": "chapter_14.md",
  "agent": "CONCISE",
  "model": "claude-sonnet-4-20250514",
  "request": {
    "prompt": "...",
    "max_tokens": 8192
  },
  "response": {
    "text": "...",
    "stop_reason": "end_turn"
  },
  "stats": {
    "input_tokens": 12345,
    "output_tokens": 2500,
    "total_tokens": 14845,
    "duration_ms": 15234.5,
    "cost_usd": 0.0745
  },
  "pricing": {
    "input_per_1m": 3.0,
    "output_per_1m": 15.0,
    "note": "Sonnet 4 pricing as of late 2024"
  }
}
```

### Key Fields
- **stop_reason**: `"end_turn"` = complete response, `"max_length"` = truncated (consider increasing `max_tokens`)
- **stats.cost_usd**: Actual cost for this API call
- **stats.total_tokens**: Combined input + output tokens

### Analyzing Costs
```bash
# Sum all costs from logs
cat reports/.chapter-reviewer-logs/*.json | jq -s 'map(.stats.cost_usd) | add'

# Find truncated responses
grep -l '"stop_reason": "max_length"' reports/.chapter-reviewer-logs/*.json
```

## Dependencies

- Python 3.9+
- `uv` - Fast Python package installer (auto-installs `rich` library)
- Claude Code CLI (`claude` command)

The script uses [uv](https://docs.astral.sh/uv/) with inline script metadata (PEP 723), so dependencies are automatically managed - no virtual environment needed!

## Ad Maiorem Dei Gloriam

*For the greater glory of God* ✟
