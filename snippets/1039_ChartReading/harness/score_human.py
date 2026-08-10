import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import score_numeric

BASE = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE, "..", "data", "charts")
WORKSHEET_PATH = os.path.join(BASE, "..", "data", "human_worksheet.md")
RESULTS_PATH = os.path.join(BASE, "..", "data", "human_results.csv")


def parse_worksheet():
    text = open(WORKSHEET_PATH, encoding="utf-8").read()
    blocks = re.split(r"^## ", text, flags=re.M)[1:]
    answers = {}
    for b in blocks:
        chart_id = b.split()[0]
        qs = re.findall(r"^(\d)\. .*?\n   Válasz: (.*)$", b, re.M)
        answers[chart_id] = {int(qid): ans.strip() for qid, ans in qs}
    return answers


def extract_leading_int(text):
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def score_extremum(expected, given_text):
    exp_num = extract_leading_int(str(expected))
    given_num = extract_leading_int(given_text)
    match = int(exp_num is not None and exp_num == given_num)
    return match, match


def main():
    ground_truth = json.load(open(os.path.join(CHARTS_DIR, "ground_truth.json"), encoding="utf-8"))
    ground_truth_by_id = {e["chart_id"]: e for e in ground_truth if e["condition"] == "image"}
    worksheet_answers = parse_worksheet()

    rows = []
    for chart_id, truth in ground_truth_by_id.items():
        given_by_id = worksheet_answers.get(chart_id, {})
        for q in truth["questions"]:
            if q["kind"] == "aggregate":
                continue
            given = given_by_id.get(q["id"], "")
            if q["kind"] == "extremum":
                exact, within_tol = score_extremum(q["expected_answer"], given)
            else:
                exact, within_tol, _ = score_numeric(q["expected_answer"], given, q["tolerance_pct"] or 5)
            rows.append({
                "chart_id": chart_id,
                "chart_type": truth["chart_type"],
                "level": truth["level"],
                "repeat": truth["repeat"],
                "condition": "image",
                "model_alias": "human",
                "question_id": q["id"],
                "question_kind": q["kind"],
                "expected_answer": q["expected_answer"],
                "given_answer": given,
                "exact_match": exact,
                "tolerance_match": within_tol,
                "parse_ok": 1,
            })

    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    exact = sum(r["exact_match"] for r in rows)
    tol = sum(r["tolerance_match"] for r in rows)
    print(f"{total} kérdés összesen")
    print(f"Egzakt egyezés: {exact}/{total} = {exact/total:.1%}")
    print(f"Tolerancián belüli egyezés: {tol}/{total} = {tol/total:.1%}")
    print(f"Kimenet: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
