"""Concrete-issue taxonomy for the Biatorbágy group. Stems match at word start (case-insensitive)."""
import re

ISSUES = [
    ('kozmu', 'Külterületek közműhiánya: ivóvíz, csatorna',
     ['re:csatornáz|csatornahálózat|csatornadíj|szennyvízcsatorn|csatorna nélkül|nincs csatorna|víz és csatorna|víz, csatorna|csatorna és víz|csatornára', 'ivóv', 'vezetékes v', 'vízvezeték', 'vízhálózat', 'közmű', 'közművesít', 'lajt', 'vízszállít', 'szennyvíz',
      'emésztő', 'szikkasztó', 'zárt tároló', 'szippant', 'kútvíz', 'fúrt kút', 'ásott kút']),
    ('terv', 'Külterületek, zártkertek jövője: rendezési terv, átminősítés',
     ['külterület', 'zártkert', 'zártkertes', 'művelés alól', 'művelés alóli', 'kivonás', 'rendezési terv', 'szabályozási terv', 'hész',
      'településrendez', 'telekspekul', 'átminősít', 'belterületbe von', 'belterületbe vonás', 'nemlakó', 'kertes mezőgazdasági',
      'mezőgazdasági terület', 'építési tilalom', 'telekalakít', 'telekméret', 'külterületi koncepció', 'szegregátum', 'tájbank', 'telekösszevon', 'szőlőhegy']),
    ('utak', 'Utak minősége: földutak, kátyúk, sár, por',
     ['kátyú', 'földút', 'földutak', 'sáros', 'sárban', 'murvá', 'aszfaltoz', 'aszfaltoz', 'útburkolat', 'szilárd burkolat',
      'útfelújít', 'úthiba', 'gödrös', 'porzik', 'porfelhő', 'útalap', 'zúzott kő', 'mart aszfalt', 'járhatatlan', 'kimosta']),
    ('jarda', 'Járdák, zebrák hiánya, gyalogosbiztonság',
     ['járda', 'zebra', 'gyalogátkel', 'gyalogos', 'gyalogút', 'babakocsi']),
    ('gyorshajtas', 'Gyorshajtás és agresszív vezetés',
     ['gyorshajt', 'száguld', 'sebességhatár', 'sebességmér', 'trafipax', 'traffipax', 'fekvőrendőr', 'versenypály', 'gyorsulás',
      'repesztenek', 'padlógáz', '30-as', '30 km', '50 km', 'tükörsima', 'cserbenhagy', 'elüt', 'elütött', 'gázolás']),
    ('forgalom', 'Torlódás, M1/M0 bővítés, csomópontok',
     ['dugó', 'dugóban', 'torlód', 'araszol', 'felhajtó', 'lehajtó', 'autópály', 'm1', 'm0', 'pátyi átjáró', 'átjáró', 'útlezár',
      'lezárás', 'terelés', 'jelzőlámp', 'körforgalom', 'kereszteződés', 'csomópont', 'kamion', 'átmenő forgalom']),
    ('tomeg', 'Tömegközlekedés: vonat, busz, menetrend',
     ['viabusz', 'volán', 'buszjárat', 'buszmegálló', 'menetrend', 'vonat', 'máv', 'vasútállomás', 're:állomás(?! bisztró)', 'késik', 'késés',
      'kanyargo', 'pótlóbusz']),
    ('parkolas', 'Parkolás, elállt kapubeállók, roncsautók',
     ['parkol', 'kapubeál', 'kocsibeál', 'kapuba áll', 'beállnak', 'roncs', 'veszteglő', 'bontódó', 'leparkol']),
    ('lerako', 'A Páty–Biatorbágy határi hulladéklerakó: tüzek, rekortán, azbeszt',
     ['szeméttelep', 'hulladéklerakó', 'lerakó', 'rekortán', 'rekortan', 'kátrány', 'pátyi vállalkozó', 'égő gumi', 'ég a gumi', 'azbeszt']),
    ('fust', 'Füst, égetés, bűz',
     ['füst', 'füstöl', 'égetés', 'éget', 'avarégetés', 'büdös', 'bűz', 'szaghatás', 'trágyaszag', 'vegyszer']),
    ('szemet', 'Szemétszállítás és illegális hulladék',
     ['szemétszáll', 'kuka', 'mohu', 'szelektív', 'kommunális', 'illegális szemét', 'illegális hulladék', 'szemetel', 'eldobál',
      'zöldhulladék', 'lomtalanít']),
    ('vad', 'Vaddisznók, vadkár, lövöldözés belterületen',
     ['vaddisznó', 'vadkan', 'vadkár', 'vadász', 'lövöld', 'lövés', 'lőnek', 'elejt', 'vadállomány', 'malacos']),
    ('szunyog', 'Szúnyoginvázió, szúnyogirtás',
     ['szúnyog', 'tigrisszúnyog', 'szúnyogirt']),
    ('zaj', 'Zaj: éjszakai építkezés, cölöpverés, tűzijáték',
     ['re:zaj(?!l)', 'cölöp', 'tűzijáték', 'petárd', 'csendrendelet', 'csend rendelet', 'éjszakai munka', 'kalapál', 'ágyú', 'motorzaj']),
    ('vilagitas', 'Közvilágítás hiánya, sötét játszóterek',
     ['közvilágít', 'utcai világítás', 'kivilágítás', 'nincs világítás', 'nincs lámpa', 'lámpa nem', 'nem ég a lámpa', 'nem világít', 'sötétben vannak', 'sötét van']),
    ('biztonsag', 'Lopások, betörések, közbiztonság',
     ['lop', 'ellop', 'elloptá', 'betör', 'tolvaj', 'feltört', 'feltör', 'bűnmegelőz', 'becsönget', 'becsenget', 'betörő']),
    ('zold', 'Fák, parkok, zöldfelületek kezelése',
     ['fakivág', 'kivágt', 'kivágá', 'favágás', 'tarra', 'kaszál', 'fűnyírás', 'zöldfelület', 'virágágy', 'faültet', 'fasor',
      'gyérít', 'invazív', 'patakpart', 'zöldterület']),
    ('szavazo', 'Szavazókörök összevonása, elérhetősége (2026. áprilisi választás)',
     ['szavazókör', 'szavazóhely', 'szavazóhelyiség', 'szavazóhelység', 'mozgóurna', 'mozgó urna', 'szavazópont', 'választókerület', 'szavazni menni', 'oviba szavaz', 'suliba szavaz']),
    ('egeszseg', 'Egészségügyi ellátás: orvosok, rendelők',
     ['háziorvos', 'gyerekorvos', 'gyermekorvos', 'fogorvos', 'iskolaorvos', 'orvosi rendel', 'orvoshoz', 'rendelő', 'egészségház', 'orvosi ügyelet', 'szakrendel', 'védőnő']),
    ('nyilvanossag', 'Helyi nyilvánosság: moderálás, törölt kommentek, helyi média',
     ['re:admin(?!iszt)', 'törölt', 'törlődnek', 'kikapcsolták a hozzászól', 'kikapcsoltak a hozzászól', 'moderál', 'cenzúr', 'helyi média',
      'körkép', 'hivatalos oldal']),
    ('jatszoter', 'Játszóterek, sportpályák állapota és nyitva tartása',
     ['játszótér', 'játszóter', 'sportpály', 'focipály', 'kosárpály', 'madaras játszó']),
    ('allat', 'Kóbor és veszélyes kutyák, állattartás',
     ['kóbor', 'kutyaharap', 'megharap', 'állattartási rendelet', 'ugatás', 'ugat', 'póráz', 'kutyaürülék', 'kutyaszar']),
    ('aram', 'Áramszünetek', ['áramszünet', 'nincs áram', 'áramkimaradás', 'eon']),
    ('vizellatas', 'Ivóvíz-ellátás belterületen: nyomás, minőség, tilalom, díj',
     ['víznyomás', 'vízhiány', 'locsolási tilalom', 'vízminőség', 'vízdíj', 'csőtörés', 'nincs víz', 'vízkorlátoz', 'vízmű', 'mellékmérő', 'almérő']),
]

def _rx(stems):
    parts = [s[3:] if s.startswith('re:') else re.escape(s) for s in sorted(stems, key=len, reverse=True)]
    return re.compile(r'(?<![0-9a-záéíóöőúüű])(' + '|'.join(parts) + ')', re.I)

RX = {k: _rx(v) for k, _, v in ISSUES}
NAMES = {k: n for k, n, _ in ISSUES}
SPECIAL = {
    'lop': re.compile(r'(?<![a-záéíóöőúüű])(lop(?:ás|ták|tak|ott|ni|nak|nák|ja|tam|kod)|ellop)', re.I),
    'éget': re.compile(r'(?<![a-záéíóöőúüű])(éget(?:nek|ett|i|ik|és|ni)|elégett)', re.I),
    'm1': re.compile(r'(?<![a-z0-9])(m1|m0)(?![0-9])', re.I),
}

def match(text):
    t = (text or '').lower()
    out = []
    for k, rx in RX.items():
        found = False
        for m in rx.finditer(t):
            w = m.group(1).lower()
            if w in ('lop',) and not SPECIAL['lop'].search(t):
                continue
            if w == 'éget' and not SPECIAL['éget'].search(t):
                continue
            if w in ('m1', 'm0') and not SPECIAL['m1'].search(t):
                continue
            if w == 'forrás' and not re.search(r'forrás(?!\s*u)', t):  # "Forrás utca" is a street name
                continue
            if w == 'átjáró' and 'gyalog' in t:
                continue
            found = True
            break
        if found:
            out.append(k)
    return out
