"""Kódkönyv – KITALÁLT PÉLDA a formátum bemutatására.

A valódi kódkönyvet az átirat elolvasása után kell megírni: a témák, a
témakörök, az összefoglalók és a helyek a konzultáción elhangzottakból
következnek. A szkript nem generálja őket.
"""

TITLE = 'Példa konzultáció'
ROLE_P = 'Résztvevők'
DURATION_MIN = 20

GROUP_HU = {'kozl': 'Közlekedés', 'varos': 'Városszerkezet'}

ISSUES = {
    'dugo': {'group': 'kozl', 'group_hu': 'Közlekedés', 'title': 'Reggeli torlódás az iskolák körül',
             'statement': 'Kitalált összefoglaló: a résztvevők szerint reggelente beáll a forgalom.',
             'asks': 'Kitalált kérés: tehermentesítő útvonal.'},
    'fout': {'group': 'varos', 'group_hu': 'Városszerkezet', 'title': 'A főutca nem tölt be központi szerepet',
             'statement': 'Kitalált összefoglaló: az átmenő forgalom miatt nincs gyalogosforgalom.',
             'asks': 'Kitalált kérés: egységes utcakép, széles járda.'},
}

# kind: 'utca', 'terület' vagy 'hely'; koordináták WGS84-ben (fiktív értékek)
PLACES = {
    'fout': {'name': 'Fő utca', 'kind': 'utca', 'lon': 19.0, 'lat': 47.5},
    'iskola': {'name': 'Iskola tér', 'kind': 'hely', 'lon': 19.002, 'lat': 47.501},
}

# húszperces szakaszok: (kezdő perc, záró perc, fő témák)
SECTIONS = [(0, 20, 'Bemutatkozás és első hozzászólások')]
