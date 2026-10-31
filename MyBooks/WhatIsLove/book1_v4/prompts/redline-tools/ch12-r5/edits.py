import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','ch12-r2','premise2-examples.md')
_s=open(P).read().split('\n')
def L(s):
    for i,x in enumerate(_s,1):
        if s in x: return i
    raise SystemExit('no line: '+s)
def e(g,o,n): return (g,L(o),o,n)
E=[
 e("Mercy: Jamel Dunn", r'''a 32-year-old disabled man''', r'''a disabled man'''),
 e("Mercy: Jamel Dunn", r'''Police called their conduct inhumane but not illegal.''', r'''The State Attorney declined to charge anyone, because no Florida law required them to help.'''),
 e("Footnote 4", r'''4. Police statements reported by Fox 35 Orlando and WHYY, July 2017: Jamel Dunn, 32, drowned in a retention pond in Cocoa, Florida, on 9 July 2017. The teenagers, aged 14 to 16, filmed and mocked him and called no one.''', r'''4. Reports in Fox 35 Orlando and CBS Miami (July 2017) and the Associated Press (22 June 2018): Jamel Dunn drowned in a retention pond in Cocoa, Florida, in July 2017. Teenagers filmed and mocked him and called no one. State Attorney Phil Archer declined to charge four juveniles and one adult. He noted that no Florida law requires a person to give emergency aid, and that a bill to create such a duty failed in 2018.'''),
 e("Footnote 3", r'''Since 2021, people whose natural death is not reasonably foreseeable have been eligible.''', r'''Bill C-7 (Royal Assent, 17 March 2021) made people whose natural death is not reasonably foreseeable eligible.'''),
 e("Footnote 7", r'''7. Pope Francis, Angelus address, 26 December 2021 ("the demographic winter"), and later speeches in Rome in 2022 and 2023. On fertility trends, see the 2024 *Lancet* study of the Institute for Health Metrics and Evaluation, which projects that 155 of 204 countries will be below replacement fertility by 2050.''', r'''7. OECD, *Society at a Glance 2024*: in 2022 the total fertility rate was below the replacement level of about 2.1 in every OECD country except Israel. United Nations, *World Population Prospects 2024*: 131 of 237 countries and areas are below replacement, home to about two-thirds of the world's people. Pope Francis, Angelus address, 26 December 2021 ("the demographic winter"), and later speeches in Rome in 2022 and 2023.'''),
]
