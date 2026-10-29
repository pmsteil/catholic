# Rich HTML Doc — internals

## Storage schema

One `localStorage` key, set by `--key` (default: a slug of the title). Value is a flat
JSON object mapping target id → comment string:

```json
{ "p014r3": "This row overstates the claim.", "p006": "Cut this sentence." }
```

Flat and stringly-typed on purpose. A note is a person's sentence about a place in a
document; anything more elaborate (categories, severities, authorship) has to be entered,
maintained, and understood, and none of it survives the export into a Markdown file that a
human reads. Add structure only when someone asks for it.

Note in particular that the schema does **not** record whether a note is a replacement, an
instruction or a question. Asking the reviewer to classify every note is friction on the
one activity the tool exists for, and the classification is usually obvious from the note
itself. The export preamble therefore tells the reader to judge each note on its content —
that judgement belongs at the point of use, not at the point of writing.

Deleting a note deletes the key. An empty string is never stored — saving a blank comment
removes the note, so "clear this" and "save nothing" are the same gesture.

## Target kinds

`block` · `sentence` · `row` · `cell`. `kindOf()` derives the kind from a class, and every
behaviour — prefill, render, export label, keyboard grouping — switches on that one value.

Coarse targets (block, row) are what <kbd>↑</kbd><kbd>↓</kbd> walk; fine targets
(sentence, cell) are what <kbd>←</kbd><kbd>→</kbd> step into. `fineOf()` defines the
relationship and is the only place that mapping lives.

## Target contract

Any element that is a comment target must carry:

| Attribute | Purpose |
|---|---|
| `id` | Stable identity; written into storage. |
| `data-ref` | Human reference shown in the UI and the export (`¶042`, `¶042 r3`). |
| `data-path` | Heading breadcrumb, ` › ` separated. Survives renumbering. |
| `data-plain` | Plain text of the block, ≤400 chars. Source of the export quotation. |

Every target also owns a slot — `<div class="note-slot" data-for="ID">` — emitted by the
builder next to wherever its note should appear: inside the block for a paragraph and its
sentences, inside the cell for a cell, in a following `<tr>` for a row. Lookup is
`document.querySelector('.note-slot[data-for="' + id + '"]')` and nothing else. This is why
adding sentence and cell targets required no new note plumbing.

Historically two shapes existed:

- **Block targets** — `.blk` with a child `.blk__note` for the editor and rendered note.
- **Row targets** — `tr.rblk` followed by a sibling `tr.note-row` whose cell holds the
  `.blk__note`. Rows cannot nest a div, so the note lives in the next row and the script
  resolves it through `hostOf()`.

To add a third shape, extend `hostOf()` and `showHost()` in `assets/review.js`. Everything
else — save, render, edit, delete, export, keyboard — is shape-agnostic and needs no
changes.

## Numbering

`p001`, `p002` … assigned in document order to targets only; headings and rules are
skipped, so numbers stay dense. Row ids append `r1`, `r2` … to their table's id.

**Numbering is not stable across rebuilds.** Insert a paragraph and every later reference
shifts, which is why the export carries the breadcrumb and the quotation as well. If you
rebuild a document a reviewer has already annotated, their notes will land on the wrong
blocks — tell them to export first, and treat rebuilds as a new round.

## Adding a source format

`parse()` in `scripts/build_review.py` takes text and returns a list of block dicts. Write
a new parser returning the same shape and `render()` works unchanged:

```python
{'kind': 'para',  'id': 'p001', 'path': 'A › B', 'plain': '…', 'html': '<p>…</p>'}
{'kind': 'table', 'id': 'p014', 'path': '…', 'plain': '…', 'head': [...], 'body': [[...]]}
{'kind': 'heading', 'level': 2, 'text': '…'}          # not a target
{'kind': 'hr'}                                         # not a target
```

Only `table` is special-cased in the renderer. Everything else needs `html` and `plain`.

## Sentence splitting quirks

The boundary regex must treat markdown emphasis as a closer. A sentence ending
`…communion.**` puts the closing asterisks between the full stop and the space; a splitter
that only allows quotes and brackets never sees the boundary and silently merges the next
sentences into that one. Closers are `" ' ’ ” ) ] * _` and backtick.

## Source quirks handled

- `<div class="blockquote">` blocks with `\hfill\small — Citation` inside are Pandoc/LaTeX
  book markup. The LaTeX is **intentional in the source** and is lifted into a `<cite>` for
  the HTML rather than treated as an error. Do not strip it from the source file.
- Markdown tables with or without a separator row.
- Fenced code blocks, ordered and unordered lists, inline links, bold, italic, code.

## What is deliberately absent

- **No inline text editing.** The reviewer describes a change; they do not rewrite the
  document. Two people editing the same prose in a file with no merge story produces a
  conflict nobody can resolve.
- **No server sync, accounts, or sharing.** The file is the unit. Email it back.
- **No note panels.** A saved note renders as a single-line margin annotation — reference,
  text, and nothing else — with Edit/Remove appearing only on hover. Notes accumulate; a
  boxed panel with a header and two full-size buttons per note buries the document under
  its own commentary by the tenth one. The prose is what is being read.
- **No toasts.** Feedback appears in one persistent live region above the action bar, so
  it is announced reliably rather than created-and-announced in the same instant.
