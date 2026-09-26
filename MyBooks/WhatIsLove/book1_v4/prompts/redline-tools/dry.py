import re,sys
sys.path.insert(0,'/'.join(__file__.split('/')[:-1]))
from edits import E
src=open(sys.argv[1]).read(); s=src; ok=True
for g,l,o,n in E:
    c=s.count(o)
    if c!=1: print("ANCHOR",c,l,o[:70]); ok=False
    else: s=s.replace(o,n)
def stats(t):
    return dict(words=len(t.split()),lines=t.count('\n'),bq=t.count('class="blockquote"'),co=t.count('class="callout"'),hf=t.count('\\hfill\\small'),
      do=t.count('<div'),dc=t.count('</div>'),sup=len(re.findall(r'<sup>\d+</sup>',t)),notes=len(re.findall(r'^\d+\. ',t.split('### Notes')[1],re.M)),fs=t.count('\\footnotesize'),ns=t.count('\\normalsize'),fn=t.count('[^'))
print("before",stats(src)); print("after ",stats(s)); print("anchors ok" if ok else "FAIL", len(E),"edits")
open(sys.argv[2],'w').write(s)
