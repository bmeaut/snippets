import sys, json, pickle, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np, pandas as pd, scipy.sparse as sp
from model import Model, norm
from topics import tag

W = 'work'
m = pickle.load(open(f'{W}/model.pkl', 'rb'))
im = pickle.load(open(f'{W}/indomain.pkl', 'rb'))
u = pd.read_pickle(f'{W}/units.pkl')
u['clean'] = [norm(t) for t in u.text]
u['has_text'] = u.clean.str.replace(r'\W', '', regex=True).str.len() >= 2
X = u[u.has_text]
F = m.features(X.clean.tolist())
sup, neu, lex, hits, emo, excl, ln = F.T
D = np.column_stack([sup, neu, lex, np.log1p(hits), emo, np.minimum(excl, 3), np.log1p(ln)])
M = sp.hstack([im['vec'].transform(X.clean.tolist()), sp.csr_matrix(im['sc'].transform(D) * 0.6)]).tocsr()
P = im['clf'].predict_proba(M)
cls = list(im['clf'].classes_)
u.loc[X.index, 'label'] = np.array(cls)[P.argmax(1)]
u.loc[X.index, 'p_neg'] = P[:, cls.index('neg')]
u.loc[X.index, 'p_pos'] = P[:, cls.index('pos')]
u['score'] = u.p_pos - u.p_neg
u['label'] = u['label'].fillna('nincs szöveg')

# topics: comments inherit parent post's topics (plus their own)
post_text = u[u.kind == 'post'].set_index('post_id').clean
u['topics'] = [tag(t) for t in u.clean]
ptopics = u[u.kind == 'post'].set_index('post_id').topics
u['thread_topics'] = [sorted(set(t) | set(ptopics.get(pid, []))) if k == 'comment' else t
                      for t, pid, k in zip(u.topics, u.post_id, u.kind)]
u['month'] = u.ts.dt.strftime('%Y-%m')
u.to_pickle(f'{W}/scored.pkl')
print(u.groupby(['kind', 'label']).size())
