#!/usr/bin/env python3
"""A B rész nyers hívás-eredményeinek pontozása és összesítése (data/b_results.csv).

Hívásonként: a bemeneti tokenszám (a keretezés fix többletével és anélkül), a kimeneti
tokenszám, az egyenértékű költség, a kinyert válasz, a helyesség és a válasz nyelve.

Használat:
    python3 score.py            # data/b_raw -> data/b_results.csv
    python3 score.py --pilot    # data/b_pilot -> data/b_pilot_results.csv
"""
import csv
import json
import re
import sys
import unicodedata

import common

DATA = common.ROOT / "data"
LANG_OF = {"EN": "en", "HU": "hu", "DE": "de", "JA": "ja"}
ANSWER = re.compile(r"ANSWER:\s*([^\n]*)")
# Lefordított jelölők (pl. a modell az "ANSWER:" jelölőt a válasz nyelvére fordítja): a helyességet
# ezekkel együtt is mérem, a pontos jelölő használatát külön mutatóként (format_ok).
ANSWER_ANY = re.compile(r"(?i)(?:ANSWER|ANTWORT|V[ÁA]LASZ|回答|答え)\s*[:：]\s*([^\n]*)")


def frame_overheads():
    """Modellenként a keretezés fix többlete (tokenek), a `frame__*.json` fájlokból."""
    out = {}
    for d in common.load_records("a_raw"):
        if d.get("ok") and d["_name"].endswith("__frame.json"):
            out[d["model"]] = d["input_tokens"] - d.get("content_tokens", 1)
    return out


def extract_number(text):
    """A legutolsó válasz-jelölős sor egész száma, vagy None."""
    m = ANSWER_ANY.findall(unicodedata.normalize("NFKC", text))
    if not m:
        return None
    digits = re.sub(r"[^\d]", "", m[-1])
    return int(digits) if digits else None


def detect_lang(text):
    """Egyszerű nyelvfelismerés a válasz szövegéből (az ANSWER sor nélkül)."""
    body = ANSWER.sub("", text).strip()
    # Rövid, főleg számokból álló válasznál (pl. "80 + 12 = 92, majd ...") a nyelv nem megbízhatóan
    # felismerhető: ilyenkor "ismeretlen".
    if sum(1 for c in body if c.isalpha()) < 25:
        return "?"
    ja = sum(1 for c in body if "぀" <= c <= "ヿ" or "一" <= c <= "鿿")
    if ja / max(1, len(body)) > 0.2:
        return "ja"
    try:
        from langdetect import DetectorFactory, detect
        DetectorFactory.seed = 0
        return detect(body)
    except Exception:
        return "?"


def main():
    pilot = "--pilot" in sys.argv
    raw_name = "b_pilot" if pilot else "b_raw"
    out = DATA / ("b_pilot_results.csv" if pilot else "b_results.csv")
    gt = {t["task_id"]: t for t in json.loads((DATA / "tasks" / "ground_truth.json").read_text(encoding="utf-8"))}
    frame = frame_overheads()

    vis = {}
    for v in ([] if pilot else common.load_records("b_visible")):
        if v.get("ok"):
            vis[v["_name"]] = v["visible_tokens"]
    rows = []
    for d in common.load_records(raw_name):
        if not d.get("ok"):
            continue
        t = gt[d["task"]]
        qlang, alang = d["variant"].split("_")
        text = d["result"]
        num = extract_number(text) if t["answer"] is not None else None
        correct = (num == t["answer"]) if t["answer"] is not None else ""
        format_ok = (ANSWER.search(unicodedata.normalize("NFKC", text)) is not None) if t["answer"] is not None else ""
        net_in = d["input_tokens"] - frame.get(d["model"], 0)
        pin, pout = common.PRICES[d["model"]]
        rows.append({
            "task_id": d["task"], "category": t["category"], "variant": d["variant"],
            "prompt_lang": qlang, "answer_lang": alang, "model_alias": d["alias"], "model": d["model"],
            "rep": d["rep"], "input_tokens": d["input_tokens"], "net_input_tokens": net_in,
            "output_tokens": d["output_tokens"],
            "net_cost_usd": (net_in * pin + d["output_tokens"] * pout) / 1e6,
            "equiv_cost_usd": d["equiv_cost_usd"],
            "answer_extracted": "" if num is None else num, "correct": correct, "format_ok": format_ok,
            "response_lang": detect_lang(text),
            "lang_ok": "" if detect_lang(text) == "?" else detect_lang(text) == LANG_OF[alang],
            "visible_tokens": vis.get(d["_name"], ""),
            "non_visible_tokens": (d["output_tokens"] - vis[d["_name"]]) if d["_name"] in vis else "",
            "response_chars": len(text), "stop_reason": d.get("stop_reason") or "",
            "wall_s": d.get("wall_s", ""),
        })
    if not rows:
        print("Nincs pontozható eredmény.")
        return
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} sor -> {out}")


if __name__ == "__main__":
    main()
