@agents.md

## ALWAYS: show a nicely formatted diff before applying any edit

Before writing ANY change to a chapter or file, ALWAYS preview it as a **nicely formatted, styled diff** — a rendered, track-changes redline (removed text shown as red strikethrough, added text shown in green — colored text only, no background highlighting), not plain markdown strikethrough in chat and never a raw/horizontally-scrolling code diff. In Cowork or chat, render it with the visualization widget so it reads like the page. In Claude Code, build it as a styled HTML file with `prompts/redline-tools/redline.py` (see `prompts/redline-tools/edits.py` for the edit format), then open it in the browser pane or publish it as an Artifact. Then wait for Patrick's approval ("y"/"n") before saving. This is non-negotiable and applies every single time, even for one-line changes. (Full redline spec is in agents.md / §1.)
