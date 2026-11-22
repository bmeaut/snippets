"""A dashboard adatfájljai a kézi címkékből és a kódkönyvből.

Használat:
    python code/build_dashboard_data.py <kódkönyv> <egységek.json> <címkék.txt> <kimeneti_mappa>

    <kódkönyv>      a kódkönyv-modul neve, pl. codebook_example
    <egységek.json> a make_units.py kimenete (units.json), VAGY a publikált
                    korábban előállított units_labeled.json – ebben benne vannak az
                    időpontok, így a teljes adatcsomag a nyers átirat nélkül is
                    újraszámolható
    <címkék.txt>    soronként: azonosító hangulat szerep problémák helyek
                    hangulat: n / 0 / p; szerep: m (moderátor és tervezőcsapat),
                    p (résztvevő), x (vegyes); problémák és helyek vesszővel, vagy -

A kimenet csak összesített adatokat és az egységenkénti címkéket tartalmazza,
szöveget nem.
"""
import collections
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
cb = importlib.import_module(sys.argv[1])
units_path, labels_path, out = sys.argv[2:5]
os.makedirs(out, exist_ok=True)

raw = json.load(open(units_path))
units = [dict(id=u['id'], start=float(u.get('start_s', u.get('start'))), end=float(u.get('end_s', u.get('end')))) for u in raw]
labels = {}
for line in open(labels_path):
    i, s, r, iss, pl = line.split()
    labels[int(i)] = dict(s=s, r=r, iss=[] if iss == '-' else iss.split(','), pl=[] if pl == '-' else pl.split(','))
assert len(labels) == len(units), 'minden egységnek kell címke'
for u in units:
    u.update(labels[u['id']])
    u['dur'] = u['end'] - u['start']
    for k in u['iss']:
        assert k in cb.ISSUES, k
    for p in u['pl']:
        assert p in cb.PLACES, p

SENT = {'n': 'neg', '0': 'neu', 'p': 'pos'}
ROLE = {'m': 'Moderátor és tervezőcsapat', 'p': cb.ROLE_P, 'x': 'Vegyes (párbeszéd)'}
N_BLOCKS = (cb.DURATION_MIN + 9) // 10


def dump(name, obj):
    json.dump(obj, open(os.path.join(out, name + '.json'), 'w'), ensure_ascii=False, indent=0)


def pct(a, b):
    return round(a / b * 1000) / 10 if b else 0


def mmss(s):
    s = int(s)
    return f'{s // 60}:{s % 60:02d}'


def counts(us):
    return collections.Counter(SENT[u['s']] for u in us)


overall = []
for r in ['p', 'm', 'x']:
    us = [u for u in units if u['r'] == r]
    c = counts(us)
    overall.append(dict(role=r, role_hu=ROLE[r], n=len(us), minutes=round(sum(u['dur'] for u in us) / 60, 1),
                        neg=c['neg'], neu=c['neu'], pos=c['pos']))
dump('overall', overall)

timeline = []
for b in range(N_BLOCKS):
    for r in ['all', 'p', 'm']:
        us = [u for u in units if b * 600 <= u['start'] < (b + 1) * 600 and (r == 'all' or u['r'] == r)]
        c, n = counts(us), len(us)
        timeline.append(dict(block=b, label=f'{b * 10}–{min(b * 10 + 10, cb.DURATION_MIN)}. perc', start_min=b * 10, role=r, n=n,
                             neg=pct(c['neg'], n), neu=pct(c['neu'], n), pos=pct(c['pos'], n)))
dump('timeline', timeline)

issues, issue_time = [], []
for k, d in cb.ISSUES.items():
    us = [u for u in units if k in u['iss']]
    n, c = len(us), counts(us)
    pc = collections.Counter(p for u in us for p in u['pl'])
    blocks = collections.Counter(int(u['start'] // 600) for u in us)
    peak = max(blocks, key=blocks.get)
    issues.append(dict(id=k, group=d['group'], group_hu=d['group_hu'], title=d['title'], statement=d['statement'], asks=d['asks'],
                       places=', '.join(cb.PLACES[p]['name'] for p, _ in pc.most_common(4)) or '–',
                       mentions=n, neg=pct(c['neg'], n), pos=pct(c['pos'], n),
                       part_share=pct(sum(1 for u in us if u['r'] == 'p'), n),
                       minutes=round(sum(u['dur'] for u in us) / 60, 1),
                       first_min=int(min(u['start'] for u in us) // 60), peak_block=f'{peak * 10}–{peak * 10 + 10}. perc'))
    for b in range(N_BLOCKS):
        issue_time.append(dict(id=k, block=b, mentions=blocks.get(b, 0)))
issues.sort(key=lambda r: -r['mentions'])
dump('issues', issues)
dump('issue_time', issue_time)

groups = []
for g, ghu in cb.GROUP_HU.items():
    us = [u for u in units if any(cb.ISSUES[k]['group'] == g for k in u['iss'])]
    c, n = counts(us), len(us)
    groups.append(dict(group=g, group_hu=ghu, mentions=n, neg=pct(c['neg'], n), neu=pct(c['neu'], n), pos=pct(c['pos'], n)))
dump('issue_groups', groups)

places, place_issues = [], []
for code, p in cb.PLACES.items():
    us = [u for u in units if code in u['pl']]
    if not us:
        continue
    c = counts(us)
    ic = collections.Counter(i for u in us for i in u['iss'])
    places.append(dict(pid=code, name=p['name'], kind=p['kind'], lon=p['lon'], lat=p['lat'], n=len(us), neg=pct(c['neg'], len(us)),
                       top_issues='; '.join(f"{cb.ISSUES[i]['title']} ({v})" for i, v in ic.most_common(3)) or '–',
                       first_time=mmss(min(u['start'] for u in us))))
    for i, v in ic.items():
        ni = sum(1 for u in us if i in u['iss'] and u['s'] == 'n')
        place_issues.append(dict(pid=code, issue=i, n=v, neg=pct(ni, v)))
places.sort(key=lambda r: -r['n'])
dump('places', places)
dump('place_issues', place_issues)

sections = []
for a, b, t in cb.SECTIONS:
    us = [u for u in units if a * 60 <= u['start'] < b * 60]
    c, n = counts(us), len(us)
    ic = collections.Counter(i for u in us for i in u['iss'])
    sections.append(dict(sec=f'{a}–{b}', title=t, n=n, part=pct(sum(1 for u in us if u['r'] == 'p'), n),
                         neg=pct(c['neg'], n), pos=pct(c['pos'], n),
                         top=', '.join(cb.ISSUES[i]['title'] for i, _ in ic.most_common(2))))
dump('sections', sections)

dump('units_labeled', [dict(id=u['id'], start=mmss(u['start']), start_s=round(u['start'], 1), end_s=round(u['end'], 1),
                            role=u['r'], sentiment=SENT[u['s']], issues=';'.join(u['iss']), places=';'.join(u['pl'])) for u in units])
p = next(r for r in overall if r['role'] == 'p')
print(f"{cb.TITLE}: {len(units)} egység; résztvevők: {pct(p['neg'], p['n'])}% negatív, {pct(p['pos'], p['n'])}% pozitív")
