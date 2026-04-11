#!/usr/bin/env python3
"""
What Is Love? — Gothic Cathedral Book Cover SVG Generator v2
==============================================================
Words conform to architectural shapes. Text IS the architecture.
- Vertical text for pillars
- Curved textPaths for arches, vault ribs, rose window
- Shape-boundary text packing for arches, spires, circles
- Dense packing throughout
"""

import svgwrite
import math
import random

# ============================================================
# CANVAS
# ============================================================
W, H = 1200, 1800
OUTPUT = '/Users/patiman/Desktop/designer-output/what-is-love-cathedral-v2.svg'

dwg = svgwrite.Drawing(OUTPUT, size=(f'{W}px', f'{H}px'),
                        viewBox=f'0 0 {W} {H}', profile='full')
defs = dwg.defs

# ============================================================
# COLORS
# ============================================================
BG           = '#1a0508'     # very dark wine-black
SKY_TEXT     = '#321018'     # barely visible (exterior names of God)
GOLD         = '#C9A84C'
GOLD_BRIGHT  = '#F0D060'
GOLD_PALE    = '#b8a060'
GOLD_DIM     = '#806830'
C_TRUTH      = '#c8a830'
C_JUSTICE    = '#8850c0'
C_MERCY      = '#c8909c'
C_SACRIFICE  = '#a81818'
C_IVORY      = '#d8d0c0'
C_PALE_GOLD  = '#c0a860'
C_CHRIST     = '#e8d898'
C_CROSS      = '#881010'

# Stained glass text colors (bright on dark)
SAC_COLORS = {
    'baptism':      '#5888b8',
    'confirmation': '#c87070',
    'eucharist':    '#d0a030',
    'penance':      '#9868c0',
    'anointing':    '#60a060',
    'orders':       '#c89840',
    'matrimony':    '#d070a0',
}

# ============================================================
# WORD LISTS (same as v1, condensed references)
# ============================================================

EXTERIOR = [
    "Father", "Abba", "YHWH", "I AM", "Creator", "Almighty",
    "Holy Holy Holy", "Eternal", "Infinite", "Alpha", "Omega",
    "El Shaddai", "Adonai", "Lord of Lords", "King of Kings",
    "Ancient of Days", "Ruach", "Spirit", "Light", "Life",
    "In the beginning", "Logos", "Let there be light",
    "He who is", "Transcendent", "Immanent", "Omnipotent",
    "Paraclete", "Comforter", "Bond of Love", "Perichoresis",
    "Trinity", "Divine communion", "Source of all love",
    "Before all time", "Without end", "God himself is an eternal exchange of love",
    "Three Persons One God", "Triune Love", "Ground of being",
    "Providence", "Perfect goodness", "Perfect beauty",
]

COMMANDMENTS = [
    "I AM the Lord your God", "No other gods",
    "Do not take the Lord's name in vain", "Keep holy the Sabbath",
    "Honor your father and mother", "You shall not kill",
    "You shall not commit adultery", "You shall not steal",
    "You shall not bear false witness", "You shall not covet",
    "The Decalogue", "Natural law", "Moral law",
    "Written on the heart", "Conscience", "Sinai", "Moses",
    "Love the Lord your God", "Love your neighbor",
    "On these two all the law depends", "Divine law",
    "Law as gift", "Foundation of justice",
]

TRUTH_W = [
    "Truth", "Logos", "The Word", "Light", "Revelation",
    "The Word became flesh", "Way Truth Life", "Your Word is truth",
    "The truth will set you free", "Sacred Scripture",
    "Tradition", "Magisterium", "Deposit of Faith",
    "Doctrine", "Creed", "Catechism", "Emet", "Aletheia",
    "Fides et Ratio", "Uncreated Light", "Transfiguration",
    "Faith seeking understanding", "Evangelization", "Gospel",
    "Witness", "Teaching", "Orthodoxy", "Illumination",
]

JUSTICE_W = [
    "Justice", "Righteousness", "Right order", "Covenant law",
    "Divine law", "Mishpat", "Dikaiosyne", "Accountability",
    "Restitution", "Rectitude", "Equity", "Fairness",
    "Let justice roll like a river", "Do justice love mercy",
    "Sovereignty", "Divine governance", "Providence",
    "Synderesis", "Moral conscience", "Proportionality",
    "Social justice", "Commutative", "Distributive",
    "Suum cuique", "Natural law",
]

MERCY_W = [
    "Mercy", "Compassion", "Lovingkindness", "Tenderness",
    "Hesed", "Rahamim", "Misericordia", "Eleos",
    "Forgiveness", "Pardon", "Absolution", "Reconciliation",
    "His mercy endures forever", "Divine Mercy",
    "Grace", "Gift", "Be merciful as your Father",
    "Patience", "Seventy times seven", "Prodigal Father",
    "Come to me all who are weary", "Gentleness", "Healing",
    "Living water", "Forbearance", "Lost sheep",
]

SACRIFICE_W = [
    "Sacrifice", "Offering", "Oblation", "Kenosis",
    "Covenant blood", "Greater love has no one than this",
    "The Cross", "Passion", "Calvary", "Good Friday",
    "Via Dolorosa", "Redemption", "Ransom", "Propitiation",
    "Expiation", "Atonement", "Lamb of God", "It is finished",
    "Tetelestai", "Martyrdom", "Take up your cross",
    "Not my will but yours", "Total gift of self", "Fiat",
    "He humbled himself", "Obedient unto death",
]

FAITH_W = [
    "Faith", "Fides", "Belief", "Trust", "Assent", "Surrender",
    "Credo", "Lord I believe", "Profession of faith",
    "Faith is the substance of things hoped for",
    "Faith without works is dead", "Living faith", "Abraham",
    "Fidelity", "Commitment", "Perseverance", "Gift of faith",
]

HOPE_W = [
    "Hope", "Spes", "Longing", "Come Lord Jesus", "Maranatha",
    "Beatific vision", "Heaven", "Eternal life", "Resurrection",
    "He will wipe away every tear", "Anchor of hope",
    "We are saved in hope", "Promise", "Covenant promise",
    "Trust", "Consolation", "Communion of saints",
    "Eye has not seen", "Parousia", "Advent longing",
]

CHARITY_W = [
    "Charity", "Caritas", "Agape", "Love", "Amor",
    "Form of all the virtues", "Binds all in perfect harmony",
    "The greatest of these is love", "Love never fails",
    "Love is patient", "Love is kind",
    "We love because he first loved us", "Benevolence",
    "Communion", "Gift of self", "Life-giving",
]

BEATITUDES = [
    "Blessed are the poor in spirit", "Kingdom of heaven",
    "Blessed are those who mourn", "Comforted",
    "Blessed are the meek", "Inherit the earth",
    "Hunger and thirst for righteousness", "Satisfied",
    "Blessed are the merciful", "Receive mercy",
    "Blessed are the pure in heart", "See God",
    "Blessed are the peacemakers", "Sons of God",
    "Persecuted for righteousness", "Rejoice",
]

SPIRITUAL_MERCY = [
    "Instruct the ignorant", "Counsel the doubtful",
    "Admonish sinners", "Bear wrongs patiently",
    "Forgive injuries", "Comfort the afflicted",
    "Pray for living and dead", "Service of the soul",
    "Patience with weakness", "Intercession",
]

GIFTS_FRUITS = [
    "Wisdom", "Understanding", "Counsel", "Fortitude",
    "Knowledge", "Piety", "Fear of the Lord",
    "Love", "Joy", "Peace", "Patience", "Kindness",
    "Goodness", "Faithfulness", "Gentleness", "Self-control",
    "By their fruits you shall know them",
]

VAULT_SCRIPTURE = [
    "God is love", "Greater love has no one",
    "Love one another as I have loved you",
    "Love your enemies", "Love the Lord your God",
    "The greatest of these is love", "Love never fails",
    "Nothing can separate us from the love of God",
    "Perfect love casts out fear", "He loved them to the end",
    "God so loved the world", "We love because he first loved us",
    "By your love they will know you are my disciples",
    "Love covers a multitude of sins",
    "Love is the fulfillment of the law",
]

EUCHARIST_ALTAR = [
    "This is my Body", "This is my Blood",
    "Do this in memory of me", "Real Presence",
    "Transubstantiation", "Agnus Dei", "Bread of Life",
    "Source and summit", "Mysterium Fidei",
    "Sanctus Sanctus Sanctus", "Sursum Corda",
    "Dona nobis pacem", "Kyrie Eleison", "Corpus Christi",
    "Gloria in Excelsis Deo", "Ite Missa Est",
]

APSE_W = [
    "God's Perfect Love", "Sacred gift of covenant",
    "Binding truth justice mercy and sacrifice",
    "Into life-giving communion", "Deus Caritas Est",
    "Form of all the virtues", "Perfect harmony",
    "To love is to will the good of another",
    "Love that never ends", "Eternal exchange of love",
    "He has destined us to share in that exchange",
    "Fundamental vocation of every human being",
    "Agape", "Caritas", "Hesed", "Amor",
]

SAC_WORDS = {
    'baptism': ["Baptism", "Rebirth", "Water", "Spirit", "Font",
        "Washing", "Adoption", "Sonship", "Regeneration", "Chrism",
        "Born of water and spirit", "Death to sin", "New life"],
    'confirmation': ["Confirmation", "Seal", "Strengthening", "Mission",
        "Gifts of Spirit", "Pentecost", "Fire", "Anointing",
        "Mature discipleship", "Apostolic witness"],
    'eucharist': ["Eucharist", "Real Presence", "Transubstantiation",
        "Body Blood Soul Divinity", "This is my Body",
        "Bread of Life", "Communion", "Source and summit",
        "Consecration", "Last Supper"],
    'penance': ["Penance", "Reconciliation", "Confession", "Contrition",
        "Absolution", "I absolve you", "Prodigal son",
        "Tribunal of mercy", "Healing", "Amendment of life"],
    'anointing': ["Anointing", "Oil", "Prayer", "Comfort", "Healing",
        "Redemptive suffering", "Peace", "Fortitude",
        "Union with Christ", "Preparation"],
    'orders': ["Holy Orders", "Priesthood", "Ordination", "Alter Christus",
        "Bishop", "Priest", "Deacon", "Shepherd", "Ministry",
        "Apostolic succession", "Sacred character"],
    'matrimony': ["Matrimony", "Covenant", "Nuptial bond", "Fidelity",
        "Fruitfulness", "Indissolubility", "Domestic church",
        "Free total faithful fruitful", "One flesh", "Gift of self"],
}

CROSS_W = [
    "Sacrifice", "Atonement", "Calvary", "Passion", "Tetelestai",
    "It is finished", "Ransom", "Redemption", "Agnus Dei",
    "By his wounds", "Pierced for our sins", "Covenant blood",
    "Poured out for many", "He gave himself", "Obedient unto death",
    "Good Friday", "Propitiation", "Expiation", "Via Dolorosa",
]

CHR_HEAD_W = ["INRI", "Ecce Homo", "Crown of thorns", "King",
    "Son of God", "Son of Man", "Emmanuel", "Holy One", "Messiah"]
CHR_BODY_W = ["Word became flesh", "Incarnation", "True God True Man",
    "Sacred Heart", "Blood and water", "He loved them to the end",
    "Kenosis", "By his wounds we are healed", "Body given for you",
    "Corpus Christi", "Real Presence", "Wounded side"]
CHR_ARMS_W = ["Come to me all who are weary", "I will give you rest",
    "Covenant embrace", "Everlasting love", "Arms open wide",
    "I have called you friends", "Welcome", "Receive"]

SPIRE_L = [
    "Genesis", "Exodus", "Psalms", "Proverbs", "Wisdom", "Isaiah",
    "Jeremiah", "Ezekiel", "Daniel", "Matthew", "Mark", "Luke",
    "John", "Acts", "Romans", "Corinthians", "Galatians",
    "Ephesians", "Hebrews", "James", "Revelation",
    "Verbum Domini", "Sacred Scripture",
]

SPIRE_R = [
    "Jesus", "Christ", "Messiah", "Emmanuel", "Logos",
    "Lamb of God", "Good Shepherd", "Light of the World",
    "Bread of Life", "True Vine", "Way Truth Life",
    "Alpha Omega", "Lord", "Savior", "Redeemer", "King",
    "Sacred Heart", "Prince of Peace", "I AM",
    "Risen Lord", "Pantocrator",
]

LATERAL_VIRTUES = [
    "Prudence", "Justice", "Fortitude", "Temperance",
    "Discernment", "Courage", "Self-mastery", "Moderation",
    "Chastity", "Humility", "Meekness", "Imago Dei",
    "Human dignity", "Sanctity of life", "Character",
]

FLOOR_W = [
    "Feed the hungry", "Give drink to the thirsty",
    "Clothe the naked", "Shelter the homeless",
    "Visit the sick", "Visit the imprisoned", "Bury the dead",
    "Whatever you did for the least of these",
    "Almsgiving", "Solidarity", "Care for the poor",
]

ROSE_W = [
    "Deus Caritas Est", "God is Love", "Agape", "Caritas",
    "Hesed", "Amor", "Amore", "Amour", "Liebe",
    "Trinity", "Perichoresis", "Perfect Love", "Covenant",
    "Communion", "Three Persons One God",
]

# ============================================================
# GEOMETRY
# ============================================================
# Cathedral outer bounds
CAT_L, CAT_R = 180, 1020
CAT_TOP, CAT_BOT = 350, 1650
CAT_CX = (CAT_L + CAT_R) // 2  # 600

# Spire positions
SPL_L, SPL_R = 180, 310
SPR_L, SPR_R = 890, 1020
SPIRE_TOP = 60
SPIRE_BASE = CAT_TOP

# Rose window
RW_CX, RW_CY, RW_R = CAT_CX, 290, 115

# Clerestory band
CW_TOP, CW_BOT = 365, 540

# Triforium
TRI_TOP, TRI_BOT = 548, 610

# Pillar positions & dimensions
PIL_W = 38
PIL_TOP, PIL_BOT = 618, 1380
PIL_X = [
    CAT_L + 50,       # Truth
    CAT_L + 260,      # Justice
    CAT_R - 260 - PIL_W,  # Mercy
    CAT_R - 50 - PIL_W,   # Sacrifice
]

# Apse (semicircular behind altar)
APS_CX = CAT_CX
APS_CY = 890
APS_RX, APS_RY = 220, 260
APS_TOP = APS_CY - APS_RY  # ~630

# Altar
ALT_L, ALT_R = 460, 740
ALT_TOP, ALT_BOT = 900, 960

# Crucifix
CRX_CX = CAT_CX
CRX_TOP = 640
CRX_BOT = 890
CRX_VW = 44
CRX_BY = 752
CRX_BH = 44
CRX_BL = 420
CRX_BR = 780

# Christ body
C_HEAD_R = 28
C_HEAD_CX, C_HEAD_CY = CRX_CX, CRX_TOP + 50

# Transept
TRN_TOP, TRN_BOT = 900, 1100
TRN_L_L, TRN_L_R = CAT_L - 100, CAT_L + 10
TRN_R_L, TRN_R_R = CAT_R - 10, CAT_R + 100

# Floor & Foundation
FLR_TOP, FLR_BOT = 1380, 1460
FND_TOP, FND_BOT = 1460, 1650

# Nave arches: tops of pointed arches between pillar pairs
ARCH_PEAK_Y = PIL_TOP - 50

# Vault peak
VAULT_PEAK_Y = CW_BOT + 15

# ============================================================
# HELPERS
# ============================================================

path_id_counter = 0
def next_path_id():
    global path_id_counter
    path_id_counter += 1
    return f'p{path_id_counter}'

def word_cycle(words):
    """Infinite cycling iterator over word list."""
    i = 0
    while True:
        yield words[i % len(words)]
        i += 1

def fill_shape(group, words, is_inside, bbox, font_size=6.5,
               color=GOLD_PALE, line_spacing=1.35, offset_x=0,
               font_family='Georgia, serif'):
    """Fill arbitrary shape with horizontal text conforming to boundaries."""
    x0, y0, x1, y1 = bbox
    lh = font_size * line_spacing
    avg_cw = font_size * 0.48
    sep = u' \u00b7 '
    sep_w = len(sep) * avg_cw
    cy = y0 + font_size + 1
    wc = word_cycle(words)

    while cy < y1 - 1:
        # Find left edge at this y
        lx = x0
        while lx < x1 and not is_inside(lx, cy):
            lx += 0.5
        # Find right edge
        rx = x1
        while rx > lx and not is_inside(rx, cy):
            rx -= 0.5
        avail = rx - lx - 4
        if avail > font_size * 3:
            tokens = []
            cx = 0
            while True:
                word = next(wc)
                ww = len(word) * avg_cw
                needed = ww + (sep_w if tokens else 0)
                if cx + needed > avail:
                    break
                if tokens:
                    cx += sep_w
                tokens.append(word)
                cx += ww
            if tokens:
                group.add(dwg.text(
                    sep.join(tokens),
                    insert=(lx + 2 + offset_x, cy),
                    font_size=f'{font_size}px',
                    font_family=font_family,
                    fill=color,
                ))
        cy += lh

def fill_rect(group, x, y, w, h, words, font_size=6.5,
              color=GOLD_PALE, line_spacing=1.35):
    """Fill rectangle with text."""
    def inside(px, py):
        return x <= px <= x + w and y <= py <= y + h
    fill_shape(group, words, inside, (x, y, x + w, y + h),
               font_size=font_size, color=color, line_spacing=line_spacing)

def fill_vertical(group, x, y, w, h, words, font_size=5.5,
                  color=GOLD_PALE, spacing=1.3):
    """Fill rectangle with vertical text (rotated 90°)."""
    if w < 4 or h < 10 or not words:
        return
    col_w = font_size * spacing
    avg_cw = font_size * 0.48
    wc = word_cycle(words)
    cx = x + font_size * 0.8
    while cx < x + w - 2:
        cy = y + 3
        while cy < y + h - font_size:
            word = next(wc)
            ww = len(word) * avg_cw
            if cy + ww > y + h:
                break
            group.add(dwg.text(
                word,
                insert=(cx, cy),
                font_size=f'{font_size}px',
                font_family='Georgia, serif',
                fill=color,
                transform=f'rotate(90,{cx},{cy})',
            ))
            cy += ww + font_size * 0.6
        cx += col_w

def add_curved_text(group, path_d, words, font_size=6, color=GOLD_PALE,
                    repeat=1, start_offset='0%'):
    """Add text along an SVG path."""
    pid = next_path_id()
    p = dwg.path(d=path_d, id=pid, fill='none', stroke='none')
    defs.add(p)
    text_str = u' \u00b7 '.join(words) * repeat
    txt = dwg.text('', font_size=f'{font_size}px',
                   font_family='Georgia, serif', fill=color)
    tp = svgwrite.text.TextPath(p, text=text_str, startOffset=start_offset)
    txt.add(tp)
    group.add(txt)

def pointed_arch_path(x1, y_base, x2, y_base2, y_peak):
    """Generate SVG path d-string for a pointed Gothic arch."""
    cx = (x1 + x2) / 2
    w = x2 - x1
    # Control points for Gothic arch (two quadratic curves meeting at peak)
    cp1x = x1 + w * 0.15
    cp1y = y_peak - (y_base - y_peak) * 0.1
    cp2x = x2 - w * 0.15
    cp2y = cp1y
    return (f'M {x1},{y_base} '
            f'Q {cp1x},{cp1y} {cx},{y_peak} '
            f'Q {cp2x},{cp2y} {x2},{y_base2}')

def is_inside_ellipse(px, py, cx, cy, rx, ry):
    return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0

def is_inside_pointed_arch(px, py, x1, x2, y_base, y_peak, h):
    """Test if point is inside a filled pointed arch shape."""
    if py > y_base or py < y_peak:
        return False
    cx = (x1 + x2) / 2
    w = x2 - x1
    # Width at this height (linear interpolation from peak to base)
    t = (py - y_peak) / (y_base - y_peak) if y_base != y_peak else 0
    half_w = (w / 2) * (t ** 0.6)  # curve inward toward peak
    return abs(px - cx) <= half_w

def is_inside_triangle(px, py, x_left, x_right, y_top, y_bottom):
    """Test if inside an isoceles triangle (point at top)."""
    if py < y_top or py > y_bottom:
        return False
    cx = (x_left + x_right) / 2
    w = x_right - x_left
    t = (py - y_top) / (y_bottom - y_top) if y_bottom != y_top else 0
    half_w = (w / 2) * t
    return abs(px - cx) <= half_w

# ============================================================
# BEGIN DRAWING
# ============================================================

# --- Background ---
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

# ============================================================
# EXTERIOR SKY — Names of God, very subtle throughout
# ============================================================
sky = dwg.g(id='sky', opacity='0.7')

def is_outside_cathedral(px, py):
    """True if the point is outside the main cathedral body."""
    # Inside cathedral main rect
    if CAT_L <= px <= CAT_R and CAT_TOP <= py <= CAT_BOT:
        return False
    # Inside spires
    if SPL_L <= px <= SPL_R and SPIRE_TOP <= py <= SPIRE_BASE:
        return False
    if SPR_L <= px <= SPR_R and SPIRE_TOP <= py <= SPIRE_BASE:
        return False
    # Inside transepts
    if TRN_L_L <= px <= TRN_L_R and TRN_TOP <= py <= TRN_BOT:
        return False
    if TRN_R_L <= px <= TRN_R_R and TRN_TOP <= py <= TRN_BOT:
        return False
    return True

fill_shape(sky, EXTERIOR, is_outside_cathedral,
           (0, 0, W, H), font_size=7, color=SKY_TEXT,
           line_spacing=1.25)
dwg.add(sky)

# ============================================================
# SUN — "DEUS CARITAS EST" with glow
# ============================================================
sun = dwg.g(id='sun')
sun_cx, sun_cy = CAT_CX, 45
# Glow rings
for i in range(8, 0, -1):
    sun.add(dwg.circle(
        center=(sun_cx, sun_cy), r=i * 16 + 20,
        fill='none', stroke=GOLD_BRIGHT,
        stroke_width=0.3, opacity=0.04 + i * 0.012,
    ))
sun.add(dwg.text('DEUS CARITAS EST',
    insert=(sun_cx, sun_cy - 2),
    text_anchor='middle', dominant_baseline='middle',
    font_size='14px', font_family='Georgia, serif',
    fill=GOLD_BRIGHT, font_weight='bold', letter_spacing='3',
))
sun.add(dwg.text('God is Love',
    insert=(sun_cx, sun_cy + 16),
    text_anchor='middle',
    font_size='9px', font_family='Georgia, serif',
    fill=GOLD_PALE, letter_spacing='1',
))
dwg.add(sun)

# ============================================================
# SPIRES — Triangular, text conforming to triangle shape
# ============================================================
spires = dwg.g(id='spires')

# Left spire
def inside_spire_l(px, py):
    return is_inside_triangle(px, py, SPL_L, SPL_R, SPIRE_TOP, SPIRE_BASE)
fill_shape(spires, SPIRE_L, inside_spire_l,
           (SPL_L, SPIRE_TOP, SPL_R, SPIRE_BASE),
           font_size=5.5, color=C_TRUTH, line_spacing=1.2)

# Right spire
def inside_spire_r(px, py):
    return is_inside_triangle(px, py, SPR_L, SPR_R, SPIRE_TOP, SPIRE_BASE)
fill_shape(spires, SPIRE_R, inside_spire_r,
           (SPR_L, SPIRE_TOP, SPR_R, SPIRE_BASE),
           font_size=5.5, color=C_TRUTH, line_spacing=1.2)

# Cross on top of each spire
spl_cx = (SPL_L + SPL_R) // 2
spr_cx = (SPR_L + SPR_R) // 2
for cx in [spl_cx, spr_cx]:
    spires.add(dwg.line((cx, SPIRE_TOP - 15), (cx, SPIRE_TOP + 5),
                        stroke=GOLD, stroke_width=1.5))
    spires.add(dwg.line((cx - 6, SPIRE_TOP - 8), (cx + 6, SPIRE_TOP - 8),
                        stroke=GOLD, stroke_width=1.2))

dwg.add(spires)

# ============================================================
# ROSE WINDOW — Circular concentric text rings
# ============================================================
rose = dwg.g(id='rose')

# Concentric text rings
ring_defs = [
    (RW_R * 0.22, 8.5, ROSE_W[:3], GOLD_BRIGHT),
    (RW_R * 0.42, 6,   ROSE_W[:8], GOLD_PALE),
    (RW_R * 0.62, 5.5, ROSE_W,     C_PALE_GOLD),
    (RW_R * 0.80, 5,   ROSE_W,     GOLD_DIM),
    (RW_R * 0.95, 4.5, ROSE_W,     GOLD_DIM),
]

for r, fs, words, col in ring_defs:
    if r < RW_R * 0.3:
        # Center text
        rose.add(dwg.text(words[0],
            insert=(RW_CX, RW_CY + 3),
            text_anchor='middle', dominant_baseline='middle',
            font_size=f'{fs}px', font_family='Georgia, serif',
            fill=col, font_weight='bold',
        ))
        continue
    # Circular textPath
    # SVG arc for a full circle: two half-arcs
    d = (f'M {RW_CX - r},{RW_CY} '
         f'A {r},{r} 0 1 1 {RW_CX + r},{RW_CY} '
         f'A {r},{r} 0 1 1 {RW_CX - r},{RW_CY}')
    add_curved_text(rose, d, words, font_size=fs, color=col, repeat=3)

# Subtle spoke lines
for a in range(0, 360, 30):
    rad = math.radians(a)
    rose.add(dwg.line(
        start=(RW_CX + RW_R * 0.18 * math.cos(rad),
               RW_CY + RW_R * 0.18 * math.sin(rad)),
        end=(RW_CX + RW_R * 0.98 * math.cos(rad),
             RW_CY + RW_R * 0.98 * math.sin(rad)),
        stroke=GOLD, stroke_width=0.3, opacity='0.25',
    ))

# Outer circle
rose.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R,
                    fill='none', stroke=GOLD, stroke_width=1.0, opacity='0.4'))
dwg.add(rose)

# ============================================================
# CLERESTORY WINDOWS — 7 Sacraments, pointed arch shape
# ============================================================
wins = dwg.g(id='windows')
sac_order = ['baptism', 'confirmation', 'penance',
             'eucharist',
             'anointing', 'orders', 'matrimony']
n_wins = 7
gap = 8
CW_L2 = CAT_L + 20
CW_R2 = CAT_R - 20
win_w = (CW_R2 - CW_L2 - (n_wins - 1) * gap) / n_wins

for i, sac in enumerate(sac_order):
    wx = CW_L2 + i * (win_w + gap)
    wy_base = CW_BOT
    wy_peak = CW_TOP
    wx2 = wx + win_w
    wcx = (wx + wx2) / 2
    col = SAC_COLORS[sac]

    # Fill text conforming to pointed arch shape
    def make_inside(wx=wx, wx2=wx2, wy_base=wy_base, wy_peak=wy_peak):
        def inside(px, py):
            return is_inside_pointed_arch(px, py, wx, wx2, wy_base, wy_peak, wy_base - wy_peak)
        return inside

    fill_shape(wins, SAC_WORDS[sac], make_inside(),
               (wx, wy_peak, wx2, wy_base),
               font_size=5, color=col, line_spacing=1.2)

    # Subtle arch outline
    arch_d = pointed_arch_path(wx, wy_base, wx2, wy_base, wy_peak)
    wins.add(dwg.path(d=arch_d + f' L {wx2},{wy_base} L {wx},{wy_base} Z',
                     fill='none', stroke=GOLD, stroke_width=0.4, opacity='0.3'))

dwg.add(wins)

# ============================================================
# TRIFORIUM — Gifts & Fruits (horizontal band)
# ============================================================
tri = dwg.g(id='triforium')
fill_rect(tri, CAT_L + 10, TRI_TOP, CAT_R - CAT_L - 20, TRI_BOT - TRI_TOP,
          GIFTS_FRUITS, font_size=6, color=C_PALE_GOLD, line_spacing=1.25)
dwg.add(tri)

# ============================================================
# VAULT RIBS — Scripture on love, diagonal textPaths from pillars to peak
# ============================================================
vault = dwg.g(id='vault')

# Vault ribs from each pillar top to vault peak
for px in PIL_X:
    pcx = px + PIL_W / 2
    d = f'M {pcx},{PIL_TOP} Q {(pcx + CAT_CX) / 2},{VAULT_PEAK_Y} {CAT_CX},{VAULT_PEAK_Y}'
    add_curved_text(vault, d, VAULT_SCRIPTURE,
                    font_size=5.5, color=C_PALE_GOLD, repeat=2)

# Transverse ribs
for i in range(len(PIL_X) - 1):
    p1 = PIL_X[i] + PIL_W / 2
    p2 = PIL_X[i + 1] + PIL_W / 2
    mid_x = (p1 + p2) / 2
    peak_y = PIL_TOP - 30
    d = f'M {p1},{PIL_TOP} Q {mid_x},{peak_y} {p2},{PIL_TOP}'
    add_curved_text(vault, d, VAULT_SCRIPTURE,
                    font_size=5, color=GOLD_DIM, repeat=1)

dwg.add(vault)

# ============================================================
# LATERAL WALLS — Cardinal Virtues, vertical text
# ============================================================
lat = dwg.g(id='lateral')
fill_vertical(lat, CAT_L + 2, PIL_TOP, 48, PIL_BOT - PIL_TOP,
              LATERAL_VIRTUES, font_size=5.5, color=C_JUSTICE)
fill_vertical(lat, CAT_R - 50, PIL_TOP, 48, PIL_BOT - PIL_TOP,
              LATERAL_VIRTUES, font_size=5.5, color=C_JUSTICE)
dwg.add(lat)

# ============================================================
# FOUR PILLARS — Vertical text, each pillar its tradition color
# ============================================================
pil = dwg.g(id='pillars')
pil_words  = [TRUTH_W, JUSTICE_W, MERCY_W, SACRIFICE_W]
pil_colors = [C_TRUTH, C_JUSTICE, C_MERCY, C_SACRIFICE]
pil_labels = ['TRUTH', 'JUSTICE', 'MERCY', 'SACRIFICE']

for i, px in enumerate(PIL_X):
    fill_vertical(pil, px, PIL_TOP, PIL_W, PIL_BOT - PIL_TOP,
                  pil_words[i], font_size=5, color=pil_colors[i],
                  spacing=1.15)

dwg.add(pil)

# ============================================================
# NAVE BAYS — Theological Virtues
# ============================================================
nav = dwg.g(id='nave')
bay_pairs = [
    (PIL_X[0] + PIL_W, PIL_X[1], FAITH_W, C_PALE_GOLD),
    (PIL_X[1] + PIL_W, PIL_X[2], CHARITY_W, C_PALE_GOLD),
    (PIL_X[2] + PIL_W, PIL_X[3], HOPE_W, C_PALE_GOLD),
]
for bl, br, words, col in bay_pairs:
    fill_rect(nav, bl + 4, PIL_TOP + 20, br - bl - 8, PIL_BOT - PIL_TOP - 40,
              words, font_size=6, color=col, line_spacing=1.3)

# Nave arches between pillars (curved text)
for i in range(len(PIL_X) - 1):
    p1 = PIL_X[i] + PIL_W / 2
    p2 = PIL_X[i + 1] + PIL_W / 2
    mid_x = (p1 + p2) / 2
    peak_y = PIL_TOP - 20
    d = pointed_arch_path(p1, PIL_TOP, p2, PIL_TOP, peak_y)
    w = [FAITH_W, CHARITY_W, HOPE_W][i]
    add_curved_text(nav, d, w, font_size=5.5, color=GOLD)

dwg.add(nav)

# ============================================================
# TRANSEPTS — Beatitudes (left), Spiritual Works (right)
# ============================================================
trn = dwg.g(id='transepts')
fill_rect(trn, TRN_L_L, TRN_TOP, TRN_L_R - TRN_L_L, TRN_BOT - TRN_TOP,
          BEATITUDES, font_size=5.5, color=C_MERCY, line_spacing=1.25)
fill_rect(trn, TRN_R_L, TRN_TOP, TRN_R_R - TRN_R_L, TRN_BOT - TRN_TOP,
          SPIRITUAL_MERCY, font_size=5.5, color=C_PALE_GOLD, line_spacing=1.25)
dwg.add(trn)

# ============================================================
# APSE — Elliptical shape, core definition
# ============================================================
apse = dwg.g(id='apse')

def inside_apse(px, py):
    # Upper half of ellipse (only the top portion visible behind altar)
    if py > APS_CY or py < APS_TOP:
        return False
    return is_inside_ellipse(px, py, APS_CX, APS_CY, APS_RX, APS_RY)

fill_shape(apse, APSE_W, inside_apse,
           (APS_CX - APS_RX, APS_TOP, APS_CX + APS_RX, APS_CY),
           font_size=6, color=C_IVORY, line_spacing=1.25)

# Curved text along apse arch
apse_d = (f'M {APS_CX - APS_RX},{APS_CY} '
          f'A {APS_RX},{APS_RY} 0 0 1 {APS_CX + APS_RX},{APS_CY}')
add_curved_text(apse, apse_d, APSE_W, font_size=5.5, color=C_IVORY, repeat=2)

dwg.add(apse)

# ============================================================
# ALTAR — Dense Eucharistic vocabulary
# ============================================================
alt = dwg.g(id='altar')
fill_rect(alt, ALT_L, ALT_TOP, ALT_R - ALT_L, ALT_BOT - ALT_TOP,
          EUCHARIST_ALTAR, font_size=5.5, color=C_TRUTH, line_spacing=1.2)
# "Deus Caritas Est" prominent
alt.add(dwg.text('Deus Caritas Est',
    insert=((ALT_L + ALT_R) / 2, ALT_BOT + 16),
    text_anchor='middle',
    font_size='7px', font_family='Georgia, serif',
    fill=GOLD_BRIGHT, font_weight='bold', letter_spacing='1.5',
))
dwg.add(alt)

# ============================================================
# THE CRUCIFIX — Cross + Christ's body, prominent
# ============================================================
crx = dwg.g(id='crucifix')

# Vertical bar — dense sacrifice words, vertical text
fill_vertical(crx, CRX_CX - CRX_VW // 2, CRX_TOP,
              CRX_VW, CRX_BOT - CRX_TOP,
              CROSS_W, font_size=5.5, color=C_CROSS, spacing=1.1)

# Horizontal bar — sacrifice words, horizontal text
fill_rect(crx, CRX_BL, CRX_BY, CRX_BR - CRX_BL, CRX_BH,
          CROSS_W, font_size=5.5, color=C_CROSS, line_spacing=1.15)

# Christ: HEAD (circular text)
head_d = (f'M {C_HEAD_CX - C_HEAD_R},{C_HEAD_CY} '
          f'A {C_HEAD_R},{C_HEAD_R} 0 1 1 {C_HEAD_CX + C_HEAD_R},{C_HEAD_CY} '
          f'A {C_HEAD_R},{C_HEAD_R} 0 1 1 {C_HEAD_CX - C_HEAD_R},{C_HEAD_CY}')
add_curved_text(crx, head_d, CHR_HEAD_W, font_size=4.5, color=C_CHRIST, repeat=2)
# Inner ring
head_d2 = (f'M {C_HEAD_CX - C_HEAD_R * 0.5},{C_HEAD_CY} '
           f'A {C_HEAD_R * 0.5},{C_HEAD_R * 0.5} 0 1 1 {C_HEAD_CX + C_HEAD_R * 0.5},{C_HEAD_CY} '
           f'A {C_HEAD_R * 0.5},{C_HEAD_R * 0.5} 0 1 1 {C_HEAD_CX - C_HEAD_R * 0.5},{C_HEAD_CY}')
add_curved_text(crx, head_d2, ['INRI', 'Ecce Homo', 'Emmanuel'],
                font_size=4, color=C_CHRIST, repeat=2)

# Christ: TORSO (vertical text, denser)
torso_l = CRX_CX - 22
torso_r = CRX_CX + 22
torso_t = C_HEAD_CY + C_HEAD_R + 2
torso_b = CRX_BY - 2
fill_vertical(crx, torso_l, torso_t, torso_r - torso_l, torso_b - torso_t,
              CHR_BODY_W, font_size=4.5, color=C_CHRIST, spacing=1.0)

# Christ: ARMS (horizontal along crossbar)
arm_l_l, arm_l_r = CRX_BL + 4, torso_l - 4
arm_r_l, arm_r_r = torso_r + 4, CRX_BR - 4
arm_y = CRX_BY + 6
for words_chunk in [CHR_ARMS_W[:4], CHR_ARMS_W[4:]]:
    fill_rect(crx, arm_l_l, CRX_BY + 4, arm_l_r - arm_l_l, CRX_BH - 8,
              words_chunk, font_size=4.5, color=C_CHRIST, line_spacing=1.15)
    fill_rect(crx, arm_r_l, CRX_BY + 4, arm_r_r - arm_r_l, CRX_BH - 8,
              words_chunk, font_size=4.5, color=C_CHRIST, line_spacing=1.15)

# Christ: LEGS (vertical text, narrow)
leg_l = CRX_CX - 16
leg_r = CRX_CX + 16
leg_t = CRX_BY + CRX_BH + 2
leg_b = CRX_BOT - 8
fill_vertical(crx, leg_l, leg_t, leg_r - leg_l, leg_b - leg_t,
              ['Cornerstone', 'Foundation', 'He humbled himself',
               'Servant', 'Death swallowed in victory', 'He is risen', 'Alleluia'],
              font_size=4.5, color=C_CHRIST, spacing=1.0)

dwg.add(crx)

# ============================================================
# FLOOR — Corporal Works of Mercy
# ============================================================
flr = dwg.g(id='floor')
fill_rect(flr, CAT_L + 55, FLR_TOP, CAT_R - CAT_L - 110, FLR_BOT - FLR_TOP,
          FLOOR_W, font_size=6, color=C_SACRIFICE, line_spacing=1.25)
dwg.add(flr)

# ============================================================
# FOUNDATION — Ten Commandments, stepped wider rows
# ============================================================
fnd = dwg.g(id='foundation')
n_steps = 5
step_h = (FND_BOT - FND_TOP) / n_steps
for s in range(n_steps):
    sy = FND_TOP + s * step_h
    inset = (n_steps - s) * 15
    sl = CAT_L - 30 + inset
    sr = CAT_R + 30 - inset
    fill_rect(fnd, sl, sy, sr - sl, step_h,
              COMMANDMENTS, font_size=5.5, color=C_IVORY,
              line_spacing=1.2)
dwg.add(fnd)

# ============================================================
# ARCHITECTURAL OUTLINES — very subtle gold lines
# ============================================================
arch_g = dwg.g(id='outlines', opacity='0.25')

# Cathedral main rect
arch_g.add(dwg.rect((CAT_L, CAT_TOP), (CAT_R - CAT_L, CAT_BOT - CAT_TOP),
                     fill='none', stroke=GOLD, stroke_width=0.6))

# Spire outlines
for sl, sr in [(SPL_L, SPL_R), (SPR_L, SPR_R)]:
    scx = (sl + sr) // 2
    arch_g.add(dwg.polygon(
        points=[(sl, SPIRE_BASE), (scx, SPIRE_TOP), (sr, SPIRE_BASE)],
        fill='none', stroke=GOLD, stroke_width=0.6))

# Transept outlines
arch_g.add(dwg.rect((TRN_L_L, TRN_TOP),
                     (TRN_L_R - TRN_L_L, TRN_BOT - TRN_TOP),
                     fill='none', stroke=GOLD, stroke_width=0.5))
arch_g.add(dwg.rect((TRN_R_L, TRN_TOP),
                     (TRN_R_R - TRN_R_L, TRN_BOT - TRN_TOP),
                     fill='none', stroke=GOLD, stroke_width=0.5))

# Pillar outlines
for px in PIL_X:
    arch_g.add(dwg.rect((px, PIL_TOP), (PIL_W, PIL_BOT - PIL_TOP),
                        fill='none', stroke=GOLD, stroke_width=0.4))

# Altar outline
arch_g.add(dwg.rect((ALT_L, ALT_TOP), (ALT_R - ALT_L, ALT_BOT - ALT_TOP),
                     fill='none', stroke=GOLD, stroke_width=0.8))

# Cross outline
arch_g.add(dwg.rect((CRX_CX - CRX_VW // 2, CRX_TOP),
                     (CRX_VW, CRX_BOT - CRX_TOP),
                     fill='none', stroke=GOLD, stroke_width=0.8))
arch_g.add(dwg.rect((CRX_BL, CRX_BY),
                     (CRX_BR - CRX_BL, CRX_BH),
                     fill='none', stroke=GOLD, stroke_width=0.8))

# Triforium lines
arch_g.add(dwg.line((CAT_L, TRI_TOP), (CAT_R, TRI_TOP),
                    stroke=GOLD, stroke_width=0.4))
arch_g.add(dwg.line((CAT_L, TRI_BOT), (CAT_R, TRI_BOT),
                    stroke=GOLD, stroke_width=0.4))

# Foundation steps
for s in range(n_steps):
    sy = FND_TOP + s * step_h
    inset = (n_steps - s) * 15
    sl = CAT_L - 30 + inset
    sr = CAT_R + 30 - inset
    arch_g.add(dwg.line((sl, sy), (sr, sy),
                        stroke=GOLD, stroke_width=0.4))

# Apse arc
arch_g.add(dwg.ellipse(center=(APS_CX, APS_CY), r=(APS_RX, APS_RY),
                       fill='none', stroke=GOLD, stroke_width=0.5))

dwg.add(arch_g)

# ============================================================
# PILLAR LABELS
# ============================================================
for i, px in enumerate(PIL_X):
    dwg.add(dwg.text(
        pil_labels[i],
        insert=(px + PIL_W / 2, PIL_BOT + 14),
        text_anchor='middle', font_size='6px',
        font_family='Georgia, serif',
        fill=pil_colors[i], font_weight='bold', letter_spacing='0.8',
    ))

# ============================================================
# SAVE
# ============================================================
dwg.save()
print(f'\n✓ Cathedral SVG v2 saved to:\n  {OUTPUT}\n')
