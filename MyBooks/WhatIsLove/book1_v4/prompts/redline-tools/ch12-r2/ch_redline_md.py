#!/usr/bin/env python3
"""Make a redline Markdown (del/ins confined to single sentences) from OLD.md -> NEW.md,
for building with rich-html-doc/build_review.py.
usage: ch_redline_md.py OLD.md NEW.md OUT.md BUILD_REVIEW.py
"""
import sys, re, difflib, importlib.util

old_p, new_p, out_p, br = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("br", br); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
split = m.split_sentences

def blocks(text):
    out, cur, in_div = [], [], 0
    for ln in text.split("\n"):
        if in_div or ln.startswith("<div"):
            cur.append(ln)
            in_div += ln.count("<div") - ln.count("</div>")
            if in_div == 0:
                out.append("\n".join(cur)); cur = []
            continue
        if ln.strip() == "":
            if cur: out.append("\n".join(cur)); cur = []
        else:
            cur.append(ln)
    if cur: out.append("\n".join(cur))
    return out

tok = re.compile(r"\s+|\*\*|[^\s*]+|\*")
def wdiff(a, b):
    ta, tb = tok.findall(a), tok.findall(b)
    s = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    o = []
    for op, i1, i2, j1, j2 in s.get_opcodes():
        x, y = "".join(ta[i1:i2]), "".join(tb[j1:j2])
        if op == "equal": o.append(x); continue
        # keep surrounding whitespace outside tags
        def wrap(tag, z):
            if not z.strip(): return z if tag == "ins" else ""
            lead = z[:len(z) - len(z.lstrip())]; trail = z[len(z.rstrip()):]
            return f"{lead}<{tag}>{z.strip()}</{tag}>{trail}"
        if x: o.append(wrap("del", x))
        if y: o.append(wrap("ins", y))
    return "".join(o)

def whole(tag, text):
    return " ".join(f"<{tag}>{s}</{tag}>" for s in split(text))

PREFIX = re.compile(r"^(#{1,6} |\d+\. |- )")
def para_diff(a, b):
    """a, b: single prose blocks (may be None)."""
    if a is None: tgt, src = b, None
    else: tgt, src = b, a
    if b is None:
        pa = PREFIX.match(a); pre = pa.group(1) if pa else ""
        return pre + whole("del", a[len(pre):])
    if a is None:
        pb = PREFIX.match(b); pre = pb.group(1) if pb else ""
        return pre + whole("ins", b[len(pre):])
    pa, pb = PREFIX.match(a), PREFIX.match(b)
    prea, preb = (pa.group(1) if pa else ""), (pb.group(1) if pb else "")
    a2, b2 = a[len(prea):], b[len(preb):]
    sa, sb = split(a2), split(b2)
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal": out += sb[j1:j2]; continue
        olds, news = sa[i1:i2], sb[j1:j2]
        # pair sentences by similarity, in order
        k = 0
        for n_ in news:
            best, bi = 0, None
            for idx in range(k, len(olds)):
                r = difflib.SequenceMatcher(None, olds[idx], n_).ratio()
                if r > best: best, bi = r, idx
            if bi is not None and best >= 0.45:
                for d in olds[k:bi]: out.append(f"<del>{d}</del>")
                out.append(wdiff(olds[bi], n_)); k = bi + 1
            else:
                out.append(f"<ins>{n_}</ins>")
        for d in olds[k:]: out.append(f"<del>{d}</del>")
    return preb + " ".join(out)

def div_diff(a, b):
    """Blockquote/callout: keep wrapper lines, diff inner prose lines."""
    if a == b: return b
    la = (a or "").split("\n"); lb = (b or "").split("\n")
    if b is None:
        return "\n".join(l if (l.startswith("<") or l.startswith("\\hfill") or not l.strip()) else whole("del", l) for l in la)
    inner_a = [l for l in la if l.strip() and not l.startswith("<") and not l.startswith("\\hfill")]
    out = []
    for l in lb:
        if l.startswith("<") or l.startswith("\\hfill") or not l.strip():
            out.append(l)
        else:
            if a is None or not inner_a: out.append(whole("ins", l))
            else: out.append(para_diff(inner_a.pop(0), l))
    return "\n".join(out)

def isdiv(x): return x is not None and x.startswith("<div")

def islist(x): return x is not None and len(x.split("\n")) > 1 and all(PREFIX.match(l) for l in x.split("\n") if l.strip())

def list_diff(a, b):
    la = a.split("\n") if a else []; lb = b.split("\n") if b else []
    sm2 = difflib.SequenceMatcher(None, la, lb, autojunk=False); out = []
    for op, i1, i2, j1, j2 in sm2.get_opcodes():
        if op == "equal": out += lb[j1:j2]; continue
        olds = la[i1:i2]
        for n_ in lb[j1:j2]:
            best, bi = 0, None
            for idx, o_ in enumerate(olds):
                r = difflib.SequenceMatcher(None, o_, n_).ratio()
                if r > best: best, bi = r, idx
            if bi is not None and best >= 0.5: out.append(para_diff(olds.pop(bi), n_))
            else: out.append(para_diff(None, n_))
        for o_ in olds: out.append(para_diff(o_, None))
    return "\n".join(out)

def bdiff(a, b):
    if isdiv(a) or isdiv(b): return div_diff(a, b)
    if islist(a) or islist(b): return list_diff(a, b)
    return para_diff(a, b)

A, B = blocks(open(old_p).read()), blocks(open(new_p).read())
setA, setB = set(A), set(B)
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
res = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal": res += B[j1:j2]; continue
    olds = [x for x in A[i1:i2] if x not in setB]   # moved blocks are not deletions
    for nb in B[j1:j2]:
        if nb in setA:
            res.append(nb); continue                  # moved, unchanged
        # pair with most similar remaining old block of the same kind
        best, bi = 0, None
        for idx, ob in enumerate(olds):
            if isdiv(ob) != isdiv(nb): continue
            r = difflib.SequenceMatcher(None, ob, nb).ratio()
            if r > best: best, bi = r, idx
        if bi is not None and best >= 0.5:
            ob = olds.pop(bi)
            res.append(bdiff(ob, nb))
        else:
            res.append(bdiff(None, nb))
    for ob in olds:
        res.append(bdiff(ob, None))
open(out_p, "w").write("\n\n".join(res) + "\n")
print("blocks", len(res))
