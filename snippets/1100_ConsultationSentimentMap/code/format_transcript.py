"""Olvasható, időbélyeges átirat a TSV-kből (Markdown).

Használat:
    python code/format_transcript.py <tsv_mappa> [kezdés_s] [vége_s] > atirat.md

Kb. percenként új bekezdést kezd „**[óó:pp:mm]**” időbélyeggel, és kiszűri az
egymás után ismétlődő szegmenseket (a Whisper „hallucinációs hurkait”).
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fixes import fix  # noqa: E402


def ts(x):
    x = int(x)
    return f"{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}"


tsv_dir = sys.argv[1]
lo = float(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
rows = []
for f in sorted(glob.glob(os.path.join(tsv_dir, "*.tsv"))):
    for line in open(f):
        s, e, t = line.rstrip("\n").split("\t", 2)
        if lo <= float(s) < hi and t:
            rows.append((float(s), fix(t)))
out, prev = [], None
for s, t in rows:
    if t != prev:
        out.append((s, t))
    prev = t
paras, cur = [], None
for s, t in out:
    if cur is None or s - cur[0] >= 60:
        cur = [s, []]
        paras.append(cur)
    cur[1].append(t)
print("\n\n".join(f"**[{ts(s)}]** " + " ".join(txt) for s, txt in paras))
