#!/usr/bin/env python3
"""Összesítő táblák és ábrák az A és B rész nyers adataiból (az index.md-hez).

Használat (a snippet gyökeréből):
    python3 analyze.py                                   # data/a_raw + data/b_results.csv
    python3 analyze.py --b-csv data/b_pilot_results.csv --out-dir /tmp/ellenorzes   # próba
"""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
RNG = np.random.default_rng(20261103)
N_BOOT = 4000

INK, MUTED, SURFACE = "#1B1E22", "#6B7280", "#FCFBF9"
LANG_COLOR = {"HU": "#B3001B", "DE": "#2A6F97", "JA": "#E09F3E"}
LANG_NAME = {"EN": "angol", "HU": "magyar", "DE": "német", "JA": "japán"}
MODEL_LABEL = {
    "claude-haiku-5-5": "Haiku 5.5", "claude-sonnet-5-5": "Sonnet 5.5", "claude-opus-5": "Opus 5",
    "claude-sonnet-4-6": "Sonnet 4.6", "claude-haiku-4-5": "Haiku 4.5",
}
NEW_TOKENIZER = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5"]
OLD_TOKENIZER = ["claude-sonnet-4-6", "claude-haiku-4-5"]


def style_ax(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#C9C4BE")
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color="#E6E1DB", linewidth=0.8)
    ax.set_axisbelow(True)


def boot_ratio(num, den, groups, n=N_BOOT):
    """Összegek hányadosa, csoportok (csomag vagy feladat) szerinti bootstrap 95%-os CI-vel."""
    df = pd.DataFrame({"n": num, "d": den, "g": groups}).groupby("g").sum()
    gn, gd = df["n"].to_numpy(float), df["d"].to_numpy(float)
    est = gn.sum() / gd.sum()
    idx = RNG.integers(0, len(gn), size=(n, len(gn)))
    r = gn[idx].sum(axis=1) / gd[idx].sum(axis=1)
    return est, float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


# ---------------------------------------------------------------- A rész
def load_a():
    rows, base = [], {}
    import sys
    sys.path.insert(0, str(HERE / "harness"))
    import common
    for d in common.load_records("a_raw"):
        if d["_name"].endswith("__frame.json") or not d.get("ok"):
            continue
        if d["lang"] == "baseline":
            base[d["model"]] = d["input_tokens"]
        else:
            rows.append({"model": d["model"], "lang": d["lang"].upper(), "batch": d["batch"],
                         "input": d["input_tokens"], "chars": d["chars"], "bytes": d["bytes"]})
    df = pd.DataFrame(rows)
    df["net"] = df["input"] - df["model"].map(base)
    return df


def summarize_a(df):
    out = []
    models = [m for m in NEW_TOKENIZER + OLD_TOKENIZER if m in set(df["model"])]
    for m in models:
        sub = df[df["model"] == m]
        en = sub[sub["lang"] == "EN"].set_index("batch")
        for lang in ("EN", "HU", "DE", "JA"):
            cur = sub[sub["lang"] == lang].set_index("batch")
            common_b = en.index.intersection(cur.index)
            if len(common_b) == 0:
                continue
            est, lo, hi = boot_ratio(cur.loc[common_b, "net"].values, en.loc[common_b, "net"].values, common_b)
            out.append({"model": m, "lang": lang, "batches": len(common_b), "ratio": est, "ci_lo": lo, "ci_hi": hi,
                        "tokens_per_batch": cur.loc[common_b, "net"].mean(),
                        "chars_per_token": cur.loc[common_b, "chars"].sum() / cur.loc[common_b, "net"].sum(),
                        "bytes_per_token": cur.loc[common_b, "bytes"].sum() / cur.loc[common_b, "net"].sum()})
    return pd.DataFrame(out)


def tokenizer_generation(df):
    """Ugyanazon nyelv és csomag tokenszáma az új és a régi tokenizálós modelleken."""
    out = []
    for lang in ("EN", "HU", "DE", "JA"):
        piv = df[df["lang"] == lang].pivot_table(index="batch", columns="model", values="net")
        for new in NEW_TOKENIZER:
            for old in OLD_TOKENIZER:
                if new in piv and old in piv:
                    ok = piv[[new, old]].dropna()
                    if len(ok):
                        est, lo, hi = boot_ratio(ok[new].values, ok[old].values, ok.index)
                        out.append({"lang": lang, "new": new, "old": old, "ratio": est, "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(out)


def plot_a(summary, out_dir):
    models = [m for m in NEW_TOKENIZER + OLD_TOKENIZER if m in set(summary["model"])]
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    width = 0.24
    for k, lang in enumerate(("HU", "DE", "JA")):
        xs, ys, lo, hi = [], [], [], []
        for i, m in enumerate(models):
            r = summary[(summary["model"] == m) & (summary["lang"] == lang)]
            if r.empty:
                continue
            r = r.iloc[0]
            xs.append(i + (k - 1) * width)
            ys.append(r["ratio"])
            lo.append(r["ratio"] - r["ci_lo"])
            hi.append(r["ci_hi"] - r["ratio"])
        ax.bar(xs, ys, width=width, color=LANG_COLOR[lang], label=LANG_NAME[lang].capitalize())
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", ecolor=INK, capsize=2, linewidth=1)
    ax.axhline(1.0, color=INK, linewidth=1, linestyle="--")
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([MODEL_LABEL[m] for m in models], color=INK)
    ax.set_ylabel("tokenszám az angolhoz képest (×)", color=INK)
    ax.set_title("Ugyanaz a tartalom: tokenszám-arány az angolhoz", color=INK, fontsize=13)
    ax.legend(frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.1))
    style_ax(ax)
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout()
    fig.savefig(out_dir / "a_token_ratio.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- B rész
VARIANTS = {lang: [f"{lang}_{lang}", f"{lang}_EN", f"EN_{lang}"] for lang in ("HU", "DE", "JA")}
VAR_LABEL = {"L_L": "kérdés és válasz is a nyelven", "L_EN": "kérdés a nyelven, válasz angolul",
             "EN_L": "kérdés angolul, válasz a nyelven"}


def b_ratios(df, metric, models, category_filter=None):
    rows = []
    d = df if category_filter is None else df[df["category"].isin(category_filter)]
    for m in models:
        sub = d[d["model_alias"] == m]
        base = sub[sub["variant"] == "EN_EN"].set_index(["task_id", "rep"])[metric]
        for lang, vs in VARIANTS.items():
            for v in vs:
                cur = sub[sub["variant"] == v].set_index(["task_id", "rep"])[metric]
                idx = base.index.intersection(cur.index)
                if len(idx) == 0:
                    continue
                groups = [i[0] for i in idx]
                est, lo, hi = boot_ratio(cur.loc[idx].values, base.loc[idx].values, groups)
                rows.append({"model_alias": m, "lang": lang, "variant": v, "n": len(idx),
                             "ratio": est, "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(rows, columns=["model_alias", "lang", "variant", "n", "ratio", "ci_lo", "ci_hi"])


def plot_b_cost(ratios, models, title, fname, out_dir):
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 4.4), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, models):
        sub = ratios[ratios["model_alias"] == m]
        width = 0.26
        for k, kind in enumerate(("L_L", "L_EN", "EN_L")):
            xs, ys, lo, hi = [], [], [], []
            for i, lang in enumerate(("HU", "DE", "JA")):
                v = kind.replace("L", lang) if kind != "L_EN" else f"{lang}_EN"
                v = {"L_L": f"{lang}_{lang}", "L_EN": f"{lang}_EN", "EN_L": f"EN_{lang}"}[kind]
                r = sub[sub["variant"] == v]
                if r.empty:
                    continue
                r = r.iloc[0]
                xs.append(i + (k - 1) * width)
                ys.append(r["ratio"])
                lo.append(r["ratio"] - r["ci_lo"])
                hi.append(r["ci_hi"] - r["ratio"])
            ax.bar(xs, ys, width=width, color=["#B3001B", "#2A6F97", "#6B8F71"][k], label=VAR_LABEL[kind])
            ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", ecolor=INK, capsize=2, linewidth=1)
        ax.axhline(1.0, color=INK, linewidth=1, linestyle="--")
        ax.set_xticks(range(3))
        ax.set_xticklabels([LANG_NAME[l] for l in ("HU", "DE", "JA")], color=INK)
        ax.set_title(m, color=INK, fontsize=12)
        style_ax(ax)
    axes[0].set_ylabel("az angol-angol változathoz képest (×)", color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=3)
    fig.suptitle(title, color=INK, fontsize=13)
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout(rect=[0, 0.07, 1, 0.95])
    fig.savefig(out_dir / fname, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def accuracy_table(df):
    rows = []
    cols = ["model_alias", "variant", "n", "correct", "rate", "ci_lo", "ci_hi", "format_ok_rate", "lang_ok_rate"]
    d = df[df["category"].isin(["szamtani", "nehez", "kinyeres"])].copy()
    d["correct"] = d["correct"].astype(bool)
    for (m, v), g in d.groupby(["model_alias", "variant"]):
        k, n = int(g["correct"].sum()), len(g)
        p, lo, hi = wilson(k, n)
        rows.append({"model_alias": m, "variant": v, "n": n, "correct": k, "rate": p, "ci_lo": lo, "ci_hi": hi,
                     "format_ok_rate": pd.to_numeric(g["format_ok"].map({True: 1, False: 0, "True": 1, "False": 0}), errors="coerce").mean(),
                     "lang_ok_rate": pd.to_numeric(g["lang_ok"].map({True: 1, False: 0, "True": 1, "False": 0}), errors="coerce").mean()})
    return pd.DataFrame(rows, columns=cols)


def plot_accuracy(acc, models, out_dir):
    order = ["EN_EN"] + [v for lang in ("HU", "DE", "JA") for v in VARIANTS[lang]]
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    width = 0.8 / max(1, len(models))
    for k, m in enumerate(models):
        sub = acc[acc["model_alias"] == m].set_index("variant")
        xs, ys, lo, hi = [], [], [], []
        for i, v in enumerate(order):
            if v in sub.index:
                r = sub.loc[v]
                xs.append(i + (k - (len(models) - 1) / 2) * width)
                ys.append(r["rate"] * 100)
                lo.append(max(0.0, (r["rate"] - r["ci_lo"]) * 100))
                hi.append(max(0.0, (r["ci_hi"] - r["rate"]) * 100))
        ax.bar(xs, ys, width=width, label=m, color=["#8A9099", "#B3001B", "#2A6F97"][k % 3])
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", ecolor=INK, capsize=2, linewidth=1)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=35, ha="right", color=INK)
    ax.set_ylim(0, 105)
    ax.set_ylabel("helyes válaszok aránya (%)", color=INK)
    ax.set_title("Pontosság változatonként (számolási és információkinyerő feladatok)", color=INK, fontsize=13)
    ax.legend(frameon=False, loc="lower left", ncol=3)
    style_ax(ax)
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout()
    fig.savefig(out_dir / "b_accuracy.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_tokens_per_call(df, models, out_dir):
    d = df[df["category"].isin(["szamtani", "nehez", "kinyeres"])]
    order = ["EN_EN"] + [v for lang in ("HU", "DE", "JA") for v in VARIANTS[lang]]
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 4.4), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, models):
        g = d[d["model_alias"] == m].groupby("variant")[["net_input_tokens", "output_tokens"]].mean()
        g = g.reindex(order)
        ax.bar(range(len(order)), g["net_input_tokens"], color="#2A6F97", label="bemenet (a fix többlet nélkül)")
        ax.bar(range(len(order)), g["output_tokens"], bottom=g["net_input_tokens"], color="#B3001B",
               label="kimenet (a számlázott kimeneti tokenek)")
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(order, rotation=60, ha="right", color=INK, fontsize=9)
        ax.set_title(m, color=INK, fontsize=12)
        style_ax(ax)
    axes[0].set_ylabel("átlagos token hívásonként", color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2)
    fig.suptitle("Átlagos tokenszám hívásonként (számolási és információkinyerő feladatok)", color=INK, fontsize=13)
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])
    fig.savefig(out_dir / "b_tokens_per_call.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


def non_visible_table(df):
    d = df.copy()
    d["non_visible_tokens"] = pd.to_numeric(d["non_visible_tokens"], errors="coerce")
    d["visible_tokens"] = pd.to_numeric(d["visible_tokens"], errors="coerce")
    d = d.dropna(subset=["non_visible_tokens", "visible_tokens"])
    d = d[d["category"].isin(["szamtani", "nehez", "kinyeres"])]
    if d.empty:
        return pd.DataFrame()
    g = d.groupby(["model_alias", "variant"]).agg(n=("task_id", "size"), visible=("visible_tokens", "mean"),
                                                   extra=("non_visible_tokens", "mean")).reset_index()
    g["extra_share"] = g["extra"] / (g["extra"] + g["visible"])
    return g


def md_table(df, cols, fmt=None):
    fmt = fmt or {}
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append(fmt[c](v) if c in fmt else (f"{v:.2f}" if isinstance(v, float) else str(v)))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b-csv", default=str(DATA / "b_results.csv"))
    ap.add_argument("--out-dir", default=str(HERE / "image"))
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = ["# Összesítő táblák (analyze.py generálta)\n"]

    a = load_a()
    if len(a):
        sa = summarize_a(a)
        sa.to_csv(DATA / "a_summary.csv", index=False)
        tokenizer_generation(a).to_csv(DATA / "a_tokenizer_generation.csv", index=False)
        plot_a(sa, out_dir)
        sa["modell"] = sa["model"].map(MODEL_LABEL)
        sa["nyelv"] = sa["lang"].map(LANG_NAME)
        tables.append("\n## A rész: tokenszám-arány az angolhoz (csomagszintű bootstrap, 95% CI)\n")
        tables.append(md_table(sa, ["modell", "nyelv", "ratio", "ci_lo", "ci_hi", "chars_per_token", "bytes_per_token"]))

    b = pd.read_csv(args.b_csv)
    b["correct"] = b["correct"].replace({"True": True, "False": False})
    models = [m for m in ("haiku", "sonnet", "opus") if m in set(b["model_alias"])]
    ans = ["szamtani", "nehez", "kinyeres"]
    for metric, name, fname in (("net_cost_usd", "számított költség", "b_cost_ratio.png"),
                                ("net_input_tokens", "bemeneti tokenek", "b_input_ratio.png"),
                                ("output_tokens", "kimeneti tokenek", "b_output_ratio.png")):
        r = b_ratios(b, metric, models, ans)
        r.to_csv(DATA / f"b_ratio_{metric}.csv", index=False)
        plot_b_cost(r, models, f"Számolási és információkinyerő feladatok: {name} az angol-angolhoz képest", fname, out_dir)
        tables.append(f"\n## B rész: {name}, arány az `EN_EN`-hez (feladatonkénti bootstrap, 95% CI)\n")
        tables.append(md_table(r, ["model_alias", "variant", "n", "ratio", "ci_lo", "ci_hi"]))
    ro = b_ratios(b, "output_tokens", models, ["nyitott"])
    ro.to_csv(DATA / "b_ratio_output_open.csv", index=False)
    tables.append("\n## B rész: kimeneti tokenek a nyitott (3 mondatos) feladatoknál\n")
    tables.append(md_table(ro, ["model_alias", "variant", "n", "ratio", "ci_lo", "ci_hi"]))

    om = [m for m in models if m in set(ro["model_alias"])]
    plot_b_cost(ro, om, "Nyitott (3 mondatos) feladatok: kimeneti tokenek az angol-angolhoz képest",
                "b_output_open.png", out_dir)
    plot_tokens_per_call(b, models, out_dir)
    think = non_visible_table(b)
    if len(think):
        think.to_csv(DATA / "b_non_visible.csv", index=False)
        tables.append("\n## B rész: látható és a látható szövegen felüli kimeneti tokenek (20%-os részminta, becslés)\n")
        tables.append(md_table(think, ["model_alias", "variant", "n", "visible", "extra", "extra_share"]))
    acc = accuracy_table(b)
    acc.to_csv(DATA / "b_accuracy.csv", index=False)
    tables.append("\n## B rész: pontosság és a kért nyelv betartása\n")
    tables.append(md_table(acc, ["model_alias", "variant", "n", "correct", "rate", "ci_lo", "ci_hi", "format_ok_rate", "lang_ok_rate"]))

    (DATA / "summary_tables.md").write_text("\n".join(tables) + "\n", encoding="utf-8")
    print("Ábrák és összesítő táblák elkészültek:", out_dir)


if __name__ == "__main__":
    main()
