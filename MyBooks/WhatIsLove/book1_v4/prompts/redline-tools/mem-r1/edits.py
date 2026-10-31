import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','memory.html')
_s=open(P).read().split('\n')
def L(s):
    for i,x in enumerate(_s,1):
        if s in x: return i
    raise SystemExit('no line: '+s)
O='<h2 id="research">13. Research &amp; Scripture Citations</h2>'
E=[("memory.html §13: research notes pointer",L(O),O,O+'\n\n<div class="card">\n  <h3>Fact research notes</h3>\n  <p>Checked facts, figures, people and saints live in <code>research-notes.md</code>, with sources, cautions and where the book uses each one. Read it before you research any fact. Add each new finding to it.</p>\n</div>')]
