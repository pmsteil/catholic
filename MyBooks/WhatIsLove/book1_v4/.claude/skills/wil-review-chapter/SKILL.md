---
name: "wil-review-chapter"
description: "Builds a review document for a chapter of Patrick Steil's book \"What Is Love? God's Perfect Love\", and applies the resulting notes back to the chapter's Markdown source. Use whenever the user asks to review, mark up, annotate, proofread, edit, or collect notes on a chapter of the book — \"build a review doc for chapter 16\", \"let me mark up chapter 9\", \"I want to go through chapter 12\" — and whenever the user hands back an exported set of review notes to be applied. Also use when asked which chapter file a note belongs to, or to regenerate a review document after edits have landed. This skill owns the book-specific parts only: which file is the source of truth, the chapter's formatting conventions (intentional LaTeX, raw HTML blockquotes, diagnostic tables, the canonical definition), the standing redline-before-apply rule, and the build defaults. The document mechanics come from the rich-html-doc skill, which this one calls rather than reimplements."
---

# Reviewing a chapter of *What Is Love?*

This skill is a thin book-specific layer over **`rich-html-doc`**. That skill owns every
mechanic — segmentation, note capture, keyboard handling, export format, offline fonts.
Do not reimplement any of it here, and do not hand-write a review document. Read
`rich-html-doc/SKILL.md` before building.

What *this* skill owns is the part that is particular to the book: which file is the
source of truth, how the chapters are formatted, and what must not be broken when notes
come back.

## The one rule that matters

**The Markdown chapter file is the source of truth. The review HTML is disposable.**

`chapters/chapter_##.md` is the input to Patrick's book-generation script. Every note
from a review pass is applied to that `.md` file. The review document is a viewing and
marking surface that gets regenerated afterwards; it is never edited, never patched, and
never the thing a note lands in.

This is the opposite of the general `rich-html-doc` default, where editing the generated
HTML in place is often the sensible thing. Here it is a mistake — an edit applied to the
HTML is lost the next time the chapter is rebuilt, and worse, it makes the two files
disagree while both look current.

So the export always carries the **full absolute path** of the `.md` file, not a bare
filename. Pass it explicitly:

```
--source /abs/path/to/book1_v4/chapters/chapter_15.md
```

## Before touching a chapter

Read the project's own instructions first — they outrank anything here:

- `AGENTS.md` and `CLAUDE.md` at the book root.
- `memory.html`, which `AGENTS.md` names as the single source of truth for conventions,
  theological positions, editorial decisions, voice, and rejected approaches. Read §1
  Standing Rules and §18 Open Work Items in full. §18 records completed decisions *and*
  explicitly rejected approaches — do not reopen a rejected one without saying so.

## Applying notes back — the redline rule

From `CLAUDE.md`, and non-negotiable:

> Before writing ANY change to a chapter file, preview it as a rendered, styled,
> word-level inline redline — removed text as red strikethrough, added text in green,
> **coloured text only, no background highlighting** — shown once in place so the prose
> reads as it flows. Never plain markdown strikethrough in chat. Never a raw or
> horizontally-scrolling code diff. Never a separate before/after pair.

Then wait for Patrick's approval — `y` is his yes, `n` is his no — before writing to
disk. Every time, including one-line changes. Group related edits and let him approve
the group.

Render the redline as its own rich HTML document, built the same way as a review
document, so he can comment on the proposed changes rather than only accept or reject
them. Serif face, so it reads like the page.

**A note is not necessarily an edit.** The export says so explicitly and it is worth
repeating: a note may be replacement prose, an instruction, a question, an objection, or
a doubt. Answer what it actually says. Do not quietly rewrite a passage in place of
replying to a question about it.

## Chapter formatting conventions

These are the things that a careless pass will damage. Each is deliberate.

- **`\hfill\small` is intentional.** It is book-formatting LaTeX for scripture
  attributions and must survive editing untouched. Do not "clean it up". The builder
  lifts it into a `<cite>` for display; the `.md` keeps it verbatim.
- **`<div class="blockquote">` blocks are raw HTML in the Markdown**, used for the
  epigraph scripture quotations that open a chapter. Preserve the wrapper.
- **`<div class="callout" style="…">` blocks** carry inline styles from an older
  solarized palette. The builder drops the inline styles for display and renders them as
  callouts. **Do not strip them from the `.md`** unless Patrick asks — the book script
  may still consume them.
- **Diagnostic tables** use exactly four markers, defined once near the top of a chapter
  and applied uniformly: `✓ Present & Rightly Ordered`, `Partial`, `Distorted`,
  `✗ Absent`. The distinction between *Distorted* and *✗* is load-bearing argument, not
  formatting — a hijacked component is not an absent one. Never silently change a marker
  while editing a cell.
- **The canonical definition appears verbatim:** "God's Perfect Love is the sacred gift
  of covenant which binds truth, justice, mercy and sacrifice into life-giving
  communion." No Oxford comma in the pillar list. "sacrifice", never "sacrificial".
  Flag any drift; do not paraphrase it to fit a sentence. In the Introduction it is set
  across three lines as display typography — that is sanctioned, not drift.
- **Scripture is RSV**, always, quoted **in full and verbatim** — never adapted,
  shortened, or composited. Cited `Book Chapter:Verse · RSV`.
- **There is no word-count target and no ceiling.** A chapter runs as long as its
  argument requires; judge it by robustness, proportion to its purpose, and freedom from
  repetition that adds nothing. (Earlier versions of this skill and of `AGENTS.md` said
  2,000–2,500 words. Patrick retired that on 5 September 2026: "we will not try to solve
  any length issues… i am happy with their lengths." Do not reintroduce it, and do not
  report a chapter as over-length.)
- The book is in **final editing** — surgical edits, not drafting. Prefer the smallest
  change that answers the note.

## Two things that bite, from experience

**Never truncate a quotation without seeing the whole sentence.** A hostile-source
quotation once had its final word dropped, which reversed its meaning and would have
been findable by any reviewer in ninety seconds. If the source cannot be opened, say so
and ask Patrick to verify it rather than quoting from recollection or secondary
reporting.

**When a paragraph is expanded substantially, check what used to follow it.** Expanding
one paragraph into eight once stranded the paragraph after it, leaving a lost thread the
reader had no way to follow. The defect looked like a wording problem and was actually a
position problem.

## Building the document

Use `rich-html-doc`'s `scripts/build_review.py`. `scripts/review_chapter.sh` here wraps
it with the defaults below; it locates `build_review.py` rather than carrying a copy.

```bash
scripts/review_chapter.sh 15 /path/to/book1_v4 -o /path/to/ch15-review.html
```

The defaults it fills in, for chapter *N* with title *T* taken from the `#` heading:

| Flag | Value |
|---|---|
| `--source` | absolute path to `chapters/chapter_NN.md` |
| `--title` | the chapter's `# ` heading, verbatim |
| `--eyebrow` | `Chapter Fifteen` — the number spelled out |
| `--subtitle` | `Chapter 15 · Review` |
| `--label` | `Chapter 15` |
| `--key` | `wil-ch15-suggestions-v1` |
| `--brand-css` | the `brand-love` skill's `assets/love-brand.css` |
| `--root-class` | `love love--red love--dark` |
| `--fonts` | Cinzel, Cinzel Decorative, Libre Baskerville, Inter — see the script |

Red dark is the default (Patrick's choice, 2026-10-29). Use light only when he asks for it.

**The wrapper only handles `chapter_NN.md`.** For `2_preface.md`, `3_introduction.md`,
`epilogue.md`, `z_authors_note.md` or a redline document, call `build_review.py`
directly and supply the same flags by hand.

### Two builder bugs you must work around, every time

`build_review.py` escapes inline HTML and splits paragraphs into sentences. Both
behaviours break redlines and footnotes, and neither is fixed upstream.

**1. Inline HTML is escaped.** `<del>`, `<ins>` and `<sup>` render as literal text.
Patch the *output* after building, touching only text nodes so attribute values — which
carry the note-matching text — are left intact:

```python
def fix(m):
    t = m.group(1)
    for a, b in (('&lt;del&gt;', '<del>'), ('&lt;/del&gt;', '</del>'),
                 ('&lt;ins&gt;', '<ins>'), ('&lt;/ins&gt;', '</ins>'),
                 ('&lt;sup&gt;', '<sup>'), ('&lt;/sup&gt;', '</sup>')):
        t = t.replace(a, b)
    return '>' + t + '<'
s = re.sub(r'>([^<]*)<', fix, s)
```

Chapters 1, 6, 7, 8, 9 and 15 have footnote markers, so the `<sup>` half matters there
even for a plain review document.

**2. The sentence splitter breaks `del`/`ins` spans.** Each sentence is wrapped in its
own `<span class="sent">`, so a `<del>` or `<ins>` covering more than one sentence opens
in one span and closes in another, and the browser mis-closes it — only the first
sentence renders as struck or inserted. It also splits on abbreviations: `St.`, `A.D.`,
and filenames like `memory.html`.

So: **keep every `<del>` and `<ins>` to a single sentence**, and avoid those
abbreviations inside them (write "around the year 180", not "A.D. 180"). Where a
multi-sentence block is unavoidable, wrap each sentence in its own pair.

**Verify every build** before handing it over: compare the tag profile against an
unmodified build of the same source (3 unclosed / 3 mismatch is this builder's normal
baseline), and confirm no `<span class="sent">` contains an unbalanced `del` or `ins`.

### The storage key

**Leave `--key-version` alone.** It is tempting to bump it on every rebuild so a stale
pass cannot resurface against new prose. Don't: the key is where Patrick's in-progress
notes live, and changing it orphans them — he opens the new build and his review is gone.
(This is exactly how six of his notes were lost on 29 July 2026.) `rich-html-doc` handles
the problem the bump was meant to solve: every note carries the text it was attached to,
so a rebuilt chapter re-attaches notes whose paragraphs moved and reports the ones whose
passage no longer exists instead of silently misfiling them.

Bump it only when Patrick asks for a genuinely fresh pass on a chapter — and say so when
you do, because it hides the previous pass behind the recovery prompt.

### Provenance

`review_chapter.sh` stamps provenance two ways in every file it produces:

1. An HTML comment right after `<!DOCTYPE html>` (machine-readable):

   ```html
   <!-- generated-by: wil-review-chapter skill (wraps rich-html-doc/scripts/build_review.py) -->
   <!-- source-of-truth: /abs/path/to/book1_v4/chapters/chapter_15.md -->
   <!-- regenerate: wil-review-chapter/scripts/review_chapter.sh -->
   ```

2. A `Generated by:` line in the exported review notes, via `rich-html-doc`'s
   `--generator` flag — that is where a later session actually looks. Pass it by hand
   when calling `build_review.py` directly.

None of this shows on the page. Which skill built the file is of no interest
while reading it, and the absolute source path is on-screen noise; Patrick asked
for it out of the footer. The only build fact the reader sees is the generation
date, which `rich-html-doc` puts in the colophon.

This is why Patrick shouldn't need to name this skill again when he hands back a
review file or its exported notes: reading the file (or being told its path) is
enough to know which skill built it, what chapter `.md` it came from, and how to
rebuild it.

## The round trip

1. Build the review document from the `.md`.
2. Patrick reads and marks it up, offline, in a browser.
3. He copies or downloads the export — Markdown, one entry per note, each carrying the
   reference, the heading breadcrumb, and a quotation of the source text.
4. Locate each note **by its quotation**, not by its `¶` reference. The references exist
   only inside the review tool and shift the moment the chapter is edited. The quotation
   is what survives.
5. Show the whole group as one redline document. Wait for `y`.
6. Write to the `.md`.
7. Rebuild the review document from the revised `.md`, **keeping the same key** — see
   the storage-key rule above.

Step 4 is where this goes wrong most often. A `(sentence)` note replaces that one
sentence inside its paragraph; a `(table cell)` note replaces that one cell. Do not
rewrite the surrounding paragraph "to match" unless the note asks for it.

When Patrick has commented on some items and not others, his convention is that
**silence is approval** — apply the uncommented ones and redline the rest. The exception
is a paragraph where only part is commented: applying half writes prose to disk that is
neither old nor new, so hold the whole paragraph and say why.

## Before saying it is done

- The `.md` still contains every `\hfill\small`, every `<div class="blockquote">`, and
  every callout wrapper it started with — count them before and after.
- Every `<div>` is balanced, and footnote markers still match the notes defined.
- The canonical definition is byte-identical wherever it appears.
- No diagnostic marker changed unless a note asked for it.
- No superseded text is left behind — grep for the phrases you replaced.
- The redline was shown and approved before the write, not after.
- Decisions and their reasoning are recorded in `memory.html` §18, including anything
  rejected and why, so it is not re-argued cold in a later session.

