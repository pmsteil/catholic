#!/usr/bin/env python3
"""
What Is Love? — Gothic Cathedral Book Cover SVG Generator v3
==============================================================
ART FIRST, TEXT SECOND.

The text is so dense it reads as colored shapes from a distance.
Only on closer inspection does the viewer realize it's made of words.

Key principles:
- Ultra-dense packing (3-5px base, 1.05 line spacing)
- Randomized word order, no obvious repetition
- Variable font sizes within each zone
- NO architectural outlines — text IS the architecture
- Color contrast between zones creates the cathedral shape
- Hero words scattered at larger sizes for close-up discovery
"""

import svgwrite
import math
import random

random.seed(42)  # reproducible but random-looking

W, H = 1200, 1800
OUTPUT = '/Users/patiman/Desktop/designer-output/what-is-love-cathedral-v3.svg'

dwg = svgwrite.Drawing(OUTPUT, size=(f'{W}px', f'{H}px'),
                        viewBox=f'0 0 {W} {H}', profile='full')
defs = dwg.defs

# ============================================================
# COLORS
# ============================================================
BG           = '#0e0305'
SKY_TEXT     = '#1e0810'
GOLD_BRIGHT  = '#F0D060'
GOLD         = '#C9A84C'
C_TRUTH      = '#b89828'
C_JUSTICE    = '#7040a8'
C_MERCY      = '#b88090'
C_SACRIFICE  = '#901818'
C_IVORY      = '#c8c0a8'
C_PALE_GOLD  = '#a89050'
C_CHRIST     = '#d8c880'
C_CROSS      = '#701010'
C_ALTAR      = '#b89030'

# Stained glass — vivid jewel tones
SC = {
    'baptism':      '#4878a8',
    'confirmation': '#b86060',
    'eucharist':    '#c89828',
    'penance':      '#8058b0',
    'anointing':    '#509050',
    'orders':       '#b88830',
    'matrimony':    '#c06090',
}

# ============================================================
# MASSIVE WORD POOLS — pulled from the full word palette
# Each zone gets a large, unique pool. Words are SHORT for dense packing.
# ============================================================

# General pool (shared, used to supplement zone-specific words)
GENERAL = [
    "love", "truth", "mercy", "justice", "sacrifice", "covenant",
    "grace", "faith", "hope", "charity", "communion", "gift",
    "light", "life", "peace", "joy", "redemption", "salvation",
    "holiness", "glory", "wisdom", "prayer", "virtue", "sacred",
    "eternal", "divine", "blessed", "holy", "spirit", "heart",
    "cross", "risen", "lamb", "shepherd", "bread", "vine",
    "water", "fire", "word", "flesh", "blood", "body",
    "soul", "healing", "freedom", "promise", "kingdom", "heaven",
    "altar", "chalice", "host", "monstrance", "tabernacle",
    "rosary", "creed", "gospel", "psalm", "alleluia", "amen",
    "agape", "caritas", "hesed", "misericordia", "fides",
    "spes", "veritas", "lux", "pax", "sanctus", "gloria",
]

EXTERIOR_POOL = [
    "Father", "Abba", "YHWH", "I AM", "Creator", "Almighty",
    "Holy", "Eternal", "Infinite", "Alpha", "Omega",
    "El Shaddai", "Adonai", "Ancient of Days", "Ruach",
    "Spirit", "Light", "Life", "Logos", "Providence",
    "Trinity", "Perichoresis", "Triune", "One God",
    "Three Persons", "Bond of Love", "Comforter",
    "Paraclete", "Advocate", "Ground of being",
    "Transcendent", "Immanent", "Omnipotent", "Source",
    "Before all time", "Without end", "Maker",
    "In the beginning", "Let there be light", "It was good",
    "Perfect goodness", "Perfect beauty", "He who is",
    "Lord of Lords", "King of Kings", "Living God",
    "Divine communion", "Shared love", "Gift of self",
    "Breath of God", "Dove", "Wind", "Anointing", "Seal",
]

COMMANDMENT_POOL = [
    "I AM the Lord", "no other gods", "holy Name",
    "keep the Sabbath", "honor father mother", "shall not kill",
    "shall not steal", "no false witness", "shall not covet",
    "Decalogue", "natural law", "moral law", "conscience",
    "Sinai", "Moses", "tablets", "written on the heart",
    "divine law", "eternal law", "foundation", "precepts",
    "love God", "love neighbor", "all the law depends",
    "law as gift", "synderesis", "right reason",
    "dignity", "sanctity of life", "Imago Dei",
    "truth-telling", "fidelity", "chastity", "honesty",
    "rest", "worship", "adoration", "reverence",
    "obedience", "respect", "just wage", "restitution",
    "purity of heart", "detachment", "generosity",
]

TRUTH_POOL = [
    "Truth", "Logos", "Word", "Light", "Revelation",
    "Scripture", "Tradition", "Magisterium", "Doctrine",
    "Creed", "Catechism", "Emet", "Aletheia", "Gospel",
    "Canon", "Orthodoxy", "Witness", "Teaching",
    "Evangelization", "Catechesis", "Illumination",
    "Transfiguration", "Uncreated Light", "Epiphany",
    "Way Truth Life", "truth sets free", "your Word is truth",
    "Word became flesh", "deposit of faith", "inerrancy",
    "faith seeking understanding", "Fides et Ratio",
    "reason", "intellect", "clarity", "certainty",
    "proclamation", "kerygma", "testimony", "inspired",
    "Verbum Domini", "In principio", "Lux aeterna",
]

JUSTICE_POOL = [
    "Justice", "Righteousness", "Right order", "Mishpat",
    "Dikaiosyne", "Equity", "Fairness", "Accountability",
    "Restitution", "Rectitude", "Suum cuique", "Due",
    "Sovereignty", "Authority", "Providence", "Governance",
    "Social justice", "Commutative", "Distributive",
    "Proportionality", "Reparation", "Conscience",
    "Let justice roll like a river", "Do justice love mercy",
    "Judgment", "Law", "Covenant law", "Divine law",
    "Moral law", "Natural law", "New law", "Precepts",
    "Synderesis", "Structure", "Order", "Kingship",
    "Dominion", "Tribunal", "Satisfaction",
    "Common good", "Solidarity", "Subsidiarity",
]

MERCY_POOL = [
    "Mercy", "Compassion", "Lovingkindness", "Tenderness",
    "Hesed", "Rahamim", "Misericordia", "Eleos",
    "Forgiveness", "Pardon", "Absolution", "Reconciliation",
    "Healing", "Grace", "Gift", "Gratuitous", "Abundance",
    "Patience", "Forbearance", "Gentleness", "Clemency",
    "Divine Mercy", "Living water", "Pale ray",
    "mercy endures forever", "Prodigal Father", "Lost sheep",
    "Come to me all who are weary", "seventy times seven",
    "Be merciful as your Father", "I desire mercy",
    "Blessed are the merciful", "font of mercy",
    "blood and water", "wounded side", "accompanying",
    "solidarity", "presence", "tenderness",
]

SACRIFICE_POOL = [
    "Sacrifice", "Offering", "Oblation", "Kenosis",
    "Covenant blood", "Cross", "Passion", "Calvary",
    "Good Friday", "Via Dolorosa", "Redemption", "Ransom",
    "Propitiation", "Expiation", "Atonement", "Lamb",
    "Agnus Dei", "Tetelestai", "Consummatum est",
    "It is finished", "Martyrdom", "Red ray",
    "Take up your cross", "Fiat", "Total gift",
    "Not my will but yours", "He humbled himself",
    "Obedient unto death", "poured out for many",
    "by his wounds", "pierced for our sins",
    "without shedding of blood", "self-denial",
    "death to self", "offering", "immolation",
]

FAITH_POOL = [
    "Faith", "Fides", "Belief", "Trust", "Assent",
    "Surrender", "Credo", "I believe", "Profession",
    "substance of things hoped for", "evidence unseen",
    "faith without works is dead", "living faith",
    "Abraham", "father of faith", "fidelity",
    "commitment", "perseverance", "cloud of witnesses",
    "gift of faith", "baptismal faith", "docility",
    "obedience of faith", "Lord I believe",
    "help my unbelief", "martyrs faith",
]

HOPE_POOL = [
    "Hope", "Spes", "Longing", "Maranatha", "Come Lord Jesus",
    "Beatific vision", "Heaven", "Eternal life", "Resurrection",
    "wipe away every tear", "Anchor of hope",
    "saved in hope", "Promise", "Covenant promise",
    "Fulfillment", "Trust", "Consolation",
    "Communion of saints", "Eye has not seen",
    "Parousia", "Advent longing", "Expectation",
    "New Jerusalem", "dwelling of God among men",
]

CHARITY_POOL = [
    "Charity", "Caritas", "Agape", "Love", "Amor",
    "form of all the virtues", "binds all in perfect harmony",
    "greatest of these is love", "love never fails",
    "love is patient", "love is kind", "love bears all",
    "love believes all", "love hopes all", "love endures all",
    "we love because he first loved us",
    "beloved let us love one another",
    "gift of self", "benevolence", "friendship with God",
    "communion", "life-giving", "fruitfulness",
]

BEATITUDE_POOL = [
    "poor in spirit", "kingdom of heaven",
    "those who mourn", "shall be comforted",
    "the meek", "inherit the earth",
    "hunger for righteousness", "shall be satisfied",
    "the merciful", "shall receive mercy",
    "pure in heart", "shall see God",
    "peacemakers", "called sons of God",
    "persecuted for righteousness", "rejoice be glad",
    "blessed", "blessedness", "vocation of the faithful",
    "countenance of Christ", "paradoxical promises",
    "sustain hope in tribulations",
]

SPIRIT_POOL = [
    "Wisdom", "Understanding", "Counsel", "Fortitude",
    "Knowledge", "Piety", "Fear of the Lord",
    "Love", "Joy", "Peace", "Patience", "Kindness",
    "Goodness", "Faithfulness", "Gentleness", "Self-control",
    "Generosity", "Modesty", "Chastity",
    "sevenfold gift", "Donum Dei", "unction",
    "anointing", "Pentecost", "epiclesis",
    "by their fruits", "Spirit of the Lord",
    "charism", "gift of God",
]

SCRIPTURE_POOL = [
    "God is love", "greater love has no one",
    "love one another", "new commandment",
    "love your enemies", "love the Lord your God",
    "greatest of these is love", "love never fails",
    "nothing can separate us", "perfect love casts out fear",
    "he loved them to the end", "God so loved the world",
    "we love because he first loved us",
    "by your love they will know", "love covers a multitude",
    "love is fulfillment of the law",
    "love poured into our hearts", "I have called you friends",
    "as the Father has loved me",
]

EUCHARIST_POOL = [
    "This is my Body", "This is my Blood",
    "Do this in memory", "Anamnesis", "Real Presence",
    "Transubstantiation", "Agnus Dei", "Bread of Life",
    "Source and summit", "Mysterium Fidei",
    "Sanctus", "Sursum Corda", "Dona nobis pacem",
    "Kyrie Eleison", "Corpus Christi", "Gloria",
    "Ite Missa Est", "Consecration", "Epiclesis",
    "Elevation", "Communion", "Living Bread",
    "Viaticum", "chalice", "paten", "host", "altar",
    "ciborium", "monstrance", "tabernacle",
    "Lamb of God who takes away", "Lord I am not worthy",
    "say the word and my soul shall be healed",
    "We proclaim your death O Lord",
    "through him with him in him",
]

APSE_POOL = [
    "God's Perfect Love", "sacred gift of covenant",
    "binding truth justice mercy sacrifice",
    "life-giving communion", "Deus Caritas Est",
    "form of all the virtues", "perfect harmony",
    "will the good of another", "love that never ends",
    "eternal exchange of love", "destined to share",
    "fundamental vocation", "Agape", "Caritas",
    "Hesed", "Amor", "Charity the form of all virtues",
    "whole concern of doctrine", "directed to love",
    "God himself is an eternal exchange of love",
]

SAC_POOLS = {
    'baptism': [
        "Baptism", "Rebirth", "Water", "Spirit", "Font",
        "Immersion", "Washing", "Cleansing", "Adoption",
        "Sonship", "Regeneration", "Chrism", "Beloved",
        "Born of water and spirit", "Death to sin",
        "Rising to new life", "White garment", "Candle",
        "Incorporation", "New creation", "Sealed",
    ],
    'confirmation': [
        "Confirmation", "Seal", "Strength", "Mission",
        "Witness", "Gifts of Spirit", "Chrism", "Bishop",
        "Pentecost", "Fire", "Wind", "Tongues",
        "Anointing", "Mature faith", "Apostolic",
        "Soldier of Christ", "Empowered", "Sent",
    ],
    'eucharist': [
        "Eucharist", "Real Presence", "Transubstantiation",
        "Body Blood Soul Divinity", "This is my Body",
        "Bread of Life", "Communion", "Source and summit",
        "Consecration", "Last Supper", "Altar", "Chalice",
        "Host", "Agnus Dei", "Monstrance", "Adoration",
        "Viaticum", "Living Bread", "Corpus Christi",
    ],
    'penance': [
        "Penance", "Reconciliation", "Confession",
        "Contrition", "Absolution", "I absolve you",
        "Prodigal son", "Tribunal of mercy", "Healing",
        "Amendment", "Forgiven", "Restored", "Seal",
        "Your sins are forgiven", "Confiteor", "Mercy",
    ],
    'anointing': [
        "Anointing", "Oil", "Prayer", "Comfort", "Healing",
        "Redemptive suffering", "Peace", "Fortitude",
        "Union with Christ", "Preparation", "Viaticum",
        "Sick", "Elders", "Laying on of hands", "Strength",
    ],
    'orders': [
        "Holy Orders", "Priesthood", "Ordination",
        "Alter Christus", "Bishop", "Priest", "Deacon",
        "Shepherd", "Ministry", "Apostolic succession",
        "Sacred character", "Celibacy", "Consecrated",
        "Fishers of men", "Ambassador", "Melchizedek",
    ],
    'matrimony': [
        "Matrimony", "Covenant", "Nuptial bond", "Fidelity",
        "Fruitfulness", "Indissolubility", "Domestic church",
        "One flesh", "Gift of self", "Family", "Children",
        "Free total faithful fruitful", "Spousal love",
        "Theology of the Body", "Nuptial meaning", "Consent",
    ],
}

CROSS_POOL = [
    "Sacrifice", "Atonement", "Calvary", "Passion",
    "Tetelestai", "It is finished", "Ransom", "Redemption",
    "Agnus Dei", "By his wounds", "Pierced", "Blood",
    "Poured out", "Obedient unto death", "Good Friday",
    "Propitiation", "Expiation", "Via Dolorosa",
    "Lamb of God", "Crucified", "Nailed", "Thorns",
    "Golgotha", "INRI", "Consummatum est", "Covenant blood",
    "Greater love", "Lay down his life", "Self-offering",
    "Cup of suffering", "not my will", "Gethsemane",
]

CHRIST_POOL = [
    "INRI", "Ecce Homo", "Crown of thorns", "King",
    "Son of God", "Son of Man", "Emmanuel", "Messiah",
    "Word became flesh", "Incarnation", "True God True Man",
    "Sacred Heart", "Blood and water", "Kenosis",
    "By his wounds we are healed", "Corpus Christi",
    "Wounded side", "He loved them to the end",
    "Body given for you", "Come to me",
    "I will give you rest", "Covenant embrace",
    "Everlasting love", "Arms open wide", "Welcome",
    "I have called you friends", "Cornerstone",
    "Foundation", "He humbled himself", "Servant",
    "He is risen", "Alleluia", "New life", "Victor",
]

SPIRE_L_POOL = [
    "Genesis", "Exodus", "Leviticus", "Numbers",
    "Deuteronomy", "Joshua", "Judges", "Ruth",
    "Samuel", "Kings", "Chronicles", "Ezra",
    "Nehemiah", "Tobit", "Judith", "Esther",
    "Maccabees", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Songs", "Wisdom", "Sirach",
    "Isaiah", "Jeremiah", "Lamentations", "Baruch",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "Thessalonians",
    "Timothy", "Titus", "Philemon", "Hebrews",
    "James", "Peter", "Jude", "Revelation",
    "Verbum Domini", "Sacred Scripture", "Word of God",
]

SPIRE_R_POOL = [
    "Jesus", "Christ", "Messiah", "Emmanuel", "Logos",
    "Lamb of God", "Good Shepherd", "Light of the World",
    "Bread of Life", "Living Water", "True Vine",
    "Way Truth Life", "Alpha Omega", "First and Last",
    "Lord", "Savior", "Redeemer", "King", "Priest",
    "Prophet", "Sacred Heart", "Prince of Peace",
    "Wonderful Counselor", "Mighty God", "Eternal Father",
    "I AM", "Holy One", "Risen Lord", "Pantocrator",
    "Christ the King", "Bridegroom", "Teacher", "Rabbi",
    "Master", "Healer", "Liberator", "Advocate",
    "Cornerstone", "Rock", "Door", "Gate",
    "Resurrection and Life", "Beginning and End",
]

VIRTUE_POOL = [
    "Prudence", "Justice", "Fortitude", "Temperance",
    "Discernment", "Courage", "Self-mastery", "Moderation",
    "Chastity", "Humility", "Meekness", "Patience",
    "Magnanimity", "Perseverance", "Sobriety", "Purity",
    "Obedience", "Simplicity", "Poverty of spirit",
    "Fasting", "Abstinence", "Mortification", "Valor",
    "Integrity", "Constancy", "Docility", "Caution",
]

FLOOR_POOL = [
    "Feed the hungry", "Give drink", "Clothe the naked",
    "Shelter the homeless", "Visit the sick",
    "Visit imprisoned", "Bury the dead",
    "For I was hungry", "Whatever you did",
    "For the least of these", "Almsgiving",
    "Solidarity", "Care for the poor",
    "Love made visible", "Charity in action",
    "Tend the wounded", "Bind up the broken",
    "Welcome the stranger", "Share your bread",
]

ROSE_POOL = [
    "Deus Caritas Est", "God is Love", "Agape", "Caritas",
    "Hesed", "Amor", "Amore", "Amour", "Liebe", "Lyubov",
    "Trinity", "Perichoresis", "Perfect Love", "Covenant",
    "Communion", "Three Persons One God", "Eternal exchange",
    "God's Perfect Love", "Sacred gift", "Life-giving",
    "Deus", "Caritas", "Est", "Love",
]

SPIRITUAL_MERCY_POOL = [
    "Instruct the ignorant", "Counsel the doubtful",
    "Admonish sinners", "Bear wrongs patiently",
    "Forgive injuries", "Comfort the afflicted",
    "Pray for living and dead", "Service of soul",
    "Patience with weakness", "Intercession",
    "Accompany", "Guide toward truth", "Listen",
    "Witness", "Encourage", "Console", "Uplift",
]

# ============================================================
# GEOMETRY — same as v2 with adjustments
# ============================================================
CAT_L, CAT_R = 180, 1020
CAT_TOP, CAT_BOT = 350, 1650
CAT_CX = 600

SPL_L, SPL_R = 180, 310
SPR_L, SPR_R = 890, 1020
SPIRE_TOP = 60
SPIRE_BASE = CAT_TOP

RW_CX, RW_CY, RW_R = CAT_CX, 290, 115

CW_TOP, CW_BOT = 365, 545
TRI_TOP, TRI_BOT = 553, 615

PIL_W = 42
PIL_TOP, PIL_BOT = 620, 1380
PIL_X = [CAT_L + 50, CAT_L + 260, CAT_R - 260 - PIL_W, CAT_R - 50 - PIL_W]

APS_CX, APS_CY = CAT_CX, 900
APS_RX, APS_RY = 230, 270

ALT_L, ALT_R = 450, 750
ALT_TOP, ALT_BOT = 910, 970

CRX_CX = CAT_CX
CRX_TOP = 640
CRX_BOT = 900
CRX_VW = 50
CRX_BY = 755
CRX_BH = 50
CRX_BL = 400
CRX_BR = 800

C_HEAD_R = 32
C_HEAD_CX, C_HEAD_CY = CRX_CX, CRX_TOP + 52

TRN_TOP, TRN_BOT = 900, 1110
TRN_L_L, TRN_L_R = CAT_L - 110, CAT_L + 10
TRN_R_L, TRN_R_R = CAT_R - 10, CAT_R + 110

FLR_TOP, FLR_BOT = 1380, 1465
FND_TOP, FND_BOT = 1465, 1660

# ============================================================
# SHAPE TESTS
# ============================================================
def inside_rect(x, y, rx, ry, rw, rh):
    return rx <= x <= rx + rw and ry <= y <= ry + rh

def inside_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0

def inside_triangle(x, y, xl, xr, yt, yb):
    if y < yt or y > yb: return False
    cx = (xl + xr) / 2
    hw = ((xr - xl) / 2) * ((y - yt) / max(yb - yt, 1))
    return abs(x - cx) <= hw

def inside_pointed_arch(x, y, xl, xr, yb, yp):
    if y > yb or y < yp: return False
    cx = (xl + xr) / 2
    hw = ((xr - xl) / 2) * (((y - yp) / max(yb - yp, 1)) ** 0.55)
    return abs(x - cx) <= hw

def inside_circle(x, y, cx, cy, r):
    return (x - cx)**2 + (y - cy)**2 <= r**2

# ============================================================
# DENSE FILL — The core engine
# ============================================================
def dense_fill(group, words, is_inside_fn, bbox,
               color, base_size=4.0, size_var=1.5,
               line_spacing=1.08, opacity_range=(0.55, 0.95),
               hero_count=0, hero_size_range=(9, 14)):
    """
    Ultra-dense text fill. From a distance reads as a colored shape.
    - base_size: smallest text size
    - size_var: random variation range added to base
    - hero_count: number of larger 'hero' words scattered in
    """
    x0, y0, x1, y1 = bbox
    pool = list(words)
    random.shuffle(pool)
    wi = 0
    total = len(pool)

    cy = y0 + base_size + 0.5
    while cy < y1 - 1:
        fs = base_size + random.uniform(0, size_var)
        lh = fs * line_spacing
        op = random.uniform(*opacity_range)

        # Find left edge
        lx = x0
        while lx < x1 and not is_inside_fn(lx, cy):
            lx += 1
        # Find right edge
        rx = x1
        while rx > lx and not is_inside_fn(rx, cy):
            rx -= 1

        avail = rx - lx - 2
        if avail > fs * 2:
            avg_cw = fs * 0.45
            tokens = []
            cx = 0
            while True:
                word = pool[wi % total]
                wi += 1
                ww = len(word) * avg_cw
                needed = ww + (avg_cw * 0.8 if tokens else 0)
                if cx + needed > avail:
                    break
                tokens.append(word)
                cx += needed
            if tokens:
                line = ' '.join(tokens)
                group.add(dwg.text(
                    line,
                    insert=(lx + 1, cy),
                    font_size=f'{fs:.1f}px',
                    font_family='Georgia, serif',
                    fill=color,
                    opacity=f'{op:.2f}',
                ))
        cy += lh

    # Hero words — larger, bolder, scattered
    if hero_count > 0:
        random.shuffle(pool)
        placed = 0
        attempts = 0
        while placed < hero_count and attempts < hero_count * 20:
            hx = random.uniform(x0 + 10, x1 - 10)
            hy = random.uniform(y0 + 10, y1 - 10)
            if is_inside_fn(hx, hy):
                word = pool[placed % total]
                hs = random.uniform(*hero_size_range)
                rot = random.uniform(-8, 8)
                group.add(dwg.text(
                    word,
                    insert=(hx, hy),
                    font_size=f'{hs:.1f}px',
                    font_family='Georgia, serif',
                    fill=color,
                    opacity='0.85',
                    font_weight='bold',
                    transform=f'rotate({rot:.1f},{hx:.0f},{hy:.0f})',
                ))
                placed += 1
            attempts += 1


def dense_fill_vertical(group, words, x, y, w, h,
                        color, base_size=4.5, size_var=1.5,
                        spacing=0.95, opacity_range=(0.55, 0.95)):
    """Dense vertical text fill for pillars."""
    pool = list(words)
    random.shuffle(pool)
    wi = 0
    total = len(pool)
    col_spacing = base_size * spacing + base_size * 0.3
    cx = x + base_size * 0.6

    while cx < x + w - 1:
        fs = base_size + random.uniform(0, size_var)
        avg_cw = fs * 0.45
        op = random.uniform(*opacity_range)
        cy = y + 2

        while cy < y + h - fs:
            word = pool[wi % total]
            wi += 1
            ww = len(word) * avg_cw
            if cy + ww > y + h:
                break
            group.add(dwg.text(
                word,
                insert=(cx, cy),
                font_size=f'{fs:.1f}px',
                font_family='Georgia, serif',
                fill=color,
                opacity=f'{op:.2f}',
                transform=f'rotate(90,{cx:.0f},{cy:.0f})',
            ))
            cy += ww + fs * 0.3
        cx += col_spacing


path_counter = 0
def curved_text(group, path_d, words, font_size=5, color=GOLD,
                repeat=2, opacity=0.7):
    global path_counter
    path_counter += 1
    pid = f'cp{path_counter}'
    p = dwg.path(d=path_d, id=pid, fill='none', stroke='none')
    defs.add(p)
    random.shuffle(words)
    text_str = ' '.join(words) * repeat
    txt = dwg.text('', font_size=f'{font_size}px',
                   font_family='Georgia, serif', fill=color,
                   opacity=f'{opacity}')
    tp = svgwrite.text.TextPath(p, text=text_str)
    txt.add(tp)
    group.add(txt)


# ============================================================
# DRAW
# ============================================================

# Background
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

# ---- EXTERIOR / SKY ----
sky = dwg.g(id='sky')
def outside_cat(x, y):
    if CAT_L <= x <= CAT_R and CAT_TOP <= y <= CAT_BOT: return False
    if SPL_L <= x <= SPL_R and SPIRE_TOP <= y <= SPIRE_BASE: return False
    if SPR_L <= x <= SPR_R and SPIRE_TOP <= y <= SPIRE_BASE: return False
    if TRN_L_L <= x <= TRN_L_R and TRN_TOP <= y <= TRN_BOT: return False
    if TRN_R_L <= x <= TRN_R_R and TRN_TOP <= y <= TRN_BOT: return False
    return True
dense_fill(sky, EXTERIOR_POOL + GENERAL, outside_cat,
           (0, 0, W, H), SKY_TEXT, base_size=5, size_var=2,
           line_spacing=1.05, opacity_range=(0.4, 0.7))
dwg.add(sky)

# ---- SUN ----
sun = dwg.g(id='sun')
sun_cx, sun_cy = CAT_CX, 42
for i in range(10, 0, -1):
    sun.add(dwg.circle(center=(sun_cx, sun_cy), r=i * 14 + 15,
            fill='none', stroke=GOLD_BRIGHT,
            stroke_width=0.25, opacity=0.03 + i * 0.008))
sun.add(dwg.text('DEUS CARITAS EST',
    insert=(sun_cx, sun_cy - 2), text_anchor='middle',
    dominant_baseline='middle', font_size='15px',
    font_family='Georgia, serif', fill=GOLD_BRIGHT,
    font_weight='bold', letter_spacing='4'))
sun.add(dwg.text('God is Love',
    insert=(sun_cx, sun_cy + 17), text_anchor='middle',
    font_size='9px', font_family='Georgia, serif',
    fill=C_PALE_GOLD, letter_spacing='1'))
dwg.add(sun)

# ---- SPIRES ----
sp = dwg.g(id='spires')
def isl(x, y): return inside_triangle(x, y, SPL_L, SPL_R, SPIRE_TOP, SPIRE_BASE)
def isr(x, y): return inside_triangle(x, y, SPR_L, SPR_R, SPIRE_TOP, SPIRE_BASE)
dense_fill(sp, SPIRE_L_POOL, isl, (SPL_L, SPIRE_TOP, SPL_R, SPIRE_BASE),
           C_TRUTH, base_size=4, size_var=2, hero_count=5, hero_size_range=(7, 10))
dense_fill(sp, SPIRE_R_POOL, isr, (SPR_L, SPIRE_TOP, SPR_R, SPIRE_BASE),
           C_TRUTH, base_size=4, size_var=2, hero_count=5, hero_size_range=(7, 10))
# Crosses atop spires
for cx in [(SPL_L + SPL_R) // 2, (SPR_L + SPR_R) // 2]:
    sp.add(dwg.line((cx, SPIRE_TOP - 18), (cx, SPIRE_TOP + 3),
                    stroke=GOLD, stroke_width=1.5))
    sp.add(dwg.line((cx - 6, SPIRE_TOP - 10), (cx + 6, SPIRE_TOP - 10),
                    stroke=GOLD, stroke_width=1.0))
dwg.add(sp)

# ---- ROSE WINDOW ----
rose = dwg.g(id='rose')
def inside_rose(x, y): return inside_circle(x, y, RW_CX, RW_CY, RW_R)
dense_fill(rose, ROSE_POOL, inside_rose,
           (RW_CX - RW_R, RW_CY - RW_R, RW_CX + RW_R, RW_CY + RW_R),
           GOLD_BRIGHT, base_size=4.5, size_var=2.5,
           opacity_range=(0.4, 0.85), hero_count=8,
           hero_size_range=(8, 13))
# Concentric ring text
for r_frac, fs, words in [
    (0.3, 5, ['Deus Caritas Est']),
    (0.55, 4.5, ROSE_POOL[:10]),
    (0.78, 4, ROSE_POOL),
    (0.95, 3.5, ROSE_POOL),
]:
    r = RW_R * r_frac
    d = (f'M {RW_CX - r},{RW_CY} '
         f'A {r},{r} 0 1 1 {RW_CX + r},{RW_CY} '
         f'A {r},{r} 0 1 1 {RW_CX - r},{RW_CY}')
    random.shuffle(words)
    curved_text(rose, d, words, font_size=fs, color=GOLD, repeat=3, opacity=0.6)
dwg.add(rose)

# ---- CLERESTORY WINDOWS (7 Sacraments) ----
wins = dwg.g(id='windows')
sac_order = ['baptism', 'confirmation', 'penance', 'eucharist',
             'anointing', 'orders', 'matrimony']
CW_L2, CW_R2 = CAT_L + 18, CAT_R - 18
gap = 7
n_wins = 7
win_w = (CW_R2 - CW_L2 - (n_wins - 1) * gap) / n_wins

for i, sac in enumerate(sac_order):
    wx = CW_L2 + i * (win_w + gap)
    wx2 = wx + win_w
    wy_base = CW_BOT
    wy_peak = CW_TOP
    col = SC[sac]

    def make_inside(wx=wx, wx2=wx2, wy_base=wy_base, wy_peak=wy_peak):
        def fn(x, y):
            return inside_pointed_arch(x, y, wx, wx2, wy_base, wy_peak)
        return fn

    dense_fill(wins, SAC_POOLS[sac], make_inside(),
               (wx, wy_peak, wx2, wy_base), col,
               base_size=3.5, size_var=1.5,
               opacity_range=(0.5, 0.9), hero_count=3,
               hero_size_range=(6, 9))
dwg.add(wins)

# ---- TRIFORIUM ----
tri = dwg.g(id='triforium')
def inside_tri(x, y):
    return inside_rect(x, y, CAT_L + 8, TRI_TOP, CAT_R - CAT_L - 16, TRI_BOT - TRI_TOP)
dense_fill(tri, SPIRIT_POOL + GENERAL[:20], inside_tri,
           (CAT_L, TRI_TOP, CAT_R, TRI_BOT), C_PALE_GOLD,
           base_size=4, size_var=1.5, opacity_range=(0.45, 0.8))
dwg.add(tri)

# ---- VAULT RIBS (curved Scripture text) ----
vault = dwg.g(id='vault')
VPEAK = CW_BOT + 10
for px in PIL_X:
    pcx = px + PIL_W / 2
    d = f'M {pcx},{PIL_TOP} Q {(pcx + CAT_CX) / 2},{VPEAK} {CAT_CX},{VPEAK}'
    curved_text(vault, d, list(SCRIPTURE_POOL), font_size=4.5,
                color=C_PALE_GOLD, repeat=2, opacity=0.5)
# Transverse arches
for i in range(len(PIL_X) - 1):
    p1 = PIL_X[i] + PIL_W / 2
    p2 = PIL_X[i + 1] + PIL_W / 2
    mid = (p1 + p2) / 2
    d = f'M {p1},{PIL_TOP} Q {mid},{PIL_TOP - 35} {p2},{PIL_TOP}'
    curved_text(vault, d, list(SCRIPTURE_POOL), font_size=4,
                color=C_PALE_GOLD, repeat=1, opacity=0.4)
dwg.add(vault)

# ---- LATERAL WALLS ----
lat = dwg.g(id='lateral')
dense_fill_vertical(lat, VIRTUE_POOL, CAT_L + 2, PIL_TOP, 50,
                    PIL_BOT - PIL_TOP, C_JUSTICE,
                    base_size=4, size_var=1.5)
dense_fill_vertical(lat, VIRTUE_POOL, CAT_R - 52, PIL_TOP, 50,
                    PIL_BOT - PIL_TOP, C_JUSTICE,
                    base_size=4, size_var=1.5)
dwg.add(lat)

# ---- FOUR PILLARS ----
pil = dwg.g(id='pillars')
pw = [TRUTH_POOL, JUSTICE_POOL, MERCY_POOL, SACRIFICE_POOL]
pc = [C_TRUTH, C_JUSTICE, C_MERCY, C_SACRIFICE]
for i, px in enumerate(PIL_X):
    dense_fill_vertical(pil, pw[i], px, PIL_TOP, PIL_W,
                        PIL_BOT - PIL_TOP, pc[i],
                        base_size=4, size_var=2, spacing=0.85)
dwg.add(pil)

# ---- NAVE BAYS ----
nav = dwg.g(id='nave')
bays = [
    (PIL_X[0] + PIL_W, PIL_X[1], FAITH_POOL),
    (PIL_X[1] + PIL_W, PIL_X[2], CHARITY_POOL),
    (PIL_X[2] + PIL_W, PIL_X[3], HOPE_POOL),
]
for bl, br, words in bays:
    bw = br - bl
    def make_in(bl=bl, br=br):
        def fn(x, y):
            return bl + 3 <= x <= br - 3 and PIL_TOP + 15 <= y <= PIL_BOT - 15
        return fn
    dense_fill(nav, words + GENERAL, make_in(),
               (bl, PIL_TOP, br, PIL_BOT), C_PALE_GOLD,
               base_size=4, size_var=1.5, opacity_range=(0.3, 0.65),
               hero_count=8, hero_size_range=(7, 11))
dwg.add(nav)

# ---- TRANSEPTS ----
trn = dwg.g(id='transepts')
def in_trn_l(x, y):
    return TRN_L_L <= x <= TRN_L_R and TRN_TOP <= y <= TRN_BOT
def in_trn_r(x, y):
    return TRN_R_L <= x <= TRN_R_R and TRN_TOP <= y <= TRN_BOT
dense_fill(trn, BEATITUDE_POOL, in_trn_l,
           (TRN_L_L, TRN_TOP, TRN_L_R, TRN_BOT), C_MERCY,
           base_size=4, size_var=1.5, hero_count=4,
           hero_size_range=(6, 9))
dense_fill(trn, SPIRITUAL_MERCY_POOL, in_trn_r,
           (TRN_R_L, TRN_TOP, TRN_R_R, TRN_BOT), C_PALE_GOLD,
           base_size=4, size_var=1.5, hero_count=4,
           hero_size_range=(6, 9))
dwg.add(trn)

# ---- APSE ----
apse = dwg.g(id='apse')
def in_apse(x, y):
    if y > APS_CY or y < APS_CY - APS_RY:
        return False
    return inside_ellipse(x, y, APS_CX, APS_CY, APS_RX, APS_RY)
dense_fill(apse, APSE_POOL + GENERAL, in_apse,
           (APS_CX - APS_RX, APS_CY - APS_RY, APS_CX + APS_RX, APS_CY),
           C_IVORY, base_size=4.5, size_var=2,
           opacity_range=(0.4, 0.8), hero_count=6,
           hero_size_range=(8, 12))
# Curved text along apse arch
apse_d = (f'M {APS_CX - APS_RX},{APS_CY} '
          f'A {APS_RX},{APS_RY} 0 0 1 {APS_CX + APS_RX},{APS_CY}')
curved_text(apse, apse_d, list(APSE_POOL), font_size=5.5,
            color=C_IVORY, repeat=2, opacity=0.6)
dwg.add(apse)

# ---- ALTAR ----
alt = dwg.g(id='altar')
def in_alt(x, y):
    return inside_rect(x, y, ALT_L, ALT_TOP, ALT_R - ALT_L, ALT_BOT - ALT_TOP)
dense_fill(alt, EUCHARIST_POOL, in_alt,
           (ALT_L, ALT_TOP, ALT_R, ALT_BOT), C_ALTAR,
           base_size=4, size_var=2, opacity_range=(0.5, 0.9),
           hero_count=4, hero_size_range=(7, 10))
# Inscription
alt.add(dwg.text('Deus Caritas Est',
    insert=((ALT_L + ALT_R) / 2, ALT_BOT + 18),
    text_anchor='middle', font_size='8px',
    font_family='Georgia, serif', fill=GOLD_BRIGHT,
    font_weight='bold', letter_spacing='2'))
dwg.add(alt)

# ---- THE CRUCIFIX ----
crx = dwg.g(id='crucifix')

# Vertical bar
def in_crx_v(x, y):
    return CRX_CX - CRX_VW // 2 <= x <= CRX_CX + CRX_VW // 2 and CRX_TOP <= y <= CRX_BOT
dense_fill(crx, CROSS_POOL, in_crx_v,
           (CRX_CX - CRX_VW // 2, CRX_TOP, CRX_CX + CRX_VW // 2, CRX_BOT),
           C_CROSS, base_size=4, size_var=2, opacity_range=(0.6, 1.0),
           hero_count=5, hero_size_range=(7, 10))

# Horizontal bar
def in_crx_h(x, y):
    return CRX_BL <= x <= CRX_BR and CRX_BY <= y <= CRX_BY + CRX_BH
dense_fill(crx, CROSS_POOL, in_crx_h,
           (CRX_BL, CRX_BY, CRX_BR, CRX_BY + CRX_BH),
           C_CROSS, base_size=4, size_var=2, opacity_range=(0.6, 1.0),
           hero_count=6, hero_size_range=(7, 10))

# Christ's body (over the cross, different color = warm ivory)
# Head
def in_head(x, y):
    return inside_circle(x, y, C_HEAD_CX, C_HEAD_CY, C_HEAD_R)
dense_fill(crx, CHRIST_POOL[:10], in_head,
           (C_HEAD_CX - C_HEAD_R, C_HEAD_CY - C_HEAD_R,
            C_HEAD_CX + C_HEAD_R, C_HEAD_CY + C_HEAD_R),
           C_CHRIST, base_size=3.5, size_var=1.5,
           opacity_range=(0.6, 0.95), hero_count=2,
           hero_size_range=(5, 7))

# Torso
torso_hw = 26
torso_t = C_HEAD_CY + C_HEAD_R + 2
torso_b = CRX_BY - 2
def in_torso(x, y):
    return (CRX_CX - torso_hw <= x <= CRX_CX + torso_hw
            and torso_t <= y <= torso_b)
dense_fill(crx, CHRIST_POOL, in_torso,
           (CRX_CX - torso_hw, torso_t, CRX_CX + torso_hw, torso_b),
           C_CHRIST, base_size=3.5, size_var=1.5,
           opacity_range=(0.6, 0.95), hero_count=4,
           hero_size_range=(5, 8))

# Arms (along crossbar, wider than torso)
arm_y = CRX_BY + 5
arm_h = CRX_BH - 10
for (al, ar) in [(CRX_BL + 5, CRX_CX - torso_hw - 3),
                  (CRX_CX + torso_hw + 3, CRX_BR - 5)]:
    def make_arm(al=al, ar=ar):
        def fn(x, y):
            return al <= x <= ar and arm_y <= y <= arm_y + arm_h
        return fn
    dense_fill(crx, CHRIST_POOL[10:], make_arm(),
               (al, arm_y, ar, arm_y + arm_h),
               C_CHRIST, base_size=3.5, size_var=1,
               opacity_range=(0.55, 0.9))

# Legs
leg_hw = 18
leg_t = CRX_BY + CRX_BH + 2
leg_b = CRX_BOT - 10
def in_legs(x, y):
    return CRX_CX - leg_hw <= x <= CRX_CX + leg_hw and leg_t <= y <= leg_b
dense_fill(crx, CHRIST_POOL[-10:], in_legs,
           (CRX_CX - leg_hw, leg_t, CRX_CX + leg_hw, leg_b),
           C_CHRIST, base_size=3.5, size_var=1,
           opacity_range=(0.55, 0.9))

dwg.add(crx)

# ---- FLOOR ----
flr = dwg.g(id='floor')
def in_floor(x, y):
    return inside_rect(x, y, CAT_L + 55, FLR_TOP, CAT_R - CAT_L - 110, FLR_BOT - FLR_TOP)
dense_fill(flr, FLOOR_POOL + GENERAL[:15], in_floor,
           (CAT_L, FLR_TOP, CAT_R, FLR_BOT), C_SACRIFICE,
           base_size=4, size_var=1.5, opacity_range=(0.4, 0.75))
dwg.add(flr)

# ---- FOUNDATION (stepped) ----
fnd = dwg.g(id='foundation')
n_steps = 6
step_h = (FND_BOT - FND_TOP) / n_steps
for s in range(n_steps):
    sy = FND_TOP + s * step_h
    inset = (n_steps - s - 1) * 12
    sl = CAT_L - 40 + inset
    sr = CAT_R + 40 - inset
    def make_step(sl=sl, sr=sr, sy=sy, sh=step_h):
        def fn(x, y): return sl <= x <= sr and sy <= y <= sy + sh
        return fn
    dense_fill(fnd, COMMANDMENT_POOL, make_step(),
               (sl, sy, sr, sy + step_h), C_IVORY,
               base_size=4, size_var=1.5, opacity_range=(0.35, 0.7))
dwg.add(fnd)

# ============================================================
# SAVE
# ============================================================
dwg.save()
print(f'\n✓ Cathedral SVG v3 saved to:\n  {OUTPUT}\n')
