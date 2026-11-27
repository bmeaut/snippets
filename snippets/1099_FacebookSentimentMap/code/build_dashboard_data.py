"""Build the anonymized JSON files the dashboard reads (no post texts, no names).

Inputs (from earlier steps): work/summary.json, work/issue_table.pkl, work/issue_monthly.pkl,
work/issues_scored.pkl, out/places.json, out/place_issues.json, out/unplaced.json, work/geo_cov.json.
Output: data/*.json
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from issue_texts import TEXTS, GROUPS, EXCLUDE

W, O, D = 'work', 'out', 'data'
os.makedirs(D, exist_ok=True)
def dump(name, obj):
    json.dump(obj, open(os.path.join(D, name + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))

d = json.load(open(f'{W}/summary.json'))
kindhu = {'post': 'Posztok', 'comment': 'Kommentek'}
dump('overall', [dict(kind=k, kind_hu=kindhu[k], **v, n=sum(v.values())) for k, v in d['overall'].items()])
dump('monthly', d['monthly'])
dump('topics', d['topics'])
lab = {'neg': 'Negatív', 'neu': 'Semleges', 'pos': 'Pozitív'}
dump('engagement', [dict(label=r['label'], label_hu=lab[r['label']], n=r['n'], reactions_mean=r['reactions_mean'],
                         reactions_median=r['reactions_median'], comments_mean=r['comments_mean'], shares_mean=r['shares_mean'])
                    for r in d['engagement']])
depth_hu = {'0': 'Fő komment', '1': 'Válasz', '2': 'Válasz a válaszra'}
dp = []
for k, v in d['by_depth'].items():
    n = sum(v.values())
    dp.append(dict(depth=k, depth_hu=depth_hu[k], **v, n=n, **{x + '_pct': round(v[x] / n * 100, 1) for x in ['neg', 'neu', 'pos']}))
dump('depth', dp)
ev = d['eval']
dump('validation', [dict(metric='cv_accuracy', value=round(ev['cv_acc'] * 100, 1)), dict(metric='cv_macro_f1', value=round(ev['cv_f1'] * 100, 1)),
                    dict(metric='n_labeled', value=ev['n']), dict(metric='acc_comments', value=round(ev['oof_acc_comment'] * 100, 1)),
                    dict(metric='acc_posts', value=round(ev['oof_acc_post'] * 100, 1)),
                    dict(metric='adj_comment_neg', value=round(d['overall_adjusted']['comment']['neg'] * 100, 1)),
                    dict(metric='adj_comment_pos', value=round(d['overall_adjusted']['comment']['pos'] * 100, 1))])

# problems: statistics + the summaries written by reading the threads (issue_texts.py); no post excerpts
t = pd.read_pickle(f'{W}/issue_table.pkl')
u = pd.read_pickle(f'{W}/issues_scored.pkl')
rows = []
for r in t.itertuples():
    if r.id in EXCLUDE:
        continue
    T = TEXTS[r.id]
    rows.append(dict(id=r.id, group=T['group'], group_hu=GROUPS[T['group']], title=T['title'], statement=T['statement'],
                     asks=T['asks'], places=T['places'], threads=int(r.threads), mentions=int(r.mentions), comments=int(r.comments),
                     thread_comments=int(r.thread_comments), neg=float(r.neg), reactions=int(r.reactions), peak_month=r.peak_month,
                     authors=int(r.authors)))
dump('issues', rows)
keep = {r['id'] for r in rows}
mon = pd.read_pickle(f'{W}/issue_monthly.pkl')
dump('issue_monthly', mon[mon.id.isin(keep)].to_dict('records'))
groups = []
for gid, gname in GROUPS.items():
    ids = [r['id'] for r in rows if r['group'] == gid]
    m = u[u.issues.apply(lambda z: any(i in z for i in ids))]
    groups.append(dict(group=gid, group_hu=gname, mentions=len(m), neg=round((m.label == 'neg').mean() * 100, 1),
                       threads=int((m.kind == 'post').sum()), issues=len(ids)))
dump('issue_groups', groups)

# biggest threads: statistics only, with a neutral topic written by hand instead of the post text
THREAD_TOPICS = {
    '2026-06-29': 'Rongálás: szétvágott szénabálák', '2026-07-15': 'M1-felhajtó: kamionos baleset és cserbenhagyás',
    '2026-11-13': 'Elhagyott rendszámtáblák az autópálya-felüljárónál', '2026-06-04': 'Fakivágás egy magántelken fészkelési időben',
    '2026-04-18': 'Közlekedési baleset; kikapcsolt hozzászólások a csoportban', '2026-03-24': 'Egyházi iskola építése közpénzből (megosztott cikk)',
    '2026-06-07': 'Elütött róka, gyorshajtás a Sóskút felé vezető úton', '2026-07-27': 'A külterületi rendezési terv bírálata',
    '2026-06-23': 'Gazdát kereső idős kutya – vita az örökbeadásról', '2026-07-08': 'Hajnali cölöpverés az M1-hídépítésnél',
    '2026-08-18': 'Éjszakai becsöngető ismeretlen', '2026-08-26': '„Biatorbágy 2051” – vita a város jövőjéről'}
th = []
for i, r in enumerate(d['threads_biggest']):
    th.append(dict(rank=i + 1, date=r['date'], topic=THREAD_TOPICS.get(r['date'], ''), n=r['n'], neg=r['neg'], pos=r['pos'],
                   neu=100 - r['neg'] - r['pos'], reactions=r['reactions']))
dump('threads', th)

# map layers
for name in ['place_issues', 'unplaced']:
    dump(name, json.load(open(f'{O}/{name}.json')))
places = json.load(open(f'{O}/places.json'))
for p in places:
    for k in ['example_text', 'example_date', 'example_comments']:
        p.pop(k, None)
dump('places', places)
dump('geo_coverage', [json.load(open(f'{W}/geo_cov.json'))])
dump('basemap', json.load(open(f'{O}/basemap.json')))
print('written to', D)
