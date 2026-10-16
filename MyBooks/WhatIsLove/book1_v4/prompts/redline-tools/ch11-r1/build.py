import re,html,sys,subprocess,os
sys.path.insert(0,'.')
from why import W
SRC='/mnt/user-data/uploads/book1_v4/chapters/chapter_11.md'
subprocess.run(['python3','redline.py','.',SRC,'ch11-redline1-2026-10-06.html','tpl.html'],check=True)
n=len(__import__('edits').E)
t=open('ch11-redline1-2026-10-06.html').read(); body=t.split('<main>')[1]
out=["# Prudence: How to Love — Redline 1","",
"Every proposed change to chapters/chapter_11.md, grouped by kind. Struck red text is removed; green text is added; ¶ marks a paragraph break. Nothing has been written to the chapter yet.","",
f"This is the bishop-readiness pass, kickoff items 1–12, revised for your 7 October ruling on facets. The read-aloud (item 13) comes in a later redline, once these land. Dry run: all {n} anchors matched exactly once; 7 quotation blocks, 7 Scripture attribution lines, 1 callout and divs 8/8 unchanged; no footnotes before or after. Every quotation added or changed was checked (Scripture against an RSVCE and a plain RSV source, Church documents on vatican.va) and saved to references/cache.","",
"Not changed, on purpose: the father/mother paragraph and the trimmed Mass paragraph (entry 166; the Mass paragraph changes only \"pillars\" to \"facets\"); the cellar case's three-step structure; the four case studies' order. Prudence as \"intelligence of love\" and the charioteer image stay.","",
"Click any sentence, paragraph or heading to leave a note on it. The editor opens with the proposed wording, so you can rewrite it in place, or clear it and write a comment or a question instead. Anything you leave without a note counts as approved. When you are done, press Copy at the bottom and paste the notes back to me.",""]
for m in re.finditer(r'<h2>(.*?)</h2>|<div class="ed"><div class="ln">(.*?)</div><p>(.*?)</p></div>',body,re.S):
    if m.group(1):
        g=html.unescape(m.group(1)); out+=["## "+g,"","**Why.** "+W[g.split(' ')[0]],""]
    else:
        lab=html.unescape(m.group(2)).replace('Section: ','')
        b=m.group(3).replace('\n',' ').replace('<b>','**').replace('</b>','**')
        b=re.sub(r'<span class="pb">¶</span>',' ¶ ',b)
        out+=["### "+lab,"",b,""]
s='\n'.join(out)
s=s.replace('&lt;div class="blockquote"&gt;','[quotation block:] ').replace('&lt;/div&gt;','[end of quotation block]').replace('\\hfill\\small ','').replace('&amp;','&')
assert '&lt;' not in s and '&gt;' not in s
open('ch11-redline1-review-2026-10-06.md','w').write(s)
D='/root/.claude/skills/synced/17e66e85-93b0-4407-9f2e-d4bb85bc1b8e_d49b3125-407b-4aca-9179-dfb85ce9bdc2'
subprocess.run(['python3',D+'/rich-html-doc/scripts/build_review.py','ch11-redline1-review-2026-10-06.md','-o','ch11-redline1-review-2026-10-06.html','--title','Prudence: How to Love — Redline 1','--eyebrow','Chapter Eleven','--subtitle','Chapter 11 · Bishop-readiness pass · Redline 1','--brand-css',D+'/brand-love/assets/love-brand.css','--root-class','love love--red love--light','--key','wil-ch11-redline1','--label','Chapter 11 Redline 1','--source','chapters/chapter_11.md','--generator','wil-review-chapter skill (wraps rich-html-doc/scripts/build_review.py)','--fonts','https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap'],check=True)
p='ch11-redline1-review-2026-10-06.html'; s=open(p).read()
parts=re.split(r'(<[^>]+>)',s); insc=False
for i,x in enumerate(parts):
    if x.startswith('<script'): insc=True
    elif x.startswith('</script'): insc=False
    elif not x.startswith('<') and not insc:
        for tg in ['del','ins','i','b','em']: x=x.replace(f'&lt;{tg}&gt;',f'<{tg}>').replace(f'&lt;/{tg}&gt;',f'</{tg}>')
        parts[i]=x
s=''.join(parts)
css='<style>main del{color:#b3261e;text-decoration:line-through;background:none}main ins{color:#1d6b3a;text-decoration:none!important;border:0!important;background:none!important}.love--dark main del{color:#ff8a80}.love--dark main ins{color:#7fd69b}</style>'
s=s.replace('</head>',css+'\n<!-- redline source: chapters/reports/ch11-redline1-review-2026-10-06.md; edits: prompts/redline-tools/ch11-r1/edits.py; rebuild: python3 build.py -->\n</head>',1)
open(p,'w').write(s); print('dels',s.count('<del>'))
