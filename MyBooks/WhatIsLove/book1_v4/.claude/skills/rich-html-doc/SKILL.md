---
name: rich-html-doc
description: Turns a chapter, article, report, spec or any prose source into a rich, self-contained, fully offline HTML document — typeset for reading, with sticky section headings, sticky table headers, a section navigator that tracks scrolling, a focus mode, and every heading, sentence, paragraph, table row and cell clickable so the reader can attach an edit, comment or question. Notes save locally and export as Markdown a person or a model can act on. Use whenever the user wants a document turned into readable interactive HTML; wants to review, mark up, annotate, comment on or red-line writing; asks for something they can click a sentence to suggest an edit on, read offline, send to a proofreader, or open in a browser with no server; or needs per-paragraph feedback exported so each note can be located in the source. Also use to rebuild an existing one. Styling comes from a brand — by default Patrick Steil's Love Brand via brand-love — but any brand stylesheet can be passed.
---

# Rich HTML Doc

Turns a source document into one HTML file that is a pleasure to read and can be marked up
and handed back — with no internet, no server, and no software beyond a browser.

Two things at once, and both matter. It is a **reading surface**: proper typography, sticky
section headings, a navigator that follows the reader, a focus mode. And it is a **review
surface**: every sentence, paragraph, row and cell can carry a note, and the notes export
in a form someone — or a model — can act on.

This skill owns the *document mechanics*: how content is split into targets, how notes are
captured and stored, and how they come back out in a form that can be located in the
source. It does **not** own the look. Styling comes from a brand stylesheet, which is a
separate concern and a separate skill.

## Build it with the script

The entry point is `scripts/build_review.py` — kept under that name so existing
invocations and docs keep working.

Do not hand-write these documents. `scripts/build_review.py` does the segmentation,
reference numbering, note plumbing, keyboard handling, export formatting, and offline
font loading — all of it already tested. Hand-rolling reproduces the bugs.

```bash
python3 scripts/build_review.py chapter_15.md -o ch15-review.html \
  --title "Counterfeit Love in the Modern World" \
  --eyebrow "Chapter Fifteen" --subtitle "Chapter 15 · Review" \
  --brand-css /path/to/love-brand.css \
  --root-class "love love--red love--dark" \
  --key wil-ch15 --label "Chapter 15" \
  --fonts "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap"
```

Everything is inlined into the output — brand tokens, annotation layer, content, script.
The result is a single file that can be emailed, dropped on a USB stick, or opened from a
folder with the network off.

## Branding

**Default to the user's own brand.** If the `brand-love` skill is present, pass its
`assets/love-brand.css` to `--brand-css` and use `--root-class "love love--red
love--dark"`. Dark is the default (Patrick's choice, 2026-10-29). Use light only when he asks for it.

To use a different brand, pass that stylesheet and its root class instead. The annotation
layer references only design tokens — `--surface`, `--ink`, `--accent`, `--border`,
`--space-*`, `--font-*` and friends — so any stylesheet defining them will paint it
correctly. If `--brand-css` is omitted, a deliberately plain neutral fallback is used and
the script says so on stderr; that is a fallback, not a design.

## What becomes commentable

**Everything with text in it is a target.** A reviewer has as much to say about a section
title as about the prose under it, and a document where some of the words answer to a
click and others quietly do not is worse than one where none of them do — the reader has
to learn a rule instead of just pointing at what they mean. Only horizontal rules are
skipped, having no text to comment on.

| Target | Reference | Reached by |
|---|---|---|
| Document title | `Title` | clicking it, or its ✎ |
| Heading | `§4` | clicking it, or its ✎ |
| Block — paragraph, list, quotation, callout, whole table | `¶042` | clicking it, or ✎ in the right gutter |
| Sentence, inside a paragraph | `¶042·s3` | clicking the sentence |
| Table row | `¶042 r3` | ✎ in the row's trailing column |
| Table cell | `¶042 r3c2` | clicking the cell, or its ✎ |

They are independent: "merge columns 2 and 3" belongs to the table, "this row overstates
it" to the row, "wrong word" to the cell. Deleting one never touches another.

Clicking resolves to the **finest** target under the pointer — `closest()` over the target
selector — so a sentence wins over its paragraph and a cell over its table, and the
coarser grain stays reachable from the ✎. A click on a table's own padding opens nothing:
commenting on all eight rows at once should be asked for deliberately, via the explicit
"Comment on whole table" button.

**Every target owns a named slot** — `<div class="note-slot" data-for="ID">` — emitted by
the builder. The script finds a target's note by id alone, so all the kinds share one code
path instead of one each. Adding another kind means emitting a slot, not writing new
plumbing.

### Headings are targets without being blocks

A heading cannot be wrapped in a `.blk` like every other target. Sticky headings depend on
the heading being a direct child of its own `<section>` (see below), and the scrollspy
resolves TOC hrefs straight to the heading elements; a wrapper breaks both. So the target
attributes go **on the heading itself**, with its note slot as the following sibling —
which the slot lookup handles already, since it finds slots by id from anywhere in the
document.

Two traps come with that:

- **The heading's anchor id doubles as its target id**, so anchors must be unique. Slugs
  truncated to 40 characters collide more often than they look — two subsections opening
  with the same six words is ordinary in a book — and a collision would silently merge two
  headings' notes into one. They are deduplicated with a counter.
- **Do not put `position:relative` on a bare `.hblk` class.** One class (0,1,0) outranks
  `main h2` (0,0,2) and silently un-stickies every section heading; the page looks correct
  until you scroll. The sticky rule is re-asserted at matching specificity, and the plain
  `relative` is there only for headings that were never sticky (h1, h4–h6) and for mobile,
  where the ✎ still needs something to anchor to.

The document title is rendered by the shell rather than the block stream, so the builder
**drops the source's own `# ` heading when it matches the title** — otherwise the title
prints twice, once under the other — and the shell's `<h1>` carries the target attributes
instead.

A cell's note renders **inside the cell**, stacked and without the reference (the cell is
its own location, and repeating it wastes the only width a narrow column has). A row's
note renders in a full-width row beneath.

**A saved note is itself a target: clicking it reopens that note for editing.** A review
pass is iterative — the second thought about a suggestion arrives while reading it back —
and the note should not have to be reached through its ✎ when the text is right there.
Clicking a note reopens *that note*, never a second editor for the block it hangs off.

**Keep the editor's Save and Cancel out of the field's flow, not on top of it.** In the
row layout they sit beside the textarea, which is fine. Inside a cell the note is a
vertical stack, and an absolutely-positioned corner placement lands them across the first
line of the textarea — covering the very text being edited. They go above the field, via
`order:-1`, so the DOM order (and therefore the tab order) still runs text-then-buttons.
Two traps in that column layout:

- **Reset `align-items` to `stretch`.** The row layout's `baseline` / `flex-start` are
  cross-axis values; once the container is a column the cross axis is horizontal, and the
  textarea shrinks to its content width instead of filling the cell.
- `align-self:flex-end` on the actions, not `text-align` — they are flex children.

### Sentence splitting

Paragraphs are split into sentences at build time and each becomes a `<span class="sent">`.
Two guards matter more than cleverness: never split after a known abbreviation or an
initial (`Mr.`, `C. S. Lewis`), and never split inside markdown emphasis — a fragment with
an unbalanced `**` renders as broken markup. When in doubt the splitter keeps the sentence
whole; an over-long target is a nuisance, a corrupted one is a bug.

Clicking a sentence opens its editor, **but only when nothing is selected** — otherwise
selecting a phrase to read it closely would fire the editor instead.

## Editing from the source text

Opening the editor on a block with no note yet **prefills the textarea with that block's
current text**, taken live from the DOM rather than a data attribute — so it is never
truncated and can never drift from what the reader is looking at. The reviewer edits the
real sentence instead of describing a change to it, which is faster and far less
ambiguous. Table rows prefill with their cells joined by ` | `.

Three rules make this safe:

- **Saving untouched text saves nothing.** The editor remembers what it prefilled and
  compares on save; an unchanged block is not a suggestion, and silently storing 190 copies
  of the chapter would make the export useless.
- **Reopening an existing note shows the note, not the original.** Re-prefilling would
  destroy work the reviewer has already done.
- **The caret goes to the end; nothing is selected.** A full selection means the first
  keystroke deletes the paragraph.

Clearing the box entirely still works — the reviewer can write a plain comment instead of
a rewrite, and a hint under the field says so.

## Keyboard navigation

Two levels, matching how a reader moves:

- <kbd>↑</kbd> <kbd>↓</kbd> — between coarse targets: paragraphs, lists, quotations,
  tables, table rows.
- <kbd>←</kbd> <kbd>→</kbd> — step into the fine ones: sentences inside a paragraph, cells
  inside a row. Stepping past either end returns to the parent.
- <kbd>E</kbd> — edit whatever is current.
- <kbd>Esc</kbd> — backs out one level: editor → cursor → focus mode.

The first <kbd>↓</kbd> starts from what is **on screen**, not the top of the document —
someone who has scrolled to chapter 12 does not want the cursor in chapter 1.

Two rules keep it from misfiring. Every shortcut is suppressed while a textarea has focus,
or typing the letter `f` in a comment throws the reader out of the document. And using the
mouse never leaves a keyboard cursor behind, or `Esc` afterwards clears an invisible
selection instead of doing what the reader expects.

## Autosave

Leaving an open editor — clicking anywhere else, or navigating away with the arrow keys —
**saves it**. Someone who types a suggestion and then clicks the next paragraph has
finished that thought; discarding it because they did not press Save is losing their work
on a technicality.

Cancel still cancels, because it sits inside the editor and so does not count as leaving.
Autosave is silent when nothing changed, and announced when something did.

## Sticky headings

The section (`h2`) and subsection (`h3`) headings follow the reader down the page, so a
long argument or a wide table never loses its context. Deeper levels are not sticky: three
stacked bars eat a third of a laptop viewport, which costs more than it gives.

**This only works because content is wrapped in nested `<section>` elements**, one per
heading. A sticky element is pinned while its *containing block* is on screen; if every
heading shares one parent they all pin at the same offset and silently stack on top of each
other, and which one you see is down to paint order. Sectioning gives each heading a scope
to hand over in.

## Sticky table headers

A table taller than the viewport loses its header row on the way down, and every cell
after that is unlabelled — worst in exactly the tables worth building this for, where the
argument *is* which column a cell sits in. So `thead` pins too, directly beneath whatever
heading is already pinned.

Two things make this work, and both are easy to get wrong:

- **The scroll wrapper has to stop being a scroll container.** `overflow-x:auto` forces
  `overflow-y` to `auto` as well, and a sticky `thead` inside a scroll container anchors
  to *that* container's scrollport — which never scrolls, because the wrapper is as tall
  as its content — so the header simply never pins. Above the mobile breakpoint the
  wrapper goes back to `overflow:visible`. Below it, horizontal scrolling is worth more
  than a pinned header, and the headings are not sticky there either.
- **The offset is measured, not hard-coded.** The header has to clear the pinned `h3`
  above it, and an `h3` that wraps to two lines is taller than one that doesn't — so a
  constant is wrong for half the tables on the page. `layoutTableHeads()` sets a
  `--thead-top` per table from the heading that actually governs it, and re-measures on
  resize, on focus toggle (which drops the appbar out of the stack), and once webfonts
  have landed and changed the heading heights.

It is a layout pass, so it is never called from the scroll handler. Give the `th` cells an
opaque background or the rows scroll through them; and because `border-collapse` leaves
the cell's bottom border behind with the table grid when the header detaches, the rule
under a pinned header is drawn as an inset shadow instead.

## Section navigation

The sidebar highlights the section and subsection the reader is in, updating as they
scroll. The active entry is **the heading that is currently pinned** — computed by
comparing each heading's position to its own sticky offset, not by guessing with a
viewport band. Deriving both from the same fact means the sidebar and the sticky bar can
never disagree, which is the usual failure of a hand-rolled scrollspy.

Details that matter:

- The state is `aria-current="location"`, so it is announced as well as drawn, and it is
  marked by weight and a left bar as well as colour.
- Headings carry `scroll-margin-top`, or clicking a link scrolls the heading you clicked to
  exactly where the sticky bar covers it.
- The sidebar scrolls itself to keep the active entry visible, without moving the page.
- Recomputed when focus mode toggles, because hiding the header changes every sticky
  offset.
- Throttled through `requestAnimationFrame` — a scroll handler that does layout reads on
  every event makes long documents stutter.

## Colophon

The document closes with one quiet right-aligned line: `Generated <date>`. A review file
outlives the moment it was built while the source keeps moving underneath it, so the
reader needs to be able to see at a glance whether what they are marking up is still
current. The same date goes into the export as `Review file generated:`, distinct from
`Exported:` — a wide gap between the two is the signal that notes were made against a
stale copy.

**Record it as a UTC instant and format it in the browser, never as the build machine's
wall clock.** These files get built somewhere other than where they are read — a
container running UTC, a CI runner, someone else's laptop — and a bare `12:35` lifted
from that machine is simply the wrong time to the person reading it. The build writes
`<time datetime="…+00:00">` and `review.js` reformats it into the reader's own timezone
on load, so one file is correct for everyone who opens it. The text inside `<time>` is
only the no-JS fallback, and it says `UTC` out loud rather than quietly showing a time
several hours off.

Keep it to the date. Build provenance — which tool made the file, what path it came from,
how to rebuild it — is not interesting while reading and does not belong on the page; put
it in an HTML comment and in the export, where the person or model acting on the notes
will actually look for it.

## Focus mode

`Focus` in the header (or `F`, or `Esc` to leave) hides the header, the section nav and the
bottom bar, and widens the prose to a single centred column. The state
persists across reloads, so a reading session survives closing the tab.

The annotation controls **stay live** in focus mode. Focus removes furniture, not function
— someone reading closely is exactly the person most likely to want to mark something.

Hiding the bottom bar also hides the whole export group, so a persistent `Exit focus` control
sits top-right at low opacity, plus `Esc`. Without it, focus mode is a trap: the reader
has no route back to their own export. Any future mode that hides chrome needs the same
escape hatch.

## The export controls

Three live together in the bottom bar — `Clear`, `View`, `Copy` — because they are one
group doing one job, and a reader looking for their notes should find every route to them
in one place. All three stay hidden until there is at least one note or answered question
to act on; a control with nothing to do reads as broken, not as "nothing here yet". The
appbar keeps only the two controls that change how the document *reads*: `Focus` and
`Dark`. (An earlier version also shipped `Download review notes` and `Restore notes` —
export-to-file and import-from-file. Both were removed: the reviewer hands notes to Claude
by copy/paste, not by file, so neither pulled its weight.)

They carry inline SVG icons, stroked `currentColor` so they follow the token through
light, dark, the primary fill and every hover state without a second rule. **The icon is
never the only label** — under 860px the qualifier drops and the buttons read `View`,
`Download`, `Copy`, keeping the verb visible while `aria-label` holds the full name for
assistive tech, which has no width problem to solve.

**All four disable together when there are no notes**, with the count beside them as the
explanation — one live button among three dead siblings reads as a bug rather than a
state.

Note the flex trap: a `.btn` is a flex container, so a bare text node next to a nested
span becomes *two* flex items and the button's `gap` opens up in the middle of a single
phrase. Wrap the whole label in one element.

## Surfacing a question back to the reviewer

The notes system is one-directional by design — it captures the reviewer's markup and
gets it out. But a model applying a review pass often hits a genuine fork: a note that's
a choice between phrasings, a concern that needs a judgment call, a claim worth checking
before it's incorporated. Those need an answer *from* the reviewer, in the document,
not a guess quietly substituted for one.

Pass `--questions path/to/questions.json` to `build_review.py`: a JSON array of
`{"key": "q1", "anchor": "¶042·s3", "text": "…"}`. `anchor` must equal the exact target
ref the question belongs to — `¶042` (block), `¶042·s3` (sentence), `¶042 r3` (row),
`¶042 r3c2` (cell), or `§4` (heading) — the same strings the builder already assigns and
prints in its `N block targets` summary. Get the anchor wrong and the question doesn't
vanish: it's rendered at the end of the document under its own heading, and the build
prints a warning naming the bad anchor, so a typo fails loudly instead of losing the
question.

Each question renders as a box that cannot be mistaken for chapter prose. It borrows the
brand's own *opposite*-mode palette — a light-mode document gets a dark-mode box, and
vice versa, computed from `--root-class` — so it never needs an invented accent colour;
with no brand supplied there is no other mode to borrow, and the fallback is a literal
bright highlight. The box carries its own answer field. There is no Save button: every
keystroke autosaves to its own storage, separate from the reviewer's own notes, so
answering feels like filling in a form rather than authoring an edit. Answered questions
gain a visual marker; the sidebar gains a "Questions to answer" panel above the section
list, with a live open-count, so a reviewer with outstanding questions sees that before
anything else — not just when they happen to scroll past one.

Both the answers and the questions themselves round-trip through the export: `View` /
`Copy` gains an "Answers to questions asked in this document" section (question text +
the reviewer's answer, or `_(not answered yet)_`), and the fenced restore block gets a
second `review-answers-data` sibling, so a pass recovered via the same-document banner
(see below) brings answers over the same way it brings notes.

## The export file

The export is written to be handed to a person **or a language model** and acted on with
no other context. A bare list of notes is guesswork at the other end, so the file states
what it is, what each part means, and what the reader is expected to do.

**A note is not necessarily an edit.** Reviewers write replacements, but they also write
instructions, questions, objections and doubts. The preamble says so explicitly and tells
the reader to answer a question rather than silently rewriting the passage in place of
replying — without that, a model handed this file treats every note as prose to substitute
and quietly loses the author's actual question:

```markdown
# Proposed edits to Chapter 15 — Counterfeit Love in the Modern World

Source document: `chapter_15.md`  (apply the edits here)
Review file: `ch15-review.html`  (where these edits were made)
Exported: 2026-07-27 13:01
2 proposed edits from a review pass.

## How to apply this file
… what the heading, the quotation and the note each mean …
```

Four things in that preamble earn their place:

- **Which file to change.** The source document and the review file are both named, and
  the preamble says outright that the HTML is not the file to edit. Without it, a model
  handed this will sometimes try to patch the review document.
- **Scope.** A `(sentence)` edit replaces that one sentence inside its paragraph; a
  `(table cell)` edit replaces that one cell. Left unsaid, a model rewrites the surrounding
  paragraph "to match".
- **References are not in the source.** `¶042` exists only in the review tool. Say so, or
  the reader searches the source file for it and finds nothing.
- **Replacement vs instruction.** A note may be finished prose to substitute, or a
  description of a change. The preamble says how to tell.

The **review file name is read from `location` at runtime**, not baked in at build time —
the reader may rename or move the file, and a stale filename in the export is worse than
none.

Then one Markdown block per note, containing three independent ways to find the spot:

```markdown
## ¶014 r3 (table row) — Section 1 › Postmodernism & Relativism

> Truth | ✗—self-refuting: it asserts "there is no objective truth" … | ✓

This row overstates the claim.
```

The reference, the heading breadcrumb, and a quotation of the source text. Three, because
**paragraph numbers shift the moment the document is edited** — the quotation is what
survives. Rows quote all their cells; paragraphs quote their opening 14 words.

## Offline is a hard requirement, not a preference

- No CDN scripts, no frameworks, no build step, no `fetch`. Vanilla JS only.
- Fonts load non-blocking via `media="print"` + an `onload` swap, so online they arrive
  and offline the request fails silently without stalling render. A plain stylesheet link
  would make the offline case *worse* than no link at all.
- Notes autosave to `localStorage`, so closing the tab is safe.

## Never lose a review pass

A half-finished review is the most valuable thing in the document and the easiest thing to
destroy: it lives in browser storage the reviewer did not choose, keyed to a document that
gets rebuilt underneath them. Three layers keep it, and all three matter.

**1. Every note stores the text it was attached to.** Block ids are positional (`p003`),
so inserting a paragraph shifts every id after it. On load, a note whose id no longer holds
the text it was written against is re-attached by quotation instead.

Two rules make that safe rather than merely clever:

- **A quotation matching more than one target identifies nothing.** `✓` appears in eighty
  cells. Ambiguous matches are left unplaced, never guessed at.
- **Never fall back to the id when the quotation fails to match.** After a paragraph is
  deleted, the old id still resolves — to a *different* paragraph. Attaching there silently
  moves a note onto text it was never about. That is worse than no match, because it looks
  like a successful restore. (This exact fall-back shipped in a draft of this feature and
  was caught only by deleting a paragraph and checking where the note landed.)

Notes that find no home are **kept and listed in the export** under their own heading with
their original quotation. A note the reviewer wrote is theirs; only they can decide it no
longer applies.

**2. Passes are recoverable across storage keys.** A rebuilt document — or one whose key
was bumped — scans storage for an earlier pass on the same source document and *offers* to
bring it over. Offered, never merged silently: the reviewer should know where the notes on
their screen came from. Documents are tied together by source path, which stays put while
keys, filenames and ids all move.

**3. The exported Markdown is a complete restore point.** It carries a fenced
`review-notes-data` block with the full payload, so the file (or copy/paste) the reviewer
already hands to Claude is also the backup record. There is no in-page way to load it back
in — the reviewer-facing import/export-to-file controls were removed as more machinery
than this workflow needed — but the data survives in the export regardless, and the
same-document recovery banner (layer 2, above) is what actually restores a pass in-browser.

**Do not bump the storage key on a routine rebuild.** It is the obvious way to stop a stale
pass resurfacing against new prose, and it throws away work in progress: the reviewer opens
the new build and their review is gone. Layer 1 already solves that problem properly.

**Tell the user the storage caveat anyway.** `localStorage` for a `file://` document is
scoped per browser, and some browsers scope it per file location too. Downloading the notes
is the real save; the browser is a convenience.

## Reviewing the result before handing it over

Run the checks in `references/testing.md`. At minimum, confirm in a headless DOM that the
page loads with no JS errors, that a note can be saved, re-opened, and removed, and that
the export contains the reference, the breadcrumb, the quotation, and the comment. These
documents are used away from any support — a broken one fails silently on a plane.

## Extending it

`references/format.md` covers the storage schema, the block-target contract, and how to
add a new source format or a new kind of target. Keep two invariants when extending:

- **A target's identity must be stable.** It is written into saved notes; changing the
  numbering scheme orphans every note the user has already made.
- **Every note must remain locatable without the document.** If a new target type cannot
  produce a meaningful quotation for the export, it is not ready to be a target.
