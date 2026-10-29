---
name: brand-love
description: Applies the Love Brand — Patrick Steil's personal design system for documents and application UI — to any HTML that gets produced. Two variants (red/crimson-gold, blue/Marian-gold) in light and dark, on measured WCAG contrast, covering prose, data, forms, buttons, navigation, app shells, alerts, tables and dialogs. Use whenever generating an HTML page, report, dashboard, one-pager, landing page, docs site, web app screen, sign-in/settings/admin UI, prototype, or chapter draft for this user, and whenever restyling existing HTML. Trigger even when the user does not say "brand", "theme", "style" or "CSS" — if the output is HTML and it is the user's own work, it should carry their brand rather than browser defaults or invented colours. Also use when asked which colour, font, token or class to use, whether a page is on-brand, or to make something "look nice" or "match my other docs".
---

# The Love Brand

Patrick Steil's design system. It applies to **anything HTML** he produces — websites,
web applications, reports, dashboards, documentation, marketing pages, book chapters,
internal notes.
It began as the visual identity for the book *What Is Love? God's Perfect Love*, which
is where the name and the crimson-and-gold palette come from, but it is a general brand.
Treat book-related work as one use among many, not as the point.

The system's job is consistency and readability: every surface should look like it came
from the same hand, and should stay comfortable to read for an hour.

Two variants (**red** and **blue**) × two modes (**light** and **dark**) = four palettes
sharing one grammar.

## When it does *not* apply

Use judgement rather than applying it reflexively. It is the user's own brand, so it
belongs on the user's own output. Skip it — or ask — when the work is styled for someone
else's identity (a client's site, a company template, a publication with its own
stylesheet), when the user has supplied their own CSS or design direction, or when the
deliverable isn't a visual document at all. Applying a personal brand to work that must
match an external identity is worse than leaving it unstyled.

## Applying it

Link the stylesheet and set two independent classes on `<html>`:

```html
<html lang="en" class="love love--red love--light">
  <link rel="stylesheet" href="love-brand.css">
  <body><div class="page"> … </div></body>
</html>
```

`assets/love-brand.css` is the stylesheet — copy it next to the document, or inline it
inside `<style>` when delivering a single self-contained file, which is usually the right
choice for something the user will open, share, or save. `assets/starter.html` is a
working page to copy.

Write both variant and mode explicitly rather than relying on a default, so a document's
appearance is never ambiguous.

Fonts load from Google Fonts (Cinzel Decorative, Cinzel, Libre Baskerville, Inter); the
tokens carry local serif fallbacks, so a page still reads correctly offline. For print or
PDF work, self-host the font files instead.

**When a document must work offline**, load them non-blocking so the network is an
enhancement rather than a dependency:

```html
<link rel="stylesheet" media="print" onload="this.media='all'"
      href="https://fonts.googleapis.com/css2?family=…&display=swap">
<noscript><link rel="stylesheet" href="…same…"></noscript>
```

Online the faces arrive and swap in; offline the request fails silently, `media` stays
`print`, the rule never applies, and the local stack is used. Neither case blocks render.
A plain `<link rel="stylesheet">` would stall the page while the request times out —
which is exactly the situation an offline document is in. If the faces happen to be
installed on the machine, the token stacks pick them up with no network at all.

## Choosing the variant

**Red** is Burnt Crimson and Gold Torch. Warm, serious, a little ceremonial. This is the
default — use it unless there's a reason not to.

**Blue** is Marian lapis and gold. Cooler and steadier, and it reads as more institutional
or documentary. Reach for it when red would feel too warm for the subject, when a document
should sit alongside the red material without competing with it, or for anything with a
Marian or covenantal theme where the association is doing real work. (Ultramarine was
ground from lapis and cost more than gold by weight, which is why the Church reserved it
for the Blessed Virgin.)

Gold is common to both, which is what makes them read as one system rather than two
brands. Never mix red and blue tokens in a single document.

**Light is the default mode.** Dark grounds cause halation — the bloom around light glyphs
on dark — which is worse for readers with astigmatism, and the user has it. Offer dark,
don't assume it. When a document is likely to be read at length, prefer light without
being asked.

## The rule that gets broken

Gold Torch `#be985c` measures 2.44:1 on the red light ground and 2.39:1 on the blue light
ground. **It can never be text on a light ground.** On both dark grounds it is comfortably
legible. So gold's role changes between modes, and the tokens encode that:

- `--accent` is text-safe in all four palettes. Every label, eyebrow, small-caps run,
  table header.
- `--ornament` is always true Gold Torch. Rules, borders, fills, flourishes — surfaces
  with no text on them.

The test is one question: *is this text?* If yes, `--accent`. If no, `--ornament`.

Two corollaries. Never hard-code `#be985c` — it is legible in one mode and invisible in
the other, so a hex that looked right while you happened to be in dark mode will silently
fail in light. And a gold rule cannot carry information on a light ground, because it
can't reach the 3:1 threshold non-text elements need; use `--border-strong` for anything a
reader must perceive to understand the page.

## Writing pages in it

Write correct, semantic HTML. Every element is styled by tag — headings, paragraphs,
blockquotes, lists, definition lists, tables with captions and footers, figures,
`details`, forms, and the full inline set (`mark`, `abbr`, `kbd`, `q`, `cite`, `sub`,
`sup`, `time`, `del`, `ins`). Plain HTML renders correctly with no classes at all, which
is what makes pasted content and Markdown conversions work without cleanup.

Classes exist for two things: components, and overriding a tag when semantic level and
visual size need to differ. An `<h3>` that must look like a page opener gets
`class="chapter-title"` — the heading level stays correct for screen readers and the
document outline while the appearance changes.

Never reference a raw hex value. If you need a colour no token provides, add a token and
re-check its contrast; inlining the value is how a system quietly stops being one.

For the full token table, the measured contrast figures for all four palettes, and the
markup for every component, read `references/tokens.md` and `references/components.md`.
Read them when building anything beyond a simple page, or whenever you're unsure which
token or class is correct — guessing a token name is the most common way a page drifts
off-system.

## Building application UI

The system has two layers over one set of tokens. The **document layer** covers anything
read; the **product layer** covers anything operated — buttons, forms, validation,
navigation, app shells, alerts, tabs, dialogs, menus, avatars, empty and loading states.
When building a screen rather than a page, read `references/app-patterns.md` for the full
markup; the essentials:

- **Buttons have a hierarchy.** `.btn` is the outlined default, `.btn--primary` is the one
  filled, dominant action per view, `.btn--danger` for destructive actions,
  `.btn--ghost` for tertiary. `.is-on` is reserved for toggles — using it as a primary
  button ships a control that permanently reports `aria-pressed="true"` to assistive tech.
- **Wrap inputs in `.field`**, and use `.field__hint`, `.field--error` with
  `.field__error`, plus `aria-invalid` and `aria-describedby`. Error state is signalled
  three ways at once — colour, a thicker stroke, and an injected `!` glyph — because
  colour alone fails for a lot of readers.
- **Use `.choice` for checkboxes and radios**, which keeps the label sentence-case and
  inline instead of the uppercase caption `label` gets by default.
- **`.panel` is the neutral container.** The five `.card` variants each carry a required
  category label, so a card is a category statement; a login form goes in a `.panel`.
- **`.appbar` + `.nav`** for chrome, `.shell--sidebar` for a sidebar layout. Current page
  is marked with `aria-current="page"`, which sets both a colour change and an underline.
- **Disabled controls need an explanation nearby**, usually a `.field__hint`. Greying a
  button without saying why is a dead end for the user.

Two constraints carry over from the document layer and are load-bearing here. The focus
ring is `--focus`, a deliberately **neutral** near-black or near-white rather than a brand
colour, so it can never be mistaken for the red error state — don't "improve" it by
tinting it. And there is **no icon font**: use inline SVG with `stroke="currentColor"` so
icons inherit their context's token, give every icon-only control an `aria-label`, and
never let an icon be the only label.

Motion is minimal on purpose. `.spinner` exists, respects `prefers-reduced-motion`, and
should always sit next to the word "Loading" — motion is not a signal everyone perceives.

## The four-part accent set

`--p-truth`, `--p-justice`, `--p-mercy`, `--p-sacrifice` are a four-colour categorical
palette, calibrated per mode so all four clear AA on the raised surface. The names come
from the book's four pillars, but the set is general-purpose: use it for chart series,
category tags, status groupings, or any four-way distinction.

Two constraints travel with it. Keep the four at equal visual weight — in book contexts
the four pillars are co-constitutive, so ranking them by size or brightness would
contradict the argument, and in general contexts an unintentionally dominant category is
just bad information design. And never let colour alone carry the meaning: mercy-green and
sacrifice-red are indistinguishable under the most common form of colour blindness, so
always label the category in text as well.

## Accessibility commitments

These are load-bearing, not preferences. The whole palette was built by measurement and
several candidate designs were cut for failing them.

- **Nothing means anything by colour alone.** Every state carries a second signal — a
  word, a glyph, a border position. The `−` and `+` glyphs the stylesheet injects into
  redlines are this, not decoration.
- **No type below weight 400, and no tracked body text.** Thin strokes and wide tracking
  are the two most reliable ways to defeat low-vision readers.
- **Never put long-form reading on pure white.** The light grounds are warm and slightly
  off-white on purpose; maximum contrast increases glare, and WCAG sets a floor, not a
  ceiling. For the same reason dark-mode body ink is not white.
- **Headings descend in order** — `h1` → `h2` → `h3`, none skipped — because the outline
  is how screen-reader users navigate.

## When the content is book material

If the document quotes *What Is Love?*, these are editorial requirements, and a
well-branded page that gets them wrong is worse than an unbranded one:

- The canonical definition appears verbatim: "God's Perfect Love is the sacred gift of
  covenant which binds truth, justice, mercy and sacrifice into life-giving communion."
  No Oxford comma in the pillar list. "sacrifice", never "sacrificial".
- Scripture is quoted from the RSV, cited as `Book Chapter:Verse · RSV`.

## Before calling a page done

Check these, because they are the failures that actually happen:

- No hard-coded hex values anywhere in the document.
- Gold appears as text only in dark mode.
- Long-form reading and redlines are never on pure white.
- Every colour-coded state also carries text or a glyph.
- Headings descend in order with none skipped.
- One variant only — no red and blue tokens in the same file.

If the user asks for a colour, weight, or effect the system doesn't have, say so and
propose the closest token rather than inventing one. The system is small on purpose; its
restraint is the house style. No shadows, no gradients, no radius above 3px. It should
feel like print.
