import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','CLAUDE.md')
_s=open(P).read().split('\n')
def L(s):
    for i,x in enumerate(_s,1):
        if s in x: return i
    raise SystemExit('no line: '+s)
E=[("CLAUDE.md: research notes pointer",L("After each edit, run `bin/split-memory.py`."),"`memory.html` stays the single source of truth. Edit it, never the `memory/` files. After each edit, run `bin/split-memory.py`.","`memory.html` stays the single source of truth. Edit it, never the `memory/` files. After each edit, run `bin/split-memory.py`.\n\n`research-notes.md` holds checked facts, figures, people and saints, with sources and where the book uses them. Read it BEFORE you research any fact. Add each new finding to it.")]
