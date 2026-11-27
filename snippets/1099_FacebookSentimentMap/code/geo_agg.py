import sys, json, re, collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import pandas as pd, numpy as np
from issue_texts import TEXTS, EXCLUDE

W = 'work'; O = 'out'
u = pd.read_pickle(f'{W}/geo_scored.pkl')
gaz = {p['pid']: p for p in json.load(open(f'{W}/gazetteer.json'))}
KEEP = set(TEXTS) - EXCLUDE
u['eff_issues'] = u.eff_issues.apply(lambda z: [i for i in z if i in KEEP])
prob = u[u.eff_issues.str.len() > 0]
print('problem items', len(prob), 'with place', (prob.eff_places.str.len() > 0).sum(),
      'share', round((prob.eff_places.str.len() > 0).mean() * 100, 1))
def red(s): return re.sub(r'\+?\d[\d \-/]{6,}\d', '[tel.]', s)

posts = u[u.kind == 'post'].set_index('post_id')
rows, pi = [], []
for pid, g in prob.explode('eff_places').dropna(subset=['eff_places']).groupby('eff_places'):
    pl = gaz[pid]
    n = len(g); neg = round((g.label == 'neg').mean() * 100, 1)
    cnt = collections.Counter(i for z in g.eff_issues for i in z)
    # example: the most-commented post among the place's problem posts (or parent post of its comments)
    cand = set(g.post_id)
    cp = posts.loc[[c for c in cand if c in posts.index]]
    cp = cp[cp.places.apply(lambda z: pid in z)] if len(cp[cp.places.apply(lambda z: pid in z)]) else cp
    ex = cp.sort_values('comments', ascending=False).iloc[0] if len(cp) else None
    s = re.sub(r'\s+', ' ', ex.clean) if ex is not None else ''
    rows.append(dict(pid=pid, name=pl['name'], kind=pl['kind'], lon=round(pl['lon'], 5), lat=round(pl['lat'], 5), n=n, neg=neg,
                     top_issue=cnt.most_common(1)[0][0], top_issues='; '.join(f'{TEXTS[i]["title"].split(":")[0]} ({c})' for i, c in cnt.most_common(3)),
                     example_date=str(ex.ts.date()) if ex is not None else '', example_comments=int(ex.comments) if ex is not None else 0,
                     example_text=red(s[:150] + ('…' if len(s) > 150 else ''))))
    for i, c in cnt.items():
        gi = g[g.eff_issues.apply(lambda z: i in z)]
        pi.append(dict(pid=pid, issue=i, n=int(c), neg=round((gi.label == 'neg').mean() * 100, 1)))
places = pd.DataFrame(rows).sort_values('n', ascending=False)
print(len(places)); print(places.head(25)[['name', 'n', 'neg', 'top_issues']].to_string())
json.dump(places.to_dict('records'), open(f'{O}/places.json', 'w'), ensure_ascii=False)
json.dump(pi, open(f'{O}/place_issues.json', 'w'), ensure_ascii=False)

# unplaced named spots
un = []
for name in ['M1 felhajtó / autópálya', 'Hulladéklerakó a pátyi határon', '„A lakópark” (nincs megnevezve)']:
    g = prob[prob.unplaced.apply(lambda z: name in z)]
    cnt = collections.Counter(i for z in g.eff_issues for i in z)
    un.append(dict(name=name, n=len(g), neg=round((g.label == 'neg').mean() * 100, 1),
                   top_issues='; '.join(f'{TEXTS[i]["title"].split(":")[0]} ({c})' for i, c in cnt.most_common(3))))
print(un)
json.dump(un, open(f'{O}/unplaced.json', 'w'), ensure_ascii=False)
json.dump(dict(problem_items=len(prob), placed=int((prob.eff_places.str.len() > 0).sum())), open(f'{W}/geo_cov.json', 'w'))

