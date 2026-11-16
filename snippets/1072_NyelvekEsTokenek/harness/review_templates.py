#!/usr/bin/env python3
"""Nyelvenként ellenőrző lapot készít a fordított sablonokból (data/templates/review_<nyelv>.md).

Minden tételnél: az angol eredeti, a ténylegesen használt szöveg (a kézi javítások után),
a DeepL fordítás, a visszafordítás, a két hasonlósági pont (chrF) és a jelölés. Jelölt,
ha a visszafordítás hasonlósága 70 alatti, vagy az NLLB-vel való egyezés a nyelv
alsó negyedében van, vagy kézi javítás készült.
"""
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "data" / "templates"
NAMES = {"hu": "magyar", "de": "német", "ja": "japán"}


def main():
    tr = json.loads((T / "translated.json").read_text(encoding="utf-8"))
    ov = json.loads((T / "overrides.json").read_text(encoding="utf-8"))
    for lang, name in NAMES.items():
        nl = sorted(v[lang]["chrf_nllb"] for v in tr.values())
        q1 = nl[len(nl) // 4]
        lines = [f"# Fordítás-ellenőrző lap: {name}\n",
                 "Jelölés: `V` = a visszafordítás hasonlósága 70 alatti, `N` = az NLLB-vel való egyezés a nyelv alsó negyedében, "
                 "`K` = kézi javítás készült (az indoklás a `overrides.json`-ban).\n",
                 "| Azonosító | Angol eredeti | Használt szöveg | DeepL | Visszafordítás | chrF (vissza) | chrF (NLLB) | Jelölés |",
                 "|---|---|---|---|---|---|---|---|"]
        for i, v in tr.items():
            d = v[lang]
            used = ov.get(i, {}).get(lang) or d["deepl"]
            flags = ("V" if d["chrf_back"] < 70 else "") + ("N" if d["chrf_nllb"] <= q1 else "") + ("K" if i in ov and lang in ov[i] else "")
            lines.append(f"| {i} | {v['en']} | {used} | {d['deepl'] if used != d['deepl'] else '(azonos)'} | {d['back_en']} | {d['chrf_back']} | {d['chrf_nllb']} | {flags} |")
        (T / f"review_{lang}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(lang, "kész, NLLB alsó negyed küszöb:", q1)


if __name__ == "__main__":
    main()
