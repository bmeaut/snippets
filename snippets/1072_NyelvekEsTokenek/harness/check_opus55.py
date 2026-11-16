#!/usr/bin/env python3
"""Az Opus 5.5 és az Opus 5 tokenizálójának összevetése az A rész adagjain.

Az Opus 5.5-öt a fő mérés Claude Code verziója (2.1.179) nem támogatta, ezért ez az ellenőrzés
egy újabb verzióval (2.1.317) fut. Az újabb verzió hívásonkénti fix bemeneti többlete nagyobb, és
hívásonként kb. 2-3 tokennyit ingadozik (azonos prompt ismételt hívására is), ezért:
  1. mindkét modellt mind a 404 adagon megmérem ugyanazzal az új verzióval (azonos keretezés),
  2. a fix többletet (kiindulási prompt) modellenként 20 hívás átlagából számolom, nem egyetlen hívásból,
  3. a két modell nettó tokenszámának különbségét adagonként számolom, és az átlagát 95%-os
     konfidencia-intervallummal adom meg (a hívásonkénti zaj adagonként nem szűrhető ki).
Kimenet: data/a_check/ (hívásonként), data/a_check_baselines.json, data/a_check_opus55.json (összefoglaló).
"""
import json
import math
import random
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor

import common
from measure_tokens_a import BATCH, INSTR, LANGS, N_BATCHES, load_flores

OUT = common.ROOT / "data" / "a_check"
NEW, OLD = "claude-opus-5-5", "claude-opus-5"


def main():
    common.RUN_NAME = "check_opus55"
    flores = load_flores()
    rng = random.Random("nyelv_opus55_minta")
    sample = {l: set(range(N_BATCHES)) for l in LANGS}
    jobs = [(NEW, "baseline", None), (OLD, "baseline", None)]
    jobs += [(NEW, l, b) for l in LANGS for b in range(N_BATCHES)]
    jobs += [(OLD, l, b) for l in LANGS for b in sorted(sample[l])]

    def name(m, l, b):
        return f"{m}__baseline.json" if b is None else f"{m}__{l}__{b:03d}.json"

    todo = [j for j in jobs if not common.read_valid(OUT / name(*j))]
    print(f"{len(jobs)} hívás, ebből {len(todo)} hiányzik.", flush=True)
    cnt = {"i": 0}
    lock = threading.Lock()

    def work(j):
        m, l, b = j
        content = "" if b is None else "\n".join(flores[l][b * BATCH:(b + 1) * BATCH])
        prompt = INSTR if b is None else content + "\n\n" + INSTR
        r = common.robust_call(prompt, m)
        common.write_json_atomic(OUT / name(*j), {"ok": True, "model": m, "lang": l, "batch": b,
                                                  "input_tokens": common.input_tokens(r["usage"]),
                                                  "usage": r["usage"]})
        with lock:
            cnt["i"] += 1
            if cnt["i"] % 50 == 0:
                print(f"[{cnt['i']}/{len(todo)}]", flush=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, todo))

    bpath = common.ROOT / "data" / "a_check_baselines.json"
    if bpath.exists():
        bl = json.loads(bpath.read_text(encoding="utf-8"))
    else:
        def base(m):
            with ThreadPoolExecutor(max_workers=6) as ex:
                return list(ex.map(lambda _: common.input_tokens(common.robust_call(INSTR, m)["usage"]), range(20)))
        bl = {"opus5": base(OLD), "opus55": base(NEW)}
        bpath.write_text(json.dumps(bl), encoding="utf-8")
    m5, m55 = statistics.mean(bl["opus5"]), statistics.mean(bl["opus55"])
    recs = [r for r in common.load_records("a_check") if r["lang"] != "baseline"]
    d = {(r["model"], r["lang"], r["batch"]): r["input_tokens"] for r in recs}
    diff, by = [], {}
    for (m, l, b), v in d.items():
        if m == NEW:
            x = (v - m55) - (d[(OLD, l, b)] - m5)
            diff.append(x)
            by.setdefault(l, []).append(x)
    sd = statistics.stdev(diff)
    ci = 1.96 * sd / math.sqrt(len(diff))
    summary = {
        "adagok": len(diff),
        "opus55_minusz_opus5_netto_kulonbseg_atlag": round(statistics.mean(diff), 2),
        "konfidencia_intervallum_95_plusz_minusz": round(ci, 2),
        "adagonkenti_szoras": round(sd, 2), "min": round(min(diff), 1), "max": round(max(diff), 1),
        "nyelvenkenti_atlag": {l: round(statistics.mean(x), 2) for l, x in by.items()},
        "alapvonal_atlag_opus5": round(m5, 1), "alapvonal_atlag_opus55": round(m55, 1),
        "alapvonal_szoras_opus5": round(statistics.pstdev(bl["opus5"]), 2),
        "alapvonal_szoras_opus55": round(statistics.pstdev(bl["opus55"]), 2),
    }
    (common.ROOT / "data" / "a_check_opus55.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
