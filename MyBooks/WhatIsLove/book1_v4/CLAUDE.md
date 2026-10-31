@agents.md

## ALWAYS: show a nicely formatted diff before applying any edit

Before writing ANY change to a chapter or file, ALWAYS preview it as a **nicely formatted, styled diff** — a rendered, track-changes redline (removed text shown as red strikethrough, added text shown in green — colored text only, no background highlighting), not plain markdown strikethrough in chat and never a raw/horizontally-scrolling code diff. In Cowork or chat, render it with the visualization widget so it reads like the page. In Claude Code, build it as a styled HTML file with `prompts/redline-tools/redline.py` (see `prompts/redline-tools/edits.py` for the edit format), then open it in the browser pane or publish it as an Artifact. Then wait for Patrick's approval ("y"/"n") before saving. This is non-negotiable and applies every single time, even for one-line changes. (Full redline spec is in agents.md / §1.)

## Claude Code only: how to load the memory map

Do not read `memory.html` in full in Claude Code. It is 470 KB and most of it is the completed-work log. Read these generated files instead:

1. `memory/README.md`, the index.
2. `memory/core.md`, every session. It holds the standing rules, writing guidelines, voice and theology.
3. `memory/chapters/chNN.md` for the chapter you edit, and `memory/structure.md` when you restructure.
4. `memory/open-items.md` before you pick the next task.
5. Search `memory/completed-log.md` with grep. Do not read it in full.

`memory.html` stays the single source of truth. Edit it, never the `memory/` files. After each edit, run `bin/split-memory.py`.

`research-notes.md` holds checked facts, figures, people and saints, with sources and where the book uses them. Read it BEFORE you research any fact. Add each new finding to it.
