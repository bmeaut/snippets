import json, math
G = json.load(open('data_raw/export.geojson'))['features']
def rings(g):
    t, c = g['type'], g['coordinates']
    return [c[0]] if t == 'Polygon' else [p[0] for p in c] if t == 'MultiPolygon' else []
def lines(g):
    t, c = g['type'], g['coordinates']
    return [c] if t == 'LineString' else c if t == 'MultiLineString' else []
def pip(pt, ring):
    x, y = pt; ins = False
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-15) + x1: ins = not ins
    return ins
B = next(f for f in G if f['properties'].get('boundary') and f['properties'].get('name') == 'Biatorbágy' and f['properties'].get('admin_level') == '8')
BR = rings(B['geometry'])[0]
def dp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + b[0] * a[1] - b[1] * a[0]) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [a, b]
def dpr(ring, eps):
    # closed ring: split at the vertex farthest from the first one, simplify both halves
    if len(ring) < 4: return ring
    a = ring[0]
    i = max(range(len(ring)), key=lambda k: (ring[k][0]-a[0])**2 + (ring[k][1]-a[1])**2)
    return dp(ring[:i+1], eps)[:-1] + dp(ring[i:], eps)
R = lambda pts: [[round(x, 5), round(y, 5)] for x, y in pts]
rows = [dict(kind='boundary', name='Biatorbágy', cls='', coords=R(dpr(BR, 0.00008)))]
MAJOR = {'primary', 'secondary', 'tertiary', 'trunk'}
seen = 0
for f in G:
    p = f['properties']; g = f['geometry']
    kind = None
    if p.get('highway') and g['type'] in ('LineString', 'MultiLineString') and p['highway'] not in ('bus_stop', 'platform'):
        kind = 'street'
    elif p.get('railway') == 'rail' and 'route' not in p: kind = 'rail'
    elif p.get('waterway') in ('stream', 'river'): kind = 'water'
    if not kind: continue
    for l in lines(g):
        if not any(pip(pt, BR) for pt in l[::max(1, len(l) // 8)] + [l[-1]]): continue
        cls = 'major' if p.get('highway') in MAJOR else ('track' if p.get('highway') in ('track', 'path', 'footway', 'cycleway') else 'minor')
        rows.append(dict(kind=kind, name=p.get('name') or '', cls=cls if kind == 'street' else '', coords=R(dp(l, 0.00004))))
areas = json.load(open('work/area_geoms.json'))
for a in areas: rows.append(dict(kind='area', name=a['name'], cls='', coords=R(dpr(a['coords'], 0.00008))))
for r in rows: r['coords'] = ';'.join(f'{x},{y}' for x, y in r['coords'])
json.dump(rows, open('out/basemap.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import collections, os
print(collections.Counter(r['kind'] for r in rows), sum(len(r['coords']) for r in rows), os.path.getsize('out/basemap.json'))
