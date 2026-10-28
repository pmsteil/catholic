import json,html
d=json.load(open('/tmp/claude-0/lab/scores.json'))
S=d['schools']
def cell(r,s):
    v=r['scores'].get(s); f=r['sound'].get(s,'')
    if v is None: return '<td class="na">…</td>'
    cls='hi' if v>=8 else 'mid' if v>=6 else 'lo'
    sound=bool(f) and not f.startswith('As written: NONE')
    flag=f'<span class="flag" title="{html.escape(f)}">!</span>' if sound else ''
    return f'<td class="{cls}">{v}{flag}</td>'
rows=[]
for r in d['rounds']:
    vals=[r['scores'][s] for s in S if s in r['scores']]
    mean=f"{sum(vals)/len(vals):.1f}" if vals else '…'
    left=sum(1 for s in S if r['sound'].get(s) and not r['sound'][s].startswith('As written: NONE'))
    rows.append(f"<tr><th>{r['round']}</th><td class='v'>{r['version']}</td>"+''.join(cell(r,s) for s in S)+f"<td class='m'>{mean}</td><td>{left if vals else '…'}</td><td class='st'>{html.escape(r['status'])}</td></tr>")
notes=''.join(f"<li><b>Round {r['round']} ({r['version']}):</b> {html.escape(r['note'])}</li>" for r in d['rounds'])
open('/tmp/claude-0/lab/scoreboard.html','w').write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Argument Lab Scoreboard</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Libre+Baskerville&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>:root{{--bg:#fbf6ee;--ink:#2a2420;--mut:#6f6259;--rule:#e4dbd0;--cr:#8f1d2c;--gold:#b08a3e;--hi:#1d6b3a;--mid:#8a6d1a;--lo:#b3261e;--card:#fffaf2}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1c1917;--ink:#ece6df;--mut:#b0a59a;--rule:#3a332e;--cr:#e07a86;--gold:#d4b06a;--hi:#7fd69b;--mid:#e5c45e;--lo:#ff8a80;--card:#24201d}}}}
body{{background:var(--bg);color:var(--ink);font-family:Inter,sans-serif;margin:0}}main{{max-width:1100px;margin:0 auto;padding:32px 16px}}
.eb{{font-family:Cinzel,serif;color:var(--cr);letter-spacing:.14em;font-size:12px;text-transform:uppercase}}h1{{font-family:Cinzel,serif;margin:.2em 0;font-size:28px}}
p.s{{font-family:"Libre Baskerville",serif;color:var(--mut)}}.w{{overflow-x:auto;border:1px solid var(--rule);border-radius:10px;background:var(--card)}}
table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:9px 7px;text-align:center;border-bottom:1px solid var(--rule)}}thead th{{color:var(--cr);font-weight:600;position:sticky;top:0;background:var(--card)}}
td.hi{{color:var(--hi);font-weight:600}}td.mid{{color:var(--mid);font-weight:600}}td.lo{{color:var(--lo);font-weight:600}}td.na{{color:var(--mut)}}td.m{{font-weight:700}}td.st{{color:var(--mut);text-align:left}}
.flag{{color:var(--lo);margin-left:2px;cursor:help}}ul{{font-family:"Libre Baskerville",serif;line-height:1.7}}.k{{color:var(--mut);font-size:12px}}</style></head><body><main>
<div class="eb">Chapter Twelve · Argument Lab</div><h1>Scoreboard</h1>
<p class="s">Robustness of each version against each school, 1–10. A red “!” marks a sound objection still standing (hover to read it). The lab ended after Round 7, when no school could log one. Round 8 is a blind confirmation: fresh reviewers who see only the final text, plus six schools new to the panel.</p>
<div class="w"><table><thead><tr><th>Round</th><th>Version</th>{''.join(f"<th>{s}</th>" for s in S)}<th>Mean</th><th>Sound left</th><th>Status</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2 style="font-family:Cinzel,serif;font-size:18px;color:var(--cr);margin-top:28px">Round notes</h2><ul>{notes}</ul>
<p class="k">Full logs: chapters/reports/ch12-argument-lab/ (EVOLUTION.md, round-N/).</p></main></body></html>''')
print('ok')
