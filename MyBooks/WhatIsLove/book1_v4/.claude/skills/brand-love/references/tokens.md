# Love Brand — token reference

Semantic names only. Components must never reference a raw hex value; if a colour is needed that no token provides, add a token and re-check contrast across all four palettes.

## The four palettes

Root classes are two independent axes: `.love` plus one of `.love--red` / `.love--blue`, plus one of `.love--light` / `.love--dark`.

### Red · Light — `.love--red.love--light`

```css
  --surface: #f7f0e4;                 /* Page background */
  --raised: #efe4cf;                  /* Cards, callouts, stripes */
  --sunken: #e6d9c2;                  /* Wells, code, inset */
  --border: #d3bd93;                  /* Hairlines, table rules */
  --border-strong: #8f7134;           /* Informational borders (≥3:1) */
  --ink-strong: #2a0e11;              /* Headings */
  --ink: #3c1418;                     /* Body copy */
  --ink-muted: #6b5540;               /* Secondary prose */
  --ink-subtle: #7d6a52;              /* Meta, captions, folios */
  --quote: #5c4030;                   /* Quotations, scripture */
  --accent: #8a6520;                  /* Labels — TEXT-SAFE in every variant */
  --ornament: #be985c;                /* Rules and fills — NEVER text on light */
  --link: #7d2229;                    /* Hyperlinks */
  --accent-ink: #f7f0e4;              /* Text on an accent fill */
  --focus: #8a2323;                   /* Focus ring */
  --danger: #8a2323;                  /* Deletions, warnings */
  --success: #1f5238;                 /* Insertions, confirmations */
  --p-truth: #255a7a;                 /* Pillar: truth */
  --p-justice: #6b5518;               /* Pillar: justice */
  --p-mercy: #1f6045;                 /* Pillar: mercy */
  --p-sacrifice: #7d2f33;             /* Pillar: sacrifice */
```

### Red · Dark — `.love--red.love--dark`

```css
  --surface: #3a1418;                 /* Page background */
  --raised: #541e23;                  /* Cards, callouts, stripes */
  --sunken: #2a0e11;                  /* Wells, code, inset */
  --border: #7a4a3a;                  /* Hairlines, table rules */
  --border-strong: #a1704f;           /* Informational borders (≥3:1) */
  --ink-strong: #f9f2e4;              /* Headings */
  --ink: #efe4d0;                     /* Body copy */
  --ink-muted: #c9a97a;               /* Secondary prose */
  --ink-subtle: #b08f68;              /* Meta, captions, folios */
  --quote: #e2cfa8;                   /* Quotations, scripture */
  --accent: #be985c;                  /* Labels — TEXT-SAFE in every variant */
  --ornament: #be985c;                /* Rules and fills — NEVER text on light */
  --link: #e0b978;                    /* Hyperlinks */
  --accent-ink: #3a1418;              /* Text on an accent fill */
  --focus: #be985c;                   /* Focus ring */
  --danger: #e39b96;                  /* Deletions, warnings */
  --success: #9fd3a0;                 /* Insertions, confirmations */
  --p-truth: #7fb0d0;                 /* Pillar: truth */
  --p-justice: #d0b870;               /* Pillar: justice */
  --p-mercy: #8fd0aa;                 /* Pillar: mercy */
  --p-sacrifice: #d08f92;             /* Pillar: sacrifice */
```

### Blue · Light — `.love--blue.love--light`

```css
  --surface: #f0f2f7;                 /* Page background */
  --raised: #e3e8f2;                  /* Cards, callouts, stripes */
  --sunken: #d7deec;                  /* Wells, code, inset */
  --border: #b0bbd4;                  /* Hairlines, table rules */
  --border-strong: #5f6f95;           /* Informational borders (≥3:1) */
  --ink-strong: #121b33;              /* Headings */
  --ink: #1e2a47;                     /* Body copy */
  --ink-muted: #4a5470;               /* Secondary prose */
  --ink-subtle: #5a6480;              /* Meta, captions, folios */
  --quote: #3b4763;                   /* Quotations, scripture */
  --accent: #795a16;                  /* Labels — TEXT-SAFE in every variant */
  --ornament: #be985c;                /* Rules and fills — NEVER text on light */
  --link: #1f4a8f;                    /* Hyperlinks */
  --accent-ink: #f0f2f7;              /* Text on an accent fill */
  --focus: #1f4a8f;                   /* Focus ring */
  --danger: #8a2323;                  /* Deletions, warnings */
  --success: #1f5238;                 /* Insertions, confirmations */
  --p-truth: #1f4a8f;                 /* Pillar: truth */
  --p-justice: #6b5518;               /* Pillar: justice */
  --p-mercy: #1f6045;                 /* Pillar: mercy */
  --p-sacrifice: #7d2f33;             /* Pillar: sacrifice */
```

### Blue · Dark — `.love--blue.love--dark`

```css
  --surface: #16223d;                 /* Page background */
  --raised: #20305a;                  /* Cards, callouts, stripes */
  --sunken: #0f1830;                  /* Wells, code, inset */
  --border: #3c4f80;                  /* Hairlines, table rules */
  --border-strong: #6c83bb;           /* Informational borders (≥3:1) */
  --ink-strong: #f6f2e6;              /* Headings */
  --ink: #e6e2d4;                     /* Body copy */
  --ink-muted: #c4b995;               /* Secondary prose */
  --ink-subtle: #a89e7e;              /* Meta, captions, folios */
  --quote: #ddd3b8;                   /* Quotations, scripture */
  --accent: #cfa961;                  /* Labels — TEXT-SAFE in every variant */
  --ornament: #be985c;                /* Rules and fills — NEVER text on light */
  --link: #e2bd80;                    /* Hyperlinks */
  --accent-ink: #16223d;              /* Text on an accent fill */
  --focus: #cfa961;                   /* Focus ring */
  --danger: #f0a09a;                  /* Deletions, warnings */
  --success: #9fd3a0;                 /* Insertions, confirmations */
  --p-truth: #8fc0e0;                 /* Pillar: truth */
  --p-justice: #d8c07a;               /* Pillar: justice */
  --p-mercy: #8fd0aa;                 /* Pillar: mercy */
  --p-sacrifice: #eda49e;             /* Pillar: sacrifice */
```

## Measured contrast (WCAG 2.2)

Computed, not estimated. Body text reaches AAA in all four palettes; every text pair clears AA. Informational borders are tested against the 3:1 non-text threshold rather than 4.5:1.

| Pair | Token | Red light | Red dark | Blue light | Blue dark |
|---|---|---|---|---|---|
| Body text | `--ink` | 14.2 (AAA) | 12.9 (AAA) | 12.69 (AAA) | 12.17 (AAA) |
| Headings | `--ink-strong` | 15.85 (AAA) | 14.58 (AAA) | 15.24 (AAA) | 14.1 (AAA) |
| Muted prose | `--ink-muted` | 6.18 (AA) | 7.3 (AAA) | 6.71 (AA) | 8.06 (AAA) |
| Meta / captions | `--ink-subtle` | 4.57 (AA) | 5.39 (AA) | 5.25 (AA) | 5.91 (AA) |
| Accent label | `--accent` | 4.68 (AA) | 6.06 (AA) | 5.7 (AA) | 7.14 (AAA) |
| Link | `--link` | 8.69 (AAA) | 8.8 (AAA) | 7.7 (AAA) | 8.89 (AAA) |
| Quotation | `--quote` | 8.31 (AAA) | 10.61 (AAA) | 8.27 (AAA) | 10.59 (AAA) |
| Body on raised | `--ink` | 12.77 (AAA) | 10.51 (AAA) | 11.57 (AAA) | 9.92 (AAA) |
| Deletion | `--danger` | 7.11 (AAA) | 5.92 (AA) | 7.29 (AAA) | 6.25 (AA) |
| Insertion | `--success` | 7.18 (AAA) | 7.75 (AAA) | 7.36 (AAA) | 7.54 (AAA) |
| Pillar · truth | `--p-truth` | 5.91 (AA) | 5.69 (AA) | 7.02 (AAA) | 6.61 (AA) |
| Pillar · justice | `--p-justice` | 5.67 (AA) | 6.79 (AA) | 5.82 (AA) | 7.19 (AAA) |
| Pillar · mercy | `--p-mercy` | 5.92 (AA) | 7.42 (AAA) | 6.07 (AA) | 7.21 (AAA) |
| Pillar · sacrifice | `--p-sacrifice` | 7.16 (AAA) | 5.06 (AA) | 7.35 (AAA) | 6.38 (AA) |
| Informational border | `--border-strong` | 4.05 (AA lg) | 3.82 (AA lg) | 4.47 (AA lg) | 4.21 (AA lg) |

## Non-colour tokens

| Group | Tokens |
|---|---|
| Fonts | `--font-display` (Cinzel Decorative) · `--font-title` (Cinzel) · `--font-body` (Libre Baskerville) · `--font-ui` (Inter) · `--font-mono` |
| Size | `--size-2xs` .6875rem · `--size-xs` .78 · `--size-sm` .875 · `--size-md` 1 · `--size-lg` 1.125 · `--size-xl` 1.4 · `--size-2xl` 1.75 · `--size-3xl` 2.2 · `--size-4xl` 2.75 |
| Leading | `--leading-tight` 1.2 · `--leading-normal` 1.5 · `--leading-prose` 1.8 |
| Tracking | `--tracking-display` .01em · `--tracking-eyebrow` .22em · `--tracking-label` .14em |
| Space | `--space-1` .25rem through `--space-8` 4rem |
| Form | `--measure` 68ch · `--radius` 3px · `--rule` 1px · `--rule-strong` 2px · `--focus-width` · `--focus-offset` |

## Font rules

`--font-display` is for `h1` and `h2` only, never below 1.4rem and never for body copy —
Cinzel Decorative is a display face and becomes illegible small. `--font-title` handles
`h3`–`h5`, eyebrows, drop caps, and stat figures. `--font-body` carries all prose.
`--font-ui` is for functional text — labels, meta, table headers, badges — things read
at a glance rather than read through.

Never set a weight below 400 and never track body text. Thin strokes and wide tracking
are the two most reliable ways to defeat low-vision readers, and both were the reason
earlier candidate designs were cut from this project.
