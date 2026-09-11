import json
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

BASE = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE, "..", "data", "charts")
PROMPTS_DIR = os.path.join(BASE, "..", "data", "prompts")
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)

CHART_TYPES = ["bar", "line", "scatter"]
REPEATS_BY_LEVEL = {1: [1, 2], 2: [1, 2], 3: [1, 2], 4: [1, 2], 5: [1, 2, 3, 4, 5]}
TEXT_CONTROL_LEVELS = [4, 5]
TEXT_CONTROL_REPEATS = [1, 2]

LEVELS = [
    {"level": 1, "n_points": 4, "decimals": 0, "n_series": 1,
     "colors": ["#2a78d6"], "value_range": (10, 100)},
    {"level": 2, "n_points": 7, "decimals": 0, "n_series": 2,
     "colors": ["#2a78d6", "#eb6834"], "value_range": (10, 100)},
    {"level": 3, "n_points": 11, "decimals": 1, "n_series": 3,
     "colors": ["#2a78d6", "#1baf7a", "#008300"], "value_range": (10, 100)},
    {"level": 4, "n_points": 16, "decimals": 2, "n_series": 3,
     "colors": ["#2a5f9e", "#2a78d6", "#4a90e0"], "value_range": (10, 100)},
    {"level": 5, "n_points": 24, "decimals": 2, "n_series": 4,
     "colors": ["#1c4d82", "#2a5f9e", "#2a78d6", "#4a90e0"], "value_range": (10, 100)},
]

SERIES_NAMES = ["A minta", "B minta", "C minta", "D minta"]
Y_LABEL = "Mért feszültség (V)"


def gen_series_values(cfg, rng):
    lo, hi = cfg["value_range"]
    series = []
    for _ in range(cfg["n_series"]):
        vals = [round(rng.uniform(lo, hi), cfg["decimals"]) for _ in range(cfg["n_points"])]
        series.append(vals)
    return series


def style_axes(ax):
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def make_bar(cfg, rng):
    x_labels = [f"{i+1}. mérés" for i in range(cfg["n_points"])]
    series = gen_series_values(cfg, rng)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    n_series = cfg["n_series"]
    width = 0.8 / n_series
    x = range(cfg["n_points"])
    for s_idx, vals in enumerate(series):
        offsets = [xi + (s_idx - (n_series - 1) / 2) * width for xi in x]
        ax.bar(offsets, vals, width=width, color=cfg["colors"][s_idx],
               label=SERIES_NAMES[s_idx] if n_series > 1 else None)
    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels, rotation=45 if cfg["n_points"] > 8 else 0, ha="right" if cfg["n_points"] > 8 else "center")
    ax.set_ylabel(Y_LABEL)
    if n_series > 1:
        ax.legend()
    style_axes(ax)
    fig.tight_layout()
    return fig, series, x_labels


def make_line(cfg, rng):
    tick_labels = [f"{i+1}" for i in range(cfg["n_points"])]
    x_labels = [f"{i+1}. mérés" for i in range(cfg["n_points"])]
    series = gen_series_values(cfg, rng)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = range(cfg["n_points"])
    for s_idx, vals in enumerate(series):
        ax.plot(x, vals, "-o", color=cfg["colors"][s_idx], linewidth=2, markersize=5,
                label=SERIES_NAMES[s_idx] if cfg["n_series"] > 1 else None)
    ax.set_xlabel("Mérés sorszáma")
    ax.set_ylabel(Y_LABEL)
    ax.set_xticks(list(x))
    ax.set_xticklabels(tick_labels)
    if cfg["n_series"] > 1:
        ax.legend()
    style_axes(ax)
    fig.tight_layout()
    return fig, series, x_labels


def make_scatter(cfg, rng):
    x_labels = None
    series = []
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for s_idx in range(cfg["n_series"]):
        lo, hi = cfg["value_range"]
        xs = [round(rng.uniform(0, 50), cfg["decimals"]) for _ in range(cfg["n_points"])]
        ys = [round(rng.uniform(lo, hi), cfg["decimals"]) for _ in range(cfg["n_points"])]
        ax.scatter(xs, ys, color=cfg["colors"][s_idx], s=40,
                   label=SERIES_NAMES[s_idx] if cfg["n_series"] > 1 else None)
        for p_idx, (px, py) in enumerate(zip(xs, ys)):
            ax.annotate(str(p_idx + 1), (px, py), textcoords="offset points",
                        xytext=(5, 5), fontsize=7, color=cfg["colors"][s_idx])
        series.append(list(zip(xs, ys)))
    ax.set_xlabel("Idő (s)")
    ax.set_ylabel(Y_LABEL)
    if cfg["n_series"] > 1:
        ax.legend()
    style_axes(ax)
    fig.tight_layout()
    return fig, series, x_labels


def build_questions_bar_line(cfg, series, x_labels, chart_type, rng):
    n_series, n_points = cfg["n_series"], cfg["n_points"]
    s1 = rng.randrange(n_series)
    p1 = rng.randrange(n_points)
    q1_val = series[s1][p1]
    label1 = f"{SERIES_NAMES[s1]}, {x_labels[p1]}" if n_series > 1 else x_labels[p1]

    s2 = rng.randrange(n_series)
    p2 = rng.randrange(n_points)
    while (s2, p2) == (s1, p1):
        s2 = rng.randrange(n_series)
        p2 = rng.randrange(n_points)
    q2_val = round(abs(series[s1][p1] - series[s2][p2]), cfg["decimals"] + 1)
    label2a = f"{SERIES_NAMES[s1]}, {x_labels[p1]}" if n_series > 1 else x_labels[p1]
    label2b = f"{SERIES_NAMES[s2]}, {x_labels[p2]}" if n_series > 1 else x_labels[p2]

    s3 = rng.randrange(n_series)
    max_idx = max(range(n_points), key=lambda i: series[s3][i])
    max_label = f"{SERIES_NAMES[s3]}, {x_labels[max_idx]}" if n_series > 1 else x_labels[max_idx]

    s4 = rng.randrange(n_series)
    avg_val = round(sum(series[s4]) / n_points, cfg["decimals"] + 1)
    avg_label = SERIES_NAMES[s4] if n_series > 1 else "az összes minta"

    return [
        {"id": 1, "kind": "exact_value",
         "question": f"Mennyi a mért érték itt: {label1}?",
         "expected_answer": q1_val, "tolerance_pct": 5},
        {"id": 2, "kind": "difference",
         "question": f"Mennyivel tér el egymástól a következő két érték: {label2a} és {label2b}?",
         "expected_answer": q2_val, "tolerance_pct": 8},
        {"id": 3, "kind": "extremum",
         "question": "Melyik ponton (minta/mérés) a legnagyobb az érték a diagramon" + (f" a(z) {SERIES_NAMES[s3]} sorozatban?" if n_series > 1 else "?"),
         "expected_answer": x_labels[max_idx], "tolerance_pct": None},
        {"id": 4, "kind": "aggregate",
         "question": f"Mennyi {avg_label} értékeinek átlaga a diagramon?",
         "expected_answer": avg_val, "tolerance_pct": 5},
    ]


def build_questions_scatter(cfg, series, rng):
    n_series, n_points = cfg["n_series"], cfg["n_points"]
    s1 = rng.randrange(n_series)
    p1 = rng.randrange(n_points)
    x1, y1 = series[s1][p1]
    label1 = f"a(z) {SERIES_NAMES[s1]} sorozat {p1+1}. pontjának" if n_series > 1 else f"a {p1+1}. pont"

    s2 = rng.randrange(n_series)
    p2 = rng.randrange(n_points)
    while (s2, p2) == (s1, p1):
        s2 = rng.randrange(n_series)
        p2 = rng.randrange(n_points)
    x2, y2 = series[s2][p2]
    q2_val = round(abs(y1 - y2), cfg["decimals"] + 1)
    label2a = f"a(z) {SERIES_NAMES[s1]} {p1+1}. pontjának" if n_series > 1 else f"a {p1+1}. pont"
    label2b = f"a(z) {SERIES_NAMES[s2]} {p2+1}. pontjának" if n_series > 1 else f"a {p2+1}. pont"

    s3 = rng.randrange(n_series)
    max_idx = max(range(n_points), key=lambda i: series[s3][i][1])
    max_label = f"a(z) {SERIES_NAMES[s3]} sorozat pontjai" if n_series > 1 else "az adatpontok"

    s4 = rng.randrange(n_series)
    avg_val = round(sum(p[1] for p in series[s4]) / n_points, cfg["decimals"] + 1)
    avg_label = f"a(z) {SERIES_NAMES[s4]} sorozat" if n_series > 1 else "az összes pont"

    return [
        {"id": 1, "kind": "exact_value",
         "question": f"Mennyi {label1} y-értéke (a mért feszültség)?",
         "expected_answer": y1, "tolerance_pct": 5},
        {"id": 2, "kind": "difference",
         "question": f"Mennyivel tér el egymástól {label2a} és {label2b} y-értéke?",
         "expected_answer": q2_val, "tolerance_pct": 8},
        {"id": 3, "kind": "extremum",
         "question": f"Hányadik pontnak (sorszám) a legnagyobb az y-értéke {max_label} közül?",
         "expected_answer": str(max_idx + 1), "tolerance_pct": None},
        {"id": 4, "kind": "aggregate",
         "question": f"Mennyi {avg_label} pontjainak átlagos y-értéke?",
         "expected_answer": avg_val, "tolerance_pct": 5},
    ]


def build_text_table(chart_type, series, x_labels, cfg):
    lines = []
    if chart_type in ("bar", "line"):
        header = ["Mérés"] + (SERIES_NAMES[:cfg["n_series"]] if cfg["n_series"] > 1 else ["Érték"])
        lines.append(" | ".join(header))
        for i in range(cfg["n_points"]):
            row = [x_labels[i]] + [str(series[s][i]) for s in range(cfg["n_series"])]
            lines.append(" | ".join(row))
    else:
        header = ["Sorozat", "Pont sorszáma", "Idő (s)", Y_LABEL]
        lines.append(" | ".join(header))
        for s in range(cfg["n_series"]):
            sname = SERIES_NAMES[s] if cfg["n_series"] > 1 else "Adat"
            for p, (x, y) in enumerate(series[s]):
                lines.append(f"{sname} | {p + 1} | {x} | {y}")
    return "\n".join(lines)


def build_prompt_text(questions, table_text):
    lines = [
        "Az alábbi táblázat egy mérés adatait tartalmazza:",
        "",
        table_text,
        "",
        "Válaszolj KIZÁRÓLAG egy JSON tömbben, minden kérdésre külön elemmel, "
        "a kérdés sorszámával (\"id\") és a válasszal (\"answer\"). "
        "Ha nem tudod megállapítani a választ, az \"answer\" értéke legyen \"nincs adat\".",
        "Formátum példa: [{\"id\": 1, \"answer\": \"...\"}, {\"id\": 2, \"answer\": \"...\"}]",
        "",
        "Kérdések:",
    ]
    for q in questions:
        lines.append(f"{q['id']}. {q['question']}")
    lines.append("")
    lines.append("Válaszolj KIZÁRÓLAG a JSON tömbbel, más szöveg nélkül.")
    return "\n".join(lines)


def build_prompt(chart_id, questions):
    lines = [
        f"Nézd meg a mellékelt diagramot: @data/charts/{chart_id}.png",
        "Válaszolj KIZÁRÓLAG egy JSON tömbben, minden kérdésre külön elemmel, "
        "a kérdés sorszámával (\"id\") és a válasszal (\"answer\"). "
        "Ha nem tudod megállapítani a választ, az \"answer\" értéke legyen \"nincs adat\".",
        "Formátum példa: [{\"id\": 1, \"answer\": \"...\"}, {\"id\": 2, \"answer\": \"...\"}]",
        "",
        "Kérdések:",
    ]
    for q in questions:
        lines.append(f"{q['id']}. {q['question']}")
    lines.append("")
    lines.append("Válaszolj KIZÁRÓLAG a JSON tömbbel, más szöveg nélkül.")
    return "\n".join(lines)


def generate_variant(chart_type, level_cfg, repeat, condition):
    rng = random.Random(f"{chart_type}_{level_cfg['level']}_{repeat}")
    if chart_type == "bar":
        fig, series, x_labels = make_bar(level_cfg, rng)
        questions = build_questions_bar_line(level_cfg, series, x_labels, chart_type, rng)
    elif chart_type == "line":
        fig, series, x_labels = make_line(level_cfg, rng)
        questions = build_questions_bar_line(level_cfg, series, x_labels, chart_type, rng)
    else:
        fig, series, x_labels = make_scatter(level_cfg, rng)
        questions = build_questions_scatter(level_cfg, series, rng)

    base_id = f"{chart_type}_level{level_cfg['level']}_rep{repeat}"

    if condition == "image":
        chart_id = base_id
        png_path = os.path.join(CHARTS_DIR, f"{chart_id}.png")
        fig.savefig(png_path, dpi=130)
        plt.close(fig)
        prompt_text = build_prompt(chart_id, questions)
        file_ref = os.path.relpath(png_path, os.path.join(BASE, ".."))
    else:
        chart_id = f"{base_id}_text"
        plt.close(fig)
        table_text = build_text_table(chart_type, series, x_labels, level_cfg)
        prompt_text = build_prompt_text(questions, table_text)
        file_ref = None

    prompt_path = os.path.join(PROMPTS_DIR, f"{chart_id}.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    return {
        "chart_id": chart_id,
        "chart_type": chart_type,
        "level": level_cfg["level"],
        "repeat": repeat,
        "condition": condition,
        "n_points": level_cfg["n_points"],
        "n_series": level_cfg["n_series"],
        "file": file_ref,
        "questions": questions,
    }


def main():
    all_charts = []
    for chart_type in CHART_TYPES:
        for level_cfg in LEVELS:
            for repeat in REPEATS_BY_LEVEL[level_cfg["level"]]:
                entry = generate_variant(chart_type, level_cfg, repeat, "image")
                all_charts.append(entry)
                print(f"[OK] {entry['chart_id']} -> {entry['file']}")

    for chart_type in CHART_TYPES:
        for level_cfg in LEVELS:
            if level_cfg["level"] not in TEXT_CONTROL_LEVELS:
                continue
            for repeat in TEXT_CONTROL_REPEATS:
                entry = generate_variant(chart_type, level_cfg, repeat, "text")
                all_charts.append(entry)
                print(f"[OK] {entry['chart_id']} (szöveges kontroll)")

    truth_path = os.path.join(CHARTS_DIR, "ground_truth.json")
    with open(truth_path, "w", encoding="utf-8") as f:
        json.dump(all_charts, f, ensure_ascii=False, indent=2)

    print(f"\n{len(all_charts)} diagram legenerálva -> {CHARTS_DIR}")
    print(f"Ground truth: {truth_path}")


if __name__ == "__main__":
    main()
