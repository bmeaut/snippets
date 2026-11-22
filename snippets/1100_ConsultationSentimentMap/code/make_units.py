"""Elemzési egységek: a szegmensek összevonása kb. 20–25 másodperces szakaszokká.

Használat:
    python code/make_units.py <tsv_mappa> <munka_mappa>

Új egység kezdődik, ha az aktuális 25 másodpercnél hosszabb lenne, vagy ha két
szegmens között 3 másodpercnél hosszabb csend van. Kimenet: units.json (a
címkézéshez, a szöveggel együtt – NEM publikálandó) és units.txt (azonosító,
perc:mp, szöveg; ebből készül a kézi címkézés).
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fixes import fix  # noqa: E402

MAX_LEN, MAX_GAP = 25, 3
tsv_dir, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
segs = []
for f in sorted(glob.glob(os.path.join(tsv_dir, "*.tsv"))):
    for line in open(f):
        s, e, t = line.rstrip("\n").split("\t", 2)
        if t.strip():
            segs.append((float(s), float(e), fix(t.strip())))
units, cur = [], None
for s, e, t in segs:
    if cur and (e - cur["start"] > MAX_LEN or s - cur["end"] > MAX_GAP):
        units.append(cur)
        cur = None
    if cur is None:
        cur = {"start": s, "end": e, "text": t}
    else:
        cur["end"] = e
        cur["text"] += " " + t
units.append(cur)
for i, u in enumerate(units):
    u["id"] = i
json.dump(units, open(os.path.join(work, "units.json"), "w"), ensure_ascii=False)
with open(os.path.join(work, "units.txt"), "w") as f:
    for u in units:
        f.write(f"{u['id']}\t{int(u['start']) // 60}:{int(u['start']) % 60:02d}\t{u['text']}\n")
print(len(units), "egység")
