# Love Brand — application patterns

The product layer. Everything here uses the same tokens as the document layer; nothing
introduces a new colour, shadow, or radius.

Contents:

1. [Buttons](#1-buttons)
2. [Fields and validation](#2-fields-and-validation)
3. [Panels](#3-panels)
4. [App shell and navigation](#4-app-shell-and-navigation)
5. [Lockup and avatar](#5-lockup-and-avatar)
6. [Alerts](#6-alerts)
7. [Tabs, dialogs, menus](#7-tabs-dialogs-menus)
8. [Empty and loading states](#8-empty-and-loading-states)
9. [Data tables](#9-data-tables)
10. [Icons](#10-icons)
11. [Tokens added by this layer](#11-tokens-added-by-this-layer)
12. [Screen checklist](#12-screen-checklist)

---

## 1. Buttons

```html
<div class="btn-row">
  <button class="btn btn--primary">Save changes</button>
  <button class="btn">Cancel</button>
  <button class="btn btn--ghost btn--sm">Reset</button>
  <button class="btn btn--danger">Delete account</button>
</div>

<button class="btn btn--primary btn--block" disabled>Sign in</button>
<p class="field__hint">Enter your email and password to continue.</p>
```

One `--primary` per view. If two actions both look primary, neither is.

`.is-on` is **not** a primary style — it pairs with `aria-pressed` on toggles:

```html
<button class="btn is-on" aria-pressed="true">Dark mode</button>
```

Pending state uses `aria-busy`, which injects a `◌` glyph:

```html
<button class="btn btn--primary" aria-busy="true" disabled>Saving</button>
```

A disabled button that doesn't say why it's disabled is a dead end. Put the reason in an
adjacent `.field__hint` — this is the same "never colour alone" principle applied to
state rather than category.

## 2. Fields and validation

```html
<div class="field">
  <label class="field__label" for="email">Email <span class="req">*</span></label>
  <input id="email" type="email" required aria-describedby="email-hint">
  <p class="field__hint" id="email-hint">We'll never share this.</p>
</div>

<div class="field field--error">
  <label class="field__label" for="pw">Password</label>
  <input id="pw" type="password" aria-invalid="true" aria-describedby="pw-err">
  <p class="field__error" id="pw-err">Must be at least 12 characters.</p>
</div>

<label class="choice">
  <input type="checkbox"> Remember me on this device
</label>

<div class="field-row field-row--2">
  <div class="field"> … </div>
  <div class="field"> … </div>
</div>
```

The error state carries three simultaneous signals — the border turns `--danger`, the
stroke thickens to `--rule-strong`, and CSS injects `!` before the message. Any one of
those alone would fail somebody. `aria-invalid="true"` triggers the border styling on its
own, so the visual and the accessible state can't drift apart.

Use `.choice` for every checkbox and radio. The bare `label` element is styled as an
uppercase field caption, which is wrong for a sentence beside a checkbox.

## 3. Panels

```html
<div class="panel panel--form">
  <div class="panel__header">
    <h2 class="panel__title">Sign in</h2>
    <a href="#" class="citation">Need help?</a>
  </div>
  …
</div>
```

`.panel` is neutral — no colour bar, no category. Use it for forms, settings groups,
sidebars, any box that is structure rather than editorial classification. `.panel--form`
caps width at `--measure-form` (26rem) and centres it; `--measure` (68ch) is a prose
measure and roughly twice too wide for a form.

Reach for `.card` only when the box genuinely has a category, since each variant's label
is part of its meaning.

## 4. App shell and navigation

```html
<header class="appbar">
  <div class="appbar__inner">
    <a class="lockup" href="/"> … </a>
    <nav><ul class="nav">
      <li><a href="/" aria-current="page">Dashboard</a></li>
      <li><a href="/reports">Reports</a></li>
    </ul></nav>
    <span class="appbar__spacer"></span>
    <div class="avatar">PS</div>
  </div>
</header>

<div class="shell shell--sidebar">
  <aside class="sidebar"><nav><ul class="nav"> … </ul></nav></aside>
  <main> … </main>
</div>

<ol class="breadcrumb"><li><a href="/">Home</a></li><li>Settings</li></ol>
```

`aria-current="page"` drives the current-item treatment, so the accessible state and the
visual state are the same thing. The underline uses `--border-strong` rather than
`--ornament`: the marker carries information, and gold cannot reach the 3:1 non-text
threshold on a light ground.

The appbar is sticky at `--z-sticky`. There is no shadow under it and it doesn't need one
— the `--border` hairline separates it from content perfectly well, which was tested.

## 5. Lockup and avatar

```html
<a class="lockup" href="/">
  <span class="lockup__mark" aria-hidden="true">L</span>
  <span class="lockup__word">Lumen<span class="lockup__sub">Analytics</span></span>
</a>

<a class="lockup lockup--lg" href="/"> … </a>   <!-- hero scale, uses --font-display -->
```

The mark's letter is text, so it takes `--accent`, never `--ornament` — this is the gold
rule showing up where it's easiest to break. At header scale the wordmark uses
`--font-title`, because Cinzel Decorative is illegible below 1.4rem; `--font-display`
only appears in `.lockup--lg`.

```html
<div class="avatar avatar--lg">PS</div>
<div class="avatar"><img src="…" alt="Patrick Steil"></div>
```

Avatars are square at `--radius`, not round — the 3px cap is deliberate and a round
avatar would be the one exception that unravels it. They are never tinted per user;
identity must not depend on colour perception.

## 6. Alerts

```html
<div class="alert" role="status">
  <div><div class="alert__title">Heads up</div>Your trial ends in six days.</div>
</div>
<div class="alert alert--success" role="status"> … </div>
<div class="alert alert--warn" role="status"> … </div>
<div class="alert alert--danger" role="alert"> … </div>
```

Each variant injects its own glyph (`i` `✓` `!` `×`) alongside the colour. Use
`role="alert"` only for genuine errors — it interrupts screen readers — and `role="status"`
for everything else.

## 7. Tabs, dialogs, menus

Tabs need more than a styled strip. Copied without the wiring below, a tab strip puts every
tab in the tab order, connects nothing to its panel, and does nothing on arrow keys.

```html
<ul class="tabs" role="tablist">
  <li><button class="btn--bare" role="tab" id="t-1" aria-controls="p-1"
              aria-selected="true"  tabindex="0">Giving history</button></li>
  <li><button class="btn--bare" role="tab" id="t-2" aria-controls="p-2"
              aria-selected="false" tabindex="-1">Notes</button></li>
</ul>
<div class="tabpanel" id="p-1" role="tabpanel" aria-labelledby="t-1" tabindex="0"> … </div>
<div class="tabpanel" id="p-2" role="tabpanel" aria-labelledby="t-2" tabindex="0" hidden> … </div>
```

Three things the markup alone can't give you, all needed: `aria-selected` moves with the
selection, `tabindex` roves so the strip is a single tab stop, and Arrow/Home/End move
between tabs. Without the roving tabindex a ten-tab strip costs a keyboard user ten
presses to get past.

```html
<dialog id="confirm">
  <h2 class="panel__title">Delete this donor?</h2>
  <p>This cannot be undone.</p>
  <div class="btn-row">
    <button class="btn" autofocus>Cancel</button>
    <button class="btn btn--danger">Delete permanently</button>
  </div>
</dialog>
```

Use the native `<dialog>` — it gives focus trapping, `Esc`, and an inert background for
free. Two rules: put `autofocus` on the **safe** control, never the destructive one; and
listen for the `close` event rather than the Cancel click, because `Esc` bypasses the
button entirely.

`.menu` is an in-flow list. To use it as a dropdown, wrap the trigger and the menu:

```html
<div class="menu-anchor">
  <button class="btn btn--ghost btn--icon btn--sm" aria-haspopup="menu"
          aria-expanded="false" aria-label="Actions for Adaeze Nwosu"> … </button>
  <ul class="menu menu--pop" hidden> … </ul>
</div>
```

`z-index` does nothing without positioning, which is what `.menu--pop` supplies. You still
write the behaviour: Escape to close, arrows between items, close on outside click, and
focus returned to the trigger.

## 8. Empty and loading states

```html
<div class="empty">
  <div class="empty__title">No reports yet</div>
  <p>Reports appear here once your first sync completes.</p>
  <button class="btn btn--primary">Run a sync</button>
</div>

<p><span class="spinner" aria-hidden="true"></span> Loading reports…</p>
```

Always pair the spinner with the word. Motion isn't perceived by everyone, and it's
suppressed entirely under `prefers-reduced-motion`, where the spinner becomes a static
ring — if the text isn't there, nothing communicates.

An empty state should say what will fill it and offer the action that does so.

## 9. Data tables

```html
<table class="table--data table--sticky">
  <thead><tr>
    <th aria-sort="descending">Date</th><th>Account</th><th class="num">Amount</th>
  </tr></thead>
  <tbody> … </tbody>
</table>
```

`aria-sort` drives the ▲/▼ indicator, so the sort direction is announced as well as
drawn. `.num` on every numeric column *including its header*, or the column edges won't
align.

## 10. Icons

There is no icon font and no icon set. Use inline SVG:

```html
<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
  <path d="M5 12h14M13 6l6 6-6 6"/>
</svg>
<button class="btn btn--ghost" aria-label="Close">
  <svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
</button>
```

`.icon` sets `stroke: currentColor`, so an icon inherits whatever token its context uses
and stays correct in all four palettes automatically. Mark decorative icons
`aria-hidden="true"`, and give icon-only controls an `aria-label` — an icon is never the
only label.

## 10b. Small utilities

```html
<div class="center"> … </div>          <!-- also centres a .btn-row inside it -->
<div class="or">or</div>                <!-- labelled divider between two paths -->
<span class="visually-hidden">Select Adaeze Nwosu</span>
```

`.visually-hidden` is load-bearing, not cosmetic: it is how a selection checkbox, an
icon-only control, or an inert nav item gets a text alternative.

`.btn` works on an `<a>` as well as a `<button>` — use the anchor when the action is a
navigation ("Create an account") and the button when it acts on the current page. That is
intended, not incidental; the element should reflect what actually happens.

The utility list is short on purpose. If an element needs three utilities, a component is
missing — add the component instead.

## 10c. Focus management

`--focus` covers what focus *looks* like. This covers where it *goes*, which is what
actually breaks applications. Every item below is a failure that happens in practice.

- **After a client-side view change**, focus stays on a button that no longer exists and
  falls to `<body>`. Give the new view's heading `tabindex="-1"` and
  `data-focus-target`, and focus it. The stylesheet suppresses the ring on
  `[data-focus-target]:focus` while leaving `:focus-visible` intact, so a programmatic
  focus doesn't draw a ring but a real keyboard focus still does.
- **After re-rendering a list** — sort, filter, paginate, toggle a checkbox — the element
  focus was on is destroyed. Re-find and re-focus the equivalent control afterwards. This
  is the single most common way a JS-rendered table becomes keyboard-unusable.
- **After a destructive action** removes the element that triggered it, `<dialog>`'s
  automatic focus restoration has nowhere to return to. Name an explicit fallback — the
  table heading, or the row that took its place.
- **Announce changes that aren't focus changes.** A result count that updates as someone
  types should sit in `aria-live="polite"`; otherwise the page silently rearranges.

## 10d. Alerts and live regions

Put the live region in the page *once*, outside whatever gets re-rendered, and change only
its contents:

```html
<div class="flash" role="status" aria-live="polite" aria-atomic="true"></div>
```

Rendering the alert as part of a view template is the obvious implementation and it is
broken: a live region created at the same instant its content appears is frequently not
announced. The alert looks right and says nothing.

There is no toast component, deliberately. Toasts are transient, easy to miss, and hard to
make accessible; inline alerts suit a system that means to feel like print. There is no
drawer either, for the same kind of reason — a drawer is a `<dialog>` on its side, with all
the focus trapping and scroll locking that implies, and doing it badly is worse than a
full-screen form.

## 11. Tokens added by this layer

| Token | Purpose |
|---|---|
| `--focus` | Focus ring. **Neutral by design** — near-black on light, near-cream on dark — so it can never be confused with the red error state. Don't tint it. |
| `--accent-hover` | Pressed/hover state for accent fills and accent text |
| `--ink-disabled` | Text inside a disabled control (≥4.5:1 on `--sunken` in all four palettes) |
| `--danger-ink` / `--success-ink` | Text on a danger or success fill |
| `--info` / `--warn` | Alert states, reusing verified palette colours |
| `--measure-form` | 26rem — the narrow column for forms and auth panels |
| `--control-h` / `--control-h-sm` | 2.5rem / 2rem control heights |
| `--z-sticky` / `--z-dropdown` | 100 / 200. There is no modal or toast rung — native `<dialog>` uses the browser top layer, and there is no toast. |
| `--appbar-h` | 3.5rem. Sticky table headers offset by this so they don't slide under the appbar. |
| `--danger-hover` | Pressed state for danger fills |

Every one of these was contrast-checked across all four palettes: text pairs against
4.5:1, and focus rings, button fills, and field borders against the 3:1 non-text
threshold that actually applies to them.

## 12. Screen checklist

Beyond the document checklist in SKILL.md:

- Exactly one `.btn--primary` per view.
- `.is-on` used only with `aria-pressed`.
- Every input inside a `.field`, every error wired with `aria-invalid` +
  `aria-describedby`.
- Every checkbox and radio **in a form** in a `.choice`. Selection checkboxes in a data
  table are the exception: they take a `.visually-hidden` label instead, since they have no
  visible text.
- Every disabled control has an adjacent explanation.
- Current nav item marked with `aria-current="page"`, not a hand-applied class.
- Icon-only controls have `aria-label`; decorative icons have `aria-hidden`.
- Spinners sit beside the word "Loading".
- Focus ring left neutral, not tinted to match the brand.
- Focus explicitly moved after every view change and re-render.
- One persistent live region for alerts, outside the re-rendered view.
- Tabs have `aria-controls`, roving `tabindex`, and arrow-key handling.
- Destructive dialogs `autofocus` the safe control.
- Navigation actions use `<a class="btn">`, page actions use `<button class="btn">`.

---

## 13. Data-table screens

The list view is where most of the product layer meets at once.

```html
<div class="toolbar">
  <div class="field field--inline toolbar__grow">
    <label class="field__label" for="q">Search</label>
    <input id="q" type="search" style="width:100%">
    <p class="field__hint">Filters as you type.</p>
  </div>
  <div class="field field--inline">
    <label class="field__label" for="status">Status</label>
    <select id="status"> … </select>
  </div>
  <div class="toolbar__end"><button class="btn btn--primary">Add donor</button></div>
</div>

<div class="bulkbar" hidden>3 selected
  <button class="btn btn--sm btn--danger">Delete selected</button></div>

<div class="table-scroll">
  <table class="table--data">
    <thead><tr>
      <th class="col-select"><input type="checkbox">
        <span class="visually-hidden">Select all</span></th>
      <th aria-sort="ascending"><button class="btn--bare">Name</button></th>
      <th class="num"><button class="btn--bare">Last gift</button></th>
    </tr></thead>
    <tbody><tr>
      <td class="col-select"><input type="checkbox">
        <span class="visually-hidden">Select Adaeze Nwosu</span></td>
      <td><button class="btn--bare">Adaeze Nwosu</button></td>
      <td class="num">$250.00</td>
    </tr></tbody>
  </table>
</div>

<p class="meta" aria-live="polite">Showing 1–6 of 12</p>
<div class="pagination">
  <button class="btn btn--sm" disabled>Previous</button>
  <span>Page 1 of 2</span>
  <button class="btn btn--sm">Next</button>
  <span class="pagination__spacer"></span>
</div>
<p class="field__hint">Previous is disabled: you are on the first page.</p>
```

Points worth holding onto:

- **Sort headers are `<button class="btn--bare">`**, not a clickable `<th>`. `aria-sort` on
  the `<th>` draws the ▲/▼ and announces the direction, so one attribute does both jobs.
- **`.btn--bare` exists because not every `<button>` is a Button.** Sort headers, row
  links, tabs, and menu items are semantically buttons and visually not. Reach for it
  instead of hand-writing a reset.
- **Selection checkboxes take `.visually-hidden` labels**, not `.choice` — they have no
  visible text, and the row's meaning has to reach a screen reader somehow.
- **The indeterminate state of a select-all checkbox is DOM-only.** It cannot be set in
  HTML, so it has to be re-applied in JS after every re-render.
- **The count line is a live region**, or filtering silently rearranges the page.
- **Disabled pagination explains itself** in a `.field__hint`. That rule started life in
  forms and generalises to every disabled control in the system.
