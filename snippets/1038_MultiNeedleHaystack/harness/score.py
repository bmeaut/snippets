import csv
import glob
import json
import os
import re
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE, "..", "data", "raw")
PROMPT_DIR = os.path.join(BASE, "..", "data", "prompts")
RESULTS_PATH = os.path.join(BASE, "..", "data", "results.csv")
CELLS_PATH = os.path.join(BASE, "..", "data", "cells.csv")


def normalize(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def strip_code_fence(text):
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def parse_answers(result_text):
    cleaned = strip_code_fence(result_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    answers = {}
    for item in parsed:
        if isinstance(item, dict) and "id" in item and "answer" in item:
            answers[int(item["id"])] = str(item["answer"])
    return answers


def is_match(needle, given):
    mode = needle.get("match", "substring")
    expected = needle["expected_answer"]
    given_norm = normalize(given)
    if mode == "any":
        return any(normalize(alt) in given_norm for alt in expected)
    if mode == "all_keywords":
        return all(normalize(kw) in given_norm for kw in expected)
    return normalize(expected) in given_norm


def position_third(frac):
    if frac < 1 / 3:
        return "eleje"
    if frac < 2 / 3:
        return "kozepe"
    return "vege"


def error_reason(raw):
    if not raw.get("is_error"):
        return ""
    text = (raw.get("result") or "").lower()
    if "too long" in text:
        return "context_overflow"
    if "session limit" in text:
        return "session_limit"
    return "other_error"


def score_cell(raw_path):
    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)

    cell_id = raw["cell_id"]
    model_alias = raw["model_alias"]
    truth_path = os.path.join(PROMPT_DIR, f"{cell_id}_truth.json")
    with open(truth_path, encoding="utf-8") as f:
        truth = json.load(f)

    reason = error_reason(raw)
    answers = parse_answers(raw.get("result", "")) if not reason else None

    rows = []
    for i, needle in enumerate(truth["needles"], start=1):
        given = answers.get(i, "") if answers is not None else ""
        correct = "" if reason else int(is_match(needle, given))
        expected_display = (needle["expected_answer"] if isinstance(needle["expected_answer"], str)
                             else " / ".join(needle["expected_answer"]))
        rows.append({
            "cell_id": cell_id,
            "model_alias": model_alias,
            "context_tokens_target": truth["context_tokens_target"],
            "k": truth["k"],
            "repeat": truth["repeat"],
            "needle_id": needle["id"],
            "needle_type": needle["type"],
            "position_frac": needle["position_frac"],
            "position_third": position_third(needle["position_frac"]),
            "expected_answer": expected_display,
            "given_answer": given,
            "correct": correct,
            "parse_ok": int(answers is not None),
            "error_reason": reason,
        })

    non_error_rows = [r for r in rows if r["correct"] != ""]
    cell_summary = {
        "cell_id": cell_id,
        "model_alias": model_alias,
        "context_tokens_target": truth["context_tokens_target"],
        "k": truth["k"],
        "repeat": truth["repeat"],
        "total_cost_usd": raw.get("total_cost_usd", 0.0),
        "duration_ms": raw.get("duration_ms", 0),
        "is_error": int(bool(raw.get("is_error"))),
        "error_reason": reason,
        "parse_ok": int(answers is not None),
        "recall": (sum(r["correct"] for r in non_error_rows) / len(non_error_rows)) if non_error_rows else "",
    }
    return rows, cell_summary


def main():
    all_rows = []
    all_cells = []
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.json")))
    if not raw_files:
        print("Nincs feldolgozható fájl a data/raw/-ban - futtasd előbb a run_test.sh-t.")
        return

    n_parse_fail = 0
    n_by_reason = {}
    for raw_path in raw_files:
        rows, cell_summary = score_cell(raw_path)
        all_rows.extend(rows)
        all_cells.append(cell_summary)
        reason = cell_summary["error_reason"]
        if reason:
            n_by_reason[reason] = n_by_reason.get(reason, 0) + 1
            print(f"[{reason}] {os.path.basename(raw_path)}")
        elif cell_summary["parse_ok"] == 0:
            n_parse_fail += 1
            print(f"[warn] JSON-parse sikertelen: {os.path.basename(raw_path)}")

    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    with open(CELLS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_cells[0].keys()))
        writer.writeheader()
        writer.writerows(all_cells)

    scored_rows = [r for r in all_rows if r["correct"] != ""]
    total = len(scored_rows)
    correct = sum(r["correct"] for r in scored_rows)
    total_cost = sum(c["total_cost_usd"] for c in all_cells)
    reason_str = ", ".join(f"{v} {k}" for k, v in n_by_reason.items()) or "0 hiba"
    if total:
        print(f"{len(raw_files)} cella feldolgozva ({n_parse_fail} parse-hiba, {reason_str}), "
              f"{total} értékelt needle, recall = {correct}/{total} = {correct/total:.1%}")
    else:
        print("Nincs értékelhető needle.")
    print(f"Összköltség eddig: ${total_cost:.2f}")
    print(f"Kimenet: {RESULTS_PATH}, {CELLS_PATH}")


if __name__ == "__main__":
    main()
