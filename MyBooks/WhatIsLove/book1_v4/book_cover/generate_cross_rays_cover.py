#!/usr/bin/env python3
"""
What Is Love? — Cross + Rays Book Cover SVG
=============================================
Simple. Powerful. A cross at the center. 4 main rays (the pillars of love).
7 sub-rays (the sacraments). Everything is words. The light of God's love
radiating from the cross into the world.
"""

import svgwrite
import math
import random

random.seed(13)

W, H = 1200, 1800
OUTPUT = '/Users/patiman/Desktop/designer-output/what-is-love-cross-rays-v1.svg'

dwg = svgwrite.Drawing(OUTPUT, size=(f'{W}px', f'{H}px'),
                        viewBox=f'0 0 {W} {H}', profile='full')
defs = dwg.defs

# ============================================================
# COLORS
# ============================================================
BG          = '#0a0204'
SKY_C       = '#180810'
CROSS_C     = '#7a1010'
CROSS_C2    = '#501010'
GOLD_B      = '#F0D060'

C_TRUTH     = '#c8a830'
C_JUSTICE   = '#7848b0'
C_MERCY     = '#c89098'
C_SACRIFICE = '#b82020'

# Sacrament colors (jewel tones)
C_BAPTISM   = '#4080b0'
C_CONFIRM   = '#c07040'
C_EUCHARIST = '#d0a028'
C_PENANCE   = '#8858b8'
C_ANOINT    = '#48a048'
C_ORDERS    = '#c0a050'
C_MATRIMONY = '#c06888'

# ============================================================
# GEOMETRY
# ============================================================
CX, CY = 600, 880  # cross center (slightly above vertical center)

# Cross bars
CROSS_W = 90       # bar width
CROSS_VT = 200     # vertical bar top
CROSS_VB = 1580    # vertical bar bottom
CROSS_HL = 100     # horizontal bar left
CROSS_HR = 1100    # horizontal bar right
CROSS_HT = CY - CROSS_W // 2
CROSS_HB = CY + CROSS_W // 2

# Ray parameters
# Main rays at diagonals, sub-rays between cross arms and main rays
# Cross arms at: 0° (right), 90° (down), 180° (left), 270° (up)
# Main rays at: 45°, 135°, 225°, 315° (diagonals)
# Sub-rays at intermediate angles

MAIN_RAY_HW = 14   # half-width in degrees
SUB_RAY_HW  = 8    # half-width in degrees
RAY_INNER   = 70   # start distance from center (outside cross overlap)
RAY_OUTER   = 950  # max distance

# ============================================================
# WORD POOLS
# ============================================================

SKY_WORDS = [
    "Father", "Abba", "YHWH", "I AM", "Creator", "Almighty", "Holy",
    "Eternal", "Infinite", "Alpha", "Omega", "El Shaddai", "Adonai",
    "Ancient of Days", "Ruach", "Spirit", "Light", "Life", "Logos",
    "Providence", "Trinity", "Perichoresis", "Triune", "One God",
    "Bond of Love", "Comforter", "Paraclete", "Transcendent",
    "Immanent", "Source", "Without end", "In the beginning",
    "Let there be light", "Perfect goodness", "Ground of being",
    "Lord of Lords", "King of Kings", "Breath of God",
    "Divine communion", "Gift of self", "He who is",
    "love", "truth", "mercy", "justice", "grace", "peace",
    "faith", "hope", "charity", "covenant", "communion",
    "redemption", "salvation", "holiness", "glory", "wisdom",
    "prayer", "virtue", "sacred", "divine", "blessed",
    "agape", "caritas", "hesed", "misericordia",
    "veritas", "lux", "pax", "sanctus", "gloria",
    "amen", "alleluia", "gospel", "psalm", "creed",
]

CROSS_WORDS = [
    "Sacrifice", "Atonement", "Calvary", "Passion", "Crucified",
    "Tetelestai", "It is finished", "Ransom", "Redemption",
    "Agnus Dei", "By his wounds", "Pierced", "Blood", "Nailed",
    "Poured out", "Obedient unto death", "Good Friday", "Golgotha",
    "Propitiation", "Expiation", "Via Dolorosa", "Lamb of God",
    "Consummatum est", "Covenant blood", "Greater love",
    "Lay down his life", "Self-offering", "Cup of suffering",
    "Not my will but yours", "Gethsemane", "Father forgive them",
    "Into your hands", "I thirst", "Woman behold your son",
    "Today you will be with me", "Why have you forsaken me",
    "Carried his cross", "Fell three times", "Mary stood",
    "Stabat Mater", "He is risen", "Resurrection", "Victor",
    "Death swallowed up", "Blood of the new covenant",
    "Once for all", "Eternal sacrifice", "High priest forever",
    "Paschal mystery", "Passover", "Blood of the lamb",
    "This is my Body", "This is my Blood", "Do this in memory",
    "For God so loved the world", "He gave his only Son",
    "Kenosis", "Self-emptying", "Fiat", "Total gift of self",
    "He humbled himself", "Servant", "INRI",
    "Ecce Homo", "Man of sorrows", "Acquainted with grief",
    "Wounded for our transgressions", "Bruised for our iniquities",
    "Chastisement upon him", "By his stripes we are healed",
    "Led like a lamb to slaughter", "Cut off from the living",
    "Offering", "Oblation", "Immolation", "Memorial",
    "Re-presentation", "Source and summit", "Anamnesis",
    "New and eternal covenant", "Love unto the end",
]

TRUTH_WORDS = [
    "Truth", "Logos", "Word", "Light", "Revelation", "Scripture",
    "Tradition", "Magisterium", "Doctrine", "Creed", "Gospel",
    "Emet", "Aletheia", "Illumination", "Transfiguration",
    "Way Truth Life", "Truth sets free", "Word became flesh",
    "Your Word is truth", "Fides et Ratio", "Wisdom",
    "Understanding", "Knowledge", "Reason", "Intellect",
    "Uncreated Light", "Verbum Domini", "Evangelization",
    "Kerygma", "Testimony", "Witness", "Catechesis",
    "Deposit of Faith", "Inerrancy", "Orthodoxy",
    "In principio erat Verbum", "Lux aeterna",
    "Faith seeking understanding", "Clarity", "Certainty",
    "Canon", "Inspired Word", "Proclamation",
]

JUSTICE_WORDS = [
    "Justice", "Righteousness", "Mishpat", "Dikaiosyne",
    "Equity", "Fairness", "Accountability", "Restitution",
    "Right order", "Covenant law", "Divine law", "Moral law",
    "Natural law", "Commandments", "Conscience", "Decalogue",
    "Sovereignty", "Authority", "Providence", "Common good",
    "Solidarity", "Subsidiarity", "Human dignity", "Imago Dei",
    "Rectitude", "Suum cuique", "Judgment", "Proportionality",
    "Social justice", "Commutative justice", "Distributive",
    "Let justice roll like a river", "Do justice love mercy",
    "Sanctity of life", "Synderesis", "Reparation",
    "Moral conscience", "Law written on the heart",
    "Foundation of justice", "Divine governance",
    "Ten Commandments", "Precepts", "Statutes",
]

MERCY_WORDS = [
    "Mercy", "Compassion", "Hesed", "Rahamim", "Misericordia",
    "Eleos", "Forgiveness", "Pardon", "Absolution", "Grace",
    "Gift", "Healing", "Reconciliation", "Tenderness",
    "Lovingkindness", "Patience", "Forbearance", "Gentleness",
    "Divine Mercy", "Living water", "Pale ray", "Font of mercy",
    "Mercy endures forever", "Prodigal Father", "Lost sheep",
    "Come to me all who are weary", "Seventy times seven",
    "Be merciful as your Father", "I desire mercy",
    "Blessed are the merciful", "Blood and water",
    "Wounded side", "Clemency", "Gratuitous",
    "Abundance", "Solidarity", "Presence", "Accompanying",
    "Comfort the afflicted", "Bind up the brokenhearted",
    "He will wipe away every tear", "Lost coin",
]

SACRIFICE_WORDS = [
    "Sacrifice", "Offering", "Oblation", "Kenosis",
    "Cross", "Calvary", "Passion", "Blood", "Lamb",
    "Atonement", "Propitiation", "Expiation", "Redemption",
    "Martyrdom", "Self-denial", "Fiat", "Total gift",
    "Not my will", "Obedient unto death", "Poured out",
    "Take up your cross", "Follow me", "It is finished",
    "Without shedding of blood", "Covenant blood",
    "Greater love has no one", "Lay down his life",
    "Gethsemane", "Cup of suffering", "Red ray",
    "Death to self", "Immolation", "Self-emptying",
    "Via Dolorosa", "Golgotha", "Good Friday",
    "He gave himself", "Paschal mystery", "Passover",
    "Blood of the lamb", "Eternal sacrifice",
]

SAC_WORDS = {
    'baptism': [
        "Baptism", "Rebirth", "Water", "Spirit", "Font", "Immersion",
        "Washing", "Cleansing", "Adoption", "Sonship", "Regeneration",
        "Chrism", "You are my beloved", "Born of water and spirit",
        "Death to sin", "Rising to new life", "White garment",
        "Candle", "New creation", "Sealed", "Incorporated",
        "Triple immersion", "In the name of the Father",
        "Original sin removed", "Laver of regeneration",
    ],
    'confirmation': [
        "Confirmation", "Seal", "Strengthening", "Mission", "Witness",
        "Gifts of Spirit", "Chrism", "Bishop", "Laying on of hands",
        "Pentecost", "Fire", "Wind", "Tongues", "Anointing",
        "Mature discipleship", "Apostolic mission", "Soldier of Christ",
        "Empowered", "Sent forth", "Be sealed with the gift",
    ],
    'eucharist': [
        "Eucharist", "Real Presence", "Transubstantiation",
        "Body Blood Soul Divinity", "This is my Body",
        "Bread of Life", "Communion", "Source and summit",
        "Consecration", "Last Supper", "Altar", "Chalice", "Host",
        "Agnus Dei", "Monstrance", "Adoration", "Living Bread",
        "Corpus Christi", "Viaticum", "Do this in memory",
        "Mysterium Fidei", "Sanctus", "Epiclesis",
    ],
    'penance': [
        "Penance", "Reconciliation", "Confession", "Contrition",
        "Absolution", "I absolve you", "Prodigal son", "Healing",
        "Tribunal of mercy", "Amendment of life", "Forgiven",
        "Restored", "Seal of confession", "Your sins are forgiven",
        "Confiteor", "Act of contrition", "Examination",
    ],
    'anointing': [
        "Anointing of the Sick", "Oil", "Prayer", "Comfort",
        "Healing", "Redemptive suffering", "Peace", "Fortitude",
        "Union with Christ", "Preparation", "Viaticum", "Elders",
        "Laying on of hands", "Strength", "Is anyone among you sick",
        "Prayer of faith will save the sick",
    ],
    'orders': [
        "Holy Orders", "Priesthood", "Ordination", "Alter Christus",
        "Bishop", "Priest", "Deacon", "Shepherd", "Ministry",
        "Apostolic succession", "Sacred character", "Celibacy",
        "Fishers of men", "Ambassador for Christ", "Melchizedek",
        "Laying on of hands", "Consecrated", "Sent",
    ],
    'matrimony': [
        "Matrimony", "Marriage", "Covenant", "Nuptial bond",
        "Fidelity", "Fruitfulness", "Indissolubility",
        "Domestic church", "One flesh", "Gift of self", "Family",
        "Free total faithful fruitful", "Spousal love",
        "Theology of the Body", "Nuptial meaning", "Consent",
        "What God has joined", "Children", "New life",
    ],
}

# ============================================================
# RAY LAYOUT
# ============================================================
# Cross arms at 0° (right), 90° (down), 180° (left), 270° (up)
# 4 main rays at diagonals: 45°, 135°, 225°, 315°
# 7 sub-rays distributed between

MAIN_RAYS = [
    (315, C_TRUTH,     TRUTH_WORDS,     'TRUTH'),      # upper-right
    (135, C_JUSTICE,   JUSTICE_WORDS,    'JUSTICE'),     # lower-right
    (225, C_MERCY,     MERCY_WORDS,     'MERCY'),       # lower-left
    (45,  C_SACRIFICE, SACRIFICE_WORDS, 'SACRIFICE'),   # upper-left → wait
]

# Actually let me think about this more carefully.
# Looking at the image from the viewer's perspective:
# Up = 270°, Down = 90°, Left = 180°, Right = 0°
#
# Main rays at diagonals:
#   Upper-right (315°) = Truth (light ascending)
#   Lower-right (45°)  = Justice (descending order)
#   Lower-left (135°)  = Sacrifice (descending offering)
#   Upper-left (225°)  = Mercy (ascending grace)
#
# Sub-rays in between (7 sacraments distributed):

MAIN_RAYS = [
    (315, C_TRUTH,     TRUTH_WORDS,     MAIN_RAY_HW),
    (45,  C_JUSTICE,   JUSTICE_WORDS,   MAIN_RAY_HW),
    (135, C_SACRIFICE, SACRIFICE_WORDS, MAIN_RAY_HW),
    (225, C_MERCY,     MERCY_WORDS,     MAIN_RAY_HW),
]

# 7 sub-rays placed between cross arms and main rays
# Angles: roughly every ~32° in the gaps
SUB_RAYS = [
    (280, C_BAPTISM,   SAC_WORDS['baptism'],      SUB_RAY_HW),   # near top
    (340, C_CONFIRM,   SAC_WORDS['confirmation'],  SUB_RAY_HW),   # upper-right
    (20,  C_EUCHARIST, SAC_WORDS['eucharist'],     SUB_RAY_HW),   # right-upper
    (70,  C_PENANCE,   SAC_WORDS['penance'],       SUB_RAY_HW),   # right-lower
    (110, C_ANOINT,    SAC_WORDS['anointing'],      SUB_RAY_HW),   # lower-right
    (160, C_ORDERS,    SAC_WORDS['orders'],         SUB_RAY_HW),   # lower-left
    (200, C_MATRIMONY, SAC_WORDS['matrimony'],      SUB_RAY_HW),   # left-lower
]

# ============================================================
# SHAPE FUNCTIONS
# ============================================================

def inside_cross(x, y):
    in_v = (CX - CROSS_W // 2 <= x <= CX + CROSS_W // 2
            and CROSS_VT <= y <= CROSS_VB)
    in_h = (CROSS_HL <= x <= CROSS_HR
            and CROSS_HT <= y <= CROSS_HB)
    return in_v or in_h

def inside_ray(x, y, angle_deg, half_width_deg, inner=RAY_INNER, outer=RAY_OUTER):
    dx = x - CX
    dy = y - CY
    dist = math.hypot(dx, dy)
    if dist < inner or dist > outer:
        return False
    pt_angle = math.degrees(math.atan2(dy, dx))
    diff = (pt_angle - angle_deg + 180) % 360 - 180
    # Slight widening with distance
    hw = half_width_deg * (0.8 + 0.4 * (dist / outer))
    return abs(diff) <= hw

def inside_ray_no_cross(x, y, angle_deg, half_width_deg):
    """Inside ray but not overlapping the cross."""
    if inside_cross(x, y):
        return False
    return inside_ray(x, y, angle_deg, half_width_deg)

# ============================================================
# FILL ENGINE
# ============================================================

def dense_fill(group, words, is_inside_fn, bbox,
               color, base_size=3.8, size_var=2.0,
               line_spacing=1.06, opacity_range=(0.5, 0.95),
               hero_count=0, hero_size=(8, 14), hero_opacity=0.85):
    x0, y0, x1, y1 = bbox
    pool = list(words)
    random.shuffle(pool)
    wi = 0
    total = len(pool)

    cy = y0 + base_size + 0.3
    while cy < y1 - 0.5:
        fs = base_size + random.uniform(0, size_var)
        lh = fs * line_spacing
        op = random.uniform(*opacity_range)

        lx = x0
        while lx < x1 and not is_inside_fn(lx, cy):
            lx += 1.0
        rx = x1
        while rx > lx and not is_inside_fn(rx, cy):
            rx -= 1.0

        avail = rx - lx - 1
        if avail > fs * 1.5:
            avg_cw = fs * 0.44
            tokens = []
            cx_used = 0
            while cx_used < avail:
                word = pool[wi % total]
                wi += 1
                ww = len(word) * avg_cw
                gap = avg_cw * 0.5 if tokens else 0
                if cx_used + gap + ww > avail:
                    break
                tokens.append(word)
                cx_used += gap + ww
            if tokens:
                group.add(dwg.text(
                    ' '.join(tokens),
                    insert=(lx + 0.5, cy),
                    font_size=f'{fs:.1f}px',
                    font_family='Georgia, serif',
                    fill=color, opacity=f'{op:.2f}',
                ))
        cy += lh

    if hero_count > 0:
        random.shuffle(pool)
        placed = 0
        for _ in range(hero_count * 40):
            if placed >= hero_count:
                break
            hx = random.uniform(x0 + 5, x1 - 5)
            hy = random.uniform(y0 + 10, y1 - 5)
            if is_inside_fn(hx, hy):
                word = pool[placed % total]
                hs = random.uniform(*hero_size)
                rot = random.uniform(-8, 8)
                group.add(dwg.text(
                    word, insert=(hx, hy),
                    font_size=f'{hs:.1f}px',
                    font_family='Georgia, serif',
                    fill=color, opacity=f'{hero_opacity}',
                    font_weight='bold',
                    transform=f'rotate({rot:.1f},{hx:.0f},{hy:.0f})',
                ))
                placed += 1


def gradient_fill(group, words, is_inside_fn, bbox,
                  color, center=(CX, CY), max_dist=800,
                  base_size=3.5, size_var=1.8,
                  line_spacing=1.06, power=1.3):
    """Fill with opacity fading from center outward."""
    x0, y0, x1, y1 = bbox
    pool = list(words)
    random.shuffle(pool)
    wi = 0
    total = len(pool)
    ccx, ccy = center

    cy = y0 + base_size + 0.3
    while cy < y1 - 0.5:
        fs = base_size + random.uniform(0, size_var)
        lh = fs * line_spacing

        lx = x0
        while lx < x1 and not is_inside_fn(lx, cy):
            lx += 1.0
        rx = x1
        while rx > lx and not is_inside_fn(rx, cy):
            rx -= 1.0

        avail = rx - lx - 1
        if avail > fs * 1.5:
            mid_x = (lx + rx) / 2
            dist = math.hypot(mid_x - ccx, cy - ccy)
            fade = max(0.05, 1.0 - (dist / max_dist) ** power)
            op = fade * random.uniform(0.45, 0.9)

            avg_cw = fs * 0.44
            tokens = []
            cx_used = 0
            while cx_used < avail:
                word = pool[wi % total]
                wi += 1
                ww = len(word) * avg_cw
                gap = avg_cw * 0.5 if tokens else 0
                if cx_used + gap + ww > avail:
                    break
                tokens.append(word)
                cx_used += gap + ww
            if tokens:
                group.add(dwg.text(
                    ' '.join(tokens),
                    insert=(lx + 0.5, cy),
                    font_size=f'{fs:.1f}px',
                    font_family='Georgia, serif',
                    fill=color, opacity=f'{op:.2f}',
                ))
        cy += lh


# ============================================================
# BUILD
# ============================================================

# Background
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

# Layer 1: Subtle background — Names of God everywhere
sky = dwg.g(id='sky')
def not_cross(x, y):
    return not inside_cross(x, y)
dense_fill(sky, SKY_WORDS, not_cross, (0, 0, W, H),
           SKY_C, base_size=5, size_var=2.5,
           line_spacing=1.04, opacity_range=(0.3, 0.6))
dwg.add(sky)

# Layer 2: "DEUS CARITAS EST"
ins = dwg.g(id='inscription')
ins.add(dwg.text('DEUS CARITAS EST',
    insert=(CX, 90), text_anchor='middle',
    dominant_baseline='middle', font_size='16px',
    font_family='Georgia, serif', fill=GOLD_B,
    font_weight='bold', letter_spacing='4', opacity='0.65'))
ins.add(dwg.text('God is Love',
    insert=(CX, 115), text_anchor='middle',
    font_size='9px', font_family='Georgia, serif',
    fill=C_TRUTH, letter_spacing='2', opacity='0.45'))
dwg.add(ins)

# Layer 3: RAYS — gradient fill, fading from cross center outward
rays = dwg.g(id='rays')

# Main rays (4 pillars) — wider, brighter
for angle, color, words, hw in MAIN_RAYS:
    def make_test(a=angle, h=hw):
        def fn(x, y):
            return inside_ray_no_cross(x, y, a, h)
        return fn
    gradient_fill(rays, words, make_test(), (0, 0, W, H),
                  color, center=(CX, CY), max_dist=850,
                  base_size=3.5, size_var=2, power=1.1)

# Sub-rays (7 sacraments) — thinner, slightly dimmer
for angle, color, words, hw in SUB_RAYS:
    def make_test(a=angle, h=hw):
        def fn(x, y):
            return inside_ray_no_cross(x, y, a, h)
        return fn
    gradient_fill(rays, words, make_test(), (0, 0, W, H),
                  color, center=(CX, CY), max_dist=750,
                  base_size=3, size_var=1.5, power=1.4)

dwg.add(rays)

# Layer 4: The Cross — dense, deep crimson
cross = dwg.g(id='cross')
dense_fill(cross, CROSS_WORDS, inside_cross,
           (CROSS_HL - 5, CROSS_VT - 5, CROSS_HR + 5, CROSS_VB + 5),
           CROSS_C, base_size=3.5, size_var=2.0,
           line_spacing=1.04, opacity_range=(0.55, 0.95),
           hero_count=30, hero_size=(7, 13), hero_opacity=0.8)
# Second layer for depth
dense_fill(cross, CROSS_WORDS[::-1], inside_cross,
           (CROSS_HL, CROSS_VT, CROSS_HR, CROSS_VB),
           CROSS_C2, base_size=2.8, size_var=1.0,
           line_spacing=1.08, opacity_range=(0.15, 0.35))
dwg.add(cross)

# Layer 5: Center glow — bright words at the cross intersection
glow = dwg.g(id='glow')
glow_r = 60
def inside_glow(x, y):
    return math.hypot(x - CX, y - CY) <= glow_r and inside_cross(x, y)
dense_fill(glow, ['Deus Caritas Est', 'God is Love', 'Agape', 'Caritas',
                   'Hesed', 'Amor', 'Love', 'Covenant', 'Communion',
                   'Perfect Love', 'Sacred gift', 'Life-giving'],
           inside_glow,
           (CX - glow_r, CY - glow_r, CX + glow_r, CY + glow_r),
           GOLD_B, base_size=3.5, size_var=2,
           line_spacing=1.05, opacity_range=(0.3, 0.6),
           hero_count=3, hero_size=(8, 12), hero_opacity=0.7)
dwg.add(glow)

# ============================================================
# SAVE
# ============================================================
dwg.save()
print(f'\n✓ Cross + Rays SVG saved to:\n  {OUTPUT}\n')
