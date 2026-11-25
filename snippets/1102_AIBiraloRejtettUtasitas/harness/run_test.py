#!/usr/bin/env python3
"""A pontozó hívások lefuttatása a `claude -p` paranccsal, folytatható módon.

Cellák: 22 beadandó × 12 változat × 2 feltétel (S: pontozás, D: pontozás + jelzés kérése)
× 3 modell × 2 ismétlés = 3 168 hívás. Minden hívás eredménye külön fájlba kerül
(data/raw/), a már kész hívásokat az újraindítás nem küldi el újra. A hibakezelést a
common.robust_call végzi.

A kiegészítő mérések (`--part skala`, `--part fmt`, `--part hosszu`) a data/tasks/parts.json
leírása szerint futnak (data/raw_skala/, raw_fmt/, raw_hosszu/), l. generate_extra.py.

A további pontozó szerkezetek (`--part struct`): XML-címkés és rendszerprompt-szerkezet, 22
beadandó × 6 változat × 2 feltétel × 3 modell × 2 ismétlés × 2 szerkezet = 3 168 hívás
(data/raw_struct/).

Használat:
    python3 run_test.py                  # teljes futás (fő mérés)
    python3 run_test.py --part struct    # a további szerkezetek
    python3 run_test.py --pilot          # kis próbafuttatás
    python3 run_test.py --max-calls 50   # csak az első 50 hiányzó hívás
"""
import argparse
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import common

TASKS = common.ROOT / "data" / "tasks"
DATA = common.ROOT / "data"
REPEATS = 2
EFFORT = "low"


def load_prompts():
    return json.loads((TASKS / "prompts.json").read_text(encoding="utf-8"))


def load_truth():
    return json.loads((TASKS / "ground_truth.json").read_text(encoding="utf-8"))


EXTRA_PARTS = ("skala", "fmt", "hosszu", "mism", "vedekezes")


def load_parts():
    return json.loads((TASKS / "parts.json").read_text(encoding="utf-8"))


def build_jobs(pilot=False, part="main"):
    if part in EXTRA_PARTS:
        spec = load_parts()[part]
        subs = spec["subs"]
        # a cellák (variáns, szerkezet) párok: vagy kifejezetten megadottak ("cells"), vagy a
        # változatok és szerkezetek szorzata
        if "cells" in spec:
            cells = [(v, st) for v, st in spec["cells"]]
        else:
            cells = [(v, st) for v in spec["variants"] for st in spec["structs"]]
        conds = spec.get("conds", ["S", "D"])
        if pilot:
            subs, cells = subs[:2], cells[:2]
        jobs = []
        for m in common.models()["grid"]:
            for s in subs:
                for v, st in cells:
                    for c in conds:
                        for r in range(1, (1 if pilot else REPEATS) + 1):
                            j = {"sub": s, "variant": v, "cond": c, "model": m["resolved_id"],
                                 "alias": m["alias"], "rep": r}
                            if st:
                                j["struct"] = st
                            jobs.append(j)
        random.Random("birao_sorrend_" + part).shuffle(jobs)
        return jobs
    truth = load_truth()
    subs = [s["sub_id"] for s in truth["submissions"]]
    variants = list(truth["variants"])
    models = common.models()["grid"]
    if pilot:
        subs = ["B07", "B15"]
        variants = ["kontroll", "direkt_hu_vege", "rendszer_en_vege", "szabaly_hu_vege", "indoklas_hu_vege", "hatarolo_hu_vege"]
    jobs = []
    if part == "struct":
        import generate_tasks as g
        variants = g.STRUCT_VARIANTS
        if pilot:
            variants = ["kontroll", "hatarolo_hu_vege"]
        structs = g.STRUCTS
    else:
        structs = [None]
    for m in models:
        for s in subs:
            for v in variants:
                for c in ("S", "D"):
                    for st in structs:
                        for r in range(1, (1 if pilot else REPEATS) + 1):
                            j = {"sub": s, "variant": v, "cond": c, "model": m["resolved_id"],
                                 "alias": m["alias"], "rep": r}
                            if st:
                                j["struct"] = st
                            jobs.append(j)
    random.Random("birao_sorrend").shuffle(jobs)
    return jobs


def job_path(j, out_dir):
    st = f"__{j['struct']}" if j.get("struct") else ""
    return out_dir / f"{j['sub']}__{j['variant']}__{j['cond']}{st}__{j['alias']}__r{j['rep']}.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--max-pause-hours", type=float, default=24)
    ap.add_argument("--workers", type=int, default=4, help="párhuzamos hívások száma")
    ap.add_argument("--effort", default=EFFORT)
    ap.add_argument("--part", choices=("main", "struct") + EXTRA_PARTS, default="main")
    ap.add_argument("--count-missing", action="store_true", help="csak a hiányzó hívások számát írja ki")
    args = ap.parse_args()
    common.RUN_NAME = ("pilot_" if args.pilot else "") + args.part
    base = "raw" if args.part == "main" else "raw_" + args.part
    out_dir = DATA / (("pilot_" + base) if args.pilot else base)

    if args.part == "main":
        prompts = load_prompts()
    elif args.part == "struct":
        prompts = json.loads((TASKS / "prompts_struct.json").read_text(encoding="utf-8"))
    else:
        prompts = json.loads((TASKS / load_parts()[args.part]["prompts"]).read_text(encoding="utf-8"))
    jobs = build_jobs(args.pilot, args.part)
    todo = [j for j in jobs if not common.read_valid(job_path(j, out_dir))]
    if args.count_missing:
        print(len(todo))
        return
    if args.max_calls:
        todo = todo[:args.max_calls]
    print(f"{len(jobs)} hívás összesen, ebből {len(todo)} hiányzik.", flush=True)

    lock = threading.Lock()
    stat = {"done": 0, "failed": 0, "cost": 0.0, "n": 0}
    t0 = time.time()

    def work(j):
        if args.part == "main":
            prompt, system = prompts[f"{j['sub']}__{j['variant']}__{j['cond']}"], None
        else:
            st = f"__{j['struct']}" if j.get("struct") else ""
            pr = prompts[f"{j['sub']}__{j['variant']}__{j['cond']}{st}"]
            prompt, system = pr["user"], pr["system"]
        t1 = time.time()
        try:
            d = common.robust_call(prompt, j["model"], effort=args.effort,
                                   max_pause_s=args.max_pause_hours * 3600, system=system)
            u = d["usage"]
            c = common.equivalent_cost(j["model"], u)
            common.write_json_atomic(job_path(j, out_dir), {
                "ok": True, **j, "effort": args.effort, "prompt_chars": len(prompt),
                "input_tokens": common.input_tokens(u), "output_tokens": u.get("output_tokens", 0),
                "equiv_cost_usd": c, "usage": u, "result": d["result"],
                "stop_reason": d.get("stop_reason"), "duration_ms": d.get("duration_ms"),
                "wall_s": round(time.time() - t1, 1), "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
            ok = True
        except common.CallFailed as e:
            common.write_json_atomic(job_path(j, out_dir), {"ok": False, **j, "error": e.text[:300]})
            ok, c = False, 0.0
        with lock:
            stat["n"] += 1
            stat["done" if ok else "failed"] += 1
            stat["cost"] += c
            if stat["n"] % 20 == 0 or stat["n"] == len(todo):
                common.write_status(state="running", total=len(jobs), todo=len(todo), done=stat["done"],
                                    failed=stat["failed"], equiv_cost_usd=round(stat["cost"], 3),
                                    elapsed_min=int((time.time() - t0) / 60))
                print(f"[{stat['n']}/{len(todo)}] kész: {stat['done']}, hibás: {stat['failed']}, "
                      f"egyenértékű költség: {stat['cost']:.2f} $, idő: {int((time.time() - t0) / 60)} perc",
                      flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    common.write_status(state="finished", done=stat["done"], failed=stat["failed"],
                        equiv_cost_usd=round(stat["cost"], 3))
    print(f"Vége. Új: {stat['done']}, hibás: {stat['failed']}, "
          f"egyenértékű költség: {stat['cost']:.2f} $")


if __name__ == "__main__":
    main()
