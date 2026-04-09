"""Maintainers and prominent contributors: GitHub usernames and Zulip user IDs."""

# Mathlib maintainers: name -> GitHub username
MAINTAINERS = {
    "Adam Topaz": "adamtopaz",
    "Anatole Dedecker": "ADedecker",
    "Anne Baanen": "Vierkantor",
    "Bhavik Mehta": "b-mehta",
    "Bryan Gin-ge Chen": "bryangingechen",
    "Damiano Testa": "adomani",
    "Eric Wieser": "eric-wieser",
    "Filippo A. E. Nuccio": "faenuccio",
    "Floris van Doorn": "fpvandoorn",
    "Frédéric Dupuis": "dupuisf",
    "Heather Macbeth": "hrmacbeth",
    "Jireh Loreaux": "j-loreaux",
    "Johan Commelin": "jcommelin",
    "Joël Riou": "joelriou",
    "Kevin Buzzard": "kbuzzard",
    "Kim Morrison": "kim-em",
    "Kyle Miller": "kmill",
    "Mario Carneiro": "digama0",
    "Markus Himmel": "TwoFX",
    "Matthew Robert Ballard": "mattrobball",
    "Michael Rothgang": "grunweg",
    "Oliver Nash": "ocfnash",
    "Patrick Massot": "PatrickMassot",
    "Riccardo Brasca": "riccardobrasca",
    "Robert Y. Lewis": "robertylewis",
    "Rémy Degenne": "RemyDegenne",
    "Sébastien Gouëzel": "sgouezel",
    "Yury G. Kudryashov": "urkud",
}

# Prominent non-maintainer contributors: top 20 by review comment count.
PROMINENT_CONTRIBUTORS = {
    "Yaël Dillies": "YaelDillies",           # 8377 reviews
    "Andrew Yang": "erdOne",                    # 3314 reviews
    "Christian Merten": "chrisflav",          # 2371 reviews
    "Violeta Hernández": "vihdzp",            # 2124 reviews
    "Robin Carlier": "robin-carlier",         # 2117 reviews
    "Etienne Marion": "EtienneC30",           # 1948 reviews
    "Junyan Xu": "alreadydone",               # 1813 reviews
    "Thomas Browning": "tb65536",             # 1532 reviews
    "Monica Omar": "themathqueen",            # 1500 reviews
    "David Loeffler": "loefflerd",            # 1495 reviews
    "Kenny Lau": "kckennylau",               # 1482 reviews
    "Ruben Van de Velde": "Ruben-VandeVelde", # 1389 reviews
    "Jovan Gerbscheid": "JovanGerb",          # 1118 reviews
    "Antoine Chambert-Loir": "AntoineChambert-Loir",  # 1043 reviews
    "Michael Stoll": "MichaelStollBayreuth",  # 1014 reviews
    "Snir Broshi": "SnirBroshi",              # 898 reviews
    "Dagur Asgeirsson": "dagurtomas",         # 887 reviews
    "Aaron Liu": "plp127",                    # 663 reviews
    "Stefan Kebekus": "kebekus",              # 575 reviews
    "Jon Eugster": "joneugster",              # 573 reviews
}

# All GitHub usernames we care about
ALL_GITHUB_USERNAMES = set(MAINTAINERS.values()) | set(PROMINENT_CONTRIBUTORS.values())

# Zulip user IDs for maintainers and prominent contributors.
# Some people have multiple accounts (e.g. bot accounts) — include all.
ZULIP_USER_IDS = {
    243562,   # Adam Topaz
    268315,   # Anatole Dedecker
    238446,   # Anne Baanen
    246273,   # Bhavik Mehta
    123965,   # Bryan Gin-ge Chen
    321459,   # Damiano Testa
    310045,   # Eric Wieser
    300245,   # Filippo A. E. Nuccio
    111080,   # Floris van Doorn
    311453,   # Frédéric Dupuis
    260507,   # Heather Macbeth
    197836,   # Jireh Loreaux
    112680,   # Johan Commelin
    459699,   # Joël Riou
    260921,   # Markus Himmel
    110038,   # Kevin Buzzard
    110087,   # Kim Morrison
    306601,   # Kyle Miller
    110049,   # Mario Carneiro
    306577,   # Matthew Ballard
    713393,   # Matthew Ballard (alt)
    634338,   # Michael Rothgang
    240862,   # Oliver Nash
    110031,   # Patrick Massot
    210574,   # Patrick Massot (alt)
    130384,   # Riccardo Brasca
    350992,   # Rémy Degenne
    110050,   # Sébastien Gouëzel
    1013125,  # Yury Kudryashov
    # Prominent contributors (top 20 by review comment count)
    387244,   # Yaël Dillies
    224323,   # Junyan Xu
    125393,   # Junyan Xu (inactive alt)
    703970,   # Etienne Marion
    253861,   # Thomas Browning
    477483,   # Monica Omar
    110064,   # Kenny Lau
    307953,   # Ruben Van de Velde
    479299,   # Jovan Gerbscheid
    933054,   # Snir Broshi
    519559,   # Dagur Asgeirsson
    816344,   # Aaron Liu
    679664,   # Stefan Kebekus
    286014,   # Robin Carlier
}

# Zulip display names -> for reference when filtering
ZULIP_NAMES = {
    # Maintainers
    "Adam Topaz", "Anatole Dedecker", "Anne Baanen", "Bhavik Mehta",
    "Bryan Gin-ge Chen", "Damiano Testa", "Eric Wieser",
    "Filippo A. E. Nuccio", "Floris van Doorn", "Frédéric Dupuis",
    "Heather Macbeth", "Jireh Loreaux", "Johan Commelin", "Joël Riou",
    "Kevin Buzzard", "Kim Morrison", "Kyle Miller", "Mario Carneiro",
    "Julia Markus Himmel", "Matthew Ballard", "Michael Rothgang",
    "Oliver Nash", "Patrick Massot", "Riccardo Brasca",
    "Robert Y. Lewis", "Rémy Degenne", "Sébastien Gouëzel",
    "Yury Kudryashov",
    # Prominent contributors
    "Yaël Dillies", "Junyan Xu", "Etienne Marion", "Thomas Browning",
    "Monica Omar", "Kenny Lau", "Ruben Van de Velde",
    "Jovan Gerbscheid", "Snir Broshi", "Dagur Asgeirsson",
    "Aaron Liu", "Stefan Kebekus", "Robin Carlier", "Jon Eugster",
}
