#!/usr/bin/env python3
"""A Költségvetés-táblázat forgatókönyv kiértékelése.

Beolvassa a data/budget/raw/ mappában lévő nyers hívás-eredményeket (a
run_test.sh mentette oda <task_id>__<model_alias>__<condition>.json +
opcionálisan .xlsx formában), és a ground_truth.json-hoz hasonlítva
data/budget/results.csv-t ír.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent.parent / "data" / "budget"
RAW_DIR = DATA_DIR / "raw"


def normalize(s: str) -> str:
    s = str(s).strip().lower().rstrip(":")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s


def has_formulas(wb_raw) -> bool:
    for ws in wb_raw.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    return True
    return False


def evaluate_formulas(xlsx_path: Path) -> dict:
    """{(SHEET_NÉV_NAGYBETŰVEL, cellahivatkozás): kiszámolt_érték} minden
    képlet-cellára. A modell (a hivatalos xlsx skill útmutatása szerint)
    gyakran valódi Excel-képletet ír (pl. SUMIF), nem kiszámolt literál
    értéket -- ez helyes, best-practice táblázatkészítés, de az openpyxl
    data_only=True módja NEM számolja ki a képleteket, csak egy korábban
    Excel/LibreOffice által elmentett gyorsítótárazott értéket olvasna
    vissza, ami egy szkriptből (nem valódi táblázatkezelőből) mentett
    fájlnál sosincs jelen -- emiatt e nélkül minden formulás cella
    "üresnek" látszana, és a skill-feltétel indokolatlanul rosszabb
    pontszámot kapna, mint a szöveges/hardcode-olt noskill-feltétel."""
    import formulas
    xl = formulas.ExcelModel().loads(str(xlsx_path)).finish()
    sol = xl.calculate()
    out = {}
    for key, rng in sol.items():
        m = re.match(r"^'\[[^\]]+\]([^']*)'!([A-Z]+\d+)$", key)
        if not m:
            continue
        sheet, cell_ref = m.group(1), m.group(2)
        try:
            value = rng.value[0][0]
        except Exception:
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            out[(sheet.upper(), cell_ref)] = float(value)
    return out


def parse_numeric_text(s: str):
    """Néhány modell az összeget nem szám típusú, hanem szöveges cellába írja,
    ezres-elválasztóval (pl. "32,600.00" vagy "-85,150.00"). Ha a szöveg
    kizárólag számjegyekből, ezres-elválasztóból, tizedespontból és
    esetleges mínuszjelből áll, számmá alakítjuk -- egyébként None (pl. egy
    heti bontás fejléce, "1. hét", nem szám)."""
    s = s.strip().replace(" ", "")
    if re.fullmatch(r"-?[\d,]+(\.\d+)?", s) and any(ch.isdigit() for ch in s):
        try:
            return float(s.replace(",", ""))
        except ValueError:
            return None
    return None


def extract_labeled_numbers(xlsx_path: Path) -> list:
    """[(sheet, row, normalized_label, value), ...] -- minden szöveges cella és a
    tőle jobbra eső első számértékű (vagy számra kiértékelhető képletű) cella
    párja, soronként."""
    wb_raw = openpyxl.load_workbook(xlsx_path, data_only=False)
    wb_values = openpyxl.load_workbook(xlsx_path, data_only=True)

    formula_lookup = {}
    if has_formulas(wb_raw):
        try:
            formula_lookup = evaluate_formulas(xlsx_path)
        except Exception:
            formula_lookup = {}

    pairs = []
    for ws_raw, ws_val in zip(wb_raw.worksheets, wb_values.worksheets):
        for row_raw, row_val in zip(ws_raw.iter_rows(), ws_val.iter_rows()):
            for cell_raw, cell_val in zip(row_raw, row_val):
                if isinstance(cell_raw.value, str) and cell_raw.value.strip() and not cell_raw.value.startswith("="):
                    label = normalize(cell_raw.value)
                    # Az UTOLSÓ számértékű cellát vesszük a sorban, nem az
                    # elsőt: az 5. szinten (heti bontás) a modellek gyakran
                    # [címke, 1.hét, 2.hét, 3.hét, 4.hét, Összesen] alakú
                    # sorokat írnak -- az első szám (1. hét) sokszor 0 vagy
                    # részösszeg, a valódi kategória-összeg a sor végén,
                    # az "Összesen" oszlopban van. Egyetlen számot tartalmazó
                    # soroknál (ami az 1-4. szinten a jellemző) ez ugyanazt
                    # az eredményt adja, mint az első számé.
                    row_value = None
                    for other_raw, other_val in zip(row_raw, row_val):
                        if other_raw.column <= cell_raw.column:
                            continue
                        value = None
                        if isinstance(other_raw.value, str) and other_raw.value.startswith("="):
                            value = formula_lookup.get((ws_raw.title.upper(), other_raw.coordinate))
                        elif isinstance(other_val.value, (int, float)) and not isinstance(other_val.value, bool):
                            value = other_val.value
                        elif isinstance(other_val.value, str):
                            value = parse_numeric_text(other_val.value)
                        if value is not None:
                            row_value = value
                    if row_value is not None:
                        pairs.append((ws_raw.title, cell_raw.row, label, row_value))
    return pairs


def find_value_for_label(pairs: list, target_label: str):
    """A célcímkéhez tartozó legvalószínűbb érték: az összesítő jellegű
    munkalapokat (nevükben "össze"/"summ") előnyben részesíti a nyers
    tranzakció-listás munkalapokkal szemben, mert egy címke (pl. egy
    kategórianév) több helyen is előfordulhat -- a tranzakciólistában
    egyetlen tétel soraként is, nem csak az összesítésben. Egy adott
    részhalmazon belül az utolsó előfordulás nyer (az összesítő tábla
    jellemzően a lista alatt/után áll)."""
    target = normalize(target_label)
    summary_pairs = [p for p in pairs if "ossze" in normalize(p[0]) or "summ" in normalize(p[0])]
    other_pairs = [p for p in pairs if p not in summary_pairs]

    for subset in (summary_pairs, other_pairs):
        matches = [v for _, _, label, v in subset if label == target]
        if matches:
            return matches[-1]
    for subset in (summary_pairs, other_pairs):
        matches = [v for _, _, label, v in subset if target in label or label in target]
        if matches:
            return matches[-1]
    return None


def score_task(task: dict, model_alias: str, condition: str) -> dict:
    task_id = task["task_id"]
    base = RAW_DIR / f"{task_id}__{model_alias}__{condition}"
    json_path = base.with_suffix(".json")
    xlsx_path = base.with_suffix(".xlsx")

    row = {
        "task_id": task_id, "level": task["level"], "repeat": task["repeat"],
        "condition": condition, "model_alias": model_alias,
        "category_totals_correct": False, "balance_correct": False,
        "weekly_max_correct": "" if task["weekly_max_category"] is None else False,
        "n_categories_total": len(task["category_totals"]),
        "n_categories_correct": 0,
        "parse_ok": False,
    }

    result_text = ""
    if json_path.exists():
        try:
            call = json.loads(json_path.read_text(encoding="utf-8"))
            result_text = call.get("result", "") or ""
        except (json.JSONDecodeError, OSError):
            pass

    if not xlsx_path.exists():
        return row

    try:
        pairs = extract_labeled_numbers(xlsx_path)
    except Exception:
        return row

    row["parse_ok"] = True

    # Abszolút érték: a prompt sosem kért előjeles kategória-összeget -- a
    # ground truth a kiadás-kategóriákat a saját egyenleg-számításához tárolja
    # negatívan, de egy táblázatban ésszerű ugyanezt "mennyit költöttem"
    # pozitív számként megjeleníteni. Csak a záró egyenleg (lentebb) marad
    # előjeles összevetés, mert az valódi nettó érték.
    # ±1 Ft tolerancia: csak lebegőpontos kerekítési maradékra, nem valódi
    # bizonytalanságra -- a megosztott költségeknél a ground truth immár
    # forintra (nem 50 Ft-ra) kerekít, ugyanúgy, ahogy egy modell egy pontos
    # osztás eredményét kerekítené.
    n_correct = 0
    for category, expected in task["category_totals"].items():
        found = find_value_for_label(pairs, category)
        if found is not None and abs(abs(found) - abs(expected)) <= 1:
            n_correct += 1
    row["n_categories_correct"] = n_correct
    row["category_totals_correct"] = n_correct == row["n_categories_total"]

    balance_found = find_value_for_label(pairs, "egyenleg")
    if balance_found is None:
        balance_found = find_value_for_label(pairs, "balance")
    row["balance_correct"] = balance_found is not None and abs(balance_found - task["balance"]) <= 1

    if task["weekly_max_category"] is not None:
        weeks_mentioned = set(int(m) for m in re.findall(r"(\d)\s*\.?\s*h[ée]t", result_text.lower()))
        row["weekly_max_correct"] = bool(weeks_mentioned & set(task["weekly_max_category"]))

    return row


def main():
    ground_truth = {t["task_id"]: t for t in json.loads((DATA_DIR / "ground_truth.json").read_text(encoding="utf-8"))}
    fieldnames = ["task_id", "level", "repeat", "condition", "model_alias",
                  "category_totals_correct", "balance_correct", "weekly_max_correct",
                  "n_categories_total", "n_categories_correct", "parse_ok"]
    rows = []
    seen = set()
    for f in sorted(RAW_DIR.glob("*.json")):
        stem = f.stem  # task_id__model_alias__condition
        parts = stem.split("__")
        if len(parts) != 3:
            continue
        task_id, model_alias, condition = parts
        if task_id not in ground_truth or stem in seen:
            continue
        seen.add(stem)
        rows.append(score_task(ground_truth[task_id], model_alias, condition))

    out_path = DATA_DIR / "results.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} sor -> {out_path}")


if __name__ == "__main__":
    main()
