import csv
import glob
import json
import os
import re
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE, "..", "data", "raw")
CHARTS_DIR = os.path.join(BASE, "..", "data", "charts")
RESULTS_PATH = os.path.join(BASE, "..", "data", "results.csv")


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


def extract_number(text):
    cleaned = text.replace(" ", " ")
    match = re.search(r"-?\d+(?:[.,]\d+)?", cleaned)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def score_numeric(expected, given_text, tolerance_pct):
    given_num = extract_number(given_text)
    if given_num is None:
        return 0, 0, given_num
    exact = int(abs(given_num - expected) < 1e-9)
    if expected == 0:
        within_tol = int(abs(given_num) < 1e-6)
    else:
        within_tol = int(abs(given_num - expected) / abs(expected) * 100 <= tolerance_pct)
    return exact, within_tol, given_num


def score_label(expected, given_text):
    match = int(normalize(str(expected)) in normalize(given_text))
    return match, match


def score_chart(raw_path, ground_truth_by_id):
    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)

    chart_id = raw["chart_id"]
    model_alias = raw["model_alias"]
    truth = ground_truth_by_id[chart_id]

    answers = None if raw.get("is_error") else parse_answers(raw.get("result", ""))

    rows = []
    for q in truth["questions"]:
        given = answers.get(q["id"], "") if answers is not None else ""
        if q["kind"] == "extremum":
            exact, within_tol = score_label(q["expected_answer"], given)
            given_num = None
        else:
            exact, within_tol, given_num = score_numeric(q["expected_answer"], given, q["tolerance_pct"] or 5)
        rows.append({
            "chart_id": chart_id,
            "chart_type": truth["chart_type"],
            "level": truth["level"],
            "repeat": truth["repeat"],
            "condition": truth.get("condition", "image"),
            "model_alias": model_alias,
            "question_id": q["id"],
            "question_kind": q["kind"],
            "expected_answer": q["expected_answer"],
            "given_answer": given,
            "exact_match": exact,
            "tolerance_match": within_tol,
            "parse_ok": int(answers is not None),
        })
    return rows


def main():
    ground_truth = json.load(open(os.path.join(CHARTS_DIR, "ground_truth.json"), encoding="utf-8"))
    ground_truth_by_id = {e["chart_id"]: e for e in ground_truth}

    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.json")))
    if not raw_files:
        print("Nincs feldolgozható fájl a data/raw/-ban - futtasd előbb a run_test.sh-t.")
        return

    all_rows = []
    n_parse_fail = 0
    for raw_path in raw_files:
        rows = score_chart(raw_path, ground_truth_by_id)
        all_rows.extend(rows)
        if rows and rows[0]["parse_ok"] == 0:
            n_parse_fail += 1
            print(f"[warn] JSON-parse sikertelen: {os.path.basename(raw_path)}")

    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    total = len(all_rows)
    exact = sum(r["exact_match"] for r in all_rows)
    tol = sum(r["tolerance_match"] for r in all_rows)
    print(f"{len(raw_files)} hívás feldolgozva ({n_parse_fail} parse-hiba), {total} kérdés összesen")
    print(f"Egzakt egyezés: {exact}/{total} = {exact/total:.1%}")
    print(f"Tolerancián belüli egyezés: {tol}/{total} = {tol/total:.1%}")
    print(f"Kimenet: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
