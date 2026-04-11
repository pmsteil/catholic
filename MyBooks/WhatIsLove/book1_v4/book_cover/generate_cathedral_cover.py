#!/usr/bin/env python3
"""
What Is Love? — Gothic Cathedral Book Cover SVG Generator
==========================================================
The entire cathedral is constructed from Catholic theological words about love.
Every zone maps to a theological concept from the word palette.

Output: what-is-love-cathedral-v1.svg
"""

import svgwrite
import math

# ============================================================
# CANVAS  (1200 x 1800 = 6x9 at 200 DPI equivalent; scales to any size)
# ============================================================
W, H = 1200, 1800
OUTPUT = '/Users/patiman/Desktop/designer-output/what-is-love-cathedral-v1.svg'

dwg = svgwrite.Drawing(OUTPUT, size=(f'{W}px', f'{H}px'),
                        viewBox=f'0 0 {W} {H}', profile='full')

# ============================================================
# COLORS
# ============================================================
BG           = '#2a0a0e'   # very dark wine
SKY_TEXT     = '#4a1828'   # barely-visible muted (sky/exterior names of God)
GOLD         = '#C9A84C'   # antique gold (architectural lines)
GOLD_BRIGHT  = '#F0D060'   # bright gold (sun)
GOLD_PALE    = '#d4bc7a'   # pale gold (general text)
C_TRUTH      = '#c8a830'   # truth — warm gold
C_JUSTICE    = '#7a40b0'   # justice — purple (visible on dark bg)
C_MERCY      = '#c09098'   # mercy — pale rose
C_SACRIFICE  = '#901010'   # sacrifice — deep crimson
C_IVORY      = '#ede8dc'   # ivory (apse, Christ body)
C_PALE_GOLD  = '#d0b870'   # pale gold (triforium, vault)
C_CHRIST     = '#e8c880'   # warm ivory (Christ figure)

# Stained glass: (window_bg, text_color)
SAC_COLORS = {
    'baptism':      ('#0a1e35', '#6090b8'),
    'confirmation': ('#380808', '#c07070'),
    'eucharist':    ('#352300', '#c89828'),
    'penance':      ('#1e0038', '#9060b0'),
    'anointing':    ('#081e08', '#508050'),
    'orders':       ('#1e1000', '#b08030'),
    'matrimony':    ('#380018', '#c06080'),
}

# ============================================================
# WORD LISTS
# ============================================================

EXTERIOR = [
    "Father", "Abba", "YHWH", "I AM", "Emmanuel", "Creator", "Almighty",
    "Holy", "Holy", "Holy", "Eternal", "Infinite", "Alpha", "Omega",
    "El Shaddai", "Adonai", "Lord of Lords", "King of Kings",
    "Ancient of Days", "Ruach", "Breath of God", "Spirit", "Light",
    "In the beginning", "Logos", "Life", "Love", "Let there be light",
    "It was good", "He who is", "Perfect goodness", "Perfect beauty",
    "Transcendent", "Immanent", "Omnipotent", "Holy One", "Paraclete",
    "Advocate", "Comforter", "Bond of Love", "Perichoresis",
    "Three Persons", "One God", "Triune Love", "Divine Life",
    "Shared love", "Gift of self", "Source of all love", "Ground of being",
    "Before all time", "Without beginning", "Without end", "From eternity",
    "Trinity", "Father Son Holy Spirit", "Divine communion",
    "God himself is an eternal exchange of love",
]

COMMANDMENTS = [
    "I AM the Lord your God", "No other gods before me",
    "You shall not take the Lord's name in vain",
    "Keep holy the Sabbath", "Honor your father and mother",
    "You shall not kill", "You shall not commit adultery",
    "You shall not steal", "You shall not bear false witness",
    "You shall not covet", "The Decalogue", "Ten Commandments",
    "Natural law", "Moral law", "Written on the heart",
    "Conscience", "Foundation of justice", "Sinai", "Moses",
    "Law as gift", "Love the Lord your God", "Love your neighbor",
    "On these two all the law depends", "Divine law", "Eternal law",
]

TRUTH_W = [
    "Truth", "Logos", "The Word", "Light", "Revelation",
    "In the beginning was the Word", "The Word became flesh",
    "I am the Way the Truth and the Life", "Your Word is truth",
    "The truth will set you free", "Sacred Scripture",
    "Sacred Tradition", "Magisterium", "Deposit of Faith",
    "Doctrine", "Creed", "Catechism", "Inerrancy", "Infallibility",
    "Emet", "Aletheia", "Fides et Ratio", "Reason",
    "Uncreated Light", "Transfiguration", "Illumination",
    "Faith seeking understanding", "Evangelization", "Catechesis",
    "Witness", "Teaching", "Gospel", "Canon", "Orthodoxy",
]

JUSTICE_W = [
    "Justice", "Righteousness", "Right order", "Covenant law",
    "Divine law", "Natural law", "Moral law", "Commandments",
    "Mishpat", "Dikaiosyne", "Commutative", "Distributive",
    "Social justice", "Legal justice", "Accountability",
    "Restitution", "Rectitude", "Equity", "Fairness",
    "Let justice roll like a river", "Do justice love mercy",
    "Authority", "Sovereignty", "Divine governance", "Providence",
    "Synderesis", "Moral conscience", "Proportionality",
    "Reparation", "Satisfaction", "Due order", "Suum cuique",
]

MERCY_W = [
    "Mercy", "Compassion", "Lovingkindness", "Tenderness",
    "Hesed", "Rahamim", "Misericordia", "Eleos",
    "Forgiveness", "Pardon", "Absolution", "Reconciliation",
    "His mercy endures forever", "I desire mercy not sacrifice",
    "Divine Mercy", "Living water", "Grace", "Gift",
    "Be merciful as your Father", "Patience", "Long-suffering",
    "Seventy times seven", "Prodigal Father", "Lost sheep",
    "Come to me all who are weary", "Solidarity", "Presence",
    "Gentleness", "Forbearance", "Healing", "Tenderness",
]

SACRIFICE_W = [
    "Sacrifice", "Offering", "Oblation", "Kenosis",
    "Covenant blood", "Without the shedding of blood",
    "Greater love has no one than this", "The Cross", "Passion",
    "Calvary", "Good Friday", "Via Dolorosa", "Redemption",
    "Ransom", "Propitiation", "Expiation", "Atonement",
    "Lamb of God", "It is finished", "Tetelestai", "Consummatum est",
    "Red ray", "Martyrdom", "Take up your cross",
    "Not my will but yours", "Total gift of self", "Fiat",
    "He humbled himself", "Obedient unto death",
]

FAITH_W = [
    "Faith", "Fides", "Belief", "Trust", "Assent", "Surrender",
    "I believe", "Credo", "Confession", "Profession of faith",
    "Lord I believe help my unbelief",
    "Faith is the substance of things hoped for",
    "Faith without works is dead", "Living faith", "Abraham",
    "Father of faith", "Fidelity", "Commitment", "Perseverance",
    "Cloud of witnesses", "Gift of faith", "Baptismal faith",
]

HOPE_W = [
    "Hope", "Spes", "Expectation", "Longing", "Come Lord Jesus",
    "Maranatha", "Beatific vision", "Heaven", "Eternal life",
    "Resurrection", "He will wipe away every tear",
    "Anchor of hope", "We are saved in hope", "Promise",
    "Covenant promise", "Fulfillment", "Trust", "Confidence",
    "Consolation", "Purgatory", "Communion of saints",
    "Eye has not seen", "Parousia", "Advent longing",
]

CHARITY_W = [
    "Charity", "Caritas", "Agape", "Love", "Amor",
    "Charity is the form of all the virtues",
    "Binds everything together in perfect harmony",
    "The greatest of these is love", "Love never fails",
    "Love is patient", "Love is kind", "We love because he first loved us",
    "Beloved let us love one another", "Benevolence", "Goodwill",
    "Friendship with God", "Communion", "Gift of self", "Life-giving",
]

BEATITUDES = [
    "Blessed are the poor in spirit", "Kingdom of heaven",
    "Blessed are those who mourn", "They shall be comforted",
    "Blessed are the meek", "They shall inherit the earth",
    "Hunger and thirst for righteousness", "They shall be satisfied",
    "Blessed are the merciful", "They shall receive mercy",
    "Blessed are the pure in heart", "They shall see God",
    "Blessed are the peacemakers", "Sons of God",
    "Persecuted for righteousness", "Rejoice and be glad",
    "Beatitudes depict the countenance of Christ",
    "They express the vocation of the faithful",
]

SPIRITUAL_MERCY = [
    "Instruct the ignorant", "Counsel the doubtful",
    "Admonish sinners", "Bear wrongs patiently",
    "Forgive injuries willingly", "Comfort the afflicted",
    "Pray for the living and the dead", "Works of mercy",
    "Service of the soul", "Guiding toward truth",
    "Patience with weakness", "Intercession", "Accompany",
]

GIFTS_FRUITS = [
    "Wisdom", "Understanding", "Counsel", "Fortitude",
    "Knowledge", "Piety", "Fear of the Lord",
    "Seven gifts of the Holy Spirit", "Donum Dei",
    "Love", "Joy", "Peace", "Patience", "Kindness",
    "Goodness", "Faithfulness", "Gentleness", "Self-control",
    "Generosity", "Fruits of the Spirit",
    "By their fruits you shall know them",
]

VAULT_SCRIPTURE = [
    "God is love and whoever abides in love abides in God",
    "Greater love has no one than this",
    "Love one another as I have loved you",
    "A new commandment I give you", "Love your enemies",
    "Love the Lord your God with all your heart",
    "The greatest of these is love", "Love never fails",
    "Nothing can separate us from the love of God",
    "Perfect love casts out fear", "He loved them to the end",
    "God so loved the world that he gave his only Son",
    "We love because he first loved us",
    "This is how all will know you are my disciples by your love",
]

EUCHARIST_ALTAR = [
    "This is my Body", "This is my Blood",
    "Do this in memory of me", "Anamnesis",
    "Real Presence", "Transubstantiation", "Consecration",
    "Body Blood Soul Divinity", "Corpus Christi", "Agnus Dei",
    "Bread of Life", "Living Bread", "Communion",
    "Source and summit", "Mysterium Fidei",
    "Sanctus Sanctus Sanctus", "Sursum Corda",
    "Lift up your hearts", "Dona nobis pacem", "Kyrie Eleison",
    "Ite Missa Est", "Gloria in Excelsis Deo",
]

APSE_W = [
    "God's Perfect Love", "Sacred gift of covenant",
    "Binding truth justice mercy and sacrifice",
    "Into life-giving communion", "Deus Caritas Est",
    "Charity is the form of all the virtues",
    "Binds everything together in perfect harmony",
    "To love is to will the good of another",
    "The whole of doctrine directed to the love that never ends",
    "God himself is an eternal exchange of love",
    "Father Son and Holy Spirit",
    "He has destined us to share in that exchange",
    "Love is the fundamental vocation of every human being",
    "Agape", "Caritas", "Hesed", "Amor",
]

SAC_WORDS = {
    'baptism': [
        "Baptism", "Rebirth", "New life", "Water", "Spirit", "Font",
        "Immersion", "Washing", "Cleansing", "Adoption", "Sonship",
        "Original sin removed", "Regeneration", "White garment",
        "Chrism", "You are my beloved", "Born of water and spirit",
        "Death to sin", "Rising to new life", "Body of Christ",
    ],
    'confirmation': [
        "Confirmation", "Seal", "Strengthening", "Mission", "Witness",
        "Gifts of the Spirit", "Chrism", "Laying on of hands",
        "Be sealed with the gift of the Holy Spirit",
        "Pentecost", "Tongues of fire", "Wind", "Anointing",
        "Mature discipleship", "Apostolic mission", "Soldier of Christ",
    ],
    'eucharist': [
        "Eucharist", "Real Presence", "Transubstantiation",
        "Body", "Blood", "Soul", "Divinity", "Corpus Christi",
        "This is my Body", "Consecration", "Source and summit",
        "Bread of Life", "Communion", "Altar", "Chalice", "Host",
        "Monstrance", "Adoration", "Last Supper", "Viaticum",
    ],
    'penance': [
        "Penance", "Reconciliation", "Confession", "Contrition",
        "Absolution", "Satisfaction", "I absolve you",
        "Your sins are forgiven", "Tribunal of mercy",
        "Seal of confession", "Prodigal son", "Healing",
        "Amendment of life", "Act of contrition", "Restoration",
    ],
    'anointing': [
        "Anointing of the Sick", "Viaticum", "Oil", "Prayer",
        "Comfort", "Healing", "Union with Christ's suffering",
        "Redemptive suffering", "Peace", "Is anyone sick",
        "The prayer of faith will save the sick",
        "Preparation for death", "Fortitude", "Last Rites",
    ],
    'orders': [
        "Holy Orders", "Priesthood", "Ordination", "Alter Christus",
        "Apostolic succession", "Bishop", "Priest", "Deacon",
        "Ministry", "Celibacy", "Service", "Shepherd",
        "Fishers of men", "Ambassadors for Christ",
        "Priest forever after the order of Melchizedek",
        "Laying on of hands", "Sacred character",
    ],
    'matrimony': [
        "Matrimony", "Marriage", "Covenant", "Nuptial bond",
        "Fidelity", "Fruitfulness", "Indissolubility",
        "Domestic church", "Family", "Free total faithful fruitful",
        "The two shall become one flesh", "Spousal love",
        "Theology of the Body", "Gift of self", "New life",
        "What God has joined let no man separate",
    ],
}

CROSS_W = [
    "Sacrifice", "Atonement", "Propitiation", "Expiation",
    "Covenant blood", "Calvary", "Passion", "Tetelestai",
    "It is finished", "Ransom", "Redemption", "Good Friday",
    "He was pierced for our sins", "By his wounds we are healed",
    "Without the shedding of blood", "Obedient unto death",
    "Lamb of God", "Agnus Dei", "Greater love has no one",
    "He gave himself for us", "Poured out for many",
]

CHR_HEAD_W = [
    "INRI", "King of the Jews", "Ecce Homo", "Crown of thorns",
    "Behold the Man", "He was despised and rejected",
    "Man of sorrows", "Son of God", "Son of Man", "Emmanuel",
    "God with us", "Messiah", "Anointed One", "Holy One",
]

CHR_BODY_W = [
    "The Word became flesh", "Incarnation",
    "True God and True Man", "Hypostatic union",
    "Sacred Heart", "Wounded side", "Blood and water flowed out",
    "He loved them to the end", "Kenosis", "Self-emptying",
    "He emptied himself", "Servant of all",
    "By his wounds we are healed", "Pierced for our transgressions",
    "Divine mercy", "Body given for you", "Blood poured out",
    "Real Presence", "Corpus Christi",
]

CHR_ARMS_W = [
    "Come to me all who are weary", "I will give you rest",
    "Outstretched arms", "Covenant embrace",
    "I have loved you with an everlasting love",
    "Arms open wide", "Welcome", "Receive",
    "As the Father has loved me so have I loved you",
    "I have called you friends",
]

CHR_LEGS_W = [
    "Cornerstone", "Foundation", "He humbled himself",
    "Servant of all", "Washed the disciples feet",
    "I came not to be served but to serve",
    "Death is swallowed up in victory",
    "He is risen", "Alleluia", "New life",
]

SPIRE_L = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "Samuel", "Kings", "Chronicles",
    "Psalms", "Proverbs", "Wisdom", "Sirach", "Isaiah", "Jeremiah",
    "Ezekiel", "Daniel", "Hosea", "Amos", "Micah", "Zechariah",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "Corinthians", "Galatians", "Ephesians", "Philippians",
    "Colossians", "Hebrews", "James", "Peter", "Revelation",
    "The Word of God", "Verbum Domini", "Sacred Scripture",
]

SPIRE_R = [
    "Jesus", "Christ", "Messiah", "Emmanuel", "Logos",
    "Son of God", "Son of Man", "Lamb of God", "Good Shepherd",
    "Light of the World", "Bread of Life", "Living Water",
    "True Vine", "Resurrection and Life", "Way Truth and Life",
    "Alpha and Omega", "First and Last", "Lord", "Savior",
    "Redeemer", "King", "Priest", "Prophet", "Sacred Heart",
    "Prince of Peace", "Wonderful Counselor", "Mighty God",
    "Eternal Father", "I AM", "Holy One", "Risen Lord",
    "Crucified Lord", "Pantocrator", "Christ the King",
]

LATERAL_VIRTUES = [
    "Prudence", "Justice", "Fortitude", "Temperance",
    "Practical wisdom", "Right reason", "Discernment",
    "Counsel", "Courage", "Perseverance", "Endurance",
    "Self-mastery", "Moderation", "Chastity", "Humility",
    "Meekness", "Cardinal virtues", "Moral formation",
    "Imago Dei", "Human dignity", "Sanctity of life",
    "The virtuous life", "Character", "Formed by love",
]

FLOOR_W = [
    "Feed the hungry", "Give drink to the thirsty",
    "Clothe the naked", "Shelter the homeless",
    "Visit the sick", "Visit the imprisoned", "Bury the dead",
    "For I was hungry and you gave me food",
    "Whatever you did for the least of these",
    "Almsgiving", "Solidarity", "Care for the poor",
    "Love made visible", "Love at work", "Corporal works of mercy",
]

ROSE_W = [
    "Deus Caritas Est", "God is Love", "Agape", "Caritas",
    "Hesed", "Amor", "Amore", "Amour", "Liebe",
    "Father", "Son", "Holy Spirit", "Trinity", "Perichoresis",
    "God's Perfect Love", "Covenant", "Communion",
    "Eternal exchange of love", "Three Persons One God",
]

# ============================================================
# GEOMETRY
# ============================================================

# Cathedral outer bounds
CAT_L = 190
CAT_R = 1010
CAT_TOP = 340
CAT_BOT = 1660

# Spires
SPL = (200, 330, 80, CAT_TOP)   # (left, right, top, bottom)
SPR = (870, 1000, 80, CAT_TOP)

# Central block (between spires, upper section)
CTR_L, CTR_R = 340, 860

# Rose window
RW_CX, RW_CY, RW_R = 600, 270, 108

# Clerestory windows (7 across)
CW_TOP, CW_BOT = 350, 520
CW_L, CW_R = CAT_L + 15, CAT_R - 15

# Triforium
TRI_TOP, TRI_BOT = 528, 595
TRI_L, TRI_R = CAT_L + 10, CAT_R - 10

# Lateral walls (buttresses)
LAT_L  = (CAT_L,      CAT_L + 55,  600, 1370)  # (l, r, top, bot)
LAT_R  = (CAT_R - 55, CAT_R,       600, 1370)

# Four pillars: x centers
PIL_TOP, PIL_BOT, PIL_W = 600, 1370, 32
PIL_XC = [
    CAT_L + 80,           # Truth
    CAT_L + 290,          # Justice
    CAT_R - 290 - PIL_W,  # Mercy
    CAT_R - 80 - PIL_W,   # Sacrifice
]

# Nave bays between pillars
BAY_TOP, BAY_BOT = 600, 1370
BAY1_L = PIL_XC[0] + PIL_W
BAY1_R = PIL_XC[1]
BAY2_L = PIL_XC[1] + PIL_W
BAY2_R = PIL_XC[2]
BAY3_L = PIL_XC[2] + PIL_W
BAY3_R = PIL_XC[3]

# Transepts
TRN_TOP, TRN_BOT = 890, 1100
TRN_L = (CAT_L - 90, CAT_L + 5, TRN_TOP, TRN_BOT)
TRN_R = (CAT_R - 5,  CAT_R + 90, TRN_TOP, TRN_BOT)

# Apse (sanctuary behind altar)
APS_L, APS_R, APS_TOP, APS_BOT = 370, 830, 608, 880

# Altar
ALT_L, ALT_R, ALT_TOP, ALT_BOT = 450, 750, 886, 935

# Floor
FLR_TOP, FLR_BOT = 1370, 1460

# Foundation
FND_TOP, FND_BOT = 1460, 1660

# Crucifix geometry
CRX_CX   = 600
CRX_TOP  = 618
CRX_BOT  = 880
CRX_VW   = 38          # vertical bar width
CRX_BY   = 740         # crossbar Y
CRX_BH   = 36          # crossbar height
CRX_BL   = 445         # crossbar left
CRX_BR   = 755         # crossbar right

# Christ body zones (within / over cross)
C_HEAD_CX, C_HEAD_CY, C_HEAD_R = CRX_CX, 668, 22
C_TRS_L  = CRX_CX - 18
C_TRS_R  = CRX_CX + 18
C_TRS_T  = C_HEAD_CY + C_HEAD_R
C_TRS_B  = CRX_BY
C_LEG_L  = CRX_CX - 14
C_LEG_R  = CRX_CX + 14
C_LEG_T  = CRX_BY + CRX_BH
C_LEG_B  = CRX_BOT - 5
# Arms (left/right of torso on crossbar)
C_ARM_LL = CRX_BL + 5
C_ARM_LR = C_TRS_L - 5
C_ARM_RL = C_TRS_R + 5
C_ARM_RR = CRX_BR - 5

# ============================================================
# HELPER: FILL RECTANGLE WITH WORDS (row-by-row packing)
# ============================================================
def fill_rect(group, x, y, w, h, words,
              font_size=7.0, color=GOLD_PALE,
              font_family='Georgia, serif', line_spacing=1.45):
    if w <= 4 or h <= 4 or not words:
        return
    lh = font_size * line_spacing
    avg_cw = font_size * 0.53
    sep = u' \u00b7 '
    sep_w = len(sep) * avg_cw
    cy = y + font_size + 1.0
    wi = 0
    total = len(words)

    while cy <= y + h - 2:
        cx = x + 2.0
        tokens = []
        while True:
            word = words[wi % total]
            ww = len(word) * avg_cw
            needed = ww + (sep_w if tokens else 0)
            if cx + needed > x + w - 2:
                wi = (wi + 1) % total
                break
            if tokens:
                cx += sep_w
            tokens.append(word)
            cx += ww
            wi = (wi + 1) % total
        if tokens:
            group.add(dwg.text(
                sep.join(tokens),
                insert=(x + 2, cy),
                font_size=f'{font_size}px',
                font_family=font_family,
                fill=color,
            ))
        cy += lh

# ============================================================
# BEGIN DRAWING
# ============================================================

# --- Background ---
dwg.add(dwg.rect((0, 0), (W, H), fill=BG))

# ============================================================
# EXTERIOR / SKY — Names of God, very subtle
# ============================================================
sky = dwg.g(id='sky')

# Left sky strip
fill_rect(sky, 0, 0, CAT_L - 5, H, EXTERIOR,
          font_size=7, color=SKY_TEXT)
# Right sky strip
fill_rect(sky, CAT_R + 5, 0, W - CAT_R - 5, H, EXTERIOR,
          font_size=7, color=SKY_TEXT)
# Sky above cathedral (between spires)
fill_rect(sky, SPL[1], 0, SPR[0] - SPL[1], SPL[2] + 20, EXTERIOR,
          font_size=7, color=SKY_TEXT)
# Sky flanking spires
fill_rect(sky, SPL[0], 0, SPL[1] - SPL[0], CAT_TOP, EXTERIOR,
          font_size=7, color=SKY_TEXT)
fill_rect(sky, SPR[0], 0, SPR[1] - SPR[0], CAT_TOP, EXTERIOR,
          font_size=7, color=SKY_TEXT)
# Ground below cathedral
fill_rect(sky, 0, FND_BOT, W, H - FND_BOT, EXTERIOR,
          font_size=7, color=SKY_TEXT)

dwg.add(sky)

# ============================================================
# SUN / "DEUS CARITAS EST" — above cathedral, subtle radiance
# ============================================================
sun_cx, sun_cy = 600, 95
# Soft glow rings
for i in range(5, 0, -1):
    dwg.add(dwg.circle(
        center=(sun_cx, sun_cy), r=i * 18 + 12,
        fill='none', stroke=GOLD_BRIGHT,
        stroke_width=0.4, opacity=0.08 + i * 0.025,
    ))
# "DEUS CARITAS EST"
dwg.add(dwg.text('DEUS CARITAS EST',
    insert=(sun_cx, sun_cy - 4),
    text_anchor='middle', dominant_baseline='middle',
    font_size='13px', font_family='Georgia, serif',
    fill=GOLD_BRIGHT, font_weight='bold', letter_spacing='2',
))
dwg.add(dwg.text('God is Love',
    insert=(sun_cx, sun_cy + 13),
    text_anchor='middle',
    font_size='8px', font_family='Georgia, serif',
    fill=GOLD_PALE,
))

# ============================================================
# SPIRES
# ============================================================
spires = dwg.g(id='spires')
fill_rect(spires, SPL[0] + 4, SPL[2] + 15, SPL[1] - SPL[0] - 8,
          SPL[3] - SPL[2] - 15, SPIRE_L, font_size=6, color=C_TRUTH)
fill_rect(spires, SPR[0] + 4, SPR[2] + 15, SPR[1] - SPR[0] - 8,
          SPR[3] - SPR[2] - 15, SPIRE_R, font_size=6, color=C_TRUTH)
dwg.add(spires)

# ============================================================
# ROSE WINDOW
# ============================================================
rose = dwg.g(id='rose_window')
# Window background
rose.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R,
                    fill='#1e1000', stroke=GOLD, stroke_width=1.5))
# Spoke lines
for a in range(0, 360, 45):
    rad = math.radians(a)
    rose.add(dwg.line(
        start=(RW_CX + RW_R * 0.25 * math.cos(rad),
               RW_CY + RW_R * 0.25 * math.sin(rad)),
        end=(RW_CX + RW_R * math.cos(rad),
             RW_CY + RW_R * math.sin(rad)),
        stroke=GOLD, stroke_width=0.6, opacity='0.5',
    ))
# Inner ring circle
rose.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R * 0.3,
                    fill='none', stroke=GOLD, stroke_width=0.6))
rose.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R * 0.62,
                    fill='none', stroke=GOLD, stroke_width=0.6))
# Words placed radially
radii = [
    (0,          RW_R * 0.22, 9,  [u'Deus Caritas Est'], GOLD_BRIGHT),
    (RW_R * 0.35, RW_R * 0.55, 6, ROSE_W[:8], GOLD_PALE),
    (RW_R * 0.65, RW_R * 0.9, 5,  ROSE_W,    C_PALE_GOLD),
]
for r_in, r_out, fsize, words, col in radii:
    if r_in == 0:
        rose.add(dwg.text(words[0],
            insert=(RW_CX, RW_CY + 3),
            text_anchor='middle', dominant_baseline='middle',
            font_size=f'{fsize}px', font_family='Georgia, serif',
            fill=col, font_weight='bold',
        ))
        continue
    r_mid = (r_in + r_out) / 2
    circumference = 2 * math.pi * r_mid
    n = max(1, int(circumference / (fsize * 5.5)))
    for j in range(n):
        angle = 2 * math.pi * j / n - math.pi / 2
        rx = RW_CX + r_mid * math.cos(angle)
        ry = RW_CY + r_mid * math.sin(angle)
        word = words[j % len(words)]
        rose.add(dwg.text(word,
            insert=(rx, ry),
            text_anchor='middle', dominant_baseline='middle',
            font_size=f'{fsize}px', font_family='Georgia, serif',
            fill=col,
            transform=f'rotate({math.degrees(angle) + 90},{rx},{ry})',
        ))
dwg.add(rose)

# ============================================================
# CLERESTORY WINDOWS — 7 Sacraments
# ============================================================
win_grp = dwg.g(id='clerestory')
sac_order = ['baptism', 'confirmation', 'eucharist',
             'penance', 'anointing', 'orders', 'matrimony']
sac_labels = ['Baptism', 'Confirmation', 'Eucharist',
              'Penance', 'Anointing', 'Orders', 'Matrimony']
n_wins = 7
total_w = CW_R - CW_L
gap = 6
win_w = (total_w - (n_wins - 1) * gap) / n_wins
win_h = CW_BOT - CW_TOP

for i, sac in enumerate(sac_order):
    wx = CW_L + i * (win_w + gap)
    wy = CW_TOP
    bg, txt = SAC_COLORS[sac]
    # Arch top  (simple pointed arch using polygon)
    arch_pt = win_w / 2
    win_grp.add(dwg.polygon(
        points=[(wx, wy + arch_pt),
                (wx + win_w / 2, wy),
                (wx + win_w, wy + arch_pt),
                (wx + win_w, wy + win_h),
                (wx, wy + win_h)],
        fill=bg,
    ))
    fill_rect(win_grp, wx + 2, wy + arch_pt / 2 + 2,
              win_w - 4, win_h - arch_pt / 2 - 4,
              SAC_WORDS[sac], font_size=5.5, color=txt)
    win_grp.add(dwg.text(
        sac_labels[i],
        insert=(wx + win_w / 2, CW_BOT + 14),
        text_anchor='middle', font_size='6px',
        font_family='Georgia, serif',
        fill=GOLD, font_weight='bold',
    ))
dwg.add(win_grp)

# ============================================================
# TRIFORIUM — Gifts & Fruits of the Holy Spirit
# ============================================================
tri = dwg.g(id='triforium')
fill_rect(tri, TRI_L, TRI_TOP, TRI_R - TRI_L, TRI_BOT - TRI_TOP,
          GIFTS_FRUITS, font_size=6.5, color=C_PALE_GOLD)
dwg.add(tri)

# ============================================================
# LATERAL WALLS — Cardinal Virtues
# ============================================================
lat = dwg.g(id='lateral_walls')
ll, lr, lt, lb = LAT_L
fill_rect(lat, ll, lt, lr - ll, lb - lt, LATERAL_VIRTUES,
          font_size=6, color=C_JUSTICE)
rl, rr, rt, rb = LAT_R
fill_rect(lat, rl, rt, rr - rl, rb - rt, LATERAL_VIRTUES,
          font_size=6, color=C_JUSTICE)
dwg.add(lat)

# ============================================================
# FOUR PILLARS — Truth, Justice, Mercy, Sacrifice
# ============================================================
pil = dwg.g(id='pillars')
pil_words  = [TRUTH_W, JUSTICE_W, MERCY_W, SACRIFICE_W]
pil_colors = [C_TRUTH, C_JUSTICE, C_MERCY, C_SACRIFICE]
pil_labels = ['TRUTH', 'JUSTICE', 'MERCY', 'SACRIFICE']

for i, px in enumerate(PIL_XC):
    fill_rect(pil, px, PIL_TOP, PIL_W, PIL_BOT - PIL_TOP,
              pil_words[i], font_size=5.0, color=pil_colors[i])

dwg.add(pil)

# ============================================================
# NAVE BAYS — Theological Virtues
# ============================================================
nav = dwg.g(id='nave')
fill_rect(nav, BAY1_L, BAY_TOP, BAY1_R - BAY1_L, BAY_BOT - BAY_TOP,
          FAITH_W, font_size=6.5, color=C_PALE_GOLD)
fill_rect(nav, BAY3_L, BAY_TOP, BAY3_R - BAY3_L, BAY_BOT - BAY_TOP,
          HOPE_W,  font_size=6.5, color=C_PALE_GOLD)
# Central bay (BAY2) - charity words in background of the apse zone
fill_rect(nav, BAY2_L, BAY_TOP, BAY2_R - BAY2_L, APS_TOP - BAY_TOP,
          CHARITY_W, font_size=6.5, color=C_PALE_GOLD)
dwg.add(nav)

# ============================================================
# TRANSEPTS — Beatitudes (left), Spiritual Works of Mercy (right)
# ============================================================
trn = dwg.g(id='transepts')
tl, tr, tt, tb = TRN_L
fill_rect(trn, tl, tt, tr - tl, tb - tt, BEATITUDES,
          font_size=6, color=C_MERCY)
rl2, rr2, rt2, rb2 = TRN_R
fill_rect(trn, rl2, rt2, rr2 - rl2, rb2 - rt2, SPIRITUAL_MERCY,
          font_size=6, color=C_PALE_GOLD)
dwg.add(trn)

# ============================================================
# APSE — Core definition + CCC quotes
# ============================================================
aps = dwg.g(id='apse')
fill_rect(aps, APS_L, APS_TOP, APS_R - APS_L, APS_BOT - APS_TOP,
          APSE_W, font_size=6.5, color=C_IVORY)
dwg.add(aps)

# ============================================================
# VAULT / CEILING — Scripture passages on love
# ============================================================
vlt = dwg.g(id='vault')
# Upper vault (above clerestory, between spires)
fill_rect(vlt, CTR_L, CAT_TOP, CTR_R - CTR_L, CW_TOP - CAT_TOP,
          VAULT_SCRIPTURE, font_size=6.5, color=C_PALE_GOLD)
dwg.add(vlt)

# ============================================================
# ALTAR — Eucharistic vocabulary
# ============================================================
alt = dwg.g(id='altar')
fill_rect(alt, ALT_L, ALT_TOP, ALT_R - ALT_L, ALT_BOT - ALT_TOP,
          EUCHARIST_ALTAR, font_size=6, color=C_TRUTH)
# "Deus Caritas Est" carved into altar front
dwg.add(dwg.text('Deus Caritas Est',
    insert=((ALT_L + ALT_R) / 2, (ALT_TOP + ALT_BOT) / 2 + 3),
    text_anchor='middle', dominant_baseline='middle',
    font_size='8px', font_family='Georgia, serif',
    fill=GOLD_BRIGHT, font_weight='bold', letter_spacing='1',
))
dwg.add(alt)

# ============================================================
# FLOOR — Corporal Works of Mercy
# ============================================================
flr = dwg.g(id='floor')
fill_rect(flr, CAT_L + 60, FLR_TOP, CAT_R - CAT_L - 120, FLR_BOT - FLR_TOP,
          FLOOR_W, font_size=6.5, color=C_SACRIFICE)
dwg.add(flr)

# ============================================================
# FOUNDATION / STEPS — Ten Commandments
# ============================================================
fnd = dwg.g(id='foundation')
fill_rect(fnd, CAT_L - 20, FND_TOP, CAT_R - CAT_L + 40, FND_BOT - FND_TOP,
          COMMANDMENTS, font_size=6.5, color=C_IVORY)
dwg.add(fnd)

# ============================================================
# THE CRUCIFIX — Cross + Christ's body
# ============================================================
crx = dwg.g(id='crucifix')

# Vertical bar (Sacrifice/Redemption words)
fill_rect(crx, CRX_CX - CRX_VW // 2, CRX_TOP,
          CRX_VW, CRX_BOT - CRX_TOP,
          CROSS_W, font_size=5.0, color=C_SACRIFICE)

# Horizontal bar
fill_rect(crx, CRX_BL, CRX_BY, CRX_BR - CRX_BL, CRX_BH,
          CROSS_W, font_size=5.0, color=C_SACRIFICE)

# Christ: HEAD
fill_rect(crx,
          C_HEAD_CX - C_HEAD_R, C_HEAD_CY - C_HEAD_R,
          C_HEAD_R * 2, C_HEAD_R * 2,
          CHR_HEAD_W, font_size=4.5, color=C_CHRIST)

# Christ: TORSO
fill_rect(crx, C_TRS_L, C_TRS_T, C_TRS_R - C_TRS_L, C_TRS_B - C_TRS_T,
          CHR_BODY_W, font_size=4.5, color=C_CHRIST)

# Christ: LEFT ARM
fill_rect(crx, C_ARM_LL, CRX_BY + 3, C_ARM_LR - C_ARM_LL, CRX_BH - 6,
          CHR_ARMS_W, font_size=4.5, color=C_CHRIST)

# Christ: RIGHT ARM
fill_rect(crx, C_ARM_RL, CRX_BY + 3, C_ARM_RR - C_ARM_RL, CRX_BH - 6,
          CHR_ARMS_W, font_size=4.5, color=C_CHRIST)

# Christ: LEGS
fill_rect(crx, C_LEG_L, C_LEG_T, C_LEG_R - C_LEG_L, C_LEG_B - C_LEG_T,
          CHR_LEGS_W, font_size=4.5, color=C_CHRIST)

dwg.add(crx)

# ============================================================
# ARCHITECTURAL OUTLINES — gold lines over everything
# ============================================================
arch = dwg.g(id='outlines', stroke=GOLD, stroke_width=0.8,
             fill='none', opacity='0.55')

# Cathedral walls
arch.add(dwg.rect((CAT_L, CAT_TOP),
                  (CAT_R - CAT_L, CAT_BOT - CAT_TOP)))

# Spire left (triangle)
scl_cx = (SPL[0] + SPL[1]) // 2
arch.add(dwg.polygon(points=[
    (SPL[0], SPL[3]), (SPL[1], SPL[3]),
    (SPL[1], SPL[2] + 40), (scl_cx, SPL[2]),
    (SPL[0], SPL[2] + 40),
]))
scr_cx = (SPR[0] + SPR[1]) // 2
arch.add(dwg.polygon(points=[
    (SPR[0], SPR[3]), (SPR[1], SPR[3]),
    (SPR[1], SPR[2] + 40), (scr_cx, SPR[2]),
    (SPR[0], SPR[2] + 40),
]))

# Triforium lines
arch.add(dwg.line((TRI_L, TRI_TOP), (TRI_R, TRI_TOP)))
arch.add(dwg.line((TRI_L, TRI_BOT), (TRI_R, TRI_BOT)))

# Altar
arch.add(dwg.rect((ALT_L, ALT_TOP),
                  (ALT_R - ALT_L, ALT_BOT - ALT_TOP),
                  stroke_width=1.2))

# Foundation step lines (3 steps)
for s in range(3):
    sy = FND_TOP + s * ((FND_BOT - FND_TOP) // 3)
    sx = CAT_L - s * 20
    sw = (CAT_R - CAT_L) + s * 40
    arch.add(dwg.line((sx, sy), (sx + sw, sy)))

# Pillar outlines
for px in PIL_XC:
    arch.add(dwg.rect((px, PIL_TOP), (PIL_W, PIL_BOT - PIL_TOP)))

# Transept outlines
tl, tr, tt, tb = TRN_L
arch.add(dwg.rect((tl, tt), (tr - tl, tb - tt)))
arch.add(dwg.rect((TRN_R[0], TRN_R[2]),
                  (TRN_R[1] - TRN_R[0], TRN_R[3] - TRN_R[2])))

# Rose window
arch.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R,
                    stroke_width=1.5))
arch.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R * 0.62))
arch.add(dwg.circle(center=(RW_CX, RW_CY), r=RW_R * 0.3))

# Crucifix cross outline
arch.add(dwg.rect(
    (CRX_CX - CRX_VW // 2 - 1, CRX_TOP - 1),
    (CRX_VW + 2, CRX_BOT - CRX_TOP + 2),
    stroke=GOLD, stroke_width=1.2,
))
arch.add(dwg.rect(
    (CRX_BL - 1, CRX_BY - 1),
    (CRX_BR - CRX_BL + 2, CRX_BH + 2),
    stroke=GOLD, stroke_width=1.2,
))

dwg.add(arch)

# ============================================================
# PILLAR LABELS (small, at top of each pillar)
# ============================================================
lbl = dwg.g(id='pillar_labels')
for i, px in enumerate(PIL_XC):
    lbl.add(dwg.text(
        pil_labels[i],
        insert=(px + PIL_W / 2, PIL_TOP - 6),
        text_anchor='middle', font_size='5.5px',
        font_family='Georgia, serif',
        fill=pil_colors[i], font_weight='bold', letter_spacing='0.5',
    ))
dwg.add(lbl)

# ============================================================
# SAVE
# ============================================================
dwg.save()
print(f'\n✓ Cathedral SVG saved to:\n  {OUTPUT}\n')
print('Convert to PNG with:')
print(f'  rsvg-convert -w 1200 -h 1800 {OUTPUT} -o {OUTPUT.replace(".svg", ".png")}')
print('  OR')
print(f'  inkscape --export-png={OUTPUT.replace(".svg", ".png")} --export-width=1200 {OUTPUT}')
