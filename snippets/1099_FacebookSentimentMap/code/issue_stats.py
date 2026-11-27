import sys, json, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import pandas as pd, numpy as np
from issues import match, NAMES, ISSUES

W = 'work'
u = pd.read_pickle(f'{W}/scored.pkl')
u = u[u.label.isin(['neg', 'neu', 'pos'])].copy()
u['issues'] = [match(t) for t in u.clean]
u.to_pickle(f'{W}/issues_scored.pkl')

posts = u[u.kind == 'post'].set_index('post_id')
rows = []
for k, name, _ in ISSUES:
    m = u[u.issues.apply(lambda z: k in z)]
    p = m[m.kind == 'post']; c = m[m.kind == 'comment']
    # threads: post mentions it, or >=2 of its comments do
    cc = c.groupby('post_id').size()
    threads = set(p.post_id) | set(cc[cc >= 2].index)
    # all comments in those threads
    thr_comments = u[(u.kind == 'comment') & u.post_id.isin(threads)]
    resid = m[(m.kind == 'post')]
    rows.append(dict(id=k, name=name, posts=len(p), comments=len(c), mentions=len(m), threads=len(threads),
                     thread_comments=len(thr_comments),
                     neg=round((m.label == 'neg').mean() * 100, 1) if len(m) else None,
                     neg_comments=round((c.label == 'neg').mean() * 100, 1) if len(c) else None,
                     reactions=int(p.reactions.sum()),
                     peak_month=m.month.value_counts().idxmax() if len(m) else None,
                     authors=m.author.nunique()))
df = pd.DataFrame(rows).sort_values('mentions', ascending=False)
print(df.to_string())
df.to_pickle(f'{W}/issue_table.pkl')

# monthly mentions per issue (for the small bar charts on the problem cards)
months = sorted(u.month.dropna().unique())
mon = []
for i in df.id:
    vc = u[u.issues.apply(lambda z: i in z)].month.value_counts()
    mon += [dict(id=i, month=mo, mentions=int(vc.get(mo, 0))) for mo in months]
pd.DataFrame(mon).to_pickle(f'{W}/issue_monthly.pkl')
