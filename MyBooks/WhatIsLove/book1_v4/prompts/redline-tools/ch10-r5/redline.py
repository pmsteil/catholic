import re,sys,html,difflib
sys.path.insert(0,sys.argv[1])
from edits import E
src=open(sys.argv[2]).read()
def md(t):
    t=html.escape(t,quote=False)
    t=t.replace('&lt;em&gt;','<em>').replace('&lt;/em&gt;','</em>')
    t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t); t=re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])',r'<i>\1</i>',t)
    return t.replace('*','')
TOK=r"\w[\w'’:.–-]*\w|\w|\n\n|\s+|[^\w\s]"
def diff(o,n):
    a=re.findall(TOK,o); b=re.findall(TOK,n)
    ops=[list(x) for x in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()]
    # coalesce short equal runs between changes
    segs=[]
    for op,i1,i2,j1,j2 in ops:
        if op=='equal': segs.append(['eq',a[i1:i2],b[j1:j2]])
        else: segs.append(['ch',a[i1:i2],b[j1:j2]])
    changed=True
    while changed:
        changed=False
        for k in range(1,len(segs)-1):
            s=segs[k]
            if s[0]=='eq' and segs[k-1][0]=='ch' and segs[k+1][0]=='ch' and len([t for t in s[1] if t.strip()])<=3:
                p,nx=segs[k-1],segs[k+1]
                segs[k-1:k+2]=[['ch',p[1]+s[1]+nx[1],p[2]+s[2]+nx[2]]]; changed=True; break
    out=[]
    for kind,A,B in segs:
        A=''.join(A); B=''.join(B)
        if kind=='eq': out.append(md(A)); continue
        lead=(re.match(r'\s*',A).group() or re.match(r'\s*',B).group()).replace('\n\n',' ')
        out.append(lead)
        if A.strip(): out.append('<del>'+md(A.strip())+'</del>')
        if '\n\n' in B and not B.strip(): out.append('<span class="pb">¶</span>'); continue
        if B.strip():
            if A.strip(): out.append(' ')
            bb=md(B.strip()).replace('\n\n','</ins><span class="pb">¶</span><ins>')
            if B.lstrip(' ').startswith('\n\n'): out.append('<span class="pb">¶</span>')
            out.append('<ins>'+bb+'</ins>')
        tr=re.search(r'\s*$',B).group() or re.search(r'\s*$',A).group()
        out.append(' <span class="pb">¶</span>' if '\n\n' in tr else tr)
    return re.sub(r'<ins></ins>','',''.join(out))
paras=[]  # (start,end)
pos=0
for m in re.finditer(r'[^\n]+',src): paras.append((m.start(),m.end()))
def para_of(i):
    for s,e in paras:
        if s<=i<e: return (s,e)
groups={}; order=[]
for g,l,o,n in E:
    i=src.find(o); p=para_of(i if o[0]!='\n' else i+1) or para_of(i)
    key=(g,p)
    if key not in groups: groups[key]=[]; order.append(key)
    groups[key].append((l,o,n))
def trim(old,new,first,last_old):
    # context: one sentence before first change, one after last change
    pre=old[:first]; m=list(re.finditer(r'[.!?]["”)*]*\s',pre))
    cut=m[-2].end() if len(m)>1 else 0
    return cut
H=[]; cur=None
for key in order:
    g,(s,e)=key
    if g!=cur: H.append(f'<h2>{html.escape(g)}</h2>'); cur=g
    old=src[s:e+1]; new=old; lines=[]
    for l,o,n in groups[key]:
        assert new.count(o)==1 or (o.startswith('\n') ), (l,o[:40])
        new=new.replace(o,n); lines.append(str(l))
    # trim context
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False); ops=[x for x in sm.get_opcodes() if x[0]!='equal']
    f=ops[0][1]; lo=ops[-1][2]; ln=ops[-1][4]
    m=list(re.finditer(r'(?<!A\.D)(?<![A-Z])[.!?:]["”)*]*\s',old[:f])); cut=m[-2].end() if len(m)>1 and not old.startswith('- ') else 0
    t=None if old.startswith('- ') else re.search(r'(?<![A-Z])[.!?]["”)*]*(\s|$)',old[lo:]); tail_o=len(old) if not t else lo+t.end()
    tail_n=ln+(tail_o-lo)
    pre='… ' if cut else ''; post=' …' if tail_o<len(old) else ''
    body=diff(old[cut:tail_o],new[cut:tail_n])
    lab='lines '+', '.join(dict.fromkeys(lines)) if len(set(lines))>1 else 'line '+lines[0]
    hs=[m for m in re.finditer(r'^(#{1,4}) +(.+)$',src[:s],re.M)]
    sec=hs[-1].group(2).strip() if hs else '(chapter opening)'
    if len(hs)>1 and hs[-1].group(1)=='###':
        par=[m for m in hs if m.group(1)=='##']
        if par: sec=par[-1].group(2).strip()+' › '+sec
    lab='Section: '+html.escape(sec.replace('*',''))+' · '+lab
    H.append(f'<div class="ed"><div class="ln">{lab}</div><p>{pre}{body}{post}</p></div>')
open(sys.argv[3],'w').write(open(sys.argv[4]).read().replace('%%BODY%%','\n'.join(H)))
print(len(order),'blocks')
