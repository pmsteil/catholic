import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','chapters','chapter_15.md')
_s=open(P).read().split('\n')
def L(s):
    for i,x in enumerate(_s,1):
        if s in x: return i
    raise SystemExit('no line: '+s)
def e(g,o,n): return (g,L(o),o,n)
E=[
 e("Chapter 15: note 1","(1973), from Guttmacher Institute counts and estimates — well past 60 million by the mid-2020s. For current annual figures, see Chapter 1, note 2.","(1973). No agency publishes an official cumulative total. The National Right to Life Committee estimates about 63 million, built from CDC and Guttmacher Institute annual counts. For current annual figures, see Chapter 1, note 4."),
]
