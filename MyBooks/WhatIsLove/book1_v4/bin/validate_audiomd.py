#!/usr/bin/env python3
"""Validate that audiomd output preserves per-chapter line counts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
CHAPTERS_DIR = ROOT_DIR / "chapters"
ORDER_FILE = CHAPTERS_DIR / "build-chapters-order.txt"
METADATA_FILE = ROOT_DIR / "build" / "book-profile-default.yaml"
DEFAULT_AUDIOMD_PATH = ROOT_DIR / "WhatIsLove_book.audiomd.md"
CHAPTER_PATTERN = re.compile(r"^#\s+Chapter\s+(\d+)\s*:")
NON_CHAPTER_H1_PATTERN = re.compile(r"^#\s+(?!Chapter\s+\d)")
RESIDUAL_HTML_PATTERN = re.compile(r"<\/?div[^>]*>|<span[^>]*>", re.IGNORECASE)


def read_order_from_metadata() -> List[Path]:
    """Parse the default metadata file for a 'chapters:' list."""
    if not METADATA_FILE.exists():
        return []

    ordered: List[Path] = []
    in_list = False
    base_indent = None
    with METADATA_FILE.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not in_list:
                if re.match(r"^chapters:\s*$", line):
                    in_list = True
                    base_indent = None
                continue

            if not line.strip():
                break

            match = re.match(r"^(\s*)-\s+(.+?)\s*$", line)
            if not match:
                break

            indent = len(match.group(1))
            if base_indent is None:
                base_indent = indent
            elif indent < base_indent:
                break

            entry = match.group(2)
            ordered.append(CHAPTERS_DIR / entry)

    return ordered


def read_ordered_chapter_files() -> List[Path]:
    """Return chapter file paths in build order."""
    ordered = read_order_from_metadata()
    if ordered:
        return ordered

    if not ORDER_FILE.exists():
        raise FileNotFoundError(
            "No chapter order found in metadata and missing order file: " f"{ORDER_FILE}"
        )

    with ORDER_FILE.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            ordered.append(CHAPTERS_DIR / line)
    return ordered


def count_lines(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    return len(lines)


def split_audiomd_by_chapter(audiomd_path: Path) -> Dict[int, List[str]]:
    if not audiomd_path.exists():
        raise FileNotFoundError(f"Audiomd output not found at {audiomd_path}")

    lines = audiomd_path.read_text(encoding="utf-8").splitlines()
    chapters: Dict[int, List[str]] = {}

    current_number: int | None = None
    buffer: List[str] = []

    for line in lines:
        match = CHAPTER_PATTERN.match(line)
        if match:
            if current_number is not None:
                chapters[current_number] = buffer
            current_number = int(match.group(1))
            buffer = [line]
        elif current_number is not None and NON_CHAPTER_H1_PATTERN.match(line):
            # A non-chapter top-level heading (e.g. "# Author's Note") closes
            # the current chapter so it doesn't bleed into its line count.
            chapters[current_number] = buffer
            current_number = None
            buffer = []
        elif current_number is not None:
            buffer.append(line)

    if current_number is not None:
        chapters[current_number] = buffer

    return chapters


def detect_residual_html(audiomd_path: Path) -> List[str]:
    lines = audiomd_path.read_text(encoding="utf-8").splitlines()
    offenders: List[str] = []
    for idx, line in enumerate(lines, start=1):
        if RESIDUAL_HTML_PATTERN.search(line):
            offenders.append(f"Line {idx}: {line.strip()}")
    return offenders


def validate_line_counts(audiomd_path: Path) -> Tuple[List[Tuple[int, str, int, int]], List[str], List[str]]:
    ordered_files = read_ordered_chapter_files()
    chapter_segments = split_audiomd_by_chapter(audiomd_path)

    mismatches: List[Tuple[int, str, int, int]] = []
    missing: List[str] = []

    for chapter_file in ordered_files:
        name = chapter_file.name
        match = re.match(r"chapter_(\d+)\.md", name, re.IGNORECASE)
        if not match:
            continue

        chapter_number = int(match.group(1))
        original_count = count_lines(chapter_file)
        current_segment = chapter_segments.get(chapter_number)

        if current_segment is None:
            missing.append(f"Chapter {chapter_number} ({name}) missing from audiomd")
            continue

        audiomd_count = len(current_segment)
        if audiomd_count != original_count:
            mismatches.append((chapter_number, name, original_count, audiomd_count))

    html_artifacts = detect_residual_html(audiomd_path)

    return mismatches, missing, html_artifacts


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "audiomd",
        nargs="?",
        default=str(DEFAULT_AUDIOMD_PATH),
        help="Path to WhatIsLove_book.audiomd.md (defaults to project root)",
    )
    args = parser.parse_args(argv)

    audiomd_path = Path(args.audiomd)

    try:
        mismatches, missing, html_artifacts = validate_line_counts(audiomd_path)
    except FileNotFoundError as exc:
        print(exc)
        return 1

    if missing:
        print("Chapters missing in audiomd output:")
        for item in missing:
            print(f"  - {item}")

    if mismatches:
        print("Line-count mismatches detected:")
        for chapter, name, original, generated in mismatches:
            diff = generated - original
            print(
                f"  - Chapter {chapter:>2} ({name}): original={original} vs audiomd={generated} (diff {diff:+d})"
            )

    if html_artifacts:
        print("\nResidual HTML detected in audiomd output:")
        for entry in html_artifacts[:20]:
            print(f"  - {entry}")
        if len(html_artifacts) > 20:
            print(f"  - …and {len(html_artifacts) - 20} more lines")

    if mismatches or html_artifacts:
        print("\nValidation failed.")
        return 1

    print("All chapter line counts match between source files and audiomd output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
