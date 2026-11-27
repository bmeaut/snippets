#!/usr/bin/env python3
"""A rész: ugyanaz a tartalom hány tokent jelent a különböző nyelveken és modelleken.

A FLORES-200 `devtest` első 1010 mondatát 10 mondatos csomagokban (101 csomag nyelvenként)
küldi el a `claude -p` paranccsal, és a bemeneti tokenszámot a JSON `usage` mezőiből olvassa ki.
Modellenként egy "alapvonal" hívás méri a fix többletet (csak a kért válaszutasítás).
A futás folytatható: a már lemért csomagokat nem kéri le újra.
"""
import argparse
import random
import time

import common

FLORES = common.ROOT / "data" / "flores"
A_RAW = common.ROOT / "data" / "a_raw"
LANGS = {"en": "eng_Latn", "hu": "hun_Latn", "de": "deu_Latn", "ja": "jpn_Jpan"}
BATCH, N_BATCHES = 10, 101
INSTR = "Reply with the single word OK."


def load_flores():
    out = {}
    for lang, code in LANGS.items():
        lines = (FLORES / f"{code}.devtest").read_text(encoding="utf-8").split("\n")
        lines = [l for l in lines if l != ""]
        assert len(lines) == 1012, (lang, len(lines))
        out[lang] = lines
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pause-hours", type=float, default=24)
    ap.add_argument("--reverse", action="store_true", help="fordított sorrend (második, párhuzamos futtatóhoz)")
    ap.add_argument("--limit", type=int, default=0, help="csak az első N feladat (próbához)")
    args = ap.parse_args()
    common.RUN_NAME = "a_rev" if args.reverse else "a"
    max_pause = args.max_pause_hours * 3600

    flores = load_flores()
    M = common.models()
    models = [m["resolved_id"] for g in ("full_grid", "comparison_sample", "tokenizer_only") for m in M[g]]

    jobs = [(m, "baseline", None) for m in models]
    jobs += [(m, lang, b) for m in models for lang in LANGS for b in range(N_BATCHES)]
    random.Random("nyelv_a_sorrend").shuffle(jobs)
    if args.reverse:
        jobs.reverse()
    if args.limit:
        jobs = jobs[:args.limit]

    done = failed = skipped = 0
    t0 = time.time()
    for n, (model, lang, b) in enumerate(jobs, 1):
        name = f"{model}__baseline" if b is None else f"{model}__{lang}__{b:03d}"
        path = A_RAW / f"{name}.json"
        if common.read_valid(path):
            skipped += 1
            continue
        if b is None:
            content, prompt = "", INSTR
        else:
            content = "\n".join(flores[lang][b * BATCH:(b + 1) * BATCH])
            prompt = content + "\n\n" + INSTR
        try:
            d = common.robust_call(prompt, model, max_pause_s=max_pause)
            u = d["usage"]
            common.write_json_atomic(path, {
                "ok": True, "model": model, "lang": lang, "batch": b,
                "input_tokens": common.input_tokens(u), "usage": u,
                "chars": len(content), "bytes": len(content.encode("utf-8")),
                "result": d["result"][:60], "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
            done += 1
        except common.CallFailed as e:
            failed += 1
            common.write_json_atomic(path, {"ok": False, "error": e.text[:300]})
        if (done + failed) % 25 == 0:
            common.write_status(state="running", total=len(jobs), done=done, skipped=skipped,
                                failed=failed, elapsed_min=int((time.time() - t0) / 60))
            print(f"[{n}/{len(jobs)}] kész: {done}, kihagyva: {skipped}, hibás: {failed}", flush=True)
    common.write_status(state="finished", total=len(jobs), done=done, skipped=skipped, failed=failed)
    print(f"Vége. Új: {done}, kihagyva (már kész): {skipped}, hibás: {failed}")


if __name__ == "__main__":
    main()
