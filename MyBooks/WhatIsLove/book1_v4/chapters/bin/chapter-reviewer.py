#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "rich>=13.0.0",
#     "anthropic>=0.39.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""
Chapter Reviewer - Batch review chapters with Claude Code agents
Reviews all chapters with a specified agent and generates a beautiful report.
Supports both Claude CLI and Anthropic API (as fallback when CLI budget is exhausted).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.theme import Theme
from rich.prompt import Confirm, Prompt

# Catholic-themed colors
CATHOLIC_THEME = Theme({
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold blue",
    "header": "bold gold1",
    "chapter": "bold cyan",
    "agent": "bold magenta",
    "sacred": "bold purple",
})

console = Console(theme=CATHOLIC_THEME)

# Global state for API mode
_use_anthropic_api = False
_anthropic_client = None
_debug_mode = False

# Logging directory
LOG_DIR_NAME = ".chapter-reviewer-logs"

# Model mapping for Anthropic API
ANTHROPIC_MODEL_MAP = {
    "opus": "claude-opus-4-5",
    "sonnet": "claude-sonnet-4-5",
    "haiku": "claude-haiku-4-5",
}

# Priority mapping for recommendations
PRIORITY_MAP = {
    1: {"label": "HIGH", "class": "priority-high", "icon": "🔴", "color": "#DC2626"},
    2: {"label": "RECOMMENDED", "class": "priority-rec", "icon": "🟡", "color": "#D97706"},
    3: {"label": "OPTIONAL", "class": "priority-opt", "icon": "🔵", "color": "#2563EB"},
}


class ReviewFormatError(ValueError):
    pass


class LegacyRecommendationFormatError(ReviewFormatError):
    pass


def get_priority_info(priority: int) -> dict:
    """Get priority display information for a given priority level."""
    return PRIORITY_MAP.get(priority, PRIORITY_MAP[3])  # Default to OPT if unknown


def debug_print(title: str, content: str, is_request: bool = True) -> None:
    """Print a dimmed debug box with the given title and content."""
    if not _debug_mode:
        return

    icon = "📤" if is_request else "📥"
    border_color = "dim blue" if is_request else "dim green"

    console.print(Panel(
        f"[dim]{content}[/dim]",
        title=f"{icon} {title}",
        border_style=border_color,
        padding=(0, 1)
    ))


def log_api_call(
    log_dir: Path,
    chapter_name: str,
    agent_name: str,
    model_id: str,
    prompt: str,
    response_text: str,
    metadata: Dict[str, Any],
    stop_reason: str = None
) -> Path:
    """Log API request, response, and stats to a timestamped JSON file.

    Returns the path to the log file.
    """
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chapter_base = chapter_name.replace('.md', '')
    log_filename = f"{timestamp}_{agent_name}_{chapter_base}.json"
    log_path = log_dir / log_filename

    # Build log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "chapter": chapter_name,
        "agent": agent_name,
        "model": model_id,
        "request": {
            "prompt": prompt,
            "max_tokens": 8192,
        },
        "response": {
            "text": response_text,
            "stop_reason": stop_reason,
        },
        "stats": {
            "input_tokens": metadata.get("input_tokens", 0),
            "output_tokens": metadata.get("output_tokens", 0),
            "total_tokens": metadata.get("input_tokens", 0) + metadata.get("output_tokens", 0),
            "duration_ms": metadata.get("duration_ms", 0),
            "cost_usd": metadata.get("total_cost_usd", 0),
        },
        "pricing": {
            "input_per_1m": 3.0,
            "output_per_1m": 15.0,
            "note": "Sonnet 4 pricing as of late 2024"
        }
    }

    # Write log file
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    return log_path


def normalize_review_data(review_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate the review JSON payload.

    Enforces that recommendations are structured objects (no legacy strings).
    """
    recommendations = review_data.get("recommendations")
    if recommendations is None:
        review_data["recommendations"] = []
        return review_data

    if not isinstance(recommendations, list):
        raise ReviewFormatError(f"recommendations must be a list, got {type(recommendations).__name__}")

    normalized_recs: List[Dict[str, Any]] = []
    for idx, rec in enumerate(recommendations):
        if not isinstance(rec, dict):
            raise LegacyRecommendationFormatError(
                f"Legacy recommendation format detected at index {idx}: expected object, got {type(rec).__name__}"
            )

        priority = rec.get("priority", 3)
        try:
            priority_int = int(priority)
        except Exception:
            raise ReviewFormatError(f"recommendations[{idx}].priority must be an int (1-3), got {priority!r}")

        if priority_int not in (1, 2, 3):
            raise ReviewFormatError(f"recommendations[{idx}].priority must be 1, 2, or 3, got {priority_int}")

        issue = rec.get("issue", "")
        if not isinstance(issue, str) or not issue.strip():
            raise ReviewFormatError(f"recommendations[{idx}].issue must be a non-empty string")

        location = rec.get("location", "")
        if not isinstance(location, str) or not location.strip():
            location = "N/A"

        original = rec.get("original", "")
        if original is None:
            original = ""
        if not isinstance(original, str):
            original = str(original)

        suggested = rec.get("suggested", "")
        if suggested is None:
            suggested = ""
        if not isinstance(suggested, str):
            suggested = str(suggested)

        normalized: Dict[str, Any] = {
            "priority": priority_int,
            "location": location,
            "issue": issue.strip(),
            "original": original,
            "suggested": suggested,
        }

        if "words_saved" in rec:
            normalized["words_saved"] = rec.get("words_saved")

        normalized_recs.append(normalized)

    review_data["recommendations"] = normalized_recs
    return review_data


def sort_recommendations_by_priority(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort recommendations by priority (1=HIGH first, then 2=REC, then 3=OPT)."""
    for idx, rec in enumerate(recommendations):
        if not isinstance(rec, dict):
            raise LegacyRecommendationFormatError(
                f"Legacy recommendation format detected at index {idx}: expected object, got {type(rec).__name__}"
            )

    def get_priority(rec: Dict[str, Any]) -> int:
        return int(rec.get("priority", 3))

    return sorted(recommendations, key=get_priority)


def get_env_file_path() -> Path:
    """Get the path to .env.local file in the chapters directory."""
    return Path.cwd() / ".env.local"


def load_api_key_from_env() -> Optional[str]:
    """Load Anthropic API key from .env.local file."""
    env_file = get_env_file_path()
    if not env_file.exists():
        return None

    try:
        from dotenv import dotenv_values
        config = dotenv_values(env_file)
        return config.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def save_api_key_to_env(api_key: str) -> bool:
    """Save Anthropic API key to .env.local file."""
    env_file = get_env_file_path()

    try:
        # Read existing content if file exists
        existing_lines = []
        if env_file.exists():
            with open(env_file, "r") as f:
                existing_lines = f.readlines()

        # Check if ANTHROPIC_API_KEY already exists
        key_found = False
        for i, line in enumerate(existing_lines):
            if line.startswith("ANTHROPIC_API_KEY="):
                existing_lines[i] = f"ANTHROPIC_API_KEY={api_key}\n"
                key_found = True
                break

        if not key_found:
            existing_lines.append(f"ANTHROPIC_API_KEY={api_key}\n")

        # Write back
        with open(env_file, "w") as f:
            f.writelines(existing_lines)

        return True
    except Exception as e:
        console.print(f"[error]Failed to save API key: {e}[/error]")
        return False


def get_anthropic_client():
    """Get or create the Anthropic client."""
    global _anthropic_client

    if _anthropic_client is not None:
        return _anthropic_client

    api_key = load_api_key_from_env()

    if not api_key:
        # Check environment variable as well
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        return None

    try:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
        return _anthropic_client
    except Exception as e:
        console.print(f"[error]Failed to initialize Anthropic client: {e}[/error]")
        return None


def setup_anthropic_api() -> bool:
    """Setup Anthropic API by prompting for API key if needed."""
    global _anthropic_client

    # First try to get existing client
    client = get_anthropic_client()
    if client:
        return True

    # Prompt user for API key
    console.print()
    console.print("[warning]No Anthropic API key found.[/warning]")
    console.print("[info]You can get an API key from: https://console.anthropic.com/[/info]")
    console.print()

    api_key = Prompt.ask("[info]Please enter your Anthropic API key[/info]", password=True)

    if not api_key or not api_key.strip():
        console.print("[error]No API key provided.[/error]")
        return False

    api_key = api_key.strip()

    # Validate the key format (basic check)
    if not api_key.startswith("sk-"):
        console.print("[warning]Warning: API key doesn't start with 'sk-'. It may be invalid.[/warning]")

    # Try to initialize client with this key
    try:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=api_key)

        # Save to .env.local
        if save_api_key_to_env(api_key):
            console.print(f"[success]API key saved to {get_env_file_path()}[/success]")

        return True
    except Exception as e:
        console.print(f"[error]Failed to initialize Anthropic client: {e}[/error]")
        return False


def is_budget_exhausted_error(error_text: str) -> bool:
    """Check if the error indicates Claude CLI budget exhaustion."""
    budget_indicators = [
        "budget",
        "exhausted",
        "limit reached",
        "quota exceeded",
        "rate limit",
        "billing",
        "usage limit",
        "spend limit",
    ]
    error_lower = error_text.lower()
    return any(indicator in error_lower for indicator in budget_indicators)


def run_anthropic_review(chapter_file: Path, workflow_file: Path, model: str = "opus", agent_name: str = "unknown", log_dir: Path = None) -> Dict[str, Any]:
    """Run Anthropic API review on a single chapter and return parsed results."""
    import time

    client = get_anthropic_client()
    if not client:
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "ERROR",
            "error": "Anthropic client not initialized",
            "successful_checks": [],
            "failed_checks": [{"check": "API Setup", "issue": "Anthropic client not available", "location": "N/A"}],
            "summary": "Failed to initialize Anthropic API client",
            "recommendations": []
        }

    # Read the chapter and workflow files
    try:
        chapter_content = chapter_file.read_text(encoding="utf-8")
        workflow_content = workflow_file.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "ERROR",
            "error": f"Failed to read files: {e}",
            "successful_checks": [],
            "failed_checks": [{"check": "File Reading", "issue": str(e), "location": "N/A"}],
            "summary": "Failed to read chapter or workflow file",
            "recommendations": []
        }

    prompt = f"""Please review this chapter according to the workflow instructions:

=== CHAPTER CONTENT ({chapter_file.name}) ===
{chapter_content}
=== END CHAPTER ===

=== REVIEW INSTRUCTIONS ===
{workflow_content}
=== END INSTRUCTIONS ===

CRITICAL: Return ONLY valid, parseable JSON. No markdown code fences. No explanatory text before or after.

RECOMMENDATION FORMAT IS STRICT:
- recommendations MUST be an array of objects, not strings
- each recommendation MUST include: priority (1-3), location, issue
- optional fields: original, suggested, words_saved
- location MUST include line number(s) when possible (e.g., "Line 42" or "Lines 42-45")
- Only use section heading + excerpt for location if line numbers cannot be determined

STRICT JSON REQUIREMENTS:
- Use ASCII quotes only (straight quotes ", not curly quotes "" or '')
- Escape quotes inside strings with backslash: \\"
- Escape newlines inside strings with: \\n
- No trailing commas after the last item in arrays or objects
- No comments
- overall_status MUST be exactly "PASS" or "FAIL" - no other values allowed
- All output must be valid JSON that passes JSON.parse()

{{
    "chapter_name": "{chapter_file.name}",
    "overall_status": "PASS or FAIL only",
    "successful_checks": [
        {{"check": "Check name", "details": "Why it passed"}}
    ],
    "failed_checks": [
        {{"check": "Check name", "issue": "Description of the problem", "location": "Line/section reference if applicable"}}
    ],
    "summary": "Brief summary of the review",
    "recommendations": [
        {{
            "priority": 1,
            "location": "Line 42 (or Lines 42-45)",
            "issue": "What to change",
            "original": "(optional excerpt)",
            "suggested": "(optional replacement)",
            "words_saved": 0
        }}
    ]
}}

Perform the review thoroughly. Return ONLY the raw JSON object, nothing else."""

    # Map model name to Anthropic model ID
    model_id = ANTHROPIC_MODEL_MAP.get(model, ANTHROPIC_MODEL_MAP["sonnet"])

    # Debug: show request
    debug_print(
        f"API Request → {model_id}",
        f"Model: {model_id}\nMax Tokens: 8192\n\n--- PROMPT ---\n{prompt}",
        is_request=True
    )

    start_time = time.time()

    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        duration_ms = (time.time() - start_time) * 1000

        # Extract metadata
        metadata = {
            "total_cost_usd": 0,  # Would need pricing calculation
            "duration_ms": duration_ms,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        # Calculate approximate cost (pricing as of late 2024)
        # Sonnet 4: $3/1M input, $15/1M output
        input_cost = (response.usage.input_tokens / 1_000_000) * 3.0
        output_cost = (response.usage.output_tokens / 1_000_000) * 15.0
        metadata["total_cost_usd"] = input_cost + output_cost

        # Get the response text and stop reason
        result_text = response.content[0].text if response.content else ""
        stop_reason = response.stop_reason if hasattr(response, 'stop_reason') else None

        # Log the API call if log_dir is provided
        if log_dir:
            log_api_call(
                log_dir=log_dir,
                chapter_name=chapter_file.name,
                agent_name=agent_name,
                model_id=model_id,
                prompt=prompt,
                response_text=result_text,
                metadata=metadata,
                stop_reason=stop_reason
            )

        # Debug: show response
        debug_print(
            f"API Response ← {model_id}",
            f"Input Tokens: {response.usage.input_tokens}\nOutput Tokens: {response.usage.output_tokens}\nCost: ${metadata['total_cost_usd']:.4f}\n\n--- RESPONSE ---\n{result_text}",
            is_request=False
        )

        # Try to parse as JSON
        try:
            # Strip markdown code fences if present using regex for robustness
            clean_text = result_text.strip()
            # Remove ```json or ``` at start and ``` at end
            clean_text = re.sub(r'^```(?:json)?\s*\n?', '', clean_text)
            clean_text = re.sub(r'\n?```\s*$', '', clean_text)

            json_start = clean_text.find("{")
            json_end = clean_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = clean_text[json_start:json_end]

                # Try parsing directly first
                try:
                    review_data = json.loads(json_str)
                    review_data["_metadata"] = metadata
                    return normalize_review_data(review_data)
                except json.JSONDecodeError as first_error:
                    # Try to repair common JSON issues
                    repaired = json_str
                    # Fix trailing commas before ] or }
                    repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
                    # Fix smart quotes
                    repaired = repaired.replace('"', '"').replace('"', '"')
                    repaired = repaired.replace(''', "'").replace(''', "'")
                    # Fix unescaped control characters in strings
                    repaired = repaired.replace('\t', '\\t')
                    # Fix em-dashes and other special chars that might break things
                    repaired = repaired.replace('—', '-').replace('–', '-')
                    # Try again after basic repairs
                    try:
                        review_data = json.loads(repaired)
                        review_data["_metadata"] = metadata
                        return review_data
                    except json.JSONDecodeError:
                        # Try json_repair library if available
                        try:
                            from json_repair import repair_json
                            repaired = repair_json(json_str)
                            review_data = json.loads(repaired)
                            review_data["_metadata"] = metadata
                            return review_data
                        except ImportError:
                            pass
                        except Exception:
                            pass
                        # Last resort: re-raise original error
                        raise first_error
        except json.JSONDecodeError as e:
            # JSON parsing failed - return with error details
            return {
                "chapter_name": chapter_file.name,
                "overall_status": "ERROR",
                "error": f"JSON parsing failed: {str(e)}",
                "successful_checks": [],
                "failed_checks": [{"check": "JSON Parsing", "issue": f"LLM returned invalid JSON: {str(e)}", "location": "API Response"}],
                "summary": f"The LLM returned malformed JSON that could not be parsed. Error: {str(e)}",
                "recommendations": [],
                "raw_output": result_text,
                "_metadata": metadata
            }

        # Return raw text if JSON parsing failed
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "UNKNOWN",
            "successful_checks": [],
            "failed_checks": [],
            "summary": result_text,
            "recommendations": [],
            "raw_output": result_text,
            "_metadata": metadata
        }

    except Exception as e:
        if isinstance(e, LegacyRecommendationFormatError):
            raise
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "ERROR",
            "error": str(e),
            "successful_checks": [],
            "failed_checks": [{"check": "API Call", "issue": str(e), "location": "N/A"}],
            "summary": f"Anthropic API error: {str(e)}",
            "recommendations": [],
            "_metadata": {"total_cost_usd": 0, "duration_ms": 0, "input_tokens": 0, "output_tokens": 0}
        }


def find_chapters(chapters_dir: Path) -> List[Path]:
    """Find all chapter markdown files."""
    chapters = sorted(chapters_dir.glob("chapter_*.md"))
    if not chapters:
        console.print("[error]No chapter files found matching pattern 'chapter_*.md'[/error]")
        sys.exit(1)
    return chapters


def find_agent_workflow(agent_name: str, base_dir: Path) -> Path:
    """Find the agent workflow file based on the agent name pattern."""
    # Look for workflow files matching the pattern
    workflows_dir = base_dir / ".agents" / "workflows"

    # Try different patterns
    patterns = [
        f"{agent_name}-*.md",
        f"*-{agent_name.lower()}.md",
        f"*{agent_name.lower()}*.md",
    ]

    for pattern in patterns:
        matches = list(workflows_dir.glob(pattern))
        if matches:
            return matches[0]

    console.print(f"[error]No workflow file found for agent '{agent_name}' in {workflows_dir}[/error]")
    console.print("[info]Available workflows:[/info]")
    for wf in workflows_dir.glob("*.md"):
        console.print(f"  • {wf.name}")
    sys.exit(1)


def get_next_review_filename(agent_name: str, output_dir: Path, chapter_name: str = None) -> Path:
    """Get the next available review filename (never overwrite).

    If chapter_name is provided, includes it in the filename for per-chapter reports.
    """
    counter = 1
    while True:
        if chapter_name:
            # Per-chapter report: AGENT-chapter_name-review1.html
            base_name = chapter_name.replace('.md', '')
            filename = output_dir / f"{agent_name}-{base_name}-review{counter}.html"
        else:
            # Combined report: AGENT-review1.html
            filename = output_dir / f"{agent_name}-review{counter}.html"
        if not filename.exists():
            return filename
        counter += 1


def run_claude_review(chapter_file: Path, workflow_file: Path, model: str = "opus") -> Dict[str, Any]:
    """Run Claude Code review on a single chapter and return parsed results."""
    prompt = f"""Please review this chapter according to the workflow instructions:

Chapter to review: @{chapter_file}
Review instructions: @{workflow_file}

IMPORTANT: Return your response in the following JSON format:
{{
    "chapter_name": "{chapter_file.name}",
    "overall_status": "PASS",
    "successful_checks": [
        {{"check": "Check name", "details": "Why it passed"}}
    ],
    "failed_checks": [
        {{"check": "Check name", "issue": "Description of the problem", "location": "Line/section references"}}
    ],
    "summary": "Brief summary of the review",
    "recommendations": [
        {{
            "priority": 1,
            "location": "Line/section reference",
            "issue": "What to change",
            "original": "(optional excerpt)",
            "suggested": "(optional replacement)",
            "words_saved": 0
        }}
    ]
}}

CRITICAL:
- overall_status MUST be exactly "PASS" or "FAIL" (no other values)
- Return ONLY the JSON object with no additional text or markdown
- recommendations MUST be an array of objects (no strings)
"""

    try:
        result = subprocess.run(
            [
                "claude", "-p", prompt,
                "--output-format", "json",
                "--model", model,
                "--max-turns", "10"
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            # Combine stderr and stdout for comprehensive error info
            error_text = result.stderr.strip() if result.stderr else ""
            stdout_text = result.stdout.strip() if result.stdout else ""

            # Build detailed error message
            error_parts = []
            error_parts.append(f"Exit code: {result.returncode}")
            if error_text:
                error_parts.append(f"stderr: {error_text}")
            if stdout_text:
                error_parts.append(f"stdout: {stdout_text[:500]}")  # Limit stdout preview

            full_error = " | ".join(error_parts)
            combined_text = f"{error_text} {stdout_text}"

            # Check for budget exhaustion in both stderr and stdout
            if is_budget_exhausted_error(combined_text):
                return {
                    "chapter_name": chapter_file.name,
                    "overall_status": "BUDGET_EXHAUSTED",
                    "error": full_error,
                    "successful_checks": [],
                    "failed_checks": [{"check": "Claude CLI Budget", "issue": full_error, "location": "N/A"}],
                    "summary": "Claude CLI budget exhausted",
                    "recommendations": [{
                        "priority": 2,
                        "location": "N/A",
                        "issue": "Consider using Anthropic API directly",
                        "original": "",
                        "suggested": ""
                    }]
                }
            return {
                "chapter_name": chapter_file.name,
                "overall_status": "ERROR",
                "error": full_error,
                "successful_checks": [],
                "failed_checks": [{"check": "Claude Execution", "issue": full_error or "Unknown error (no output)", "location": "N/A"}],
                "summary": f"Failed to execute Claude review (exit code {result.returncode})",
                "recommendations": []
            }

        # Parse the JSON output from Claude
        output = json.loads(result.stdout)

        # Extract metadata (tokens, cost, duration)
        metadata = {
            "total_cost_usd": output.get("total_cost_usd", 0),
            "duration_ms": output.get("duration_ms", 0),
            "input_tokens": output.get("input_tokens", 0),
            "output_tokens": output.get("output_tokens", 0),
        }

        # Extract the actual result content
        if "result" in output:
            result_text = output["result"]

            # Try to parse the result as JSON
            try:
                # Strip markdown code fences if present using regex for robustness
                clean_text = result_text.strip()
                clean_text = re.sub(r'^```(?:json)?\s*\n?', '', clean_text)
                clean_text = re.sub(r'\n?```\s*$', '', clean_text)

                # Find JSON object in the result
                json_start = clean_text.find("{")
                json_end = clean_text.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_str = clean_text[json_start:json_end]

                    # Try parsing directly first
                    try:
                        review_data = json.loads(json_str)
                        review_data["_metadata"] = metadata
                        return normalize_review_data(review_data)
                    except json.JSONDecodeError as first_error:
                        # Try to repair common JSON issues
                        repaired = json_str
                        # Fix trailing commas before ] or }
                        repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
                        # Fix smart quotes
                        repaired = repaired.replace('"', '"').replace('"', '"')
                        repaired = repaired.replace(''', "'").replace(''', "'")
                        # Fix unescaped control characters in strings
                        repaired = repaired.replace('\t', '\\t')
                        # Fix em-dashes and other special chars
                        repaired = repaired.replace('—', '-').replace('–', '-')
                        # Try again after basic repairs
                        try:
                            review_data = json.loads(repaired)
                            review_data["_metadata"] = metadata
                            return normalize_review_data(review_data)
                        except json.JSONDecodeError:
                            # Try json_repair library if available
                            try:
                                from json_repair import repair_json
                                repaired = repair_json(json_str)
                                review_data = json.loads(repaired)
                                review_data["_metadata"] = metadata
                                return normalize_review_data(review_data)
                            except ImportError:
                                pass
                            except Exception:
                                pass
                            # Last resort: re-raise original error
                            raise first_error
            except json.JSONDecodeError as e:
                # Return error details instead of silently falling through
                return {
                    "chapter_name": chapter_file.name,
                    "overall_status": "ERROR",
                    "error": f"JSON parsing failed: {str(e)}",
                    "successful_checks": [],
                    "failed_checks": [{"check": "JSON Parsing", "issue": f"LLM returned invalid JSON: {str(e)}", "location": "API Response"}],
                    "summary": f"The LLM returned malformed JSON that could not be parsed. Error: {str(e)}",
                    "recommendations": [],
                    "raw_output": result_text,
                    "_metadata": metadata
                }

            # If parsing failed, return the raw text
            return {
                "chapter_name": chapter_file.name,
                "overall_status": "UNKNOWN",
                "successful_checks": [],
                "failed_checks": [],
                "summary": result_text,
                "recommendations": [],
                "raw_output": result_text,
                "_metadata": metadata
            }

        # No "result" field in output - check for specific error cases
        subtype = output.get("subtype", "")

        if subtype == "error_max_turns":
            # Claude hit the max turns limit before completing
            return {
                "chapter_name": chapter_file.name,
                "overall_status": "ERROR",
                "error": f"Claude exceeded maximum turns ({output.get('num_turns', 10)} turns used)",
                "successful_checks": [],
                "failed_checks": [{
                    "check": "Max Turns Exceeded",
                    "issue": f"The review agent used all {output.get('num_turns', 10)} turns without completing. The workflow may be too complex or the chapter may be very long.",
                    "location": "N/A"
                }],
                "summary": "Review incomplete - exceeded maximum turns",
                "recommendations": [
                    {
                        "priority": 2,
                        "location": "N/A",
                        "issue": "Try increasing --max-turns (e.g., --max-turns 20)",
                        "original": "",
                        "suggested": ""
                    },
                    {
                        "priority": 2,
                        "location": "N/A",
                        "issue": "Or simplify the review workflow",
                        "original": "",
                        "suggested": ""
                    },
                    {
                        "priority": 2,
                        "location": "N/A",
                        "issue": "Or break the chapter into smaller sections",
                        "original": "",
                        "suggested": ""
                    }
                ],
                "raw_output": json.dumps(output, indent=2),
                "_metadata": metadata
            }

        # Other unexpected output format
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "ERROR",
            "error": "Unexpected output format - missing 'result' field in Claude's response",
            "successful_checks": [],
            "failed_checks": [],
            "summary": "Could not parse Claude output",
            "recommendations": [],
            "raw_output": json.dumps(output, indent=2),  # Show the full JSON response
            "_metadata": metadata
        }

    except subprocess.TimeoutExpired:
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "TIMEOUT",
            "error": "Review timed out after 5 minutes",
            "successful_checks": [],
            "failed_checks": [{"check": "Execution", "issue": "Timeout", "location": "N/A"}],
            "summary": "Review timed out",
            "recommendations": []
        }
    except json.JSONDecodeError as e:
        # Claude returned non-JSON output
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "ERROR",
            "error": f"Failed to parse JSON response: {str(e)}",
            "successful_checks": [],
            "failed_checks": [{"check": "JSON Parsing", "issue": str(e), "location": f"Line {e.lineno}, Column {e.colno}"}],
            "summary": "Claude returned invalid JSON",
            "recommendations": [],
            "raw_output": result.stdout if 'result' in locals() else "No output captured"
        }
    except Exception as e:
        if isinstance(e, LegacyRecommendationFormatError):
            raise
        return {
            "chapter_name": chapter_file.name,
            "overall_status": "ERROR",
            "error": str(e),
            "successful_checks": [],
            "failed_checks": [{"check": "Execution", "issue": str(e), "location": "N/A"}],
            "summary": f"Error: {str(e)}",
            "recommendations": []
        }


def display_results(results: List[Dict[str, Any]], agent_name: str):
    """Display beautiful results using rich."""
    # Header
    console.print()
    console.print(Panel.fit(
        f"[header]✟ Chapter Review Results ✟[/header]\n"
        f"[agent]Agent: {agent_name}[/agent]\n"
        f"[info]Chapters Reviewed: {len(results)}[/info]",
        border_style="gold1"
    ))
    console.print()

    # Summary statistics - normalize status based on failed_checks if LLM returns non-standard status
    def normalize_status(r):
        status = r.get("overall_status", "UNKNOWN")
        if status in ["PASS", "FAIL", "ERROR", "TIMEOUT", "UNKNOWN"]:
            return status
        # LLM returned non-standard status (e.g., "REC") - determine from failed_checks
        if len(r.get("failed_checks", [])) > 0:
            return "FAIL"
        return "PASS"

    passed = sum(1 for r in results if normalize_status(r) == "PASS")
    failed = sum(1 for r in results if normalize_status(r) == "FAIL")
    errors = sum(1 for r in results if normalize_status(r) in ["ERROR", "TIMEOUT", "UNKNOWN"])

    summary_table = Table(title="📊 Summary", border_style="cyan")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Count", justify="right", style="bold")
    summary_table.add_column("Percentage", justify="right")

    total = len(results)
    summary_table.add_row("✓ Passed", str(passed), f"{passed/total*100:.1f}%", style="success")
    summary_table.add_row("✗ Failed", str(failed), f"{failed/total*100:.1f}%", style="error")
    if errors > 0:
        summary_table.add_row("⚠ Errors", str(errors), f"{errors/total*100:.1f}%", style="warning")

    console.print(summary_table)
    console.print()

    # Failed checks details
    if failed > 0 or errors > 0:
        console.print(Panel("[error]✗ Chapters Requiring Attention[/error]", border_style="red"))

        for result in results:
            # Use normalized status to catch non-standard LLM responses like "REC"
            normalized = normalize_status(result)
            if normalized in ["FAIL", "ERROR", "TIMEOUT", "UNKNOWN"]:
                chapter_name = result.get("chapter_name", "Unknown")
                original_status = result.get("overall_status", "UNKNOWN")

                console.print(f"\n[chapter]📖 {chapter_name}[/chapter]")
                console.print(f"[error]Status: {original_status}[/error]")

                if result.get("summary"):
                    console.print(f"[info]Summary:[/info] {result['summary']}")

                # Show detailed error information for ERROR/TIMEOUT/UNKNOWN statuses
                status = result.get("overall_status")
                if status in ["ERROR", "TIMEOUT", "UNKNOWN"]:
                    error_details = []

                    # Show error message if present
                    if result.get("error"):
                        error_details.append(f"[error]Error:[/error] {result['error']}")

                    # Show raw output preview if present (first 500 chars)
                    if result.get("raw_output"):
                        raw_output = result["raw_output"]
                        preview_length = 99999
                        if len(raw_output) > preview_length:
                            preview = raw_output[:preview_length] + "..."
                        else:
                            preview = raw_output
                        error_details.append(f"\n[warning]Claude's Response (preview):[/warning]\n{preview}")
                        if len(raw_output) > preview_length:
                            error_details.append(f"\n[dim](Full output: {len(raw_output)} characters)[/dim]")

                    if error_details:
                        console.print(Panel(
                            "\n".join(error_details),
                            title="[bold red]Error Details[/bold red]",
                            border_style="red",
                            padding=(1, 2)
                        ))

                # Failed checks - details are in HTML report, skip console table

                # Recommendations (with priority support)
                recommendations = result.get("recommendations", [])
                if recommendations:
                    console.print("[sacred]Edit Recommendations:[/sacred]")
                    sorted_recs = sort_recommendations_by_priority(recommendations)
                    for rec in sorted_recs:
                        if isinstance(rec, dict):
                            # New priority-based format
                            priority = rec.get("priority", 3)
                            priority_info = get_priority_info(priority)
                            location = rec.get("location", "")
                            issue = rec.get("issue", "")
                            original = rec.get("original", "")
                            suggested = rec.get("suggested", "")

                            # Build location display - show prominently
                            console.print(f"  {priority_info['icon']} [bold]{priority_info['label']}[/bold] {location}: {issue}")
                            if original:
                                # Truncate but show more context
                                orig_display = original[:100] + "..." if len(original) > 100 else original
                                console.print(f"      [dim]Original:[/dim] {orig_display}")
                            if suggested:
                                sugg_display = suggested[:100] + "..." if len(suggested) > 100 else suggested
                                console.print(f"      [dim]Suggested:[/dim] {sugg_display}")
                        else:
                            raise LegacyRecommendationFormatError(
                                f"Legacy recommendation format detected in display_results: {type(rec).__name__}"
                            )

                console.print("─" * 80)

    # Successful chapters
    if passed > 0:
        console.print()
        console.print(Panel("[success]✓ Chapters That Passed[/success]", border_style="green"))

        for result in results:
            if result.get("overall_status") == "PASS":
                chapter_name = result.get("chapter_name", "Unknown")
                successful_checks = result.get("successful_checks", [])

                console.print(f"[success]✓[/success] [chapter]{chapter_name}[/chapter] - {len(successful_checks)} checks passed")

                # Also show recommendations for passing chapters (optional improvements)
                recommendations = result.get("recommendations", [])
                if recommendations:
                    console.print("[sacred]  Edit Recommendations:[/sacred]")
                    sorted_recs = sort_recommendations_by_priority(recommendations)
                    for rec in sorted_recs:
                        if isinstance(rec, dict):
                            # New priority-based format
                            priority = rec.get("priority", 3)
                            priority_info = get_priority_info(priority)
                            location = rec.get("location", "")
                            issue = rec.get("issue", "")
                            original = rec.get("original", "")
                            suggested = rec.get("suggested", "")

                            # Build location display - show prominently
                            console.print(f"    {priority_info['icon']} [bold]{priority_info['label']}[/bold] {location}: {issue}")
                            if original:
                                # Truncate but show more context
                                orig_display = original[:100] + "..." if len(original) > 100 else original
                                console.print(f"        [dim]Original:[/dim] {orig_display}")
                            if suggested:
                                sugg_display = suggested[:100] + "..." if len(suggested) > 100 else suggested
                                console.print(f"        [dim]Suggested:[/dim] {sugg_display}")
                        else:
                            raise LegacyRecommendationFormatError(
                                f"Legacy recommendation format detected in display_results: {type(rec).__name__}"
                            )
                    console.print()


def save_concise_html_report(results: List[Dict[str, Any]], agent_name: str, output_file: Path):
    """Save a concise HTML report with only recommendations - optimized for LLM processing.

    Shows the same detailed recommendation info as the full report (location, original, suggested)
    but omits summary stats, detailed check tables, and other verbose sections.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>""" + agent_name + """ Review - Recommendations</title>
    <style>
        body { font-family: Georgia, serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.5; }
        h1 { color: #663399; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
        h2 { color: #663399; margin-top: 25px; margin-bottom: 10px; }
        h3 { color: #333; margin-top: 20px; }
        .chapter { background: #f9f9f9; border-left: 4px solid #663399; padding: 15px; margin: 20px 0; }
        .summary { margin-bottom: 5px; color: #555; font-style: italic; }
        .failed-checks { margin: 15px 0; }
        .failed-checks table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
        .failed-checks th { background: #8B0000; color: white; padding: 8px; text-align: left; }
        .failed-checks td { padding: 8px; border-bottom: 1px solid #ddd; }
        .recommendations { background: #fffef0; border-left: 4px solid #D4AF37; padding: 15px; margin: 15px 0; }
        .priority-high { border-left: 4px solid #DC2626; padding-left: 12px; margin: 10px 0; background: #fef2f2; }
        .priority-rec { border-left: 4px solid #D97706; padding-left: 12px; margin: 10px 0; background: #fffbeb; }
        .priority-opt { border-left: 4px solid #2563EB; padding-left: 12px; margin: 10px 0; background: #eff6ff; }
        .priority-label { font-weight: bold; margin-right: 8px; }
        .priority-high .priority-label { color: #DC2626; }
        .priority-rec .priority-label { color: #D97706; }
        .priority-opt .priority-label { color: #2563EB; }
        .location { font-family: monospace; color: #666; font-size: 0.9em; }
        .issue { margin: 5px 0; }
        .original, .suggested { font-size: 0.9em; color: #555; margin: 5px 0; padding: 8px; background: #fff; border: 1px solid #eee; }
        .original strong, .suggested strong { color: #333; }
        .footer { text-align: center; margin-top: 40px; color: #888; font-style: italic; }
        .passed { color: #2D5016; font-weight: bold; }
    </style>
</head>
<body>
    <h1>✟ """ + agent_name + """ Review - Recommendations</h1>
    <p><em>Generated: """ + timestamp + """</em></p>
""")

        # Count totals for summary
        total_recs = sum(len(r.get("recommendations", [])) for r in results)
        total_failed = sum(len(r.get("failed_checks", [])) for r in results)

        f.write(f"""    <p><strong>Summary:</strong> {total_recs} recommendations, {total_failed} failed checks across {len(results)} chapter(s)</p>\n""")

        # Output each chapter
        for result in results:
            chapter_name = result.get("chapter_name", "Unknown")
            status = result.get("overall_status", "UNKNOWN")
            summary = result.get("summary", "")
            failed_checks = result.get("failed_checks", [])
            recommendations = result.get("recommendations", [])

            # Skip chapters with nothing to report
            if not recommendations and not failed_checks and status == "PASS":
                f.write(f"""    <p class="passed">✓ {chapter_name} - No changes needed</p>\n""")
                continue

            f.write(f"""
    <div class="chapter">
        <h2>{chapter_name}</h2>
""")

            # Summary if present
            if summary:
                summary_html = summary.replace("<", "&lt;").replace(">", "&gt;")
                f.write(f"""        <p class="summary">{summary_html}</p>\n""")

            # Failed checks table (concise version)
            if failed_checks:
                f.write("""        <div class="failed-checks">
            <h3>Failed Checks</h3>
            <table>
                <tr><th>Check</th><th>Issue</th><th>Location</th></tr>
""")
                for check in failed_checks:
                    check_name = check.get("check", "Unknown").replace("<", "&lt;").replace(">", "&gt;")
                    issue = check.get("issue", "No details").replace("<", "&lt;").replace(">", "&gt;")
                    location = check.get("location", "N/A").replace("<", "&lt;").replace(">", "&gt;")
                    f.write(f"""                <tr><td>{check_name}</td><td>{issue}</td><td>{location}</td></tr>\n""")
                f.write("""            </table>
        </div>
""")

            # Recommendations (full detail)
            if recommendations:
                sorted_recs = sort_recommendations_by_priority(recommendations)
                f.write("""        <div class="recommendations">
            <h3>📿 Recommendations</h3>
""")
                for rec in sorted_recs:
                    if isinstance(rec, dict):
                        priority = rec.get("priority", 3)
                        priority_info = get_priority_info(priority)
                        location = rec.get("location", "").replace("<", "&lt;").replace(">", "&gt;")
                        issue = rec.get("issue", "").replace("<", "&lt;").replace(">", "&gt;")
                        original = rec.get("original", "").replace("<", "&lt;").replace(">", "&gt;")
                        suggested = rec.get("suggested", "").replace("<", "&lt;").replace(">", "&gt;")

                        f.write(f"""            <div class="recommendation-item {priority_info['class']}">
                <span class="priority-label">{priority_info['icon']} {priority_info['label']}</span>
                <span class="location">{location}</span>
                <div class="issue">{issue}</div>
""")
                        if original:
                            f.write(f"""                <div class="original"><strong>Original:</strong> {original}</div>\n""")
                        if suggested:
                            f.write(f"""                <div class="suggested"><strong>Suggested:</strong> {suggested}</div>\n""")
                        f.write("""            </div>\n""")
                    else:
                        raise LegacyRecommendationFormatError(
                            f"Legacy recommendation format detected in save_concise_html_report: {type(rec).__name__}"
                        )
                f.write("""        </div>\n""")

            f.write("""    </div>\n""")

        f.write("""
    <div class="footer">
        <p>✟ Ad Maiorem Dei Gloriam ✟</p>
    </div>
</body>
</html>
""")


def save_html_report(results: List[Dict[str, Any]], agent_name: str, output_file: Path, concise: bool = False):
    """Save validation report as HTML suitable for Bishop's office submission.

    If concise=True, generates a minimal report with only recommendations,
    suitable for passing to an LLM for modifications.
    """
    if concise:
        save_concise_html_report(results, agent_name, output_file)
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_formatted = datetime.now().strftime("%B %d, %Y")

    # Calculate statistics - normalize status based on failed_checks if LLM returns non-standard status
    def normalize_status(r):
        status = r.get("overall_status", "UNKNOWN")
        if status in ["PASS", "FAIL", "ERROR", "TIMEOUT", "UNKNOWN"]:
            return status
        # LLM returned non-standard status (e.g., "REC") - determine from failed_checks
        if len(r.get("failed_checks", [])) > 0:
            return "FAIL"
        return "PASS"

    passed = sum(1 for r in results if normalize_status(r) == "PASS")
    failed = sum(1 for r in results if normalize_status(r) == "FAIL")
    errors = sum(1 for r in results if normalize_status(r) in ["ERROR", "TIMEOUT", "UNKNOWN"])
    total = len(results)

    # Count total checks
    total_checks_passed = sum(len(r.get("successful_checks", [])) for r in results)
    total_checks_failed = sum(len(r.get("failed_checks", [])) for r in results)
    total_checks = total_checks_passed + total_checks_failed

    with open(output_file, "w", encoding="utf-8") as f:
        # HTML header with Catholic-themed professional styling
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Official Validation Report - """ + agent_name + """</title>
    <style>
        :root {
            --gold: #D4AF37;
            --purple: #663399;
            --red: #8B0000;
            --dark: #2C2C2C;
            --light-bg: #FAFAFA;
            --success: #2D5016;
            --error: #8B0000;
            --warning: #B8860B;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: var(--dark);
            background: white;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
        }

        .header {
            text-align: center;
            # border-bottom: 3px solid var(--gold);
            padding-bottom: 30px;
            margin-bottom: 40px;
        }

        .cross {
            font-size: 48px;
            color: var(--gold);
            margin-bottom: 10px;
        }

        h1 {
            font-size: 32px;
            color: var(--purple);
            margin-bottom: 10px;
        }

        h2 {
            font-size: 24px;
            color: var(--purple);
            margin-top: 30px;
            margin-bottom: 15px;
            # border-bottom: 2px solid var(--gold);
            padding-bottom: 5px;
        }

        h3 {
            font-size: 20px;
            color: var(--dark);
            margin-top: 25px;
            margin-bottom: 10px;
        }

        h4 {
            font-size: 16px;
            color: var(--purple);
            margin-top: 15px;
            margin-bottom: 10px;
        }

        .metadata {
            background: var(--light-bg);
            border-left: 4px solid var(--gold);
            padding: 20px;
            margin: 20px 0;
        }

        .metadata p {
            margin: 5px 0;
        }

        .summary-box {
            background: linear-gradient(to right, #f8f8f8, white);
            border: 2px solid var(--gold);
            padding: 25px;
            margin: 20px 0;
            border-radius: 5px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: white;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid var(--gold);
        }

        .stat-card.success {
            border-left-color: var(--success);
        }

        .stat-card.error {
            border-left-color: var(--error);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
        }

        th {
            background: var(--purple);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }

        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }

        tr:nth-child(even) {
            background: var(--light-bg);
        }

        tr:hover {
            background: #f0f0f0;
        }

        .chapter-section {
            background: white;
            border: 1px solid #ddd;
            margin: 20px 0;
            padding: 20px;
            border-radius: 5px;
            page-break-inside: avoid;
        }

        .chapter-section.passed {
            border-left: 5px solid var(--success);
        }

        .chapter-section.failed {
            border-left: 5px solid var(--error);
        }

        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 14px;
        }

        .status-badge.passed {
            background: var(--success);
            color: white;
        }

        .status-badge.failed {
            background: var(--error);
            color: white;
        }

        .status-badge.error {
            background: var(--warning);
            color: white;
        }

        .check-icon {
            font-weight: bold;
            margin-right: 5px;
        }

        .check-icon.success {
            color: var(--success);
        }

        .check-icon.error {
            color: var(--error);
        }

        ul {
            margin: 10px 0 10px 30px;
        }

        li {
            margin: 5px 0;
        }

        .recommendations {
            background: #fffef0;
            border-left: 4px solid var(--gold);
            padding: 15px;
            margin: 15px 0;
        }

        /* Priority-based styling */
        .priority-high {
            border-left: 4px solid #DC2626;
            padding-left: 12px;
            margin: 8px 0;
        }

        .priority-high .priority-label {
            color: #DC2626;
            font-weight: bold;
        }

        .priority-rec {
            border-left: 4px solid #D97706;
            padding-left: 12px;
            margin: 8px 0;
        }

        .priority-rec .priority-label {
            color: #D97706;
        }

        .priority-opt {
            border-left: 4px solid #2563EB;
            padding-left: 12px;
            margin: 8px 0;
        }

        .priority-opt .priority-label {
            color: #2563EB;
        }

        .recommendation-item {
            background: white;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
        }

        .recommendation-item .location {
            font-family: monospace;
            color: #666;
            font-size: 0.9em;
        }

        .recommendation-item .issue {
            font-weight: bold;
            margin: 5px 0;
        }

        .recommendation-item .original {
            background: #fee2e2;
            padding: 8px;
            border-radius: 3px;
            margin: 5px 0;
            font-family: monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
        }

        .recommendation-item .suggested {
            background: #dcfce7;
            padding: 8px;
            border-radius: 3px;
            margin: 5px 0;
            font-family: monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
        }

        .conclusion {
            background: var(--light-bg);
            border: 2px solid var(--purple);
            padding: 25px;
            margin: 30px 0;
            border-radius: 5px;
            page-break-before: always;
        }

        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid var(--gold);
            font-style: italic;
            color: #666;
        }

        hr {
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }

        @media print {
            body {
                padding: 20px;
            }
            .chapter-section {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="cross">✟</div>
        <h1>Official Validation Report</h1>
        <h2 style="border: none;">""" + agent_name + """ Review</h2>
    </div>

    <div class="metadata">
        <p><strong>Date:</strong> """ + date_formatted + """</p>
        <p><strong>Generated:</strong> """ + timestamp + """</p>
        <p><strong>Review Type:</strong> """ + agent_name + """</p>
        <p><strong>Total Chapters:</strong> """ + str(total) + """</p>
    </div>

    <h2>Report Summary</h2>
    <div class="summary-box">
        <p>This report documents the """ + agent_name + """ review of all """ + str(total) + """ chapters.
        A total of """ + str(total_checks) + """ validation checks were performed across all chapters.</p>
    </div>

    <h3>Overall Results</h3>
    <div class="stats">
        <div class="stat-card success">
            <h4>Chapters Passed</h4>
            <p style="font-size: 24px; font-weight: bold; color: var(--success);">""" + str(passed) + """ / """ + str(total) + """</p>
            <p>""" + f"{passed/total*100:.1f}" + """% Success Rate</p>
        </div>
        <div class="stat-card error">
            <h4>Chapters Failed</h4>
            <p style="font-size: 24px; font-weight: bold; color: var(--error);">""" + str(failed) + """ / """ + str(total) + """</p>
            <p>""" + f"{failed/total*100:.1f}" + """% Failure Rate</p>
        </div>
""")

        if errors > 0:
            f.write("""        <div class="stat-card error">
            <h4>Errors Encountered</h4>
            <p style="font-size: 24px; font-weight: bold; color: var(--warning);">""" + str(errors) + """ / """ + str(total) + """</p>
            <p>""" + f"{errors/total*100:.1f}" + """% Error Rate</p>
        </div>
""")

        # Calculate percentages safely (avoid division by zero)
        success_pct = f"{total_checks_passed/total_checks*100:.1f}" if total_checks > 0 else "0.0"
        failed_pct = f"{total_checks_failed/total_checks*100:.1f}" if total_checks > 0 else "0.0"

        f.write("""        <div class="stat-card">
            <h4>Total Validation Checks</h4>
            <p style="font-size: 24px; font-weight: bold; color: var(--purple);">""" + str(total_checks) + """</p>
            <p>✓ Successful: """ + str(total_checks_passed) + """ (""" + success_pct + """%)</p>
            <p>✗ Failed: """ + str(total_checks_failed) + """ (""" + failed_pct + """%)</p>
        </div>
    </div>

    <h2>Detailed Chapter Validation Reports</h2>
    <p>The following sections provide complete validation details for each chapter, including all successful and unsuccessful checks.</p>
""")

        # Detailed chapter reports
        for result in results:
            chapter_name = result.get("chapter_name", "Unknown")
            status = result.get("overall_status", "UNKNOWN")
            successful_checks = result.get("successful_checks", [])
            failed_checks = result.get("failed_checks", [])

            status_class = "passed" if status == "PASS" else "failed"
            status_text = "PASSED" if status == "PASS" else "FAILED" if status == "FAIL" else status
            status_icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"

            f.write(f"""
    <div class="chapter-section {status_class}">
        <h3>{status_icon} {chapter_name}</h3>
        <span class="status-badge {status_class}">{status_text}</span>
        <p><strong>Checks Performed:</strong> {len(successful_checks) + len(failed_checks)} |
           <strong>Passed:</strong> {len(successful_checks)} |
           <strong>Failed:</strong> {len(failed_checks)}</p>
""")

            if result.get("summary"):
                summary = result["summary"].replace("<", "&lt;").replace(">", "&gt;")
                f.write(f"""        <p><strong>Summary:</strong> {summary}</p>\n""")

            # Successful checks
            if successful_checks:
                f.write("""
        <h4>✓ Successful Validations</h4>
        <table>
            <thead>
                <tr>
                    <th>Check</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
""")
                for check in successful_checks:
                    check_name = check.get("check", "Unknown").replace("<", "&lt;").replace(">", "&gt;")
                    details = check.get("details", "Passed").replace("<", "&lt;").replace(">", "&gt;")
                    f.write(f"""                <tr>
                    <td><span class="check-icon success">✓</span>{check_name}</td>
                    <td>{details}</td>
                </tr>
""")
                f.write("""            </tbody>
        </table>
""")

            # Failed checks
            if failed_checks:
                f.write("""
        <h4>✗ Failed Validations</h4>
        <table>
            <thead>
                <tr>
                    <th>Check</th>
                    <th>Issue</th>
                    <th>Location</th>
                </tr>
            </thead>
            <tbody>
""")
                for check in failed_checks:
                    check_name = check.get("check", "Unknown").replace("<", "&lt;").replace(">", "&gt;")
                    issue = check.get("issue", "No details").replace("<", "&lt;").replace(">", "&gt;")
                    location = check.get("location", "N/A").replace("<", "&lt;").replace(">", "&gt;")
                    f.write(f"""                <tr>
                    <td><span class="check-icon error">✗</span>{check_name}</td>
                    <td>{issue}</td>
                    <td>{location}</td>
                </tr>
""")
                f.write("""            </tbody>
        </table>
""")

            # Recommendations (with priority support)
            recommendations = result.get("recommendations", [])
            if recommendations:
                sorted_recs = sort_recommendations_by_priority(recommendations)
                f.write("""        <div class="recommendations">
            <h4>📿 Edit Recommendations</h4>
""")
                for rec in sorted_recs:
                    if isinstance(rec, dict):
                        # New priority-based format
                        priority = rec.get("priority", 3)
                        priority_info = get_priority_info(priority)
                        location = rec.get("location", "").replace("<", "&lt;").replace(">", "&gt;")
                        issue = rec.get("issue", "").replace("<", "&lt;").replace(">", "&gt;")
                        original = rec.get("original", "").replace("<", "&lt;").replace(">", "&gt;")
                        suggested = rec.get("suggested", "").replace("<", "&lt;").replace(">", "&gt;")

                        f.write(f"""            <div class="recommendation-item {priority_info['class']}">
                <span class="priority-label">{priority_info['icon']} {priority_info['label']}</span>
                <span class="location">{location}</span>
                <div class="issue">{issue}</div>
""")
                        if original:
                            f.write(f"""                <div class="original"><strong>Original:</strong> {original}</div>\n""")
                        if suggested:
                            f.write(f"""                <div class="suggested"><strong>Suggested:</strong> {suggested}</div>\n""")
                        f.write("""            </div>\n""")
                    else:
                        raise LegacyRecommendationFormatError(
                            f"Legacy recommendation format detected in save_html_report: {type(rec).__name__}"
                        )
                f.write("""        </div>
""")

            f.write("""    </div>
""")

        # Summary of issues
        if failed > 0 or errors > 0:
            f.write("""
    <h2>The following Issues Require Attention</h2>
    <p>The following chapters require corrections before final approval:</p>
""")

            for result in results:
                if result.get("overall_status") in ["FAIL", "ERROR", "TIMEOUT", "UNKNOWN"]:
                    chapter_name = result.get("chapter_name", "Unknown")
                    failed_checks = result.get("failed_checks", [])
                    f.write(f"""
    <div class="chapter-section failed">
        <h3>{chapter_name}</h3>
        <ol>
""")
                    for check in failed_checks:
                        check_name = check.get("check", "Unknown").replace("<", "&lt;").replace(">", "&gt;")
                        issue = check.get("issue", "No details").replace("<", "&lt;").replace(">", "&gt;")
                        f.write(f"""            <li><strong>{check_name}:</strong> {issue}</li>\n""")
                    f.write("""        </ol>
    </div>
""")

        # Conclusion
        f.write("""
    <div class="conclusion">
        <h2>Conclusion</h2>
""")

        if failed == 0 and errors == 0:
            f.write(f"""        <p>All {total} chapters have successfully passed {agent_name} validation.
        The manuscript has been thoroughly reviewed and found to be in compliance with all {total_checks} validation criteria.</p>
""")
        else:
            f.write(f"""        <p>This manuscript has been reviewed with {total_checks} validation checks across {total} chapters.
        {passed} chapters passed all validations, while {failed + errors} chapters require attention as detailed in the sections above.</p>
""")

        f.write(f"""
        <h3>Certification</h3>
        <p>This validation report was generated using automated {agent_name} review processes and provides
        an assessment of the manuscript's compliance with established criteria.</p>
    </div>

    <div class="footer">
        <p>Report prepared: {date_formatted}</p>
        <p>Generated by: Catholic Chapter Reviewer</p>
        <p>For submission to: Bishop's Office</p>
        <p style="margin-top: 20px; font-size: 18px; color: var(--gold);">✟ Ad Maiorem Dei Gloriam ✟</p>
    </div>
</body>
</html>
""")


def main():
    parser = argparse.ArgumentParser(
        prog='bin/chapter-reviewer.py',
        description="""✟ Catholic Book Chapter Reviewer ✟

Review all chapters with a specified Claude Code agent.
Generates professional HTML reports suitable for Bishop's office submission.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review all chapters
  %(prog)s CCC
  %(prog)s COMPREHENSIVE

  # Review specific chapters
  %(prog)s CCC chapter_01.md
  %(prog)s COMPREHENSIVE chapter_01.md chapter_02.md chapter_03.md

Available Agents located in .agents folder.

Models:
  opus      - Claude Opus 4.5 (most capable, higher cost)
  sonnet    - Claude Sonnet 4.5 (balanced performance/cost, default)
  haiku     - Claude Haiku (faster, lower cost)

API Fallback:
  If Claude CLI budget is exhausted, you'll be prompted to switch to
  the Anthropic API. The API key will be stored in .env.local.
  Use --api flag to use Anthropic API directly from the start.

Output:
  - Real-time progress with token usage
  - Incremental HTML report updates
  - Detailed validation results
  - Versioned reports: reports/{AGENT}-review1.html (auto-incremented)
  - Latest report: reports/final/{AGENT}.html (always overwritten)

Concise Mode (--concise):
  Generates a minimal report with only recommendations, optimized for
  passing to an LLM for automated modifications. Omits detailed check
  results and focuses on actionable items.

Ad Maiorem Dei Gloriam ✟
        """
    )
    parser.add_argument(
        "agent_name",
        help="Name of the agent to use (e.g., CCC, COMPREHENSIVE, CONCISE)"
    )
    parser.add_argument(
        "chapters",
        nargs="*",
        help="Specific chapter files to review (e.g., chapter_01.md chapter_02.md). If not specified, reviews all chapters."
    )
    parser.add_argument(
        "--chapters-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing chapter files (default: current directory)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save review reports (default: same as chapters-dir)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="opus",
        help="Claude model to use (default: opus). Options: opus, sonnet, haiku"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Use Anthropic API directly instead of Claude CLI"
    )
    parser.add_argument(
        "--concise",
        action="store_true",
        help="Generate concise report with only recommendations (for LLM processing)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show dimmed debug boxes around each API request and response"
    )

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Setup paths
    chapters_dir = args.chapters_dir
    output_dir = args.output_dir or (chapters_dir / "reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup final report directory
    final_dir = output_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    # Display header
    console.print()
    console.print(Panel.fit(
        "[header]✟ Catholic Book Chapter Reviewer ✟[/header]\n"
        "[sacred]Ad Maiorem Dei Gloriam[/sacred]",
        border_style="gold1"
    ))
    console.print()

    # Find chapters and agent
    console.print(f"[info]📂 Looking for chapters in:[/info] {chapters_dir}")

    # If specific chapters were provided, use those; otherwise find all
    if args.chapters:
        chapters = []
        for chapter_name in args.chapters:
            chapter_path = chapters_dir / chapter_name
            if not chapter_path.exists():
                console.print(f"[error]Chapter not found:[/error] {chapter_name}")
                sys.exit(1)
            chapters.append(chapter_path)
        console.print(f"[success]Reviewing {len(chapters)} specified chapters[/success]")
    else:
        chapters = find_chapters(chapters_dir)
        console.print(f"[success]Found {len(chapters)} chapters[/success]")

    # console.print(f"[info]🤖 Looking for skill:[/info] {args.agent_name}")
    workflow_file = find_agent_workflow(args.agent_name, chapters_dir)
    console.print(f"[success]Found skill:[/success] {workflow_file.name}")
    console.print()

    # Initialize API mode and debug mode
    global _use_anthropic_api, _debug_mode
    _use_anthropic_api = args.api
    _debug_mode = args.debug

    if _use_anthropic_api:
        if not setup_anthropic_api():
            console.print("[error]Failed to setup Anthropic API. Exiting.[/error]")
            sys.exit(1)
        model_id = ANTHROPIC_MODEL_MAP.get(args.model, ANTHROPIC_MODEL_MAP["sonnet"])
        console.print(f"[success]🔑 Anthropic API ready (model: {model_id})[/success]")

    # Determine if we're doing per-chapter reports (specific chapters) or combined report (all chapters)
    per_chapter_mode = bool(args.chapters)

    # Setup logging directory
    log_dir = output_dir / LOG_DIR_NAME
    log_dir.mkdir(parents=True, exist_ok=True)

    # Process chapters with progress bar
    results = []
    output_files = []  # Track all output files for per-chapter mode

    # For combined mode, get a single output file
    if not per_chapter_mode:
        output_file = get_next_review_filename(args.agent_name, output_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        task = progress.add_task(
            "[sacred]Reviewing chapters...[/sacred]",
            total=len(chapters)
        )

        for chapter in chapters:
            progress.update(task, description=f"[chapter]Reviewing {chapter.name}...[/chapter]")

            # Choose review method based on mode
            if _use_anthropic_api:
                result = run_anthropic_review(chapter, workflow_file, args.model, args.agent_name, log_dir)
            else:
                result = run_claude_review(chapter, workflow_file, args.model)

                # Check for budget exhaustion and offer to switch to API
                if result.get("overall_status") == "BUDGET_EXHAUSTED":
                    # Stop progress bar to allow user input
                    progress.stop()
                    console.print()
                    console.print("[warning]⚠ Claude CLI budget exhausted![/warning]")
                    console.print(f"[dim]{result.get('error', 'No details')}[/dim]")
                    console.print()

                    # Ask user if they want to switch to API
                    if Confirm.ask("[info]Would you like to continue using the Anthropic API?[/info]", default=True):
                        if setup_anthropic_api():
                            _use_anthropic_api = True
                            console.print("[success]Switched to Anthropic API[/success]")
                            console.print()
                            # Resume progress bar
                            progress.start()
                            # Retry this chapter with API
                            result = run_anthropic_review(chapter, workflow_file, args.model, args.agent_name, log_dir)
                        else:
                            console.print("[error]Failed to setup Anthropic API. Stopping.[/error]")
                            results.append(result)
                            break
                    else:
                        console.print("[info]Stopping review process.[/info]")
                        results.append(result)
                        break

            results.append(result)

            # Show immediate feedback with token usage on one line
            status = result.get("overall_status", "UNKNOWN")
            metadata = result.get("_metadata", {})

            # Format token usage info
            input_tokens = metadata.get("input_tokens", 0)
            output_tokens = metadata.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens
            cost = metadata.get("total_cost_usd", 0)
            duration = metadata.get("duration_ms", 0) / 1000  # Convert to seconds

            # Count passed/failed checks
            passed_checks = len(result.get("successful_checks", []))
            failed_checks = len(result.get("failed_checks", []))

            # Build one-line status
            status_icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
            status_color = "success" if status == "PASS" else "error" if status == "FAIL" else "warning"

            status_line = f"  [{status_color}]{status_icon}[/{status_color}] {chapter.name}"
            status_line += f" [{status_color}]({passed_checks}✓ {failed_checks}✗)[/{status_color}]"

            if total_tokens > 0:
                status_line += f" [info]{total_tokens:,}tok ${cost:.4f} {duration:.1f}s[/info]"

            progress.console.print(status_line)

            # Save report(s)
            if per_chapter_mode:
                # Per-chapter mode: save one report per chapter
                chapter_output_file = get_next_review_filename(args.agent_name, output_dir, chapter.name)
                save_html_report([result], args.agent_name, chapter_output_file, args.concise)
                output_files.append(chapter_output_file)
            else:
                # Combined mode: update the combined report incrementally
                save_html_report(results, args.agent_name, output_file, args.concise)

            progress.advance(task)

    console.print()

    # Display results
    display_results(results, args.agent_name)

    # Calculate total token usage and cost
    total_input_tokens = sum(r.get("_metadata", {}).get("input_tokens", 0) for r in results)
    total_output_tokens = sum(r.get("_metadata", {}).get("output_tokens", 0) for r in results)
    total_tokens = total_input_tokens + total_output_tokens
    total_cost = sum(r.get("_metadata", {}).get("total_cost_usd", 0) for r in results)
    total_duration = sum(r.get("_metadata", {}).get("duration_ms", 0) for r in results) / 1000  # Convert to seconds

    console.print()

    if per_chapter_mode:
        # Per-chapter mode: show each report file, no final report
        summary_msg = "[success]✓ Review Complete[/success]\n"
        summary_msg += "[info]Reports generated:[/info]\n"
        for of in output_files:
            summary_msg += f"  [chapter]reports/{of.name}[/chapter]\n"
    else:
        # Combined mode: save final report and show both
        final_file = final_dir / f"{args.agent_name}.html"
        save_html_report(results, args.agent_name, final_file, args.concise)

        console.print(f"[info]Versioned report:[/info] [chapter]{output_file}[/chapter]")
        console.print(f"[info]Latest report:[/info] [chapter]{final_file}[/chapter]")

        summary_msg = "[success]✓ Review Complete[/success]\n"
        summary_msg += f"[info]Versioned:[/info] [chapter]reports/{output_file.name}[/chapter]\n"
        summary_msg += f"[info]Latest:[/info] [chapter]reports/final/{final_file.name}[/chapter]\n"

    if total_tokens > 0:
        summary_msg += "\n[sacred]📊 Total Usage:[/sacred]\n"
        summary_msg += f"[info]  Input tokens: {total_input_tokens:,}[/info]\n"
        summary_msg += f"[info]  Output tokens: {total_output_tokens:,}[/info]\n"
        summary_msg += f"[info]  Total tokens: {total_tokens:,}[/info]\n"
        summary_msg += f"[info]  Total cost: ${total_cost:.4f}[/info]\n"
        summary_msg += f"[info]  Total time: {total_duration:.1f}s ({total_duration/60:.1f}m)[/info]"

    console.print(Panel.fit(summary_msg, border_style="green"))
    console.print()

    # Open report(s) in the editor
    if False:
        open_script = chapters_dir / "bin" / "open-in-editor"
        if open_script.exists():
            try:
                if per_chapter_mode:
                    # Open each per-chapter report
                    for of in output_files:
                        subprocess.run([str(open_script), str(of)], check=False)
                else:
                    # Open the final combined report
                    subprocess.run([str(open_script), str(final_file)], check=False)
            except Exception as e:
                console.print(f"[warning]Could not open report: {e}[/warning]")

    # call beep cli with no args...
    if True:
        subprocess.run(["beep"], check=False)

    # Exit with appropriate code
    failed = sum(1 for r in results if r.get("overall_status") != "PASS")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
