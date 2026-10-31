import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','chapters','chapter_16.md')
_s=open(P).read().split('\n')
def L(s):
    for i,x in enumerate(_s,1):
        if s in x: return i
    raise SystemExit('no line: '+s)
def e(g,o,n): return (g,L(o),o,n)
E=[
 e("Chapter 16: the 60 million figure","Abortion eliminates 60+ million children in America alone—entire","Abortion eliminates 60+ million children in America alone<sup>1</sup>—entire"),
 e("Chapter 16: new Notes section","- **Mary Eberstadt:** *How the West Really Lost God*—Family breakdown and loss of faith","- **Mary Eberstadt:** *How the West Really Lost God*—Family breakdown and loss of faith\n\n### Notes\n\n\\footnotesize\n\n1. Cumulative U.S. abortions since *Roe v. Wade* (1973). No agency publishes an official cumulative total. The National Right to Life Committee estimates about 63 million, built from CDC and Guttmacher Institute annual counts. For current annual figures, see Chapter 1, note 4.\n\n\\normalsize"),
]
