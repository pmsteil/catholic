#!/usr/bin/env python3
"""Build a self-contained, offline, per-block-commentable HTML review document.

    python3 build_review.py chapter_15.md -o review.html \
        --title "Counterfeit Love" --brand-css /path/to/love-brand.css

Everything is inlined: brand tokens, the annotation layer, the content, the script.
The result is one file that works with no network and no server.
"""
import argparse, datetime, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')

# ── sentence splitting ────────────────────────────────────────────────────
_ABBR = ('mr','mrs','ms','dr','st','ss','fr','rev','msgr','prof','sr','jr','vs',
         'etc','ie','eg','cf','no','vol','ch','al','ff','ca')

def split_sentences(t):
    """Split prose into sentences conservatively. Two guards matter more than
    cleverness: never split after a known abbreviation or an initial, and never
    split inside markdown emphasis — a sentence with unbalanced ** would render
    as broken markup."""
    parts, start = [], 0
    # Closers include markdown emphasis: a sentence ending "…communion.**" has
    # its full stop separated from the space by the closing asterisks, and a
    # boundary that only looks for quotes will silently merge the next sentences
    # into it.
    CLOSE = r'["\'\u2019\u201d)\]*_`]*'
    for m in re.finditer(r'[.!?…]' + CLOSE + r'\s+', t):
        head = t[start:m.end()]
        prev = re.search(r'([A-Za-z.]+)[.!?…]' + CLOSE + r'\s+$', head)
        if prev:
            w = prev.group(1).lower().replace('.', '')
            if w in _ABBR or len(w) == 1:      # "Mr." / "C. S. Lewis"
                continue
        if head.count('**') % 2 or head.count('`') % 2:
            continue
        parts.append(head)
        start = m.end()
    tail = t[start:]
    if tail.strip():
        parts.append(tail)
    return [p for p in (x.strip() for x in parts) if p] or [t]

# ── markdown → blocks ──────────────────────────────────────────────────────
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'`([^`]+?)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t.replace('---', '—')

def parse(src):
    """Split source markdown into blocks. Every block that carries prose becomes
    a comment target; headings and rules do not."""
    lines, blocks, path, pid, i = src.split('\n'), [], [], 0, 0

    def target(kind, **kw):
        nonlocal pid
        pid += 1
        blocks.append(dict(kind=kind, id=f'p{pid:03d}', path=' › '.join(path), **kw))

    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1; continue

        # Raw <div> blocks. Book sources carry these for the print pipeline. Any
        # inline style="…" on them is dropped: a document is branded by its
        # stylesheet, and hard-coded colours from another palette would ship a
        # foreign theme into the middle of the page.
        if s.startswith('<div'):
            kind = 'epigraph' if 'blockquote' in s else 'rawdiv'
            buf = []; i += 1
            while i < len(lines) and '</div>' not in lines[i]:
                buf.append(lines[i]); i += 1
            i += 1
            text = '\n'.join(buf).strip()
            # content may trail on the opening line after the tag
            lead = re.sub(r'^<div[^>]*>', '', s).strip()
            if lead: text = (lead + '\n' + text).strip()
            cite = ''
            m = re.search(r'\\hfill\\small\s*—\s*(.+)', text)
            if m:
                cite = m.group(1).strip(); text = text[:m.start()].strip()
            text = re.sub(r'</div>\s*$', '', text).strip().strip('"').strip()
            if kind == 'epigraph':
                h = f'<p>{inline(text)}</p>' + (f'<cite>{html.escape(cite)}</cite>' if cite else '')
                target('epigraph', html=f'<blockquote class="scripture--bar">{h}</blockquote>',
                       plain=text + (f' — {cite}' if cite else ''))
            else:
                paras = ''.join(f'<p>{inline(x.strip())}</p>'
                                for x in text.split('\n') if x.strip())
                target('callout', html=f'<div class="callout">{paras}</div>', plain=text)
            continue

        if re.fullmatch(r'-{3,}|\*{3,}', s):
            blocks.append(dict(kind='hr')); i += 1; continue

        if s.startswith('```'):
            fence = s[:3]; buf = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                buf.append(lines[i]); i += 1
            i += 1
            code = html.escape('\n'.join(buf))
            target('code', html=f'<pre><code>{code}</code></pre>',
                   plain='\n'.join(buf)[:200])
            continue

        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            path = [] if lvl <= 1 else (path[:lvl-2] + [txt])
            # A heading is a comment target like anything else — a reviewer has as
            # much to say about a section title as about the prose under it. Its
            # breadcrumb is the path *above* it, not including itself.
            blocks.append(dict(kind='heading', level=lvl, text=txt,
                               plain=txt, path=' › '.join(path[:-1])))
            i += 1; continue

        if s.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i += 1
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
            if len(cells) >= 2 and set(cells[1][0].replace(' ', '')) <= set('-:'):
                head, body = cells[0], cells[2:]
            else:
                head, body = None, cells
            target('table', head=head, body=body,
                   plain=' | '.join(head or (body[0] if body else [])) + ' …')
            continue

        if re.match(r'^([-*+]|\d+\.)\s', s):
            ordered = bool(re.match(r'^\d+\.', s)); items = []
            while i < len(lines) and re.match(r'^([-*+]|\d+\.)\s', lines[i].strip()):
                items.append(re.sub(r'^([-*+]|\d+\.)\s+', '', lines[i].strip())); i += 1
            tag = 'ol' if ordered else 'ul'
            target('list', html=f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>',
                   plain=' • '.join(items))
            continue

        # paragraph: consume until blank line
        buf = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r'^(#{1,6}\s|\||```|[-*+]\s|\d+\.\s|<div|-{3,}$)', lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        txt = ' '.join(buf)
        target('para', sentences=split_sentences(txt), plain=txt)
    return blocks

# ── blocks → HTML ──────────────────────────────────────────────────────────
def attrs(b, ref):
    return (f'id="{b["id"]}" data-ref="{ref}" '
            f'data-path="{html.escape(b.get("path",""), quote=True)}" '
            f'data-plain="{html.escape(b.get("plain","")[:400], quote=True)}"')

def slot(tid):
    """Every target owns a named, empty container. The script finds a target's
    note by id alone, so blocks, sentences, rows and cells all share one code
    path instead of four."""
    return f'<div class="note-slot" data-for="{tid}"></div>'

def question_style(root_class):
    """A reviewer's question from Claude has to look unmistakably different from
    the surrounding prose — the whole point is that the reader spots it as
    something temporary that wants an answer, not more chapter text. The
    cheapest way to guarantee that against an unknown brand stylesheet is to
    reuse the brand's OWN opposite-mode palette: nest a wrapper carrying the
    same colour ramp but the inverted light/dark class, and every token the
    question box draws from (--surface, --ink, --accent, …) resolves to the
    other mode's values for that subtree only, because these are plain class
    selectors, not a :root-only rule. If no brand was supplied there is no
    other mode to borrow, so the fallback is a literal bright highlight."""
    tokens = root_class.split()
    ramp = next((t for t in tokens if t in ('love--red', 'love--blue')), None)
    mode = 'love--light' if 'love--light' in tokens else ('love--dark' if 'love--dark' in tokens else None)
    if not ramp or not mode:
        return None, True   # fallback: no dark/light pair to invert
    inverted = 'love--dark' if mode == 'love--light' else 'love--light'
    return f'love {ramp} {inverted}', False

def qblock(qs, invert_classes, fallback):
    """Render zero or more reviewer-question boxes for one target. A target can
    carry more than one open question, so this always returns a list to join."""
    out = []
    for q in qs:
        qid = f'q-{q["key"]}'
        cls = 'qblk qblk--fallback' if fallback else f'qblk {invert_classes}'
        out.append(
            f'<div class="{cls}" id="{qid}" data-qkey="{html.escape(q["key"], quote=True)}" '
            f'data-qanchor="{html.escape(q.get("anchor",""), quote=True)}">'
            f'<p class="qblk__label">Question from your reviewer</p>'
            f'<div class="qblk__text">{inline(q["text"])}</div>'
            f'<label class="qblk__alabel" for="ta-{qid}">Your answer</label>'
            f'<textarea id="ta-{qid}" class="qblk__answer" rows="2" '
            f'placeholder="Type your answer — it saves as you go, no button to press."></textarea>'
            f'</div>')
    return ''.join(out)

def render(blocks, doc_title=None, questions=None, invert_classes=None, fallback=False):
    """Content is wrapped in nested <section> elements, one per h2 and h3.

    This is what makes sticky headings behave. A sticky element is pinned only
    while its *containing block* is on screen; if every heading shares one parent,
    they all pin at the same offset and stack invisibly on top of each other
    instead of handing over. Sectioning gives each heading a scope to end in — and
    it is better document structure regardless."""
    out, toc = [], []
    depth = []   # open <section> levels
    seen_anchors, hcount = {}, [0]
    questions = dict(questions or {})   # anchor -> [ {key, text, anchor}, … ]; popped as matched
    def qs_for(anchor):
        return questions.pop(anchor, [])

    def qtitle(q):
        t = q['text'].strip()
        return t if len(t) <= 44 else t[:44].rstrip() + '…'

    def render_qs(qs, level):
        """Render a group of question boxes AND give each one a line in the
        section nav, at the point in the document where it actually sits —
        not off in a separate panel. The nav entry carries the SAME
        opposite-mode (or fallback-highlight) class as the box itself, so the
        one thing a reviewer needs to know from the sidebar alone — "there is
        something here that needs me, not just more chapter" — reads the same
        way in both places instead of looking like an ordinary section link."""
        if not qs:
            return ''
        qcls = 'qblk--fallback' if fallback else (invert_classes or '')
        for q in qs:
            toc.append((level, f'q-{q["key"]}', qtitle(q), 'question', qcls))
        return qblock(qs, invert_classes, fallback)

    def close_to(level):
        while depth and depth[-1] >= level:
            out.append('</section>'); depth.pop()

    def anchor_for(txt):
        """The anchor doubles as the heading's target id, so it has to be unique.
        Truncating a slug to 40 characters collides more often than it looks —
        two subsections opening with the same six words is normal in a book — and
        a collision would silently merge two headings' notes into one."""
        base = 'sec-' + (re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')[:40] or 'x')
        n = seen_anchors.get(base, 0) + 1
        seen_anchors[base] = n
        return base if n == 1 else f'{base}-{n}'

    for b in blocks:
        k = b['kind']
        if k == 'hr':
            out.append('<hr>'); continue
        if k == 'heading':
            lvl, txt = b['level'], b['text']
            # The shell already prints the document title above the body, as its
            # own editable target. Emitting the source's `# ` line again would
            # show the title twice, one under the other.
            if lvl == 1 and doc_title is not None and txt == doc_title:
                continue
            b['id'] = anchor_for(txt)
            hcount[0] += 1
            href = '§' + str(hcount[0])
            if lvl in (2, 3):
                close_to(lvl)
                out.append(f'<section class="sec sec--{lvl}">')
                depth.append(lvl)
                toc.append((lvl, b['id'], txt, 'heading', ''))
            out.append(
                f'<h{lvl} class="hblk" {attrs(b, href)}>'
                f'<span class="hblk__text">{inline(txt)}</span>'
                f'<button class="btn btn--sm btn--icon hblk__add" type="button" '
                f'title="Suggest an edit to this heading" '
                f'aria-label="Suggest an edit to the heading {html.escape(txt, quote=True)}">✎</button>'
                f'</h{lvl}>')
            out.append(f'<div class="blk__notes">{slot(b["id"])}</div>')
            out.append(render_qs(qs_for(href), min(lvl + 1, 3)))
            continue

        ref = '¶' + b['id'][1:]
        if k == 'table':
            head, rows = b['head'], b['body']
            ncols = len(head or (rows[0] if rows else [])) + 1
            t = [f'<div class="blk blk--table" {attrs(b, ref)}>',
                 f'<div class="blk__head"><span class="blk__ref">{ref} · table</span>'
                 f'<button class="btn btn--ghost btn--sm blk__add" type="button" '
                 f'aria-label="Comment on the whole table {ref}">✎ Comment on whole table</button></div>',
                 f'<div class="blk__notes">{slot(b["id"])}</div>',
                 '<div class="table-scroll"><table class="table--rows">']
            if head:
                t.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) +
                         '<th class="col-act"><span class="visually-hidden">Comment</span></th></tr></thead>')
            t.append('<tbody>')
            for ri, r in enumerate(rows, 1):
                rplain = ' | '.join(r)
                t.append(f'<tr class="rblk" id="{b["id"]}r{ri}" data-ref="{ref} r{ri}" '
                         f'data-path="{html.escape(b.get("path",""), quote=True)}" '
                         f'data-plain="{html.escape(rplain[:400], quote=True)}">')
                for ci, c in enumerate(r, 1):
                    cid = f'{b["id"]}r{ri}c{ci}'
                    colname = (head[ci-1] if head and ci <= len(head) else f'column {ci}')
                    t.append(
                        f'<td class="cblk" id="{cid}" data-ref="{ref} r{ri}c{ci}" '
                        f'data-col="{html.escape(colname, quote=True)}" '
                        f'data-path="{html.escape(b.get("path",""), quote=True)}" '
                        f'data-plain="{html.escape(c[:400], quote=True)}">'
                        f'<span class="cell__text">{inline(c)}</span>'
                        f'<button class="btn btn--sm btn--icon cell__add" type="button" '
                        f'title="Comment on this cell" '
                        f'aria-label="Comment on row {ri}, {html.escape(colname, quote=True)}">✎</button>'
                        f'{slot(cid)}</td>')
                t.append(f'<td class="col-act"><button class="btn btn--ghost btn--sm btn--icon row__add" '
                         f'type="button" title="Comment on this whole row" '
                         f'aria-label="Comment on the whole of row {ri}: '
                         f'{html.escape(rplain[:70], quote=True)}">✎</button></td></tr>')
                t.append(f'<tr class="note-row" hidden><td colspan="{ncols}">'
                         f'{slot(b["id"] + "r" + str(ri))}</td></tr>')
                # A question can be asked of the whole row or of one cell in it;
                # either way it needs the table's full width to read properly, so
                # it renders as its own row rather than squeezed into a <td>.
                rowqs = qs_for(f'{ref} r{ri}')
                for ci in range(1, len(r) + 1):
                    rowqs += qs_for(f'{ref} r{ri}c{ci}')
                if rowqs:
                    t.append(f'<tr class="qrow"><td colspan="{ncols}">'
                             f'{render_qs(rowqs, min((depth[-1] if depth else 2), 3))}</td></tr>')
            t.append('</tbody></table></div></div>')
            out.append(''.join(t))
            out.append(render_qs(qs_for(ref), min((depth[-1] if depth else 2), 3)))  # whole-table question
            continue

        opening = html.escape(b.get('plain','')[:60], quote=True)
        blockqs = qs_for(ref)
        if k == 'para':
            sents, spans, slots = b['sentences'], [], [slot(b['id'])]
            for si, sent in enumerate(sents, 1):
                sid = f'{b["id"]}s{si}'
                spans.append(
                    f'<span class="sent" id="{sid}" tabindex="-1" data-ref="{ref}·s{si}" '
                    f'data-path="{html.escape(b.get("path",""), quote=True)}" '
                    f'data-plain="{html.escape(sent[:400], quote=True)}" '
                    f'title="Click to suggest an edit to this sentence">{inline(sent)}</span>')
                slots.append(slot(sid))
                # A question about one sentence still needs the paragraph's full
                # measure to read comfortably, so it surfaces after the whole
                # paragraph rather than shoehorned between two sentence spans.
                blockqs += qs_for(f'{ref}·s{si}')
            inner = f'<p>{" ".join(spans)}</p>'
        else:
            inner, slots = b['html'], [slot(b['id'])]
        out.append(
            f'<div class="blk" {attrs(b, ref)}><div class="blk__body">{inner}</div>'
            f'<button class="btn btn--sm btn--icon blk__add" type="button" '
            f'title="Suggest an edit to the whole of {ref}" '
            f'aria-label="Suggest an edit to the whole of {ref}: {opening}">✎</button>'
            f'<div class="blk__notes">{"".join(slots)}</div></div>')
        out.append(render_qs(blockqs, min((depth[-1] if depth else 2), 3)))
    close_to(2)
    if questions:
        # Anything left didn't match a rendered target — a typo'd anchor, or one
        # written against a block that got cut. Surfacing it (rather than
        # dropping it) means a wrong anchor fails loudly instead of silently
        # losing the question; print it too so the build log catches it early.
        leftover = [q for qs in questions.values() for q in qs]
        print(f'warning: {len(leftover)} question(s) had no matching anchor: '
              + ', '.join(q.get('anchor','?') for q in leftover), file=sys.stderr)
        out.append('<div class="qblk-orphans">')
        out.append(render_qs(leftover, 2))
        out.append('</div>')
    return '\n'.join(out), toc

# ── assembly ───────────────────────────────────────────────────────────────
FONT_LINKS = """
<!-- Progressive fonts: non-blocking. Online they arrive and swap in; offline the
     request fails silently, media stays "print", and the local stacks are used. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" media="print" onload="this.media='all'" href="__FONTS__">
<noscript><link rel="stylesheet" href="__FONTS__"></noscript>
"""

def read(p):
    with open(p) as f: return f.read()

def build(a):
    src = read(a.input)
    blocks = parse(src)
    title = a.title or next((b['text'] for b in blocks if b['kind'] == 'heading'
                             and b['level'] == 1), os.path.basename(a.input))

    brand_css, root = '', a.root_class
    if a.brand_css and os.path.exists(a.brand_css):
        brand_css = read(a.brand_css)
    else:
        brand_css = read(os.path.join(ASSETS, 'fallback-tokens.css'))
        root = 'rv'
        print('note: no --brand-css supplied; using neutral fallback tokens', file=sys.stderr)

    # Questions Claude wants Patrick to answer in this pass, keyed by the exact
    # target ref they belong to (¶042, ¶042·s3, ¶042 r3, ¶042 r3c2, or §N for a
    # heading) — see question_style() for how they're styled against the brand.
    qmap = {}
    if a.questions and os.path.exists(a.questions):
        with open(a.questions) as f:
            qlist = json.load(f)
        for q in qlist:
            qmap.setdefault(q['anchor'], []).append(q)
    invert_classes, qfallback = question_style(root)

    body, toc = render(blocks, doc_title=title, questions=qmap,
                       invert_classes=invert_classes, fallback=qfallback)

    fonts = FONT_LINKS.replace('__FONTS__', a.fonts) if a.fonts else ''
    def toc_item(entry):
        l, anc, t, kind, qcls = entry
        if kind == 'question':
            # Inline, at its real position among the section links — not a
            # separate panel — and carrying the box's own highlight class, so
            # the same "this needs you" signal reads in the nav as it does in
            # the body.
            return (f'<li class="toc-l{l} toc-question {qcls}">'
                    f'<a href="#{anc}">{html.escape(t)}</a></li>')
        return f'<li class="toc-l{l}"><a href="#{anc}">{html.escape(t)}</a></li>'
    tochtml = ''.join(toc_item(e) for e in toc)

    # When the document was built. A review file outlives the moment it was made
    # and the source keeps moving underneath it, so the reader needs to be able to
    # see at a glance whether what they are marking up is still current.
    #
    # Recorded as an instant in UTC, never as the build machine's wall clock: the
    # file is often built somewhere other than where it is read — a container in
    # UTC, a CI runner, someone else's laptop — and a bare "12:35" from that
    # machine is simply the wrong time to the person reading it. review.js
    # reformats this into the reader's own timezone on load. The text inside
    # <time> is only the no-JS fallback, so it says UTC out loud rather than
    # quietly showing a time five hours off.
    stamp = datetime.datetime.now(datetime.timezone.utc)
    generated_iso = stamp.isoformat(timespec='seconds')
    fallback = '{d} {m} {y}, {t} UTC'.format(d=stamp.day, m=stamp.strftime('%B'),
                                             y=stamp.year, t=stamp.strftime('%H:%M'))
    colophon = (f'Generated <time datetime="{html.escape(generated_iso, quote=True)}">'
                f'{html.escape(fallback)}</time>')

    shell = read(os.path.join(ASSETS, 'shell.html'))
    page = f"""<!DOCTYPE html>
<html lang="en" class="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Review</title>
{fonts}<style>
{brand_css}

{read(os.path.join(ASSETS, 'review.css'))}
</style>
</head>
{shell.replace('__TITLE__', html.escape(title)).replace('__SUBTITLE__', html.escape(a.subtitle or ''))
      .replace('__EYEBROW__', html.escape(a.eyebrow or '')).replace('__TOC__', tochtml)
      .replace('__COLOPHON__', colophon).replace('__BODY__', body)}
<script>
var REVIEW_KEY = {json.dumps(a.key or ('review-' + re.sub(r'[^a-z0-9]+','-',title.lower())[:40]))};
var REVIEW_TITLE = {json.dumps(title)};
var REVIEW_SOURCE = {json.dumps(a.source or os.path.basename(a.input))};
var REVIEW_LABEL = {json.dumps(a.label or a.eyebrow or a.subtitle or '')};
var REVIEW_GENERATOR = {json.dumps(a.generator or '')};
var REVIEW_GENERATED = {json.dumps(generated_iso)};
var REVIEW_STEM = {json.dumps(a.stem or os.path.splitext(os.path.basename(a.input))[0])};
var REVIEW_FILE = {json.dumps(os.path.basename(a.output))};
{read(os.path.join(ASSETS, 'review.js'))}
</script>
</body>
</html>"""
    with open(a.output, 'w') as f: f.write(page)
    n = sum(1 for b in blocks if 'id' in b)
    rows = sum(len(b['body']) for b in blocks if b['kind'] == 'table')
    print(f'{a.output}: {len(page)//1024}KB · {n} block targets + {rows} table rows '
          f'= {n + rows} commentable')

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('input')
    p.add_argument('-o', '--output', required=True)
    p.add_argument('--title'); p.add_argument('--eyebrow'); p.add_argument('--subtitle')
    p.add_argument('--brand-css', help='path to a brand stylesheet defining the design tokens')
    p.add_argument('--root-class', default='love love--red love--dark',
                   help='class(es) for <html>, e.g. "love love--blue love--dark"')
    p.add_argument('--key', help='localStorage key (defaults to a slug of the title)')
    p.add_argument('--label', help='how the document identifies itself in the export '
                                   '(e.g. "Chapter 15"); defaults to --eyebrow')
    p.add_argument('--source', help='source filename to record in the export '
                                    '(defaults to the input filename)')
    p.add_argument('--generator', help='name of the tool/skill that produced this file, '
                                       'recorded in the export so a later reader knows '
                                       'what built it and how to rebuild it (optional)')
    p.add_argument('--stem', help='base name for the downloaded notes file '
                                  '(defaults to the input filename without extension)')
    p.add_argument('--fonts', default='', help='font stylesheet URL to load progressively')
    p.add_argument('--questions', help='path to a JSON file of [{"key","anchor","text"}, …] — '
                                       'questions the model wants the reviewer to answer in-document; '
                                       '"anchor" must equal the exact target ref it belongs to '
                                       '(¶042, ¶042·s3, ¶042 r3, ¶042 r3c2, or §N for a heading)')
    build(p.parse_args())

if __name__ == '__main__':
    main()
