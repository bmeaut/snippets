#!/usr/bin/env python3
"""A látható válasz tokenszámának mérése egy véletlenszerű 20%-os részmintán.

A B rész `output_tokens` értéke több lehet, mint a válasz látható szövegének tokenszáma. A látható
válasz szövegét ugyanazon a modellen promptként elküldi (a 4.2 szerinti hívásszerkezettel), a
bemeneti tokenszámból a fix alapvonalat levonja, és a látható szövegen felüli részt
(`output_tokens` - látható tokenek) számolja ki. Folytatható, hibatűrő.
"""
import argparse
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import common

B_RAW = common.ROOT / "data" / "b_raw"
OUT = common.ROOT / "data" / "b_visible"
A_RAW = common.ROOT / "data" / "a_raw"
INSTR = "Reply with the single word OK."
SHARE = 0.20


def baselines():
    out = {}
    for p in A_RAW.glob("*__baseline.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("ok"):
            out[d["model"]] = d["input_tokens"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-pause-hours", type=float, default=24)
    args = ap.parse_args()
    common.RUN_NAME = "visible"
    base = baselines()
    files = sorted(B_RAW.glob("*.json"))
    rng = random.Random("nyelv_visible_resz")
    sample = rng.sample(files, int(len(files) * SHARE))
    todo = [p for p in sample if not common.read_valid(OUT / p.name)]
    print(f"{len(sample)} mintaelem, ebből {len(todo)} hiányzik.", flush=True)
    lock = threading.Lock()
    n = {"i": 0, "bad": 0}

    def work(p):
        d = json.loads(p.read_text(encoding="utf-8"))
        prompt = d["result"] + "\n\n" + INSTR
        try:
            r = common.robust_call(prompt, d["model"], max_pause_s=args.max_pause_hours * 3600)
            tokens = common.input_tokens(r["usage"]) - base[d["model"]]
            common.write_json_atomic(OUT / p.name, {"ok": True, "model": d["model"], "alias": d["alias"],
                                                   "task": d["task"], "variant": d["variant"], "rep": d["rep"],
                                                   "visible_tokens": tokens, "output_tokens": d["output_tokens"],
                                                   "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
        except common.CallFailed as e:
            common.write_json_atomic(OUT / p.name, {"ok": False, "error": e.text[:200]})
            with lock:
                n["bad"] += 1
        with lock:
            n["i"] += 1
            if n["i"] % 50 == 0:
                print(f"[{n['i']}/{len(todo)}] hibás: {n['bad']}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    print("Vége. Hibás:", n["bad"])


if __name__ == "__main__":
    main()
