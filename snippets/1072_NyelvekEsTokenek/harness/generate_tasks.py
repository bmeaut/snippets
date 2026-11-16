#!/usr/bin/env python3
"""A B rész feladatainak, promptjainak és helyes válaszainak generálása.

A feladatok sablonokból és véletlen számokból készülnek, szintén rögzített,
string-kulcsos véletlenszám-generátorral (`random.Random(f"nyelv_{sablon}_{sorszam}")`,
a beépített `hash()` használata tilos). A helyes választ ugyanabból az adatból számolja,
amiből a promptot állítja össze.

Kimenet:
    data/tasks/ground_truth.json       (feladatonként: paraméterek, helyes válasz)
    data/tasks/prompts/<task_id>__<valtozat>.txt
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATES = ROOT / "data" / "templates"
OUT_DIR = ROOT / "data" / "tasks"

LANGS = ["hu", "de", "ja"]
LANG_NAME_EN = {"hu": "Hungarian", "de": "German", "ja": "Japanese"}
REPEATS = 3  # feladat / sablon a számtani és a kinyerős kategóriában


def distinct(rng, lo, hi, n=3):
    return rng.sample(range(lo, hi + 1), n)


def spec(tid, rng):
    """(paraméterek, helyes válasz) a sablon azonosítója szerint. A bemeneti számok egész számok, 2 és 999 között."""
    if tid == "N01":
        a, b = rng.randint(20, 90), rng.randint(10, 60)
        c = rng.randint(5, min(40, a + b - 1))
        return {"A": a, "B": b, "C": c}, a + b - c
    if tid == "N02":
        a, b = rng.randint(20, 80), rng.randint(3, 9)
        c = rng.randint(10, min(300, a * b - 1))
        return {"A": a, "B": b, "C": c}, a * b - c
    if tid == "N03":
        a, b = rng.randint(5, 40), rng.randint(3, 9)
        c = a * b + rng.randint(10, 100)
        return {"A": a, "B": b, "C": c}, c - a * b
    if tid == "N04":
        a, b = rng.randint(6, 24), rng.randint(3, 12)
        c = rng.randint(5, a - 1)
        return {"A": a, "B": b, "C": c}, a * b + c
    if tid == "N05":
        a = rng.randint(30, 90)
        b, c = rng.randint(5, a // 3), rng.randint(5, a // 3)
        return {"A": a, "B": b, "C": c}, a - b - c
    if tid == "N06":
        c, k = rng.randint(4, 12), rng.randint(5, 30)
        total = c * k
        a = rng.randint(20, total - 5)
        return {"A": a, "B": total - a, "C": c}, k
    if tid == "N07":
        a = rng.randint(200, 600)
        b, c = rng.randint(20, a // 2), rng.randint(3, 12)
        return {"A": a, "B": b, "C": c}, (a - b) * c
    if tid == "N08":
        a, b = rng.randint(20, 80), rng.randint(4, 12)
        c = rng.randint(5, 40)
        return {"A": a, "B": b, "C": c}, a * b - c
    if tid == "N09":
        a, b = rng.randrange(20, 101, 2), rng.randint(5, 50)
        return {"A": a, "B": b}, a // 2 + b
    if tid == "N10":
        a, b, c = distinct(rng, 20, 300)
        return {"A": a, "B": b, "C": c}, a + b + c
    if tid == "H01":
        a, b, c, d = rng.randint(8, 45), rng.randint(2, 9), rng.randint(3, 12), rng.randint(5, 30)
        return {"A": a, "B": b, "C": c, "D": d}, 1000 - (a * c + b * d)
    if tid == "H02":
        b = rng.randint(40, 120)
        c, d = rng.randint(10, b - 5), rng.randint(5, 15)
        a = rng.randint(d * (b - c) + 20, d * (b - c) + 400)
        return {"A": a, "B": b, "C": c, "D": d}, a - d * (b - c)
    if tid == "H03":
        a, b, c = rng.randint(25, 95), rng.randint(6, 12), rng.randint(5, 20)
        d = rng.randint(20, 300)
        return {"A": a, "B": b, "C": c, "D": d}, a * b * c - d
    if tid == "H04":
        a, b, c, d = rng.randint(45, 140), rng.randint(2, 9), rng.randint(45, 140), rng.randint(2, 9)
        return {"A": a, "B": b, "C": c, "D": d}, a * b + c * d
    if tid == "H05":
        a = rng.randint(400, 900)
        b = rng.randint(40, 200)
        c, d = rng.randint(20, b), rng.randint(30, 150)
        return {"A": a, "B": b, "C": c, "D": d}, a - b + c - d
    if tid == "H06":
        a = rng.randint(60, 120)
        b = rng.randint(20, 40)
        c = rng.randint(5, b)
        d = rng.randint(5, min(40, a - (b - c) - 1))
        return {"A": a, "B": b, "C": c, "D": d}, a - (b - c + d)
    if tid == "H07":
        b, c = rng.randint(3, 9), rng.randint(3, 9)
        a = rng.randint(30, min(120, 900 // (b + c)))
        d = rng.randint(a * (b + c) + 50, min(999, a * (b + c) + 300))
        return {"A": a, "B": b, "C": c, "D": d}, d - a * (b + c)
    if tid == "H08":
        a, b = rng.randint(25, 60), rng.randint(12, 30)
        c = rng.randint(20, 120)
        d = rng.randint(30, 150)
        return {"A": a, "B": b, "C": c, "D": d}, a * b - c - d
    if tid == "H09":
        a, b = rng.randint(8, 30), rng.randint(10, 60)
        c = rng.randint(2, a - 1)
        d = rng.randint(5, 25)
        return {"A": a, "B": b, "C": c, "D": d}, a * b + c * d
    if tid == "H10":
        a, b, c = rng.randint(40, 150), rng.randint(40, 150), rng.randint(40, 150)
        d = rng.randint(a + b + c + 20, min(999, a + b + c + 200))
        return {"A": a, "B": b, "C": c, "D": d}, d - a - b - c
    if tid.startswith("E"):
        a, b, c = distinct(rng, 20, 400)
        vals = {"A": a, "B": b, "C": c}
        answers = {"E01": b, "E02": b, "E03": c, "E04": max(a, b, c), "E05": min(a, b, c),
                   "E06": b, "E07": a, "E08": sorted([a, b, c])[1], "E09": max(a, b, c), "E10": c}
        return vals, answers[tid]
    raise KeyError(tid)


def load_texts():
    """Nyelvenként a sablonok szövege (helykitöltőkkel), a kézi javítások alkalmazásával."""
    src = json.loads((TEMPLATES / "source_en.json").read_text(encoding="utf-8"))
    tr = json.loads((TEMPLATES / "translated.json").read_text(encoding="utf-8"))
    ov_path = TEMPLATES / "overrides.json"
    ov = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.exists() else {}
    texts = {"en": {}, "hu": {}, "de": {}, "ja": {}}
    for group in ("numeric", "hard", "extraction", "open", "instructions"):
        for it in src[group]:
            i = it["id"]
            en = it["text"].replace("<x>", "").replace("</x>", "")
            texts["en"][i] = en
            for lang in LANGS:
                t = ov.get(i, {}).get(lang) or tr[i][lang]["deepl"]
                texts[lang][i] = t
    return src, texts


def fill(text, params):
    for k, v in params.items():
        text = text.replace("{" + k + "}", str(v))
    assert "{" not in text, text
    return text


def build():
    src, texts = load_texts()
    tasks = []
    for group, cat in (("numeric", "szamtani"), ("hard", "nehez"), ("extraction", "kinyeres")):
        for it in src[group]:
            for k in range(1, REPEATS + 1):
                rng = random.Random(f"nyelv_{it['id']}_{k}")
                params, answer = spec(it["id"], rng)
                tasks.append({"task_id": f"{it['id']}_{k}", "category": cat, "template_id": it["id"],
                              "params": params, "answer": answer})
    for it in src["open"]:
        tasks.append({"task_id": f"{it['id']}_1", "category": "nyitott", "template_id": it["id"],
                      "params": {}, "answer": None})

    for t in tasks:
        tid, params = t["template_id"], t["params"]
        has_answer = t["category"] != "nyitott"
        prompts = {}

        def compose(lang_q, instr_lang, answer_line_lang, extra_lang_instr):
            q = fill(texts[lang_q][tid], params)
            parts = [q]
            if has_answer:
                parts.append(texts[answer_line_lang]["I_ANSWER_LINE"])
            if extra_lang_instr:
                parts.append(extra_lang_instr)
            return "\n".join(parts)

        prompts["EN_EN"] = compose("en", "en", "en", None)
        for lang in LANGS:
            L = lang.upper()
            prompts[f"{L}_{L}"] = compose(lang, lang, lang, None)
            prompts[f"{L}_EN"] = compose(lang, lang, lang, texts[lang]["I_ANSWER_ENGLISH"])
            prompts[f"EN_{L}"] = compose("en", "en", "en", f"Answer in {LANG_NAME_EN[lang]}.")
        t["variants"] = sorted(prompts)
        t["_prompts"] = prompts
    return tasks


def main():
    tasks = build()
    pdir = OUT_DIR / "prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    for old in pdir.glob("*.txt"):
        old.unlink()
    gt = []
    allp = {}
    for t in tasks:
        for v, text in t.pop("_prompts").items():
            (pdir / f"{t['task_id']}__{v}.txt").write_text(text + "\n", encoding="utf-8")
            allp[f"{t['task_id']}__{v}"] = text
        gt.append(t)
    # A publikált, csomagolt változat: egyetlen fájl (a prompts/ mappa újragenerálható).
    (OUT_DIR / "prompts.json").write_text(json.dumps(allp, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "ground_truth.json").write_text(json.dumps(gt, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(gt)} feladat, {len(list(pdir.glob('*.txt')))} prompt -> {OUT_DIR}")


if __name__ == "__main__":
    main()
