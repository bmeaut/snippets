import sys, json, pickle, itertools
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
import model
from model import Model
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

m = pickle.load(open('work/model.pkl', 'rb'))
s = json.load(open('work/val_sample.json'))
gold = np.array(open('work/gold.txt').read().split())
F = m.features([r['text'] for r in s])
kinds = np.array([r['kind'] for r in s])

def ev(lab, mask=slice(None)):
    return accuracy_score(gold[mask], lab[mask]), f1_score(gold[mask], lab[mask], average='macro')

# component baselines
sup = F[:, 0]
for name, sc in [('supervised', F[:, 0]), ('lexicon', F[:, 2]), ('emoji', F[:, 4])]:
    best = max(((ev(np.where(sc > t, 'pos', np.where(sc < -t, 'neg', 'neu')))[1], t) for t in np.arange(0.02, 1.0, 0.02)))
    print(f'{name:12s} best macroF1={best[0]:.3f} @th={best[1]:.2f}')

# grid search with 2-fold CV over random halves (repeat) to get honest estimate
grid = list(itertools.product([0.5, 1.0, 1.5], [0.5, 1.0, 1.5, 2.0], [0.5, 1.0], [0, 0.25], np.arange(0.1, 0.8, 0.05)))
def lab_for(g):
    w0, w1, w2, w3, th = g
    return Model.combine(F, (w0, w1, w2, w3), th)[1]
labs = {g: lab_for(g) for g in grid}
rng = np.random.default_rng(0)
cv = []
for rep in range(20):
    idx = rng.permutation(len(gold)); a, b = idx[:100], idx[100:]
    for tr, te in [(a, b), (b, a)]:
        g = max(grid, key=lambda g: f1_score(gold[tr], labs[g][tr], average='macro'))
        cv.append((accuracy_score(gold[te], labs[g][te]), f1_score(gold[te], labs[g][te], average='macro')))
cv = np.array(cv)
print('CV held-out acc %.3f  macroF1 %.3f' % tuple(cv.mean(0)))
gbest = max(grid, key=lambda g: f1_score(gold, labs[g], average='macro'))
L = labs[gbest]
print('best on all', gbest, ev(L))
print('comments', ev(L, kinds == 'comment'), 'posts', ev(L, kinds == 'post'))
print(confusion_matrix(gold, L, labels=['neg', 'neu', 'pos']))
json.dump(dict(params=[float(x) for x in gbest], cv_acc=float(cv[:, 0].mean()), cv_f1=float(cv[:, 1].mean()),
               acc_all=float(ev(L)[0]), f1_all=float(ev(L)[1]),
               acc_comments=float(ev(L, kinds == 'comment')[0]), acc_posts=float(ev(L, kinds == 'post')[0])),
          open('work/val_result.json', 'w'))
if '-v' in sys.argv:
    import re
    for i, (g, p) in enumerate(zip(gold, L)):
        if g != p:
            print(i, g, p, np.round(F[i, [0, 2, 4]], 2), re.sub(r'\s+', ' ', s[i]['text'])[:110])
