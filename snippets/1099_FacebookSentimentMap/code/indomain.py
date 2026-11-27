"""In-domain classifier: hand-labelled FB items + out-of-domain/lexicon/emoji features. Repeated CV, then fit on all."""
import sys, json, pickle
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np, pandas as pd, scipy.sparse as sp
from model import Model, norm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

W = 'work'
m = pickle.load(open(f'{W}/model.pkl', 'rb'))
s1 = json.load(open(f'{W}/val_sample.json')); g1 = open(f'{W}/gold.txt').read().split()
s2 = json.load(open(f'{W}/train2_sample.json')); g2 = open(f'{W}/gold2.txt').read().split()
items = s1 + s2; y = np.array(g1 + g2)
texts = [norm(r['text']) for r in items]
kinds = np.array([r['kind'] for r in items])

units = pd.read_pickle(f'{W}/units.pkl')
alltexts = [norm(t) for t in units.text.tolist()]
vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=150000)
vec.fit(alltexts)

def dense(F):
    sup, neu, lex, hits, emo, excl, ln = F.T
    q = np.array([[('?' in t) * 1.0] for t in texts]) if F.shape[0] == len(texts) else None
    return np.column_stack([sup, neu, lex, np.log1p(hits), emo, np.minimum(excl, 3), np.log1p(ln)])

F = m.features(texts)
D = dense(F)
Xt = vec.transform(texts)

def build(Xt, D, scaler):
    return sp.hstack([Xt, sp.csr_matrix(scaler.transform(D) * 0.6)]).tocsr()

res = {}
for C in [0.5, 1, 2, 4]:
    accs, f1s, preds = [], [], []
    for tr, te in RepeatedStratifiedKFold(n_splits=5, n_repeats=6, random_state=1).split(D, y):
        sc = StandardScaler().fit(D[tr])
        clf = LogisticRegression(C=C, max_iter=3000, class_weight='balanced').fit(build(Xt[tr], D[tr], sc), y[tr])
        p = clf.predict(build(Xt[te], D[te], sc))
        accs.append(accuracy_score(y[te], p)); f1s.append(f1_score(y[te], p, average='macro'))
    res[C] = (np.mean(accs), np.mean(f1s))
    print(f'C={C}: CV acc {np.mean(accs):.3f}  macroF1 {np.mean(f1s):.3f}')

# rule-based baseline on same 460 for comparison
p = json.load(open(f'{W}/val_result.json'))['params']
_, Lr = Model.combine(F, tuple(p[:4]), p[4])
print('rule baseline on 460 (tuned on first 200):', accuracy_score(y, Lr), f1_score(y, Lr, average='macro'))
print('rule baseline on 260 new only:', accuracy_score(y[200:], Lr[200:]), f1_score(y[200:], Lr[200:], average='macro'))

Cbest = max(res, key=lambda c: res[c][1])
# out-of-fold confusion matrix (single 10-fold run) for prevalence correction
from sklearn.model_selection import StratifiedKFold
oof = np.empty(len(y), dtype=object)
for tr, te in StratifiedKFold(n_splits=10, shuffle=True, random_state=3).split(D, y):
    sc = StandardScaler().fit(D[tr])
    clf = LogisticRegression(C=Cbest, max_iter=3000, class_weight='balanced').fit(build(Xt[tr], D[tr], sc), y[tr])
    oof[te] = clf.predict(build(Xt[te], D[te], sc))
labs = ['neg', 'neu', 'pos']
cm = confusion_matrix(y, oof, labels=labs)
print('OOF confusion (rows=gold):\n', cm)
for k in ['comment', 'post']:
    mk = kinds == k
    print(k, 'OOF acc', round(accuracy_score(y[mk], oof[mk]), 3), 'F1', round(f1_score(y[mk], oof[mk], average='macro'), 3), 'n', mk.sum())

sc = StandardScaler().fit(D)
clf = LogisticRegression(C=Cbest, max_iter=3000, class_weight='balanced').fit(build(Xt, D, sc), y)
pickle.dump(dict(vec=vec, sc=sc, clf=clf), open(f'{W}/indomain.pkl', 'wb'))
json.dump(dict(C=Cbest, cv_acc=res[Cbest][0], cv_f1=res[Cbest][1], n=len(y), cm=cm.tolist(), labels=labs,
               gold_dist={l: int((y == l).sum()) for l in labs},
               oof_acc_comment=accuracy_score(y[kinds == 'comment'], oof[kinds == 'comment']),
               oof_acc_post=accuracy_score(y[kinds == 'post'], oof[kinds == 'post'])),
          open(f'{W}/indomain_eval.json', 'w'), indent=1)
