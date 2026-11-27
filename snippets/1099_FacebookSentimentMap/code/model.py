"""Hungarian sentiment: supervised TF-IDF model (HuSST + OpinHuBank) + PrecoSenti lexicon + emoji."""
import json, re, csv, pickle, unicodedata
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_union, make_pipeline

EXT = 'ext'

def norm(t):
    t = unicodedata.normalize('NFKC', t or '')
    t = re.sub(r'https?://\S+', ' ', t)
    return t

# ---------- training corpora ----------
def load_train():
    X, y = [], []
    for s in ['train', 'dev']:
        for r in json.load(open(f'{EXT}/HuSST/data/sst_{s}.json')):
            X.append(r['Sent']); y.append(r['label'])
    with open(f'{EXT}/SentimentAnalysisHUN/resources/SentimentCorpus/OpinHuBank_20130106.csv', encoding='iso-8859-2') as f:
        for r in csv.DictReader(f):
            a = [int(r[f'Annot{i}']) for i in range(1, 6)]
            s = sum(a)
            lab = 'positive' if s >= 2 else 'negative' if s <= -2 else 'neutral'
            X.append(r['Sentence']); y.append(lab)
    return X, y

# ---------- lexicon ----------
def load_lex(name):
    with open(f'{EXT}/SentimentAnalysisHUN/resources/SentimentLexicons/{name}', encoding='utf-8', errors='ignore') as f:
        return [w.strip().lower() for w in f if w.strip() and ' ' not in w.strip()]

POS_LEX = set(load_lex('PrecoPos.txt'))
NEG_LEX = set(load_lex('PrecoNeg.txt'))
# domain additions for informal Facebook Hungarian
POS_LEX |= {'köszön', 'köszi', 'kösz', 'szuper', 'király', 'csodás', 'gratul', 'imád', 'hálás', 'szeretettel',
            'gyönyörű', 'fantasztikus', 'remek', 'kiváló', 'tökéletes', 'örül', 'boldog', 'végre', 'szívesen',
            'támogat', 'egyetért', 'egyet ért', 'aranyos', 'cuki', 'hajrá', 'bravó', 'jó', 'jól', 'szép', 'szeret'}
NEG_LEX |= {'szar', 'gáz', 'mutyi', 'hülye', 'idióta', 'felháborító', 'felháborít', 'botrány', 'szégyen',
            'gyalázat', 'tragédia', 'sajnos', 'büdös', 'katasztróf', 'borzalm', 'rossz', 'baj', 'probléma',
            'panasz', 'veszély', 'lop', 'ellop', 'betör', 'csaló', 'átver', 'hazug', 'hazud', 'utál', 'undor',
            'zaj', 'kosz', 'szemét', 'szemetel', 'dug', 'tűrhetetlen', 'elfogadhatatlan', 'pusztul', 'tönkre',
            'baleset', 'elüt', 'ütött', 'csalód', 'mérges', 'düh', 'idegesít', 'kurva', 'bunkó', 'paraszt',
            'senki', 'rettenet', 'elkeserít', 'fáj', 'nincs', 'semmi', 'sehol', 'nem működik', 'gratul'}
# 'gratul' is often sarcastic ("Gratulálok!") — keep positive but weaker via ambiguity handling below
AMBIG = {'gratul', 'senki', 'nincs', 'semmi'}
NEGATORS = {'nem', 'sem', 'se', 'ne', 'nincs', 'nincsen', 'soha', 'semmi'}

TOK = re.compile(r"[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ]+")

def _build_index(lex):
    exact = {w for w in lex if len(w) < 5}
    pref = sorted({w for w in lex if len(w) >= 5}, key=len, reverse=True)
    byfirst = {}
    for w in pref:
        byfirst.setdefault(w[:3], []).append(w)
    return exact, byfirst

POS_IDX = _build_index(POS_LEX)
NEG_IDX = _build_index(NEG_LEX)
# Short stems that are safe with common suffixes only
SHORT_OK_SUFFIX = re.compile(r'^(ak|ek|at|et|ok|ök|ul|ül|an|en|ja|je|nak|nek|ban|ben|ra|re|ról|ről|tól|től|hoz|hez|höz|on|ön|ság|ség|abb|ebb|ul|é|ja|ből|ból|ért|val|vel|t|k|n)?$')

def match(tok, idx):
    exact, byfirst = idx
    if tok in exact:
        return True
    for w in exact:
        if len(w) >= 3 and tok.startswith(w) and SHORT_OK_SUFFIX.match(tok[len(w):]):
            return True
    for w in byfirst.get(tok[:3], []):
        if tok.startswith(w) and len(tok) - len(w) <= 8:
            return True
    return False

def lex_score(text):
    toks = [t.lower() for t in TOK.findall(text)]
    s, hits = 0.0, 0
    for i, t in enumerate(toks):
        if t in NEGATORS:
            continue
        p, n = match(t, POS_IDX), match(t, NEG_IDX)
        if p == n:
            continue
        v = 1.0 if p else -1.0
        # the word 'jó' as part of greetings ('jó napot', 'jó reggelt') is neutral
        if t in ('jó',) and i + 1 < len(toks) and toks[i + 1].startswith(('nap', 'regg', 'est', 'éjsz')):
            continue
        if any(t.startswith(a) for a in AMBIG):
            v *= 0.5
        prev = toks[max(0, i - 2):i]
        if any(x in NEGATORS for x in prev):
            v = -v * 0.8
        s += v; hits += 1
    n = max(len(toks), 1)
    return s / np.sqrt(n), hits

POS_EMO = set('😊😍❤🥰🙏👍😀😁😃😄🤩✨🎉🥳💪👏🫶😘💖💕💚💙💛🧡🤍♥☺🙂😉🌸🌞🍀🤗😇👌🎊🌟⭐💐')
NEG_EMO = set('😡😠🤬😢😭☹😞👎🙄😤😒😔😟😣😖😩😫🤮🤢💩😕🥺😰😨⚠🛑‼')
LAUGH = set('😂🤣😅😆')

def emo_score(text):
    p = sum(1 for ch in text if ch in POS_EMO)
    n = sum(1 for ch in text if ch in NEG_EMO)
    l = sum(1 for ch in text if ch in LAUGH)
    p += len(re.findall(r'[:;]-?[)D]|<3', text))
    n += len(re.findall(r':-?\(', text))
    excl = len(re.findall(r'[!?]{3,}', text))
    return np.tanh(p - n + 0.3 * l), excl

class Model:
    def fit(self):
        X, y = load_train()
        self.vec = make_union(
            TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), min_df=2, sublinear_tf=True, max_features=300000, lowercase=True),
            TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1, sublinear_tf=True, lowercase=True))
        Xv = self.vec.fit_transform([norm(x) for x in X])
        self.clf = LogisticRegression(max_iter=2000, C=4, class_weight='balanced')
        self.clf.fit(Xv, y)
        self.classes = list(self.clf.classes_)
        return self

    def features(self, texts):
        texts = [norm(t) for t in texts]
        P = self.clf.predict_proba(self.vec.transform(texts))
        ip, ineg, ineu = self.classes.index('positive'), self.classes.index('negative'), self.classes.index('neutral')
        rows = []
        for t, p in zip(texts, P):
            ls, hits = lex_score(t)
            es, excl = emo_score(t)
            rows.append([p[ip] - p[ineg], p[ineu], ls, hits, es, excl, len(t)])
        return np.array(rows)

    @staticmethod
    def combine(F, w=(1.0, 1.0, 0.8, 0.25), th=0.35):
        sup, neu, lex, hits, emo, excl, ln = F.T
        score = w[0] * sup + w[1] * lex + w[2] * emo - w[3] * np.minimum(excl, 3) * (lex <= 0)
        score = np.clip(score, -3, 3)
        lab = np.where(score > th, 'pos', np.where(score < -th, 'neg', 'neu'))
        return score, lab

if __name__ == '__main__':
    m = Model().fit()
    pickle.dump(m, open('work/model.pkl', 'wb'))
    print('trained', m.classes)
