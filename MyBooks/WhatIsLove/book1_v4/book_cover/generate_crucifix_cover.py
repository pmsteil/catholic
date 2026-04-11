#!/usr/bin/env python3
"""
What Is Love? — Crucifix Book Cover SVG
=========================================
A single, stunning crucifix made entirely of theological words about love.
From a distance: a luminous Christ on the Cross against dark wine.
Up close: every word is Catholic teaching on love.

Layers (back to front):
  1. Dark wine background
  2. Subtle Names of God filling the entire field
  3. Rays of grace emanating from Sacred Heart (Truth/Justice/Mercy/Sacrifice)
  4. The Cross (deep crimson sacrifice words)
  5. Christ's body (warm luminous gold incarnation words)
  6. Crown of thorns, INRI, Sacred Wound details
  7. "DEUS CARITAS EST" inscription above
"""

import svgwrite
import math
import random

random.seed(7)

W, H = 1200, 1800
OUTPUT = '/Users/patiman/Desktop/designer-output/what-is-love-crucifix-v1.svg'

dwg = svgwrite.Drawing(OUTPUT, size=(f'{W}px', f'{H}px'),
                        viewBox=f'0 0 {W} {H}', profile='full')
defs = dwg.defs

# ============================================================
# COLORS
# ============================================================
BG          = '#0a0204'      # near black wine
SKY         = '#140610'      # subtle sky text
CROSS_C     = '#6a0e0e'      # deep crimson cross
CROSS_C2    = '#8a1515'      # lighter crimson variation
BODY_C      = '#d4be78'      # warm gold (Christ body)
BODY_C2     = '#e8d498'      # bright gold highlights
BODY_DIM    = '#a89058'      # dimmer body
GOLD_B      = '#F0D060'      # bright gold (INRI, inscription)
C_TRUTH     = '#c8a830'      # gold ray
C_JUSTICE   = '#7848b0'      # violet ray
C_MERCY     = '#c08898'      # pale rose ray
C_SACRIFICE = '#981818'      # crimson ray
THORN_C     = '#583020'      # dark thorns
WOUND_PALE  = '#c8a8b0'      # pale ray (mercy) from wound
WOUND_RED   = '#a82020'      # red ray (sacrifice) from wound

# ============================================================
# WORD POOLS — massive, non-repeating
# ============================================================

SKY_WORDS = [
    "Father", "Abba", "YHWH", "I AM", "Creator", "Almighty", "Holy",
    "Eternal", "Infinite", "Alpha", "Omega", "El Shaddai", "Adonai",
    "Ancient of Days", "Ruach", "Spirit", "Light", "Life", "Logos",
    "Providence", "Trinity", "Perichoresis", "Triune", "One God",
    "Three Persons", "Bond of Love", "Comforter", "Paraclete",
    "Transcendent", "Immanent", "Source", "Before all time",
    "Without end", "In the beginning", "Let there be light",
    "Perfect goodness", "Perfect beauty", "Ground of being",
    "Lord of Lords", "King of Kings", "Living God", "Maker",
    "Breath of God", "Dove", "Wind", "Seal", "Anointing",
    "Divine communion", "Gift of self", "He who is",
    "love", "truth", "mercy", "justice", "grace", "peace",
    "faith", "hope", "charity", "covenant", "communion",
    "redemption", "salvation", "holiness", "glory", "wisdom",
    "prayer", "virtue", "sacred", "divine", "blessed", "heart",
    "agape", "caritas", "hesed", "misericordia", "fides",
    "spes", "veritas", "lux", "pax", "sanctus", "gloria",
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
    "Not my will but yours", "Gethsemane", "Scourged",
    "Stripped", "Crowned with thorns", "Mocked", "Condemned",
    "Carried his cross", "Simon of Cyrene", "Veronica",
    "Daughters of Jerusalem", "Fell three times", "Mary stood",
    "Stabat Mater", "Into your hands", "Why have you forsaken me",
    "Father forgive them", "Today you will be with me in paradise",
    "Woman behold your son", "I thirst", "Death",
    "Burial", "Stone rolled away", "He is not here",
    "He is risen", "Resurrection", "Victor over death",
    "Death swallowed up", "O death where is your sting",
    "Without shedding of blood", "Blood of the new covenant",
    "Eternal sacrifice", "Once for all", "High priest forever",
    "Melchizedek", "Altar", "Oblation", "Immolation",
    "Kenosis", "Self-emptying", "Fiat", "Total gift",
    "Redemptive suffering", "Offering", "Martyrdom",
    "Witness unto death", "Take up your cross", "Follow me",
    "Paschal mystery", "Passover", "Liberation", "Exodus",
    "Blood of the lamb", "Doorposts", "Angel of death passed over",
    "Eucharistic sacrifice", "Re-presentation", "Memorial",
    "This is my Body", "This is my Blood", "Do this in memory",
    "New and eternal covenant", "Source and summit",
    "Anamnesis", "He gave himself", "Love unto the end",
    "As the Father sent me", "Sent into the world",
    "For God so loved the world", "He gave his only Son",
    "Whoever believes shall not perish", "Eternal life",
]

BODY_WORDS = [
    "Incarnation", "Word became flesh", "Emmanuel", "God with us",
    "True God", "True Man", "Hypostatic union", "Two natures",
    "Sacred Heart", "Blood and water", "Wounded side",
    "He loved them to the end", "Kenosis", "Self-emptying",
    "By his wounds we are healed", "Corpus Christi",
    "Body given for you", "Come to me all who are weary",
    "I will give you rest", "Covenant embrace", "Welcome",
    "Everlasting love", "Arms open wide", "I have called you friends",
    "Cornerstone", "Foundation", "He humbled himself", "Servant",
    "He is risen", "Alleluia", "New life", "Victor",
    "Son of God", "Son of Man", "Messiah", "Christ", "Anointed",
    "King of Kings", "Lord of Lords", "Prince of Peace",
    "Wonderful Counselor", "Mighty God", "Eternal Father",
    "Alpha and Omega", "First and Last", "Beginning and End",
    "Bread of Life", "Living Water", "True Vine", "Good Shepherd",
    "Light of the World", "Way Truth Life", "Gate",
    "Resurrection and Life", "I AM", "Before Abraham I AM",
    "Who do you say that I am", "You are the Christ",
    "Transfiguration", "Baptism in the Jordan", "Beloved Son",
    "In whom I am well pleased", "Listen to him",
    "Love one another as I have loved you", "New commandment",
    "By this all will know you are my disciples",
    "As the Father has loved me so I have loved you",
    "Remain in my love", "If you keep my commandments",
    "I chose you", "I appointed you to go and bear fruit",
    "Love is patient", "Love is kind", "Love bears all things",
    "Love believes all things", "Love hopes all things",
    "Love endures all things", "Love never fails",
    "Greatest of these is love", "We love because he first loved us",
    "Perfect love casts out fear", "God is love",
    "Whoever abides in love abides in God",
    "Nothing can separate us from the love of God",
    "Neither death nor life nor angels nor principalities",
    "Nor things present nor things to come", "Nor height nor depth",
    "Nor any creature", "From the love of God in Christ Jesus",
    "Mercy", "Compassion", "Hesed", "Rahamim", "Misericordia",
    "Forgiveness", "Healing", "Reconciliation", "Grace",
    "Gratuitous gift", "Unearned", "Abundant", "Overflowing",
    "Truth", "Logos", "Revelation", "Scripture", "Tradition",
    "Magisterium", "Deposit of Faith", "Gospel",
    "Justice", "Righteousness", "Right order", "Covenant law",
    "Charity", "Caritas", "Agape", "Amor", "Benevolence",
    "Faith", "Hope", "Trust", "Surrender", "Belief",
    "Prudence", "Fortitude", "Temperance", "Humility",
    "Chastity", "Obedience", "Patience", "Meekness",
    "Beatitudes", "Blessed", "Poor in spirit", "Pure in heart",
    "Peacemakers", "Merciful", "Hunger for righteousness",
    "Baptism", "Confirmation", "Eucharist", "Penance",
    "Anointing", "Holy Orders", "Matrimony", "Sacrament",
    "Real Presence", "Transubstantiation", "Communion",
    "Consecration", "Epiclesis", "Body Blood Soul Divinity",
    "Feed the hungry", "Give drink", "Clothe the naked",
    "Shelter the homeless", "Visit the sick", "Visit imprisoned",
    "Instruct the ignorant", "Counsel the doubtful",
    "Comfort the afflicted", "Bear wrongs patiently",
    "Forgive injuries", "Pray for living and dead",
    "Wisdom", "Understanding", "Counsel", "Knowledge",
    "Piety", "Fear of the Lord", "Joy", "Peace", "Kindness",
    "Goodness", "Faithfulness", "Gentleness", "Self-control",
    "Covenant", "Promise", "Fulfillment", "Kingdom",
    "Church", "Body of Christ", "Bride of Christ", "People of God",
    "Communion of saints", "Mystical Body", "Pilgrim Church",
    "Salvation", "Justification", "Sanctification", "Glorification",
    "Theosis", "Divinization", "Beatific vision", "Heaven",
    "Eternal life", "New Jerusalem", "He will wipe every tear",
    "Deus Caritas Est", "God is Love",
    "God's Perfect Love", "Sacred gift of covenant",
    "Binding truth justice mercy sacrifice",
    "Life-giving communion", "Form of all the virtues",
    "Binds everything together in perfect harmony",
    "To love is to will the good of another",
    "The whole of doctrine directed to love that never ends",
]

THORN_WORDS = [
    "Thorns", "Crown", "Mockery", "Scourged", "Condemned",
    "Suffering", "Sorrow", "Anguish", "Agony", "Sweat like blood",
    "Man of sorrows", "Acquainted with grief", "Despised",
    "Rejected", "Stricken", "Smitten", "Afflicted",
    "Wounded for our transgressions", "Bruised for our iniquities",
    "Chastisement upon him", "By his stripes", "Led like a lamb",
    "Silent before shearers", "Cut off from the land of living",
    "Covenant bond", "Willing suffering", "Voluntary embrace",
]

RAY_WORDS = {
    'truth': [
        "Truth", "Logos", "Word", "Light", "Revelation", "Scripture",
        "Tradition", "Magisterium", "Doctrine", "Creed", "Gospel",
        "Emet", "Aletheia", "Illumination", "Transfiguration",
        "Way Truth Life", "Truth sets free", "Fides et Ratio",
        "Wisdom", "Understanding", "Knowledge", "Reason",
        "Uncreated Light", "Verbum", "Evangelization", "Kerygma",
    ],
    'justice': [
        "Justice", "Righteousness", "Mishpat", "Dikaiosyne",
        "Equity", "Fairness", "Accountability", "Restitution",
        "Right order", "Covenant law", "Divine law", "Moral law",
        "Natural law", "Commandments", "Conscience", "Decalogue",
        "Sovereignty", "Authority", "Providence", "Common good",
        "Solidarity", "Subsidiarity", "Human dignity", "Imago Dei",
    ],
    'mercy': [
        "Mercy", "Compassion", "Hesed", "Rahamim", "Misericordia",
        "Eleos", "Forgiveness", "Pardon", "Absolution", "Grace",
        "Gift", "Healing", "Reconciliation", "Tenderness",
        "Lovingkindness", "Patience", "Forbearance", "Gentleness",
        "Living water", "Divine Mercy", "Prodigal Father",
        "Come to me", "Lost sheep", "Seventy times seven",
    ],
    'sacrifice': [
        "Sacrifice", "Offering", "Oblation", "Kenosis",
        "Cross", "Calvary", "Passion", "Blood", "Lamb",
        "Atonement", "Propitiation", "Expiation", "Redemption",
        "Martyrdom", "Self-denial", "Fiat", "Total gift",
        "Not my will", "Obedient unto death", "Poured out",
        "Take up your cross", "Follow me", "It is finished",
    ],
}

# ============================================================
# GEOMETRY — The Crucifix
# ============================================================
CX = 600  # center of everything

# Cross dimensions (large, dominant) — proportioned like a traditional Latin cross
CROSS_VW = 100       # vertical bar width
CROSS_HH = 90        # horizontal bar height
CROSS_TOP = 230
CROSS_BOT = 1520
CROSS_BAR_Y = 520    # top of horizontal bar (higher than center, like a real crucifix)
CROSS_BAR_Y2 = CROSS_BAR_Y + CROSS_HH  # bottom of horizontal bar
CROSS_ARM_EXT = 330  # extension from vertical bar to each side
CROSS_LEFT = CX - CROSS_VW // 2 - CROSS_ARM_EXT
CROSS_RIGHT = CX + CROSS_VW // 2 + CROSS_ARM_EXT

# Christ body profile: (y, half_width) — interpolated for smooth silhouette
# Head is above crossbar, body hangs from it
BODY_PROFILE = [
    (320, 0),       # crown/top of head
    (340, 28),      # upper head
    (370, 38),      # mid head (widest)
    (400, 36),      # lower head
    (420, 30),      # jaw
    (440, 18),      # neck
    (460, 22),      # base of neck
    (480, 40),      # shoulders begin
    (510, 58),      # full shoulders
    (540, 55),      # upper chest
    (580, 50),      # chest
    (620, 48),      # mid-torso (at crossbar)
    (680, 44),      # below crossbar
    (740, 40),      # rib area (Sacred Heart zone)
    (800, 36),      # lower ribs
    (860, 32),      # waist
    (920, 34),      # hips
    (980, 30),      # upper thigh
    (1050, 25),     # mid thigh
    (1120, 22),     # above knee
    (1180, 20),     # knee
    (1240, 18),     # below knee
    (1300, 16),     # shin
    (1360, 14),     # ankle
    (1400, 18),     # feet (crossed, wider)
    (1430, 14),     # lower feet
    (1450, 0),      # bottom
]

# Arms: follow crossbar with natural droop
# Arm profile: (x_distance_from_center, y_offset_from_bar_center, half_thickness)
ARM_PROFILE = [
    (58, 0, 28),     # at shoulder
    (100, 4, 26),    # upper arm
    (150, 10, 24),
    (200, 18, 22),   # mid arm
    (250, 26, 20),
    (300, 34, 18),   # forearm
    (350, 40, 16),
    (400, 44, 14),   # near wrist
    (430, 46, 12),   # wrist
    (458, 48, 15),   # hand (wider)
    (470, 48, 10),   # fingertips
]

# Sacred Heart center
HEART_CX, HEART_CY = CX - 8, 730

# Wound position (right side of chest)
WOUND_CX, WOUND_CY = CX + 38, 720

# ============================================================
# SHAPE FUNCTIONS
# ============================================================

def body_half_width(y):
    """Get half-width of body at given y by interpolating profile."""
    if y < BODY_PROFILE[0][0] or y > BODY_PROFILE[-1][0]:
        return 0
    for i in range(len(BODY_PROFILE) - 1):
        y1, w1 = BODY_PROFILE[i]
        y2, w2 = BODY_PROFILE[i + 1]
        if y1 <= y <= y2:
            t = (y - y1) / (y2 - y1) if y2 != y1 else 0
            return w1 + (w2 - w1) * t
    return 0

def inside_body(x, y):
    """Test if point is inside Christ's torso/head/legs."""
    hw = body_half_width(y)
    return hw > 0 and abs(x - CX) <= hw

def inside_arms(x, y):
    """Test if point is inside Christ's arms (along crossbar)."""
    bar_cy = CROSS_BAR_Y + CROSS_HH / 2
    dist_from_center = abs(x - CX)
    # Must be beyond shoulders but within crossbar
    if dist_from_center < 50 or dist_from_center > 475:
        return False
    # Interpolate arm profile
    for i in range(len(ARM_PROFILE) - 1):
        d1, dy1, ht1 = ARM_PROFILE[i]
        d2, dy2, ht2 = ARM_PROFILE[i + 1]
        if d1 <= dist_from_center <= d2:
            t = (dist_from_center - d1) / (d2 - d1) if d2 != d1 else 0
            dy = dy1 + (dy2 - dy1) * t
            ht = ht1 + (ht2 - ht1) * t
            arm_cy = bar_cy + dy
            return abs(y - arm_cy) <= ht
    return False

def inside_christ(x, y):
    """Test if point is inside any part of Christ's body."""
    return inside_body(x, y) or inside_arms(x, y)

def inside_cross_only(x, y):
    """Inside the cross bars but NOT inside Christ's body."""
    in_vbar = (CX - CROSS_VW // 2 <= x <= CX + CROSS_VW // 2
               and CROSS_TOP <= y <= CROSS_BOT)
    in_hbar = (CROSS_LEFT <= x <= CROSS_RIGHT
               and CROSS_BAR_Y <= y <= CROSS_BAR_Y2)
    in_cross = in_vbar or in_hbar
    return in_cross and not inside_christ(x, y)

def inside_cross_all(x, y):
    """Inside the cross bars (including where body overlaps)."""
    in_vbar = (CX - CROSS_VW // 2 <= x <= CX + CROSS_VW // 2
               and CROSS_TOP <= y <= CROSS_BOT)
    in_hbar = (CROSS_LEFT <= x <= CROSS_RIGHT
               and CROSS_BAR_Y <= y <= CROSS_BAR_Y2)
    return in_vbar or in_hbar

def inside_crown(x, y):
    """Ring of thorns around the head."""
    r = math.hypot(x - CX, y - 365)
    return 40 <= r <= 58

def inside_ray(x, y, angle_deg, half_width_deg=12):
    """Test if point is inside a ray emanating from Sacred Heart."""
    dx = x - HEART_CX
    dy = y - HEART_CY
    dist = math.hypot(dx, dy)
    if dist < 80 or dist > 700:
        return False
    angle = math.degrees(math.atan2(dy, dx))
    diff = (angle - angle_deg + 180) % 360 - 180
    # Ray narrows slightly with distance then widens
    hw = half_width_deg * (0.7 + 0.5 * (dist / 700))
    return abs(diff) <= hw

# ============================================================
# FILL ENGINE
# ============================================================

def dense_fill(group, words, is_inside_fn, bbox,
               color, base_size=3.8, size_var=2.0,
               line_spacing=1.06, opacity_range=(0.5, 0.95),
               hero_count=0, hero_size=(9, 15), hero_opacity=0.85):
    """Ultra-dense fill. Words become the visual material."""
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

        # Scan for left edge
        lx = x0
        while lx < x1 and not is_inside_fn(lx, cy):
            lx += 0.8
        # Scan for right edge
        rx = x1
        while rx > lx and not is_inside_fn(rx, cy):
            rx -= 0.8

        avail = rx - lx - 1
        if avail > fs * 1.5:
            avg_cw = fs * 0.44
            tokens = []
            cx_used = 0
            while cx_used < avail:
                word = pool[wi % total]
                wi += 1
                ww = len(word) * avg_cw
                gap = avg_cw * 0.6 if tokens else 0
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

    # Hero words
    if hero_count > 0:
        random.shuffle(pool)
        placed = 0
        for _ in range(hero_count * 30):
            if placed >= hero_count:
                break
            hx = random.uniform(x0 + 5, x1 - 5)
            hy = random.uniform(y0 + 10, y1 - 5)
            if is_inside_fn(hx, hy):
                word = pool[placed % total]
                hs = random.uniform(*hero_size)
                rot = random.uniform(-6, 6)
                group.add(dwg.text(
                    word,
                    insert=(hx, hy),
                    font_size=f'{hs:.1f}px',
                    font_family='Georgia, serif',
                    fill=color, opacity=f'{hero_opacity}',
                    font_weight='bold',
                    transform=f'rotate({rot:.1f},{hx:.0f},{hy:.0f})',
                ))
                placed += 1


def dense_fill_gradient(group, words, is_inside_fn, bbox,
                        color, center, max_dist=700,
                        base_size=3.5, size_var=1.5,
                        line_spacing=1.08):
    """Fill with opacity fading based on distance from center point."""
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
            lx += 1
        rx = x1
        while rx > lx and not is_inside_fn(rx, cy):
            rx -= 1

        avail = rx - lx - 1
        if avail > fs * 2:
            mid_x = (lx + rx) / 2
            dist = math.hypot(mid_x - ccx, cy - ccy)
            fade = max(0.08, 1.0 - (dist / max_dist) ** 1.2)
            op = fade * random.uniform(0.5, 0.9)

            avg_cw = fs * 0.44
            tokens = []
            cx_used = 0
            while cx_used < avail:
                word = pool[wi % total]
                wi += 1
                ww = len(word) * avg_cw
                gap = avg_cw * 0.6 if tokens else 0
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
# BUILD THE IMAGE
# ============================================================

# Layer 0: Background
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

# Layer 1: Subtle sky/Names of God filling entire canvas
sky = dwg.g(id='sky')
def always(x, y): return True
dense_fill(sky, SKY_WORDS, always, (0, 0, W, H),
           SKY, base_size=5, size_var=2.5,
           line_spacing=1.04, opacity_range=(0.35, 0.65))
dwg.add(sky)

# Layer 2: "DEUS CARITAS EST" inscription
ins = dwg.g(id='inscription')
ins.add(dwg.text('DEUS CARITAS EST',
    insert=(CX, 120), text_anchor='middle',
    dominant_baseline='middle', font_size='18px',
    font_family='Georgia, serif', fill=GOLD_B,
    font_weight='bold', letter_spacing='5', opacity='0.7'))
ins.add(dwg.text('God is Love',
    insert=(CX, 145), text_anchor='middle',
    font_size='10px', font_family='Georgia, serif',
    fill=BODY_C, letter_spacing='2', opacity='0.5'))
# Subtle glow behind inscription
for i in range(6, 0, -1):
    ins.add(dwg.circle(center=(CX, 130), r=i * 25 + 30,
            fill='none', stroke=GOLD_B,
            stroke_width=0.2, opacity=0.02 + i * 0.005))
dwg.add(ins)

# Layer 3: Rays of grace from Sacred Heart
rays = dwg.g(id='rays')
ray_config = [
    # (angle_degrees, color, word_key)
    (0,    C_TRUTH,     'truth'),      # right
    (45,   C_TRUTH,     'truth'),      # upper-right
    (90,   C_SACRIFICE, 'sacrifice'),  # down (toward altar)
    (135,  C_MERCY,     'mercy'),      # lower-left
    (180,  C_MERCY,     'mercy'),      # left
    (225,  C_JUSTICE,   'justice'),     # upper-left
    (270,  C_TRUTH,     'truth'),      # up (toward heaven)
    (315,  C_JUSTICE,   'justice'),     # upper-right
    # Additional subtle rays
    (22,   C_SACRIFICE, 'sacrifice'),
    (68,   C_MERCY,     'mercy'),
    (112,  C_JUSTICE,   'justice'),
    (158,  C_TRUTH,     'truth'),
    (202,  C_SACRIFICE, 'sacrifice'),
    (248,  C_MERCY,     'mercy'),
    (292,  C_JUSTICE,   'justice'),
    (338,  C_SACRIFICE, 'sacrifice'),
]

for angle, color, key in ray_config:
    def make_ray_test(a=angle):
        def fn(x, y):
            if inside_cross_all(x, y):
                return False  # rays behind cross
            return inside_ray(x, y, a, half_width_deg=10)
        return fn

    dense_fill_gradient(rays, RAY_WORDS[key], make_ray_test(),
                        (0, 0, W, H), color,
                        center=(HEART_CX, HEART_CY),
                        max_dist=650, base_size=3.5, size_var=1.5)
dwg.add(rays)

# Layer 4: The Cross (deep crimson sacrifice text)
cross = dwg.g(id='cross')
dense_fill(cross, CROSS_WORDS, inside_cross_only,
           (CROSS_LEFT - 5, CROSS_TOP - 5, CROSS_RIGHT + 5, CROSS_BOT + 5),
           CROSS_C, base_size=3.5, size_var=2,
           line_spacing=1.05, opacity_range=(0.55, 0.95),
           hero_count=25, hero_size=(7, 12), hero_opacity=0.8)

# Second pass for variation
dense_fill(cross, CROSS_WORDS[::-1], inside_cross_only,
           (CROSS_LEFT, CROSS_TOP, CROSS_RIGHT, CROSS_BOT),
           CROSS_C2, base_size=2.8, size_var=1.2,
           line_spacing=1.08, opacity_range=(0.2, 0.45))
dwg.add(cross)

# Layer 5: Christ's Body (warm luminous gold)
body = dwg.g(id='body')
dense_fill(body, BODY_WORDS, inside_christ,
           (CROSS_LEFT - 5, 315, CROSS_RIGHT + 5, 1460),
           BODY_C, base_size=3.2, size_var=2.0,
           line_spacing=1.04, opacity_range=(0.55, 0.95),
           hero_count=40, hero_size=(6, 11), hero_opacity=0.85)

# Brighter layer for luminosity
dense_fill(body, BODY_WORDS[::-1], inside_christ,
           (CX - 60, 400, CX + 60, 1400),
           BODY_C2, base_size=2.5, size_var=1.0,
           line_spacing=1.1, opacity_range=(0.15, 0.35))
dwg.add(body)

# Layer 6: Crown of thorns
thorns = dwg.g(id='thorns')
dense_fill(thorns, THORN_WORDS, inside_crown,
           (CX - 60, 305, CX + 60, 425),
           THORN_C, base_size=3, size_var=1.5,
           line_spacing=1.05, opacity_range=(0.6, 0.95),
           hero_count=5, hero_size=(5, 8))
dwg.add(thorns)

# Layer 7: INRI tablet
inri = dwg.g(id='inri')
inri.add(dwg.text('I N R I',
    insert=(CX, CROSS_TOP + 30), text_anchor='middle',
    dominant_baseline='middle', font_size='14px',
    font_family='Georgia, serif', fill=GOLD_B,
    font_weight='bold', letter_spacing='4', opacity='0.8'))
dwg.add(inri)

# Layer 8: Sacred Wound — burst of mercy/sacrifice at Christ's side
wound = dwg.g(id='wound')
# Small bright burst
for i in range(15):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(5, 35)
    wx = WOUND_CX + r * math.cos(a)
    wy = WOUND_CY + r * math.sin(a)
    if inside_christ(wx, wy) or r < 20:
        col = WOUND_PALE if random.random() > 0.5 else WOUND_RED
        word = random.choice(["blood", "water", "mercy", "sacrifice",
                              "pierced", "wounded side", "font of mercy",
                              "Living water", "pale ray", "red ray",
                              "Divine Mercy", "healing"])
        fs = random.uniform(3, 6)
        wound.add(dwg.text(word,
            insert=(wx, wy), font_size=f'{fs:.1f}px',
            font_family='Georgia, serif', fill=col,
            opacity=f'{random.uniform(0.5, 0.9):.2f}',
            transform=f'rotate({random.uniform(-20, 20):.0f},{wx:.0f},{wy:.0f})',
        ))
dwg.add(wound)

# ============================================================
# SAVE
# ============================================================
dwg.save()
print(f'\n✓ Crucifix SVG saved to:\n  {OUTPUT}\n')
