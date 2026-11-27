#!/usr/bin/env python3
"""B rész: a feladatok lefuttatása a `claude -p` paranccsal, folytatható módon.

Cellák: Haiku 5.5 és Sonnet 5.5 teljes rács (70 feladat), Opus 5 összevető minta
(20 feladat). Minden feladat 10 változatban, 2 ismétlésben fut.
Minden hívás eredménye külön fájlba kerül (data/b_raw/), a már kész hívásokat
az újraindítás nem küldi el újra. A hibakezelést a common.robust_call végzi.

Használat:
    python3 run_test.py                  # teljes futás
    python3 run_test.py --pilot          # kis próbafuttatás (modellenként 2 feladat)
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
COMPARE_TASKS = 30  # az Opus összevető minta mérete (10 számtani + 10 nehéz + 10 kinyerős)


def load_tasks():
    return json.loads((TASKS / "ground_truth.json").read_text(encoding="utf-8"))


def pick_compare(tasks):
    """Az összevető minta: a három válaszos kategóriából 10-10 feladat, rögzített maggal."""
    rng = random.Random("nyelv_opus_minta")
    out = []
    for cat in ("szamtani", "nehez", "kinyeres"):
        ids = [t["task_id"] for t in tasks if t["category"] == cat]
        out += rng.sample(ids, 10)
    return set(out)


def build_jobs(pilot=False):
    tasks = load_tasks()
    M = common.models()
    compare = pick_compare(tasks)
    jobs = []
    for group, ids in (("full_grid", None), ("comparison_sample", compare)):
        for m in M[group]:
            sel = [t for t in tasks if ids is None or t["task_id"] in ids]
            if pilot:
                sel = [t for t in tasks if t["task_id"] in ("N01_1", "E04_1", "O01_1")][:3]
            for t in sel:
                for v in t["variants"]:
                    for r in range(1, (1 if pilot else REPEATS) + 1):
                        jobs.append({"task": t["task_id"], "variant": v, "model": m["resolved_id"],
                                     "alias": m["alias"], "rep": r})
    random.Random("nyelv_b_sorrend").shuffle(jobs)
    return jobs


def job_path(j, out_dir):
    return out_dir / f"{j['task']}__{j['variant']}__{j['alias']}__r{j['rep']}.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--max-pause-hours", type=float, default=24)
    ap.add_argument("--workers", type=int, default=3, help="párhuzamos hívások száma")
    ap.add_argument("--equiv-cap", type=float, default=0, help="egyenértékű dollár felső határ (0 = nincs)")
    args = ap.parse_args()
    common.RUN_NAME = "b_pilot" if args.pilot else "b"
    out_dir = DATA / ("b_pilot" if args.pilot else "b_raw")

    jobs = build_jobs(args.pilot)
    todo = [j for j in jobs if not common.read_valid(job_path(j, out_dir))]
    if args.max_calls:
        todo = todo[:args.max_calls]
    print(f"{len(jobs)} hívás összesen, ebből {len(todo)} hiányzik.", flush=True)

    lock = threading.Lock()
    stat = {"done": 0, "failed": 0, "cost": 0.0, "n": 0, "stop": False}
    t0 = time.time()

    def work(j):
        if stat["stop"]:
            return
        prompt = (TASKS / "prompts" / f"{j['task']}__{j['variant']}.txt").read_text(encoding="utf-8")
        t1 = time.time()
        try:
            d = common.robust_call(prompt, j["model"], max_pause_s=args.max_pause_hours * 3600)
            u = d["usage"]
            c = common.equivalent_cost(j["model"], u)
            common.write_json_atomic(job_path(j, out_dir), {
                "ok": True, **j, "prompt_chars": len(prompt),
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
            if args.equiv_cap and stat["cost"] >= args.equiv_cap:
                stat["stop"] = True

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    done, failed, cost = stat["done"], stat["failed"], stat["cost"]
    common.write_status(state="finished", done=done, failed=failed, equiv_cost_usd=round(cost, 3))
    print(f"Vége. Új: {done}, hibás: {failed}, egyenértékű költség: {cost:.2f} $")


if __name__ == "__main__":
    main()
