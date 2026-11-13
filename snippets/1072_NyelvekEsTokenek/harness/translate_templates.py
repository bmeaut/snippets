#!/usr/bin/env python3
"""A feladatsablonok és az utasítás-mondatok lefordítása és ellenőrzése.

1. Elsődleges fordítás: DeepL API (ingyenes kulcs, a `DEEPL_API_KEY` környezeti változóból).
   A helykitöltők ({A}, {N1}, ...) és az `ANSWER:` jelölő XML-címkébe zárva, `ignore_tags`
   használatával sértetlenül maradnak.
2. Visszafordítás angolra (DeepL), hasonlóság az eredetihez (chrF).
3. Független keresztellenőrzés: NLLB-200 (helyben futó, ingyenes), a két fordítás hasonlósága.

Kimenet: data/templates/translated.json (folytatható: a kész tételeket nem fordítja újra).

Használat:
    DEEPL_API_KEY=... python3 translate_templates.py            # DeepL + visszafordítás
    python3 translate_templates.py --nllb                        # NLLB keresztellenőrzés
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "templates"
SRC = DATA / "source_en.json"
OUT = DATA / "translated.json"

LANGS = {"hu": "HU", "de": "DE", "ja": "JA"}
NLLB_CODES = {"en": "eng_Latn", "hu": "hun_Latn", "de": "deu_Latn", "ja": "jpn_Jpan"}
PLACEHOLDER = re.compile(r"\{[A-Z0-9]+\}")
# Számok és nevek, amikre a helykitöltők cserélődnek az NLLB-s összevetésnél.
NLLB_FILL = {"{A}": "111", "{B}": "222", "{C}": "333", "{D}": "444"}


def items(src):
    for group in ("numeric", "hard", "extraction", "open", "instructions"):
        for it in src[group]:
            yield it["id"], it["text"]


def mask(text):
    """Helykitöltők XML-címkébe zárása (a DeepL ne fordítsa le)."""
    return PLACEHOLDER.sub(lambda m: f"<x>{m.group(0)}</x>", text)


def unmask(text):
    return re.sub(r"</?x>", "", text)


def deepl(texts, source, target):
    key = os.environ["DEEPL_API_KEY"]
    resp = requests.post(
        "https://api-free.deepl.com/v2/translate",
        headers={"Authorization": f"DeepL-Auth-Key {key}"},
        data=dict({"text": texts, "source_lang": source, "target_lang": target,
                   "tag_handling": "xml", "ignore_tags": "x"},
                  **({"formality": "prefer_more"} if target in ("DE", "JA") else {})),
        timeout=60,
    )
    resp.raise_for_status()
    return [t["text"] for t in resp.json()["translations"]]


def placeholders_ok(src, out):
    from collections import Counter
    a = Counter(PLACEHOLDER.findall(src))
    b = Counter(PLACEHOLDER.findall(out))
    return a == b


def run_deepl():
    src = json.loads(SRC.read_text(encoding="utf-8"))
    res = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for lang, dl in LANGS.items():
        todo = [(i, t) for i, t in items(src) if lang not in res.get(i, {})]
        if not todo:
            continue
        masked = [mask(t) if "<x>" not in t else t for _, t in todo]
        fwd = deepl(masked, "EN", dl)
        time.sleep(0.5)
        back = deepl(fwd, dl, "EN-US")
        for (i, t), f, b in zip(todo, fwd, back):
            res.setdefault(i, {"en": t})[lang] = {
                "deepl": unmask(f), "back_en": unmask(b),
                "placeholders_ok": placeholders_ok(t, unmask(f)),
            }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [(i, l) for i, v in res.items() for l in LANGS if not v[l]["placeholders_ok"]]
    print("kész:", len(res), "tétel; hibás helykitöltő:", bad)


def fill(text):
    for k, v in NLLB_FILL.items():
        text = text.replace(k, v)
    return text.replace("<x>", "").replace("</x>", "")


def run_nllb():
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    res = json.loads(OUT.read_text(encoding="utf-8"))
    name = "facebook/nllb-200-distilled-600M"
    tok = AutoTokenizer.from_pretrained(name, src_lang=NLLB_CODES["en"])
    model = AutoModelForSeq2SeqLM.from_pretrained(name)
    model.eval()
    for lang in LANGS:
        ids = [i for i in res if "nllb" not in res[i][lang]]
        for k in range(0, len(ids), 8):
            batch = ids[k:k + 8]
            srcs = [fill(res[i]["en"]) for i in batch]
            enc = tok(srcs, return_tensors="pt", padding=True)
            with torch.no_grad():
                out = model.generate(**enc, forced_bos_token_id=tok.convert_tokens_to_ids(NLLB_CODES[lang]),
                                     max_new_tokens=160, num_beams=4)
            for i, o in zip(batch, tok.batch_decode(out, skip_special_tokens=True)):
                res[i][lang]["nllb"] = o
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("NLLB kész")


def run_scores():
    from sacrebleu.metrics import CHRF
    chrf = CHRF()
    res = json.loads(OUT.read_text(encoding="utf-8"))
    for i, v in res.items():
        for lang in LANGS:
            d = v[lang]
            d["chrf_back"] = round(chrf.sentence_score(fill(d["back_en"]), [fill(v["en"])]).score, 1)
            if "nllb" in d:
                d["chrf_nllb"] = round(chrf.sentence_score(fill(d["deepl"]), [d["nllb"]]).score, 1)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("chrF pontok kiszámolva")


if __name__ == "__main__":
    if "--nllb" in sys.argv:
        run_nllb()
    elif "--scores" in sys.argv:
        run_scores()
    else:
        run_deepl()
