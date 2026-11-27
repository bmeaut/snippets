"""Gazetteer from the user's Overpass GeoJSON export + place matching in posts/comments."""
import sys, json, re, math, collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import pandas as pd, numpy as np

G = json.load(open('data_raw/export.geojson'))
F = G['features']

# ---------- geometry helpers ----------
def rings(geom):
    t, c = geom['type'], geom['coordinates']
    if t == 'Polygon': return [c[0]]
    if t == 'MultiPolygon': return [p[0] for p in c]
    return []

def lines(geom):
    t, c = geom['type'], geom['coordinates']
    if t == 'LineString': return [c]
    if t == 'MultiLineString': return c
    if t == 'Polygon': return [c[0]]
    if t == 'MultiPolygon': return [p[0] for p in c]
    if t == 'Point': return [[c]]
    return []

def pip(pt, ring):
    x, y = pt; inside = False; n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-15) + x1:
            inside = not inside
    return inside

boundary = next(f for f in F if f['properties'].get('boundary') and f['properties'].get('name') == 'Biatorbágy' and f['properties'].get('admin_level') == '8')
BR = rings(boundary['geometry'])[0]
bx = [p[0] for p in BR]; by = [p[1] for p in BR]
BBOX = (min(bx) - .01, min(by) - .01, max(bx) + .01, max(by) + .01)

def in_town(geom, margin=True):
    pts = [p for l in lines(geom) for p in l]
    if not pts: return False
    inside = sum(pip(p, BR) for p in pts[:: max(1, len(pts) // 20)])
    return inside > 0

def rep_point(geom):
    pts = [p for l in lines(geom) for p in l]
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    if geom['type'] in ('Polygon', 'MultiPolygon'):
        return [cx, cy]
    return min(pts, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)

# ---------- streets ----------
streets = collections.defaultdict(list)
for f in F:
    p = f['properties']
    if p.get('highway') and p.get('name') and f['geometry']['type'] in ('LineString', 'MultiLineString') and p['highway'] != 'bus_stop':
        if in_town(f['geometry']):
            streets[p['name']].extend(lines(f['geometry']))

TYPES = {
    'utca': r'(?:utc[a-záéíóöőúüű]*|u\.)', 'út': r'(?:út(?:on|ra|ról|tól|ig|nál|nak|ba|ban|at|ja|ját|i|on)?|utat|útj[a-záéíóöőúüű]*)',
    'útja': r'(?:útj[a-záéíóöőúüű]*)', 'tér': r'(?:t[eé]r[a-záéíóöőúüű]*)', 'köz': r'(?:köz(?:ben|re|ből|nél|ön|be|t)?)(?![a-záéíóöőúüű])',
    'sétány': r'(?:sétány[a-záéíóöőúüű]*)', 'sor': r'(?:sor(?:on|ra|ról|nál)?)(?![a-záéíóöőúüű])', 'dűlő': r'(?:dűlő[a-záéíóöőúüű]*)',
    'lejtő': r'(?:lejtő[a-záéíóöőúüű]*)', 'park': r'(?:park[a-záéíóöőúüű]*)', 'körút': r'(?:körút[a-záéíóöőúüű]*)',
}
places = []  # dict(pid, name, kind, pattern, geom_lines, lon, lat)
first_tokens = collections.Counter()
for name in streets:
    parts = name.split(' ')
    if len(parts) >= 3: first_tokens[(parts[0], parts[-1])] += 1
for name, ls in streets.items():
    parts = name.split(' ')
    typ = parts[-1]
    if typ not in TYPES or len(parts) < 2:
        continue
    stem = ' '.join(parts[:-1])
    pats = [re.escape(stem) + r'\s+' + TYPES[typ]]
    # short alias: "Petőfi utca" for "Petőfi Sándor utca"
    if len(parts) == 3 and parts[0][0].isupper() and first_tokens[(parts[0], typ)] == 1 and len(parts[0]) >= 4 \
            and (parts[0] + ' ' + typ) not in streets \
            and not any((' ' + parts[0] + ' ' + typ) in (' ' + o) and o != name for o in streets):
        pats.append(re.escape(parts[0]) + r'\s+' + TYPES[typ])
    geom = {'type': 'MultiLineString', 'coordinates': ls}
    lon, lat = rep_point(geom)
    places.append(dict(pid='s:' + name, name=name, kind='utca', pats=pats, lon=lon, lat=lat))

# ---------- districts / localities / POIs ----------
def find_geom(pred):
    for f in F:
        if pred(f['properties']):
            return f['geometry']
    return None

AREAS = [
    ('Pecató', r'pecat[óo]', lambda p: p.get('name') == 'Pecató üdülőterület'),
    ('Katalin-hegy', r'katalin[\s-]?hegy', lambda p: p.get('name') == 'Katalinhegy üdülőterület'),
    ('Iharos', r'iharos', lambda p: p.get('name') == 'Iharos' and p.get('boundary')),
    ('Szarvasugrás', r'szarvasugr[áa]s', lambda p: p.get('name') == 'Szarvasugrás' and p.get('boundary')),
    ('Füzes', r'(?<![a-záéíóöőúüű])füzes(?!\s*-?\s*patak)(?![a-záéíóöőúüű]*patak)', lambda p: p.get('name') == 'Füzes' and p.get('boundary')),
    ('Ürgehegy', r'ürge[\s-]?hegy', lambda p: p.get('name') == 'Ürgehegy'),
    ('Szarvas-hegy', r'szarvas[\s-]?hegy', lambda p: p.get('name') == 'Szarvashegy'),
    ('Öreghegy', r'öreg[\s-]?hegy', lambda p: p.get('name') == 'Öreghegy'),
    ('Kutyahegy', r'kutya[\s-]?hegy', lambda p: p.get('name') == 'Kutyahegy'),
    ('Tópark', r'tópark', lambda p: p.get('name') == 'Tópark'),
    ('Viadukt lakópark', r'viadukt\s+lakópark', lambda p: p.get('name') == 'Viadukt lakópark'),
    ('Zöldsziget lakópark', r'zöldsziget', lambda p: p.get('name') == 'Zöldsziget lakópark'),
    ('Nyakas-kő', r'nyakas[\s-]?k[őö]', lambda p: p.get('name') == 'Nyakas-kő'),
    ('Kálvária-hegy', r'kálvária', lambda p: p.get('name') == 'Kálvária-hegy'),
    ('Rozália park', r'rozália\s*park', lambda p: p.get('name') == 'Rozália park'),
    ('Vasútállomás', r'(?<![a-záéíóöőúüű])(?:vasút)?állomás(?!\s+(?:bisztr|bistro|utc))(?!ról\s+indul)|pályaudvar', lambda p: p.get('name') == 'Biatorbágy, vasútállomás'),
    ('Viadukt', r'(?<![a-záéíóöőúüű])viadukt(?!\s+(?:lakópark|utc|center|medical|se\b|fitt))', lambda p: p.get('name') == 'Viadukt' and p.get('highway')),
    ('Penny (Torbágy)', r'penny', lambda p: p.get('name') == 'Penny'),
    ('BIT gimnázium', r'(?<![A-Za-z])BIT(?![A-Za-z])|innovatív technikum', lambda p: p.get('name') == 'Biatorbágyi Innovatív Technikum és Gimnázium'),
    ('Premier Outlet', r'outlet', lambda p: p.get('name') == 'Premier Outlet'),
    ('Serház', r'serház', lambda p: p.get('name') == 'Serház'),
]
area_geoms = []
for name, pat, pred in AREAS:
    g = find_geom(pred)
    if g is None:
        print('MISSING', name); continue
    lon, lat = rep_point(g)
    flags = 0 if name == 'BIT gimnázium' else re.I
    places.append(dict(pid='a:' + name, name=name, kind='terület' if g['type'] in ('Polygon', 'MultiPolygon') else 'hely',
                       pats=[pat], flags=flags, lon=lon, lat=lat))
    if g['type'] in ('Polygon', 'MultiPolygon'):
        area_geoms.append(dict(name=name, coords=[[round(x, 5), round(y, 5)] for x, y in rings(g)[0]]))

# Named places people mention but that are not on the export (shown beside the map)
UNPLACED = [
    ('M1 felhajtó / autópálya', r'felhajtó|lehajtó|\bm1\b|autópály'),
    ('Hulladéklerakó a pátyi határon', r'szeméttelep|hulladéklerakó|lerakó|rekortán|rekortan'),
    ('„A lakópark” (nincs megnevezve)', r'(?<![a-záéíóöőúüű])lakópark(?:ban|ból|ba|hoz|nál|ot|on|ra|ról|tól)?(?![a-záéíóöőúüű])'),
]

for pl in places:
    pl['rx'] = re.compile(r'(?<![A-Za-záéíóöőúüűÁÉÍÓÖŐÚÜŰ])(?:' + '|'.join(pl['pats']) + ')', pl.get('flags', re.I))
UNRX = [(n, re.compile(p, re.I)) for n, p in UNPLACED]

# ---------- match ----------
u = pd.read_pickle('work/issues_scored.pkl')
CAP = re.compile(r'([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+)\s+$')
BAD_STATION = re.compile(r'(kelenföld\w*|déli|keleti|nyugati|busz|autóbusz-?|töltő|vizsga|mérő|benzinkút)\s*-?$', re.I)
def ok(pl, t, m):
    pre = t[max(0, m.start() - 40):m.start()]
    if pl['kind'] == 'utca':
        c = CAP.search(pre)
        if c and not re.search(r'[.!?:\n]\s*\S+\s+$', pre[-len(c.group(0)) - 3:]) and len(pre) > len(c.group(0)):
            full = c.group(1) + ' ' + pl['name']
            if full not in STREETNAMES:
                return False
    if pl['pid'] == 'a:Vasútállomás' and BAD_STATION.search(pre[-25:] + ''):
        return False
    return True
STREETNAMES = set(streets)
def find(text):
    t = text or ''
    hits = [pl['pid'] for pl in places if any(ok(pl, t, m) for m in pl['rx'].finditer(t))]
    # a street hit that is fully contained in a longer street hit (e.g. "Szabadság út" vs "Szabadság utca") is fine; keep all
    return hits
u['places'] = [find(t) for t in u.clean]
u['unplaced'] = [[n for n, rx in UNRX if rx.search(t or '')] for t in u.clean]
post_places = u[u.kind == 'post'].set_index('post_id').places
post_issues = u[u.kind == 'post'].set_index('post_id').issues
u['eff_places'] = [p if (p or k == 'post') else (post_places.get(pid, []) if len(post_places.get(pid, [])) <= 2 else []) for p, k, pid in zip(u.places, u.kind, u.post_id)]
u['eff_issues'] = [sorted(set(i) | (set(post_issues.get(pid, [])) if k == 'comment' else set())) for i, k, pid in zip(u.issues, u.kind, u.post_id)]
u.to_pickle('work/geo_scored.pkl')
json.dump([{k: v for k, v in pl.items() if k in ('pid', 'name', 'kind', 'lon', 'lat')} for pl in places], open('work/gazetteer.json', 'w'), ensure_ascii=False)
json.dump(area_geoms, open('work/area_geoms.json', 'w'), ensure_ascii=False)

own = u[u.places.str.len() > 0]
print('places in gazetteer', len(places), 'streets', sum(1 for p in places if p['kind'] == 'utca'))
print('items with own place', len(own), 'with effective place', (u.eff_places.str.len() > 0).sum(), 'of', len(u))
c = collections.Counter(p for ps in u.places for p in ps)
print(c.most_common(40))
cu = collections.Counter(n for ns in u.unplaced for n in ns); print(cu)
