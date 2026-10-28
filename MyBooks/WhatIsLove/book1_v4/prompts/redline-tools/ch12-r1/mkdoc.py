import re,difflib,sys
sys.path.insert(0,'/tmp/claude-0/ch12-r1')
from edits import E
src=open('/mnt/user-data/uploads/book1_v4/chapters/chapter_12.md').read()
TOK=r"\w[\w'’:.–-]*\w|\w|\n|\s+|[^\w\s]"
def wrap(tag,txt):
    # one tag pair per sentence-ish chunk, so the builder's sentence splitter never cuts a span
    parts=re.split(r'(?<=[.!?:;])(["”’)*]*\s+)',txt)
    out=''
    for i in range(0,len(parts),2):
        seg=parts[i]; gap=parts[i+1] if i+1<len(parts) else ''
        m=re.match(r'^(["”’)*]*)(\s+)$',gap) if gap else None
        tailq,sp=(m.group(1),m.group(2)) if m else ('','')
        seg=seg+tailq
        if seg.strip(): out+=f'<{tag}>{seg}</{tag}>'
        out+=sp
    return out
def diff(o,n):
    a=re.findall(TOK,o); b=re.findall(TOK,n)
    segs=[['eq' if op=='equal' else 'ch',a[i1:i2],b[j1:j2]] for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()]
    ch=True
    while ch:
        ch=False
        for k in range(1,len(segs)-1):
            s=segs[k]
            if s[0]=='eq' and segs[k-1][0]=='ch' and segs[k+1][0]=='ch' and len([t for t in s[1] if t.strip()])<=3:
                p,nx=segs[k-1],segs[k+1]; segs[k-1:k+2]=[['ch',p[1]+s[1]+nx[1],p[2]+s[2]+nx[2]]]; ch=True; break
    out=''
    for kind,A,B in segs:
        A=''.join(A); B=''.join(B)
        if kind=='eq': out+=A; continue
        lead=re.match(r'\s*',A).group() if A.strip() else re.match(r'\s*',B).group()
        out+=lead
        if A.strip(): out+=wrap('del',A.strip())
        if A.strip() and B.strip(): out+=' '
        if B.strip(): out+=wrap('ins',B.strip())
        out+=re.search(r'\s*$',B).group() if B.strip() else re.search(r'\s*$',A).group()
    return out
lines=src.split('\n')
def lineno(i): return src[:i].count('\n')+1
def section(i):
    hs=list(re.finditer(r'^(#{2,3}) +(.+)$',src[:i],re.M))
    if not hs: return '(chapter opening)'
    sec=hs[-1].group(2).strip()
    if hs[-1].group(1)=='###':
        par=[m for m in hs if m.group(1)=='##']
        if par: sec=par[-1].group(2).strip()+' › '+sec
    return sec.replace('*','')
# group edits by (group, paragraph line)
blocks=[];idx={}
for g,l,o,n in E:
    i=src.find(o); ln=lineno(i)
    key=(g,ln)
    if key not in idx: idx[key]=len(blocks); blocks.append([g,ln,i,[]])
    blocks[idx[key]][3].append((o,n))
out=[]; cur=None
for g,ln,i,eds in blocks:
    if g!=cur: out.append('## '+g); cur=g
    old=lines[ln-1]; new=old
    for o,n in eds: new=new.replace(o,n)
    out.append(f'*Section: {section(i)} · line {ln}*')
    if old.startswith('- ') or old.startswith('#'):
        # list items / headings: show old line struck and new lines inserted, whole
        if old.startswith('#'):
            out.append(wrap('del',old.lstrip('# '))+' → '+wrap('ins',new.lstrip('# ')))
        else:
            newl=new.split('\n')
            if len(newl)==1: out.append('- '+diff(old[2:],new[2:]))
            else:
                first=newl[0]; rest=newl[1:]
                out.append('- '+diff(old[2:],first[2:]) if first.startswith('- ') else '- '+wrap('del',old[2:]))
                for r in rest:
                    if r.startswith('- '): out.append('- '+wrap('ins',r[2:]))
                    elif r.startswith('### '): out.append('**'+wrap('ins','New sub-heading: '+r[4:])+'**')
                    elif r.strip(): out.append(wrap('ins',r))
    else:
        out.append(diff(old,new))
open('/tmp/claude-0/ch12-r1/body.md','w').write('\n\n'.join(out)+'\n')
print(len(blocks),'blocks')
