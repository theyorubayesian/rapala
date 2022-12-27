import calendar

AFRIQUE_MONTH_MAP = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12
}

AMHARIC_MONTH_MAP = {
    "ጃንዩወሪ": 1,
    "ፌብሩወሪ": 2,
    "ማርች": 3,
    "ኤፕሪል": 4,
    "ሜይ": 5,
    "ጁን": 6,
    "ጁላይ": 7,
    "ኦገስት": 8,
    "ሴፕቴምበር": 9,
    "ኦክቶበር": 10,
    "ኖቬምበር": 11,
    "ዲሴምበር": 12
}

BAMBARA_MONTH_MAP = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12
}

HAUSA_MONTH_MAP = {
    "janairu": 1,
    "fabrairu": 2,
    "maris": 3,
    "afrilu": 4,
    "mayu": 5,
    "yuni": 6,
    "yuli": 7,
    'agusta': 8,
    "satumba": 9,
    "oktoba": 10,
    "nuwamba": 11,
    "disamba": 12
}

KINYARWANDA_MONTH_MAP = {}

LINGALA_MONTH_MAP = AFRIQUE_MONTH_MAP

NDEBELE_MONTH_MAP = {
    "zibandlela": 1,
    "nhlolanja": 2,
    "mbimbitho": 3,
    "mabasa": 4,
    "nkwenkwezi": 5,
    "nhlangula": 6,
    "ntulikazi": 7,
    "ncwabakazi": 8,
    "mpandula": 9,
    "mfumfu": 10,
    "lwezi": 11,
    "mpalakazi": 12
}

OROMOO_MONTH_MAP = {
    "amajjii": 1,
    "guraandhalaa": 2,
    "bitootessa": 3,
    "ebla": 4,
    "caamsaa": 5,
    "waxabajjii": 6,
    "adoolessa": 7,
    "hagayya": 8,
    "fulbaana": 9,
    "onkoloolessa": 10,
    "sadaasaa": 11,
    "muddee": 12
}

SHONA_MONTH_MAP = {
    "ndira": 1,
    "kukadzi": 2,
    "kurume": 3,
    "kubvumbi": 4,
    "chivabvu": 5,
    "chikumi": 6,
    "chikunguru": 7,
    "nyamavhuvhu": 8,
    "gunyana": 9,
    "gumiguru": 10,
    "mbudzi": 11,
    "zvita": 12
}

SOMALIA_MONTH_MAP = {calendar.month_name[i].lower(): i for i in range(1, 13)}

SWAHILI_MONTH_MAP = {
    "januari": 1,
    "februari": 2,
    "machi": 3,
    "aprili": 4,
    "mei": 5,
    "juni": 6,
    "julai": 7,
    "agosti": 8,
    "septemba": 9,
    "oktoba": 10,
    "novemba": 11,
    "desemba": 12
}

TIGRINYA_MONTH_MAP = {
    "ጥሪ": 1,
    "ለካቲት": 2,
    "መጋቢት": 3,
    "ሚያዝያ": 4,
    "ግንቦት": 5,
    "ሰነ": 6,
    "ሓምለ": 7,
    "ነሓሰ": 8,
    "መስከረም": 9,
    "ጥቅምቲ": 10,
    "ሕዳር": 11,
    "ታሕሳስ": 12
}

MONTH_MAP = {
    "afr": AFRIQUE_MONTH_MAP,
    "amh": AMHARIC_MONTH_MAP,
    "bam": BAMBARA_MONTH_MAP,
    "hau": HAUSA_MONTH_MAP,
    "kin": KINYARWANDA_MONTH_MAP,
    "lin": LINGALA_MONTH_MAP,
    "nde": NDEBELE_MONTH_MAP,
    "orm": OROMOO_MONTH_MAP,
    "sna": SHONA_MONTH_MAP,
    "som": SOMALIA_MONTH_MAP,
    "swa": SWAHILI_MONTH_MAP,
    "tir": TIGRINYA_MONTH_MAP
}

URLS = {
    "afr": "https://www.voaafrique.com",
    "amh": "https://amharic.voanews.com",
    "orm": "https://www.voaafaanoromoo.com",
    "bam": "https://www.voabambara.com",
    "hau": "https://www.voahausa.com",
    "kin": "https://www.radiyoyacuvoa.com",
    "lin": "https://www.voalingala.com",
    "nde": "https://www.voandebele.com",
    "sna": "https://www.voashona.com",
    "som": "https://www.voasomali.com",
    "swa": "https://www.voaswahili.com",
    "tir": "https://tigrigna.voanews.com"
}
