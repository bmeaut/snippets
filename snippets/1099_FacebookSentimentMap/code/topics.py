import re
# Keyword stems (lowercase, prefix match on word starts) for local-community topics in Biatorbágy group
TOPICS = {
    'Közlekedés, utak, parkolás': ['közleked', 'forgalom', 'forgalm', 'autópály', 'm1', 'm0', 'felhajt', 'lehajt', 'körforgal', 'dugó', 'dugóban',
                                   'parkol', 'járd', 'útépít', 'kátyú', 'busz', 'viabusz', 'volán', 'vonat', 'máv', 'kamion', 'sebess', 'lámpa',
                                   'jelzőlámp', 'átjáró', 'felüljár', 'kerékpár', 'bicikl', 'gyalog', 'zebra', 'traffipax', 'útlezár', 'terel'],
    'Baleset, bűn, biztonság': ['baleset', 'ellop', 'lopás', 'lopt', 'betör', 'tolvaj', 'rendőr', 'csaló', 'csalás', 'átver', 'elüt', 'gázol', 'cserbenhagy',
                                'bűnmegelőz', 'kamera', 'gyanús', 'vandál', 'rongál', 'lövöld', 'tűz', 'tűzolt', 'mentő'],
    'Önkormányzat, városvezetés, politika': ['önkormányz', 'polgármest', 'képviselő', 'testület', 'hivatal', 'város vezet', 'városvezet', 'kocsis',
                                             'választás', 'választási', 'választók', 'választókerület', 'szavaz', 'kampány', 'fidesz', 'tisza', 'kormány', 'párt', 'fórum', 'rendelet',
                                             'jegyző', 'főépítész', 'szabályozási', 'rendezési terv', 'külterület', 'adó'],
    'Környezet, zöld, állatok': ['fa', 'fák', 'fát', 'kivág', 'erdő', 'park', 'zöld', 'szemét', 'hulladék', 'lerakó', 'szúnyog', 'kutya', 'cica',
                                 'macska', 'róka', 'őz', 'vad', 'vaddisznó', 'madár', 'fecske', 'gólya', 'sün', 'állat', 'patak', 'forrás', 'szárazs',
                                 'azbeszt', 'por', 'bűz', 'szag', 'égetés', 'zaj', 'tűzijáték', 'locsol', 'kert'],
    'Közszolgáltatás, infrastruktúra': ['áram', 'áramszünet', 'eon', 'víz', 'vízm', 'csatorn', 'csőtörés', 'közvilágít', 'szemétszáll', 'kuka',
                                        'szelektív', 'internet', 'posta', 'orvos', 'egészségház', 'rendelő', 'háziorvos', 'óvod', 'iskol', 'bölcső', 'játszótér'],
    'Kultúra, programok, közösség': ['program', 'fesztivál', 'koncert', 'kiállít', 'előadás', 'színház', 'jfmk', 'művelődési', 'könyvtár', 'táncház',
                                     'városünnep', 'ünnep', 'szüret', 'vásár', 'piac', 'túra', 'futás', 'verseny', 'gyereknap', 'tábor', 'mozi',
                                     'adomány', 'jótékony', 'önkéntes'],
    'Hirdetés, szolgáltatás, állás': ['eladó', 'kiadó', 'vállal', 'szolgáltat', 'keresünk', 'munkatárs', 'állás', 'jelentkez', 'akció', 'kedvezmény',
                                      'rendelj', 'nyitva', 'ajánlat', 'ár', 'ft', 'forint', 'webshop', 'ingyen elvihető', 'albérlet', 'bérel',
                                      'keresek', 'ajánl'],
    'Elveszett / talált': ['elveszett', 'elveszet', 'elhagyt', 'talált', 'gazdi', 'eltűnt', 'szökött', 'megkerült', 'meglett'],
}
_compiled = {k: re.compile(r'(?<![a-záéíóöőúüű])(' + '|'.join(re.escape(w) for w in v) + ')', re.I) for k, v in TOPICS.items()}
# short tokens need whole-word-ish matching to avoid noise
SHORT_EXACT = {'fa', 'fák', 'fát', 'őz', 'vad', 'vaddisznó', 'por', 'ár', 'ft', 'm1', 'm0', 'víz', 'adó', 'eon', 'tűz', 'park', 'párt'}

def tag(text):
    t = (text or '').lower()
    out = []
    for k, rx in _compiled.items():
        hit = False
        for mo in rx.finditer(t):
            w = mo.group(1)
            if w in SHORT_EXACT:
                end = mo.end()
                nxt = t[end:end + 3]
                if re.match(r'[a-záéíóöőúüű]', nxt or ' ') and not re.match(r'(ak|at|ot|ban|ben|nál|nél|ról|ről|ra|re|on|en|ön|ja|je|t|k|i|ért|val|vel)\b', nxt + ' '):
                    continue
            hit = True; break
        if hit:
            out.append(k)
    return out
