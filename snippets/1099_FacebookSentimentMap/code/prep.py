import json, sys, random, re
import pandas as pd

src = sys.argv[1]
d = json.load(open(src))
rows = []
for p in d:
    own = (p.get('text') or '').strip()
    sh = p.get('sharedPost') or {}
    shtxt = (sh.get('text') or '').strip()
    text = own if own else shtxt
    rows.append(dict(kind='post', id=p['post_id'], post_id=p['post_id'], text=text,
                     own_text=bool(own), shared=bool(sh), author=p['user']['name'],
                     ts=p['creation_timestamp'] / 1000, reactions=p['reactions_count'],
                     comments=p['comments_count'], shares=p['shares_count'], depth=None,
                     comment_reactions=None))
    for c in p.get('topComment') or []:
        rows.append(dict(kind='comment', id=c['id'], post_id=p['post_id'],
                         text=(c.get('text') or '').strip(), own_text=True, shared=False,
                         author=c.get('author_name'), ts=c.get('timestamp'),
                         reactions=None, comments=None, shares=None, depth=c.get('depth'),
                         comment_reactions=c.get('reactions_count')))
df = pd.DataFrame(rows)
df['ts'] = pd.to_datetime(df['ts'], unit='s', utc=True).dt.tz_convert('Europe/Budapest')
df.to_pickle('work/units.pkl')
print(df.groupby('kind').size(), (df.text == '').groupby(df.kind).sum())

# validation sample
random.seed(42)
t = df[df.text.str.len() > 2]
sample = pd.concat([t[t.kind == 'comment'].sample(130, random_state=7),
                    t[t.kind == 'post'].sample(70, random_state=7)])
sample[['kind', 'id', 'text']].to_json('work/val_sample.json', orient='records', force_ascii=False)
for i, r in enumerate(sample.itertuples()):
    print(f"{i}|{r.kind[0]}| " + re.sub(r'\s+', ' ', r.text)[:260])
