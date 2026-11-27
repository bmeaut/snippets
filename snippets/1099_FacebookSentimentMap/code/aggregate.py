import sys, json, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np, pandas as pd
W = 'work'
u = pd.read_pickle(f'{W}/scored.pkl')
ev = json.load(open(f'{W}/indomain_eval.json'))
raw = json.load(open('data_raw/posts.json'))
utype = {p['post_id']: p['user'].get('type') for p in raw}
u['author_type'] = u.post_id.map(utype).where(u.kind == 'post')
L = ['neg', 'neu', 'pos']
t = u[u.label.isin(L)].copy()

def dist(df):
    c = df.label.value_counts().reindex(L, fill_value=0)
    return {k: int(v) for k, v in c.items()}

# prevalence correction (adjusted classify-and-count) using OOF confusion matrix
cm = np.array(ev['cm'], float)
Pm = (cm / cm.sum(1, keepdims=True)).T  # P(pred | true): columns true
def adjust(d):
    obs = np.array([d[k] for k in L], float); obs /= obs.sum()
    from scipy.optimize import nnls
    x, _ = nnls(np.vstack([Pm, np.ones(3) * 10]), np.append(obs, 10))
    return dict(zip(L, (x / x.sum()).round(3).tolist()))

out = {}
out['eval'] = ev
out['counts'] = dict(posts=int((u.kind == 'post').sum()), comments=int((u.kind == 'comment').sum()),
                     posts_text=int(((u.kind == 'post') & u.label.isin(L)).sum()),
                     comments_text=int(((u.kind == 'comment') & u.label.isin(L)).sum()),
                     start=str(u.ts.min().date()), end=str(u.ts.max().date()),
                     posts_with_comments=int(u[u.kind == 'comment'].post_id.nunique()),
                     post_authors=int(u[u.kind == 'post'].author.nunique()),
                     comment_authors=int(u[u.kind == 'comment'].author.nunique()))
out['overall'] = {k: dist(t[t.kind == k]) for k in ['post', 'comment']}
out['overall_adjusted'] = {k: adjust(out['overall'][k]) for k in ['post', 'comment']}
print(json.dumps(out['overall'], indent=0), out['overall_adjusted'])
print(u[u.kind == 'post'].author_type.value_counts())
out['by_author_type'] = {str(k): dist(g) for k, g in t[t.kind == 'post'].groupby('author_type')}

# monthly
mo = []
for (mth, k), g in t.groupby(['month', 'kind']):
    d = dist(g); n = sum(d.values())
    mo.append(dict(month=mth, kind=k, n=n, **{x: round(d[x] / n * 100, 1) for x in L}, net=round((d['pos'] - d['neg']) / n * 100, 1)))
out['monthly'] = mo
print(pd.DataFrame(mo).pivot(index='month', columns='kind', values=['n', 'neg', 'pos']))

# topics (thread-level for comments)
tp = []
for top in sorted({x for ts in t.thread_topics for x in ts}):
    for k in ['post', 'comment']:
        g = t[(t.kind == k) & t.thread_topics.apply(lambda z: top in z)]
        d = dist(g); n = sum(d.values())
        if n:
            tp.append(dict(topic=top, kind=k, n=n, **{x: round(d[x] / n * 100, 1) for x in L}, net=round((d['pos'] - d['neg']) / n * 100, 1)))
out['topics'] = tp
print(pd.DataFrame(tp).sort_values(['kind', 'net']).to_string())

# engagement by post sentiment
pp = t[t.kind == 'post']
eng = pp.groupby('label').agg(n=('id', 'size'), reactions_mean=('reactions', 'mean'), reactions_median=('reactions', 'median'),
                              comments_mean=('comments', 'mean'), comments_median=('comments', 'median'), shares_mean=('shares', 'mean')).round(1)
out['engagement'] = eng.reset_index().to_dict('records')
print(eng)

# thread climate: for posts with >=15 scored comments
cc = t[t.kind == 'comment']
thr = cc.groupby('post_id').agg(n=('id', 'size'), neg=('label', lambda s: (s == 'neg').mean()), pos=('label', lambda s: (s == 'pos').mean()))
thr = thr[thr.n >= 15]
posts = u[u.kind == 'post'].set_index('post_id')
def snippet(pid):
    s = re.sub(r'\s+', ' ', posts.loc[pid, 'clean'] or '')
    return (s[:150] + '…') if len(s) > 150 else s
rows = []
for pid, r in thr.iterrows():
    rows.append(dict(post_id=pid, date=str(posts.loc[pid, 'ts'].date()), n=int(r.n), neg=round(r.neg * 100), pos=round(r.pos * 100),
                     reactions=int(posts.loc[pid, 'reactions']), comments=int(posts.loc[pid, 'comments']),
                     post_label=posts.loc[pid, 'label'], text=snippet(pid), topics=posts.loc[pid, 'topics']))
thr_df = pd.DataFrame(rows)
out['threads_negative'] = thr_df.sort_values(['neg', 'n'], ascending=False).head(12).to_dict('records')
out['threads_positive'] = thr_df.sort_values(['pos', 'n'], ascending=False).head(10).to_dict('records')
out['threads_biggest'] = thr_df.sort_values('n', ascending=False).head(12).to_dict('records')
out['thread_count'] = len(thr_df)
out['thread_neg_share_dist'] = np.histogram(thr_df.neg, bins=[0, 20, 40, 60, 80, 101])[0].tolist()
print(thr_df.sort_values('neg', ascending=False).head(12)[['date', 'n', 'neg', 'pos', 'text']].to_string())

# comment depth: replies vs top-level
out['by_depth'] = {str(int(k)): dist(g) for k, g in cc.groupby('depth')}
print(out['by_depth'])

# comment reactions: do negative comments get more likes?
out['comment_reactions'] = cc.groupby('label').comment_reactions.mean().round(2).to_dict()
print(out['comment_reactions'])

# examples (high-confidence, short) — for the dashboard, paraphrase-free since it's user's own data
ex = {}
for lab, col in [('neg', 'p_neg'), ('pos', 'p_pos')]:
    g = cc[(cc.label == lab) & cc.clean.str.len().between(40, 160)].sort_values(col, ascending=False)
    ex[lab] = [re.sub(r'\s+', ' ', x) for x in g.clean.head(8)]
out['examples'] = ex
json.dump(out, open(f'{W}/summary.json', 'w'), ensure_ascii=False, indent=1, default=str)

# export labelled data
exp = u[['kind', 'id', 'post_id', 'ts', 'author', 'label', 'p_neg', 'p_pos', 'reactions', 'comments', 'comment_reactions', 'depth', 'thread_topics', 'text']].copy()
exp['ts'] = exp.ts.dt.strftime('%Y-%m-%d %H:%M')
exp['thread_topics'] = exp.thread_topics.apply(lambda z: '; '.join(z))
exp['p_neg'] = exp.p_neg.round(3); exp['p_pos'] = exp.p_pos.round(3)
exp.to_csv(f'{W}/szentiment_cimkezett.csv', index=False, encoding='utf-8-sig')
