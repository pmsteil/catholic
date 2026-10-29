# Love Brand — component reference

Contents:

1. [Root and layout](#1-root-and-layout)
2. [Typography overrides](#2-typography-overrides)
3. [Ornament](#3-ornament)
4. [Cards](#4-cards)
5. [Callout: the definition block](#5-callout-the-definition-block)
6. [Quotation blocks](#6-quotation-blocks)
7. [The four-part accent set](#7-the-four-part-accent-set)
8. [Redline / diff](#8-redline--diff)
9. [Tables, badges, statistics](#9-tables-badges-statistics)
10. [Table of contents](#10-table-of-contents)
11. [Elements styled by tag](#11-elements-styled-by-tag)
12. [IDs](#12-ids)
13. [Full class list](#13-full-class-list)

Everything here is optional. Plain semantic HTML already renders correctly; these are
for structure the tags can't express on their own.

---

## 1. Root and layout

```html
<html lang="en" class="love love--red love--light">
  <body>
    <div class="page">        <!-- 1080px max, centred, padded -->
      <div class="prose"> … </div>    <!-- clamps to 68ch measure -->
      <div class="spread"> … </div>   <!-- 1.15fr / .85fr two-column, stacks under 860px -->
      <div class="stack"> … </div>    <!-- uniform vertical rhythm between children -->
    </div>
  </body>
</html>
```

`.prose` matters more than it looks. Paragraphs are already capped at `--measure`, but a
`div` full of mixed content isn't — wrap long-form regions in `.prose` or lines run to the
full 1080px and become tiring. Use `.wide` to opt a wide table out of the measure.

## 2. Typography overrides

Tags carry the defaults; these are for when semantic level and visual size must differ.

| Class | Use |
|---|---|
| `.eyebrow` | Small caps kicker above a heading |
| `.lede` | Opening paragraph, larger and muted |
| `.meta` | Byline, word count, timestamp, status line |
| `.dropcap` | Decorative first letter on an opening paragraph |
| `.citation` | Small print beneath a component, source note |

```html
<p class="eyebrow">Section Two</p>
<h2>The heading</h2>
<p class="lede">An opening line that carries more weight than body copy.</p>
<p class="meta">2,340 words · updated 26 July 2026</p>
```

## 3. Ornament

```html
<hr>                                        <!-- full-width hairline -->
<hr class="rule--short rule--center">       <!-- 64px gold rule -->
<div class="fleuron">✦ ✦ ✦</div>            <!-- scene break -->
```

The short rule uses `--ornament` and is decorative only. If a divider needs to communicate
structure rather than decorate it, use a plain `<hr>` — that one uses `--border` and is
perceivable in every palette.

## 4. Cards

Five variants, distinguished by the colour of the left border **and** the label text.

```html
<div class="card card--theology">
  <div class="card__label">Theology</div>
  Body content.
</div>
```

| Variant | Intended for |
|---|---|
| `card--theology` | Doctrine, principles, anything load-bearing (gold) |
| `card--decision` | A settled choice and its reasoning (blue) |
| `card--voice` | Tone, phrasing, style notes (green) |
| `card--research` | Sources, findings, open threads (amber) |
| `card--rejected` | Considered and declined — kept so it isn't re-proposed (red) |

The names are editorial in origin but map cleanly onto general use: `theology` → key
principle, `decision` → decision record, `voice` → style note, `research` → finding,
`rejected` → rejected option. Keep the label text, since it is what carries the meaning
for anyone who can't distinguish the border colours.

## 5. Callout: the definition block

A high-emphasis callout for a single statement that must be reproduced exactly — a
definition, a thesis, a policy line, a quoted commitment.

```html
<div class="definition">
  <div class="definition__label">Canonical · do not alter</div>
  <div class="definition__text">The statement.</div>
</div>

<div class="definition definition--hero">   <!-- centred, larger, for page openers -->
  …
</div>
```

## 6. Quotation blocks

Plain `<blockquote>` is styled and is usually right. `.scripture` is a variant with rules
above and below rather than a left bar, for a pull-quote that should sit as its own band.

```html
<blockquote>
  <p>The quotation.</p>
  <cite>Attribution</cite>
</blockquote>

<div class="scripture">
  "The quotation."
  <span class="scripture__cite">Psalm 85:10 · RSV</span>
</div>

<div class="scripture scripture--bar"> … </div>   <!-- left gold bar instead -->
```

## 7. The four-part accent set

```html
<ul class="pillars">
  <li class="pillar pillar--truth">Truth</li>
  <li class="pillar pillar--justice">Justice</li>
  <li class="pillar pillar--mercy">Mercy</li>
  <li class="pillar pillar--sacrifice">Sacrifice</li>
</ul>

<div class="pillar-strip">      <!-- 4px header band -->
  <div style="background:var(--p-truth)"></div>
  <div style="background:var(--p-justice)"></div>
  <div style="background:var(--p-mercy)"></div>
  <div style="background:var(--p-sacrifice)"></div>
</div>
```

Relabel freely for non-book use — the classes are the colour positions, not the words.
Keep all four at equal weight and always label in text; the green and red are
indistinguishable under deuteranopia.

## 8. Redline / diff

```html
<div class="redline">
  <div class="redline__label">Redline · §4</div>
  <del>old text</del> <ins>new text</ins>
</div>
```

The stylesheet injects `−` and `+` before deletions and insertions. Don't override it —
it's what keeps a diff readable in greyscale and under red-green colour blindness.

## 9. Tables, badges, statistics

`<table>` is fully styled; the classes below are additions.

```html
<table>
  <caption>Caption sits below, in the UI face.</caption>
  <thead><tr><th>Item</th><th>Status</th><th class="num">Count</th></tr></thead>
  <tbody>
    <tr><td>One</td><td><span class="badge ok">Final</span></td><td class="num">2,340</td></tr>
  </tbody>
  <tfoot><tr><td colspan="2">Total</td><td class="num">6,362</td></tr></tfoot>
</table>
```

`.num` right-aligns and uses tabular figures — apply it to every numeric column, header
included, or the column edges won't line up. `.mono` for code-ish cells.

Badges: `.badge` plus `.ok` / `.warn` / `.bad`. The word inside is the signal; the colour
reinforces it.

```html
<div class="stats">
  <div class="stat"><span class="stat__num">16</span><span class="stat__label">Chapters</span></div>
</div>
```

## 10. Table of contents

```html
<nav class="toc">
  <ol><li><a href="#one">First section</a></li></ol>
</nav>
```

Numbering comes from CSS counters, so don't hand-number the items.

## 11. Elements styled by tag

No classes needed for any of these:

| Group | Elements |
|---|---|
| Headings | `h1` `h2` `h3` `h4` `h5` `h6`, plus `<small>` inside a heading for a subtitle |
| Blocks | `p` `blockquote` (+ `cite`, `footer`) `address` `hr` `pre` |
| Inline | `a` `strong` `b` `em` `i` `small` `mark` `del` `s` `ins` `u` `abbr[title]` `cite` `q` `sub` `sup` `time` `code` `kbd` `samp` `var` |
| Lists | `ul` `ol` `li` `li::marker` `dl` `dt` `dd`, nesting handled |
| Tables | `table` `caption` `thead` `tbody` `tfoot` `tr` `th` `td`, even-row striping |
| Media | `figure` `figcaption` `img` `video` |
| Interactive | `details` `summary` `button` `label` `input` `textarea` `select` `fieldset` `legend` `progress` `::placeholder` |
| Global | `:focus-visible` `::selection`, print styles, `prefers-reduced-motion` |

## 12. IDs

The system defines **no styling on IDs**, deliberately. IDs outrank classes in
specificity, which makes them hard to override, and they can't repeat, which makes them
useless for anything reusable. Two jobs only:

- **Anchors** — `id="section-two"`. Lowercase, hyphenated, prefixed by kind.
- **Accessibility wiring** — `aria-labelledby`, `aria-describedby`, `<label for>`.

Script hooks should use `data-` attributes.

## 13. Full class list

```
Root       .love  .love--red  .love--blue  .love--light  .love--dark
Layout     .page  .prose  .spread  .stack  .wide
Type       .eyebrow  .lede  .meta  .dropcap  .citation
Ornament   .rule--short  .rule--center  .fleuron
Callout    .definition  .definition--hero  .definition__label  .definition__text
Quote      .scripture  .scripture--bar  .scripture__cite
Accents    .pillars  .pillar  .pillar--truth  .pillar--justice
           .pillar--mercy  .pillar--sacrifice  .pillar-strip
Cards      .card  .card__label  .card--decision  .card--theology
           .card--voice  .card--rejected  .card--research
Diff       .redline  .redline__label
Data       .badge  .badge.ok  .badge.warn  .badge.bad  .tag  .num  .mono
           .stats  .stat  .stat__num  .stat__label  .toc
Utility    .btn  .btn.is-on  .no-print
```

If a class isn't on this list it doesn't exist. Extend the stylesheet rather than
inventing one in a document.
