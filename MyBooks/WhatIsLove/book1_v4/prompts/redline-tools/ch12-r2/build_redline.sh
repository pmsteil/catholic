#!/usr/bin/env bash
# build_redline.sh REDLINE.md OUT.html
set -euo pipefail
IN="$1"; OUT="$2"
SK=/root/.claude/skills/synced/17e66e85-93b0-4407-9f2e-d4bb85bc1b8e_d49b3125-407b-4aca-9179-dfb85ce9bdc2
BR=$SK/rich-html-doc/scripts/build_review.py
BRAND=$SK/brand-love/assets/love-brand.css
FONTS="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cinzel+Decorative:wght@400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap"
SRC=/Users/patiman/git/__master__/_projects_/catholic/catholic-book-writing/MyBooks/WhatIsLove/book1_v4/chapters/chapter_12.md
python3 "$BR" "$IN" -o "$OUT" --source "$SRC" --title "The Lawgiver Is Love" \
  --eyebrow "Chapter Twelve" --subtitle "Chapter 12 · Redline 2 · the moral argument" \
  --label "Chapter 12 Redline 2" --key "wil-ch12-redline2" --stem "ch12-redline2-notes" \
  --root-class "love love--red love--light" \
  --generator "wil-review-chapter skill (wraps rich-html-doc/scripts/build_review.py)" \
  --fonts "$FONTS" --brand-css "$BRAND"
python3 - "$OUT" "$SRC" <<'PY'
import re, sys
p, src = sys.argv[1], sys.argv[2]
s = open(p).read()
def fix(m):
    t = m.group(1)
    for a, b in (('&lt;del&gt;', '<del>'), ('&lt;/del&gt;', '</del>'),
                 ('&lt;ins&gt;', '<ins>'), ('&lt;/ins&gt;', '</ins>'),
                 ('&lt;sup&gt;', '<sup>'), ('&lt;/sup&gt;', '</sup>')):
        t = t.replace(a, b)
    return '>' + t + '<'
s = re.sub(r'>([^<]*)<', fix, s)
css = ("<style>del{color:#b3261e;text-decoration:line-through;background:none}"
       "ins{color:#1e7a3c;text-decoration:none;background:none}</style></head>")
s = s.replace('</head>', css, 1)
s = s.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- generated-by: wil-review-chapter skill (wraps rich-html-doc/scripts/build_review.py) -->\n'
              f'<!-- source-of-truth: {src} -->\n<!-- redline: chapter_12.md -> proposed; generator ch_redline_md.py -->', 1)
open(p, 'w').write(s)
# verify: no sent span with unbalanced del/ins
bad = 0
for m in re.finditer(r'<span class="sent"[^>]*>(.*?)</span>', s, re.S):
    x = m.group(1)
    if x.count('<del>') != x.count('</del>') or x.count('<ins>') != x.count('</ins>'):
        bad += 1
print('unbalanced sentence spans:', bad, '| del', s.count('<del>'), '| ins', s.count('<ins>'), '| escaped left', s.count('&lt;del&gt;') + s.count('&lt;ins&gt;'))
PY
