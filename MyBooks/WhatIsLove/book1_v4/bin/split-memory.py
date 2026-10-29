#!/usr/bin/env python3
"""Split memory.html into small Markdown files in memory/ for Claude Code.

memory.html stays the single source of truth. Never edit memory/*.md by hand.
Run this script after every change to memory.html:

    bin/split-memory.py

Needs pandoc. Output: memory/README.md (index), core.md, structure.md,
research.md, open-items.md, completed-log.md and chapters/chNN.md.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "memory.html"
OUT = ROOT / "memory"

# h2 id -> output file
GROUPS = {
    "core.md": ["canonical", "voice", "theology", "rejected", "apologetics"],
    "structure.md": ["cross", "structure"],
    "research.md": ["research", "future", "sources"],
    "chapters/ch05.md": ["ch5"],
    "chapters/ch06.md": ["ch6"],
    "chapters/ch07.md": ["ch7"],
    "chapters/ch08.md": ["ch8"],
    "chapters/ch09.md": ["ch9"],
    "chapters/ch10.md": ["ch10"],
    "chapters/ch13-14.md": ["ch13"],
}

DESC = {
    "core.md": "Standing rules, writing guidelines, voice, theology, rejected approaches, apologetics. Read this first, every session.",
    "structure.md": "Book structure, chapter patterns, cross-chapter decisions. Read before restructuring or writing a new chapter.",
    "research.md": "Scripture and research citations, future work, source file index. Read when you cite or plan.",
    "open-items.md": "Open work items (In Progress and Future Tasks). Read before choosing the next task.",
    "completed-log.md": "Log of completed work and its reasons. Large. Do not read in full: search it with grep.",
}


def pandoc(fragment: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "html-native_divs-native_spans", "-t", "gfm", "--wrap=none"],
        input=fragment, capture_output=True, text=True, check=True,
    )
    return re.sub(r"\n{3,}", "\n\n", result.stdout).strip() + "\n"


def write(path: str, body: str) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "<!-- GENERATED from memory.html by bin/split-memory.py. "
        "Do not edit. Edit memory.html, then rerun the script. -->\n\n"
    )
    target.write_text(header + body)


def main() -> int:
    html = SRC.read_text()
    matches = list(re.finditer(r'<h2 id="([^"]+)">', html))
    if not matches:
        sys.exit("No h2 sections found in memory.html")
    sections = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else html.find("</body>")
        sections[m.group(1)] = html[m.start():end if end != -1 else len(html)]

    used = set()
    for path, ids in GROUPS.items():
        missing = [i for i in ids if i not in sections]
        if missing:
            sys.exit(f"Section id not found in memory.html: {missing}")
        write(path, "\n".join(pandoc(sections[i]) for i in ids))
        used.update(ids)

    todos = sections["todos"]
    done = re.search(r"<h3[^>]*>\s*Completed\s*</h3>", todos)
    if not done:
        sys.exit('Cannot find the "Completed" heading in section 18')
    write("open-items.md", pandoc(todos[:done.start()]))
    write("completed-log.md", pandoc(todos[done.start():]))
    used.add("todos")

    unassigned = set(sections) - used
    if unassigned:
        sys.exit(f"Sections not assigned to any file: {sorted(unassigned)}")

    rows = []
    for path in list(GROUPS) + ["open-items.md", "completed-log.md"]:
        size = (OUT / path).stat().st_size // 1024
        desc = DESC.get(path, "Decisions for this chapter. Read before you edit the chapter.")
        rows.append(f"| [{path}]({path}) | {size} KB | {desc} |")
    index = (
        "# Memory index\n\n"
        "These files are generated from `../memory.html`. Do not edit them.\n"
        "Edit `memory.html`, then run `bin/split-memory.py`.\n\n"
        "| File | Size | When to read |\n|---|---|---|\n" + "\n".join(rows) + "\n"
    )
    (OUT / "README.md").write_text(index)
    print(index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
