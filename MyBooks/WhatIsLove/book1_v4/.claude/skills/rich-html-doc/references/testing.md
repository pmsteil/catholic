# Rich HTML Doc — verification

Review documents are used away from support. Check the build before handing it over.

## Quick manual pass

1. Open the file with the network disabled. It should render immediately in the fallback
   faces, not stall.
2. Hover a paragraph → ✎ appears. Click → editor opens, focus lands in the textarea.
3. Save a note → gold left bar appears, count in the bottom bar increments, and all four
   export controls enable (they are disabled at zero notes).
4. Reload the page → the note is still there.
5. Hover a table row → ✎ appears in the trailing column. Save a note → it appears in a
   full-width row beneath, and the table's own note is unaffected.
6. Copy review notes → each entry has a reference, a breadcrumb, a quotation, and the
   comment.
7. Tab through with the keyboard alone. Every ✎ must be reachable and labelled.
8. Save several notes in a row and scroll. The document should still read as a document —
   if the notes dominate, they are too heavy. A one-line note is roughly 40px; a boxed
   panel is roughly 200px, and five of those is a page of chrome.

## Headless check

`jsdom` covers everything except paint. Stub `localStorage` and `HTMLDialogElement`:

```js
const {JSDOM} = require('jsdom');
const store = {_d:{}, getItem(k){return this._d[k]||null}, setItem(k,v){this._d[k]=v}};
const errs = [];
const dom = new JSDOM(html, {runScripts:'dangerously', beforeParse(w){
  Object.defineProperty(w,'localStorage',{value:store});
  w.HTMLDialogElement.prototype.showModal = function(){ this.open = true; };
  w.HTMLDialogElement.prototype.close     = function(){ this.open = false; };
  w.onerror = m => errs.push(m);
}});
```

Assert at least:

- page loads with `errs.length === 0`
- target count matches what the builder reported
- every `tr.rblk` is followed by a `tr.note-row`
- saving a note sets `has-note`, renders the text, and writes to storage
- edit reopens with the existing text; cancel restores; remove clears
- a row note and its table's note are independent
- export contains `##` reference, `>` quotation, breadcrumb, and comment text
- every ✎ has an `aria-label`; the action column header has a visually-hidden label
- every `.note-row` `colspan` equals the table's column count
- no anchor points anywhere except in-document `#` links

## Focus mode

- Toggling hides appbar, sidebar, bottom bar, and intro; prose stays.
- `F` toggles, `Esc` exits, and **neither fires while a textarea has focus** — otherwise
  typing the letter f in a comment throws the reader out of the document.
- The exit control is present and functional after a reload, not only after a click.
- Annotating still works while focused.

## Prefill

- Opening a fresh block prefills with its full text, not a truncated excerpt.
- Saving without editing stores nothing and tells the user why.
- Reopening a saved note shows the note, never the original.
- Caret sits at the end with no selection.
- Rows prefill with cells joined by ` | `.

## Sentences, cells, navigation

- Clicking a sentence opens its editor; **selecting text does not**.
- A cell's note renders inside the cell and does not squeeze the text to one word per line.
- The row control edits the row, not the enclosing table — check the ids, not the visuals.
- Arrows move, `E` edits, and neither fires while typing.
- At most two headings are pinned at once. Test by comparing each heading's
  `getBoundingClientRect().top` to its computed sticky `top`, not by "is it near the top of
  the viewport" — a heading that merely scrolled into that band is not stuck.

## Export header

Check that the header names the title, the label, the **source document**, the **review
file**, a timestamp, and the count; that the preamble explains scope, replacement-vs-
instruction, and that references do not exist in the source.

Test the review filename by **renaming the file and reloading it** — it is read from
`location` precisely so it survives a rename, and a build-time constant passes a naive test
while being wrong in use.

An export that says only "Review notes" is unusable a week later, and unusable to a model
immediately.

Also assert the preamble **does not frame every note as an edit** — the phrases telling the
reader not to assume a replacement, and to answer a question rather than rewrite around it,
are the difference between a model applying the review and a model silently discarding the
author's questions.

## Scrollspy

Assert that the highlighted sidebar entries **equal** the pinned headings, at several
scroll positions — not that "something is highlighted". Comparing the two lists is what
catches an off-by-one section, and it is the whole point of deriving both from the sticky
offset.

Also check: nothing is highlighted above the first section; at most two entries at once;
clicking a link leaves the heading below the sticky bar; the active entry stays inside the
sidebar's own scroll area.

## Failure modes worth testing for specifically

- **Row editor writing to the wrong host.** A row's textarea lives in the *next* element,
  not inside the row. Code that reaches for `blk.querySelector('textarea')` silently fails
  on rows while working on paragraphs. This bug shipped once; test both shapes.
- **Notes lost on reload** — usually a storage write that throws inside a `try` and gets
  swallowed. The document should warn the user, not fail quietly.
- **Action controls overlapping prose.** An absolutely-positioned control with a
  transparent background will render *on top of* the paragraph text. It looks fine on a
  short block and becomes unreadable garble on a full one. The control belongs in a
  reserved gutter — `padding-right` on the block — never floating over the words. Prove it
  geometrically rather than by eye:

  ```js
  const btn = el.querySelector('.blk__add').getBoundingClientRect();
  const body = el.querySelector('.blk__body').getBoundingClientRect();
  const overlapX = Math.min(btn.right, body.right) - Math.max(btn.left, body.left);
  const overlapY = Math.min(btn.bottom, body.bottom) - Math.max(btn.top, body.top);
  assert(!(overlapX > 0 && overlapY > 0));
  ```

  Also screenshot a hovered block with Playwright and look at it. jsdom has no layout, so
  it cannot catch this class of bug at all — every check can pass while the page is
  unusable.

- **A mode with no way out.** Hiding the chrome hides the export controls. Test the exit
  path after a reload, not just after toggling — a state restored from storage with no
  visible way to leave it strands the user with their notes locked inside the file.

- **`innerText` where it does not exist.** jsdom and some embedded engines implement only
  `textContent`. Reading `el.innerText.trim()` blind throws *inside a click handler*, which
  surfaces as a button that does nothing — no visible error, no clue. Guard with a
  `typeof` check and fall back to `textContent`. This is also the one bug jsdom will catch
  that a browser will not, so run both.

- **Prefill that select-alls.** `textarea.value = x` followed by `focus()` selects nothing
  in most browsers, but calling `select()` — or relying on `autofocus` on some engines —
  highlights the whole paragraph, and the reviewer's first keystroke wipes it. Set the
  caret explicitly.
- **Prefill overwriting saved work.** Distinguish "no note yet" from "note is an empty
  string" with `!== undefined`, not truthiness, or clearing a note and reopening it
  silently restores the original.

- **Sticky headings that stack instead of handing over.** All headings sharing one parent
  pin at the same offset and draw over each other; only paint order decides which is
  visible. Wrap each section in its own container.
- **A control that silently targets the wrong thing.** When a row and its parent table both
  have a ✎, a class name copied from the parent makes the row button edit the table. It
  looks completely correct on screen. Assert on the target's `id`, not on whether an editor
  opened.
- **`[hidden]` losing to a design system.** `hidden` sets `display:none` in the UA
  stylesheet, and any author rule — `.btn { display: inline-flex }` — beats it. Add an
  explicit `[hidden] { display: none }` for any component built on a styled base class.
- **Outlines on inline elements.** A sentence that wraps gets one outline box *per line*.
  Inline states need background and underline, never outline.

- **Copy doing nothing** in browsers where the clipboard API is unavailable over
  `file://`. The fallback selects the text and tells the user to press Ctrl/Cmd+C.

## Button-row checks

`btn.js` (jsdom) and `btnshot.js` (Chromium) cover the export group specifically. The two
catch disjoint failures and both are worth keeping:

- jsdom answers *identity* — is the button in the bottom bar and not the appbar, does it
  carry a text label as well as an icon, does the icon stroke `currentColor` with no
  hard-coded hex, does the whole group disable at zero notes and re-enable at one.
- Chromium answers *geometry* — icon size and vertical centring, icons inside their
  button box, no overlap, the bar still one row at 1440 / 1024 / 760, and the icon colour
  actually changing when the mode toggles.

jsdom implements `<dialog>` but not `showModal`/`close`; shim them in the jsdom pass and
prove real modal behaviour in the browser pass.
