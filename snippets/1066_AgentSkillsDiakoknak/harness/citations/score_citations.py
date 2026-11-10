#!/usr/bin/env python3
"""A Hivatkozásjegyzék forgatókönyv kiértékelése.

Beolvassa a data/citations/raw/ mappában lévő nyers hívás-eredményeket
(<task_id>__<model_alias>__<condition>.json + opcionálisan .docx), és a
ground_truth.json expected_formatted listájával összevetve
data/citations/results.csv-t ír. Egy sor = egy forrás egy hívásban.
"""
import csv
import difflib
import json
import re
from pathlib import Path

from docx import Document

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent.parent / "data" / "citations"
RAW_DIR = DATA_DIR / "raw"

CITATION_LIKE = re.compile(r"\(\d{4}")


def normalize_text(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    s = s.replace("–", "-").replace("—", "-")
    return s


def extract_citation_paragraphs(docx_path: Path) -> list:
    doc = Document(str(docx_path))
    out = []
    for p in doc.paragraphs:
        text = normalize_text(p.text)
        if text and CITATION_LIKE.search(text):
            out.append(text)
    return out


def greedy_pair(expected: list, produced: list) -> dict:
    """expected_index -> produced_index a legjobb hasonlóság szerint, egy-egyértékűen."""
    candidates = []
    for i, e in enumerate(expected):
        for j, p in enumerate(produced):
            ratio = difflib.SequenceMatcher(None, e, p).ratio()
            candidates.append((ratio, i, j))
    candidates.sort(reverse=True)
    used_e, used_p = set(), set()
    pairing = {}
    for ratio, i, j in candidates:
        if i in used_e or j in used_p:
            continue
        pairing[i] = j
        used_e.add(i)
        used_p.add(j)
    return pairing


def score_task(task: dict, model_alias: str, condition: str) -> list:
    task_id = task["task_id"]
    base = RAW_DIR / f"{task_id}__{model_alias}__{condition}"
    docx_path = base.with_suffix(".docx")
    expected = [normalize_text(e) for e in task["expected_formatted"]]
    n_expected = len(expected)

    rows = []
    if not docx_path.exists():
        for i in range(n_expected):
            rows.append({
                "task_id": task_id, "level": task["level"], "repeat": task["repeat"],
                "condition": condition, "model_alias": model_alias, "source_index": i,
                "formatting_correct": False, "order_correct": False,
                "completeness_correct": False, "parse_ok": False,
            })
        return rows

    try:
        produced = extract_citation_paragraphs(docx_path)
        parse_ok = True
    except Exception:
        produced = []
        parse_ok = False

    pairing = greedy_pair(expected, produced)  # expected_idx -> produced_idx
    formatting_correct = {}
    for i, e in enumerate(expected):
        j = pairing.get(i)
        formatting_correct[i] = j is not None and produced[j] == e

    completeness_correct = (len(produced) == n_expected) and (len(pairing) == n_expected)

    # order_correct: a produced sorrendben (doc-index szerint) az expected_idx-ek
    # sorozata legyen szigorúan növekvő -- csak akkor értelmes/igaz, ha teljes a párosítás.
    order_correct = False
    if completeness_correct:
        produced_to_expected = {j: i for i, j in pairing.items()}
        seq = [produced_to_expected[j] for j in range(len(produced)) if j in produced_to_expected]
        order_correct = seq == sorted(seq)

    for i in range(n_expected):
        rows.append({
            "task_id": task_id, "level": task["level"], "repeat": task["repeat"],
            "condition": condition, "model_alias": model_alias, "source_index": i,
            "formatting_correct": formatting_correct.get(i, False),
            "order_correct": order_correct,
            "completeness_correct": completeness_correct,
            "parse_ok": parse_ok,
        })
    return rows


def main():
    ground_truth = {t["task_id"]: t for t in json.loads((DATA_DIR / "ground_truth.json").read_text(encoding="utf-8"))}
    fieldnames = ["task_id", "level", "repeat", "condition", "model_alias", "source_index",
                  "formatting_correct", "order_correct", "completeness_correct", "parse_ok"]
    rows = []
    seen = set()
    for f in sorted(RAW_DIR.glob("*.json")):
        stem = f.stem
        parts = stem.split("__")
        if len(parts) != 3:
            continue
        task_id, model_alias, condition = parts
        if task_id not in ground_truth or stem in seen:
            continue
        seen.add(stem)
        rows.extend(score_task(ground_truth[task_id], model_alias, condition))

    out_path = DATA_DIR / "results.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} sor -> {out_path}")


if __name__ == "__main__":
    main()
